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

            .auto-status {{
                display: flex; gap: 20px; align-items: center; justify-content: center;
                background: rgba(15, 23, 42, 0.6); padding: 10px 20px; border-radius: 8px;
                border: 1px solid #334155; font-size: 0.9rem; color: #94a3b8;
                margin-bottom: 20px;
            }}
            .auto-status span {{ display: flex; align-items: center; gap: 5px; }}
            #autoRefresh {{ color: #22c55e; font-weight: 600; }}
            .updating {{ color: #f59e0b !important; }}
            
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
                <div class="auto-status">
                    <span id="lastUpdate">Última actualización: Cargando...</span>
                    <span id="autoRefresh">🔄 Auto-refresh: 30s</span>
                </div>
            </div>
            
            <div class="warning">
                ⚠️ DASHBOARD PRIVADO - Solo para análisis interno y mejora del sistema<br>
                🎯 <strong>SISTEMA PROFESIONAL:</strong> Solo se analizan señales con Score ≥80 (PREMIUM). Estas son las únicas que envían emails y tienen máxima probabilidad de éxito (≥70%).
            </div>
            
            <div class="stats-grid">
                <div class="stat-card" title="📊 Total de señales generadas por el algoritmo de trading. Incluye todas las señales BUY/SELL procesadas desde el inicio del sistema.">
                    <div class="stat-value win-rate">{total_signals}</div>
                    <div class="stat-label">Total Señales</div>
                    <div class="stat-trend">✅ {performance_stats.get('wins', 0)} wins • ❌ {performance_stats.get('losses', 0)} losses • ⏰ {performance_stats.get('expired', 0)} expired • 🔄 {performance_stats.get('pending', 0)} pending</div>
                </div>

                <div class="stat-card" title="📈 Porcentaje de señales exitosas (WIN) vs total de señales completadas. Se calcula como: (Señales WIN / Señales Completadas) × 100. No incluye señales pendientes.">
                    <div class="stat-value {'win-rate' if win_rate >= 60 else 'neutral' if win_rate >= 50 else 'loss-rate'}">{win_rate:.1f}%</div>
                    <div class="stat-label">Win Rate</div>
                    <div class="stat-trend">{'🎯 Excelente' if win_rate >= 70 else '✅ Bueno' if win_rate >= 60 else '⚠️ Mejorable' if win_rate >= 50 else '❌ Revisar'}</div>
                </div>

                <div class="stat-card" title="💰 Retorno promedio de todas las señales completadas. Se calcula como: Suma de todos los retornos / Número de señales completadas. Incluye tanto ganancias como pérdidas.">
                    <div class="stat-value {'win-rate' if avg_return > 0 else 'loss-rate'}">{avg_return:+.2f}%</div>
                    <div class="stat-label">Retorno Promedio</div>
                    <div class="stat-trend">💰 Mejor: {safe_float(performance_stats.get('best_return', 0)):+.2f}% • 📉 Peor: {safe_float(performance_stats.get('worst_return', 0)):+.2f}%</div>
                </div>

                <div class="stat-card">
                    <div class="stat-value {'win-rate' if safe_float(performance_stats.get('net_profit', 0)) > 0 else 'loss-rate'}">{safe_float(performance_stats.get('net_profit', 0)):+.2f}%</div>
                    <div class="stat-label">Profit Neto</div>
                    <div class="stat-trend">📈 Total: {safe_float(performance_stats.get('total_profit', 0)):+.2f}% • 📉 Pérdidas: {safe_float(performance_stats.get('total_loss', 0)):+.2f}%</div>
                </div>

                <div class="stat-card" title="🎯 Score promedio del SISTEMA PROFESIONAL. Evalúa: Momentum Multi-timeframe (35%), Volumen Inteligente (30%), Price Action (25%), Volatilidad Controlada (10%). Solo señales ≥80 envían emails y se analizan aquí.">
                    <div class="stat-value neutral">{safe_float(performance_stats.get('avg_score', 0)):.0f}/100</div>
                    <div class="stat-label">Score Promedio (Sistema Profesional)</div>
                    <div class="stat-trend">⏱️ Tiempo medio: {safe_float(performance_stats.get('avg_time_minutes', 0)):.0f} min • 📧 Solo Score ≥80</div>
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

                <!-- Filtros y Controles -->
                <div class="filters-container" style="margin-bottom: 20px; padding: 15px; background: rgba(15, 23, 42, 0.3); border-radius: 8px; display: flex; gap: 15px; flex-wrap: wrap; align-items: center;">
                    <div class="filter-group">
                        <label style="color: #94a3b8; font-size: 0.9rem; margin-right: 8px;">Símbolo:</label>
                        <select id="symbolFilter" style="padding: 5px 10px; border-radius: 4px; border: 1px solid #334155; background: #1e293b; color: #e2e8f0;">
                            <option value="">Todos</option>
                            <option value="BTCUSDT">₿ BTCUSDT</option>
                            <option value="ETHUSDT">Ξ ETHUSDT</option>
                            <option value="SOLUSDT">◎ SOLUSDT</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label style="color: #94a3b8; font-size: 0.9rem; margin-right: 8px;">Tipo:</label>
                        <select id="typeFilter" style="padding: 5px 10px; border-radius: 4px; border: 1px solid #334155; background: #1e293b; color: #e2e8f0;">
                            <option value="">Todos</option>
                            <option value="buy">🟢 BUY</option>
                            <option value="sell">🔴 SELL</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label style="color: #94a3b8; font-size: 0.9rem; margin-right: 8px;">Estado:</label>
                        <select id="statusFilter" style="padding: 5px 10px; border-radius: 4px; border: 1px solid #334155; background: #1e293b; color: #e2e8f0;">
                            <option value="">Todos</option>
                            <option value="WIN">✅ WIN</option>
                            <option value="LOSS">❌ LOSS</option>
                            <option value="EXPIRED">⏰ EXPIRED</option>
                            <option value="PENDING">🔄 PENDING</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label style="color: #94a3b8; font-size: 0.9rem; margin-right: 8px;">Score Min:</label>
                        <input type="number" id="scoreFilter" min="0" max="100" placeholder="0-100" style="width: 80px; padding: 5px 8px; border-radius: 4px; border: 1px solid #334155; background: #1e293b; color: #e2e8f0;">
                    </div>

                    <div class="filter-group">
                        <label style="color: #94a3b8; font-size: 0.9rem; margin-right: 8px;">Por página:</label>
                        <select id="pageSize" style="padding: 5px 10px; border-radius: 4px; border: 1px solid #334155; background: #1e293b; color: #e2e8f0;">
                            <option value="10">10</option>
                            <option value="25" selected>25</option>
                            <option value="50">50</option>
                            <option value="100">100</option>
                        </select>
                    </div>

                    <button onclick="resetFilters()" style="padding: 6px 12px; border-radius: 4px; border: 1px solid #334155; background: #374151; color: #e2e8f0; cursor: pointer;">
                        🔄 Reset
                    </button>
                </div>

                <div class="table-container">
                    <table class="signals-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Símbolo</th>
                            <th>Tipo</th>
                            <th>Score</th>
                            <th>Precio</th>
                            <th>TP/SL</th>
                            <th>Estado</th>
                            <th>Retorno</th>
                            <th>Tiempo</th>
                        </tr>
                    </thead>
                    <tbody id="signalsTableBody">
                        {generate_signals_table(recent_signals)}
                    </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            let refreshCountdown = 30;
            let lastSignalCount = {performance_stats.get('total_signals', 0)};

            // Función para actualizar timestamp
            function updateTimestamp() {{
                const now = new Date();
                const timeStr = now.toLocaleTimeString('es-ES');
                document.getElementById('lastUpdate').innerHTML = '⏰ Última actualización: ' + timeStr;
            }}

            // Función para auto-evaluación cuando hay nuevas señales
            async function autoEvaluateIfNeeded() {{
                try {{
                    const response = await fetch('/api/signal-count');
                    const data = await response.json();

                    if (data.count > lastSignalCount) {{
                        console.log('🔍 Nuevas señales detectadas, evaluando automáticamente...');
                        await autoEvaluate();
                        lastSignalCount = data.count;
                    }}
                }} catch (error) {{
                    console.log('Error verificando señales:', error);
                }}
            }}

            // Función de auto-evaluación silenciosa
            async function autoEvaluate() {{
                try {{
                    const response = await fetch('/force-evaluate', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    const result = await response.json();
                    if (result.success && result.updated_count > 0) {{
                        console.log('✅ Auto-evaluación: ' + result.updated_count + ' señales actualizadas');
                    }}
                }} catch (error) {{
                    console.log('Error en auto-evaluación:', error);
                }}
            }}

            // Countdown para refresh
            function updateCountdown() {{
                document.getElementById('autoRefresh').innerHTML = '🔄 Próxima actualización: ' + refreshCountdown + 's';
                refreshCountdown--;

                if (refreshCountdown < 0) {{
                    document.getElementById('autoRefresh').innerHTML = '🔄 Actualizando...';
                    document.getElementById('autoRefresh').className = 'updating';
                    location.reload();
                }}
            }}

            // Inicializar
            updateTimestamp();
            setInterval(updateTimestamp, 1000);
            setInterval(updateCountdown, 1000);
            setInterval(autoEvaluateIfNeeded, 10000); // Verificar cada 10 segundos

            // JavaScript para filtros y paginación
            let allSignals = [];
            let filteredSignals = [];
            let currentPage = 1;
            let pageSize = 25;

            // Cargar datos iniciales
            function loadSignalsData() {{
                const tableBody = document.getElementById('signalsTableBody');
                if (!tableBody) return;

                // Extraer datos de la tabla existente
                const rows = tableBody.querySelectorAll('tr');
                allSignals = [];

                rows.forEach(row => {{
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 9) {{
                        allSignals.push({{
                            timestamp: cells[0].textContent.trim(),
                            symbol: cells[1].textContent.trim(),
                            type: cells[2].textContent.trim(),
                            score: parseInt(cells[3].textContent.replace(/[^0-9]/g, '')) || 0,
                            price: cells[4].textContent.trim(),
                            tpsl: cells[5].textContent.trim(),
                            status: cells[6].textContent.trim(),
                            return: cells[7].textContent.trim(),
                            time: cells[8].textContent.trim(),
                            html: row.outerHTML
                        }});
                    }}
                }});

                filteredSignals = [...allSignals];
                applyFilters();
            }}

            // Aplicar filtros
            function applyFilters() {{
                const symbolFilter = document.getElementById('symbolFilter').value;
                const typeFilter = document.getElementById('typeFilter').value;
                const statusFilter = document.getElementById('statusFilter').value;
                const scoreFilter = parseInt(document.getElementById('scoreFilter').value) || 0;

                filteredSignals = allSignals.filter(signal => {{
                    if (symbolFilter && !signal.symbol.includes(symbolFilter)) return false;
                    if (typeFilter && !signal.type.toLowerCase().includes(typeFilter)) return false;
                    if (statusFilter && !signal.status.includes(statusFilter)) return false;
                    if (scoreFilter && signal.score < scoreFilter) return false;
                    return true;
                }});

                currentPage = 1;
                updateTable();
                updatePagination();
            }}

            // Actualizar tabla
            function updateTable() {{
                const tableBody = document.getElementById('signalsTableBody');
                if (!tableBody) return;

                const startIndex = (currentPage - 1) * pageSize;
                const endIndex = startIndex + pageSize;
                const pageSignals = filteredSignals.slice(startIndex, endIndex);

                if (pageSignals.length === 0) {{
                    tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #94a3b8; padding: 20px;">No hay señales que coincidan con los filtros</td></tr>';
                }} else {{
                    tableBody.innerHTML = pageSignals.map(signal => signal.html).join('');
                }}
            }}

            // Actualizar paginación
            function updatePagination() {{
                const totalPages = Math.ceil(filteredSignals.length / pageSize);
                let paginationHtml = '';

                if (totalPages > 1) {{
                    paginationHtml = '<div style="margin-top: 20px; text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;">';

                    // Botón anterior
                    if (currentPage > 1) {{
                        paginationHtml += '<button onclick="changePage(' + (currentPage - 1) + ')" style="padding: 8px 12px; border-radius: 4px; border: 1px solid #334155; background: #374151; color: #e2e8f0; cursor: pointer;">← Anterior</button>';
                    }}

                    // Números de página
                    const startPage = Math.max(1, currentPage - 2);
                    const endPage = Math.min(totalPages, currentPage + 2);

                    for (let i = startPage; i <= endPage; i++) {{
                        const isActive = i === currentPage;
                        paginationHtml += '<button onclick="changePage(' + i + ')" style="padding: 8px 12px; border-radius: 4px; border: 1px solid #334155; background: ' + (isActive ? '#3b82f6' : '#374151') + '; color: #e2e8f0; cursor: pointer; font-weight: ' + (isActive ? '600' : 'normal') + ';">' + i + '</button>';
                    }}

                    // Botón siguiente
                    if (currentPage < totalPages) {{
                        paginationHtml += '<button onclick="changePage(' + (currentPage + 1) + ')" style="padding: 8px 12px; border-radius: 4px; border: 1px solid #334155; background: #374151; color: #e2e8f0; cursor: pointer;">Siguiente →</button>';
                    }}

                    paginationHtml += '<span style="color: #94a3b8; margin-left: 15px;">Página ' + currentPage + ' de ' + totalPages + ' (' + filteredSignals.length + ' señales)</span>';
                    paginationHtml += '</div>';
                }}

                // Agregar paginación después de la tabla
                let paginationContainer = document.getElementById('paginationContainer');
                if (!paginationContainer) {{
                    paginationContainer = document.createElement('div');
                    paginationContainer.id = 'paginationContainer';
                    document.querySelector('.table-container').after(paginationContainer);
                }}
                paginationContainer.innerHTML = paginationHtml;
            }}

            // Cambiar página
            function changePage(page) {{
                currentPage = page;
                updateTable();
                updatePagination();
            }}

            // Reset filtros
            function resetFilters() {{
                document.getElementById('symbolFilter').value = '';
                document.getElementById('typeFilter').value = '';
                document.getElementById('statusFilter').value = '';
                document.getElementById('scoreFilter').value = '';
                document.getElementById('pageSize').value = '25';
                pageSize = 25;
                applyFilters();
            }}

            // Inicializar filtros cuando la página carga
            setTimeout(() => {{
                loadSignalsData();

                // Event listeners para filtros
                document.getElementById('symbolFilter').addEventListener('change', applyFilters);
                document.getElementById('typeFilter').addEventListener('change', applyFilters);
                document.getElementById('statusFilter').addEventListener('change', applyFilters);
                document.getElementById('scoreFilter').addEventListener('input', applyFilters);

                // Tamaño de página
                document.getElementById('pageSize').addEventListener('change', function() {{
                    pageSize = parseInt(this.value);
                    currentPage = 1;
                    updateTable();
                    updatePagination();
                }});
            }}, 1000);
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
        # Mapear resultado a texto legible - SINCRONIZADO CON CARDS
        result_raw = signal.get('result')

        # Debug: mostrar el valor real
        print(f"DEBUG: signal {signal.get('id')} result_raw = '{result_raw}' (type: {type(result_raw)})")

        if result_raw in ['WIN', 'WIN_TP', 'WIN_TIME'] or result_raw == 1:
            result_text = '✅ WIN'
            status_class = 'status-win'
        elif result_raw in ['LOSS', 'LOSS_SL', 'LOSS_TIME'] or result_raw == 0:
            result_text = '❌ LOSS'
            status_class = 'status-loss'
        elif result_raw == 'EXPIRED' or result_raw == 2:
            result_text = '⏰ EXPIRED'
            status_class = 'status-pending'
        elif result_raw is None or str(result_raw) == 'None' or result_raw == '':
            result_text = '🔄 PENDING'
            status_class = 'status-pending'
        else:
            # Si es un número extraño, convertir a estado
            try:
                num_result = float(result_raw)
                if num_result == 1:
                    result_text = '✅ WIN'
                    status_class = 'status-win'
                elif num_result == 0:
                    result_text = '❌ LOSS'
                    status_class = 'status-loss'
                elif num_result == 2:
                    result_text = '⏰ EXPIRED'
                    status_class = 'status-pending'
                else:
                    result_text = '🔄 PENDING'
                    status_class = 'status-pending'
            except:
                # Valor desconocido, mostrar tal como está para debug
                result_text = f'❓ {result_raw}'
                status_class = 'status-pending'

        # Calcular retorno real
        actual_return = safe_float(signal.get('actual_return', 0))

        # Calcular tiempo transcurrido más realista
        time_resolution = safe_float(signal.get('time_to_resolution', 0))
        if time_resolution == 0 or time_resolution > 1000:
            try:
                from datetime import datetime
                timestamp_str = signal.get('timestamp', '')
                if 'T' in timestamp_str:
                    signal_time = datetime.fromisoformat(timestamp_str.replace('T', ' '))
                    now = datetime.now()
                    time_diff = (now - signal_time).total_seconds() / 60
                    time_resolution = min(int(time_diff), 480)  # Max 8 horas
                else:
                    time_resolution = 0
            except:
                time_resolution = 0

        # Formatear TP/SL
        tp_price = safe_float(signal.get('tp_price', 0))
        sl_price = safe_float(signal.get('sl_price', 0))
        entry_price = safe_float(signal.get('entry_price', 0))

        # Calcular % de TP y SL
        if entry_price > 0:
            tp_percent = ((tp_price - entry_price) / entry_price) * 100 if tp_price > 0 else 0
            sl_percent = ((sl_price - entry_price) / entry_price) * 100 if sl_price > 0 else 0

            # Para SELL, invertir los cálculos
            if signal.get('signal_type', '').lower() == 'sell':
                tp_percent = -tp_percent
                sl_percent = -sl_percent
        else:
            tp_percent = 0
            sl_percent = 0

        tp_sl_text = f"TP: {tp_percent:+.1f}%<br>SL: {sl_percent:+.1f}%" if tp_price > 0 and sl_price > 0 else "N/A"

        html += f"""
        <tr>
            <td>{signal.get('timestamp', '')[:16]}</td>
            <td>{signal.get('symbol', '')}</td>
            <td>{signal.get('signal_type', '').upper()}</td>
            <td>{safe_float(signal.get('score', 0)):.0f}/100</td>
            <td>${safe_float(signal.get('entry_price', 0)):,.2f}</td>
            <td style="font-size: 0.85rem; line-height: 1.2;">{tp_sl_text}</td>
            <td class="{status_class}"><strong>{result_text}</strong></td>
            <td class="{status_class}">{actual_return:+.2f}%</td>
            <td>{int(time_resolution)} min</td>
        </tr>
        """
    return html

def get_analytics_data():
    """Obtiene datos para el dashboard de analytics"""
    from performance_tracker import performance_tracker
    
    # Obtener estadísticas de rendimiento
    performance_stats = performance_tracker.get_performance_stats(30)
    
    # Obtener señales recientes directamente de la base de datos
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
        recent_signals.append({
            'id': signal[0],
            'timestamp': signal[1],
            'symbol': signal[2],
            'signal_type': signal[3],
            'entry_price': safe_float(signal[4]),
            'score': safe_float(signal[5]),
            'tp_price': safe_float(signal[15]),  # Take Profit
            'sl_price': safe_float(signal[16]),  # Stop Loss
            'result': signal[18] if signal[18] is not None else None,
            'actual_return': safe_float(signal[21]),
            'time_to_resolution': safe_float(signal[22]),
            'today': signal[1][:10] == datetime.now().strftime('%Y-%m-%d') if signal[1] else False
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
