#!/usr/bin/env python3
"""
Script seguro para resetear datos del sistema de trading
Solo para uso del administrador
"""

import requests
import sys

def reset_trading_data():
    """Resetea los datos del sistema de trading"""
    
    print("🔐 RESET DE DATOS DEL SISTEMA DE TRADING")
    print("=" * 50)
    print("⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos de señales")
    print("📋 Se creará un backup automático antes del reset")
    print()
    
    # Confirmación de seguridad
    confirm1 = input("¿Estás seguro de que quieres resetear los datos? (escriba 'SI'): ")
    if confirm1 != 'SI':
        print("❌ Operación cancelada")
        return
    
    confirm2 = input("¿Confirmas que eres el administrador? (escriba 'ADMIN'): ")
    if confirm2 != 'ADMIN':
        print("❌ Operación cancelada")
        return
    
    print("\n🔄 Enviando solicitud de reset...")
    
    try:
        # Enviar solicitud con token de seguridad
        headers = {
            'Authorization': 'Bearer SCALPING_RESET_2025',
            'Content-Type': 'application/json'
        }
        
        # URL del servidor (cambiar según entorno)
        base_url = input("URL del servidor (Enter para local): ").strip()
        if not base_url:
            base_url = 'http://127.0.0.1:8000'
        elif not base_url.startswith('http'):
            base_url = f'https://{base_url}'

        response = requests.post(
            f'{base_url}/admin/reset-data',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Reset completado exitosamente")
                print(f"📝 {result.get('message')}")
                if result.get('backup_created'):
                    print("💾 Backup creado en signals_backup")
            else:
                print(f"❌ Error: {result.get('error')}")
        elif response.status_code == 401:
            print("❌ Error de autorización: Token inválido")
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el bot esté ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    reset_trading_data()
