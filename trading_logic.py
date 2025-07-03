# trading_logic.py - Lógica de trading y señales
import logging
import time
from datetime import datetime
from email_service import send_signal_email
from indicators import calculate_price_targets

logger = logging.getLogger(__name__)

class TradingLogic:
    def __init__(self):
        self.last_signals = {}
        self.signal_count = 0
        self.cooldown_time = 1800  # 30 minutos entre señales del mismo par
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
    
    def check_signal_distance(self, symbol, current_price, signal_type):
        """Verifica distancia mínima entre señales"""
        if symbol not in self.last_signals:
            return True
        
        last_signal = self.last_signals[symbol]
        last_time = last_signal.get("time", 0)
        last_price = last_signal.get("price", 0)
        last_type = last_signal.get("type", "")
        
        # Cooldown de tiempo
        time_diff = time.time() - last_time
        if time_diff < self.cooldown_time:
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
    
    def check_buy_conditions(self, symbol, market_data, timeframe_data):
        """Verifica condiciones para señal de compra"""
        data = market_data[symbol]
        
        # Condiciones básicas
        conditions = {
            "RSI_1m_favorable": 30 <= data["rsi_1m"] <= 70,
            "RSI_15m_bullish": data["rsi_15m"] > 50,
            "EMA_crossover": data["ema_fast"] > data["ema_slow"],
            "Volume_high": data["volume"] > data["vol_avg"] * 1.2,
            "Confidence_excellent": data["score"] >= 90,  # Solo señales EXCELENTES por email
            "Price_above_EMA": data["price"] > data["ema_fast"],
            "Candle_positive": data["candle_change_percent"] > 0.1
        }
        
        # Validar vela de ruptura si hay datos
        if timeframe_data and "1m" in timeframe_data:
            conditions["Breakout_candle"] = self.validate_breakout_candle(
                timeframe_data["1m"], "buy"
            )
        
        # Verificar distancia de señales
        conditions["Signal_distance"] = self.check_signal_distance(
            symbol, data["price"], "buy"
        )
        
        # Contar condiciones cumplidas
        fulfilled = sum(1 for v in conditions.values() if v)
        required = 7  # Mínimo 7 de 8 condiciones para emails
        
        logger.info(f"🔍 BUY {symbol}: {fulfilled}/{len(conditions)} condiciones cumplidas")
        
        return fulfilled >= required, conditions
    
    def check_sell_conditions(self, symbol, market_data, timeframe_data):
        """Verifica condiciones para señal de venta"""
        data = market_data[symbol]
        
        # Condiciones básicas
        conditions = {
            "RSI_1m_favorable": 30 <= data["rsi_1m"] <= 70,
            "RSI_15m_bearish": data["rsi_15m"] < 50,
            "EMA_crossunder": data["ema_fast"] < data["ema_slow"],
            "Volume_high": data["volume"] > data["vol_avg"] * 1.2,
            "Confidence_excellent": data["score"] >= 90,  # Solo señales EXCELENTES por email
            "Price_below_EMA": data["price"] < data["ema_fast"],
            "Candle_negative": data["candle_change_percent"] < -0.1
        }
        
        # Validar vela de ruptura si hay datos
        if timeframe_data and "1m" in timeframe_data:
            conditions["Breakout_candle"] = self.validate_breakout_candle(
                timeframe_data["1m"], "sell"
            )
        
        # Verificar distancia de señales
        conditions["Signal_distance"] = self.check_signal_distance(
            symbol, data["price"], "sell"
        )
        
        # Contar condiciones cumplidas
        fulfilled = sum(1 for v in conditions.values() if v)
        required = 7  # Mínimo 7 de 8 condiciones para emails
        
        logger.info(f"🔍 SELL {symbol}: {fulfilled}/{len(conditions)} condiciones cumplidas")
        
        return fulfilled >= required, conditions
    
    def check_daily_email_limit(self):
        """Verifica si se ha alcanzado el límite diario de emails"""
        from datetime import date
        today = date.today()

        # Resetear contador si es un nuevo día
        if self.last_email_date != today:
            self.daily_email_count = 0
            self.last_email_date = today

        return self.daily_email_count < self.max_daily_emails

    def process_signal(self, symbol, signal_type, market_data, conditions):
        """Procesa y envía una señal de trading"""
        try:
            data = market_data[symbol]

            # Verificar límite diario de emails
            if not self.check_daily_email_limit():
                logger.warning(f"📧 Límite diario de emails alcanzado ({self.max_daily_emails})")
                return False
            
            # Calcular price targets
            price_targets = calculate_price_targets(
                data["price"], data["atr"], signal_type, symbol
            )
            
            # Enviar email
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
                
                # Actualizar market_data
                market_data[symbol]["last_signal"] = signal_type
                market_data[symbol]["last_signal_price"] = data["price"]
                market_data[symbol]["last_signal_time"] = time.time()
                
                logger.info(f"✅ Señal {signal_type.upper()} enviada para {symbol}")
                return True
            else:
                logger.error(f"❌ Error enviando señal {signal_type} para {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error procesando señal {signal_type} para {symbol}: {e}")
            return False
    
    def analyze_signals(self, market_data, timeframe_data=None):
        """Analiza señales para todos los símbolos"""
        signals_sent = 0
        
        for symbol in market_data:
            try:
                # Verificar señal de compra
                buy_valid, buy_conditions = self.check_buy_conditions(
                    symbol, market_data, timeframe_data
                )
                
                if buy_valid:
                    if self.process_signal(symbol, "buy", market_data, buy_conditions):
                        signals_sent += 1
                        continue  # No verificar sell si ya enviamos buy
                
                # Verificar señal de venta
                sell_valid, sell_conditions = self.check_sell_conditions(
                    symbol, market_data, timeframe_data
                )
                
                if sell_valid:
                    if self.process_signal(symbol, "sell", market_data, sell_conditions):
                        signals_sent += 1
                
            except Exception as e:
                logger.error(f"❌ Error analizando señales para {symbol}: {e}")
        
        if signals_sent > 0:
            logger.info(f"📧 {signals_sent} señales enviadas en este ciclo")
        
        return signals_sent
    
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
