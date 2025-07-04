# analytics_dashboard.py - Dashboard de análisis de rendimiento
from flask import jsonify
import sqlite3
from datetime import datetime, timedelta

import json

def safe_float(value, default=0):
    """Convierte un valor a float de forma segura"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def generate_analytics_dashboard(performance_stats, recent_signals, market_trends):
    """Genera el dashboard de análisis de rendimiento"""
    
    # Calcular métricas adicionales con validación
    total_signals = performance_stats.get('total_signals', 0)
    win_rate = safe_float(performance_stats.get('win_rate', 0))
    avg_return = safe_float(performance_stats.get('avg_return', 0))
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📊 Trading Analytics - Performance Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9; min-height: 100vh; padding: 20px;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; }}

            /* Header Navigation */
            .header-nav {{
                display: flex; justify-content: center; gap: 20px; margin-bottom: 30px;
                padding: 15px; background: rgba(30, 41, 59, 0.8); border-radius: 15px;
            }}
            .nav-link {{
                color: #94a3b8; text-decoration: none; padding: 10px 20px;
                border-radius: 8px; font-weight: 500; transition: all 0.3s ease;
                border: 1px solid transparent;
            }}
            .nav-link:hover {{ background: rgba(148, 163, 184, 0.1); color: #f1f5f9; border-color: rgba(148, 163, 184, 0.3); }}
            .nav-link.active {{ background: rgba(59, 130, 246, 0.2); color: #3b82f6; border-color: rgba(59, 130, 246, 0.3); }}

            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .header p {{ color: #94a3b8; font-size: 1.1rem; }}
            
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ 
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                padding: 25px; border-radius: 15px; border: 1px solid #475569;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }}
            .stat-value {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 8px; }}
            .stat-label {{ color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }}
            .stat-trend {{ font-size: 0.8rem; margin-top: 8px; }}
            
            .win-rate {{ color: #22c55e; }}
            .loss-rate {{ color: #ef4444; }}
            .neutral {{ color: #f59e0b; }}
            
            .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
            .chart-card {{ 
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                padding: 25px; border-radius: 15px; border: 1px solid #475569;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }}
            .chart-title {{ font-size: 1.3rem; font-weight: 600; margin-bottom: 20px; color: #f1f5f9; }}
            
            .score-breakdown {{ margin-bottom: 30px; }}
            .score-item {{ 
                display: flex; justify-content: space-between; align-items: center;
                padding: 15px; margin-bottom: 10px; border-radius: 10px;
                background: rgba(15, 23, 42, 0.6); border: 1px solid #334155;
            }}
            .score-range {{ font-weight: 600; }}
            .score-stats {{ display: flex; gap: 20px; font-size: 0.9rem; }}
            
            .signals-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .signals-table th, .signals-table td {{
                padding: 12px; text-align: left; border-bottom: 1px solid #334155;
            }}
            .signals-table th {{
                background: rgba(15, 23, 42, 0.8); color: #94a3b8; font-weight: 600;
                text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px;
            }}
            .signals-table tr:hover {{ background: rgba(15, 23, 42, 0.4); }}

            /* Responsive table */
            .table-container {{ overflow-x: auto; }}
            @media (max-width: 768px) {{
                .signals-table {{ font-size: 0.8rem; }}
                .signals-table th, .signals-table td {{ padding: 8px 4px; }}
                .signals-table th:nth-child(n+6), .signals-table td:nth-child(n+6) {{ display: none; }}
            }}
            @media (max-width: 480px) {{
                .signals-table th:nth-child(n+4), .signals-table td:nth-child(n+4) {{ display: none; }}
                .signals-table th, .signals-table td {{ padding: 6px 2px; font-size: 0.7rem; }}
            }}
            
            .status-win {{ color: #22c55e; font-weight: 600; }}
            .status-loss {{ color: #ef4444; font-weight: 600; }}
            .status-pending {{ color: #f59e0b; font-weight: 600; }}
            
            .refresh-btn {{ 
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white; border: none; padding: 12px 24px; border-radius: 8px;
                font-weight: 600; cursor: pointer; margin-bottom: 20px;
            }}
            .refresh-btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4); }}
            
            .warning {{ 
                background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);
                padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center;
                color: #fecaca; font-weight: 600;
            }}
            
            @media (max-width: 768px) {{
                .charts-grid {{ grid-template-columns: 1fr; }}
                .stats-grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <nav class="header-nav">
                <a href="/" class="nav-link">📊 Dashboard</a>
                <a href="/analytics" class="nav-link active">📈 Análisis</a>
                <a href="/instructions" class="nav-link">📚 Instrucciones</a>
            </nav>

            <div class="header">
                <h1>📊 Trading Performance Analytics</h1>
                <p>Sistema de análisis de rendimiento y optimización de señales</p>
                <button class="refresh-btn" onclick="location.reload()">🔄 Actualizar Datos</button>
                <button class="refresh-btn" onclick="forceEvaluate()" style="background: #f59e0b; margin-left: 10px;">⚡ Evaluar Señales</button>
            </div>
            
            <div class="warning">
                ⚠️ DASHBOARD PRIVADO - Solo para análisis interno y mejora del sistema
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value win-rate">{total_signals}</div>
                    <div class="stat-label">Total Señales</div>
                    <div class="stat-trend">✅ {performance_stats.get('wins', 0)} wins • ❌ {performance_stats.get('losses', 0)} losses • ⏰ {performance_stats.get('expired', 0)} expired • 🔄 {performance_stats.get('pending', 0)} pending</div>
                </div>

                <div class="stat-card">
                    <div class="stat-value {'win-rate' if win_rate >= 60 else 'neutral' if win_rate >= 50 else 'loss-rate'}">{win_rate:.1f}%</div>
                    <div class="stat-label">Win Rate</div>
                    <div class="stat-trend">{'🎯 Excelente' if win_rate >= 70 else '✅ Bueno' if win_rate >= 60 else '⚠️ Mejorable' if win_rate >= 50 else '❌ Revisar'}</div>
                </div>

                <div class="stat-card">
                    <div class="stat-value {'win-rate' if avg_return > 0 else 'loss-rate'}">{avg_return:+.2f}%</div>
                    <div class="stat-label">Retorno Promedio</div>
                    <div class="stat-trend">💰 Mejor: {safe_float(performance_stats.get('best_return', 0)):+.2f}% • 📉 Peor: {safe_float(performance_stats.get('worst_return', 0)):+.2f}%</div>
                </div>

                <div class="stat-card">
                    <div class="stat-value {'win-rate' if safe_float(performance_stats.get('net_profit', 0)) > 0 else 'loss-rate'}">{safe_float(performance_stats.get('net_profit', 0)):+.2f}%</div>
                    <div class="stat-label">Profit Neto</div>
                    <div class="stat-trend">📈 Total: {safe_float(performance_stats.get('total_profit', 0)):+.2f}% • 📉 Pérdidas: {safe_float(performance_stats.get('total_loss', 0)):+.2f}%</div>
                </div>

                <div class="stat-card">
                    <div class="stat-value neutral">{safe_float(performance_stats.get('avg_score', 0)):.0f}/100</div>
                    <div class="stat-label">Score Promedio</div>
                    <div class="stat-trend">⏱️ Tiempo medio: {safe_float(performance_stats.get('avg_time_minutes', 0)):.0f} min</div>
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-title">📈 Rendimiento por Score</div>
                    <div class="score-breakdown">
                        {generate_score_breakdown(performance_stats.get('score_breakdown', []))}
                    </div>
                </div>

                <div class="chart-card">
                    <div class="chart-title">💰 Análisis por Símbolo</div>
                    <div class="score-breakdown">
                        {generate_symbol_breakdown(performance_stats.get('symbol_breakdown', []))}
                    </div>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-title">🕐 Mejores Horarios</div>
                    <div class="score-breakdown">
                        {generate_hourly_breakdown(performance_stats.get('hourly_breakdown', []))}
                    </div>
                </div>

                <div class="chart-card">
                    <div class="chart-title">📊 Análisis de Volatilidad</div>
                    <div class="score-breakdown">
                        {generate_volatility_breakdown(performance_stats.get('volatility_breakdown', []))}
                    </div>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-title">🔥 Análisis de Rachas</div>
                    <div class="score-breakdown">
                        {generate_streak_analysis(performance_stats.get('streak_analysis', {}))}
                    </div>
                </div>

                <div class="chart-card">
                    <div class="chart-title">⏱️ Métricas de Sistema</div>
                    <div class="score-item">
                        <span class="score-range">Tiempo Promedio TP/SL</span>
                        <span class="score-stats">{performance_stats.get('avg_time_minutes', 0):.0f} minutos</span>
                    </div>
                    <div class="score-item">
                        <span class="score-range">Señales Hoy</span>
                        <span class="score-stats">{len([s for s in recent_signals if s.get('today', False)])} señales</span>
                    </div>
                    <div class="score-item">
                        <span class="score-range">Última Actualización</span>
                        <span class="score-stats">{datetime.now().strftime('%H:%M:%S')}</span>
                    </div>
                    <div class="score-item">
                        <span class="score-range">Fiabilidad Sistema</span>
                        <span class="score-stats">{'🎯 Alta' if win_rate >= 60 else '⚠️ Media' if win_rate >= 50 else '❌ Baja'}</span>
                    </div>
                </div>
            </div>
            
            <div class="chart-card">
                <div class="chart-title">📋 Señales Recientes</div>
                <div class="table-container">
                    <table class="signals-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Símbolo</th>
                            <th>Tipo</th>
                            <th>Score</th>
                            <th>Precio</th>
                            <th>Estado</th>
                            <th>Retorno</th>
                            <th>Tiempo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_signals_table(recent_signals)}
                    </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            // Auto-refresh cada 5 minutos
            setTimeout(function() {{ location.reload(); }}, 300000);

            // Actualizar timestamp cada segundo
            setInterval(function() {{
                var now = new Date();
                var timeElements = document.querySelectorAll('.stat-trend');
                // Actualizar solo el último elemento que es el timestamp
            }}, 1000);

            async function forceEvaluate() {{
                const btn = event.target;
                btn.disabled = true;
                btn.innerHTML = '⏳ Evaluando...';

                try {{
                    const response = await fetch('/force-evaluate', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});

                    const result = await response.json();

                    if (result.success) {{
                        btn.innerHTML = '✅ Completado';
                        alert('✅ Evaluación completada: ' + result.updated_count + ' señales actualizadas');
                        setTimeout(function() {{ location.reload(); }}, 1000);
                    }} else {{
                        btn.innerHTML = '❌ Error';
                        alert('❌ Error: ' + result.error);
                    }}
                }} catch (error) {{
                    btn.innerHTML = '❌ Error';
                    alert('❌ Error de conexión: ' + error.message);
                }}

                setTimeout(function() {{
                    btn.disabled = false;
                    btn.innerHTML = '⚡ Evaluar Señales';
                }}, 3000);
            }}
        </script>

    </body>
    </html>
    """

def generate_score_breakdown(score_breakdown):
    """Genera el desglose de rendimiento por score"""
    if not score_breakdown:
        return "<div class='score-item'><span>No hay datos suficientes</span></div>"

    html = ""
    for item in score_breakdown:
        win_rate = safe_float(item.get('win_rate', 0))
        color_class = 'win-rate' if win_rate >= 60 else 'neutral' if win_rate >= 50 else 'loss-rate'

        html += f"""
        <div class="score-item">
            <span class="score-range">{item.get('range', 'N/A')}</span>
            <div class="score-stats">
                <span class="{color_class}">{win_rate:.1f}% WR</span>
                <span>{item.get('count', 0)} señales</span>
                <span>{safe_float(item.get('avg_return', 0)):+.2f}%</span>
                <span>📈 {safe_float(item.get('best_return', 0)):+.1f}%</span>
            </div>
        </div>
        """
    return html

def generate_symbol_breakdown(symbol_breakdown):
    """Genera el desglose de rendimiento por símbolo"""
    if not symbol_breakdown:
        return "<div class='score-item'><span>No hay datos suficientes</span></div>"

    html = ""
    for item in symbol_breakdown:
        win_rate = safe_float(item.get('win_rate', 0))
        color_class = 'win-rate' if win_rate >= 60 else 'neutral' if win_rate >= 50 else 'loss-rate'

        # Emoji por símbolo
        emoji = {"BTCUSDT": "₿", "ETHUSDT": "Ξ", "SOLUSDT": "◎"}.get(item.get('symbol', ''), "💰")

        html += f"""
        <div class="score-item">
            <span class="score-range">{emoji} {item.get('symbol', 'N/A')}</span>
            <div class="score-stats">
                <span class="{color_class}">{win_rate:.1f}% WR</span>
                <span>{item.get('count', 0)} señales</span>
                <span>{safe_float(item.get('avg_return', 0)):+.2f}%</span>
                <span>📊 {safe_float(item.get('avg_score', 0)):.0f}/100</span>
            </div>
        </div>
        """
    return html

def generate_hourly_breakdown(hourly_breakdown):
    """Genera el desglose de rendimiento por horario"""
    if not hourly_breakdown:
        return "<div class='score-item'><span>No hay datos suficientes</span></div>"

    # Ordenar por win rate
    sorted_hours = sorted(hourly_breakdown, key=lambda x: x.get('win_rate', 0), reverse=True)[:8]

    html = ""
    for item in sorted_hours:
        win_rate = safe_float(item.get('win_rate', 0))
        color_class = 'win-rate' if win_rate >= 60 else 'neutral' if win_rate >= 50 else 'loss-rate'

        html += f"""
        <div class="score-item">
            <span class="score-range">🕐 {item.get('hour', 'N/A')}</span>
            <div class="score-stats">
                <span class="{color_class}">{win_rate:.1f}% WR</span>
                <span>{item.get('count', 0)} señales</span>
                <span>{safe_float(item.get('avg_return', 0)):+.2f}%</span>
            </div>
        </div>
        """
    return html

def generate_signals_table(recent_signals):
    """Genera la tabla de señales recientes"""
    if not recent_signals:
        return "<tr><td colspan='8' style='text-align: center; color: #94a3b8;'>No hay señales recientes</td></tr>"
    
    html = ""
    for signal in recent_signals[:20]:  # Últimas 20 señales
        status_class = {
            'WIN_TP': 'status-win',
            'LOSS_SL': 'status-loss',
            'PENDING': 'status-pending'
        }.get(signal.get('result', 'PENDING'), 'status-pending')
        
        html += f"""
        <tr>
            <td>{signal.get('timestamp', '')[:16]}</td>
            <td>{signal.get('symbol', '')}</td>
            <td>{signal.get('signal_type', '').upper()}</td>
            <td>{signal.get('score', 0)}/100</td>
            <td>${safe_float(signal.get('entry_price', 0)):,.2f}</td>
            <td class="{status_class}">{signal.get('result', 'None')}</td>
            <td>{safe_float(signal.get('actual_return', 0)):+.2f}%</td>
            <td>{int(safe_float(signal.get('time_to_resolution', 0)))} min</td>
        </tr>
        """
    return html

def get_analytics_data():
    """Obtiene datos para el dashboard de analytics"""
    from performance_tracker import performance_tracker
    
    # Obtener estadísticas de rendimiento
    performance_stats = performance_tracker.get_performance_stats(30)
    
    # Obtener señales recientes
    conn = sqlite3.connect(performance_tracker.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM signals 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''')
    
    signals_raw = cursor.fetchall()
    recent_signals = []
    
    for signal in signals_raw:
        # Función auxiliar para convertir a float de forma segura
        def safe_float(value, default=0):
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default

        recent_signals.append({
            'id': signal[0],
            'timestamp': signal[1],
            'symbol': signal[2],
            'signal_type': signal[3],
            'entry_price': safe_float(signal[4]),
            'score': safe_float(signal[5]),
            'result': signal[18] if signal[18] is not None else 'None',
            'actual_return': safe_float(signal[21]),
            'time_to_resolution': safe_float(signal[22]),
            'today': signal[1][:10] == datetime.now().strftime('%Y-%m-%d')
        })
    
    conn.close()
    
    # Tendencias de mercado (placeholder)
    market_trends = {}
    
    return performance_stats, recent_signals, market_trends

def generate_volatility_breakdown(volatility_analysis):
    """Genera el análisis de volatilidad por símbolo"""
    if not volatility_analysis:
        return "<div class='score-item'><span>No hay datos de volatilidad</span></div>"

    html = ""
    for item in volatility_analysis:
        emoji = {"BTCUSDT": "₿", "ETHUSDT": "Ξ", "SOLUSDT": "◎"}.get(item['symbol'], "💰")
        volatility_level = "🔥 Alta" if item.get('avg_atr', 0) > 100 else "⚡ Media" if item.get('avg_atr', 0) > 50 else "📊 Baja"

        html += f"""
        <div class="score-item">
            <span class="score-range">{emoji} {item['symbol']}</span>
            <div class="score-stats">
                <span>{volatility_level}</span>
                <span>ATR: {safe_float(item.get('avg_atr', 0)):.1f}</span>
                <span>Velas: {safe_float(item.get('avg_candle_volatility', 0)):.2f}%</span>
                <span>{item.get('count', 0)} señales</span>
            </div>
        </div>
        """
    return html

def generate_streak_analysis(streak_analysis):
    """Genera el análisis de rachas"""
    if not streak_analysis:
        return "<div class='score-item'><span>No hay datos de rachas</span></div>"

    current_streak = streak_analysis.get('current_streak', 0)
    max_win_streak = streak_analysis.get('max_win_streak', 0)
    max_loss_streak = streak_analysis.get('max_loss_streak', 0)
    streak_status = streak_analysis.get('streak_status', 'NEUTRAL')

    # Determinar emoji y color para racha actual
    if current_streak > 0:
        current_emoji = "🔥"
        current_color = "win-rate"
        current_text = f"Ganando {current_streak}"
    elif current_streak < 0:
        current_emoji = "❄️"
        current_color = "loss-rate"
        current_text = f"Perdiendo {abs(current_streak)}"
    else:
        current_emoji = "⚖️"
        current_color = "neutral"
        current_text = "Neutral"

    html = f"""
    <div class="score-item">
        <span class="score-range">🎯 Racha Actual</span>
        <div class="score-stats">
            <span class="{current_color}">{current_emoji} {current_text}</span>
        </div>
    </div>
    <div class="score-item">
        <span class="score-range">🏆 Mejor Racha Ganadora</span>
        <div class="score-stats">
            <span class="win-rate">🔥 {max_win_streak} seguidas</span>
        </div>
    </div>
    <div class="score-item">
        <span class="score-range">💀 Peor Racha Perdedora</span>
        <div class="score-stats">
            <span class="loss-rate">❄️ {max_loss_streak} seguidas</span>
        </div>
    </div>
    """
    return html
