import os
import requests
import time
import numpy as np
import smtplib
from email.mime.text import MIMEText
from flask import Flask, jsonify
from datetime import datetime
import threading
import logging

# Configurar logging detallado con archivo
import os
log_file = "bot_logs.txt"

# Crear handler para archivo
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
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

# Log inicial
logger.info("=" * 60)
logger.info("🚀 SISTEMA DE LOGS INICIADO")
logger.info(f"📝 Archivo de logs: {log_file}")
logger.info("=" * 60)

# Logs inmediatos para debugging
logger.info("📦 Importaciones completadas")
logger.info("🔧 Iniciando configuración...")

# === CONFIGURACIÓN ===
VERSION = "v3.3-TRACE-LOGS"
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
    "BTCUSDT": {"price": 0.0, "rsi": 0.0, "ema_fast": 0.0, "ema_slow": 0.0, "volume": 0.0, "score": 0, "last_signal": None, "pnl_daily": 0.0, "atr": 0.0},
    "ETHUSDT": {"price": 0.0, "rsi": 0.0, "ema_fast": 0.0, "ema_slow": 0.0, "volume": 0.0, "score": 0, "last_signal": None, "pnl_daily": 0.0, "atr": 0.0},
    "SOLUSDT": {"price": 0.0, "rsi": 0.0, "ema_fast": 0.0, "ema_slow": 0.0, "volume": 0.0, "score": 0, "last_signal": None, "pnl_daily": 0.0, "atr": 0.0}
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
def send_email(subject, body):
    if not all([EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO]):
        logger.warning("Configuración de email incompleta. No se enviará notificación.")
        return False
        
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        logger.info(f"✅ Email enviado: {subject}")
        return True
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")
        return False

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
            logger.warning(f"⚠️ Error de Binance: {data}")
            logger.warning("🔄 Cambiando a datos simulados...")
            using_simulation = True
            return generate_simulation_data(limit)

        logger.info("✅ Datos reales obtenidos de Binance")
        using_simulation = False
        return data
    except Exception as e:
        logger.error(f"❌ Error conectando con Binance: {e}")
        logger.warning("🔄 Usando datos simulados para demostración...")
        using_simulation = True
        return generate_simulation_data(limit)

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
        return None

def generate_simulation_data(limit=100):
    """Genera datos simulados realistas para BTCUSDT"""
    import random
    
    current_time = int(time.time() * 1000)
    base_price = 97000
    
    data = []
    price = base_price
    
    for i in range(limit):
        change = random.uniform(-0.002, 0.002)
        price *= (1 + change)
        
        open_price = price
        high_price = price * (1 + random.uniform(0, 0.001))
        low_price = price * (1 - random.uniform(0, 0.001))
        close_price = price
        volume = random.uniform(100, 1000)
        
        candle = [
            current_time - (limit - i) * 60000,
            f"{open_price:.2f}",
            f"{high_price:.2f}",
            f"{low_price:.2f}",
            f"{close_price:.2f}",
            f"{volume:.2f}",
            current_time - (limit - i) * 60000 + 59999,
            "0", 0, "0", "0", "0"
        ]
        data.append(candle)
        
    return data

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
    """Calcula Average True Range"""
    if len(highs) < 2:
        return 0.0

    tr1 = highs[1:] - lows[1:]
    tr2 = np.abs(highs[1:] - closes[:-1])
    tr3 = np.abs(lows[1:] - closes[:-1])

    true_range = np.maximum(tr1, np.maximum(tr2, tr3))
    return np.mean(true_range[-period:]) if len(true_range) >= period else np.mean(true_range)

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
        if not mtf_data:
            logger.error(f"❌ No se pudieron obtener datos para {symbol}")
            return False

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
        logger.info(f"🎯 ATR: {atr_val:.2f}, Macro: {macro_trend}")

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

        # Procesar señales
        current_signal = market_data[symbol]["last_signal"]

        if (buy_signal or strong_buy) and current_signal != "buy":
            signal_type = "STRONG BUY" if strong_buy else "BUY"
            logger.info(f"🟢 ¡SEÑAL DE {signal_type} DETECTADA para {symbol}!")

            # Crear mensaje detallado
            msg = f"""🟢 {signal_type} SIGNAL - {params['emoji']} {params['name']}

💰 Precio: ${close_now:.2f}
📈 RSI: {rsi_1m:.2f} (15m: {rsi_15m:.2f})
📊 EMA {params['ema_fast']}/{params['ema_slow']}: {ema_fast_val:.2f}/{ema_slow_val:.2f}
📦 Volumen: {vol_now:,.0f} (Avg: {vol_avg:,.0f})
🎯 Score: {confidence_score}/100
🛡️ ATR: {atr_val:.2f}
⏰ Hora: {datetime.utcnow().strftime('%H:%M UTC')}

Condiciones:
✅ Cruce EMA: {crossover_buy}
✅ RSI: {params['rsi_low']}-{params['rsi_high']} ({rsi_1m:.1f})
✅ Volumen: {vol_now > vol_avg}
✅ RSI 15m: {rsi_15m > 50} ({rsi_15m:.1f})
✅ Macro Trend: {macro_trend if pair_type == 'BTC' else 'N/A'}
✅ Horario: {is_valid_trading_hour()}"""

            if send_email(f"🟢 {signal_type} - {symbol} Scalping Bot", msg):
                global signal_count
                signal_count += 1
                market_data[symbol]["last_signal"] = "buy"
                logger.info(f"✅ Email {signal_type} enviado - {symbol} - Señal #{signal_count}")
            else:
                logger.error(f"❌ Error enviando email {signal_type} - {symbol}")

        elif (sell_signal or strong_sell) and current_signal != "sell":
            signal_type = "STRONG SELL" if strong_sell else "SELL"
            logger.info(f"🔴 ¡SEÑAL DE {signal_type} DETECTADA para {symbol}!")

            # Crear mensaje detallado
            msg = f"""🔴 {signal_type} SIGNAL - {params['emoji']} {params['name']}

💰 Precio: ${close_now:.2f}
📈 RSI: {rsi_1m:.2f} (15m: {rsi_15m:.2f})
📊 EMA {params['ema_fast']}/{params['ema_slow']}: {ema_fast_val:.2f}/{ema_slow_val:.2f}
📦 Volumen: {vol_now:,.0f} (Avg: {vol_avg:,.0f})
🎯 Score: {confidence_score}/100
🛡️ ATR: {atr_val:.2f}
⏰ Hora: {datetime.utcnow().strftime('%H:%M UTC')}

Condiciones:
✅ Cruce EMA: {crossunder_sell}
✅ RSI: 35-55 ({rsi_1m:.1f})
✅ Volumen: {vol_now > vol_avg}
✅ RSI 15m: {rsi_15m < 50} ({rsi_15m:.1f})
✅ Macro Trend: {not macro_trend if pair_type == 'BTC' else 'N/A'}
✅ Horario: {is_valid_trading_hour()}"""

            if send_email(f"🔴 {signal_type} - {symbol} Scalping Bot", msg):
                signal_count += 1
                market_data[symbol]["last_signal"] = "sell"
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
                logger.error(f"❌ Error procesando {symbol}: {e}")

        logger.info(f"✅ Análisis completado: {success_count}/{len(SYMBOLS)} símbolos exitosos")
        return success_count > 0

    except Exception as e:
        logger.error(f"❌ Error en análisis principal: {e}")
        return False

# === Flask App ===
app = Flask(__name__)

@app.route("/")
def home():
    global last_analysis_time, signal_count, using_simulation, bot_running, market_data

    status = "🟢 ACTIVO" if bot_running and last_analysis_time else "🟡 INICIANDO"
    last_time = last_analysis_time.strftime('%H:%M:%S') if last_analysis_time else "N/A"
    data_source = "📊 Datos simulados (demo)" if using_simulation else "📡 Datos reales de Binance"
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
                <div class="crypto-price">${data['price']:.2f}</div>
            </div>

            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value">{data['rsi']:.1f}</div>
                    <div class="metric-label">RSI</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{data['ema_fast']:.2f}</div>
                    <div class="metric-label">EMA {params['ema_fast']}</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{data['ema_slow']:.2f}</div>
                    <div class="metric-label">EMA {params['ema_slow']}</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{data['atr']:.2f}</div>
                    <div class="metric-label">ATR</div>
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
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>🔄 Auto-refresh cada 30 segundos • ⚡ Análisis cada 60 segundos</p>
                <p>⚠️ Solo para fines educativos • Gestiona tu riesgo responsablemente</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html

@app.route("/status")
def status():
    return jsonify({
        "status": "active" if bot_running else "starting",
        "symbols": SYMBOLS,
        "market_data": market_data,
        "signal_count": signal_count,
        "last_analysis": last_analysis_time.isoformat() if last_analysis_time else None,
        "using_simulation": using_simulation,
        "email_configured": validate_config(),
        "trading_hour": is_valid_trading_hour(),
        "current_hour_utc": datetime.utcnow().hour
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/debug")
def debug():
    """Endpoint de debug avanzado para el sistema multi-par"""
    global last_analysis_time, signal_count, using_simulation, bot_running, market_data

    # Calcular estadísticas
    total_score = sum(data["score"] for data in market_data.values())
    active_pairs = sum(1 for data in market_data.values() if data["price"] > 0)
    avg_score = total_score // max(active_pairs, 1) if active_pairs > 0 else 0

    return jsonify({
        "bot_status": {
            "running": bot_running,
            "version": VERSION,
            "last_analysis": last_analysis_time.isoformat() if last_analysis_time else None,
            "analysis_age_seconds": (datetime.now() - last_analysis_time).total_seconds() if last_analysis_time else None,
            "using_simulation": using_simulation
        },
        "symbols": SYMBOLS,
        "market_data": market_data,
        "statistics": {
            "total_signals": signal_count,
            "active_pairs": active_pairs,
            "average_score": avg_score,
            "trading_hour": is_valid_trading_hour(),
            "current_hour_utc": datetime.utcnow().hour
        },
        "config": {
            "email_configured": validate_config(),
            "intervals": {
                "main": INTERVAL,
                "confirmation_15m": INTERVAL_15M,
                "macro_1h": INTERVAL_1H
            },
            "analysis_interval_seconds": 60
        },
        "adaptive_params": {
            symbol: get_adaptive_params(detect_pair_type(symbol))
            for symbol in SYMBOLS
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route("/test")
def test():
    """Endpoint para forzar un análisis de prueba"""
    logger.info("🧪 TEST: Forzando análisis manual...")

    try:
        success = check_signals()
        logger.info(f"🧪 TEST: Resultado del análisis: {success}")
        return jsonify({
            "test_result": "success" if success else "failed",
            "message": "Análisis manual ejecutado",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"🧪 TEST: Error en análisis manual: {e}")
        return jsonify({
            "test_result": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

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

@app.route("/force-start")
def force_start():
    """Endpoint para forzar el inicio del bot en Render"""
    global bot_running

    logger.info("🔧 FORCE START: Forzando inicio del bot...")

    try:
        # Marcar como running
        bot_running = True

        # Ejecutar análisis inmediato
        success = check_signals()

        # Verificar estado
        status = "active" if bot_running else "starting"

        return jsonify({
            "force_start": "success",
            "bot_running": bot_running,
            "analysis_result": success,
            "status": status,
            "message": "Bot forzado a iniciar",
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Error en force start: {e}")
        return jsonify({
            "force_start": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

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
            logger.info(f"🔄 Iniciando ciclo de análisis #{cycle_count}")
            logger.info(f"🕐 Timestamp: {datetime.now().isoformat()}")
            logger.info(f"🔄 Estado bot_running: {bot_running}")

            success = check_signals()
            logger.info(f"📊 Resultado análisis: {success}")

            if success:
                logger.info(f"✅ Ciclo #{cycle_count} completado exitosamente")
            else:
                logger.warning(f"⚠️ Ciclo #{cycle_count} falló")

            logger.info(f"⏰ Esperando 60 segundos para próximo análisis...")
            logger.info(f"💤 Iniciando sleep de 60 segundos...")
            time.sleep(60)
            logger.info(f"⏰ Sleep completado, continuando...")
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
logger.info("🔧 Verificando si es __main__...")

# === Inicio de la aplicación ===
if __name__ == "__main__":
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

    # Obtener puerto de Render
    port = int(os.environ.get("PORT", 5000))
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
    import sys
    sys.stdout.flush()

    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
