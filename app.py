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

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN ===
VERSION = "v2.1-LOGS"
DEPLOY_TIME = datetime.now().strftime("%m/%d %H:%M")  # Se actualiza automáticamente en cada deploy

SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("INTERVAL", "1m")

# Configuración de email desde variables de entorno
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Variables globales
last_signal = None
signal_count = 0
last_analysis_time = None
current_price = 0
current_rsi = 0
using_simulation = False
bot_running = False

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

# === Bot principal ===
def check_signals():
    global last_signal, signal_count, last_analysis_time, current_price, current_rsi

    try:
        logger.info(f"🔍 Analizando {SYMBOL}...")

        # Obtener datos
        logger.info("📡 Obteniendo datos de mercado...")
        data = get_klines(SYMBOL, INTERVAL)
        if not data or len(data) == 0:
            logger.error("❌ No se pudieron obtener datos")
            return False

        logger.info(f"✅ Obtenidos {len(data)} candles de datos")

        if not all(isinstance(d, list) and len(d) > 5 for d in data):
            logger.error("❌ Formato de datos incorrecto")
            return False
            
        # Procesar datos
        logger.info("📊 Calculando indicadores técnicos...")
        closes = np.array([float(c[4]) for c in data])
        volumes = np.array([float(c[5]) for c in data])

        ema_fast = ema(closes, 10)
        ema_slow = ema(closes, 21)
        close_now = closes[-1]
        rsi_now = rsi(closes)
        vol_now = volumes[-1]
        vol_avg = np.mean(volumes[-20:])

        # Actualizar variables globales
        current_price = close_now
        current_rsi = rsi_now
        last_analysis_time = datetime.now()

        logger.info(f"💰 Precio actual: ${close_now:.2f}")
        logger.info(f"📈 RSI: {rsi_now:.2f}")
        logger.info(f"📊 EMA rápida: {ema_fast:.2f}, EMA lenta: {ema_slow:.2f}")
        logger.info(f"📦 Volumen: {vol_now:,.0f} (Promedio: {vol_avg:,.0f})")

        # Evaluar condiciones de señales
        logger.info("🔍 Evaluando condiciones de trading...")

        ema_condition_buy = ema_fast > ema_slow
        rsi_condition_buy = 50 < rsi_now < 65
        vol_condition_buy = vol_now > vol_avg

        ema_condition_sell = ema_fast < ema_slow
        rsi_condition_sell = 38 < rsi_now < 55
        vol_condition_sell = vol_now > vol_avg

        logger.info(f"🔍 Condiciones BUY: EMA({ema_condition_buy}) + RSI({rsi_condition_buy}) + VOL({vol_condition_buy})")
        logger.info(f"🔍 Condiciones SELL: EMA({ema_condition_sell}) + RSI({rsi_condition_sell}) + VOL({vol_condition_sell})")

        buy = ema_condition_buy and rsi_condition_buy and vol_condition_buy
        sell = ema_condition_sell and rsi_condition_sell and vol_condition_sell

        logger.info(f"🎯 Señal BUY: {buy}, Señal SELL: {sell}")
        logger.info(f"📝 Última señal enviada: {last_signal}")

        if buy and last_signal != "buy":
            logger.info("🟢 ¡SEÑAL DE COMPRA DETECTADA!")
            msg = f"🟢 BUY Signal\n{SYMBOL} a {close_now:.2f}\nRSI: {rsi_now:.2f}\nEMA Fast: {ema_fast:.2f}\nEMA Slow: {ema_slow:.2f}\nVolumen: {vol_now:,.0f}"

            if send_email("🟢 BUY SIGNAL - Scalping Bot", msg):
                signal_count += 1
                last_signal = "buy"
                logger.info(f"✅ Email BUY enviado exitosamente - Señal #{signal_count}")
            else:
                logger.error("❌ Error enviando email BUY")

        elif sell and last_signal != "sell":
            logger.info("🔴 ¡SEÑAL DE VENTA DETECTADA!")
            msg = f"🔴 SELL Signal\n{SYMBOL} a {close_now:.2f}\nRSI: {rsi_now:.2f}\nEMA Fast: {ema_fast:.2f}\nEMA Slow: {ema_slow:.2f}\nVolumen: {vol_now:,.0f}"

            if send_email("🔴 SELL SIGNAL - Scalping Bot", msg):
                signal_count += 1
                last_signal = "sell"
                logger.info(f"✅ Email SELL enviado exitosamente - Señal #{signal_count}")
            else:
                logger.error("❌ Error enviando email SELL")

        else:
            logger.info(f"⏸️ Sin señales nuevas - Esperando condiciones...")

        logger.info("✅ Análisis completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"Error en análisis: {e}")
        return False

# === Flask App ===
app = Flask(__name__)

@app.route("/")
def home():
    global last_analysis_time, current_price, current_rsi, signal_count, last_signal, using_simulation, bot_running
    
    status = "🟢 ACTIVO" if bot_running and last_analysis_time else "🟡 INICIANDO"
    last_time = last_analysis_time.strftime('%H:%M:%S') if last_analysis_time else "N/A"
    data_source = "📊 Datos simulados (demo)" if using_simulation else "📡 Datos reales de Binance"
    email_status = "✅ Configurado" if all([EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO]) else "⚠️ No configurado"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scalping Bot</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; color: #333; }}
            .status {{ text-align: center; font-size: 24px; margin: 20px 0; }}
            .active {{ color: #28a745; }}
            .waiting {{ color: #ffc107; }}
            .info {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
            .metric-value {{ font-size: 18px; font-weight: bold; color: #007bff; }}
            .metric-label {{ font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Scalping Alert Bot</h1>
                <p>Trading automático con EMA y RSI</p>
                <div style="font-size: 11px; color: #888; margin-top: 8px; border-top: 1px solid #333; padding-top: 8px;">
                    {VERSION} • Deploy: {DEPLOY_TIME}
                </div>
            </div>
            
            <div class="status {'active' if status == '🟢 ACTIVO' else 'waiting'}">
                {status}
            </div>
            
            <div class="info">
                <div class="metric">
                    <div class="metric-value">{SYMBOL}</div>
                    <div class="metric-label">Símbolo</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${current_price:.2f}</div>
                    <div class="metric-label">Precio Actual</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{current_rsi:.1f}</div>
                    <div class="metric-label">RSI</div>
                </div>
            </div>
            
            <div class="info">
                <div class="metric">
                    <div class="metric-value">{signal_count}</div>
                    <div class="metric-label">Señales Enviadas</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{last_signal or 'Ninguna'}</div>
                    <div class="metric-label">Última Señal</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{last_time}</div>
                    <div class="metric-label">Último Análisis</div>
                </div>
            </div>
            
            <div class="info">
                <p><strong>📧 Email:</strong> {email_status}</p>
                <p><strong>⏱️ Intervalo:</strong> Análisis cada 60 segundos</p>
                <p><strong>🔄 Auto-refresh:</strong> Página se actualiza cada 30 segundos</p>
                <p><strong>{data_source}</strong></p>
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
        "symbol": SYMBOL,
        "current_price": current_price,
        "current_rsi": current_rsi,
        "signal_count": signal_count,
        "last_signal": last_signal,
        "last_analysis": last_analysis_time.isoformat() if last_analysis_time else None,
        "using_simulation": using_simulation,
        "email_configured": all([EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO])
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/debug")
def debug():
    """Endpoint de debug para ver el estado interno del bot"""
    global last_analysis_time, current_price, current_rsi, signal_count, last_signal, using_simulation, bot_running

    return jsonify({
        "bot_status": {
            "running": bot_running,
            "last_analysis": last_analysis_time.isoformat() if last_analysis_time else None,
            "analysis_age_seconds": (datetime.now() - last_analysis_time).total_seconds() if last_analysis_time else None
        },
        "market_data": {
            "symbol": SYMBOL,
            "current_price": current_price,
            "current_rsi": current_rsi,
            "using_simulation": using_simulation
        },
        "signals": {
            "count": signal_count,
            "last_signal": last_signal
        },
        "config": {
            "email_configured": validate_config(),
            "interval": INTERVAL,
            "analysis_interval_seconds": 60
        },
        "timestamp": datetime.now().isoformat()
    })

# === Loop de monitoreo ===
def monitoring_loop():
    global bot_running
    logger.info("🚀 Iniciando bot de trading...")
    logger.info(f"📊 Monitoreando {SYMBOL} cada 60 segundos")

    email_configured = validate_config()
    if email_configured:
        logger.info("📧 Enviando alertas por email cuando detecte señales")
    else:
        logger.warning("📧 Email no configurado - solo monitoreo web")

    bot_running = True
    logger.info("✅ Bot marcado como running - iniciando loop de análisis")

    # Hacer primer análisis inmediatamente
    logger.info("🔄 Ejecutando primer análisis...")
    try:
        success = check_signals()
        if success:
            logger.info("✅ Primer análisis completado exitosamente")
        else:
            logger.warning("⚠️ Primer análisis falló, continuando...")
    except Exception as e:
        logger.error(f"❌ Error en primer análisis: {e}")

    cycle_count = 1
    while True:
        try:
            logger.info(f"🔄 Iniciando ciclo de análisis #{cycle_count}")
            success = check_signals()
            if success:
                logger.info(f"✅ Ciclo #{cycle_count} completado")
            else:
                logger.warning(f"⚠️ Ciclo #{cycle_count} falló")

            logger.info(f"⏰ Esperando 60 segundos para próximo análisis...")
            time.sleep(60)
            cycle_count += 1
        except Exception as e:
            logger.error(f"❌ Error en loop principal (ciclo #{cycle_count}): {e}")
            logger.info("⏰ Esperando 60 segundos antes de reintentar...")
            time.sleep(60)

# === Inicio de la aplicación ===
if __name__ == "__main__":
    logger.info("🚀 INICIANDO SCALPING BOT...")
    logger.info("=" * 50)

    # Mostrar configuración
    logger.info(f"📊 Símbolo: {SYMBOL}")
    logger.info(f"⏰ Intervalo: {INTERVAL}")
    logger.info(f"📧 Email configurado: {validate_config()}")

    # Iniciar loop de monitoreo en hilo separado
    logger.info("🔄 Iniciando hilo de monitoreo...")
    monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitoring_thread.start()
    logger.info("✅ Hilo de monitoreo iniciado")

    # Obtener puerto de Render
    port = int(os.environ.get("PORT", 5000))

    logger.info(f"🌐 Iniciando servidor web en puerto {port}...")
    logger.info("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=False)
