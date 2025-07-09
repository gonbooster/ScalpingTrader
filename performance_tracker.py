# performance_tracker.py - Sistema de análisis de rendimiento de señales
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import time

logger = logging.getLogger(__name__)

class PerformanceTracker:
    def __init__(self, db_path="trading_performance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de señales enviadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                entry_price REAL NOT NULL,
                score INTEGER NOT NULL,
                conditions_met INTEGER NOT NULL,
                total_conditions INTEGER NOT NULL,
                rsi_1m REAL,
                rsi_15m REAL,
                ema_fast REAL,
                ema_slow REAL,
                volume_ratio REAL,
                atr REAL,
                candle_change REAL,
                tp_price REAL,
                sl_price REAL,
                expected_move REAL,
                risk_reward REAL,
                market_conditions TEXT,
                status TEXT DEFAULT 'PENDING',
                result TEXT,
                exit_price REAL,
                exit_timestamp TEXT,
                actual_return REAL,
                time_to_resolution INTEGER,
                notes TEXT
            )
        ''')
        
        # Tabla de análisis de mercado (para correlaciones)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                rsi_1m REAL,
                rsi_15m REAL,
                score INTEGER,
                volume_ratio REAL,
                trend_direction TEXT,
                volatility REAL,
                conditions_met INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("📊 Base de datos de rendimiento inicializada")
    
    def record_signal(self, signal_data: Dict):
        """Registra una nueva señal enviada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (
                timestamp, symbol, signal_type, entry_price, score,
                conditions_met, total_conditions, rsi_1m, rsi_15m,
                ema_fast, ema_slow, volume_ratio, atr, candle_change,
                tp_price, sl_price, expected_move, risk_reward, market_conditions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal_data['timestamp'],
            signal_data['symbol'],
            signal_data['signal_type'],
            signal_data['entry_price'],
            signal_data['score'],
            signal_data['conditions_met'],
            signal_data['total_conditions'],
            signal_data.get('rsi_1m'),
            signal_data.get('rsi_15m'),
            signal_data.get('ema_fast'),
            signal_data.get('ema_slow'),
            signal_data.get('volume_ratio'),
            signal_data.get('atr'),
            signal_data.get('candle_change'),
            signal_data.get('tp_price'),
            signal_data.get('sl_price'),
            signal_data.get('expected_move'),
            signal_data.get('risk_reward'),
            json.dumps(signal_data.get('market_conditions', {}))
        ))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"📊 Señal registrada: {signal_data['symbol']} {signal_data['signal_type']} (ID: {signal_id})")
        return signal_id
    
    def record_market_data(self, market_data: Dict):
        """Registra datos de mercado para análisis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for symbol, data in market_data.items():
            cursor.execute('''
                INSERT INTO market_analysis (
                    timestamp, symbol, price, rsi_1m, rsi_15m, score,
                    volume_ratio, trend_direction, volatility, conditions_met
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                symbol,
                data.get('price'),
                data.get('rsi_1m'),
                data.get('rsi_15m'),
                data.get('score'),
                data.get('volume', 0) / data.get('vol_avg', 1) if data.get('vol_avg') else 0,
                'bullish' if data.get('ema_fast', 0) > data.get('ema_slow', 0) else 'bearish',
                data.get('atr', 0) / data.get('price', 1) * 100 if data.get('price') else 0,
                0  # Se actualizará con las condiciones reales
            ))
        
        conn.commit()
        conn.close()
    
    def check_signal_outcomes(self):
        """Verifica el resultado de señales pendientes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Obtener TODAS las señales pendientes (sin límite de tiempo para verificación más agresiva)
        cursor.execute('''
            SELECT * FROM signals
            WHERE result IS NULL OR result = 'None' OR result = ''
            ORDER BY timestamp DESC
        ''')

        pending_signals = cursor.fetchall()
        updated_count = 0

        for signal in pending_signals:
            signal_id = signal[0]
            symbol = signal[2]
            signal_type = signal[3]
            entry_price = signal[4]
            tp_price = signal[15]
            sl_price = signal[16]
            entry_time = datetime.fromisoformat(signal[1])

            # Verificar tiempo transcurrido
            hours_elapsed = (datetime.now() - entry_time).total_seconds() / 3600
            minutes_elapsed = int(hours_elapsed * 60)

            # Obtener precio actual
            current_price = self.get_current_price(symbol)
            if not current_price:
                continue

            # Lógica de evaluación más agresiva y realista
            result = None
            actual_return = self.calculate_return(signal_type, entry_price, current_price)

            # Verificar TP/SL primero
            tp_sl_result = self.check_tp_sl_hit(signal_type, entry_price, current_price, tp_price, sl_price)

            if tp_sl_result:
                result = tp_sl_result
            elif hours_elapsed >= 1:  # Evaluar después de 1 hora (optimizado)
                # Lógica basada en movimiento de precio - MÁS AGRESIVA
                if signal_type.upper() == 'BUY':
                    if actual_return >= 1.2:  # +1.2% = WIN (reducido de 1.5%)
                        result = 'WIN_TIME'
                    elif actual_return <= -0.8:  # -0.8% = LOSS (reducido de -1%)
                        result = 'LOSS_TIME'
                    elif hours_elapsed >= 3:  # 3 horas = EXPIRED (reducido de 8h)
                        result = 'EXPIRED'
                elif signal_type.upper() == 'SELL':
                    if actual_return >= 1.2:  # Precio bajó 1.2% = WIN (reducido de 1.5%)
                        result = 'WIN_TIME'
                    elif actual_return <= -0.8:  # Precio subió 0.8% = LOSS (reducido de -1%)
                        result = 'LOSS_TIME'
                    elif hours_elapsed >= 3:  # 3 horas = EXPIRED (reducido de 8h)
                        result = 'EXPIRED'

            # Si hay resultado, actualizar
            if result:
                cursor.execute('''
                    UPDATE signals SET
                    result = ?,
                    exit_price = ?,
                    exit_timestamp = ?,
                    actual_return = ?,
                    time_to_resolution = ?,
                    notes = ?
                    WHERE id = ?
                ''', (
                    result, current_price, datetime.now().isoformat(),
                    actual_return, minutes_elapsed,
                    f'Evaluado por {"TP/SL" if tp_sl_result else "tiempo"} después de {hours_elapsed:.1f}h',
                    signal_id
                ))
                updated_count += 1
                win_emoji = "🎯" if "WIN" in result else "❌" if "LOSS" in result else "⏰"
                logger.info(f"📊 {win_emoji} {symbol} {signal_type}: {result} ({actual_return:+.2f}%) en {hours_elapsed:.1f}h")
                continue



        conn.commit()
        conn.close()

        if updated_count > 0:
            logger.info(f"📊 Actualizadas {updated_count} señales")

        return updated_count

    def force_evaluate_all_pending(self):
        """Fuerza la evaluación de TODAS las señales pendientes inmediatamente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Obtener todas las señales pendientes (incluyendo result NULL)
            cursor.execute('''
                SELECT * FROM signals
                WHERE result IS NULL OR result = 'None' OR result = ''
                ORDER BY timestamp ASC
            ''')
            pending_signals = cursor.fetchall()

            logger.info(f"🔍 Evaluando {len(pending_signals)} señales pendientes...")

            updated_count = 0
            for signal in pending_signals:
                signal_id = signal[0]
                symbol = signal[2]
                signal_type = signal[3]
                entry_price = signal[4]
                entry_time = datetime.fromisoformat(signal[1])

                # Obtener precio actual
                current_price = self.get_current_price(symbol)
                if not current_price:
                    continue

                # Calcular tiempo transcurrido
                hours_elapsed = (datetime.now() - entry_time).total_seconds() / 3600
                minutes_elapsed = int(hours_elapsed * 60)

                # Calcular retorno actual
                actual_return = self.calculate_return(signal_type, entry_price, current_price)

                # Determinar resultado basado en tiempo y movimiento de precio
                result = None

                # Si han pasado más de 2 horas, marcar como EXPIRED automáticamente - OPTIMIZADO
                if hours_elapsed >= 2:
                    result = 'EXPIRED'
                    logger.info(f"📊 ⏰ {symbol} {signal_type}: EXPIRED (2+ horas)")
                elif signal_type.upper() == 'BUY':
                    if actual_return >= 1.2:  # +1.2% = WIN claro (reducido de 1.5%)
                        result = 'WIN_TIME'
                    elif actual_return <= -0.8:  # -0.8% = LOSS claro (reducido de -1%)
                        result = 'LOSS_TIME'
                    elif hours_elapsed >= 1:  # Evaluar después de 1 hora con criterios más flexibles
                        if actual_return >= 0.4:  # +0.4% = WIN después de 1h (más flexible)
                            result = 'WIN_TIME'
                        elif actual_return <= -0.3:  # -0.3% = LOSS después de 1h (más flexible)
                            result = 'LOSS_TIME'
                        elif hours_elapsed >= 2:  # Solo EXPIRED después de 2 horas
                            if actual_return >= 0.2:  # Movimiento mínimo positivo = WIN
                                result = 'WIN_TIME'
                            elif actual_return <= -0.2:  # Movimiento mínimo negativo = LOSS
                                result = 'LOSS_TIME'
                            else:
                                result = 'EXPIRED'  # Verdaderamente neutral = EXPIRED
                    else:
                        # Menos de 1 hora, mantener PENDING solo si no hay movimiento claro
                        if actual_return >= 1.2 or actual_return <= -0.8:
                            result = 'WIN_TIME' if actual_return >= 1.2 else 'LOSS_TIME'
                        # Si no hay movimiento claro, mantener como PENDING
                elif signal_type.upper() == 'SELL':
                    if actual_return >= 1.2:  # Precio bajó 1.2% = WIN claro (reducido de 1.5%)
                        result = 'WIN_TIME'
                    elif actual_return <= -0.8:  # Precio subió 0.8% = LOSS claro (reducido de -1%)
                        result = 'LOSS_TIME'
                    elif hours_elapsed >= 1:  # Evaluar después de 1 hora con criterios más flexibles
                        if actual_return >= 0.4:  # Precio bajó 0.4% = WIN después de 1h (más flexible)
                            result = 'WIN_TIME'
                        elif actual_return <= -0.3:  # Precio subió 0.3% = LOSS después de 1h (más flexible)
                            result = 'LOSS_TIME'
                        elif hours_elapsed >= 2:  # Solo EXPIRED después de 2 horas
                            if actual_return >= 0.2:  # Movimiento mínimo positivo = WIN
                                result = 'WIN_TIME'
                            elif actual_return <= -0.2:  # Movimiento mínimo negativo = LOSS
                                result = 'LOSS_TIME'
                            else:
                                result = 'EXPIRED'  # Verdaderamente neutral = EXPIRED
                    else:
                        # Menos de 1 hora, mantener PENDING solo si no hay movimiento claro
                        if actual_return >= 1.2 or actual_return <= -0.8:
                            result = 'WIN_TIME' if actual_return >= 1.2 else 'LOSS_TIME'
                        # Si no hay movimiento claro, mantener como PENDING

                # Actualizar señal solo si hay un resultado definido
                if result:
                    cursor.execute('''
                        UPDATE signals SET
                        result = ?,
                        exit_price = ?,
                        exit_timestamp = ?,
                        actual_return = ?,
                        time_to_resolution = ?,
                        notes = 'Evaluación forzada para análisis'
                        WHERE id = ?
                    ''', (
                        result, current_price, datetime.now().isoformat(),
                        actual_return, minutes_elapsed, signal_id
                    ))

                    updated_count += 1
                    win_emoji = "🎯" if "WIN" in result else "❌" if "LOSS" in result else "⏰"
                    logger.info(f"📊 {win_emoji} {symbol} {signal_type}: {result} ({actual_return:+.2f}%)")
                else:
                    # Mantener como PENDING si no hay resultado claro
                    logger.info(f"📊 🔄 {symbol} {signal_type}: Mantener PENDING ({actual_return:+.2f}%)")

            conn.commit()
            conn.close()

            logger.info(f"✅ Evaluación forzada completada: {updated_count} señales actualizadas")
            return updated_count

        except Exception as e:
            logger.error(f"❌ Error en evaluación forzada: {e}")
            return 0

    def get_recent_signals(self, limit=50):
        """Obtiene las señales recientes con el mismo formato que usa get_performance_stats"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM signals
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

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
                    'tp_price': safe_float(signal[15]),  # Take Profit
                    'sl_price': safe_float(signal[16]),  # Stop Loss
                    'result': signal[20] if signal[20] is not None else None,
                    'actual_return': safe_float(signal[23]),
                    'time_to_resolution': safe_float(signal[24]),
                    'today': signal[1][:10] == datetime.now().strftime('%Y-%m-%d') if signal[1] else False
                })

            conn.close()
            return recent_signals

        except Exception as e:
            logger.error(f"❌ Error obteniendo señales recientes: {e}")
            return []

    def calculate_streaks(self, streak_data):
        """Calcula rachas ganadoras y perdedoras"""
        if not streak_data:
            return 0, 0, 0

        current_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        current_win_streak = 0
        current_loss_streak = 0

        last_result = None

        for result, timestamp, symbol in streak_data:
            if result and 'WIN' in result:
                if last_result and 'WIN' in last_result:
                    current_win_streak += 1
                else:
                    current_win_streak = 1
                    current_loss_streak = 0
                max_win_streak = max(max_win_streak, current_win_streak)
                current_streak = current_win_streak

            elif result and 'LOSS' in result:
                if last_result and 'LOSS' in last_result:
                    current_loss_streak += 1
                else:
                    current_loss_streak = 1
                    current_win_streak = 0
                max_loss_streak = max(max_loss_streak, current_loss_streak)
                current_streak = -current_loss_streak

            last_result = result

        return current_streak, max_win_streak, max_loss_streak

    def get_sample_stats(self):
        """Retorna datos de ejemplo cuando no hay datos reales"""
        return {
            'total_signals': 0,
            'wins': 0,
            'losses': 0,
            'expired': 0,
            'pending': 0,
            'win_rate': 0,
            'avg_return': 0,
            'avg_score': 0,
            'avg_time_minutes': 0,
            'best_return': 0,
            'worst_return': 0,
            'total_profit': 0,
            'total_loss': 0,
            'net_profit': 0,
            'score_breakdown': [
                {
                    'range': 'PREMIUM (95-100)',
                    'count': 0,
                    'wins': 0,
                    'win_rate': 0,
                    'avg_return': 0,
                    'best_return': 0,
                    'worst_return': 0
                },
                {
                    'range': 'EXCELLENT (90-94)',
                    'count': 0,
                    'wins': 0,
                    'win_rate': 0,
                    'avg_return': 0,
                    'best_return': 0,
                    'worst_return': 0
                }
            ],
            'symbol_breakdown': [
                {
                    'symbol': 'BTCUSDT',
                    'count': 0,
                    'wins': 0,
                    'win_rate': 0,
                    'avg_return': 0,
                    'avg_score': 0
                },
                {
                    'symbol': 'ETHUSDT',
                    'count': 0,
                    'wins': 0,
                    'win_rate': 0,
                    'avg_return': 0,
                    'avg_score': 0
                },
                {
                    'symbol': 'SOLUSDT',
                    'count': 0,
                    'wins': 0,
                    'win_rate': 0,
                    'avg_return': 0,
                    'avg_score': 0
                }
            ],
            'hourly_breakdown': [],
            'volatility_analysis': [
                {
                    'symbol': 'BTCUSDT',
                    'avg_volatility': 0,
                    'max_volatility': 0,
                    'count': 0
                },
                {
                    'symbol': 'ETHUSDT',
                    'avg_volatility': 0,
                    'max_volatility': 0,
                    'count': 0
                },
                {
                    'symbol': 'SOLUSDT',
                    'avg_volatility': 0,
                    'max_volatility': 0,
                    'count': 0
                }
            ],
            'streak_analysis': {
                'current_streak': 0,
                'max_win_streak': 0,
                'max_loss_streak': 0,
                'streak_status': 'NEUTRAL'
            }
        }

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obtiene el precio actual de Binance"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return float(response.json()['price'])
        except Exception as e:
            logger.error(f"Error obteniendo precio de {symbol}: {e}")
        return None
    
    def check_tp_sl_hit(self, signal_type: str, entry_price: float, 
                       current_price: float, tp_price: float, sl_price: float) -> Optional[str]:
        """Verifica si se alcanzó TP o SL"""
        if signal_type == "buy":
            if current_price >= tp_price:
                return "WIN_TP"
            elif current_price <= sl_price:
                return "LOSS_SL"
        else:  # sell
            if current_price <= tp_price:
                return "WIN_TP"
            elif current_price >= sl_price:
                return "LOSS_SL"
        return None
    
    def calculate_return(self, signal_type: str, entry_price: float, exit_price: float) -> float:
        """Calcula el retorno real de la señal"""
        if signal_type == "buy":
            return ((exit_price - entry_price) / entry_price) * 100
        else:  # sell
            return ((entry_price - exit_price) / entry_price) * 100
    
    def get_performance_stats(self, days: int = 30) -> Dict:
        """Obtiene estadísticas de rendimiento completas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Debug: Verificar si hay datos
        cursor.execute('SELECT COUNT(*) FROM signals')
        total_count = cursor.fetchone()[0]
        logger.info(f"📊 Total señales en BD: {total_count}")

        cursor.execute('SELECT COUNT(*) FROM signals WHERE result IS NULL OR result = \'None\' OR result = \'\'')
        pending_count = cursor.fetchone()[0]
        logger.info(f"📊 Señales pendientes: {pending_count}")

        # Estadísticas básicas - SOLO SEÑALES EXCELENTES (Score ≥85)
        cursor.execute('''
            SELECT
                COUNT(*) as total_signals,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result LIKE 'LOSS%' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN result = 'EXPIRED' THEN 1 ELSE 0 END) as expired,
                SUM(CASE WHEN result IS NULL OR result = 'None' OR result = '' THEN 1 ELSE 0 END) as pending,
                AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return,
                AVG(score) as avg_score,
                AVG(CASE WHEN time_to_resolution IS NOT NULL THEN time_to_resolution END) as avg_time_minutes,
                MAX(actual_return) as best_return,
                MIN(actual_return) as worst_return,
                SUM(CASE WHEN result LIKE 'WIN%' THEN actual_return ELSE 0 END) as total_profit,
                SUM(CASE WHEN result LIKE 'LOSS%' THEN actual_return ELSE 0 END) as total_loss
            FROM signals
            WHERE datetime(timestamp) > datetime('now', '-{} days')
        '''.format(days))

        basic_stats = cursor.fetchone()

        # Estadísticas por score - CORREGIDO PARA MOSTRAR TODOS LOS RANGOS
        cursor.execute('''
            SELECT
                CASE
                    WHEN score >= 90 THEN 'ULTRA-PREMIUM (90-100)'
                    WHEN score >= 85 THEN 'PREMIUM (85-89)'
                    WHEN score >= 80 THEN 'EXCELENTE (80-84)'
                    WHEN score >= 70 THEN 'FUERTE (70-79)'
                    WHEN score >= 60 THEN 'BUENA (60-69)'
                    ELSE 'REGULAR (<60)'
                END as score_range,
                COUNT(*) as count,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return,
                MAX(actual_return) as best_return,
                MIN(actual_return) as worst_return
            FROM signals
            WHERE datetime(timestamp) > datetime('now', '-{} days')
            GROUP BY score_range
            ORDER BY
                CASE
                    WHEN score_range = 'ULTRA-PREMIUM (90-100)' THEN 1
                    WHEN score_range = 'PREMIUM (85-89)' THEN 2
                    WHEN score_range = 'EXCELENTE (80-84)' THEN 3
                    WHEN score_range = 'FUERTE (70-79)' THEN 4
                    WHEN score_range = 'BUENA (60-69)' THEN 5
                    ELSE 6
                END
        '''.format(days))

        score_stats = cursor.fetchall()

        # Estadísticas por símbolo (INCLUIR TODAS las señales)
        cursor.execute('''
            SELECT
                symbol,
                COUNT(*) as count,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result LIKE 'LOSS%' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN result = 'EXPIRED' THEN 1 ELSE 0 END) as expired,
                SUM(CASE WHEN result IS NULL OR result = 'None' OR result = '' THEN 1 ELSE 0 END) as pending,
                AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return,
                AVG(score) as avg_score
            FROM signals
            WHERE datetime(timestamp) > datetime('now', '-{} days')
            GROUP BY symbol
            ORDER BY count DESC
        '''.format(days))

        symbol_stats = cursor.fetchall()

        # Estadísticas por horario (INCLUIR TODAS las señales)
        cursor.execute('''
            SELECT
                strftime('%H', timestamp) as hour,
                COUNT(*) as count,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return,
                AVG(score) as avg_score
            FROM signals
            WHERE datetime(timestamp) > datetime('now', '-{} days')
            GROUP BY hour
            HAVING count >= 2
            ORDER BY count DESC
        '''.format(days))

        hourly_stats = cursor.fetchall()

        # Análisis de volatilidad por símbolo (usar ATR como proxy)
        cursor.execute('''
            SELECT
                symbol,
                AVG(atr) as avg_atr,
                MAX(atr) as max_atr,
                AVG(ABS(candle_change)) as avg_candle_volatility,
                COUNT(*) as count
            FROM signals
            WHERE datetime(timestamp) > datetime('now', '-{} days')
            AND atr IS NOT NULL
            GROUP BY symbol
        '''.format(days))

        volatility_stats = cursor.fetchall()

        # Análisis de streaks (rachas) - GENERAL
        cursor.execute('''
            SELECT
                result,
                timestamp,
                symbol
            FROM signals
            WHERE result IS NOT NULL AND result != 'None'
            AND datetime(timestamp) > datetime('now', '-{} days')
            ORDER BY timestamp DESC
        '''.format(days))

        streak_data = cursor.fetchall()
        current_streak, max_win_streak, max_loss_streak = self.calculate_streaks(streak_data)

        # Análisis de streaks POR SÍMBOLO
        symbol_streaks = {}
        for symbol in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']:
            cursor.execute('''
                SELECT
                    result,
                    timestamp,
                    symbol
                FROM signals
                WHERE result IS NOT NULL AND result != 'None'
                AND symbol = ?
                AND datetime(timestamp) > datetime('now', '-{} days')
                ORDER BY timestamp DESC
            '''.format(days), (symbol,))

            symbol_data = cursor.fetchall()
            if symbol_data:
                current, max_win, max_loss = self.calculate_streaks(symbol_data)
                symbol_streaks[symbol] = {
                    'current_streak': current,
                    'max_win_streak': max_win,
                    'max_loss_streak': max_loss,
                    'last_signal_time': symbol_data[0][1] if symbol_data else None
                }

        conn.close()

        total_signals = basic_stats[0] or 0
        wins = basic_stats[1] or 0
        losses = basic_stats[2] or 0
        expired = basic_stats[3] or 0
        pending = basic_stats[4] or 0
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

        # Si no hay datos, mostrar mensaje informativo
        if total_signals == 0:
            logger.info("📊 No hay señales registradas aún. Esperando primera señal...")

        return {
            'total_signals': total_signals,
            'wins': wins,
            'losses': losses,
            'expired': expired,
            'pending': pending,
            'win_rate': win_rate,
            'avg_return': basic_stats[5] or 0,
            'avg_score': basic_stats[6] or 0,
            'avg_time_minutes': basic_stats[7] or 0,
            'best_return': basic_stats[8] or 0,
            'worst_return': basic_stats[9] or 0,
            'total_profit': basic_stats[10] or 0,
            'total_loss': basic_stats[11] or 0,
            'net_profit': (basic_stats[10] or 0) + (basic_stats[11] or 0),
            'score_breakdown': [
                {
                    'range': row[0],
                    'count': row[1],
                    'wins': row[2],
                    'win_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                    'avg_return': row[3] or 0,
                    'best_return': row[4] or 0,
                    'worst_return': row[5] or 0
                }
                for row in score_stats
            ],
            'symbol_breakdown': [
                {
                    'symbol': row[0],
                    'count': row[1],
                    'wins': row[2],
                    'losses': row[3],
                    'expired': row[4],
                    'pending': row[5],
                    'win_rate': (row[2] / (row[2] + row[3]) * 100) if (row[2] + row[3]) > 0 else 0,
                    'avg_return': row[6] or 0,
                    'avg_score': row[7] or 0
                }
                for row in symbol_stats
            ],
            'hourly_breakdown': [
                {
                    'hour': f"{int(row[0]):02d}:00",
                    'count': row[1],
                    'wins': row[2],
                    'win_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                    'avg_return': row[3] or 0,
                    'avg_score': row[4] or 0
                }
                for row in hourly_stats
            ],
            'hourly_breakdown': [
                {
                    'hour': f"{int(row[0]):02d}:00",
                    'count': row[1],
                    'wins': row[2],
                    'win_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                    'avg_return': row[3] or 0,
                    'avg_score': row[4] or 0
                }
                for row in hourly_stats
            ],
            'volatility_breakdown': [
                {
                    'symbol': row[0],
                    'avg_atr': row[1] or 0,
                    'max_atr': row[2] or 0,
                    'avg_candle_volatility': row[3] or 0,
                    'count': row[4]
                }
                for row in volatility_stats
            ],
            'streak_analysis': {
                'current_streak': current_streak,
                'max_win_streak': max_win_streak,
                'max_loss_streak': max_loss_streak,
                'streak_status': 'WIN' if current_streak > 0 else 'LOSS' if current_streak < 0 else 'NEUTRAL'
            },
            'symbol_streaks': symbol_streaks
        }

# Instancia global
performance_tracker = PerformanceTracker()
