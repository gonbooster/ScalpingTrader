import os
import sys
import requests
import time
import numpy as np
import smtplib
from email.mime.text import MIMEText
from flask import Flask, jsonify
from datetime import datetime
import threading
import logging

# Configurar logging con rotación automática
import os
log_file = "bot_logs.txt"
MAX_LOG_LINES = 500  # Máximo 500 líneas

def rotate_logs():
    """Mantiene solo las últimas MAX_LOG_LINES líneas"""
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) > MAX_LOG_LINES:
                # Mantener solo las últimas MAX_LOG_LINES líneas
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines[-MAX_LOG_LINES:])
    except Exception as e:
        print(f"Error rotando logs: {e}")

# Crear handler para archivo
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Crear handler para consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formato de logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Rotar logs al inicio
rotate_logs()

# Log inicial
logger.info("🚀 SISTEMA DE LOGS INICIADO (Max: 500 líneas)")
logger.info(f"📝 Archivo: {log_file}")

# Logs inmediatos para debugging
logger.info("📦 Importaciones completadas")
logger.info("🔧 Iniciando configuración...")

# === CONFIGURACIÓN ===
VERSION = "v4.4-ADVANCED-FILTERS"
DEPLOY_TIME = datetime.now().strftime("%m/%d %H:%M")

# Múltiples pares como en tu script Pine
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "1m"
INTERVAL_15M = "15m"
INTERVAL_1H = "1h"

# Configuración de email desde variables de entorno
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Variables globales para múltiples pares
market_data = {
    "BTCUSDT": {"price": 0.0, "rsi": 0.0, "ema_fast": 0.0, "ema_slow": 0.0, "volume": 0.0, "score": 0, "last_signal": None, "pnl_daily": 0.0, "atr": 0.0, "last_signal_price": 0.0, "last_signal_time": 0},
    "ETHUSDT": {"price": 0.0, "rsi": 0.0, "ema_fast": 0.0, "ema_slow": 0.0, "volume": 0.0, "score": 0, "last_signal": None, "pnl_daily": 0.0, "atr": 0.0, "last_signal_price": 0.0, "last_signal_time": 0},
    "SOLUSDT": {"price": 0.0, "rsi": 0.0, "ema_fast": 0.0, "ema_slow": 0.0, "volume": 0.0, "score": 0, "last_signal": None, "pnl_daily": 0.0, "atr": 0.0, "last_signal_price": 0.0, "last_signal_time": 0}
}
signal_count = 0
last_analysis_time = None
using_simulation = False
bot_running = False

# === Logs de debugging después de definir variables ===
logger.info("🔧 Variables definidas correctamente")
logger.info(f"📧 EMAIL_FROM: {'✅' if EMAIL_FROM else '❌'}")
logger.info(f"📧 EMAIL_PASSWORD: {'✅' if EMAIL_PASSWORD else '❌'}")
logger.info(f"📧 EMAIL_TO: {'✅' if EMAIL_TO else '❌'}")
logger.info(f"📊 SYMBOLS: {SYMBOLS}")
logger.info(f"⏰ INTERVALS: {INTERVAL}, {INTERVAL_15M}, {INTERVAL_1H}")
logger.info(f"📊 market_data keys: {list(market_data.keys())}")
logger.info(f"🤖 bot_running: {bot_running}")
logger.info("✅ Configuración inicial completada - definiendo funciones...")

# === Funciones de detección de pares (como en Pine Script) ===
def detect_pair_type(symbol):
    """Detecta el tipo de par como en tu script Pine"""
    ticker = symbol.upper()
    if "BTC" in ticker:
        return "BTC"
    elif "ETH" in ticker:
        return "ETH"
    elif "SOL" in ticker:
        return "SOL"
    else:
        return "OTHER"

def get_adaptive_params(pair_type):
    """Parámetros adaptativos por par como en tu script Pine"""
    if pair_type == "BTC":
        return {
            "ema_fast": 10, "ema_slow": 21,
            "rsi_low": 50, "rsi_high": 65,
            "vol_multiplier": 1.8,
            "emoji": "🟠", "name": "BTC"
        }
    elif pair_type == "ETH":
        return {
            "ema_fast": 9, "ema_slow": 23,
            "rsi_low": 47, "rsi_high": 63,
            "vol_multiplier": 1.6,
            "emoji": "🟣", "name": "ETH"
        }
    elif pair_type == "SOL":
        return {
            "ema_fast": 7, "ema_slow": 20,
            "rsi_low": 45, "rsi_high": 68,
            "vol_multiplier": 1.4,
            "emoji": "🔵", "name": "SOL"
        }
    else:
        return {
            "ema_fast": 10, "ema_slow": 21,
            "rsi_low": 50, "rsi_high": 65,
            "vol_multiplier": 1.5,
            "emoji": "❓", "name": "OTHER"
        }

def is_valid_trading_hour():
    """Filtro de horarios como en tu script Pine (8-18 UTC)"""
    current_hour = datetime.utcnow().hour
    return 8 <= current_hour <= 18

def calculate_confidence_score(symbol, rsi, rsi_15m, volume, vol_avg, ema_fast, ema_slow, macro_trend, pair_type):
    """Score de confianza 0-100 como en tu script Pine"""
    score = 0

    # RSI 15m > 50: +25 puntos
    if rsi_15m > 50:
        score += 25

    # Volumen alto: +25, normal: +15
    if volume > vol_avg * 1.5:
        score += 25
    elif volume > vol_avg:
        score += 15

    # Macro trend para BTC: +20
    if pair_type == "BTC" and macro_trend:
        score += 20

    # Cruce de EMAs: +15
    if abs(ema_fast - ema_slow) > 0:
        score += 15

    # RSI en zona óptima: +15
    if 50 < rsi < 60:
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

# === Validación de configuración ===
def validate_config():
    """Valida que todas las variables de entorno necesarias estén configuradas"""
    required_vars = ["EMAIL_FROM", "EMAIL_PASSWORD", "EMAIL_TO"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Variables de entorno faltantes: {missing_vars}")
        logger.warning("El bot funcionará sin notificaciones por email")
        return False
    return True

# === Envío de email ===
def send_email(subject, body, html_body=None):
    """Envía email con diseño profesional HTML"""
    if not all([EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO]):
        logger.warning("Configuración de email incompleta. No se enviará notificación.")
        return False

    try:
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart('alternative')
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        # Texto plano como fallback
        msg.attach(MIMEText(body, 'plain'))

        # HTML si está disponible
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        logger.info(f"✅ Email enviado: {subject}")
        return True
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")
        return False

def create_professional_email(signal_type, symbol, price, rsi, rsi_15m, ema_fast, ema_slow, volume, vol_avg, confidence_score, atr_val, candle_change_percent, conditions, price_targets=None):
    """Crea email HTML profesional con % de vela"""

    # Colores según el tipo de señal
    if signal_type == "buy":
        color = "#28a745"
        emoji = "🟢"
        action = "COMPRA"
        bg_color = "#d4edda"
    else:
        color = "#dc3545"
        emoji = "🔴"
        action = "VENTA"
        bg_color = "#f8d7da"

    # Texto plano
    plain_text = f"""
{emoji} SEÑAL DE {action} - {symbol}

💰 Precio: ${price:,.2f}
📈 Cambio vela: {candle_change_percent:+.2f}%
📊 RSI: {rsi:.1f} (15m: {rsi_15m:.1f})
📈 EMA: {ema_fast:.2f} / {ema_slow:.2f}
📦 Volumen: {volume:,.0f} (Avg: {vol_avg:,.0f})
🎯 Score: {confidence_score}/100
🛡️ ATR: {atr_val:.2f}
⏰ Hora: {datetime.utcnow().strftime('%H:%M UTC')}

Condiciones cumplidas:
{chr(10).join([f"{'✅' if v else '❌'} {k}: {v}" for k, v in conditions.items()])}

🎯 OBJETIVOS DE PRECIO:
{f'''🟢 Take Profit: ${price_targets["take_profit"]:,.2f} (+{price_targets["expected_move_percent"]:.1f}%)
🔴 Stop Loss: ${price_targets["stop_loss"]:,.2f} (-{price_targets["risk_percent"]:.1f}%)
⚖️ Risk/Reward: 1:{price_targets["risk_reward_ratio"]:.1f}''' if price_targets else 'No calculado'}

⚠️ Solo para fines educativos. Gestiona tu riesgo responsablemente.
    """

    # HTML profesional
    html_text = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .header {{ background: {color}; color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .header p {{ margin: 10px 0 0 0; font-size: 16px; opacity: 0.9; }}
            .content {{ padding: 30px; }}
            .alert {{ background: {bg_color}; border-left: 5px solid {color}; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
            .metric {{ background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: {color}; }}
            .metric-label {{ font-size: 12px; color: #6c757d; margin-top: 5px; }}
            .conditions {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .condition {{ margin: 8px 0; font-size: 14px; }}
            .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; font-size: 12px; }}
            .candle-change {{ font-size: 20px; font-weight: bold; color: {color}; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{emoji} SEÑAL DE {action}</h1>
                <p>{symbol} • Scalping Bot PRO</p>
            </div>

            <div class="content">
                <div class="alert">
                    <strong>💰 Precio Actual: ${price:,.2f}</strong><br>
                    <span class="candle-change">📈 Cambio Vela: {candle_change_percent:+.2f}%</span>
                </div>

                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{rsi:.1f}</div>
                        <div class="metric-label">RSI (1m)</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{rsi_15m:.1f}</div>
                        <div class="metric-label">RSI (15m)</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{volume:,.0f}</div>
                        <div class="metric-label">Volumen</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{confidence_score}/100</div>
                        <div class="metric-label">Score</div>
                    </div>
                </div>

                <div class="conditions">
                    <h3>📋 Condiciones Cumplidas:</h3>
                    {chr(10).join([f'<div class="condition">{"✅" if v else "❌"} <strong>{k}:</strong> {v}</div>' for k, v in conditions.items()])}
                </div>

                {f'''<div style="background: #e8f5e8; border: 2px solid {color}; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: {color}; margin-top: 0;">🎯 OBJETIVOS DE PRECIO</h3>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0;">
                        <div style="text-align: center; padding: 10px; background: white; border-radius: 8px;">
                            <div style="font-size: 18px; font-weight: bold; color: #28a745;">🟢 Take Profit</div>
                            <div style="font-size: 16px; margin: 5px 0;">${price_targets["take_profit"]:,.2f}</div>
                            <div style="font-size: 14px; color: #28a745;">+{price_targets["expected_move_percent"]:.1f}%</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: white; border-radius: 8px;">
                            <div style="font-size: 18px; font-weight: bold; color: #dc3545;">🔴 Stop Loss</div>
                            <div style="font-size: 16px; margin: 5px 0;">${price_targets["stop_loss"]:,.2f}</div>
                            <div style="font-size: 14px; color: #dc3545;">-{price_targets["risk_percent"]:.1f}%</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: white; border-radius: 8px;">
                            <div style="font-size: 18px; font-weight: bold; color: #6c757d;">⚖️ Risk/Reward</div>
                            <div style="font-size: 16px; margin: 5px 0;">1:{price_targets["risk_reward_ratio"]:.1f}</div>
                            <div style="font-size: 14px; color: #6c757d;">Ratio</div>
                        </div>
                    </div>
                </div>''' if price_targets else ''}

                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>⚠️ Aviso:</strong> Esta señal es solo para fines educativos. Siempre gestiona tu riesgo responsablemente.
                </div>
            </div>

            <div class="footer">
                <p>🤖 Scalping Bot PRO • ⏰ {datetime.utcnow().strftime('%H:%M UTC')} • 🛡️ ATR: {atr_val:.2f}</p>
            </div>
        </div>
    </body>
    </html>
    """

    return plain_text.strip(), html_text

# === Carga datos Binance ===
def get_klines(symbol, interval, limit=100):
    global using_simulation
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        logger.info(f"📡 Conectando a Binance: {url}")

        response = requests.get(url, timeout=10)
        logger.info(f"📡 Respuesta Binance: Status {response.status_code}")

        data = response.json()

        if isinstance(data, dict) and "code" in data:
            logger.error(f"❌ ERROR BINANCE: {data}")

            if response.status_code == 451:
                logger.error("🚫 BINANCE BLOQUEADO: Ubicación geográfica restringida")
                logger.error("🌍 Solución: Usar servidor en Europa (Koyeb, Railway EU, etc)")

            using_simulation = True
            raise Exception(f"Binance API Error: {data}")

        logger.info("✅ Datos reales obtenidos de Binance")
        using_simulation = False
        return data
    except Exception as e:
        logger.error(f"❌ FALLO CRÍTICO conectando con Binance: {e}")
        logger.error("🛑 BOT DETENIDO - No hay datos reales disponibles")
        using_simulation = True
        raise Exception(f"No se pueden obtener datos reales: {e}")

def get_multi_timeframe_data(symbol):
    """Obtiene datos de múltiples timeframes como en tu script Pine"""
    try:
        # Datos principales (1m)
        data_1m = get_klines(symbol, INTERVAL, 100)
        # Datos 15m para confirmación
        data_15m = get_klines(symbol, INTERVAL_15M, 50)
        # Datos 1h para macro trend
        data_1h = get_klines(symbol, INTERVAL_1H, 30)

        return {
            "1m": data_1m,
            "15m": data_15m,
            "1h": data_1h
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo datos multi-timeframe: {e}")
        logger.error("🛑 ANÁLISIS DETENIDO - Sin datos reales de Binance")
        raise Exception(f"No se pueden obtener datos para {symbol}: {e}")

# Función de datos simulados ELIMINADA
# El bot ahora solo funciona con datos reales de Binance

# === Indicadores ===
def ema(values, period):
    if len(values) < period:
        return values[-1] if len(values) > 0 else 0
    return np.convolve(values, np.ones(period)/period, mode='valid')[-1]

def rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    deltas = np.diff(prices)
    ups = deltas.clip(min=0)
    downs = -deltas.clip(max=0)
    avg_gain = np.mean(ups[-period:])
    avg_loss = np.mean(downs[-period:])
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    return 100 - (100 / (1 + rs))

def atr(highs, lows, closes, period=14):
    """Calcula Average True Range con suavizado exponencial (como TradingView)"""
    if len(highs) < 2:
        return 0.0

    tr1 = highs[1:] - lows[1:]
    tr2 = np.abs(highs[1:] - closes[:-1])
    tr3 = np.abs(lows[1:] - closes[:-1])

    true_range = np.maximum(tr1, np.maximum(tr2, tr3))

    if len(true_range) < period:
        return np.mean(true_range)

    # ATR con suavizado exponencial
    alpha = 2.0 / (period + 1)
    atr_value = np.mean(true_range[:period])  # Primer valor como SMA

    for i in range(period, len(true_range)):
        atr_value = alpha * true_range[i] + (1 - alpha) * atr_value

    return atr_value

def calculate_adx(highs, lows, closes, period=14):
    """Calcula ADX para detectar tendencia vs lateralidad"""
    if len(highs) < period + 1:
        return 0.0

    # Directional Movement
    dm_plus = np.maximum(highs[1:] - highs[:-1], 0)
    dm_minus = np.maximum(lows[:-1] - lows[1:], 0)

    # True Range
    tr1 = highs[1:] - lows[1:]
    tr2 = np.abs(highs[1:] - closes[:-1])
    tr3 = np.abs(lows[1:] - closes[:-1])
    true_range = np.maximum(tr1, np.maximum(tr2, tr3))

    # Smoothed values
    alpha = 1.0 / period

    if len(true_range) < period:
        return 0.0

    # Initialize
    atr_smooth = np.mean(true_range[:period])
    di_plus = np.mean(dm_plus[:period]) / atr_smooth * 100 if atr_smooth > 0 else 0
    di_minus = np.mean(dm_minus[:period]) / atr_smooth * 100 if atr_smooth > 0 else 0

    # Calculate ADX
    dx_values = []
    for i in range(period, len(true_range)):
        atr_smooth = alpha * true_range[i] + (1 - alpha) * atr_smooth
        di_plus = alpha * dm_plus[i] + (1 - alpha) * di_plus
        di_minus = alpha * dm_minus[i] + (1 - alpha) * di_minus

        dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100 if (di_plus + di_minus) > 0 else 0
        dx_values.append(dx)

    # ADX is smoothed DX
    adx = np.mean(dx_values[-period:]) if len(dx_values) >= period else 0
    return adx

def validate_breakout_candle(data, signal_type):
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
    avg_volume = np.mean(volumes)

    # Rango de la vela
    candle_range = high_price - low_price
    body_size = abs(close_price - open_price)

    # Validaciones
    volume_check = volume > avg_volume * 1.2  # Volumen 20% superior
    body_dominance = body_size / candle_range > 0.6 if candle_range > 0 else False  # Cuerpo dominante

    if signal_type == "buy":
        # Para BUY: vela verde que cierre en el 60% superior
        green_candle = close_price > open_price
        upper_close = (close_price - low_price) / candle_range > 0.6 if candle_range > 0 else False
        return volume_check and body_dominance and green_candle and upper_close
    else:
        # Para SELL: vela roja que cierre en el 60% inferior
        red_candle = close_price < open_price
        lower_close = (high_price - close_price) / candle_range > 0.6 if candle_range > 0 else False
        return volume_check and body_dominance and red_candle and lower_close

def check_signal_distance(symbol, current_price, signal_type):
    """Verifica distancia mínima entre señales para evitar lateralidad"""
    if symbol not in market_data:
        return True

    last_signal = market_data[symbol].get("last_signal")
    last_price = market_data[symbol].get("last_signal_price", 0)
    last_time = market_data[symbol].get("last_signal_time", 0)

    current_time = time.time()

    # Filtro de tiempo: mínimo 5 minutos entre señales
    if last_time > 0 and (current_time - last_time) < 300:  # 5 minutos
        return False

    # Filtro de precio: mínimo 1% de movimiento
    if last_price > 0:
        price_change_percent = abs((current_price - last_price) / last_price) * 100
        if price_change_percent < 1.0:  # Menos de 1% de movimiento
            return False

    # Evitar señales opuestas inmediatas (BUY→SELL→BUY)
    if last_signal and last_signal != signal_type:
        if (current_time - last_time) < 600:  # 10 minutos para señales opuestas
            return False

    return True

def update_signal_tracking(symbol, signal_type, price):
    """Actualiza el tracking de señales para filtrado"""
    if symbol not in market_data:
        return

    market_data[symbol]["last_signal"] = signal_type
    market_data[symbol]["last_signal_price"] = price
    market_data[symbol]["last_signal_time"] = time.time()

# === Bot principal multi-par ===
def analyze_symbol(symbol):
    """Analiza un símbolo específico con la estrategia de tu script Pine"""
    try:
        logger.info(f"🔍 Analizando {symbol}...")

        # Detectar tipo de par
        pair_type = detect_pair_type(symbol)
        params = get_adaptive_params(pair_type)

        # Obtener datos multi-timeframe
        logger.info("📡 Obteniendo datos multi-timeframe...")
        mtf_data = get_multi_timeframe_data(symbol)
        # Si hay error, get_multi_timeframe_data ya lanza excepción

        # Procesar datos 1m (principal)
        data_1m = mtf_data["1m"]
        if not data_1m or len(data_1m) < 50:
            logger.error(f"❌ Datos insuficientes para {symbol}")
            return False

        # Procesar datos 15m y 1h
        data_15m = mtf_data["15m"]
        data_1h = mtf_data["1h"]
            
        # Calcular indicadores técnicos con parámetros adaptativos
        logger.info("📊 Calculando indicadores técnicos...")

        # Datos 1m (principal)
        closes_1m = np.array([float(c[4]) for c in data_1m])
        volumes_1m = np.array([float(c[5]) for c in data_1m])
        highs_1m = np.array([float(c[2]) for c in data_1m])
        lows_1m = np.array([float(c[3]) for c in data_1m])

        # EMAs adaptativas según el par
        ema_fast_val = ema(closes_1m, params["ema_fast"])
        ema_slow_val = ema(closes_1m, params["ema_slow"])

        # RSI principal
        rsi_1m = rsi(closes_1m)

        # ATR para stop-loss dinámico
        atr_val = atr(highs_1m, lows_1m, closes_1m)

        # ADX para detectar tendencia vs lateralidad
        adx_val = calculate_adx(highs_1m, lows_1m, closes_1m)

        # Volumen
        vol_now = volumes_1m[-1]
        vol_avg = np.mean(volumes_1m[-20:])

        # Datos 15m para confirmación
        if data_15m and len(data_15m) >= 14:
            closes_15m = np.array([float(c[4]) for c in data_15m])
            rsi_15m = rsi(closes_15m)
        else:
            rsi_15m = rsi_1m  # Fallback

        # Datos 1h para macro trend
        if data_1h and len(data_1h) >= 21:
            closes_1h = np.array([float(c[4]) for c in data_1h])
            ema_1h_fast = ema(closes_1h, 9)
            ema_1h_slow = ema(closes_1h, 21)
            macro_trend = ema_1h_fast > ema_1h_slow
        else:
            macro_trend = True  # Fallback

        close_now = closes_1m[-1]

        logger.info(f"💰 {symbol} Precio: ${close_now:.2f}")
        logger.info(f"📈 RSI: {rsi_1m:.2f} (15m: {rsi_15m:.2f})")
        logger.info(f"📊 EMA {params['ema_fast']}/{params['ema_slow']}: {ema_fast_val:.2f}/{ema_slow_val:.2f}")
        logger.info(f"📦 Volumen: {vol_now:,.0f} (Avg: {vol_avg:,.0f})")
        logger.info(f"🎯 ATR: {atr_val:.2f}, ADX: {adx_val:.1f}, Macro: {macro_trend}")

        # Evaluar condiciones de señales (como en tu script Pine)
        logger.info("🔍 Evaluando condiciones de trading...")

        # Detectar cruces de EMAs
        prev_ema_fast = ema(closes_1m[:-1], params["ema_fast"])
        prev_ema_slow = ema(closes_1m[:-1], params["ema_slow"])

        crossover_buy = prev_ema_fast <= prev_ema_slow and ema_fast_val > ema_slow_val
        crossunder_sell = prev_ema_fast >= prev_ema_slow and ema_fast_val < ema_slow_val

        # Condiciones de compra (como en Pine Script)
        buy_conditions = {
            "crossover": crossover_buy,
            "rsi_range": params["rsi_low"] < rsi_1m < params["rsi_high"],
            "volume": vol_now > vol_avg,
            "rsi_15m": rsi_15m > 50,
            "macro_trend": macro_trend if pair_type == "BTC" else True,
            "valid_hour": is_valid_trading_hour()
        }

        # Condiciones de venta (como en Pine Script)
        sell_conditions = {
            "crossunder": crossunder_sell,
            "rsi_range": 35 < rsi_1m < 55,
            "volume": vol_now > vol_avg,
            "rsi_15m": rsi_15m < 50,
            "macro_trend": not macro_trend if pair_type == "BTC" else True,
            "valid_hour": is_valid_trading_hour()
        }

        # Señales básicas
        buy_signal = all(buy_conditions.values())
        sell_signal = all(sell_conditions.values())

        # Señales fuertes (con volumen alto)
        strong_buy = (buy_signal and
                     vol_now > vol_avg * params["vol_multiplier"] and
                     params["rsi_low"] + 2 < rsi_1m < params["rsi_high"] - 2)

        strong_sell = (sell_signal and
                      vol_now > vol_avg * params["vol_multiplier"] and
                      38 < rsi_1m < 48)

        # Calcular score de confianza (0-100)
        confidence_score = calculate_confidence_score(
            symbol, rsi_1m, rsi_15m, vol_now, vol_avg,
            ema_fast_val, ema_slow_val, macro_trend, pair_type
        )

        # Actualizar datos del mercado
        market_data[symbol].update({
            "score": confidence_score,
            "atr": atr_val
        })

        # Log detallado de condiciones
        logger.info(f"🔍 Condiciones BUY: {buy_conditions}")
        logger.info(f"🔍 Condiciones SELL: {sell_conditions}")
        logger.info(f"🎯 Señal BUY: {buy_signal}, Strong: {strong_buy}")
        logger.info(f"🎯 Señal SELL: {sell_signal}, Strong: {strong_sell}")
        logger.info(f"📊 Score de confianza: {confidence_score}/100")
        logger.info(f"📝 Última señal {symbol}: {market_data[symbol]['last_signal']}")

        # Procesar señales con filtros avanzados
        current_signal = market_data[symbol]["last_signal"]

        # FILTROS ANTI-LATERALIDAD
        # 1. ADX mínimo para evitar lateralidad
        adx_filter = adx_val > 20  # ADX > 20 indica tendencia

        # 2. Validación de vela de ruptura
        breakout_buy = validate_breakout_candle(data_1m, "buy") if (buy_signal or strong_buy) else True
        breakout_sell = validate_breakout_candle(data_1m, "sell") if (sell_signal or strong_sell) else True

        # 3. Distancia mínima entre señales
        distance_buy = check_signal_distance(symbol, close_now, "buy") if (buy_signal or strong_buy) else True
        distance_sell = check_signal_distance(symbol, close_now, "sell") if (sell_signal or strong_sell) else True

        logger.info(f"🔍 FILTROS - ADX: {adx_val:.1f} ({'✅' if adx_filter else '❌'})")
        logger.info(f"🔍 FILTROS - Breakout BUY: {'✅' if breakout_buy else '❌'}, SELL: {'✅' if breakout_sell else '❌'}")
        logger.info(f"🔍 FILTROS - Distancia BUY: {'✅' if distance_buy else '❌'}, SELL: {'✅' if distance_sell else '❌'}")

        if (buy_signal or strong_buy) and current_signal != "buy" and adx_filter and breakout_buy and distance_buy:
            signal_type = "STRONG BUY" if strong_buy else "BUY"
            logger.info(f"🟢 ¡SEÑAL DE {signal_type} DETECTADA para {symbol}!")

            # Calcular % de cambio de la vela actual
            open_price = float(data_1m[0][1])  # Precio de apertura de la vela actual
            candle_change_percent = ((close_now - open_price) / open_price) * 100

            # Condiciones para el email
            conditions = {
                "Cruce EMA": crossover_buy,
                f"RSI {params['rsi_low']}-{params['rsi_high']}": f"{rsi_1m:.1f}",
                "Volumen > Promedio": vol_now > vol_avg,
                "RSI 15m > 50": f"{rsi_15m:.1f}",
                "Macro Trend": macro_trend if pair_type == 'BTC' else 'N/A',
                "Horario Trading": is_valid_trading_hour()
            }

            # Calcular objetivos de precio
            price_targets = calculate_price_targets(close_now, atr_val, "buy", symbol)

            # Crear email profesional
            plain_text, html_text = create_professional_email(
                "buy", symbol, close_now, rsi_1m, rsi_15m,
                ema_fast_val, ema_slow_val, vol_now, vol_avg,
                confidence_score, atr_val, candle_change_percent, conditions, price_targets
            )

            if send_email(f"🟢 {signal_type} - {symbol} Scalping Bot", plain_text, html_text):
                global signal_count
                signal_count += 1
                market_data[symbol]["last_signal"] = "buy"
                update_signal_tracking(symbol, "buy", close_now)  # Tracking avanzado
                logger.info(f"✅ Email {signal_type} enviado - {symbol} - Señal #{signal_count}")
            else:
                logger.error(f"❌ Error enviando email {signal_type} - {symbol}")

        elif (sell_signal or strong_sell) and current_signal != "sell" and adx_filter and breakout_sell and distance_sell:
            signal_type = "STRONG SELL" if strong_sell else "SELL"
            logger.info(f"🔴 ¡SEÑAL DE {signal_type} DETECTADA para {symbol}!")

            # Calcular % de cambio de la vela actual
            open_price = float(data_1m[0][1])  # Precio de apertura de la vela actual
            candle_change_percent = ((close_now - open_price) / open_price) * 100

            # Condiciones para el email
            conditions = {
                "Cruce EMA": crossunder_sell,
                "RSI 35-55": f"{rsi_1m:.1f}",
                "Volumen > Promedio": vol_now > vol_avg,
                "RSI 15m < 50": f"{rsi_15m:.1f}",
                "Macro Trend": not macro_trend if pair_type == 'BTC' else 'N/A',
                "Horario Trading": is_valid_trading_hour()
            }

            # Calcular objetivos de precio
            price_targets = calculate_price_targets(close_now, atr_val, "sell", symbol)

            # Crear email profesional
            plain_text, html_text = create_professional_email(
                "sell", symbol, close_now, rsi_1m, rsi_15m,
                ema_fast_val, ema_slow_val, vol_now, vol_avg,
                confidence_score, atr_val, candle_change_percent, conditions, price_targets
            )

            if send_email(f"🔴 {signal_type} - {symbol} Scalping Bot", plain_text, html_text):
                signal_count += 1
                market_data[symbol]["last_signal"] = "sell"
                update_signal_tracking(symbol, "sell", close_now)  # Tracking avanzado
                logger.info(f"✅ Email {signal_type} enviado - {symbol} - Señal #{signal_count}")
            else:
                logger.error(f"❌ Error enviando email {signal_type} - {symbol}")

        else:
            logger.info(f"⏸️ {symbol} - Sin señales nuevas (Score: {confidence_score}/100)")

        logger.info(f"✅ Análisis de {symbol} completado")
        return True

    except Exception as e:
        logger.error(f"❌ Error analizando {symbol}: {e}")
        return False

def check_signals():
    """Función principal que analiza todos los símbolos"""
    global last_analysis_time

    try:
        logger.info("🔍 Iniciando análisis multi-par...")
        last_analysis_time = datetime.now()

        success_count = 0
        for symbol in SYMBOLS:
            try:
                if analyze_symbol(symbol):
                    success_count += 1
                time.sleep(1)  # Pequeña pausa entre símbolos
            except Exception as e:
                logger.error(f"❌ ERROR CRÍTICO procesando {symbol}: {e}")

                # Si es error de Binance, detener todo
                if "Binance API Error" in str(e) or "No se pueden obtener datos" in str(e):
                    logger.error("🛑 DETENIENDO BOT - Binance no disponible")
                    logger.error("🌍 Solución: Usar servidor en Europa (Koyeb, Railway EU, etc)")
                    global using_simulation
                    using_simulation = True
                    return False

        if success_count == 0:
            logger.error("🛑 NINGÚN ANÁLISIS EXITOSO - Bot detenido")
            return False

        logger.info(f"✅ Análisis completado: {success_count}/{len(SYMBOLS)} símbolos exitosos")
        return success_count > 0

    except Exception as e:
        logger.error(f"❌ Error en análisis principal: {e}")
        return False

def get_rsi_color(rsi):
    """Determina el color del RSI basado en niveles"""
    if rsi <= 30:
        return "oversold"  # Verde - sobreventa
    elif rsi >= 70:
        return "overbought"  # Rojo - sobrecompra
    else:
        return "neutral"  # Amarillo - neutral

# === Flask App ===
app = Flask(__name__)

@app.route("/")
def home():
    global last_analysis_time, signal_count, using_simulation, bot_running, market_data

    if using_simulation:
        status = "🔴 ERROR - Binance bloqueado"
    elif bot_running and last_analysis_time:
        status = "🟢 ACTIVO"
    else:
        status = "🟡 INICIANDO"
    last_time = last_analysis_time.strftime('%H:%M:%S') if last_analysis_time else "N/A"
    if using_simulation:
        data_source = "🚫 ERROR: Binance bloqueado - Servidor en ubicación restringida"
    else:
        data_source = "📡 Datos reales de Binance"
    email_status = "✅ Configurado" if validate_config() else "⚠️ No configurado"
    current_hour = datetime.utcnow().hour
    trading_hour_status = "✅ Horario óptimo" if is_valid_trading_hour() else "⚠️ Fuera de horario"
    
    # Generar tarjetas de criptomonedas
    crypto_cards = ""
    total_score = 0
    active_pairs = 0

    for symbol in SYMBOLS:
        data = market_data[symbol]
        pair_type = detect_pair_type(symbol)
        params = get_adaptive_params(pair_type)

        if data["price"] > 0:
            active_pairs += 1
            total_score += data["score"]

        # Determinar estado de señal
        if data["last_signal"] == "buy":
            signal_class = "signal-buy"
            signal_text = "🟢 COMPRA ACTIVA"
        elif data["last_signal"] == "sell":
            signal_class = "signal-sell"
            signal_text = "🔴 VENTA ACTIVA"
        else:
            signal_class = "signal-wait"
            signal_text = "⏸️ ESPERANDO"

        crypto_cards += f"""
        <div class="crypto-card {pair_type.lower()}">
            <div class="crypto-header">
                <div class="crypto-name">{params['emoji']} {params['name']}</div>
                <div style="text-align: right;">
                    <div class="crypto-price">${data['price']:.2f}</div>
                    <div class="last-update">Actualizado: {datetime.now().strftime('%H:%M:%S')}</div>
                </div>
            </div>

            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value rsi-{get_rsi_color(data['rsi'])}">{data['rsi']:.1f}</div>
                    <div class="metric-label">RSI</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${data['ema_fast']:.2f}</div>
                    <div class="metric-label">EMA {params['ema_fast']}</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${data['ema_slow']:.2f}</div>
                    <div class="metric-label">EMA {params['ema_slow']}</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${data['atr']:.4f}</div>
                    <div class="metric-label">ATR</div>
                </div>
            </div>

            <!-- Nuevo: Indicadores de tendencia -->
            <div class="trend-indicators">
                <div class="trend-item">
                    <span class="trend-label">📈 Tendencia:</span>
                    <span class="trend-value {'trend-bullish' if data['ema_fast'] > data['ema_slow'] else 'trend-bearish'}">
                        {'🟢 Alcista' if data['ema_fast'] > data['ema_slow'] else '🔴 Bajista'}
                    </span>
                </div>
                <div class="trend-item">
                    <span class="trend-label">💪 Momentum:</span>
                    <span class="trend-value {'momentum-strong' if abs(data['rsi'] - 50) > 20 else 'momentum-weak'}">
                        {'🔥 Fuerte' if abs(data['rsi'] - 50) > 20 else '😴 Débil'}
                    </span>
                </div>
            </div>

            <div class="signal-status {signal_class}">
                {signal_text}
            </div>

            <div style="margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span><strong>Score de Confianza:</strong></span>
                    <span><strong>{data["score"]}/100</strong></span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {data["score"]}%;"></div>
                </div>
            </div>
        </div>
        """

    avg_score = f"{total_score // max(active_pairs, 1)}/100" if active_pairs > 0 else "0/100"
    status_class = "active" if status == "🟢 ACTIVO" else "waiting"

    # Crear HTML directamente (más simple y confiable)
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 Scalping PRO - Multi-Par Dashboard</title>
        <meta http-equiv="refresh" content="30">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }}
            .container {{
                max-width: 1400px; margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white; padding: 30px; text-align: center;
            }}
            .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
            .version {{ font-size: 0.9em; opacity: 0.8; margin-top: 15px; }}
            .status-bar {{
                background: #f8f9fa; padding: 20px; display: flex;
                justify-content: space-between; flex-wrap: wrap;
            }}
            .status-item {{
                margin: 5px; padding: 10px 15px; background: white;
                border-radius: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .status-active {{ color: #28a745; }}
            .status-waiting {{ color: #ffc107; }}
            .main-content {{ padding: 30px; }}
            .crypto-grid {{
                display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px; margin-bottom: 30px;
            }}
            .crypto-card {{
                background: white; border-radius: 15px; padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-left: 5px solid;
            }}
            .crypto-card.btc {{ border-left-color: #f7931a; }}
            .crypto-card.eth {{ border-left-color: #627eea; }}
            .crypto-card.sol {{ border-left-color: #9945ff; }}
            .crypto-header {{
                display: flex; justify-content: space-between;
                align-items: center; margin-bottom: 20px;
            }}
            .crypto-name {{ font-size: 1.5em; font-weight: bold; }}
            .crypto-price {{ font-size: 1.8em; font-weight: bold; color: #2c3e50; }}
            .metrics-grid {{
                display: grid; grid-template-columns: repeat(2, 1fr);
                gap: 15px; margin-bottom: 20px;
            }}
            .metric {{ background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; }}
            .metric-value {{ font-size: 1.4em; font-weight: bold; color: #2c3e50; }}
            .metric-label {{ font-size: 0.9em; color: #6c757d; margin-top: 5px; }}
            .rsi-oversold {{ color: #28a745 !important; }}
            .rsi-overbought {{ color: #dc3545 !important; }}
            .rsi-neutral {{ color: #ffc107 !important; }}
            .trend-indicators {{
                display: flex; justify-content: space-between;
                margin: 15px 0; padding: 10px; background: #f8f9fa;
                border-radius: 8px; font-size: 0.9em;
            }}
            .trend-item {{ display: flex; align-items: center; gap: 5px; }}
            .trend-label {{ font-weight: 500; color: #6c757d; }}
            .trend-bullish {{ color: #28a745; font-weight: bold; }}
            .trend-bearish {{ color: #dc3545; font-weight: bold; }}
            .momentum-strong {{ color: #fd7e14; font-weight: bold; }}
            .momentum-weak {{ color: #6c757d; }}
            .price-change {{
                font-size: 0.9em; margin-left: 10px; padding: 2px 8px;
                border-radius: 12px; font-weight: bold;
            }}
            .price-up {{ background: #d4edda; color: #155724; }}
            .price-down {{ background: #f8d7da; color: #721c24; }}
            .last-update {{
                font-size: 0.8em; color: #6c757d;
                text-align: center; margin-top: 10px;
            }}
            .signal-status {{
                padding: 15px; border-radius: 10px; text-align: center;
                font-weight: bold; margin-top: 15px;
            }}
            .signal-buy {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; }}
            .signal-sell {{ background: linear-gradient(135deg, #dc3545, #fd7e14); color: white; }}
            .signal-wait {{ background: linear-gradient(135deg, #6c757d, #adb5bd); color: white; }}
            .confidence-bar {{
                width: 100%; height: 20px; background: #e9ecef;
                border-radius: 10px; overflow: hidden; margin-top: 10px;
            }}
            .confidence-fill {{
                height: 100%; background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
                transition: width 0.3s ease;
            }}
            .stats-section {{
                background: white; border-radius: 15px; padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 30px;
            }}
            .stats-grid {{
                display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
            .stat-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
            .stat-label {{ color: #6c757d; margin-top: 5px; }}
            .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Scalping PRO Dashboard</h1>
                <p>Análisis Multi-Par Avanzado • BTC/ETH/SOL</p>
                <div class="version">{VERSION} • Deploy: {DEPLOY_TIME}</div>
            </div>

            <div class="status-bar">
                <div class="status-item status-{status_class}">🤖 Estado: {status}</div>
                <div class="status-item">📧 Email: {email_status}</div>
                <div class="status-item">⏰ Horario: {trading_hour_status}</div>
                <div class="status-item">📡 Fuente: {data_source}</div>
                <div class="status-item">🔔 Señales: {signal_count}</div>
                <div class="status-item">⏱️ Último: {last_time}</div>
            </div>

            <div class="main-content">
                <div class="crypto-grid">
                    {crypto_cards}
                </div>

                <div class="stats-section">
                    <h2 style="margin-bottom: 20px; color: #2c3e50;">📊 Estadísticas Generales</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">{signal_count}</div>
                            <div class="stat-label">Señales Enviadas</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{active_pairs}</div>
                            <div class="stat-label">Pares Activos</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{avg_score}</div>
                            <div class="stat-label">Score Promedio</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{current_hour}:00 UTC</div>
                            <div class="stat-label">Hora Actual</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{'🟢' if not using_simulation else '🔴'}</div>
                            <div class="stat-label">Conexión API</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">60s</div>
                            <div class="stat-label">Frecuencia</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="footer">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
                    <div>
                        <p>🔄 Auto-refresh cada 30 segundos • ⚡ Análisis cada 60 segundos</p>
                        <p>⚠️ Solo para fines educativos • Gestiona tu riesgo responsablemente</p>
                    </div>
                    <div style="text-align: right;">
                        <p><strong>🎯 Estrategia Multi-Par</strong></p>
                        <p>📊 RSI + EMA + ATR + Score</p>
                        <p>🌍 Horario: 8:00-18:00 UTC</p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return html

# Endpoint /status eliminado - usar /health para monitoreo

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# Endpoint /debug eliminado - información disponible en dashboard principal

# Endpoint /test eliminado - análisis automático cada 60 segundos

@app.route("/test-email")
def test_email():
    """Endpoint para enviar email de prueba"""
    logger.info("📧 TEST: Enviando email de prueba...")

    try:
        # Crear mensaje de prueba
        test_message = f"""🧪 EMAIL DE PRUEBA - Scalping Bot

✅ ¡Tu bot está funcionando correctamente!

🤖 Estado: Activo y monitoreando
📊 Pares: BTC, ETH, SOL
⏰ Hora de prueba: {datetime.now().strftime('%H:%M:%S')}
📡 Conexión: Binance API funcionando
📧 Email: Sistema configurado correctamente

🎯 Próximos pasos:
- El bot analizará cada 60 segundos
- Recibirás emails cuando detecte señales válidas
- Dashboard disponible en http://localhost:5000

⚠️ Este es un email de prueba. Los emails reales incluirán:
- Precio exacto de entrada
- Análisis técnico completo
- Score de confianza
- Condiciones del mercado

¡Tu bot está listo para detectar oportunidades! 🚀"""

        # Enviar email
        if send_email("🧪 TEST - Scalping Bot Funcionando", test_message):
            logger.info("✅ Email de prueba enviado exitosamente")
            return jsonify({
                "test_result": "success",
                "message": "Email de prueba enviado correctamente",
                "email_to": EMAIL_TO,
                "timestamp": datetime.now().isoformat()
            })
        else:
            logger.error("❌ Error enviando email de prueba")
            return jsonify({
                "test_result": "failed",
                "message": "Error enviando email de prueba",
                "timestamp": datetime.now().isoformat()
            })

    except Exception as e:
        logger.error(f"❌ Error en test de email: {e}")
        return jsonify({
            "test_result": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

# === Logs después de definir todas las funciones ===
logger.info("🔧 Todas las funciones definidas correctamente")
logger.info("🔧 Definiendo rutas Flask...")

@app.route("/logs")
def view_logs():
    """Endpoint para ver los logs del bot"""
    try:
        if os.path.exists("bot_logs.txt"):
            with open("bot_logs.txt", "r", encoding="utf-8") as f:
                logs = f.read()

            # Obtener últimas 100 líneas
            log_lines = logs.split('\n')
            recent_logs = log_lines[-100:] if len(log_lines) > 100 else log_lines

            return f"""
            <html>
            <head>
                <title>🤖 Bot Logs - Render Debug</title>
                <meta http-equiv="refresh" content="10">
                <style>
                    body {{ font-family: monospace; background: #1a1a1a; color: #00ff00; padding: 20px; }}
                    .log-container {{ background: #000; padding: 20px; border-radius: 10px; }}
                    .log-line {{ margin: 2px 0; }}
                    .error {{ color: #ff4444; }}
                    .warning {{ color: #ffaa00; }}
                    .info {{ color: #00ff00; }}
                    .header {{ color: #00aaff; font-size: 18px; margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">🤖 SCALPING BOT LOGS - ÚLTIMAS 100 LÍNEAS</div>
                <div class="header">🔄 Auto-refresh cada 10 segundos</div>
                <div class="log-container">
                    {'<br>'.join([f'<div class="log-line">{line}</div>' for line in recent_logs if line.strip()])}
                </div>
            </body>
            </html>
            """
        else:
            return jsonify({
                "error": "Archivo de logs no encontrado",
                "message": "El bot aún no ha generado logs",
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"❌ Error leyendo logs: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route("/logs-json")
def view_logs_json():
    """Endpoint para ver los logs en formato JSON"""
    try:
        if os.path.exists("bot_logs.txt"):
            with open("bot_logs.txt", "r", encoding="utf-8") as f:
                logs = f.read()

            log_lines = logs.split('\n')
            recent_logs = [line for line in log_lines[-50:] if line.strip()]

            return jsonify({
                "logs": recent_logs,
                "total_lines": len(log_lines),
                "showing_last": len(recent_logs),
                "file_exists": True,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "logs": [],
                "file_exists": False,
                "error": "Archivo de logs no encontrado",
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

# Endpoint /force-start eliminado - inicio automático

# === Loop de monitoreo ===
def monitoring_loop():
    global bot_running

    logger.info("🚀 HILO DE MONITOREO INICIADO")
    logger.info(f"🧵 Thread ID: {threading.current_thread().ident}")
    logger.info(f"🧵 Thread Name: {threading.current_thread().name}")
    logger.info("🚀 Iniciando bot de trading multi-par...")
    logger.info(f"📊 Monitoreando {', '.join(SYMBOLS)} cada 60 segundos")

    try:
        email_configured = validate_config()
        logger.info(f"📧 Validación email: {email_configured}")
        if email_configured:
            logger.info("📧 Enviando alertas por email cuando detecte señales")
        else:
            logger.warning("📧 Email no configurado - solo monitoreo web")

        bot_running = True
        logger.info("✅ Bot marcado como running - iniciando loop de análisis")
        logger.info(f"🔄 Variables globales: bot_running={bot_running}")

    except Exception as e:
        logger.error(f"❌ Error en inicialización del hilo: {e}")
        logger.error(f"❌ Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

    cycle_count = 1
    logger.info("🔄 Entrando en loop principal infinito...")

    while True:
        try:
            # Rotar logs cada 10 ciclos para evitar saturación
            if cycle_count % 10 == 0:
                rotate_logs()

            logger.info(f"🔄 Ciclo #{cycle_count}")

            success = check_signals()

            if success:
                logger.info(f"✅ Ciclo #{cycle_count} completado")
            else:
                logger.warning(f"⚠️ Ciclo #{cycle_count} falló")

            logger.info(f"💤 Sleep 60s...")
            time.sleep(60)
            cycle_count += 1

        except Exception as e:
            logger.error(f"❌ Error en loop principal (ciclo #{cycle_count}): {e}")
            logger.error(f"❌ Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
            logger.info("⏰ Esperando 60 segundos antes de reintentar...")
            time.sleep(60)
            cycle_count += 1

# === Logs antes del main ===
logger.info("🔧 Todas las rutas Flask definidas")
logger.info("🔧 Llegando al punto de ejecución principal...")
logger.info(f"🔧 __name__ = '{__name__}'")
logger.info("🔧 Verificando si es __main__...")

# === Función de inicialización ===
def initialize_bot():
    """Función para inicializar el bot (funciona tanto en __main__ como en import)"""
    logger.info("🚀 INICIANDO SCALPING BOT...")
    logger.info("=" * 50)
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"🖥️ Platform: {sys.platform}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"📝 Log file: {os.path.abspath('bot_logs.txt')}")

    # Mostrar configuración
    logger.info(f"📊 Símbolos: {', '.join(SYMBOLS)}")
    logger.info(f"⏰ Intervalos: {INTERVAL}, {INTERVAL_15M}, {INTERVAL_1H}")

    try:
        email_config = validate_config()
        logger.info(f"📧 Email configurado: {email_config}")
        logger.info(f"📧 EMAIL_FROM: {'✅ Set' if EMAIL_FROM else '❌ Missing'}")
        logger.info(f"📧 EMAIL_PASSWORD: {'✅ Set' if EMAIL_PASSWORD else '❌ Missing'}")
        logger.info(f"📧 EMAIL_TO: {'✅ Set' if EMAIL_TO else '❌ Missing'}")
    except Exception as e:
        logger.error(f"❌ Error validando email: {e}")

    # Obtener puerto (Koyeb usa 8000, Render usa PORT)
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🌐 Puerto configurado: {port}")

    # Para Render: usar un enfoque más simple sin hilos complejos
    logger.info("🔄 Configurando monitoreo para Render...")

    # Hacer un análisis inicial inmediatamente
    logger.info("🔄 Ejecutando análisis inicial...")
    try:
        result = check_signals()
        logger.info(f"✅ Análisis inicial completado: {result}")
    except Exception as e:
        logger.error(f"❌ Error en análisis inicial: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

    # Iniciar hilo de monitoreo (más simple para Render)
    logger.info("🔄 Iniciando hilo de monitoreo...")
    try:
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        logger.info(f"🧵 Thread creado: {monitoring_thread}")
        monitoring_thread.start()
        logger.info("✅ Hilo de monitoreo iniciado")
        logger.info(f"🧵 Thread alive: {monitoring_thread.is_alive()}")
    except Exception as e:
        logger.error(f"❌ Error iniciando hilo: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

    logger.info(f"🌐 Iniciando servidor web en puerto {port}...")
    logger.info("=" * 50)

    # Forzar flush de logs
    sys.stdout.flush()

    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

# === Inicio de la aplicación ===
if __name__ == "__main__":
    logger.info("✅ Ejecutando desde __main__")
    initialize_bot()
else:
    logger.info(f"⚠️ Ejecutando como import desde: {__name__}")
    logger.info("🔧 Forzando inicialización para Render...")
    initialize_bot()
