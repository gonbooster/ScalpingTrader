# 🤖 Scalping Trader Bot

Bot de trading automático que monitorea BTCUSDT y envía alertas por email basadas en indicadores técnicos (EMA y RSI).

## 🚀 Características

- **Análisis técnico automático**: Utiliza EMA (10/21) y RSI para generar señales
- **Notificaciones por email**: Envía alertas automáticas cuando detecta oportunidades
- **Dashboard web**: Interfaz web para monitorear el estado del bot
- **Datos en tiempo real**: Conecta con la API de Binance
- **Modo simulación**: Funciona con datos simulados si Binance no está disponible
- **Desplegable en la nube**: Optimizado para Render.com

## 📊 Indicadores Utilizados

### Señales de Compra (BUY)
- EMA rápida (10) > EMA lenta (21)
- RSI entre 50-65
- Volumen superior al promedio

### Señales de Venta (SELL)
- EMA rápida (10) < EMA lenta (21)
- RSI entre 38-55
- Volumen superior al promedio

## 🛠️ Instalación Local

1. **Clonar el repositorio**
```bash
git clone <tu-repo>
cd ScalpingTrader
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
export EMAIL_FROM="tu-email@gmail.com"
export EMAIL_PASSWORD="tu-app-password"
export EMAIL_TO="destino@gmail.com"
export SYMBOL="BTCUSDT"
export INTERVAL="1m"
```

4. **Ejecutar la aplicación**
```bash
python app.py
```

5. **Acceder al dashboard**
Abre tu navegador en `http://localhost:5000`

## ☁️ Despliegue en Render.com

### Opción 1: Usando render.yaml (Recomendado)

1. **Conectar repositorio**
   - Ve a [Render.com](https://render.com)
   - Conecta tu cuenta de GitHub
   - Selecciona este repositorio

2. **Configurar variables de entorno**
   En el dashboard de Render, configura:
   ```
   EMAIL_FROM = tu-email@gmail.com
   EMAIL_PASSWORD = tu-app-password-de-gmail
   EMAIL_TO = destino@gmail.com
   SYMBOL = BTCUSDT
   INTERVAL = 1m
   ```

3. **Desplegar**
   Render detectará automáticamente el archivo `render.yaml` y desplegará la aplicación.

### Opción 2: Configuración Manual

1. **Crear nuevo Web Service**
   - Tipo: Web Service
   - Repositorio: Tu repositorio de GitHub
   - Branch: main

2. **Configuración de Build**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
   ```

3. **Variables de entorno**
   Agregar las mismas variables mencionadas arriba.

## 📧 Configuración de Email

Para recibir notificaciones por email, necesitas configurar una **App Password** de Gmail:

1. **Habilitar 2FA en Gmail**
   - Ve a tu cuenta de Google
   - Seguridad → Verificación en 2 pasos

2. **Generar App Password**
   - Seguridad → Contraseñas de aplicaciones
   - Selecciona "Correo" y "Otro"
   - Copia la contraseña generada (16 caracteres)

3. **Configurar variables**
   ```
   EMAIL_FROM = tu-email@gmail.com
   EMAIL_PASSWORD = la-app-password-de-16-caracteres
   EMAIL_TO = donde-quieres-recibir-alertas@gmail.com
   ```

## 🔧 API Endpoints

- **`/`** - Dashboard principal con interfaz web
- **`/status`** - Estado del bot en formato JSON
- **`/health`** - Health check para monitoreo

## 📱 Características del Dashboard

- **Auto-refresh**: Se actualiza cada 30 segundos
- **Métricas en tiempo real**: Precio, RSI, señales enviadas
- **Estado del bot**: Activo/Iniciando
- **Fuente de datos**: Indica si usa datos reales o simulados
- **Estado del email**: Muestra si las notificaciones están configuradas

## ⚠️ Consideraciones Importantes

- **Solo para fines educativos**: Este bot es para aprendizaje, no para trading real
- **Sin garantías**: Los resultados pasados no garantizan resultados futuros
- **Gestión de riesgo**: Siempre usa stop-loss y gestión adecuada del capital
- **Datos simulados**: Si Binance no está disponible, usa datos simulados para demostración

## 🔒 Seguridad

- Las variables de entorno mantienen seguras las credenciales
- No se almacenan datos sensibles en el código
- Logging configurado para debugging sin exponer información sensible

## 📈 Monitoreo

El bot incluye:
- Logging detallado de todas las operaciones
- Health checks para monitoreo de uptime
- Manejo de errores robusto
- Reconexión automática en caso de fallos

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**⚠️ Disclaimer**: Este software es solo para fines educativos. El trading de criptomonedas conlleva riesgos significativos. Nunca inviertas más de lo que puedes permitirte perder.
