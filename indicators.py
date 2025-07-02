# indicators.py - Cálculos de indicadores técnicos
import numpy as np

def calculate_ema(prices, period):
    """Calcula la Media Móvil Exponencial"""
    if len(prices) < period:
        return 0.0

    prices_array = np.array(prices, dtype=float)

    # Calcular EMA manualmente sin pandas
    alpha = 2.0 / (period + 1)
    ema = prices_array[0]  # Primer valor

    for price in prices_array[1:]:
        ema = alpha * price + (1 - alpha) * ema

    return ema

def calculate_rsi(prices, period=14):
    """Calcula el Índice de Fuerza Relativa"""
    if len(prices) < period + 1:
        return 50.0
    
    prices_array = np.array(prices, dtype=float)
    deltas = np.diff(prices_array)
    
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_atr(highs, lows, closes, period=14):
    """Calcula el Average True Range"""
    if len(highs) < period + 1:
        return 0.0
    
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)
    
    # True Range calculation
    tr1 = highs[1:] - lows[1:]
    tr2 = np.abs(highs[1:] - closes[:-1])
    tr3 = np.abs(lows[1:] - closes[:-1])
    
    true_range = np.maximum(tr1, np.maximum(tr2, tr3))
    
    if len(true_range) < period:
        return np.mean(true_range)
    
    # ATR calculation (simple moving average of True Range)
    atr = np.mean(true_range[-period:])
    
    return atr

def calculate_adx(highs, lows, closes, period=14):
    """Calcula el Average Directional Index"""
    if len(highs) < period + 1:
        return 0.0
    
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)
    
    # Calculate True Range
    tr1 = highs[1:] - lows[1:]
    tr2 = np.abs(highs[1:] - closes[:-1])
    tr3 = np.abs(lows[1:] - closes[:-1])
    true_range = np.maximum(tr1, np.maximum(tr2, tr3))
    
    # Calculate Directional Movement
    dm_plus = np.where((highs[1:] - highs[:-1]) > (lows[:-1] - lows[1:]), 
                       np.maximum(highs[1:] - highs[:-1], 0), 0)
    dm_minus = np.where((lows[:-1] - lows[1:]) > (highs[1:] - highs[:-1]), 
                        np.maximum(lows[:-1] - lows[1:], 0), 0)
    
    if len(true_range) < period:
        return 25.0  # Default neutral value
    
    # Smooth the values
    tr_smooth = np.mean(true_range[-period:])
    dm_plus_smooth = np.mean(dm_plus[-period:])
    dm_minus_smooth = np.mean(dm_minus[-period:])
    
    if tr_smooth == 0:
        return 25.0
    
    # Calculate DI+ and DI-
    di_plus = (dm_plus_smooth / tr_smooth) * 100
    di_minus = (dm_minus_smooth / tr_smooth) * 100
    
    # Calculate DX
    if (di_plus + di_minus) == 0:
        return 25.0
    
    dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100
    
    return dx

def calculate_volume_sma(volumes, period=20):
    """Calcula la media móvil simple del volumen"""
    if len(volumes) < period:
        return np.mean(volumes) if volumes else 0
    
    volumes_array = np.array(volumes, dtype=float)
    return np.mean(volumes_array[-period:])

def calculate_confidence_score(rsi_1m, rsi_15m, volume_ratio, adx, macro_trend):
    """Calcula un score de confianza basado en múltiples indicadores"""
    score = 0
    
    # RSI 1m (peso: 25%)
    if 30 <= rsi_1m <= 70:
        score += 25
    elif 25 <= rsi_1m <= 75:
        score += 15
    elif 20 <= rsi_1m <= 80:
        score += 10
    
    # RSI 15m (peso: 25%)
    if 30 <= rsi_15m <= 70:
        score += 25
    elif 25 <= rsi_15m <= 75:
        score += 15
    elif 20 <= rsi_15m <= 80:
        score += 10
    
    # Volumen (peso: 20%)
    if volume_ratio > 1.5:
        score += 20
    elif volume_ratio > 1.2:
        score += 15
    elif volume_ratio > 1.0:
        score += 10
    
    # ADX (peso: 15%)
    if adx > 40:
        score += 15
    elif adx > 25:
        score += 10
    elif adx > 20:
        score += 5
    
    # Macro Trend (peso: 15%)
    if macro_trend:
        score += 15
    
    return min(score, 100)

def calculate_price_targets(current_price, atr_value, signal_type, symbol):
    """Calcula objetivos de precio basados en ATR y volatilidad"""
    
    # Multiplicadores según el tipo de par
    if symbol.startswith('BTC'):
        atr_multiplier_tp = 2.5  # Take Profit más conservador para BTC
        atr_multiplier_sl = 1.2  # Stop Loss más ajustado
    elif symbol.startswith('ETH'):
        atr_multiplier_tp = 2.8
        atr_multiplier_sl = 1.3
    else:  # SOL y otros
        atr_multiplier_tp = 3.0  # Más agresivo para altcoins
        atr_multiplier_sl = 1.5
    
    if signal_type == "buy":
        # Para BUY: esperamos subida
        take_profit = current_price + (atr_value * atr_multiplier_tp)
        stop_loss = current_price - (atr_value * atr_multiplier_sl)
        expected_move_percent = ((take_profit - current_price) / current_price) * 100
        risk_percent = ((current_price - stop_loss) / current_price) * 100
    else:
        # Para SELL: esperamos bajada
        take_profit = current_price - (atr_value * atr_multiplier_tp)
        stop_loss = current_price + (atr_value * atr_multiplier_sl)
        expected_move_percent = ((current_price - take_profit) / current_price) * 100
        risk_percent = ((stop_loss - current_price) / current_price) * 100
    
    # Risk/Reward ratio
    risk_reward_ratio = expected_move_percent / risk_percent if risk_percent > 0 else 0
    
    return {
        "take_profit": take_profit,
        "stop_loss": stop_loss,
        "expected_move_percent": expected_move_percent,
        "risk_percent": risk_percent,
        "risk_reward_ratio": risk_reward_ratio
    }
