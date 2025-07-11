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
    """Crea email HTML profesional con los 8 criterios reales"""

    # Colores según el tipo de señal
    if signal_type == "buy":
        color = "#28a745"
        emoji = "🟢"
        action = "COMPRA"
    else:
        color = "#dc3545"
        emoji = "🔴"
        action = "VENTA"

    # Crear enlace directo al mercado de Binance
    # Convertir BTCUSDT -> BTC_USDT para la URL de Binance
    if symbol.endswith('USDT'):
        base_asset = symbol[:-4]  # Quitar 'USDT'
        binance_pair = f"{base_asset}_USDT"
    elif symbol.endswith('USDC'):
        base_asset = symbol[:-4]  # Quitar 'USDC'
        binance_pair = f"{base_asset}_USDC"
    else:
        binance_pair = symbol  # Fallback

    binance_url = f"https://www.binance.com/en/trade/{binance_pair}?_from=markets&type=spot"

    # Mapear condiciones REALES del backend con información educativa completa
    criteria_map = {
        "RSI_1m_favorable": f"🔴 RSI 1min: {rsi:.1f}/100 (Objetivo: 30-70 zona favorable)",
        "RSI_15m_bullish": f"📊 RSI 15min: {rsi_15m:.1f}/100 (Objetivo: >50 tendencia alcista)",
        "EMA_crossover": f"📈 EMA Cruce: Rápida {ema_fast:.2f} > Lenta {ema_slow:.2f} (Tendencia alcista confirmada)",
        "Volume_high": f"📦 Volumen: {volume:,.0f} vs {vol_avg:,.0f} promedio ({volume/vol_avg:.1f}x - Objetivo: >1.2x)",
        "Confidence_good": f"🎯 Score Algoritmo: {confidence_score}/100 (PROFESIONAL: ≥75 para validar, ≥80 para email)",
        "Price_above_EMA": f"💰 Posición: ${price:,.2f} vs EMA ${ema_fast:.2f} ({((price-ema_fast)/ema_fast*100):+.2f}% - Precio sobre media)",
        "Candle_positive": f"🕯️ Momentum: {candle_change_percent:+.2f}% vela actual (Objetivo: >0.1% positiva)",
        "Breakout_candle": f"⚡ Ruptura: Vela con volumen elevado y momentum fuerte",
        "Signal_distance": f"⏰ Timing: Distancia adecuada desde última señal (anti-spam)"
    }

    # Crear lista de criterios con estado
    criteria_status = []
    for key, value in conditions.items():
        if key in criteria_map:
            status = "✅" if value else "❌"
            criteria_status.append(f"{status} {criteria_map[key]}")
        else:
            # Fallback para condiciones no mapeadas
            status = "✅" if value else "❌"
            criteria_status.append(f"{status} {key}: {value}")

    # Contar criterios cumplidos
    fulfilled_count = sum(1 for v in conditions.values() if v)
    total_count = len(conditions)

    # Calcular contexto de mercado
    market_strength = "FUERTE" if fulfilled_count >= 7 else "BUENA" if fulfilled_count >= 5 else "DÉBIL"
    confidence_level = "ALTA" if confidence_score >= 85 else "MEDIA" if confidence_score >= 65 else "BAJA"

    # Generar recomendaciones específicas
    if signal_type == "buy":
        if fulfilled_count >= 7 and confidence_score >= 80:
            recommendation = "🟢 RECOMENDACIÓN: Señal de alta calidad. Considerar entrada con gestión de riesgo."
        elif fulfilled_count >= 5 and confidence_score >= 65:
            recommendation = "🟡 RECOMENDACIÓN: Señal moderada. Esperar confirmación adicional o usar posición reducida."
        else:
            recommendation = "🔴 RECOMENDACIÓN: Señal débil. Mejor esperar mejores condiciones."
    else:
        recommendation = "📊 INFORMACIÓN: Señal de venta detectada para análisis."
    
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

📊 ANÁLISIS DE MERCADO:
• Fuerza de señal: {market_strength} ({fulfilled_count}/{total_count} criterios)
• Confianza algoritmo: {confidence_level} ({confidence_score}/100)
• Ratio volumen: {volume/vol_avg:.1f}x promedio

📋 CRITERIOS TÉCNICOS DETALLADOS:
{chr(10).join(criteria_status)}

{recommendation}

🎯 OBJETIVOS DE PRECIO:
{f'''🟢 Take Profit: ${price_targets["take_profit"]:,.2f} (+{price_targets["expected_move_percent"]:.1f}%)
🔴 Stop Loss: ${price_targets["stop_loss"]:,.2f} (-{price_targets["risk_percent"]:.1f}%)
⚖️ Risk/Reward: 1:{price_targets["risk_reward_ratio"]:.1f}''' if price_targets else 'No calculado'}

📈 ACCESO DIRECTO AL MERCADO:
🔗 Binance: {binance_url}

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

                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: {color}; margin-top: 0;">📊 ANÁLISIS DE MERCADO</h3>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0;">
                        <div style="text-align: center; padding: 10px; background: white; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: bold; color: {color};">Fuerza</div>
                            <div style="font-size: 18px; margin: 5px 0;">{market_strength}</div>
                            <div style="font-size: 14px; color: #6c757d;">{fulfilled_count}/{total_count} criterios</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: white; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: bold; color: {color};">Confianza</div>
                            <div style="font-size: 18px; margin: 5px 0;">{confidence_level}</div>
                            <div style="font-size: 14px; color: #6c757d;">{confidence_score}/100</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: white; border-radius: 8px;">
                            <div style="font-size: 16px; font-weight: bold; color: {color};">Volumen</div>
                            <div style="font-size: 18px; margin: 5px 0;">{volume/vol_avg:.1f}x</div>
                            <div style="font-size: 14px; color: #6c757d;">vs promedio</div>
                        </div>
                    </div>
                </div>

                <div class="conditions">
                    <h3>📋 Criterios Técnicos Detallados:</h3>
                    {''.join([f'<div class="condition" style="margin: 8px 0; padding: 8px; background: #f8f9fa; border-radius: 5px;">{criterion}</div>' for criterion in criteria_status])}
                </div>

                <div style="background: {'#e8f5e8' if signal_type == 'buy' else '#fff3cd'}; border: 2px solid {color}; padding: 15px; border-radius: 10px; margin: 20px 0;">
                    <strong>{recommendation}</strong>
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

                <div style="background: #e3f2fd; border: 2px solid #2196f3; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
                    <h3 style="color: #1976d2; margin-top: 0;">📈 ACCESO DIRECTO AL MERCADO</h3>
                    <a href="{binance_url}" target="_blank" style="display: inline-block; background: #f0b90b; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; margin: 10px 0;">
                        🔗 Abrir {symbol} en Binance
                    </a>
                    <div style="font-size: 12px; color: #666; margin-top: 10px;">
                        Enlace directo al par {symbol} en Binance Spot Trading
                    </div>
                </div>

                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #856404;">⚠️ IMPORTANTE - GESTIÓN DE RIESGO</h4>
                    <ul style="margin: 10px 0; padding-left: 20px; color: #856404;">
                        <li><strong>Nunca inviertas más del 2-5%</strong> de tu capital en una sola operación</li>
                        <li><strong>Usa siempre Stop Loss</strong> según los niveles calculados</li>
                        <li><strong>Confirma la señal</strong> con tu propio análisis antes de operar</li>
                        <li><strong>Este sistema es educativo</strong> - No es consejo financiero</li>
                    </ul>
                    <div style="text-align: center; margin-top: 15px; font-size: 12px; color: #6c757d;">
                        📚 Aprende más en: <a href="http://127.0.0.1:8000/instructions" style="color: {color};">Guía de Trading</a>
                    </div>
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
    
    # Crear subject con prioridad basada en score
    action = "COMPRA" if signal_type == "buy" else "VENTA"
    emoji = "🟢" if signal_type == "buy" else "🔴"

    if confidence_score >= 95:
        priority = "🔥 PREMIUM"
    elif confidence_score >= 90:
        priority = "⭐ EXCELENTE"
    else:
        priority = ""

    subject = f"{emoji} {priority} {action} - {symbol} ({confidence_score}/100)"
    
    return email_service.send_email(subject, plain_text, html_text)

def test_email_connection() -> bool:
    """Prueba la conexión de email"""
    if not email_service:
        return False
    return email_service.test_connection()
