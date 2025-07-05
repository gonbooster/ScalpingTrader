# market_analyzer.py - Análisis de mercado y datos
import numpy as np
import logging
from datetime import datetime, timezone
from binance_api import get_multi_timeframe_data, extract_prices, binance_api
from indicators import (
    calculate_ema, calculate_rsi, calculate_atr, calculate_adx,
    calculate_volume_sma, calculate_confidence_score, calculate_price_targets
)

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    def __init__(self, symbols=None):
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.market_data = self._initialize_market_data()
        self.using_simulation = False
        self.binance_api = binance_api  # Referencia a la instancia de BinanceAPI
    
    def _initialize_market_data(self):
        """Inicializa estructura de datos del mercado"""
        data = {}
        for symbol in self.symbols:
            data[symbol] = {
                "price": 0.0, "rsi": 0.0, "rsi_1m": 0.0, "rsi_5m": 0.0, "rsi_15m": 0.0,
                "ema_fast": 0.0, "ema_slow": 0.0, "volume": 0.0, "vol_avg": 0.0,
                "score": 0, "last_signal": None, "pnl_daily": 0.0, "atr": 0.0,
                "last_signal_price": 0.0, "last_signal_time": 0,
                "candle_change_percent": 0.0, "take_profit_buy": 0.0,
                "stop_loss_buy": 0.0, "expected_move_buy": 0.0, "risk_reward_buy": 0.0,
                "take_profit_sell": 0.0, "stop_loss_sell": 0.0,
                "expected_move_sell": 0.0, "risk_reward_sell": 0.0,
                # Nuevos campos para cambios de precio
                "price_24h_change_percent": 0.0, "price_24h_change_amount": 0.0,
                "previous_price": 0.0, "price_change_percent": 0.0, "price_change_amount": 0.0
            }
        return data
    
    def detect_pair_type(self, symbol):
        """Detecta el tipo de par"""
        ticker = symbol.upper()
        if "BTC" in ticker:
            return "BTC"
        elif "ETH" in ticker:
            return "ETH"
        elif "SOL" in ticker:
            return "SOL"
        else:
            return "OTHER"
    
    def get_adaptive_params(self, pair_type):
        """Parámetros adaptativos por par"""
        params = {
            "BTC": {"ema_fast": 10, "ema_slow": 21, "rsi_low": 50, "rsi_high": 65, "vol_multiplier": 1.8},
            "ETH": {"ema_fast": 9, "ema_slow": 23, "rsi_low": 47, "rsi_high": 63, "vol_multiplier": 1.6},
            "SOL": {"ema_fast": 7, "ema_slow": 20, "rsi_low": 45, "rsi_high": 68, "vol_multiplier": 1.4},
            "OTHER": {"ema_fast": 10, "ema_slow": 21, "rsi_low": 50, "rsi_high": 65, "vol_multiplier": 1.5}
        }
        return params.get(pair_type, params["OTHER"])
    
    def is_valid_trading_hour(self):
        """Filtro de horarios (8-18 UTC)"""
        current_hour = datetime.now(timezone.utc).hour
        return 8 <= current_hour <= 18
    
    def analyze_symbol(self, symbol):
        """Analiza un símbolo específico"""
        try:
            logger.info(f"🔍 Analizando {symbol}...")
            
            # Obtener datos multi-timeframe
            timeframe_data = get_multi_timeframe_data(symbol)
            if not timeframe_data or "1m" not in timeframe_data:
                logger.error(f"❌ No se pudieron obtener datos para {symbol}")
                return False
            
            data_1m = timeframe_data["1m"]
            data_5m = timeframe_data.get("5m", [])
            data_15m = timeframe_data.get("15m", [])
            data_1h = timeframe_data.get("1h", [])
            
            # Extraer precios
            prices_1m = extract_prices(data_1m)
            if not prices_1m or "closes" not in prices_1m:
                logger.error(f"❌ Error extrayendo precios de {symbol}")
                return False
            
            # Datos básicos
            closes_1m = np.array(prices_1m["closes"])
            highs_1m = np.array(prices_1m["highs"])
            lows_1m = np.array(prices_1m["lows"])
            volumes_1m = np.array(prices_1m["volumes"])
            
            close_now = prices_1m["current_price"]
            vol_now = prices_1m["current_volume"]

            # Obtener datos de 24h para cambios de precio
            symbol_info = self.binance_api.get_symbol_info(symbol)
            price_24h_change_percent = float(symbol_info.get('priceChangePercent', 0)) if symbol_info else 0
            price_24h_change_amount = float(symbol_info.get('priceChange', 0)) if symbol_info else 0

            # Calcular cambio desde última actualización
            previous_price = self.market_data[symbol].get("price", close_now)
            price_change_amount = close_now - previous_price
            price_change_percent = ((close_now - previous_price) / previous_price * 100) if previous_price > 0 else 0
            
            # Parámetros adaptativos
            pair_type = self.detect_pair_type(symbol)
            params = self.get_adaptive_params(pair_type)
            
            # Calcular indicadores
            ema_fast_val = calculate_ema(closes_1m, params["ema_fast"])
            ema_slow_val = calculate_ema(closes_1m, params["ema_slow"])
            rsi_1m = calculate_rsi(closes_1m)
            atr_val = calculate_atr(highs_1m, lows_1m, closes_1m)
            adx_val = calculate_adx(highs_1m, lows_1m, closes_1m)
            
            # Volumen promedio
            vol_avg = calculate_volume_sma(volumes_1m, 20)
            
            # RSI 5m para confirmación rápida
            if data_5m and len(data_5m) >= 14:
                prices_5m = extract_prices(data_5m)
                closes_5m = np.array(prices_5m["closes"])
                rsi_5m = calculate_rsi(closes_5m)
            else:
                rsi_5m = rsi_1m

            # RSI 15m para tendencia general
            if data_15m and len(data_15m) >= 14:
                prices_15m = extract_prices(data_15m)
                closes_15m = np.array(prices_15m["closes"])
                rsi_15m = calculate_rsi(closes_15m)
            else:
                rsi_15m = rsi_5m
            
            # Macro trend (1h)
            macro_trend = True  # Simplificado por ahora
            if data_1h and len(data_1h) >= 20:
                prices_1h = extract_prices(data_1h)
                closes_1h = np.array(prices_1h["closes"])
                ema_1h = calculate_ema(closes_1h, 20)
                macro_trend = close_now > ema_1h
            
            # Calcular % de cambio de vela actual
            open_price = float(data_1m[0][1])
            candle_change_percent = ((close_now - open_price) / open_price) * 100

            # Score de confianza - NUEVO SISTEMA REALISTA
            from indicators import calculate_realistic_scalping_score

            # Preparar datos para el nuevo scoring (rsi_5m ya está calculado arriba)
            scoring_data = {
                "rsi_1m": rsi_1m,
                "rsi_5m": rsi_5m,
                "rsi_15m": rsi_15m,
                "volume": vol_now,
                "vol_avg": vol_avg,
                "ema_fast": ema_fast_val,
                "ema_slow": ema_slow_val,
                "price": close_now,
                "candle_change_percent": candle_change_percent,
                "atr": atr_val
            }

            confidence_score = calculate_realistic_scalping_score(scoring_data)
            
            # Calcular price targets para ambos escenarios
            price_targets_buy = calculate_price_targets(close_now, atr_val, "buy", symbol)
            price_targets_sell = calculate_price_targets(close_now, atr_val, "sell", symbol)
            
            # Calcular criterios de trading para visualización
            buy_criteria = self.calculate_buy_criteria(close_now, rsi_1m, rsi_15m, ema_fast_val, ema_slow_val, vol_now, vol_avg, confidence_score, candle_change_percent)
            sell_criteria = self.calculate_sell_criteria(close_now, rsi_1m, rsi_15m, ema_fast_val, ema_slow_val, vol_now, vol_avg, confidence_score, candle_change_percent)

            # Actualizar datos del mercado
            self.market_data[symbol].update({
                "previous_price": previous_price,
                "price": close_now,
                "rsi": rsi_1m,
                "rsi_1m": rsi_1m,
                "rsi_5m": rsi_5m,
                "rsi_15m": rsi_15m,
                "ema_fast": ema_fast_val,
                "ema_slow": ema_slow_val,
                "volume": vol_now,
                "vol_avg": vol_avg,
                "score": confidence_score,
                "confidence_score": confidence_score,
                "atr": atr_val,
                "candle_change_percent": candle_change_percent,
                "price_24h_change_percent": price_24h_change_percent,
                "price_24h_change_amount": price_24h_change_amount,
                "price_change_percent": price_change_percent,
                "price_change_amount": price_change_amount,
                "take_profit_buy": price_targets_buy["take_profit"],
                "stop_loss_buy": price_targets_buy["stop_loss"],
                "expected_move_buy": price_targets_buy["expected_move_percent"],
                "risk_reward_buy": price_targets_buy["risk_reward_ratio"],
                "take_profit_sell": price_targets_sell["take_profit"],
                "stop_loss_sell": price_targets_sell["stop_loss"],
                "expected_move_sell": price_targets_sell["expected_move_percent"],
                "risk_reward_sell": price_targets_sell["risk_reward_ratio"],
                "buy_criteria": buy_criteria,
                "sell_criteria": sell_criteria
            })
            
            logger.info(f"✅ {symbol}: price=${close_now:,.2f}, rsi={rsi_1m:.1f}, score={confidence_score}/100")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error analizando {symbol}: {e}")
            return False
    
    def analyze_all_symbols(self):
        """Analiza todos los símbolos"""
        success_count = 0
        for symbol in self.symbols:
            if self.analyze_symbol(symbol):
                success_count += 1
        
        logger.info(f"📊 Análisis completado: {success_count}/{len(self.symbols)} símbolos")
        return success_count > 0
    
    def get_market_data(self):
        """Retorna los datos del mercado"""
        return self.market_data
    
    def get_symbol_data(self, symbol):
        """Retorna datos de un símbolo específico"""
        return self.market_data.get(symbol, {})

    def calculate_buy_criteria(self, price, rsi_1m, rsi_15m, ema_fast, ema_slow, volume, vol_avg, score, candle_change):
        """Calcula criterios de compra para visualización"""
        criteria = {
            "RSI_1m_favorable": 30 <= rsi_1m <= 70,
            "RSI_15m_bullish": rsi_15m > 50,
            "EMA_crossover": ema_fast > ema_slow,
            "Volume_high": volume > vol_avg * 1.2,
            "Confidence_good": score >= 75,
            "Price_above_EMA": price > ema_fast,
            "Candle_positive": candle_change > 0.1,
            "Breakout_candle": volume > vol_avg * 1.2 and candle_change > 0.1  # Simplificado para dashboard
        }

        fulfilled = sum(1 for v in criteria.values() if v)

        return {
            "criteria": criteria,
            "fulfilled": fulfilled,
            "total": len(criteria),
            "percentage": (fulfilled / len(criteria)) * 100
        }

    def calculate_sell_criteria(self, price, rsi_1m, rsi_15m, ema_fast, ema_slow, volume, vol_avg, score, candle_change):
        """Calcula criterios de venta para visualización"""
        criteria = {
            "RSI_1m_favorable": 30 <= rsi_1m <= 70,
            "RSI_15m_bearish": rsi_15m < 50,
            "EMA_crossunder": ema_fast < ema_slow,
            "Volume_high": volume > vol_avg * 1.2,
            "Confidence_good": score >= 70,
            "Price_below_EMA": price < ema_fast,
            "Candle_negative": candle_change < -0.1,
            "Breakout_candle": volume > vol_avg * 1.2 and candle_change < -0.1  # Simplificado para dashboard
        }

        fulfilled = sum(1 for v in criteria.values() if v)

        return {
            "criteria": criteria,
            "fulfilled": fulfilled,
            "total": len(criteria),
            "percentage": (fulfilled / len(criteria)) * 100
        }

# Instancia global
market_analyzer = MarketAnalyzer()

def analyze_market():
    """Función helper para analizar el mercado"""
    return market_analyzer.analyze_all_symbols()

def get_market_data():
    """Función helper para obtener datos del mercado"""
    return market_analyzer.get_market_data()

def get_symbol_data(symbol):
    """Función helper para obtener datos de un símbolo"""
    return market_analyzer.get_symbol_data(symbol)
