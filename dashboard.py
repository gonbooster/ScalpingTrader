# dashboard.py - Frontend y dashboard web
from datetime import datetime

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
    crypto_cards = generate_crypto_cards(market_data, last_signals)
    
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
            </div>

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

            <div class="crypto-grid">
                {crypto_cards}
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

def generate_crypto_cards(market_data, last_signals):
    """Genera las cards de criptomonedas"""
    crypto_cards = ""
    
    for symbol, data in market_data.items():
        # Datos básicos
        name = symbol.replace('USDT', '')
        price = f"${data.get('price', 0):,.2f}"
        rsi = data.get('rsi', 0)
        rsi_15m = data.get('rsi_15m', 0)
        score = data.get('score', 0)
        
        # Nuevos datos del email
        candle_change = data.get('candle_change_percent', 0)
        vol_now = data.get('volume', 0)
        vol_avg = data.get('vol_avg', 1)
        
        # Targets para BUY y SELL
        tp_buy = data.get('take_profit_buy', 0)
        sl_buy = data.get('stop_loss_buy', 0)
        move_buy = data.get('expected_move_buy', 0)
        rr_buy = data.get('risk_reward_buy', 0)
        
        tp_sell = data.get('take_profit_sell', 0)
        sl_sell = data.get('stop_loss_sell', 0)
        move_sell = data.get('expected_move_sell', 0)
        rr_sell = data.get('risk_reward_sell', 0)
        
        # Señal actual
        signal = last_signals.get(symbol, {})
        signal_type = signal.get('action', 'ESPERANDO')
        signal_class = f"signal-{signal_type.lower()}"
        signal_text = f"🎯 {signal_type}"
        
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
        volume_class = "high-volume" if vol_now > vol_avg * 1.5 else "normal-volume"
        
        # Color del símbolo según el tipo
        symbol_color = "#f7931a" if name == "BTC" else "#627eea" if name == "ETH" else "#9945ff"
        symbol_icon = "₿" if name == "BTC" else "Ξ" if name == "ETH" else "◎"
        
        crypto_cards += f"""
        <div class="crypto-card {name.lower()}" data-symbol="{symbol}" style="border-left: 4px solid {symbol_color};">
            <div class="crypto-header">
                <div class="crypto-name" style="color: {symbol_color};">
                    <span class="crypto-icon">{symbol_icon}</span> {name}
                </div>
                <div class="crypto-price" data-price="{symbol}">{price}</div>
            </div>
            
            <div class="candle-change {candle_class}" data-candle="{symbol}">
                📈 Cambio Actual: {candle_change:+.2f}%
            </div>
            
            <div class="metrics-grid">
                <div class="metric rsi-metric">
                    <div class="metric-value" data-rsi="{symbol}">{rsi:.1f}</div>
                    <div class="metric-label">RSI 1min</div>
                </div>
                <div class="metric rsi-metric">
                    <div class="metric-value" data-rsi15="{symbol}">{rsi_15m:.1f}</div>
                    <div class="metric-label">RSI 15min</div>
                </div>
                <div class="metric volume-metric {volume_class}">
                    <div class="metric-value" data-volume="{symbol}">{vol_now:,.0f}</div>
                    <div class="metric-label">Volumen Actual</div>
                </div>
                <div class="metric score-metric {confidence_class}">
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
            
            <div class="signal-status {signal_class}" data-signal="{symbol}">
                {signal_text}
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill {confidence_class}" style="width: {score}%"></div>
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
        .header p { color: #94a3b8; font-size: 1rem; }
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
        .crypto-price { font-size: 1.3rem; color: #34d399; font-weight: 700; }
        .candle-change { text-align: center; padding: 8px 12px; border-radius: 8px; font-weight: 600; margin-bottom: 15px; }
        .candle-change.positive { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .candle-change.negative { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px; }
        .metric { background: rgba(30, 41, 59, 0.6); padding: 12px; border-radius: 10px; text-align: center; border: 1px solid #475569; }
        .metric-value { font-size: 1.2rem; font-weight: 700; color: #f1f5f9; }
        .metric-label { font-size: 0.8rem; color: #f1f5f9 !important; margin-top: 4px; font-weight: 500; }
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
        .signal-status { padding: 12px; border-radius: 10px; text-align: center; font-weight: 700; margin-bottom: 12px; text-transform: uppercase; }
        .signal-buy { background: linear-gradient(135deg, #22c55e, #16a34a); color: white; }
        .signal-sell { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; }
        .signal-wait, .signal-esperando { background: linear-gradient(135deg, #6b7280, #4b5563); color: white; }
        .confidence-bar { background: rgba(15, 23, 42, 0.6); border-radius: 12px; height: 10px; overflow: hidden; border: 1px solid #334155; }
        .confidence-fill { height: 100%; transition: width 0.5s ease; }
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
            if (element && value) element.textContent = value;
        }
        
        function showUpdateIndicator() {
            const indicator = document.getElementById('updateIndicator');
            indicator.classList.add('show');
            setTimeout(() => indicator.classList.remove('show'), 2000);
        }
    </script>
    """
