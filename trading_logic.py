# trading_logic.py - Lógica de trading y señales
import logging
import time
import numpy as np
from datetime import datetime
from email_service import send_signal_email
from indicators import calculate_price_targets

# Importar tracker de rendimiento y optimizador adaptativo
try:
    from performance_tracker import performance_tracker
    TRACKING_ENABLED = True
except ImportError:
    TRACKING_ENABLED = False
    logging.warning("Performance tracker no disponible")

try:
    from adaptive_optimizer import adaptive_optimizer
    OPTIMIZATION_ENABLED = True
except ImportError:
    OPTIMIZATION_ENABLED = False
    logging.warning("Optimizador adaptativo no disponible")

logger = logging.getLogger(__name__)

class TradingLogic:
    def __init__(self):
        self.last_signals = {}
        self.signal_count = 0
        self.cooldown_time = 1800   # 30 minutos entre señales del mismo par
        self.daily_email_count = 0
        self.last_email_date = None
        self.max_daily_emails = 10  # Máximo 10 emails por día
    
    def validate_breakout_candle(self, data, signal_type):
        """Valida que la vela de ruptura tenga características fuertes"""
        if len(data) < 2:
            return False
        
        current_candle = data[-1]
        open_price = float(current_candle[1])
        high_price = float(current_candle[2])
        low_price = float(current_candle[3])
        close_price = float(current_candle[4])
        volume = float(current_candle[5])
        
        # Calcular volumen promedio de las últimas 10 velas
        volumes = [float(x[5]) for x in data[-10:]]
        avg_volume = sum(volumes) / len(volumes)
        
        # Rango de la vela
        candle_range = high_price - low_price
        body_size = abs(close_price - open_price)
        
        # Validaciones
        volume_check = volume > avg_volume * 1.2
        body_dominance = body_size / candle_range > 0.6 if candle_range > 0 else False
        
        if signal_type == "buy":
            green_candle = close_price > open_price
            upper_close = (close_price - low_price) / candle_range > 0.6 if candle_range > 0 else False
            return volume_check and body_dominance and green_candle and upper_close
        else:
            red_candle = close_price < open_price
            lower_close = (high_price - close_price) / candle_range > 0.6 if candle_range > 0 else False
            return volume_check and body_dominance and red_candle and lower_close
    
    def check_signal_distance(self, symbol, current_price, signal_type, score=0):
        """Verifica distancia mínima entre señales con cooldown inteligente"""
        if symbol not in self.last_signals:
            return True

        last_signal = self.last_signals[symbol]
        last_time = last_signal.get("time", 0)
        last_price = last_signal.get("price", 0)
        last_type = last_signal.get("type", "")

        # Cooldown inteligente basado en calidad de señal
        time_diff = time.time() - last_time

        if score >= 95:  # SEÑALES PREMIUM (95-100)
            cooldown = 300   # 5 minutos - Oportunidades de oro
        elif score >= 90:  # SEÑALES EXCELENTES (90-94)
            cooldown = 900   # 15 minutos - Muy buenas oportunidades
        else:  # SEÑALES NORMALES (<90)
            cooldown = self.cooldown_time  # 30 minutos - Señales regulares

        if time_diff < cooldown:
            logger.info(f"⏰ Cooldown activo: {int((cooldown - time_diff)/60)}min restantes (score: {score})")
            return False

        # Distancia de precio (mínimo 0.5% de diferencia)
        if last_price > 0:
            price_diff = abs(current_price - last_price) / last_price
            if price_diff < 0.005:  # 0.5%
                return False

        return True
    
    def update_signal_tracking(self, symbol, signal_type, price):
        """Actualiza el tracking de señales"""
        self.last_signals[symbol] = {
            "type": signal_type,
            "price": price,
            "time": time.time(),
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_market_trend(self, symbol, timeframe_data):
        """Detecta la tendencia del mercado usando datos reales de Binance"""
        try:
            if not timeframe_data or "1h" not in timeframe_data:
                return 'SIDEWAYS'  # Default si no hay datos

            data_1h = timeframe_data["1h"]
            if not data_1h or len(data_1h) < 20:
                return 'SIDEWAYS'

            from binance_api import extract_prices
            from indicators import calculate_ema

            prices_1h = extract_prices(data_1h)
            closes_1h = np.array(prices_1h["closes"])

            # EMAs para determinar tendencia
            ema_20 = calculate_ema(closes_1h, 20)
            ema_50 = calculate_ema(closes_1h, 50) if len(closes_1h) >= 50 else ema_20
            current_price = closes_1h[-1]

            # Calcular slope de precios (últimas 10 velas)
            recent_prices = closes_1h[-10:]
            price_slope = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100

            # Determinar tendencia basada en datos reales
            if current_price > ema_20 > ema_50 and price_slope > 1.0:
                return 'BULLISH'
            elif current_price < ema_20 < ema_50 and price_slope < -1.0:
                return 'BEARISH'
            else:
                return 'SIDEWAYS'

        except Exception as e:
            logger.error(f"Error detectando tendencia para {symbol}: {e}")
            return 'SIDEWAYS'

    def check_trend_filter(self, symbol, signal_type, market_trend):
        """Filtro adaptativo basado en análisis de datos reales"""
        # Basado en análisis real: SELL en BEARISH = 66.7% WR, BUY en BULLISH = 50% WR

        if market_trend == "BEARISH":
            if signal_type == "sell":
                logger.info(f"✅ {symbol}: SELL en mercado BEARISH - Filtro APROBADO (WR histórico: 66.7%)")
                return True, 60  # Score mínimo reducido para aprovechar alta efectividad
            else:
                logger.info(f"❌ {symbol}: BUY en mercado BEARISH - Filtro RECHAZADO (WR histórico: 7.7%)")
                return False, 0

        elif market_trend == "BULLISH":
            if signal_type == "buy":
                logger.info(f"✅ {symbol}: BUY en mercado BULLISH - Filtro APROBADO (WR histórico: 50%)")
                return True, 70  # Score mínimo moderado
            else:
                logger.info(f"⚠️ {symbol}: SELL en mercado BULLISH - Filtro RECHAZADO (sin datos históricos)")
                return False, 0

        else:  # SIDEWAYS
            # Mercado lateral tiene baja efectividad según datos reales
            logger.info(f"⚠️ {symbol}: {signal_type.upper()} en mercado SIDEWAYS - Filtro RECHAZADO (WR histórico: <25%)")
            return False, 0

    def check_buy_conditions(self, symbol, market_data, timeframe_data):
        """Verifica condiciones para señal de compra con filtro de tendencia"""
        data = market_data[symbol]

        # 1. FILTRO DE TENDENCIA PRIMERO (basado en datos reales)
        market_trend = self.detect_market_trend(symbol, timeframe_data)
        trend_approved, min_score_required = self.check_trend_filter(symbol, "buy", market_trend)

        if not trend_approved:
            return False, {}  # Rechazar inmediatamente si la tendencia no es favorable

        # 2. Condiciones básicas con score adaptativo
        conditions = {
            "RSI_1m_favorable": 30 <= data["rsi_1m"] <= 70,
            "RSI_15m_bullish": data["rsi_15m"] > 50,
            "EMA_crossover": data["ema_fast"] > data["ema_slow"],
            "Volume_high": data["volume"] > data["vol_avg"] * 1.2,
            "Confidence_good": data["score"] >= min_score_required,  # Score adaptativo por tendencia
            "Price_above_EMA": data["price"] > data["ema_fast"],
            "Candle_positive": data["candle_change_percent"] > 0.1
        }
        
        # Validar vela de ruptura si hay datos
        if timeframe_data and "1m" in timeframe_data:
            conditions["Breakout_candle"] = self.validate_breakout_candle(
                timeframe_data["1m"], "buy"
            )
        
        # Validar vela de ruptura si hay datos
        if timeframe_data and "1m" in timeframe_data:
            conditions["Breakout_candle"] = self.validate_breakout_candle(
                timeframe_data["1m"], "buy"
            )

        # Verificar distancia de señales (con score para cooldown inteligente)
        conditions["Signal_distance"] = self.check_signal_distance(
            symbol, data["price"], "buy", data["score"]
        )

        # Añadir información de tendencia a las condiciones
        conditions["Market_trend"] = market_trend
        conditions["Trend_approved"] = trend_approved
        conditions["Min_score_required"] = min_score_required

        # Simplificar: usar EXACTAMENTE los 8 criterios del dashboard
        # Excluir solo Signal_distance (control interno)
        main_conditions = {k: v for k, v in conditions.items() if k not in ["Signal_distance", "Market_trend", "Trend_approved", "Min_score_required"]}
        main_fulfilled = sum(1 for v in main_conditions.values() if v)
        signal_distance_ok = conditions.get("Signal_distance", True)

        # Requerimientos BUY adaptativos por tendencia
        if market_trend == "BULLISH":
            required_main = 5  # Menos estricto en mercado favorable
        else:
            required_main = 6  # Más estricto en otros mercados

        main_valid = main_fulfilled >= required_main

        logger.info(f"🔍 BUY {symbol} ({market_trend}): {main_fulfilled}/8 criterios + distancia {'✅' if signal_distance_ok else '❌'} = {'✅ VÁLIDA' if main_valid and signal_distance_ok else '❌ NO VÁLIDA'}")
        if main_fulfilled < required_main:
            logger.info(f"   ❌ Faltan {required_main - main_fulfilled} criterios para BUY (necesita {required_main}/8 en {market_trend})")
        if not signal_distance_ok:
            logger.info(f"   ❌ Distancia de señal no válida (cooldown activo)")

        return main_valid and signal_distance_ok, conditions
    
    def check_sell_conditions(self, symbol, market_data, timeframe_data):
        """Verifica condiciones para señal de venta con filtro de tendencia"""
        data = market_data[symbol]

        # 1. FILTRO DE TENDENCIA PRIMERO (basado en datos reales)
        market_trend = self.detect_market_trend(symbol, timeframe_data)
        trend_approved, min_score_required = self.check_trend_filter(symbol, "sell", market_trend)

        if not trend_approved:
            return False, {}  # Rechazar inmediatamente si la tendencia no es favorable

        # 2. Condiciones básicas con score adaptativo
        conditions = {
            "RSI_1m_favorable": 30 <= data["rsi_1m"] <= 70,  # Mismo que BUY
            "RSI_15m_bearish": data["rsi_15m"] < 50,          # Opuesto a BUY
            "EMA_crossunder": data["ema_fast"] < data["ema_slow"],  # Opuesto a BUY
            "Volume_high": data["volume"] > data["vol_avg"] * 1.2,  # Mismo que BUY
            "Confidence_good": data["score"] >= min_score_required,  # Score adaptativo por tendencia
            "Price_below_EMA": data["price"] < data["ema_fast"],    # Opuesto a BUY
            "Candle_negative": data["candle_change_percent"] < -0.1,  # Opuesto a BUY
            "Breakout_candle": data["volume"] > data["vol_avg"] * 1.2 and data["candle_change_percent"] < -0.1  # Ruptura bajista
        }

        # Verificar distancia de señales (control interno)
        conditions["Signal_distance"] = self.check_signal_distance(symbol, data["price"], "sell", data["score"])

        # Añadir información de tendencia a las condiciones
        conditions["Market_trend"] = market_trend
        conditions["Trend_approved"] = trend_approved
        conditions["Min_score_required"] = min_score_required

        # Simplificar: usar EXACTAMENTE los 8 criterios del dashboard
        # Excluir solo Signal_distance (control interno)
        main_conditions = {k: v for k, v in conditions.items() if k not in ["Signal_distance", "Market_trend", "Trend_approved", "Min_score_required"]}
        main_fulfilled = sum(1 for v in main_conditions.values() if v)
        signal_distance_ok = conditions.get("Signal_distance", True)

        # Requerimientos SELL adaptativos por tendencia
        if market_trend == "BEARISH":
            required_main = 4  # Menos estricto en mercado bajista (66.7% WR histórico)
        else:
            required_main = 6  # Más estricto en otros mercados

        main_valid = main_fulfilled >= required_main

        logger.info(f"🔍 SELL {symbol} ({market_trend}): {main_fulfilled}/8 criterios + distancia {'✅' if signal_distance_ok else '❌'} = {'✅ VÁLIDA' if main_valid and signal_distance_ok else '❌ NO VÁLIDA'}")
        if main_fulfilled < required_main:
            logger.info(f"   ❌ Faltan {required_main - main_fulfilled} criterios para SELL (necesita {required_main}/8 en {market_trend})")

        return main_valid and signal_distance_ok, conditions
    
    def check_daily_email_limit(self):
        """Verifica si se ha alcanzado el límite diario de emails"""
        from datetime import date
        today = date.today()

        # Resetear contador si es un nuevo día
        if self.last_email_date != today:
            self.daily_email_count = 0
            self.last_email_date = today

        return self.daily_email_count < self.max_daily_emails

    def process_signal(self, symbol, signal_type, market_data, conditions, send_email=True):
        """Procesa y envía una señal de trading"""
        try:
            data = market_data[symbol]

            # Solo verificar límites de email si vamos a enviar email
            if send_email:
                # FILTRO INTELIGENTE BASADO EN TENDENCIA Y DATOS REALES
                market_trend = conditions.get("Market_trend", "SIDEWAYS")
                min_score_required = conditions.get("Min_score_required", 90)

                # Criterios adaptativos por tendencia (basado en análisis real)
                email_approved = False
                if market_trend == "BEARISH" and signal_type == "sell" and data["score"] >= 70:
                    # SELL en BEARISH tiene 66.7% WR histórico - Enviar email
                    email_approved = True
                    logger.info(f"🔥 SEÑAL PREMIUM: SELL en BEARISH (Score: {data['score']}) - WR histórico: 66.7%")
                elif market_trend == "BULLISH" and signal_type == "buy" and data["score"] >= 80:
                    # BUY en BULLISH tiene 50% WR histórico - Más conservador
                    email_approved = True
                    logger.info(f"🔥 SEÑAL PREMIUM: BUY en BULLISH (Score: {data['score']}) - WR histórico: 50%")
                elif data["score"] >= 95:
                    # Score ultra-alto siempre se envía (independiente de tendencia)
                    email_approved = True
                    logger.info(f"🔥 SEÑAL ULTRA-PREMIUM (Score: {data['score']}) - Bypassing trend filter")
                else:
                    logger.info(f"📊 Señal registrada pero NO enviada por email - {signal_type.upper()} en {market_trend} (Score: {data['score']}) no cumple criterios premium")
                    send_email = False

                # Verificar límite diario solo si la señal fue aprobada
                if email_approved and not self.check_daily_email_limit():
                    logger.warning(f"📧 Límite diario de emails alcanzado ({self.max_daily_emails})")
                    send_email = False
                elif not email_approved:
                    send_email = False
            
            # Calcular price targets
            price_targets = calculate_price_targets(
                data["price"], data["atr"], signal_type, symbol
            )
            logger.info(f"🎯 Price targets para {symbol}: {price_targets}")
            
            # Enviar email solo si send_email=True
            if send_email:
                email_sent = send_signal_email(
                    signal_type, symbol, data["price"], data["rsi_1m"], data["rsi_15m"],
                    data["ema_fast"], data["ema_slow"], data["volume"], data["vol_avg"],
                    data["score"], data["atr"], data["candle_change_percent"],
                    conditions, price_targets
                )

                if email_sent:
                    self.signal_count += 1
                    self.daily_email_count += 1  # Incrementar contador diario
                    self.update_signal_tracking(symbol, signal_type, data["price"])

                    # Registrar en performance tracker
                    if TRACKING_ENABLED:
                        self.record_signal_for_tracking(symbol, signal_type, data, conditions, price_targets)

                    # Actualizar market_data
                    market_data[symbol]["last_signal"] = signal_type
                    market_data[symbol]["last_signal_price"] = data["price"]
                    market_data[symbol]["last_signal_time"] = time.time()

                    logger.info(f"✅ Señal {signal_type.upper()} enviada por EMAIL para {symbol}")
                    return True
                else:
                    logger.error(f"❌ Error enviando señal {signal_type} para {symbol}")
                    return False
            else:
                # Solo logging, sin email
                self.update_signal_tracking(symbol, signal_type, data["price"])

                # Registrar en performance tracker SIEMPRE (con o sin email)
                if TRACKING_ENABLED:
                    self.record_signal_for_tracking(symbol, signal_type, data, conditions, price_targets)

                # Actualizar market_data
                market_data[symbol]["last_signal"] = signal_type
                market_data[symbol]["last_signal_price"] = data["price"]
                market_data[symbol]["last_signal_time"] = time.time()

                logger.info(f"📊 Señal {signal_type.upper()} detectada para {symbol} (sin email)")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error procesando señal {signal_type} para {symbol}: {e}")
            return False
    
    def analyze_signals(self, market_data, timeframe_data=None):
        """Analiza señales para todos los símbolos"""
        signals_sent = 0

        # Verificar resultados de señales pendientes cada 10 ciclos
        if hasattr(self, 'cycle_count'):
            self.cycle_count += 1
        else:
            self.cycle_count = 1

        # Verificar señales cada 3 ciclos (más frecuente) para resultados más rápidos
        if self.cycle_count % 3 == 0 and TRACKING_ENABLED:
            try:
                updated = performance_tracker.check_signal_outcomes()
                if updated > 0:
                    logger.info(f"📊 Verificadas {updated} señales pendientes")
            except Exception as e:
                logger.error(f"❌ Error verificando señales: {e}")

        for symbol in market_data:
            try:
                # Verificar señal de compra
                buy_valid, buy_conditions = self.check_buy_conditions(
                    symbol, market_data, timeframe_data
                )

                if buy_valid:
                    if self.process_signal(symbol, "buy", market_data, buy_conditions, send_email=True):
                        signals_sent += 1
                        continue  # No verificar sell si ya enviamos buy

                # Verificar señal de venta SOLO si no hay señal de compra
                sell_valid, sell_conditions = self.check_sell_conditions(
                    symbol, market_data, timeframe_data
                )

                if sell_valid:
                    # SELL signals pueden enviar email si son en mercado BEARISH (66.7% WR histórico)
                    market_trend = sell_conditions.get("Market_trend", "SIDEWAYS")
                    send_sell_email = (market_trend == "BEARISH")  # Solo SELL en BEARISH envían email

                    if self.process_signal(symbol, "sell", market_data, sell_conditions, send_email=send_sell_email):
                        if send_sell_email:
                            signals_sent += 1  # Contar como señal enviada si se envió email
                
            except Exception as e:
                logger.error(f"❌ Error analizando señales para {symbol}: {e}")
        
        if signals_sent > 0:
            logger.info(f"📧 {signals_sent} señales enviadas en este ciclo")
        
        return signals_sent
    
    def record_signal_for_tracking(self, symbol, signal_type, data, conditions, price_targets):
        """Registra señal en el sistema de tracking"""
        try:
            signal_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'signal_type': signal_type,
                'entry_price': data['price'],
                'score': data['score'],
                'conditions_met': sum(1 for v in conditions.values() if v),
                'total_conditions': len(conditions),
                'rsi_1m': data.get('rsi_1m'),
                'rsi_15m': data.get('rsi_15m'),
                'ema_fast': data.get('ema_fast'),
                'ema_slow': data.get('ema_slow'),
                'volume_ratio': data.get('volume', 0) / data.get('vol_avg', 1) if data.get('vol_avg') else 0,
                'atr': data.get('atr'),
                'candle_change': data.get('candle_change_percent'),
                'tp_price': price_targets.get('take_profit') if price_targets else None,
                'sl_price': price_targets.get('stop_loss') if price_targets else None,
                'expected_move': price_targets.get('expected_move_percent') if price_targets else None,
                'risk_reward': price_targets.get('risk_reward_ratio') if price_targets else None,
                'market_conditions': {
                    'conditions': {k: bool(v) for k, v in conditions.items()},  # Convertir a bool explícitamente
                    'timeframe_data': 'multi_tf_analysis'
                },
                'market_trend': conditions.get('Market_trend', 'SIDEWAYS')
            }

            performance_tracker.record_signal(signal_data)
            logger.info(f"📊 Señal registrada en tracking: {symbol} {signal_type}")

        except Exception as e:
            logger.error(f"❌ Error registrando señal en tracking: {e}")

    def get_stats(self):
        """Retorna estadísticas del trading"""
        return {
            "total_signals": self.signal_count,
            "last_signals": self.last_signals,
            "cooldown_time": self.cooldown_time
        }

# Instancia global
trading_logic = TradingLogic()

def analyze_trading_signals(market_data, timeframe_data=None):
    """Función helper para analizar señales"""
    return trading_logic.analyze_signals(market_data, timeframe_data)

def get_trading_stats():
    """Función helper para obtener estadísticas"""
    return trading_logic.get_stats()
