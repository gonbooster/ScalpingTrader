# instructions_dashboard.py - Dashboard educativo para principiantes
from version_info import get_version_badge

def generate_instructions_dashboard():
    """Genera el dashboard de instrucciones educativas"""
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📚 Guía de Trading - ScalpingTrader</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #e2e8f0;
                line-height: 1.6;
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}

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
            .nav-link.active {{ background: rgba(34, 197, 94, 0.2); color: #22c55e; border-color: rgba(34, 197, 94, 0.3); }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding: 30px;
                background: rgba(15, 23, 42, 0.8);
                border-radius: 20px;
                border: 1px solid #334155;
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #3b82f6, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .header p {{
                font-size: 1.2rem;
                color: #94a3b8;
                margin-bottom: 20px;
            }}
            
            .warning {{
                background: linear-gradient(45deg, #dc2626, #ef4444);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                font-weight: 600;
                margin-bottom: 20px;
            }}
            
            .nav-buttons {{
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }}
            
            .nav-btn {{
                padding: 12px 24px;
                background: rgba(59, 130, 246, 0.2);
                border: 1px solid #3b82f6;
                border-radius: 10px;
                color: #3b82f6;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            
            .nav-btn:hover {{
                background: #3b82f6;
                color: white;
                transform: translateY(-2px);
            }}
            
            .section {{
                background: rgba(15, 23, 42, 0.6);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                border: 1px solid #334155;
            }}
            
            .section h2 {{
                font-size: 1.8rem;
                margin-bottom: 20px;
                color: #3b82f6;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .section h3 {{
                font-size: 1.4rem;
                margin: 25px 0 15px 0;
                color: #8b5cf6;
                border-left: 4px solid #8b5cf6;
                padding-left: 15px;
            }}
            
            .indicator-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            
            .indicator-card {{
                background: rgba(30, 41, 59, 0.8);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #475569;
                transition: transform 0.3s ease;
            }}
            
            .indicator-card:hover {{
                transform: translateY(-5px);
                border-color: #3b82f6;
            }}
            
            .indicator-title {{
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 10px;
                color: #22c55e;
            }}
            
            .indicator-description {{
                color: #cbd5e1;
                margin-bottom: 15px;
            }}
            
            .indicator-example {{
                background: rgba(0, 0, 0, 0.3);
                padding: 10px;
                border-radius: 8px;
                border-left: 4px solid #22c55e;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
            }}
            
            .criteria-explanation {{
                background: linear-gradient(45deg, rgba(34, 197, 94, 0.1), rgba(59, 130, 246, 0.1));
                border-radius: 12px;
                padding: 25px;
                margin: 20px 0;
                border: 1px solid #22c55e;
            }}
            
            .criteria-list {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            
            .criteria-item {{
                background: rgba(30, 41, 59, 0.6);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #3b82f6;
            }}
            
            .criteria-item strong {{
                color: #3b82f6;
                display: block;
                margin-bottom: 5px;
            }}
            
            .score-explanation {{
                background: linear-gradient(45deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1));
                border-radius: 12px;
                padding: 25px;
                margin: 20px 0;
                border: 1px solid #8b5cf6;
            }}
            
            .score-ranges {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            
            .score-range {{
                text-align: center;
                padding: 20px;
                border-radius: 12px;
                font-weight: 600;
            }}
            
            .score-excellent {{ background: linear-gradient(45deg, #22c55e, #16a34a); }}
            .score-good {{ background: linear-gradient(45deg, #3b82f6, #2563eb); }}
            .score-medium {{ background: linear-gradient(45deg, #f59e0b, #d97706); }}
            .score-poor {{ background: linear-gradient(45deg, #ef4444, #dc2626); }}
            
            .trading-flow {{
                background: rgba(30, 41, 59, 0.8);
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
            }}
            
            .flow-step {{
                display: flex;
                align-items: center;
                margin: 15px 0;
                padding: 15px;
                background: rgba(59, 130, 246, 0.1);
                border-radius: 10px;
                border-left: 4px solid #3b82f6;
            }}
            
            .flow-number {{
                background: #3b82f6;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                margin-right: 15px;
                flex-shrink: 0;
            }}
            
            .back-btn {{
                position: fixed;
                top: 20px;
                left: 20px;
                background: rgba(59, 130, 246, 0.2);
                border: 1px solid #3b82f6;
                border-radius: 10px;
                padding: 10px 20px;
                color: #3b82f6;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                z-index: 1000;
            }}
            
            .back-btn:hover {{
                background: #3b82f6;
                color: white;
            }}
            
            /* Responsive Design */
            @media (max-width: 768px) {{
                .container {{ padding: 10px; }}
                .header h1 {{ font-size: 2rem; }}
                .header p {{ font-size: 1rem; }}
                .section {{ padding: 20px; }}
                .indicator-grid {{ grid-template-columns: 1fr; }}
                .criteria-list {{ grid-template-columns: 1fr; }}
                .score-ranges {{ grid-template-columns: 1fr; }}
                .nav-buttons {{ flex-direction: column; align-items: center; }}
                .flow-step {{ flex-direction: column; text-align: center; }}
                .flow-number {{ margin-bottom: 10px; margin-right: 0; }}
            }}
            
            @media (max-width: 480px) {{
                .header {{ padding: 20px; }}
                .section {{ padding: 15px; }}
                .indicator-card {{ padding: 15px; }}
                .back-btn {{ position: relative; top: auto; left: auto; margin-bottom: 20px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <nav class="header-nav">
                <a href="/" class="nav-link">📊 Dashboard</a>
                <a href="/analytics" class="nav-link">📈 Análisis</a>
                <a href="/instructions" class="nav-link active">📚 Instrucciones</a>
            </nav>

            <div class="header">
                <h1>📚 Guía Completa de Trading</h1>
                <p>Aprende a interpretar todos los indicadores y señales del ScalpingTrader</p>
                
                <div class="warning">
                    ⚠️ SOLO PARA FINES EDUCATIVOS - NO ES CONSEJO FINANCIERO
                </div>
                
                <div class="nav-buttons">
                    <a href="#indicadores" class="nav-btn">📊 Indicadores</a>
                    <a href="#criterios" class="nav-btn">✅ 8 Criterios</a>
                    <a href="#score" class="nav-btn">🎯 Sistema de Score</a>
                    <a href="#targets" class="nav-btn">💰 TP/SL</a>
                    <a href="#flujo" class="nav-btn">🔄 Flujo de Trading</a>
                </div>
            </div>

            <!-- SECCIÓN 1: INDICADORES TÉCNICOS -->
            <div id="indicadores" class="section">
                <h2>📊 Indicadores Técnicos Explicados</h2>

                <h3>🔴 RSI (Relative Strength Index)</h3>
                <p>El RSI mide si una criptomoneda está "sobrecomprada" o "sobrevendida". Es como un termómetro del mercado.</p>

                <div class="indicator-grid">
                    <div class="indicator-card">
                        <div class="indicator-title">📈 RSI 1 minuto</div>
                        <div class="indicator-description">
                            <strong>¿Qué es?</strong> Mide la fuerza del precio en el último minuto.<br>
                            <strong>¿Para qué?</strong> Detectar cambios inmediatos de tendencia.<br>
                            <strong>Interpretación:</strong>
                        </div>
                        <div class="indicator-example">
                            • RSI > 70: 🔴 Sobrecomprado (puede bajar)
                            • RSI < 30: 🟢 Sobrevendido (puede subir)
                            • RSI 30-70: 🟡 Neutral
                        </div>
                    </div>

                    <div class="indicator-card">
                        <div class="indicator-title">📊 RSI 5 minutos</div>
                        <div class="indicator-description">
                            <strong>¿Qué es?</strong> Mide la fuerza del precio en los últimos 5 minutos.<br>
                            <strong>¿Para qué?</strong> Confirmar la tendencia a corto plazo.<br>
                            <strong>Interpretación:</strong>
                        </div>
                        <div class="indicator-example">
                            • Más confiable que RSI 1m
                            • Filtra ruido del mercado
                            • Mejor para confirmar señales
                        </div>
                    </div>

                    <div class="indicator-card">
                        <div class="indicator-title">📉 RSI 15 minutos</div>
                        <div class="indicator-description">
                            <strong>¿Qué es?</strong> Mide la fuerza del precio en los últimos 15 minutos.<br>
                            <strong>¿Para qué?</strong> Ver la tendencia general más estable.<br>
                            <strong>Interpretación:</strong>
                        </div>
                        <div class="indicator-example">
                            • Más estable y confiable
                            • Menos señales falsas
                            • Ideal para confirmar dirección
                        </div>
                    </div>

                    <div class="indicator-card">
                        <div class="indicator-title">⚡ Momentum</div>
                        <div class="indicator-description">
                            <strong>¿Qué es?</strong> Mide la velocidad del cambio de precio.<br>
                            <strong>¿Para qué?</strong> Detectar si el precio acelera o desacelera.<br>
                            <strong>Interpretación:</strong>
                        </div>
                        <div class="indicator-example">
                            • Momentum > 0: 🟢 Precio subiendo rápido
                            • Momentum < 0: 🔴 Precio bajando rápido
                            • Momentum ≈ 0: 🟡 Precio estable
                        </div>
                    </div>

                    <div class="indicator-card">
                        <div class="indicator-title">📊 Volumen</div>
                        <div class="indicator-description">
                            <strong>¿Qué es?</strong> Cantidad de dinero que se está moviendo.<br>
                            <strong>¿Para qué?</strong> Confirmar si una señal es fuerte.<br>
                            <strong>Interpretación:</strong>
                        </div>
                        <div class="indicator-example">
                            • Volumen alto + señal = 🟢 Muy confiable
                            • Volumen bajo + señal = 🟡 Menos confiable
                            • Ratio > 1.5 = 🔥 Alta actividad
                        </div>
                    </div>

                    <div class="indicator-card">
                        <div class="indicator-title">🎯 Score de Confianza</div>
                        <div class="indicator-description">
                            <strong>¿Qué es?</strong> Calificación de 0-100 que evalúa 8 condiciones.<br>
                            <strong>¿Para qué?</strong> Saber qué tan buena es una oportunidad.<br>
                            <strong>Interpretación:</strong>
                        </div>
                        <div class="indicator-example">
                            • 90-100: 🔥 EXCELENTE (muy probable)
                            • 75-89: 🟢 FUERTE (buena probabilidad)
                            • 60-74: 🟡 BUENA (probabilidad media)
                            • <60: 🔴 DÉBIL (baja probabilidad)
                        </div>
                    </div>
                </div>
            </div>

            <!-- SECCIÓN 2: LOS 8 CRITERIOS -->
            <div id="criterios" class="section">
                <h2>✅ Los 8 Criterios de Trading Explicados</h2>

                <div class="criteria-explanation">
                    <h3>🤔 ¿Cómo funciona el sistema?</h3>
                    <p>El sistema evalúa estos 8 criterios técnicos específicos en tiempo real.
                    <strong>Cada criterio cumplido aumenta la probabilidad de éxito de la operación.</strong></p>

                    <p><strong>📊 Progress Bar:</strong> Muestra (criterios cumplidos / 8) × 100 + bonus por score alto (≥75)</p>
                    <p><strong>🎯 Señales:</strong> Solo se envían emails para señales BUY con alta probabilidad</p>
                </div>

                <h3>📋 Los 8 Criterios Reales del Sistema:</h3>

                <div class="criteria-list">
                    <div class="criteria-item">
                        <strong>1. 🔴 RSI1 - RSI 1 minuto</strong>
                        RSI entre 30-70 (zona favorable para trading)
                        <br><em>Evita zonas extremas de sobrecompra (>70) o sobreventa (<30)</em>
                    </div>

                    <div class="criteria-item">
                        <strong>2. 📊 RSI15 - RSI 15 minutos</strong>
                        RSI > 50 (tendencia alcista confirmada)
                        <br><em>Timeframe más estable que confirma la dirección general</em>
                    </div>

                    <div class="criteria-item">
                        <strong>3. 📈 EMA - Cruce de Medias</strong>
                        EMA rápida (10) > EMA lenta (21) - Tendencia alcista
                        <br><em>Las medias móviles confirman la dirección del mercado</em>
                    </div>

                    <div class="criteria-item">
                        <strong>4. 📦 VOL - Volumen Elevado</strong>
                        Volumen > 1.2x promedio (interés del mercado)
                        <br><em>Más volumen = mayor confianza en la señal</em>
                    </div>

                    <div class="criteria-item">
                        <strong>5. 🎯 CONF - Score de Confianza</strong>
                        Score ≥ 75/100 (calidad algorítmica alta)
                        <br><em>Algoritmo sofisticado que combina múltiples indicadores</em>
                    </div>

                    <div class="criteria-item">
                        <strong>6. 💰 PRICE - Posición del Precio</strong>
                        Precio > EMA rápida (posición alcista)
                        <br><em>El precio debe estar por encima de la media móvil rápida</em>
                    </div>

                    <div class="criteria-item">
                        <strong>7. 🕯️ VELA - Momentum de Vela</strong>
                        Vela positiva > 0.1% (momentum alcista)
                        <br><em>La vela actual debe mostrar fuerza compradora</em>
                    </div>

                    <div class="criteria-item">
                        <strong>8. ⚡ ACT - Actividad del Mercado</strong>
                        Volumen > promedio (actividad suficiente)
                        <br><em>Confirma que hay suficiente actividad para operar</em>
                    </div>
                </div>

                <div class="criteria-explanation">
                    <h3>🎯 ¿Cuándo aparecen las señales?</h3>
                    <div class="score-ranges">
                        <div class="score-range score-excellent">
                            <div>🔥 Progress ≥ 75%</div>
                            <div>COMPRAR FUERTE</div>
                            <div>Alta probabilidad + Email</div>
                        </div>
                        <div class="score-range score-good">
                            <div>✅ Progress 50-74%</div>
                            <div>COMPRAR DÉBIL</div>
                            <div>Probabilidad media + Email</div>
                        </div>
                        <div class="score-range score-medium">
                            <div>⚠️ Progress 25-49%</div>
                            <div>ESPERAR</div>
                            <div>Sin email - Solo observar</div>
                        </div>
                        <div class="score-range score-poor">
                            <div>❌ Progress < 25%</div>
                            <div>NO COMPRAR</div>
                            <div>Condiciones desfavorables</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SECCIÓN 3: SISTEMA DE SCORE -->
            <div id="score" class="section">
                <h2>🎯 Sistema de Score Explicado</h2>

                <div class="score-explanation">
                    <h3>🤖 ¿Cómo funciona el Score?</h3>
                    <p>El score es como una <strong>calificación de examen</strong> que evalúa qué tan buena es una oportunidad de trading.
                    Va de 0 a 100 puntos y se calcula analizando múltiples factores técnicos.</p>

                    <h3>📊 ¿Qué evalúa el Score?</h3>
                    <ul style="margin: 15px 0; padding-left: 20px;">
                        <li>🔴 <strong>RSI en múltiples timeframes</strong> (1m, 5m, 15m)</li>
                        <li>📈 <strong>Tendencia del precio</strong> (EMA rápida vs lenta)</li>
                        <li>⚡ <strong>Momentum</strong> (velocidad del cambio)</li>
                        <li>📊 <strong>Volumen de trading</strong> (actividad del mercado)</li>
                        <li>🕐 <strong>Volatilidad</strong> (qué tan activo está el mercado)</li>
                        <li>⏰ <strong>Timing</strong> (horario óptimo para operar)</li>
                    </ul>
                </div>

                <h3>🎨 Interpretación Visual del Score:</h3>
                <div class="score-ranges">
                    <div class="score-range score-excellent">
                        <div style="font-size: 2rem;">🔥</div>
                        <div><strong>90-100 puntos</strong></div>
                        <div>EXCELENTE</div>
                        <div style="font-size: 0.9rem;">Probabilidad muy alta de éxito</div>
                    </div>
                    <div class="score-range score-good">
                        <div style="font-size: 2rem;">✅</div>
                        <div><strong>75-89 puntos</strong></div>
                        <div>FUERTE</div>
                        <div style="font-size: 0.9rem;">Buena probabilidad de éxito</div>
                    </div>
                    <div class="score-range score-medium">
                        <div style="font-size: 2rem;">⚠️</div>
                        <div><strong>60-74 puntos</strong></div>
                        <div>BUENA</div>
                        <div style="font-size: 0.9rem;">Probabilidad media</div>
                    </div>
                    <div class="score-range score-poor">
                        <div style="font-size: 2rem;">❌</div>
                        <div><strong>0-59 puntos</strong></div>
                        <div>DÉBIL</div>
                        <div style="font-size: 0.9rem;">Baja probabilidad - NO operar</div>
                    </div>
                </div>
            </div>

            <!-- SECCIÓN 4: TP/SL -->
            <div id="targets" class="section">
                <h2>💰 Take Profit (TP) y Stop Loss (SL) Explicados</h2>

                <div class="indicator-grid">
                    <div class="indicator-card">
                        <div class="indicator-title">🎯 Take Profit (TP)</div>
                        <div class="indicator-description">
                            <strong>¿Qué es?</strong> El precio al que deberías vender para obtener ganancias.<br>
                            <strong>¿Para qué?</strong> Asegurar que tomes ganancias cuando el precio suba.<br>
                            <strong>Ejemplo:</strong>
                        </div>
                        <div class="indicator-example">
                            Si compras BTC a $100,000
                            TP podría ser $101,500 (+1.5%)
                            = Ganancia de $1,500 por Bitcoin
                        </div>
                    </div>

                    <div class="indicator-card">
                        <div class="indicator-title">🛡️ Stop Loss (SL)</div>
                        <div class="indicator-description">
                            <strong>¿Qué es?</strong> El precio al que deberías vender para limitar pérdidas.<br>
                            <strong>¿Para qué?</strong> Protegerte si el precio va en contra tuya.<br>
                            <strong>Ejemplo:</strong>
                        </div>
                        <div class="indicator-example">
                            Si compras BTC a $100,000
                            SL podría ser $99,200 (-0.8%)
                            = Pérdida máxima de $800 por Bitcoin
                        </div>
                    </div>
                </div>

                <div class="criteria-explanation">
                    <h3>🧮 ¿Cómo se calculan?</h3>
                    <p>El sistema usa el <strong>ATR (Average True Range)</strong> que mide la volatilidad típica del mercado:</p>
                    <ul style="margin: 15px 0; padding-left: 20px;">
                        <li>📈 <strong>TP:</strong> Precio actual + (ATR × 2) = Objetivo de ganancia</li>
                        <li>📉 <strong>SL:</strong> Precio actual - (ATR × 1) = Límite de pérdida</li>
                        <li>⚖️ <strong>Risk/Reward:</strong> Normalmente 1:2 (arriesgas $1 para ganar $2)</li>
                    </ul>
                </div>
            </div>

            <!-- SECCIÓN 5: FLUJO DE TRADING -->
            <div id="flujo" class="section">
                <h2>🔄 Flujo Completo de Trading</h2>

                <div class="trading-flow">
                    <h3>📋 Paso a Paso: ¿Cómo usar el sistema?</h3>

                    <div class="flow-step">
                        <div class="flow-number">1</div>
                        <div>
                            <strong>📊 Revisar el Dashboard</strong><br>
                            Mira los indicadores de BTC, ETH y SOL. Busca scores altos (75+) y muchos criterios cumplidos (6+/8).
                        </div>
                    </div>

                    <div class="flow-step">
                        <div class="flow-number">2</div>
                        <div>
                            <strong>✅ Verificar Criterios</strong><br>
                            Asegúrate de que se cumplan mínimo 6 de 8 criterios. Más criterios = mayor probabilidad de éxito.
                        </div>
                    </div>

                    <div class="flow-step">
                        <div class="flow-number">3</div>
                        <div>
                            <strong>🎯 Revisar Score</strong><br>
                            Solo considera señales con score 75+ (FUERTE) o 90+ (EXCELENTE). Evita scores bajos.
                        </div>
                    </div>

                    <div class="flow-step">
                        <div class="flow-number">4</div>
                        <div>
                            <strong>📧 Esperar Email</strong><br>
                            El sistema solo envía emails para las mejores oportunidades (75+ score y 6+ criterios).
                        </div>
                    </div>

                    <div class="flow-step">
                        <div class="flow-number">5</div>
                        <div>
                            <strong>💰 Planificar TP/SL</strong><br>
                            Antes de operar, define tu Take Profit (ganancia objetivo) y Stop Loss (pérdida máxima).
                        </div>
                    </div>

                    <div class="flow-step">
                        <div class="flow-number">6</div>
                        <div>
                            <strong>⏰ Timing Correcto</strong><br>
                            Opera durante horarios de alta liquidez. Evita fines de semana y horarios de baja actividad.
                        </div>
                    </div>

                    <div class="flow-step">
                        <div class="flow-number">7</div>
                        <div>
                            <strong>📈 Monitorear</strong><br>
                            Sigue la evolución de tu operación. Respeta tu TP y SL predefinidos.
                        </div>
                    </div>

                    <div class="flow-step">
                        <div class="flow-number">8</div>
                        <div>
                            <strong>📊 Analizar Resultados</strong><br>
                            Revisa el dashboard de Analytics para ver el rendimiento histórico y aprender.
                        </div>
                    </div>
                </div>

                <div class="criteria-explanation">
                    <h3>⚠️ Reglas de Oro del Trading</h3>
                    <ul style="margin: 15px 0; padding-left: 20px; line-height: 1.8;">
                        <li>🚫 <strong>NUNCA operes con dinero que no puedes permitirte perder</strong></li>
                        <li>📊 <strong>Solo opera cuando se cumplan 6+ criterios</strong></li>
                        <li>🎯 <strong>Siempre define TP y SL antes de operar</strong></li>
                        <li>⏰ <strong>Respeta los horarios de alta liquidez</strong></li>
                        <li>📈 <strong>Empieza con cantidades pequeñas para aprender</strong></li>
                        <li>🧠 <strong>Controla tus emociones - sigue el sistema</strong></li>
                        <li>📚 <strong>Esto es EDUCATIVO - no consejo financiero</strong></li>
                    </ul>
                </div>
            </div>

            <div class="section">
                <h2>🎓 Resumen Final</h2>
                <p style="font-size: 1.1rem; text-align: center; margin: 20px 0;">
                    El <strong>ScalpingTrader</strong> es una herramienta educativa que analiza múltiples indicadores técnicos
                    para identificar oportunidades de trading. Usa esta información para <strong>aprender</strong> sobre
                    análisis técnico, pero recuerda que <strong>ningún sistema es 100% preciso</strong>.
                </p>


            </div>
        </div>

        <!-- Badge de versión automático -->
        {get_version_badge()}
    </body>
    </html>
    """
