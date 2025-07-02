# email_service.py - Servicio de envío de emails
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, email_from: str, email_password: str, email_to: str):
        self.email_from = email_from
        self.email_password = email_password
        self.email_to = email_to
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_email(self, subject: str, plain_text: str, html_text: str = None) -> bool:
        """Envía un email con texto plano y HTML"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            
            # Agregar texto plano
            part1 = MIMEText(plain_text, 'plain', 'utf-8')
            msg.attach(part1)
            
            # Agregar HTML si está disponible
            if html_text:
                part2 = MIMEText(html_text, 'html', 'utf-8')
                msg.attach(part2)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email enviado: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Prueba la conexión SMTP"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
            return True
        except:
            return False

def create_professional_email(signal_type: str, symbol: str, price: float, 
                            rsi: float, rsi_15m: float, ema_fast: float, 
                            ema_slow: float, volume: float, vol_avg: float,
                            confidence_score: int, atr_val: float, 
                            candle_change_percent: float, conditions: Dict,
                            price_targets: Optional[Dict] = None) -> tuple:
    """Crea email HTML profesional con % de vela"""
    
    # Colores según el tipo de señal
    if signal_type == "buy":
        color = "#28a745"
        emoji = "🟢"
        action = "COMPRA"
    else:
        color = "#dc3545"
        emoji = "🔴"
        action = "VENTA"
    
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
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: {color}; color: white; padding: 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 20px; }}
            .alert {{ background: #e8f5e8; border: 2px solid {color}; padding: 15px; border-radius: 5px; margin: 15px 0; text-align: center; }}
            .metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
            .metric {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #dee2e6; }}
            .metric-value {{ font-size: 20px; font-weight: bold; color: {color}; }}
            .metric-label {{ font-size: 12px; color: #6c757d; margin-top: 5px; }}
            .conditions {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .condition {{ margin: 5px 0; }}
            .candle-change {{ font-weight: bold; color: {color}; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{emoji} SEÑAL DE {action}</h1>
                <h2>{symbol}</h2>
            </div>

            <div class="content">
                <div class="alert">
                    <strong>💰 Precio Actual: ${price:,.2f}</strong><br>
                    <span class="candle-change">📈 Cambio Vela: {candle_change_percent:+.2f}%</span>
                </div>

                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{rsi:.1f}</div>
                        <div class="metric-label">RSI 1m</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{rsi_15m:.1f}</div>
                        <div class="metric-label">RSI 15m</div>
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
                    <h3>📋 Condiciones:</h3>
                    {''.join([f'<div class="condition">{"✅" if v else "❌"} {k}: {v}</div>' for k, v in conditions.items()])}
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
        </div>
    </body>
    </html>
    """
    
    return plain_text, html_text

# Variables globales para el servicio de email
email_service = None

def initialize_email_service(email_from: str, email_password: str, email_to: str):
    """Inicializa el servicio de email"""
    global email_service
    email_service = EmailService(email_from, email_password, email_to)

def send_signal_email(signal_type: str, symbol: str, price: float, 
                     rsi: float, rsi_15m: float, ema_fast: float, 
                     ema_slow: float, volume: float, vol_avg: float,
                     confidence_score: int, atr_val: float, 
                     candle_change_percent: float, conditions: Dict,
                     price_targets: Optional[Dict] = None) -> bool:
    """Envía email de señal de trading"""
    if not email_service:
        logger.warning("📧 Servicio de email no inicializado")
        return False
    
    # Crear contenido del email
    plain_text, html_text = create_professional_email(
        signal_type, symbol, price, rsi, rsi_15m, ema_fast, ema_slow,
        volume, vol_avg, confidence_score, atr_val, candle_change_percent,
        conditions, price_targets
    )
    
    # Crear subject
    action = "COMPRA" if signal_type == "buy" else "VENTA"
    emoji = "🟢" if signal_type == "buy" else "🔴"
    subject = f"{emoji} {action} - {symbol} Scalping Bot"
    
    return email_service.send_email(subject, plain_text, html_text)

def test_email_connection() -> bool:
    """Prueba la conexión de email"""
    if not email_service:
        return False
    return email_service.test_connection()
