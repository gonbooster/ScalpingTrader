def generate_dashboard_html(market_data, last_signals, signal_count, bot_running, last_analysis_time, using_simulation, email_status):
    """Dashboard limpio con diseño profesional"""

    # Generar filas de cryptos
    crypto_rows = ""
    for symbol, data in market_data.items():
        name = symbol.replace('USDT', '')
        price = data.get('price', 0)
        rsi_1m = data.get('rsi_1m', 0)
        rsi_15m = data.get('rsi_15m', 0)
        vol_ratio = data.get('volume_ratio', 0)
        score = data.get('score', 0)
        candle_change = data.get('candle_change_percent', 0)

        # Iconos y colores por crypto
        icons = {'BTC': '₿', 'ETH': 'Ξ', 'SOL': '◎'}
        colors = {'BTC': '#f7931a', 'ETH': '#627eea', 'SOL': '#9945ff'}
        icon = icons.get(name, '●')
        color = colors.get(name, '#64748b')

        # 8 criterios REALES del backend (trading_logic.py)

        c1 = "✓" if 30 <= rsi_1m <= 70 else "○"                             # RSI 1min favorable (30-70)
        c2 = "✓" if rsi_15m > 50 else "○"                                    # RSI 15min alcista (>50)
        c3 = "✓" if data.get('ema_fast', 0) > data.get('ema_slow', 0) else "○"  # EMA crossover
        c4 = "✓" if vol_ratio > 1.2 else "○"                                 # Volumen alto (>1.2x)
        c5 = "✓" if score >= 75 else "○"                                     # Confianza buena (>=75)
        c6 = "✓" if price > data.get('ema_fast', 0) else "○"                 # Precio sobre EMA
        c7 = "✓" if candle_change > 0.1 else "○"                            # Vela positiva (>0.1%)
        c8 = "✓" if vol_ratio > 1.0 else "○"                                # Actividad del mercado

        count = [c1,c2,c3,c4,c5,c6,c7,c8].count("✓")

        # PROGRESS BAR CON BONUS POR SCORE ALTO
        base_percentage = (count / 8) * 100  # Base: criterios cumplidos
        bonus_points = max(0, score - 75) if score >= 75 else 0  # Bonus si score ≥ 75
        progress_percentage = min(100, base_percentage + bonus_points)  # Máximo 100%

        # Señal clara basada en PROGRESS BAR FINAL
        if progress_percentage >= 75:      # 75%+ = FUERTE
            signal = "COMPRAR FUERTE"
            signal_class = "signal-strong"
            score_label = "EXCELENTE"
        elif progress_percentage >= 50:   # 50-74% = DÉBIL
            signal = "COMPRAR DÉBIL"
            signal_class = "signal-weak"
            score_label = "BUENA"
        elif progress_percentage >= 25:   # 25-49% = ESPERAR
            signal = "ESPERAR"
            signal_class = "signal-wait"
            score_label = "REGULAR"
        else:                              # 0-24% = NO COMPRAR
            signal = "NO COMPRAR"
            signal_class = "signal-no"
            score_label = "DÉBIL"

        # Datos de cambios de precio
        price_24h_change_percent = data.get('price_24h_change_percent', 0)
        price_24h_change_amount = data.get('price_24h_change_amount', 0)
        price_change_percent = data.get('price_change_percent', 0)
        price_change_amount = data.get('price_change_amount', 0)

        # Iconos y colores para cambios
        change_24h_icon = "📈" if price_24h_change_percent >= 0 else "📉"
        change_24h_color = "#22c55e" if price_24h_change_percent >= 0 else "#ef4444"
        change_now_icon = "🔼" if price_change_percent >= 0 else "🔽"
        change_now_color = "#22c55e" if price_change_percent >= 0 else "#ef4444"

        crypto_rows += f"""
        <tr class="crypto-row">
            <td class="crypto-cell">
                <span class="crypto-icon" style="color:{color}">{icon}</span>
                <span class="crypto-name" style="color:{color}">{name}</span>
            </td>
            <td class="price-cell">
                <div class="price-main">${price:,.2f}</div>
                <div class="price-change-24h" style="color:{change_24h_color}">
                    {change_24h_icon} {price_24h_change_percent:+.2f}% (${price_24h_change_amount:+,.2f}) 24h
                </div>
                <div class="price-change-now" style="color:{change_now_color}">
                    {change_now_icon} {price_change_percent:+.3f}% (${price_change_amount:+,.2f}) última act.
                </div>
            </td>
            <td class="criterion" title="RSI 1min: {rsi_1m:.1f} (30-70=✓)"><span class="signal-{c1.lower()}">{c1}</span></td>
            <td class="criterion" title="RSI 15min: {rsi_15m:.1f} (>50=✓)"><span class="signal-{c2.lower()}">{c2}</span></td>
            <td class="criterion" title="EMA: {data.get('ema_fast', 0):.1f} vs {data.get('ema_slow', 0):.1f}"><span class="signal-{c3.lower()}">{c3}</span></td>
            <td class="criterion" title="Volumen: {vol_ratio:.1f}x (>1.2x=✓)"><span class="signal-{c4.lower()}">{c4}</span></td>
            <td class="criterion" title="Score: {score}/100 (≥75=✓ +{bonus_points}pts bonus)"><span class="signal-{c5.lower()}">{c5}</span></td>
            <td class="criterion" title="Precio: ${price:,.2f} vs EMA {data.get('ema_fast', 0):.1f}"><span class="signal-{c6.lower()}">{c6}</span></td>
            <td class="criterion" title="Vela actual: {candle_change:.2f}% (>0.1%=✓)"><span class="signal-{c7.lower()}">{c7}</span></td>
            <td class="criterion" title="Actividad: Vol {vol_ratio:.1f}x (>1.0x=✓)"><span class="signal-{c8.lower()}">{c8}</span></td>
            <td class="signal-cell">
                <div class="trading-signal {signal_class}">{signal}</div>
                <div class="reliability-bar">
                    <div class="reliability-fill {signal_class}" style="width: {progress_percentage:.1f}%"></div>
                    <span class="reliability-text">{progress_percentage:.1f}% ({count}/8{'+' + str(bonus_points) + 'pts' if bonus_points > 0 else ''})</span>
                </div>
                <div class="reliability-label">{score_label}</div>
            </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head>
<title>🚀 Trading Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #0f172a; color: #f1f5f9; margin: 0; padding: 0;
}}
.dashboard-header {{
    background: linear-gradient(135deg, #1e293b, #334155);
    border-bottom: 2px solid #475569; margin-bottom: 20px; padding: 0;
}}
.header-top {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 15px 25px; flex-wrap: wrap;
}}
.header-left {{
    display: flex; align-items: center; gap: 15px;
}}
.dashboard-title {{
    margin: 0; font-size: 1.8rem; font-weight: 700;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.version-info {{
    background: rgba(34, 197, 94, 0.2); color: #22c55e;
    padding: 4px 12px; border-radius: 20px; font-size: 0.75rem;
    font-weight: 600; border: 1px solid rgba(34, 197, 94, 0.3);
}}
.header-right {{
    display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
}}
.refresh-indicator {{
    display: flex; align-items: center; gap: 8px;
    background: rgba(59, 130, 246, 0.1); padding: 8px 12px;
    border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.3);
    opacity: 0; transition: opacity 0.3s ease;
}}
.refresh-indicator.active {{ opacity: 1; }}
.refresh-dot {{
    width: 8px; height: 8px; background: #3b82f6;
    border-radius: 50%; animation: pulse 1.5s infinite;
}}
.refresh-text {{ font-size: 0.75rem; color: #3b82f6; font-weight: 500; }}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.5; transform: scale(1.2); }}
}}
.header-nav {{
    display: flex; gap: 15px;
}}
.nav-link {{
    color: #94a3b8; text-decoration: none; padding: 8px 16px;
    border-radius: 8px; font-weight: 500; font-size: 0.9rem;
    transition: all 0.3s ease; border: 1px solid transparent;
}}
.nav-link:hover {{
    background: rgba(148, 163, 184, 0.1); color: #f1f5f9;
    border-color: rgba(148, 163, 184, 0.3);
}}
.nav-link.active {{
    background: rgba(34, 197, 94, 0.2); color: #22c55e;
    border-color: rgba(34, 197, 94, 0.3);
}}
.academic-notice {{
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1));
    border: 1px solid rgba(245, 158, 11, 0.3); color: #fbbf24;
    padding: 12px 25px; font-size: 0.85rem; text-align: center;
    border-left: none; border-right: none;
}}
.dashboard-main {{
    padding: 0 25px 25px 25px; max-width: 1400px; margin: 0 auto;
}}
.trading-table {{
    width: 100%; background: #1e293b; border-radius: 12px;
    border-collapse: collapse; overflow: hidden;
}}
.trading-table th, .trading-table td {{
    padding: 12px 8px; text-align: center; border-bottom: 1px solid #334155;
}}
.trading-table th {{
    background: #334155; color: #f1f5f9; font-weight: 600;
}}
.buy-header {{
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: white !important; font-weight: 700;
}}
.crypto-cell {{ text-align: left !important; }}
.crypto-icon {{ font-size: 1.2rem; margin-right: 8px; }}
.crypto-name {{ font-weight: 600; }}
.price-cell {{ text-align: right !important; }}
.price-main {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; }}
.price-change-24h {{ font-size: 0.75rem; font-weight: 600; margin-bottom: 2px; }}
.price-change-now {{ font-size: 0.7rem; font-weight: 500; opacity: 0.9; }}
.signal-✓ {{ color: #22c55e; font-weight: 700; }}
.signal-○ {{ color: #64748b; }}
.score-value {{ font-weight: 600; }}
.score-label {{ font-size: 0.7rem; color: #94a3b8; }}
.score-count {{ font-size: 0.65rem; color: #64748b; margin-top: 2px; }}
.signal-explanation {{ font-size: 0.7rem; color: #94a3b8; margin-top: 2px; }}
.signal-strong {{ color: #22c55e; font-weight: 700; }}
.signal-weak {{ color: #f59e0b; font-weight: 600; }}
.signal-wait {{ color: #64748b; }}
.signal-no {{ color: #ef4444; }}
.reliability-bar {{
    position: relative; height: 16px; background: #334155;
    border-radius: 8px; margin: 6px 0; overflow: hidden;
}}
.reliability-fill {{
    height: 100%; border-radius: 8px; transition: width 0.3s ease;
}}
.reliability-fill.signal-strong {{ background: linear-gradient(90deg, #22c55e, #16a34a); }}
.reliability-fill.signal-weak {{ background: linear-gradient(90deg, #f59e0b, #d97706); }}
.reliability-fill.signal-wait {{ background: linear-gradient(90deg, #64748b, #475569); }}
.reliability-fill.signal-no {{ background: linear-gradient(90deg, #ef4444, #dc2626); }}
.reliability-text {{
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    font-size: 0.7rem; font-weight: 600; color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}}
.reliability-label {{ font-size: 0.7rem; color: #94a3b8; text-align: center; }}
.trading-table th[title]:hover::after,
.trading-table td[title]:hover::after {{
    content: attr(title); position: fixed; background: rgba(0,0,0,0.9);
    color: white; padding: 8px 12px; border-radius: 6px;
    font-size: 0.8rem; z-index: 9999; top: 50%; left: 50%;
    transform: translate(-50%, -50%); max-width: 300px;
}}
@media (max-width: 768px) {{
    .header-top {{ flex-direction: column; gap: 15px; text-align: center; }}
    .header-right {{ justify-content: center; }}
    .header-nav {{ flex-wrap: wrap; justify-content: center; }}
    .dashboard-main {{ padding: 0 15px 15px 15px; }}
    .trading-table {{ font-size: 0.8rem; }}
    .trading-table th, .trading-table td {{ padding: 8px 4px; }}
    .academic-notice {{ font-size: 0.8rem; padding: 10px 15px; }}
    .dashboard-title {{ font-size: 1.5rem; }}
}}
</style>
</head><body>
<header class="dashboard-header">
    <div class="header-top">
        <div class="header-left">
            <h1 class="dashboard-title">🚀 Trading Dashboard</h1>
            <div class="version-info">v5.0-MODULAR</div>
        </div>
        <div class="header-right">
            <div class="refresh-indicator" id="refreshIndicator">
                <span class="refresh-dot"></span>
                <span class="refresh-text">Actualizando...</span>
            </div>
            <nav class="header-nav">
                <a href="/" class="nav-link active">📊 Dashboard</a>
                <a href="/logs" class="nav-link">📡 Logs</a>
                <a href="/instructions" class="nav-link">📚 Instrucciones</a>
            </nav>
        </div>
    </div>
    <div class="academic-notice">
        ⚠️ <strong>AVISO ACADÉMICO:</strong> Este sistema es únicamente para fines educativos y de investigación.
        No constituye asesoramiento financiero. Opere bajo su propia responsabilidad.
    </div>
</header>
<main class="dashboard-main">
<table class="trading-table">
<thead>
<tr>
    <th>CRYPTO</th><th>PRECIO</th>
    <th colspan="8" class="buy-header">🟢 CRITERIOS DE COMPRA (8)</th>
    <th>SEÑAL</th>
</tr>
<tr>
    <th></th><th></th>
    <th title="RSI 1min entre 30-70 (zona favorable)">RSI1</th><th title="RSI 15min mayor a 50 (tendencia alcista)">RSI15</th>
    <th title="EMA rápida por encima de EMA lenta (tendencia)">EMA</th><th title="Volumen mayor a 1.2x del promedio (interés)">VOL</th>
    <th title="Score confianza ≥ 75 (da bonus al progress bar)">CONF</th><th title="Precio por encima de EMA rápida (posición)">PRICE</th>
    <th title="Vela actual positiva mayor a 0.1% (momentum)">VELA</th><th title="Volumen mayor a promedio (actividad)">ACT</th>
    <th></th>
</tr>
</thead>
<tbody>
{crypto_rows}
</tbody>
</table>
</main>
<script>
// Indicador de refresh
const refreshIndicator = document.getElementById('refreshIndicator');

function showRefreshIndicator() {{
    refreshIndicator.classList.add('active');
}}

function hideRefreshIndicator() {{
    refreshIndicator.classList.remove('active');
}}

// Auto-refresh con indicador
setInterval(() => {{
    showRefreshIndicator();
    fetch('/api/data')
        .then(r => r.json())
        .then(data => {{
            if(data.market_data) {{
                setTimeout(() => {{
                    location.reload();
                }}, 1000); // Mostrar indicador por 1 segundo
            }} else {{
                hideRefreshIndicator();
            }}
        }})
        .catch(() => {{
            hideRefreshIndicator();
        }});
}}, 30000);

// Mostrar indicador al cargar la página
window.addEventListener('load', () => {{
    showRefreshIndicator();
    setTimeout(hideRefreshIndicator, 2000);
}});
</script>
</body></html>"""