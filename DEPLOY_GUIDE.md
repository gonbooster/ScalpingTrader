# 🚀 Guía de Despliegue en Render.com

## Pasos para Desplegar tu Scalping Bot

### 1. Preparar el Repositorio

Asegúrate de que todos los archivos estén en tu repositorio de GitHub:
- `app.py` - Aplicación principal
- `requirements.txt` - Dependencias de Python
- `render.yaml` - Configuración de Render
- `Procfile` - Comando de inicio alternativo
- `runtime.txt` - Versión de Python
- `README.md` - Documentación

### 2. Crear Cuenta en Render.com

1. Ve a [render.com](https://render.com)
2. Regístrate con tu cuenta de GitHub
3. Autoriza el acceso a tus repositorios

### 3. Configurar App Password de Gmail

**IMPORTANTE**: Para recibir notificaciones por email, necesitas una App Password:

1. **Habilitar 2FA en Gmail**:
   - Ve a [myaccount.google.com](https://myaccount.google.com)
   - Seguridad → Verificación en 2 pasos
   - Sigue los pasos para habilitarla

2. **Generar App Password**:
   - Seguridad → Contraseñas de aplicaciones
   - Selecciona "Correo" y "Otro (nombre personalizado)"
   - Escribe "Scalping Bot"
   - **Copia la contraseña de 16 caracteres** (sin espacios)

### 4. Desplegar en Render

#### Opción A: Usando render.yaml (Automático)

1. **Conectar Repositorio**:
   - En Render, click "New +"
   - Selecciona "Web Service"
   - Conecta tu repositorio de GitHub
   - Selecciona la rama `main`

2. **Render detectará automáticamente** el archivo `render.yaml`

3. **Configurar Variables de Entorno**:
   En la sección "Environment Variables":
   ```
   EMAIL_FROM = tu-email@gmail.com
   EMAIL_PASSWORD = la-app-password-de-16-caracteres
   EMAIL_TO = donde-quieres-recibir-alertas@gmail.com
   ```

4. **Desplegar**:
   - Click "Create Web Service"
   - Render comenzará el build automáticamente

#### Opción B: Configuración Manual

1. **Crear Web Service**:
   - New + → Web Service
   - Conecta tu repositorio

2. **Configuración**:
   ```
   Name: scalping-trader
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
   ```

3. **Variables de Entorno** (mismas que arriba)

### 5. Verificar el Despliegue

1. **Esperar el Build**: Toma 2-5 minutos
2. **Verificar Logs**: Revisa que no haya errores
3. **Acceder a la URL**: Render te dará una URL como `https://scalping-trader-xxx.onrender.com`
4. **Probar el Dashboard**: Deberías ver la interfaz web funcionando

### 6. Configuración Opcional

#### Variables de Entorno Adicionales:
```
SYMBOL = BTCUSDT          # Par de trading (por defecto)
INTERVAL = 1m             # Intervalo de análisis (por defecto)
```

#### Para Múltiples Pares:
Si quieres monitorear otros pares, cambia `SYMBOL`:
- `ETHUSDT` para Ethereum
- `ADAUSDT` para Cardano
- `SOLUSDT` para Solana

### 7. Monitoreo y Mantenimiento

#### URLs Importantes:
- **Dashboard**: `https://tu-app.onrender.com/`
- **Status API**: `https://tu-app.onrender.com/status`
- **Health Check**: `https://tu-app.onrender.com/health`

#### Logs en Render:
- Ve a tu servicio en Render
- Click en "Logs" para ver la actividad en tiempo real
- Busca mensajes como "🟢 SEÑAL BUY enviada" o "🔴 SEÑAL SELL enviada"

### 8. Solución de Problemas

#### El bot no envía emails:
1. Verifica que las variables de entorno estén configuradas
2. Confirma que la App Password sea correcta (16 caracteres, sin espacios)
3. Revisa los logs para errores de autenticación

#### Error de build:
1. Verifica que `requirements.txt` esté presente
2. Asegúrate de que la versión de Python sea compatible

#### El bot no se conecta a Binance:
- No te preocupes, el bot automáticamente usará datos simulados
- Esto es normal desde algunas ubicaciones geográficas

### 9. Costos

- **Plan Free de Render**: 
  - 750 horas/mes gratis
  - Suficiente para un bot 24/7
  - Se "duerme" después de 15 minutos de inactividad
  - Se "despierta" automáticamente con requests

- **Para uso 24/7 sin interrupciones**:
  - Considera el plan Starter ($7/mes)
  - Mantiene el bot siempre activo

### 10. Seguridad

✅ **Buenas prácticas implementadas**:
- Variables de entorno para credenciales
- No hay datos sensibles en el código
- Logging sin exponer información privada
- Validación de configuración

❌ **NO hagas esto**:
- No pongas credenciales directamente en el código
- No compartas tu App Password
- No uses tu contraseña principal de Gmail

### 11. Próximos Pasos

Una vez desplegado:
1. **Monitorea los primeros días** para asegurar que funciona correctamente
2. **Ajusta los parámetros** si es necesario (RSI, EMA, etc.)
3. **Considera añadir más indicadores** técnicos
4. **Implementa stop-loss** si planeas usar para trading real

---

## 🆘 ¿Necesitas Ayuda?

Si tienes problemas:
1. Revisa los logs en Render
2. Verifica que todas las variables de entorno estén configuradas
3. Confirma que la App Password de Gmail sea correcta
4. Asegúrate de que el repositorio tenga todos los archivos necesarios

**¡Tu bot estará funcionando en minutos!** 🚀
