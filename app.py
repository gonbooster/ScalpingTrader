# app.py - Scalping Trading Bot - Refactorizado y Modular (< 200 líneas)
import os
import time
import threading
from datetime import datetime
from flask import Flask, jsonify

# Importar módulos propios
from log_manager import get_logger, get_logs_html_response, get_logs_json_response, rotate_logs
from market_analyzer import analyze_market, get_market_data
from trading_logic import analyze_trading_signals, get_trading_stats
from dashboard import generate_dashboard_html
from email_service import initialize_email_service, test_email_connection
from config import validate_config, SYMBOLS, PORT

# Configurar logger
logger = get_logger()

# === CONFIGURACIÓN ===
VERSION = "v5.0-MODULAR"
DEPLOY_TIME = datetime.now().strftime("%m/%d %H:%M")

# Configuración de email desde variables de entorno
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Inicializar servicio de email
if EMAIL_FROM and EMAIL_PASSWORD and EMAIL_TO:
    initialize_email_service(EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO)
    logger.info("✅ Servicio de email inicializado")
else:
    logger.warning("⚠️ Servicio de email no inicializado - faltan variables de entorno")

# Variables globales del bot
last_signals = {}
signal_count = 0
bot_running = False
bot_thread = None
last_analysis_time = None
using_simulation = False

logger.info(f"🚀 Scalping Bot {VERSION} iniciado")
logger.info(f"📊 Símbolos: {SYMBOLS}")
logger.info(f"📧 Email: {'✅' if validate_config() else '❌'}")

# === FUNCIONES PRINCIPALES DEL BOT ===

def trading_loop():
    """Loop principal de trading"""
    global bot_running, last_analysis_time, signal_count, using_simulation
    
    bot_running = True
    cycle_count = 0
    
    logger.info("🚀 INICIANDO LOOP DE TRADING")

    # Primer análisis inmediato
    logger.info("⚡ Ejecutando primer análisis...")
    try:
        if analyze_market():
            last_analysis_time = datetime.now()
            market_data = get_market_data()
            analyze_trading_signals(market_data, last_signals)
            logger.info("✅ Primer análisis completado")
    except Exception as e:
        logger.error(f"❌ Error en primer análisis: {e}")

    while bot_running:
        try:
            cycle_count += 1
            logger.info(f"🔄 Ciclo {cycle_count} - Analizando mercado...")
            
            # Analizar mercado usando el módulo
            if analyze_market():
                last_analysis_time = datetime.now()
                
                # Obtener datos del mercado
                market_data = get_market_data()
                
                # Analizar señales de trading
                signals_sent = analyze_trading_signals(market_data)
                signal_count += signals_sent
                
                logger.info(f"✅ Ciclo {cycle_count} completado - {signals_sent} señales enviadas")
            else:
                logger.error(f"❌ Error en ciclo {cycle_count}")
                using_simulation = True
            
            # Rotar logs cada 5 ciclos
            if cycle_count % 5 == 0:
                rotate_logs()
                logger.info(f"🔄 Logs rotados - ciclo {cycle_count}")
            
            # Esperar 60 segundos
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot detenido por usuario")
            break
        except Exception as e:
            logger.error(f"❌ Error crítico en trading loop: {e}")
            using_simulation = True
            time.sleep(60)
    
    bot_running = False
    logger.info("🛑 Trading loop finalizado")

# === FLASK APP ===
app = Flask(__name__)

@app.route("/")
def dashboard():
    """Dashboard principal"""
    try:
        market_data = get_market_data()
        email_status = "✅ OK" if validate_config() else "⚠️ Error"
        
        html = generate_dashboard_html(
            market_data, last_signals, signal_count, bot_running,
            last_analysis_time, using_simulation, email_status
        )
        
        return html
    except Exception as e:
        logger.error(f"❌ Error generando dashboard: {e}")
        return f"<h1>Error: {e}</h1>"

@app.route("/api/data")
def api_data():
    """API endpoint para datos en tiempo real"""
    try:
        market_data = get_market_data()
        trading_stats = get_trading_stats()
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "market_data": market_data,
            "trading_stats": trading_stats,
            "bot_status": {
                "running": bot_running,
                "last_analysis": last_analysis_time.isoformat() if last_analysis_time else None,
                "signal_count": signal_count,
                "using_simulation": using_simulation
            }
        })
    except Exception as e:
        logger.error(f"❌ Error en API: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/logs")
def view_logs():
    """Endpoint para ver logs del bot"""
    return get_logs_html_response(100)

@app.route("/logs-json")
def view_logs_json():
    """Endpoint para logs en JSON"""
    return get_logs_json_response(50)

@app.route("/test-email")
def test_email():
    """Endpoint para probar email"""
    logger.info("📧 TEST: Probando conexión de email...")
    
    try:
        if test_email_connection():
            logger.info("✅ Conexión de email verificada exitosamente")
            return jsonify({
                "test_result": "success",
                "message": "Conexión de email verificada correctamente",
                "email_to": EMAIL_TO,
                "timestamp": datetime.now().isoformat()
            })
        else:
            logger.error("❌ Error en conexión de email")
            return jsonify({
                "test_result": "failed",
                "message": "Error en conexión de email",
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"❌ Error probando email: {e}")
        return jsonify({
            "test_result": "error",
            "message": f"Error: {e}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/start")
def start_bot():
    """Endpoint para iniciar el bot"""
    global bot_running
    
    if not bot_running:
        # Iniciar bot en hilo separado
        bot_thread = threading.Thread(target=trading_loop, daemon=True)
        bot_thread.start()
        
        logger.info("🚀 Bot iniciado desde endpoint")
        return jsonify({
            "status": "success",
            "message": "Bot iniciado correctamente",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "status": "info",
            "message": "Bot ya está ejecutándose",
            "timestamp": datetime.now().isoformat()
        })

@app.route("/stop")
def stop_bot():
    """Endpoint para detener el bot"""
    global bot_running
    
    if bot_running:
        bot_running = False
        logger.info("🛑 Bot detenido desde endpoint")
        return jsonify({
            "status": "success",
            "message": "Bot detenido correctamente",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "status": "info",
            "message": "Bot no está ejecutándose",
            "timestamp": datetime.now().isoformat()
        })

@app.route("/status")
def bot_status():
    """Endpoint para estado del bot"""
    return jsonify({
        "version": VERSION,
        "deploy_time": DEPLOY_TIME,
        "bot_running": bot_running,
        "last_analysis": last_analysis_time.isoformat() if last_analysis_time else None,
        "signal_count": signal_count,
        "using_simulation": using_simulation,
        "symbols": SYMBOLS,
        "email_configured": validate_config(),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/analytics')
def analytics():
    """Dashboard de análisis de rendimiento (PRIVADO)"""
    try:
        from analytics_dashboard import get_analytics_data, generate_analytics_dashboard

        performance_stats, recent_signals, market_trends = get_analytics_data()
        return generate_analytics_dashboard(performance_stats, recent_signals, market_trends)

    except ImportError as e:
        logger.error(f"ImportError en analytics: {e}")
        return f"""
        <html>
        <head><title>Analytics - Error</title></head>
        <body style="font-family: Arial; background: #1e293b; color: white; padding: 20px;">
            <h1>❌ Error: Analytics module not available</h1>
            <p>Error: {str(e)}</p>
            <a href="/" style="color: #60a5fa;">← Volver al Dashboard</a>
        </body>
        </html>
        """, 500
    except Exception as e:
        logger.error(f"Error en analytics: {e}")
        return f"""
        <html>
        <head><title>Analytics - Error</title></head>
        <body style="font-family: Arial; background: #1e293b; color: white; padding: 20px;">
            <h1>❌ Error en Analytics</h1>
            <p>Error: {str(e)}</p>
            <a href="/" style="color: #60a5fa;">← Volver al Dashboard</a>
        </body>
        </html>
        """, 500

@app.route('/analytics/api')
def analytics_api():
    """API de datos de analytics"""
    try:
        from analytics_dashboard import get_analytics_data

        performance_stats, recent_signals, market_trends = get_analytics_data()
        return jsonify({
            "performance": performance_stats,
            "recent_signals": recent_signals[:10],  # Solo últimas 10
            "market_trends": market_trends,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error en analytics API: {e}")
        return jsonify({"error": str(e)}), 500

# === MAIN ===
# Inicializar bot automáticamente cuando se importa el módulo (para Gunicorn)
def init_trading_bot():
    """Inicializa el bot de trading una sola vez"""
    global bot_running, bot_thread

    if not bot_running:
        logger.info("🔄 Preparando thread de trading...")
        logger.info("🚀 Iniciando thread de trading...")
        bot_thread = threading.Thread(target=trading_loop, daemon=True)
        bot_thread.start()
        logger.info("✅ Thread de trading iniciado")

        # Dar tiempo al thread para inicializar
        import time
        time.sleep(2)
        logger.info("⏰ Thread de trading inicializado")

# Inicializar bot automáticamente
init_trading_bot()

if __name__ == "__main__":
    logger.info(f"🌐 Iniciando servidor Flask en puerto {PORT}")
    logger.info("🌐 Iniciando servidor Flask...")
    app.run(host="0.0.0.0", port=PORT, debug=False)
