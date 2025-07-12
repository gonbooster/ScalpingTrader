# log_manager.py - Sistema de logs centralizado
import os
import logging
from datetime import datetime, date
from flask import jsonify

class LogManager:
    def __init__(self, log_file="bot_logs.txt"):
        self.log_file = log_file
        self.current_date = date.today()
        self.setup_logging()
    
    def check_and_clean_daily_logs(self):
        """Limpia logs si ha cambiado el día"""
        try:
            today = date.today()
            if today != self.current_date:
                # Ha cambiado el día, limpiar logs
                if os.path.exists(self.log_file):
                    # Hacer backup del día anterior
                    backup_file = f"bot_logs_{self.current_date.strftime('%Y%m%d')}.txt"
                    if os.path.exists(self.log_file):
                        os.rename(self.log_file, backup_file)
                        print(f"📁 Logs del día anterior guardados en: {backup_file}")

                # Actualizar fecha actual
                self.current_date = today
                print(f"🗓️ Nuevo día detectado: {today.strftime('%Y-%m-%d')} - Logs limpiados")

                # Crear nuevo archivo de logs
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Logs del día {today.strftime('%Y-%m-%d')}\n")

        except Exception as e:
            print(f"Error limpiando logs diarios: {e}")

    def rotate_logs(self):
        """Verifica cambio de día y limpia si es necesario"""
        self.check_and_clean_daily_logs()
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        # Verificar cambio de día al inicio
        self.rotate_logs()

        # Configurar handlers
        file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Configurar logger
        logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

        # Log inicial
        logger = logging.getLogger(__name__)
        logger.info("🚀 SISTEMA DE LOGS INICIADO")
        logger.info(f"📝 Archivo: {self.log_file} (Todos los logs del día {self.current_date.strftime('%Y-%m-%d')})")
        logger.info(f"🗓️ Limpieza automática: Al cambiar de día")
    
    def get_logs_html(self, limit=None):
        """Retorna logs en formato HTML - Muestra todos los logs del día actual"""
        try:
            self.rotate_logs()

            if not os.path.exists(self.log_file):
                return "<p>No hay logs disponibles</p>"

            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Mostrar todos los logs del día (sin límite) o aplicar límite si se especifica
            if limit and len(lines) > limit:
                recent_lines = lines[-limit:]
                showing_text = f"últimas {len(recent_lines)} líneas de {len(lines)} totales"
            else:
                recent_lines = lines
                showing_text = f"todas las {len(lines)} líneas del día {self.current_date.strftime('%Y-%m-%d')}"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Bot Logs</title>
                <style>
                    body {{ font-family: 'Courier New', monospace; background: #1a1a1a; color: #00ff00; margin: 20px; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: #333; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                    .logs {{ background: #000; padding: 20px; border-radius: 8px; white-space: pre-wrap; font-size: 12px; line-height: 1.4; max-height: 600px; overflow-y: auto; }}
                    .info {{ color: #00ff00; }}
                    .warning {{ color: #ffaa00; }}
                    .error {{ color: #ff0000; }}
                    .debug {{ color: #00aaff; }}
                    .refresh-btn {{ background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px 0; }}
                    .refresh-btn:hover {{ background: #218838; }}
                </style>
                <script>
                    function refreshLogs() {{
                        location.reload();
                    }}
                    // Auto-refresh cada 30 segundos
                    setInterval(refreshLogs, 30000);
                </script>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 Scalping Bot - Logs del Sistema</h1>
                        <p>📊 Mostrando {showing_text}</p>
                        <p>🗓️ Fecha actual: {self.current_date.strftime('%Y-%m-%d')} | 🔄 Auto-limpieza: Al cambiar de día</p>
                        <button class="refresh-btn" onclick="refreshLogs()">🔄 Actualizar Logs</button>
                    </div>
                    <div class="logs">{''.join(recent_lines)}</div>
                </div>
            </body>
            </html>
            """
            return html_content

        except Exception as e:
            return f"<p>Error cargando logs: {e}</p>"
    
    def get_logs_json(self, limit=None):
        """Retorna logs en formato JSON - Muestra todos los logs del día actual"""
        try:
            self.rotate_logs()

            if not os.path.exists(self.log_file):
                return {"logs": [], "total": 0, "date": self.current_date.strftime('%Y-%m-%d')}

            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Mostrar todos los logs del día o aplicar límite si se especifica
            if limit and len(lines) > limit:
                recent_lines = lines[-limit:]
            else:
                recent_lines = lines

            # Procesar líneas
            processed_logs = []
            for line in recent_lines:
                line = line.strip()
                if line and not line.startswith('#'):  # Ignorar comentarios
                    processed_logs.append({
                        "timestamp": line.split(" - ")[0] if " - " in line else "",
                        "level": line.split(" - ")[1] if " - " in line and len(line.split(" - ")) > 1 else "INFO",
                        "message": " - ".join(line.split(" - ")[2:]) if " - " in line and len(line.split(" - ")) > 2 else line
                    })

            return {
                "logs": processed_logs,
                "total": len(lines),
                "showing": len(recent_lines),
                "date": self.current_date.strftime('%Y-%m-%d'),
                "auto_cleanup": "Al cambiar de día"
            }

        except Exception as e:
            return {"error": f"Error cargando logs: {e}"}

# Instancia global
log_manager = LogManager()

def get_logger():
    """Retorna el logger configurado"""
    return logging.getLogger(__name__)

def rotate_logs():
    """Función helper para rotar logs"""
    log_manager.rotate_logs()

def get_logs_html_response(limit=None):
    """Función helper para Flask - Muestra todos los logs del día por defecto"""
    return log_manager.get_logs_html(limit)

def get_logs_json_response(limit=None):
    """Función helper para Flask - Muestra todos los logs del día por defecto"""
    return jsonify(log_manager.get_logs_json(limit))
