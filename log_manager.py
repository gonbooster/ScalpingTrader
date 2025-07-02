# log_manager.py - Sistema de logs centralizado
import os
import logging
from flask import jsonify

class LogManager:
    def __init__(self, log_file="bot_logs.txt", max_lines=500):
        self.log_file = log_file
        self.max_lines = max_lines
        self.setup_logging()
    
    def rotate_logs(self):
        """Mantiene solo las últimas max_lines líneas"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                if len(lines) > self.max_lines:
                    with open(self.log_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines[-self.max_lines:])
        except Exception as e:
            print(f"Error rotando logs: {e}")
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        # Rotar logs al inicio
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
        logger.info(f"📝 Archivo: {self.log_file} (Max: {self.max_lines} líneas)")
    
    def get_logs_html(self, limit=100):
        """Retorna logs en formato HTML"""
        try:
            self.rotate_logs()
            
            if not os.path.exists(self.log_file):
                return "<p>No hay logs disponibles</p>"
            
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Tomar las últimas 'limit' líneas
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
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
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 Scalping Bot - Logs del Sistema</h1>
                        <p>📊 Mostrando últimas {len(recent_lines)} líneas de {len(lines)} totales</p>
                        <p>🔄 Auto-rotación: {self.max_lines} líneas máximo</p>
                    </div>
                    <div class="logs">{''.join(recent_lines)}</div>
                </div>
            </body>
            </html>
            """
            return html_content
            
        except Exception as e:
            return f"<p>Error cargando logs: {e}</p>"
    
    def get_logs_json(self, limit=50):
        """Retorna logs en formato JSON"""
        try:
            self.rotate_logs()
            
            if not os.path.exists(self.log_file):
                return {"logs": [], "total": 0}
            
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Tomar las últimas 'limit' líneas
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            # Procesar líneas
            processed_logs = []
            for line in recent_lines:
                line = line.strip()
                if line:
                    processed_logs.append({
                        "timestamp": line.split(" - ")[0] if " - " in line else "",
                        "level": line.split(" - ")[1] if " - " in line and len(line.split(" - ")) > 1 else "INFO",
                        "message": " - ".join(line.split(" - ")[2:]) if " - " in line and len(line.split(" - ")) > 2 else line
                    })
            
            return {
                "logs": processed_logs,
                "total": len(lines),
                "showing": len(recent_lines),
                "max_lines": self.max_lines
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

def get_logs_html_response(limit=100):
    """Función helper para Flask"""
    return log_manager.get_logs_html(limit)

def get_logs_json_response(limit=50):
    """Función helper para Flask"""
    return jsonify(log_manager.get_logs_json(limit))
