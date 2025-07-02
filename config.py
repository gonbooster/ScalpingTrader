"""
Configuración centralizada para el Scalping Bot
"""
import os

class Config:
    # Configuración de trading
    SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
    INTERVAL = os.getenv("INTERVAL", "1m")
    
    # Parámetros de indicadores técnicos
    EMA_FAST_PERIOD = int(os.getenv("EMA_FAST_PERIOD", "10"))
    EMA_SLOW_PERIOD = int(os.getenv("EMA_SLOW_PERIOD", "21"))
    RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
    
    # Rangos de RSI para señales
    RSI_BUY_MIN = float(os.getenv("RSI_BUY_MIN", "50"))
    RSI_BUY_MAX = float(os.getenv("RSI_BUY_MAX", "65"))
    RSI_SELL_MIN = float(os.getenv("RSI_SELL_MIN", "38"))
    RSI_SELL_MAX = float(os.getenv("RSI_SELL_MAX", "55"))
    
    # Configuración de email
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_TO = os.getenv("EMAIL_TO")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
    
    # Configuración de la aplicación
    ANALYSIS_INTERVAL = int(os.getenv("ANALYSIS_INTERVAL", "60"))  # segundos
    WEB_REFRESH_INTERVAL = int(os.getenv("WEB_REFRESH_INTERVAL", "30"))  # segundos
    
    # Configuración de datos
    KLINES_LIMIT = int(os.getenv("KLINES_LIMIT", "100"))
    VOLUME_AVERAGE_PERIOD = int(os.getenv("VOLUME_AVERAGE_PERIOD", "20"))
    
    # URLs de API
    BINANCE_API_BASE = os.getenv("BINANCE_API_BASE", "https://api.binance.com/api/v3")
    
    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Valida la configuración y retorna errores si los hay"""
        errors = []
        
        # Validar parámetros numéricos
        if cls.EMA_FAST_PERIOD >= cls.EMA_SLOW_PERIOD:
            errors.append("EMA_FAST_PERIOD debe ser menor que EMA_SLOW_PERIOD")
        
        if cls.RSI_BUY_MIN >= cls.RSI_BUY_MAX:
            errors.append("RSI_BUY_MIN debe ser menor que RSI_BUY_MAX")
            
        if cls.RSI_SELL_MIN >= cls.RSI_SELL_MAX:
            errors.append("RSI_SELL_MIN debe ser menor que RSI_SELL_MAX")
        
        # Validar rangos
        if not (0 <= cls.RSI_BUY_MIN <= 100):
            errors.append("RSI_BUY_MIN debe estar entre 0 y 100")
            
        if not (0 <= cls.RSI_BUY_MAX <= 100):
            errors.append("RSI_BUY_MAX debe estar entre 0 y 100")
            
        if not (0 <= cls.RSI_SELL_MIN <= 100):
            errors.append("RSI_SELL_MIN debe estar entre 0 y 100")
            
        if not (0 <= cls.RSI_SELL_MAX <= 100):
            errors.append("RSI_SELL_MAX debe estar entre 0 y 100")
        
        return errors
    
    @classmethod
    def get_email_config(cls):
        """Retorna la configuración de email"""
        return {
            'from': cls.EMAIL_FROM,
            'password': cls.EMAIL_PASSWORD,
            'to': cls.EMAIL_TO,
            'smtp_server': cls.SMTP_SERVER,
            'smtp_port': cls.SMTP_PORT
        }
    
    @classmethod
    def is_email_configured(cls):
        """Verifica si el email está configurado correctamente"""
        return all([cls.EMAIL_FROM, cls.EMAIL_PASSWORD, cls.EMAIL_TO])
    
    @classmethod
    def get_trading_params(cls):
        """Retorna los parámetros de trading"""
        return {
            'symbol': cls.SYMBOL,
            'interval': cls.INTERVAL,
            'ema_fast': cls.EMA_FAST_PERIOD,
            'ema_slow': cls.EMA_SLOW_PERIOD,
            'rsi_period': cls.RSI_PERIOD,
            'rsi_buy_range': (cls.RSI_BUY_MIN, cls.RSI_BUY_MAX),
            'rsi_sell_range': (cls.RSI_SELL_MIN, cls.RSI_SELL_MAX)
        }
