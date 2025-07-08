#!/usr/bin/env python3
# performance_analyzer.py - Análisis profundo del rendimiento del sistema

import sqlite3
import logging
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analizador profundo del rendimiento del sistema de trading"""
    
    def __init__(self):
        self.db_path = 'trading_performance.db'
    
    def analyze_comprehensive_performance(self):
        """Análisis comprehensivo del rendimiento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("🔍 ANÁLISIS PROFUNDO DEL RENDIMIENTO DEL SISTEMA")
            print("=" * 80)
            
            # 1. ANÁLISIS POR SCORE RANGES
            self._analyze_score_performance(cursor)
            
            # 2. ANÁLISIS POR SÍMBOLO
            self._analyze_symbol_performance(cursor)
            
            # 3. ANÁLISIS TEMPORAL
            self._analyze_temporal_performance(cursor)
            
            # 4. ANÁLISIS DE CRITERIOS
            self._analyze_criteria_performance(cursor)
            
            # 5. ANÁLISIS DE TP/SL
            self._analyze_tp_sl_performance(cursor)
            
            # 6. RECOMENDACIONES
            self._generate_recommendations(cursor)
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
    
    def _analyze_score_performance(self, cursor):
        """Analiza rendimiento por rangos de score"""
        print("\n📊 1. ANÁLISIS POR SCORE RANGES:")
        print("-" * 50)
        
        cursor.execute('''
            SELECT
                CASE
                    WHEN score >= 90 THEN '90-100 (ULTRA-PREMIUM)'
                    WHEN score >= 85 THEN '85-89 (PREMIUM)'
                    WHEN score >= 80 THEN '80-84 (EXCELENTE)'
                    WHEN score >= 70 THEN '70-79 (FUERTE)'
                    WHEN score >= 60 THEN '60-69 (BUENA)'
                    ELSE '<60 (REGULAR)'
                END as score_range,
                COUNT(*) as total,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result LIKE 'LOSS%' THEN 1 ELSE 0 END) as losses,
                AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return,
                AVG(time_to_resolution) as avg_time
            FROM signals
            WHERE result IS NOT NULL AND result != 'None'
            GROUP BY score_range
            ORDER BY MIN(score) DESC
        ''')
        
        for row in cursor.fetchall():
            range_name, total, wins, losses, avg_return, avg_time = row
            win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
            
            print(f"📈 {range_name}:")
            print(f"   Señales: {total} | Win Rate: {win_rate:.1f}% | Retorno: {avg_return:.2f}% | Tiempo: {avg_time:.0f}min")
            
            if win_rate < 40:
                print(f"   ⚠️ PROBLEMA: Win rate muy bajo ({win_rate:.1f}%)")
    
    def _analyze_symbol_performance(self, cursor):
        """Analiza rendimiento por símbolo"""
        print("\n💰 2. ANÁLISIS POR SÍMBOLO:")
        print("-" * 50)
        
        for symbol in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']:
            cursor.execute('''
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result LIKE 'LOSS%' THEN 1 ELSE 0 END) as losses,
                    AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return,
                    AVG(score) as avg_score,
                    AVG(atr) as avg_atr
                FROM signals
                WHERE symbol = ? AND result IS NOT NULL AND result != 'None'
            ''', (symbol,))
            
            row = cursor.fetchone()
            if row and row[0] > 0:
                total, wins, losses, avg_return, avg_score, avg_atr = row
                win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
                
                print(f"🪙 {symbol}:")
                print(f"   Señales: {total} | Win Rate: {win_rate:.1f}% | Retorno: {avg_return:.2f}%")
                print(f"   Score Promedio: {avg_score:.0f} | ATR Promedio: ${avg_atr:.2f}")
                
                if win_rate < 35:
                    print(f"   ❌ CRÍTICO: Win rate muy bajo para {symbol}")
    
    def _analyze_temporal_performance(self, cursor):
        """Analiza rendimiento temporal"""
        print("\n⏰ 3. ANÁLISIS TEMPORAL:")
        print("-" * 50)
        
        # Por hora del día
        cursor.execute('''
            SELECT
                strftime('%H', timestamp) as hour,
                COUNT(*) as total,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return
            FROM signals
            WHERE result IS NOT NULL AND result != 'None'
            GROUP BY hour
            HAVING total >= 2
            ORDER BY wins DESC
        ''')
        
        print("🕐 Mejores horas (por wins):")
        for row in cursor.fetchall()[:5]:
            hour, total, wins, avg_return = row
            win_rate = (wins / total * 100) if total > 0 else 0
            print(f"   {hour}:00 - WR: {win_rate:.1f}% | Señales: {total} | Retorno: {avg_return:.2f}%")
    
    def _analyze_criteria_performance(self, cursor):
        """Analiza rendimiento por criterios cumplidos"""
        print("\n✅ 4. ANÁLISIS DE CRITERIOS:")
        print("-" * 50)
        
        cursor.execute('''
            SELECT
                conditions_met,
                COUNT(*) as total,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return
            FROM signals
            WHERE result IS NOT NULL AND result != 'None'
            GROUP BY conditions_met
            ORDER BY conditions_met DESC
        ''')
        
        print("📊 Rendimiento por criterios cumplidos:")
        for row in cursor.fetchall():
            criteria, total, wins, avg_return = row
            win_rate = (wins / total * 100) if total > 0 else 0
            print(f"   {criteria}/8 criterios - WR: {win_rate:.1f}% | Señales: {total} | Retorno: {avg_return:.2f}%")
            
            if criteria >= 6 and win_rate < 50:
                print(f"   ⚠️ PROBLEMA: Con {criteria} criterios debería tener >50% WR")
    
    def _analyze_tp_sl_performance(self, cursor):
        """Analiza efectividad de TP/SL"""
        print("\n🎯 5. ANÁLISIS DE TP/SL:")
        print("-" * 50)
        
        cursor.execute('''
            SELECT
                result,
                COUNT(*) as count,
                AVG(actual_return) as avg_return,
                AVG(time_to_resolution) as avg_time
            FROM signals
            WHERE result IS NOT NULL AND result != 'None'
            GROUP BY result
            ORDER BY count DESC
        ''')
        
        print("📈 Tipos de resolución:")
        for row in cursor.fetchall():
            result_type, count, avg_return, avg_time = row
            print(f"   {result_type}: {count} señales | Retorno: {avg_return:.2f}% | Tiempo: {avg_time:.0f}min")
    
    def _generate_recommendations(self, cursor):
        """Genera recomendaciones específicas"""
        print("\n🚀 6. RECOMENDACIONES ESPECÍFICAS:")
        print("-" * 50)
        
        # Obtener estadísticas generales
        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return,
                AVG(score) as avg_score
            FROM signals
            WHERE result IS NOT NULL AND result != 'None'
        ''')
        
        total, wins, avg_return, avg_score = cursor.fetchone()
        win_rate = (wins / total * 100) if total > 0 else 0
        
        print(f"📊 ESTADO ACTUAL: {win_rate:.1f}% WR | {avg_return:.2f}% retorno | {avg_score:.0f} score promedio")
        print()
        
        # Recomendaciones específicas
        if win_rate < 40:
            print("🔴 CRÍTICO - Win Rate < 40%:")
            print("   1. ⬆️ AUMENTAR criterios requeridos de 5/8 a 6/8 o 7/8")
            print("   2. 🎯 REDUCIR TP targets (más conservador)")
            print("   3. 🛡️ AJUSTAR SL más cerca (menos riesgo)")
            print("   4. 📧 SUBIR filtro email a Score ≥90")
            
        if avg_return < 0:
            print("🔴 CRÍTICO - Retorno Negativo:")
            print("   1. 📉 REDUCIR multiplicadores ATR para TP")
            print("   2. 🔒 AUMENTAR multiplicadores ATR para SL")
            print("   3. ⏱️ REDUCIR timeout de señales")
            
        if avg_score < 75:
            print("🟡 MEJORAR - Score Promedio Bajo:")
            print("   1. 🔧 OPTIMIZAR algoritmo de scoring")
            print("   2. 📊 MEJORAR detección de momentum")
            print("   3. 📈 AÑADIR más indicadores técnicos")
        
        print("\n💡 MEJORAS INMEDIATAS SUGERIDAS:")
        print("   1. 🎯 Cambiar criterios requeridos: 5/8 → 6/8")
        print("   2. 📧 Cambiar filtro email: Score ≥85 → Score ≥90")
        print("   3. 🎯 Reducir TP multipliers: BTC 2.0→1.5, ETH 2.2→1.8, SOL 2.5→2.0")
        print("   4. 🛡️ Reducir SL multipliers: BTC 1.0→0.8, ETH 1.1→0.9, SOL 1.2→1.0")
        print("   5. ⏱️ Reducir timeout: 3h → 2h")

if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    analyzer.analyze_comprehensive_performance()
