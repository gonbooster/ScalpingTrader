# 🚀 DEPLOYMENT EN KOYEB - SCALPING TRADER

## 📋 PASOS PARA DEPLOYMENT:

### 1. 📤 SUBIR A GITHUB:
```bash
git add .
git commit -m "🚀 DEPLOYMENT READY v8.0 - Sistema completo con auto-refresh y reset seguro"
git push origin main
```

### 2. 🌐 CONFIGURAR EN KOYEB:

1. **Ir a:** https://app.koyeb.com/
2. **Crear nueva app:** "ScalpingTrader"
3. **Fuente:** GitHub Repository
4. **Repositorio:** gonbooster/ScalpingTrader
5. **Branch:** main

### 3. ⚙️ CONFIGURACIÓN DE BUILD:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Run Command:**
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
```

### 4. 🔧 VARIABLES DE ENTORNO:

**Obligatorias:**
- `PORT`: (automático en Koyeb)

**Opcionales para email:**
- `EMAIL_FROM`: tu-email@gmail.com
- `EMAIL_PASSWORD`: tu-app-password
- `EMAIL_TO`: destinatario@gmail.com
- `SMTP_SERVER`: smtp.gmail.com
- `SMTP_PORT`: 465

### 5. 🎯 CONFIGURACIÓN AVANZADA:

**Instance Type:** Free (512MB RAM)
**Region:** Frankfurt (mejor para Europa)
**Health Check:** HTTP GET /
**Port:** 8000 (automático)

### 6. 🔄 CONFIGURACIÓN HTTP:

**IMPORTANTE:** Cambiar de HTTP/2 a HTTP/1.1 en configuración del servicio para evitar errores 502.

### 7. 📊 MONITOREO:

**UptimeRobot:** Configurar monitoreo en https://uptimerobot.com/
- URL: https://tu-app.koyeb.app/
- Intervalo: 5 minutos
- Alertas: Email cuando esté down

## 🔐 RESET SEGURO EN PRODUCCIÓN:

Para resetear datos en producción:
```bash
# Modificar reset_data.py con la URL de producción
python reset_data.py
# Cambiar: http://127.0.0.1:8000 por https://tu-app.koyeb.app
```

## 🎉 FUNCIONALIDADES DESPLEGADAS:

✅ **Dashboard principal** con datos en tiempo real
✅ **Analytics automático** con auto-refresh cada 30s
✅ **Auto-evaluación** de señales cada 10s
✅ **Sistema responsive** para móvil
✅ **Reset seguro** con autenticación
✅ **Tracking WIN/LOSS** automático
✅ **API endpoints** para datos en tiempo real

## 🌐 URLs DISPONIBLES:

- **Dashboard:** https://tu-app.koyeb.app/
- **Analytics:** https://tu-app.koyeb.app/analytics
- **Instrucciones:** https://tu-app.koyeb.app/instructions
- **API Señales:** https://tu-app.koyeb.app/api/signal-count
- **Reset Admin:** https://tu-app.koyeb.app/admin/reset-data

## ⚠️ NOTAS IMPORTANTES:

1. **Base de datos:** SQLite se resetea en cada deployment
2. **Logs:** Se mantienen en memoria, no persistentes
3. **Email:** Opcional, funciona sin configurar
4. **Binance API:** Funciona desde Koyeb (no bloqueado)
5. **Auto-refresh:** Optimizado para no sobrecargar servidor gratuito

## 🔧 TROUBLESHOOTING:

**Error 502:** Cambiar HTTP/2 → HTTP/1.1
**Timeout:** Aumentar timeout en gunicorn
**Memory:** Optimizar workers (usar solo 1)
**Logs duplicados:** Normal en inicialización
