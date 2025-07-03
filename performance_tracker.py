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
        
        # Obtener señales pendientes de las últimas 24 horas
        cursor.execute('''
            SELECT * FROM signals 
            WHERE status = 'PENDING' 
            AND datetime(timestamp) > datetime('now', '-24 hours')
        ''')
        
        pending_signals = cursor.fetchall()
        
        for signal in pending_signals:
            signal_id = signal[0]
            symbol = signal[2]
            signal_type = signal[3]
            entry_price = signal[4]
            tp_price = signal[15]
            sl_price = signal[16]
            entry_time = datetime.fromisoformat(signal[1])
            
            # Obtener precio actual
            current_price = self.get_current_price(symbol)
            if not current_price:
                continue
            
            # Verificar si se alcanzó TP o SL
            result = self.check_tp_sl_hit(
                signal_type, entry_price, current_price, tp_price, sl_price
            )
            
            if result:
                # Actualizar resultado
                exit_time = datetime.now()
                time_to_resolution = int((exit_time - entry_time).total_seconds() / 60)
                actual_return = self.calculate_return(
                    signal_type, entry_price, current_price
                )
                
                cursor.execute('''
                    UPDATE signals SET 
                    status = 'COMPLETED',
                    result = ?,
                    exit_price = ?,
                    exit_timestamp = ?,
                    actual_return = ?,
                    time_to_resolution = ?
                    WHERE id = ?
                ''', (
                    result, current_price, exit_time.isoformat(),
                    actual_return, time_to_resolution, signal_id
                ))
                
                logger.info(f"📊 Señal {signal_id} completada: {result} ({actual_return:.2f}%)")
        
        conn.commit()
        conn.close()
    
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
        """Obtiene estadísticas de rendimiento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estadísticas básicas
        cursor.execute('''
            SELECT 
                COUNT(*) as total_signals,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result LIKE 'LOSS%' THEN 1 ELSE 0 END) as losses,
                AVG(actual_return) as avg_return,
                AVG(score) as avg_score,
                AVG(time_to_resolution) as avg_time_minutes
            FROM signals 
            WHERE status = 'COMPLETED'
            AND datetime(timestamp) > datetime('now', '-{} days')
        '''.format(days))
        
        basic_stats = cursor.fetchone()
        
        # Estadísticas por score
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN score >= 95 THEN 'PREMIUM (95-100)'
                    WHEN score >= 90 THEN 'EXCELLENT (90-94)'
                    WHEN score >= 80 THEN 'GOOD (80-89)'
                    ELSE 'FAIR (<80)'
                END as score_range,
                COUNT(*) as count,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                AVG(actual_return) as avg_return
            FROM signals 
            WHERE status = 'COMPLETED'
            AND datetime(timestamp) > datetime('now', '-{} days')
            GROUP BY score_range
        '''.format(days))
        
        score_stats = cursor.fetchall()
        
        conn.close()
        
        total_signals = basic_stats[0] or 0
        wins = basic_stats[1] or 0
        win_rate = (wins / total_signals * 100) if total_signals > 0 else 0
        
        return {
            'total_signals': total_signals,
            'wins': wins,
            'losses': basic_stats[2] or 0,
            'win_rate': win_rate,
            'avg_return': basic_stats[3] or 0,
            'avg_score': basic_stats[4] or 0,
            'avg_time_minutes': basic_stats[5] or 0,
            'score_breakdown': [
                {
                    'range': row[0],
                    'count': row[1],
                    'wins': row[2],
                    'win_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                    'avg_return': row[3] or 0
                }
                for row in score_stats
            ]
        }

# Instancia global
performance_tracker = PerformanceTracker()
