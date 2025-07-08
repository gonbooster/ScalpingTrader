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
    """SISTEMA LEGACY - Mantenido por compatibilidad"""
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

def calculate_realistic_scalping_score(data):
    """
    🚀 NUEVO SISTEMA DE SCORING REALISTA PARA SCALPING CRYPTO
    Optimizado para precisión y efectividad en trading de alta frecuencia
    """
    from datetime import datetime

    score = 0

    # 1. 📈 MOMENTUM MULTI-TIMEFRAME (35%) - Clave para scalping
    rsi_1m = data.get("rsi_1m", 50)
    rsi_5m = data.get("rsi_5m", 50)
    rsi_15m = data.get("rsi_15m", 50)

    # Momentum ascendente OPTIMIZADO - Más estricto para mejor calidad
    if rsi_1m > rsi_5m > rsi_15m and rsi_1m > 55:  # Aceleración alcista fuerte (más estricto)
        score += 30
    elif rsi_1m > rsi_5m + 3 and rsi_1m > 50:  # Momentum positivo significativo
        score += 25
    elif rsi_1m > rsi_5m and rsi_1m > 45:  # Momentum básico
        score += 20
    else:  # Sin momentum
        score += 10

    # RSI en zona óptima para scalping - EQUILIBRADO
    if 30 <= rsi_1m <= 70:  # Zona óptima
        score += 5
    else:  # Fuera de zona
        score += 0

    # 2. 🔊 VOLUMEN INTELIGENTE (30%) - Confirmación de movimiento
    volume_ratio = data.get("volume", 1) / max(data.get("vol_avg", 1), 1)

    # Volumen explosivo (señal fuerte) - EQUILIBRADO PARA CALIDAD
    if volume_ratio > 2.0:  # Volumen excepcional
        score += 30
    elif volume_ratio > 1.5:  # Volumen muy alto
        score += 25
    elif volume_ratio > 1.2:  # Volumen alto
        score += 20
    elif volume_ratio > 1.0:  # Volumen moderado
        score += 15
    else:  # Volumen bajo
        score += 5

    # 3. 🎯 PRICE ACTION (25%) - Confirmación técnica
    ema_fast = data.get("ema_fast", 0)
    ema_slow = data.get("ema_slow", 0)
    price = data.get("price", 0)
    candle_change = abs(data.get("candle_change_percent", 0))

    # Alineación de EMAs - MÁS GENEROSO
    ema_alignment = ema_fast > ema_slow if ema_fast and ema_slow else False
    price_vs_ema = price > ema_fast if price and ema_fast else False

    if ema_alignment and price_vs_ema and candle_change > 0.1:  # Setup perfecto
        score += 25
    elif ema_alignment and price_vs_ema:  # Setup bueno
        score += 20
    elif ema_alignment or price_vs_ema:  # Setup básico
        score += 15
    else:  # Sin alineación
        score += 10

    # 4. 📊 VOLATILIDAD CONTROLADA (10%) - Risk management
    atr_value = data.get("atr", 0)
    if price > 0 and atr_value > 0:
        atr_ratio = (atr_value / price) * 100

        # Volatilidad óptima para scalping - MÁS GENEROSO
        if 0.5 <= atr_ratio <= 3.0:  # Volatilidad perfecta para scalping
            score += 10
        elif 0.3 <= atr_ratio <= 5.0:  # Volatilidad buena
            score += 8
        elif atr_ratio <= 7.0:  # Volatilidad aceptable
            score += 6
        else:  # Volatilidad muy alta
            score += 3
    else:
        score += 8  # Score neutro si no hay datos de ATR

    # 5. ⏰ TIMING Y LIQUIDEZ (10%) - Horarios óptimos
    try:
        hour = datetime.now().hour

        # Horarios de alta liquidez y actividad
        if 8 <= hour <= 22:  # Horarios principales (Europa + América)
            score += 10
        elif 6 <= hour <= 24:  # Horarios extendidos
            score += 7
        elif 0 <= hour <= 2:  # Horarios asiáticos
            score += 5
        else:  # Horarios de baja liquidez
            score += 2
    except:
        score += 5  # Score neutro si hay error con la hora

    # Asegurar que el score esté en rango válido
    final_score = max(0, min(score, 100))

    return final_score

def calculate_price_targets(current_price, atr_value, signal_type, symbol):
    """Calcula objetivos de precio basados en ATR y volatilidad"""
    
    # Multiplicadores según el tipo de par - ULTRA-CONSERVADORES para máximo win rate
    if symbol.startswith('BTC'):
        atr_multiplier_tp = 1.5  # TP ultra-conservador para BTC (reducido de 2.0)
        atr_multiplier_sl = 0.8  # SL más ajustado (reducido de 1.0)
    elif symbol.startswith('ETH'):
        atr_multiplier_tp = 1.8  # TP ultra-conservador (reducido de 2.2)
        atr_multiplier_sl = 0.9  # SL más ajustado (reducido de 1.1)
    else:  # SOL y otros
        atr_multiplier_tp = 2.0  # TP ultra-conservador (reducido de 2.5)
        atr_multiplier_sl = 1.0  # SL más ajustado (reducido de 1.2)
    
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
