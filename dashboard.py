# dashboard.py - Frontend y dashboard web
from datetime import datetime

def get_24h_price_change(symbol, current_price):
    """Obtiene el cambio de precio en 24h desde Binance"""
    try:
        import requests
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            price_change_percent = float(data.get('priceChangePercent', 0))
            price_24h_ago = current_price / (1 + price_change_percent / 100)
            return price_24h_ago, price_change_percent
    except Exception as e:
        print(f"Error obteniendo datos 24h para {symbol}: {e}")
    return None, 0

def generate_criteria_indicators(criteria_data, signal_type):
    """Genera los indicadores visuales de criterios"""
    if not criteria_data or 'criteria' not in criteria_data:
        return "".join(['<span class="criteria-dot inactive">⚪</span>' for _ in range(8)])

    criteria = criteria_data['criteria']
    indicators = ""

    # Nombres amigables para los criterios
    criteria_names = {
        'buy': {
            "RSI_1m_favorable": "RSI 1m OK",
            "RSI_15m_bullish": "RSI 15m ↗",
            "EMA_crossover": "EMA Cross",
            "Volume_high": "Vol Alto",
            "Confidence_excellent": "Score 90+",
            "Price_above_EMA": "Precio > EMA",
            "Candle_positive": "Vela +",
            "Signal_distance": "Distancia"
        },
        'sell': {
            "RSI_1m_overbought": "RSI 1m 70+",
            "RSI_15m_bearish": "RSI 15m ↘",
            "EMA_crossunder": "EMA Cross",
            "Volume_high": "Vol Alto",
            "Confidence_excellent": "Score 90+",
            "Price_below_EMA": "Precio < EMA",
            "Candle_negative": "Vela -",
            "Signal_distance": "Distancia"
        }
    }

    names = criteria_names.get(signal_type, {})

    for key, value in criteria.items():
        name = names.get(key, key)
        if value:
            indicators += f'<span class="criteria-dot active" title="{name}">✅</span>'
        else:
            indicators += f'<span class="criteria-dot inactive" title="{name}">⚪</span>'

    return indicators

def generate_status_cards(symbol, bot_running, email_status, signal_count, last_time):
    """Genera las cards de status para cada crypto"""
    status = "🟢 ACTIVO" if bot_running else "🟡 INICIANDO"

    return f"""
    <div class="status-cards">
        <div class="status-card">
            <div class="status-label">Estado</div>
            <div class="status-value">{status}</div>
        </div>
        <div class="status-card">
            <div class="status-label">Email</div>
            <div class="status-value">{email_status}</div>
        </div>
        <div class="status-card">
            <div class="status-label">Horario</div>
            <div class="status-value">✅ Óptimo</div>
        </div>
        <div class="status-card">
            <div class="status-label">Señales</div>
            <div class="status-value">{signal_count}</div>
        </div>
        <div class="status-card">
            <div class="status-label">Último</div>
            <div class="status-value">{last_time}</div>
        </div>
    </div>
    """

def generate_dashboard_html(market_data, last_signals, signal_count, bot_running,
                          last_analysis_time, using_simulation, email_status):
    """Genera el HTML completo del dashboard"""
    
    # Estado del sistema
    if using_simulation:
        status = "🔴 ERROR"
        data_source = "Binance bloqueado"
    elif bot_running and last_analysis_time:
        status = "🟢 ACTIVO"
        data_source = "Datos reales"
    else:
        status = "🟡 INICIANDO"
        data_source = "Conectando..."
    
    # Formato de tiempo más claro
    if last_analysis_time:
        now = datetime.now()
        time_diff = (now - last_analysis_time).total_seconds()

        # Manejar tiempo negativo (diferencias de zona horaria)
        if time_diff < 0:
            last_time = f"{last_analysis_time.strftime('%H:%M:%S')} (ahora)"
        elif time_diff < 60:
            last_time = f"{last_analysis_time.strftime('%H:%M:%S')} (hace {int(time_diff)}s)"
        elif time_diff < 3600:  # Menos de 1 hora
            last_time = f"{last_analysis_time.strftime('%H:%M:%S')} (hace {int(time_diff/60)}m)"
        else:  # Más de 1 hora
            last_time = f"{last_analysis_time.strftime('%H:%M:%S')} (hace {int(time_diff/3600)}h)"
    else:
        last_time = "N/A"
    
    # Generar cards de criptomonedas
    crypto_cards = generate_crypto_cards(market_data, last_signals, signal_count, bot_running, last_analysis_time, using_simulation, email_status)
    
    # HTML completo
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scalping Dashboard</title>
        {get_dashboard_css()}
        {get_dashboard_js()}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 Scalping Dashboard</h1>
                <p>BTC • ETH • SOL • Análisis en tiempo real</p>
                <div class="header-buttons">
                    <a href="/analytics" class="analytics-btn-compact" target="_blank">📊 Analytics</a>
                    <a href="/logs" class="logs-btn-compact" target="_blank">📋 Logs</a>
                </div>
            </div>



            <div class="crypto-grid">
                {crypto_cards}
            </div>

            <!-- Status Cards en Footer -->
            <div class="status-bar">
                <div class="status-item status-active">
                    <strong>Estado:</strong> {status}
                </div>
                <div class="status-item">
                    <strong>Email:</strong> {email_status}
                </div>
                <div class="status-item">
                    <strong>Horario:</strong> ✅ Óptimo
                </div>
                <div class="status-item">
                    <strong>Señales:</strong> {signal_count}
                </div>
                <div class="status-item">
                    <strong>Último:</strong> {last_time}
                </div>
            </div>

            <div class="footer">
                <p>🤖 Scalping Bot PRO • ⚠️ Solo para fines educativos</p>
            </div>
        </div>

        <div class="update-indicator" id="updateIndicator">
            ✅ Datos actualizados
        </div>
    </body>
    </html>
    """
    
    return html

def generate_crypto_cards(market_data, last_signals, signal_count, bot_running, last_analysis_time, using_simulation, email_status):
    """Genera las cards de criptomonedas"""
    crypto_cards = ""

    # Estado del sistema
    if using_simulation:
        status = "🔴 ERROR"
    elif bot_running and last_analysis_time:
        status = "🟢 ACTIVO"
    else:
        status = "🟡 INICIANDO"

    # Formato de tiempo más claro
    if last_analysis_time:
        from datetime import datetime
        now = datetime.now()
        diff = now - last_analysis_time
        seconds = int(diff.total_seconds())

        if seconds < 60:
            last_time = f"{last_analysis_time.strftime('%H:%M:%S')} (hace {seconds}s)"
        else:
            minutes = seconds // 60
            last_time = f"{last_analysis_time.strftime('%H:%M:%S')} (hace {minutes}m)"
    else:
        last_time = "Nunca"

    for symbol, data in market_data.items():
        # Datos básicos
        name = symbol.replace('USDT', '')
        price_raw = data.get('price', 0)  # Precio sin formatear
        rsi_1m = data.get('rsi_1m', 0)
        rsi_5m = data.get('rsi_5m', 0)
        rsi_15m = data.get('rsi_15m', 0)
        score = data.get('score', 0)
        
        # Nuevos datos del email
        candle_change = data.get('candle_change_percent', 0)
        vol_now = data.get('volume', 0)
        vol_avg = data.get('vol_avg', 1)

        # Cambio de precio actual (momentum de la vela actual)
        change_emoji = "📈" if candle_change > 0 else "📉" if candle_change < 0 else "➡️"
        change_color = "#22c55e" if candle_change > 0 else "#ef4444" if candle_change < 0 else "#94a3b8"

        # Interpretación del momentum
        if abs(candle_change) >= 0.5:
            momentum_strength = "🔥 FUERTE"
        elif abs(candle_change) >= 0.2:
            momentum_strength = "⚡ MEDIO"
        else:
            momentum_strength = "📊 DÉBIL"

        # Calcular ratio de volumen de forma segura
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 0
        
        # Targets para BUY y SELL
        tp_buy = data.get('take_profit_buy', 0)
        sl_buy = data.get('stop_loss_buy', 0)
        move_buy = data.get('expected_move_buy', 0)
        rr_buy = data.get('risk_reward_buy', 0)

        tp_sell = data.get('take_profit_sell', 0)
        sl_sell = data.get('stop_loss_sell', 0)
        move_sell = data.get('expected_move_sell', 0)
        rr_sell = data.get('risk_reward_sell', 0)

        # Criterios de trading
        buy_criteria = data.get('buy_criteria', {})
        sell_criteria = data.get('sell_criteria', {})
        
        # Señal actual (eliminada - redundante con sistema de confianza)
        
        # Sistema de niveles de confianza profesional
        if score >= 90:
            confidence_class = "confidence-excellent"
            confidence_label = "EXCELENTE"
            confidence_emoji = "🔥"
        elif score >= 75:
            confidence_class = "confidence-strong"
            confidence_label = "FUERTE"
            confidence_emoji = "🎯"
        elif score >= 60:
            confidence_class = "confidence-good"
            confidence_label = "BUENA"
            confidence_emoji = "✅"
        elif score >= 40:
            confidence_class = "confidence-weak"
            confidence_label = "DÉBIL"
            confidence_emoji = "⚠️"
        else:
            confidence_class = "confidence-poor"
            confidence_label = "POBRE"
            confidence_emoji = "❌"

        # Clases adicionales
        candle_class = "positive" if candle_change > 0 else "negative" if candle_change < 0 else "neutral"
        volume_class = "high-volume" if vol_ratio > 1.5 else "normal-volume"
        
        # Color del símbolo según el tipo
        symbol_color = "#f7931a" if name == "BTC" else "#627eea" if name == "ETH" else "#9945ff"
        symbol_icon = "₿" if name == "BTC" else "Ξ" if name == "ETH" else "◎"

        # Convertir precio a float si es string
        try:
            price_float = float(price_raw) if isinstance(price_raw, str) else price_raw
        except (ValueError, TypeError):
            price_float = 0.0

        # Obtener datos de precio 24h anterior
        price_24h_ago, price_change_24h = get_24h_price_change(symbol, price_float)

        # Formatear precio actual
        price_display = f"${price_float:,.2f}"

        # Formatear precio 24h anterior y cambio
        if price_24h_ago and price_24h_ago > 0:
            price_24h_display = f"${price_24h_ago:,.2f}"
            change_color = "#22c55e" if price_change_24h > 0 else "#ef4444" if price_change_24h < 0 else "#94a3b8"
            change_emoji = "📈" if price_change_24h > 0 else "📉" if price_change_24h < 0 else "➡️"
            price_24h_info = f'<div class="price-24h" style="font-size: 0.75rem; color: {change_color}; margin-top: 2px;">{change_emoji} 24h: {price_24h_display} ({price_change_24h:+.2f}%)</div>'
        else:
            price_24h_info = ""

        crypto_cards += f"""
        <div class="crypto-card {name.lower()}" data-symbol="{symbol}" style="border-left: 4px solid {symbol_color};">
            <div class="crypto-header">
                <div class="crypto-name" style="color: {symbol_color};">
                    <span class="crypto-icon">{symbol_icon}</span> {name}
                </div>
                <div class="crypto-price-container">
                    <div class="crypto-price" data-price="{symbol}">{price_display}</div>
                    {price_24h_info}
                </div>
            </div>
            
            <div class="candle-change {candle_class}" data-candle="{symbol}" title="MOMENTUM 1MIN - Cómo interpretar: 📈 VERDE (+%) = Precio subiendo → Bueno para COMPRAR | 📉 ROJO (-%) = Precio bajando → Bueno para VENDER | 🔥 FUERTE >0.5% = Movimiento potente | ⚡ MEDIO 0.2-0.5% = Movimiento normal | 📊 DÉBIL <0.2% = Movimiento lento">
                {change_emoji} Momentum 1min: {candle_change:+.2f}% {momentum_strength}
            </div>
            
            <div class="metrics-grid">
                <div class="metric rsi-metric" title="RSI 1min: Indicador de momentum inmediato. 0-30=Sobreventa (posible rebote), 30-70=Neutral, 70-100=Sobrecompra (posible caída). Ideal para timing exacto de entrada.">
                    <div class="metric-value" data-rsi="{symbol}">{rsi_1m:.1f}</div>
                    <div class="metric-label">📊 RSI 1min</div>
                    <div class="metric-status">{'🔴 Sobrecompra' if rsi_1m >= 70 else '🟢 Sobreventa' if rsi_1m <= 30 else '🟡 Neutral'}</div>
                </div>
                <div class="metric rsi-metric" title="RSI 5min: Confirmación rápida del momentum. Más confiable que 1min, menos ruido. Perfecto para scalping - filtra señales falsas del 1min.">
                    <div class="metric-value">{rsi_5m:.1f}</div>
                    <div class="metric-label">⚡ RSI 5min</div>
                    <div class="metric-status">{'🔴 Sobrecompra' if rsi_5m >= 70 else '🟢 Sobreventa' if rsi_5m <= 30 else '🟡 Neutral'}</div>
                </div>
                <div class="metric rsi-metric" title="RSI 15min: Tendencia general del mercado. Indica la dirección principal. Si coincide con 1m y 5m = señal muy fuerte. Evita operar contra esta tendencia.">
                    <div class="metric-value" data-rsi15="{symbol}">{rsi_15m:.1f}</div>
                    <div class="metric-label">🎯 RSI 15min</div>
                    <div class="metric-status">{'🔴 Sobrecompra' if rsi_15m >= 70 else '🟢 Sobreventa' if rsi_15m <= 30 else '🟡 Neutral'}</div>
                </div>
                <div class="metric volume-metric {volume_class}" title="Volumen: Cantidad de operaciones. Ratio >1.5x = alta actividad (más confiable). Volumen alto confirma la fuerza del movimiento.">
                    <div class="metric-value" data-volume="{symbol}">{vol_now:,.0f}</div>
                    <div class="metric-label">📊 Volumen</div>
                    <div class="metric-status">Ratio: {vol_ratio:.1f}x</div>
                </div>
            </div>

            <!-- Criterios de Trading ANTES del Score -->
            <div class="criteria-section">
                <div class="criteria-header">📋 Criterios de Trading</div>
                <div class="criteria-grid">
                    <div class="criteria-column">
                        <div class="criteria-title">🟢 COMPRA</div>
                        <div class="criteria-indicators">
                            {generate_criteria_indicators(buy_criteria, 'buy')}
                        </div>
                        <div class="criteria-count">{buy_criteria.get('fulfilled', 0)}/{buy_criteria.get('total', 8)} criterios</div>
                    </div>
                    <div class="criteria-column">
                        <div class="criteria-title">🔴 VENTA</div>
                        <div class="criteria-indicators">
                            {generate_criteria_indicators(sell_criteria, 'sell')}
                        </div>
                        <div class="criteria-count">{sell_criteria.get('fulfilled', 0)}/{sell_criteria.get('total', 8)} criterios</div>
                    </div>
                </div>
            </div>

            <div class="metrics-grid" style="margin-top: 7px;">
                <div class="metric score-metric {confidence_class}" title="Score de Confianza: Algoritmo que evalúa 8 condiciones técnicas. 90-100=Excelente (alta probabilidad), 75-89=Fuerte, 60-74=Buena, <60=Débil. Solo se envían emails con 90+ y 7/8 condiciones.">
                    <div class="metric-value" data-score="{symbol}">{confidence_emoji} {score}/100</div>
                    <div class="metric-label">{confidence_label}</div>
                </div>
            </div>
            
            <div class="trading-scenarios">
                <div class="scenario-title">📊 Escenarios de Trading:</div>
                
                <div class="scenario buy-scenario">
                    <div class="scenario-header">🟢 Si COMPRAS ahora:</div>
                    <div class="scenario-targets">
                        <div class="target profit">
                            <span class="target-label">🎯 Objetivo:</span>
                            <span class="target-value">${tp_buy:,.2f}</span>
                            <span class="target-percent">+{move_buy:.1f}%</span>
                        </div>
                        <div class="target loss">
                            <span class="target-label">🛡️ Stop Loss:</span>
                            <span class="target-value">${sl_buy:,.2f}</span>
                            <span class="target-percent">R/R: 1:{rr_buy:.1f}</span>
                        </div>
                    </div>
                </div>
                
                <div class="scenario sell-scenario">
                    <div class="scenario-header">🔴 Si VENDES ahora:</div>
                    <div class="scenario-targets">
                        <div class="target profit">
                            <span class="target-label">🎯 Objetivo:</span>
                            <span class="target-value">${tp_sell:,.2f}</span>
                            <span class="target-percent">-{move_sell:.1f}%</span>
                        </div>
                        <div class="target loss">
                            <span class="target-label">🛡️ Stop Loss:</span>
                            <span class="target-value">${sl_sell:,.2f}</span>
                            <span class="target-percent">R/R: 1:{rr_sell:.1f}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    return crypto_cards

# Función generate_stats_section eliminada - sección de estadísticas removida

def get_dashboard_css():
    """Retorna el CSS del dashboard"""
    return """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #e0e6ed; line-height: 1.6; min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 25px; margin-bottom: 25px; border-radius: 12px;
            border: 1px solid #475569; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .header h1 { 
            font-size: 2rem; color: #f1f5f9; margin-bottom: 8px;
            background: linear-gradient(135deg, #60a5fa, #34d399);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .header p { color: #94a3b8; font-size: 1rem; margin-bottom: 15px; }
        .header-buttons {
            display: flex; justify-content: center; gap: 10px; margin-top: 10px;
        }
        .analytics-btn-compact {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white; text-decoration: none;
            padding: 6px 12px; border-radius: 6px;
            font-weight: 600; font-size: 0.8rem; transition: all 0.3s ease;
            border: 1px solid rgba(139, 92, 246, 0.3);
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2);
            display: inline-block; opacity: 0.8;
        }
        .analytics-btn-compact:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
            text-decoration: none; color: white;
            opacity: 1;
        }
        .logs-btn-compact {
            background: linear-gradient(135deg, #64748b, #475569);
            color: white; text-decoration: none;
            padding: 6px 12px; border-radius: 6px;
            font-weight: 600; font-size: 0.8rem; transition: all 0.3s ease;
            border: 1px solid rgba(100, 116, 139, 0.3);
            box-shadow: 0 2px 8px rgba(100, 116, 139, 0.2);
            display: inline-block; opacity: 0.8;
        }
        .logs-btn-compact:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(100, 116, 139, 0.4);
            text-decoration: none; color: white;
            opacity: 1;
        }
        .status-bar {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 15px; margin-bottom: 25px;
        }
        .status-item {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 15px; border-radius: 10px; border: 1px solid #475569;
            font-size: 0.9rem; box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        }
        .status-active { border-left: 4px solid #22c55e; }
        .crypto-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 25px; margin-bottom: 25px;
        }
        .crypto-card {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 25px; border-radius: 16px; border: 1px solid #475569;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3); transition: all 0.3s ease;
        }
        .crypto-card:hover { transform: translateY(-5px); }
        .crypto-header { 
            display: flex; justify-content: space-between; align-items: center; 
            margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #475569;
        }
        .crypto-name { font-size: 1.4rem; font-weight: 700; display: flex; align-items: center; gap: 8px; }
        .crypto-price-container { text-align: right; }
        .crypto-price { font-size: 1.3rem; color: #34d399; font-weight: 700; }
        .price-24h { font-size: 0.75rem; margin-top: 2px; opacity: 0.8; }

        .criteria-section {
            background: rgba(15, 23, 42, 0.6); padding: 15px; border-radius: 10px;
            margin-top: 20px; border: 1px solid #334155;
        }
        .criteria-header {
            font-size: 0.9rem; font-weight: 600; color: #94a3b8;
            text-align: center; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;
        }
        .criteria-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .criteria-column { text-align: center; }
        .criteria-title {
            font-size: 0.8rem; font-weight: 600; margin-bottom: 8px;
            color: #f1f5f9; text-transform: uppercase; letter-spacing: 1px;
        }
        .criteria-indicators {
            display: flex; justify-content: center; gap: 3px; margin-bottom: 8px;
            flex-wrap: wrap;
        }
        .criteria-dot {
            font-size: 0.7rem; cursor: help; transition: transform 0.2s ease;
        }
        .criteria-dot:hover { transform: scale(1.2); }
        .criteria-count {
            font-size: 0.75rem; color: #94a3b8; font-weight: 600;
        }

        .status-cards {
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;
            margin-top: 15px; padding: 12px;
            background: rgba(15, 23, 42, 0.4); border-radius: 8px;
            border: 1px solid #334155;
        }
        .status-card {
            text-align: center; padding: 6px 4px;
            background: rgba(30, 41, 59, 0.6); border-radius: 6px;
            border: 1px solid #475569;
        }
        .status-label {
            font-size: 0.65rem; color: #94a3b8;
            text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px;
        }
        .status-value {
            font-size: 0.7rem; color: #f1f5f9; font-weight: 600;
        }
        .candle-change { text-align: center; padding: 8px 12px; border-radius: 8px; font-weight: 600; margin-bottom: 15px; }
        .candle-change.positive { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .candle-change.negative { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px; }
        .score-metric { grid-column: span 2; }
        .metric { background: rgba(30, 41, 59, 0.6); padding: 12px; border-radius: 10px; text-align: center; border: 1px solid #475569; }
        .metric-value { font-size: 1.2rem; font-weight: 700; color: #f1f5f9; }
        .metric-label { font-size: 0.8rem; color: #f1f5f9 !important; margin-top: 4px; font-weight: 500; }
        .metric-status { font-size: 0.6rem; color: #f1f5f9 !important; margin-top: 2px; font-weight: 400; }
        .score-metric .metric-label { color: #f1f5f9 !important; font-weight: 600; }
        .trading-scenarios { margin-bottom: 15px; padding: 15px; background: rgba(15, 23, 42, 0.4); border-radius: 12px; border: 1px solid #334155; }
        .scenario-title { font-size: 0.9rem; font-weight: 600; color: #f1f5f9; margin-bottom: 12px; text-align: center; }
        .scenario { margin-bottom: 12px; padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }
        .buy-scenario { background: rgba(34, 197, 94, 0.05); border-color: rgba(34, 197, 94, 0.2); }
        .sell-scenario { background: rgba(239, 68, 68, 0.05); border-color: rgba(239, 68, 68, 0.2); }
        .scenario-header { font-size: 0.8rem; font-weight: 600; margin-bottom: 8px; color: #f1f5f9; text-align: center; }
        .scenario-targets { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .target { text-align: center; padding: 6px; border-radius: 6px; }
        .target-label { font-size: 0.7rem; color: #f1f5f9; display: block; font-weight: 500; }
        .target-value { font-size: 0.85rem; font-weight: 600; color: #f1f5f9; display: block; }
        .target-percent { font-size: 0.65rem; color: #60a5fa; display: block; font-weight: 500; }
        .target.profit { background: rgba(34, 197, 94, 0.1); }
        .target.loss { background: rgba(239, 68, 68, 0.1); }

        .confidence-poor { background: linear-gradient(90deg, #dc2626, #ef4444); }
        .confidence-weak { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
        .confidence-good { background: linear-gradient(90deg, #22c55e, #34d399); }
        .confidence-strong { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
        .confidence-excellent { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }


        .footer { text-align: center; margin-top: 25px; color: #64748b; font-size: 0.85rem; }
        .update-indicator { position: fixed; top: 20px; right: 20px; background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 10px 18px; border-radius: 25px; font-size: 0.85rem; opacity: 0; transition: all 0.3s ease; z-index: 1000; }
        .update-indicator.show { opacity: 1; }
    </style>
    """

def get_dashboard_js():
    """Retorna el JavaScript del dashboard"""
    return """
    <script>
        // Auto-refresh cada 30 segundos
        setInterval(() => {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                    showUpdateIndicator();
                })
                .catch(error => console.error('Error:', error));
        }, 30000);
        
        function updateDashboard(data) {
            // Actualizar datos en tiempo real
            Object.keys(data.market_data || {}).forEach(symbol => {
                const symbolData = data.market_data[symbol];
                updateElement(`[data-price="${symbol}"]`, `$${symbolData.price?.toLocaleString()}`);
                updateElement(`[data-rsi="${symbol}"]`, symbolData.rsi?.toFixed(1));
                updateElement(`[data-score="${symbol}"]`, `${symbolData.score}/100`);

                // Actualizar etiquetas de confianza si es necesario
                const scoreValue = symbolData.score || 0;
                let confidenceLabel = "";
                let confidenceEmoji = "";

                if (scoreValue >= 90) {
                    confidenceLabel = "EXCELENTE";
                    confidenceEmoji = "🔥";
                } else if (scoreValue >= 75) {
                    confidenceLabel = "FUERTE";
                    confidenceEmoji = "🎯";
                } else if (scoreValue >= 60) {
                    confidenceLabel = "BUENA";
                    confidenceEmoji = "✅";
                } else if (scoreValue >= 40) {
                    confidenceLabel = "DÉBIL";
                    confidenceEmoji = "⚠️";
                } else {
                    confidenceLabel = "POBRE";
                    confidenceEmoji = "❌";
                }

                // Actualizar la etiqueta de confianza
                const scoreElement = document.querySelector(`[data-score="${symbol}"]`);
                if (scoreElement) {
                    scoreElement.textContent = `${confidenceEmoji} ${scoreValue}/100`;
                }

                // Actualizar la etiqueta de confianza
                const labelElement = scoreElement?.parentElement?.querySelector('.metric-label');
                if (labelElement) {
                    labelElement.textContent = confidenceLabel;
                }
            });

            // Actualizar timestamp si está disponible
            if (data.bot_status?.last_analysis) {
                const lastTime = new Date(data.bot_status.last_analysis);
                const now = new Date();
                const diffSeconds = Math.floor((now - lastTime) / 1000);
                const timeStr = lastTime.toLocaleTimeString();

                let agoStr;
                if (diffSeconds < 0) {
                    agoStr = 'ahora';
                } else if (diffSeconds < 60) {
                    agoStr = `hace ${diffSeconds}s`;
                } else if (diffSeconds < 3600) {
                    agoStr = `hace ${Math.floor(diffSeconds/60)}m`;
                } else {
                    agoStr = `hace ${Math.floor(diffSeconds/3600)}h`;
                }

                updateElement('.status-item:nth-child(5)', `<strong>Último:</strong> ${timeStr} (${agoStr})`);
            }
        }

        function updateElement(selector, value) {
            const element = document.querySelector(selector);
            if (element && value) {
                // Si contiene HTML, usar innerHTML, sino textContent
                if (value.includes('<') && value.includes('>')) {
                    element.innerHTML = value;
                } else {
                    element.textContent = value;
                }
            }
        }
        
        function showUpdateIndicator() {
            const indicator = document.getElementById('updateIndicator');
            indicator.classList.add('show');
            setTimeout(() => indicator.classList.remove('show'), 2000);
        }
    </script>
    """
