# 🐍 Configuración Local - Scalping Bot

## Instalación de Python (Windows)

### Opción 1: Desde python.org (Recomendado)

1. **Descargar Python**:
   - Ve a [python.org/downloads](https://www.python.org/downloads/)
   - Descarga Python 3.11 o superior
   - **IMPORTANTE**: Marca "Add Python to PATH" durante la instalación

2. **Verificar instalación**:
   ```cmd
   python --version
   pip --version
   ```

### Opción 2: Desde Microsoft Store

1. Abre Microsoft Store
2. Busca "Python 3.11"
3. Instala la versión oficial

## Configuración del Proyecto

### 1. Clonar/Descargar el Proyecto
```cmd
cd C:\Users\gonza\Documents\augment-projects\ScalpingTrader
```

### 2. Crear Entorno Virtual (Recomendado)
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias
```cmd
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:
```cmd
copy .env.example .env
```

Edita `.env` con tus datos:
```
EMAIL_FROM=tu-email@gmail.com
EMAIL_PASSWORD=tu-app-password-de-gmail
EMAIL_TO=donde-quieres-recibir-alertas@gmail.com
```

### 5. Probar la Configuración
```cmd
python test_bot.py
```

### 6. Ejecutar el Bot
```cmd
python app.py
```

### 7. Acceder al Dashboard
Abre tu navegador en: `http://localhost:5000`

## Configuración de Gmail App Password

1. **Habilitar 2FA**:
   - Ve a [myaccount.google.com](https://myaccount.google.com)
   - Seguridad → Verificación en 2 pasos

2. **Generar App Password**:
   - Seguridad → Contraseñas de aplicaciones
   - Selecciona "Correo" y "Otro"
   - Copia la contraseña de 16 caracteres

## Solución de Problemas

### Python no encontrado
- Reinstala Python marcando "Add to PATH"
- O usa la ruta completa: `C:\Python311\python.exe`

### Error de módulos
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### Error de permisos
- Ejecuta CMD como administrador
- O usa `--user`: `pip install --user -r requirements.txt`

## Comandos Útiles

```cmd
# Activar entorno virtual
venv\Scripts\activate

# Desactivar entorno virtual
deactivate

# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Ver logs en tiempo real
python app.py

# Probar solo la configuración
python test_bot.py
```

## Estructura del Proyecto

```
ScalpingTrader/
├── app.py              # Aplicación principal
├── config.py           # Configuración centralizada
├── test_bot.py         # Script de pruebas
├── requirements.txt    # Dependencias Python
├── render.yaml         # Configuración Render
├── Procfile           # Comando de inicio
├── runtime.txt        # Versión Python
├── README.md          # Documentación principal
├── DEPLOY_GUIDE.md    # Guía de despliegue
├── LOCAL_SETUP.md     # Esta guía
└── .env.example       # Ejemplo de variables
```

## ¿Problemas con la Instalación Local?

**¡No te preocupes!** El proyecto está diseñado para funcionar perfectamente en Render.com sin necesidad de instalación local.

**Salta directamente al despliegue**:
1. Sube el código a GitHub
2. Sigue la guía en `DEPLOY_GUIDE.md`
3. Tu bot estará funcionando en minutos

## Próximos Pasos

Una vez que tengas el bot funcionando localmente:

1. **Personaliza los parámetros** en `.env`
2. **Prueba diferentes símbolos** (ETHUSDT, ADAUSDT, etc.)
3. **Ajusta los rangos de RSI** según tu estrategia
4. **Monitorea los resultados** antes de usar con dinero real

---

**⚠️ Recuerda**: Este bot es solo para fines educativos. Nunca uses dinero real sin entender completamente los riesgos del trading.
