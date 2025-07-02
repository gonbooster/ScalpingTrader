# 🚀 ScalpingTrader - Professional Crypto Scalping Bot

[![Version](https://img.shields.io/badge/version-v4.4--ADVANCED--FILTERS-blue.svg)](https://github.com/gonbooster/ScalpingTrader)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Deployment](https://img.shields.io/badge/deploy-Koyeb-purple.svg)](https://koyeb.com)

A sophisticated cryptocurrency scalping bot that analyzes multiple trading pairs (BTC/ETH/SOL) using advanced technical indicators, sends professional HTML email alerts, and provides real-time market analysis with price targets.

## ✨ Features

### 🎯 **Advanced Trading Strategy**
- **Multi-timeframe analysis** (1m, 15m, 1h)
- **Adaptive parameters** per cryptocurrency type
- **Confidence scoring system** (0-100)
- **Anti-sideways market filters** with ADX
- **Breakout candle validation**
- **Minimum signal distance filtering**

### 📊 **Technical Indicators**
- **EMA Crossovers** (adaptive periods)
- **RSI Multi-timeframe** (1m + 15m confirmation)
- **Volume Analysis** (above average filtering)
- **ATR** (Average True Range) with exponential smoothing
- **ADX** (Average Directional Index) for trend detection
- **Macro trend analysis** for BTC pairs

### 📧 **Professional Email Alerts**
- **HTML email design** with responsive layout
- **Price targets calculation** (Take Profit & Stop Loss)
- **Risk/Reward ratio** analysis
- **Current candle percentage change**
- **Real-time market data** from Binance
- **Signal strength indicators**

### 🌐 **Web Dashboard**
- **Real-time monitoring** interface
- **Multi-pair overview** with live data
- **Signal history** and performance metrics
- **Health check endpoints** for monitoring
- **Professional UI** with crypto-themed design

### 🛡️ **Risk Management**
- **Geographic restrictions** handling (Binance API)
- **Signal filtering** to avoid false positives
- **Minimum time/price distance** between signals
- **ATR-based position sizing** recommendations
- **Trading hours filtering** (8-18 UTC optimal)

## 🏗️ Architecture

```
ScalpingTrader/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
└── bot_logs.txt          # Rotating logs (auto-managed)
```

## 📋 Prerequisites

- **Python 3.8+**
- **Gmail account** with App Password
- **Koyeb account** (free tier available)
- **UptimeRobot account** (optional, for 24/7 monitoring)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/gonbooster/ScalpingTrader.git
cd ScalpingTrader
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file or set environment variables:
```bash
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=recipient@gmail.com
```

### 4. Run Locally (Testing)
```bash
python app.py
```

### 5. Access Dashboard
Open `http://localhost:8000` in your browser

## 🔧 Detailed Setup Guide

### 📧 Gmail Configuration

#### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification**
3. Follow the setup process

#### Step 2: Generate App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and **Other (Custom name)**
3. Enter "ScalpingTrader" as the app name
4. Copy the generated 16-character password
5. Use this password in `EMAIL_PASSWORD` variable

#### Step 3: Test Email Configuration
Visit `https://your-app.koyeb.app/test-email` to verify email setup

### 🌐 Koyeb Deployment

#### Step 1: Create Koyeb Account
1. Visit [Koyeb.com](https://www.koyeb.com/)
2. Sign up for free account
3. Verify your email

#### Step 2: Deploy Application
1. **Create New Service**
   - Service Type: `Web Service`
   - Source: `GitHub` → Connect your repository
   - Branch: `main`

2. **Configure Build**
   - Builder: `Buildpack`
   - Build Command: (leave empty)
   - Run Command: `python app.py`

3. **Set Environment Variables**
   ```
   EMAIL_FROM=your-email@gmail.com
   EMAIL_PASSWORD=your-16-char-app-password
   EMAIL_TO=recipient@gmail.com
   ```

4. **Configure Instance**
   - Instance: `Free (0.1 vCPU, 512MB RAM)`
   - Region: `Frankfurt` (recommended for Binance API access)
   - Port: `8000`
   - Health Check: `TCP on port 8000`

5. **Deploy**
   - Click "Deploy"
   - Wait 3-5 minutes for deployment
   - Note your app URL: `https://your-app-name.koyeb.app`

#### Step 3: Verify Deployment
1. Visit your app URL
2. Check dashboard functionality
3. Test email alerts: `https://your-app.koyeb.app/test-email`

### 📊 UptimeRobot Monitoring (Optional)

#### Step 1: Create UptimeRobot Account
1. Visit [UptimeRobot.com](https://uptimerobot.com/)
2. Sign up for free account

#### Step 2: Add Monitor
1. **Create New Monitor**
   - Monitor Type: `HTTP(s)`
   - URL: `https://your-app.koyeb.app/health`
   - Monitoring Interval: `5 minutes`
   - Monitor Timeout: `30 seconds`

2. **Configure Alerts**
   - Email notifications on downtime
   - Optional: SMS alerts (paid feature)

#### Benefits
- **Keeps app awake** 24/7 (prevents cold starts)
- **Immediate downtime alerts**
- **Performance monitoring**
- **99.9% uptime tracking**

## 🎛️ Configuration Options

### Trading Parameters
The bot uses adaptive parameters based on cryptocurrency type:

#### Bitcoin (BTC) Pairs
- EMA Fast: 8, EMA Slow: 21
- RSI Range: 45-55
- ATR Multiplier: 2.5x (conservative)

#### Ethereum (ETH) Pairs
- EMA Fast: 10, EMA Slow: 21
- RSI Range: 40-60
- ATR Multiplier: 2.8x

#### Solana (SOL) Pairs
- EMA Fast: 12, EMA Slow: 26
- RSI Range: 35-65
- ATR Multiplier: 3.0x (aggressive)

### Signal Filters
- **ADX Minimum**: 20 (trend strength)
- **Volume Threshold**: 120% of average
- **Candle Body**: 60% dominance required
- **Time Distance**: 5 minutes minimum
- **Price Distance**: 1% minimum movement

## 📊 API Endpoints

### Public Endpoints
- `GET /` - Main dashboard
- `GET /health` - Health check (for monitoring)
- `GET /logs` - View recent logs
- `GET /logs-json` - Logs in JSON format
- `GET /test-email` - Test email configuration

### Dashboard Features
- **Real-time prices** from Binance API
- **Signal history** with timestamps
- **Confidence scores** for each pair
- **Market status** indicators
- **Performance metrics**

## 🔍 Monitoring & Logs

### Log Management
- **Automatic rotation** (max 500 lines)
- **Structured logging** with timestamps
- **Error tracking** and debugging info
- **Signal history** with details

### Key Metrics
- **Signal count** (total alerts sent)
- **Confidence scores** (0-100 scale)
- **Market data** (prices, volumes, indicators)
- **Filter status** (ADX, breakout, distance)

## ⚠️ Important Notes

### Geographic Restrictions
- **Binance API** may be restricted in some regions
- **Koyeb Frankfurt** region recommended for EU access
- **VPN solutions** may be required for restricted areas

### Risk Disclaimer
- **Educational purposes only**
- **Not financial advice**
- **Always manage risk responsibly**
- **Test with small amounts first**

### Performance Optimization
- **Real data only** (no simulation in production)
- **60-second analysis intervals**
- **Efficient API usage** (respects rate limits)
- **Memory-optimized** log rotation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues
1. **Email not working**: Check App Password configuration
2. **Binance API errors**: Verify geographic access
3. **App sleeping**: Set up UptimeRobot monitoring
4. **Deployment fails**: Check environment variables

### Getting Help
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check this README for setup guides
- **Email Testing**: Use `/test-email` endpoint

## 🎯 Roadmap

- [ ] **Telegram notifications** integration
- [ ] **Multiple exchange** support (Coinbase, Kraken)
- [ ] **Backtesting** functionality
- [ ] **Portfolio tracking** features
- [ ] **Mobile app** companion

---

**⚡ Built with Python, Flask, and professional trading strategies**

**🚀 Deploy in minutes, trade in seconds**
