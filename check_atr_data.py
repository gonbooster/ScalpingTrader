#!/usr/bin/env python3
# check_atr_data.py - Verificar datos de ATR en la base de datos

import sqlite3
import sys

def check_atr_data():
    """Verifica los valores de ATR en la base de datos"""
    try:
        conn = sqlite3.connect('trading_performance.db')
        cursor = conn.cursor()
        
        print("🔍 VERIFICANDO DATOS DE ATR EN LA BASE DE DATOS:")
        print("=" * 60)
        
        # Últimos 10 valores de ATR
        cursor.execute('''
            SELECT symbol, atr, candle_change, entry_price, timestamp 
            FROM signals 
            ORDER BY id DESC 
            LIMIT 10
        ''')
        
        print("\n📊 ÚLTIMOS 10 VALORES DE ATR:")
        for row in cursor.fetchall():
            symbol, atr, candle_change, price, timestamp = row
            print(f"{symbol}: ATR={atr:.2f}, Candle={candle_change:.2f}%, Price=${price:.2f}, Time={timestamp[:16]}")
        
        # Estadísticas por símbolo
        cursor.execute('''
            SELECT 
                symbol,
                COUNT(*) as count,
                AVG(atr) as avg_atr,
                MIN(atr) as min_atr,
                MAX(atr) as max_atr,
                AVG(ABS(candle_change)) as avg_candle_volatility
            FROM signals 
            WHERE atr IS NOT NULL 
            GROUP BY symbol
        ''')
        
        print("\n📈 ESTADÍSTICAS DE ATR POR SÍMBOLO:")
        for row in cursor.fetchall():
            symbol, count, avg_atr, min_atr, max_atr, avg_candle = row
            print(f"{symbol}: Count={count}, Avg ATR={avg_atr:.2f}, Min={min_atr:.2f}, Max={max_atr:.2f}, Avg Candle={avg_candle:.2f}%")
        
        # Verificar si hay valores nulos
        cursor.execute('''
            SELECT symbol, COUNT(*) as null_count
            FROM signals 
            WHERE atr IS NULL 
            GROUP BY symbol
        ''')
        
        null_data = cursor.fetchall()
        if null_data:
            print("\n⚠️ VALORES NULOS DE ATR:")
            for row in null_data:
                print(f"{row[0]}: {row[1]} valores nulos")
        else:
            print("\n✅ No hay valores nulos de ATR")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")

if __name__ == "__main__":
    check_atr_data()
