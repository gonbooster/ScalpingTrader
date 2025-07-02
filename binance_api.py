# binance_api.py - Conexión con la API de Binance
import requests
import logging
import time
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class BinanceAPI:
    def __init__(self, base_url="https://api.binance.com/api/v3"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ScalpingBot/1.0'
        })
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> Optional[List]:
        """Obtiene datos de velas de Binance"""
        url = f"{self.base_url}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            logger.info(f"📡 Conectando a Binance: {url}?symbol={symbol}&interval={interval}&limit={limit}")
            
            response = self.session.get(url, params=params, timeout=10)
            logger.info(f"📡 Respuesta Binance: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Datos reales obtenidos de Binance")
                return data
            else:
                logger.error(f"❌ Error Binance: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout conectando a Binance")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("❌ Error de conexión a Binance")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return None
    
    def get_multi_timeframe_data(self, symbol: str) -> Dict:
        """Obtiene datos de múltiples timeframes para un símbolo"""
        logger.info("📡 Obteniendo datos multi-timeframe...")
        
        # Obtener datos de diferentes timeframes
        data_1m = self.get_klines(symbol, "1m", 100)
        if not data_1m:
            return {}
        
        time.sleep(0.1)  # Rate limiting
        
        data_15m = self.get_klines(symbol, "15m", 50)
        if not data_15m:
            return {}
        
        time.sleep(0.1)  # Rate limiting
        
        data_1h = self.get_klines(symbol, "1h", 30)
        if not data_1h:
            return {}
        
        return {
            "1m": data_1m,
            "15m": data_15m,
            "1h": data_1h
        }
    
    def extract_prices_from_klines(self, klines: List) -> Dict:
        """Extrae precios de los datos de klines"""
        if not klines:
            return {}
        
        closes = [float(k[4]) for k in klines]
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        volumes = [float(k[5]) for k in klines]
        opens = [float(k[1]) for k in klines]
        
        return {
            "closes": closes,
            "highs": highs,
            "lows": lows,
            "volumes": volumes,
            "opens": opens,
            "current_price": closes[-1] if closes else 0,
            "current_volume": volumes[-1] if volumes else 0
        }
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Obtiene información básica del símbolo"""
        url = f"{self.base_url}/ticker/24hr"
        params = {"symbol": symbol}
        
        try:
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Error obteniendo info de {symbol}: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error obteniendo info de {symbol}: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Prueba la conexión con Binance"""
        try:
            url = f"{self.base_url}/ping"
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

# Instancia global
binance_api = BinanceAPI()

def get_binance_data(symbol: str, interval: str, limit: int = 100) -> Optional[List]:
    """Función helper para obtener datos de Binance"""
    return binance_api.get_klines(symbol, interval, limit)

def get_multi_timeframe_data(symbol: str) -> Dict:
    """Función helper para obtener datos multi-timeframe"""
    return binance_api.get_multi_timeframe_data(symbol)

def extract_prices(klines: List) -> Dict:
    """Función helper para extraer precios"""
    return binance_api.extract_prices_from_klines(klines)

def test_binance_connection() -> bool:
    """Función helper para probar conexión"""
    return binance_api.test_connection()
