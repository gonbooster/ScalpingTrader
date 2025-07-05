#!/usr/bin/env python3
"""
Reset manual de la base de datos de trading
"""

import sqlite3
import os
from datetime import datetime

def manual_reset():
    """Reset manual de todos los datos"""
    
    print("🗑️ RESET MANUAL DE BASE DE DATOS")
    print("=" * 40)
    
    # Confirmar
    confirm = input("¿Eliminar TODOS los datos? (escriba 'SI'): ")
    if confirm != 'SI':
        print("❌ Cancelado")
        return
    
    try:
        # Eliminar base de datos existente
        db_path = 'trading_performance.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Base de datos eliminada")
        
        # Crear nueva base de datos vacía
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla signals con TODAS las columnas necesarias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                entry_price REAL NOT NULL,
                score REAL NOT NULL,
                conditions_met INTEGER,
                total_conditions INTEGER,
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
                result TEXT,
                exit_price REAL,
                exit_timestamp TEXT,
                actual_return REAL,
                time_to_resolution INTEGER,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Nueva base de datos creada")
        print("📊 Estado: 0 señales")
        print("🎉 Reset completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    manual_reset()
