# adaptive_optimizer.py - Sistema de optimización adaptativa
import logging
import sqlite3
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AdaptiveOptimizer:
    """Sistema que ajusta parámetros automáticamente basado en rendimiento"""
    
    def __init__(self):
        self.db_path = 'trading_performance.db'
        self.min_signals_for_optimization = 20  # Mínimo de señales para optimizar
        self.optimization_interval_hours = 24   # Optimizar cada 24 horas
        self.last_optimization = None
        
    def should_optimize(self):
        """Determina si es momento de optimizar parámetros"""
        if not self.last_optimization:
            return True
            
        hours_since_last = (datetime.now() - self.last_optimization).total_seconds() / 3600
        return hours_since_last >= self.optimization_interval_hours
    
    def get_recent_performance(self, hours=24):
        """Obtiene rendimiento de las últimas X horas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener señales de las últimas X horas
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN result LIKE 'WIN%' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result LIKE 'LOSS%' THEN 1 ELSE 0 END) as losses,
                    AVG(CASE WHEN actual_return IS NOT NULL THEN actual_return END) as avg_return,
                    AVG(time_to_resolution) as avg_time
                FROM signals 
                WHERE datetime(timestamp) > datetime('now', '-{} hours')
                AND result IS NOT NULL
            '''.format(hours))
            
            stats = cursor.fetchone()
            conn.close()
            
            if stats[0] == 0:  # No hay datos
                return None
                
            win_rate = (stats[1] / (stats[1] + stats[2])) * 100 if (stats[1] + stats[2]) > 0 else 0
            
            return {
                'total_signals': stats[0],
                'wins': stats[1],
                'losses': stats[2],
                'win_rate': win_rate,
                'avg_return': stats[3] or 0,
                'avg_time_minutes': stats[4] or 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo rendimiento: {e}")
            return None
    
    def get_optimization_recommendations(self):
        """Genera recomendaciones de optimización basadas en rendimiento"""
        performance = self.get_recent_performance(24)
        
        if not performance or performance['total_signals'] < self.min_signals_for_optimization:
            return None
            
        recommendations = []
        
        # Analizar win rate
        if performance['win_rate'] < 40:
            recommendations.append({
                'type': 'SCORE_THRESHOLD',
                'action': 'INCREASE',
                'current': 85,
                'suggested': 90,
                'reason': f"Win rate bajo ({performance['win_rate']:.1f}%) - Aumentar umbral de score"
            })
            
        elif performance['win_rate'] > 60:
            recommendations.append({
                'type': 'SCORE_THRESHOLD',
                'action': 'DECREASE',
                'current': 85,
                'suggested': 80,
                'reason': f"Win rate alto ({performance['win_rate']:.1f}%) - Permitir más señales"
            })
        
        # Analizar tiempo de resolución
        if performance['avg_time_minutes'] > 120:  # Más de 2 horas
            recommendations.append({
                'type': 'TIMEOUT',
                'action': 'DECREASE',
                'current': 180,  # 3 horas
                'suggested': 120,  # 2 horas
                'reason': f"Tiempo promedio alto ({performance['avg_time_minutes']:.0f} min) - Reducir timeout"
            })
            
        # Analizar retorno promedio
        if performance['avg_return'] < 0.3:
            recommendations.append({
                'type': 'TP_MULTIPLIER',
                'action': 'INCREASE',
                'current': 2.0,
                'suggested': 2.2,
                'reason': f"Retorno promedio bajo ({performance['avg_return']:.2f}%) - Aumentar TP"
            })
        
        return {
            'performance': performance,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def log_optimization_analysis(self):
        """Registra análisis de optimización en logs"""
        analysis = self.get_optimization_recommendations()
        
        if not analysis:
            logger.info("🔧 Optimización: Datos insuficientes para análisis")
            return
            
        perf = analysis['performance']
        logger.info(f"🔧 ANÁLISIS DE OPTIMIZACIÓN:")
        logger.info(f"📊 Últimas 24h: {perf['total_signals']} señales, {perf['win_rate']:.1f}% WR, {perf['avg_return']:.2f}% retorno")
        logger.info(f"⏱️ Tiempo promedio: {perf['avg_time_minutes']:.0f} minutos")
        
        if analysis['recommendations']:
            logger.info(f"💡 RECOMENDACIONES:")
            for rec in analysis['recommendations']:
                logger.info(f"   • {rec['reason']}")
        else:
            logger.info("✅ Sistema funcionando óptimamente - No se requieren ajustes")
            
        self.last_optimization = datetime.now()

# Instancia global
adaptive_optimizer = AdaptiveOptimizer()
