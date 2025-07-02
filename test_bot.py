#!/usr/bin/env python3
"""
Script de prueba para verificar que el bot funciona correctamente
"""
import os
import sys
import requests
import time
from config import Config

def test_configuration():
    """Prueba la configuración del bot"""
    print("🔧 Probando configuración...")
    
    # Validar configuración
    errors = Config.validate()
    if errors:
        print("❌ Errores de configuración:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ Configuración válida")
    
    # Mostrar parámetros
    params = Config.get_trading_params()
    print(f"📊 Parámetros de trading:")
    print(f"   - Símbolo: {params['symbol']}")
    print(f"   - Intervalo: {params['interval']}")
    print(f"   - EMA rápida: {params['ema_fast']}")
    print(f"   - EMA lenta: {params['ema_slow']}")
    print(f"   - RSI período: {params['rsi_period']}")
    print(f"   - RSI compra: {params['rsi_buy_range']}")
    print(f"   - RSI venta: {params['rsi_sell_range']}")
    
    # Verificar email
    if Config.is_email_configured():
        print("✅ Email configurado correctamente")
    else:
        print("⚠️ Email no configurado - solo funcionará el dashboard web")
    
    return True

def test_binance_connection():
    """Prueba la conexión con Binance"""
    print("\n🌐 Probando conexión con Binance...")
    
    try:
        url = f"{Config.BINANCE_API_BASE}/klines"
        params = {
            'symbol': Config.SYMBOL,
            'interval': Config.INTERVAL,
            'limit': 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print("✅ Conexión con Binance exitosa")
                latest_price = float(data[-1][4])  # Precio de cierre
                print(f"📈 Último precio de {Config.SYMBOL}: ${latest_price:,.2f}")
                return True
            else:
                print("⚠️ Respuesta inesperada de Binance")
                return False
        else:
            print(f"⚠️ Error HTTP {response.status_code} - Usando datos simulados")
            return False
            
    except Exception as e:
        print(f"⚠️ Error conectando con Binance: {e}")
        print("   El bot funcionará con datos simulados")
        return False

def test_email_functionality():
    """Prueba la funcionalidad de email (opcional)"""
    if not Config.is_email_configured():
        print("\n📧 Email no configurado - saltando prueba")
        return True
    
    print("\n📧 Probando funcionalidad de email...")
    
    try:
        # Importar función de email del app principal
        sys.path.append('.')
        from app import send_email
        
        # Enviar email de prueba
        subject = "🧪 Prueba - Scalping Bot"
        body = f"""
        Este es un email de prueba del Scalping Bot.
        
        Configuración:
        - Símbolo: {Config.SYMBOL}
        - Intervalo: {Config.INTERVAL}
        - Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
        
        Si recibes este email, las notificaciones están funcionando correctamente.
        """
        
        if send_email(subject, body):
            print("✅ Email de prueba enviado correctamente")
            print(f"   Revisa tu bandeja de entrada: {Config.EMAIL_TO}")
            return True
        else:
            print("❌ Error enviando email de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de email: {e}")
        return False

def test_web_interface():
    """Prueba que la aplicación web se puede iniciar"""
    print("\n🌐 Probando interfaz web...")
    
    try:
        # Importar la app Flask
        sys.path.append('.')
        from app import app
        
        # Crear cliente de prueba
        with app.test_client() as client:
            # Probar endpoint principal
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Endpoint principal (/) funciona")
            else:
                print(f"❌ Error en endpoint principal: {response.status_code}")
                return False
            
            # Probar endpoint de status
            response = client.get('/status')
            if response.status_code == 200:
                print("✅ Endpoint de status (/status) funciona")
            else:
                print(f"❌ Error en endpoint de status: {response.status_code}")
                return False
            
            # Probar endpoint de health
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Endpoint de health (/health) funciona")
            else:
                print(f"❌ Error en endpoint de health: {response.status_code}")
                return False
        
        print("✅ Interfaz web funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error probando interfaz web: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🤖 Scalping Bot - Suite de Pruebas")
    print("=" * 50)
    
    tests = [
        ("Configuración", test_configuration),
        ("Conexión Binance", test_binance_connection),
        ("Funcionalidad Email", test_email_functionality),
        ("Interfaz Web", test_web_interface)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El bot está listo para desplegarse.")
        print("\n📋 Próximos pasos:")
        print("1. Sube el código a GitHub")
        print("2. Conecta el repositorio en Render.com")
        print("3. Configura las variables de entorno")
        print("4. Despliega la aplicación")
        print("\nVer DEPLOY_GUIDE.md para instrucciones detalladas.")
    else:
        print(f"\n⚠️ {total - passed} prueba(s) fallaron. Revisa la configuración antes de desplegar.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
