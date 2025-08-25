# 🌾 AgriPredict - Smart Crop Yield Forecasting System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0+-orange.svg)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive AI-powered agricultural platform that provides real-time weather monitoring, crop yield predictions, and farming insights with **9 Indian languages** support and intelligent voice assistance.

## 🌟 Features

### Core Functionalities
- **User Current Location**: Automatic location detection for region-specific forecasts
- **Real-time Weather Integration**: Live weather data + 7-day forecast from OpenWeatherMap API
- **Push Notifications**: Early warnings 1-2 hours before climate changes (rain, drought, flood, heat stress)
- **Multi-Language Support**: Full website + voice alerts in 9 Indian languages
- **🗣️ Voice Assistant**: Smart crop recommendations with weather-based suggestions
- **Crop Suitability Prediction**: AI-based analysis with soil values (NPK, pH) + weather conditions
- **Visual Predictions**: Color-coded indicators (red/yellow/green) for farmer-friendly results
- **Voice Summarization**: Text-to-speech in farmer's chosen language for accessibility

### Advanced Features
- **ML-Powered Yield Prediction**: Random Forest and Gradient Boosting models
- **Interactive Dashboard**: Real-time monitoring with charts and visualizations
- **Weather Alerts System**: Automated notifications for weather changes
- **Crop Suitability Analysis**: Percentage-based suitability scoring
- **Regional Adaptation**: Customized for Indian agricultural regions

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- OpenWeatherMap API key (free from https://openweathermap.org/api)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd Ok
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenWeatherMap API key
   ```

5. **Start the application:**
   ```bash
   # Option 1: Start both servers simultaneously
   npm run dev-all
   
   # Option 2: Start servers separately
   # Terminal 1 - Node.js server
   npm run dev
   
   # Terminal 2 - Flask API server
   npm run flask
   ```

6. **Access the application:**
   - Frontend: http://localhost:3000
   - Flask API: http://localhost:5000

## 🏗️ Architecture

### Frontend (Node.js + Express)
- **index.html**: Clean, responsive UI with all requested features
- **server.js**: Express server for static files and API proxying
- **Real-time Updates**: Weather data refreshes every 5 minutes
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Backend (Python Flask)
- **app.py**: Main Flask application with all API endpoints
- **CropYieldPredictor.py**: ML model for crop yield predictions
- **Multi-language Support**: API responses in English, Hindi, Marathi
- **Location Services**: Automatic region detection using geolocation

### API Endpoints
- `GET /api/health` - System health check
- `POST /api/location` - Detect user location
- `GET /api/weather` - Current weather and forecast
- `GET /api/alerts` - Weather and farming alerts
- `POST /api/crop-suitability` - Crop suitability analysis
- `POST /api/predict-yield` - ML-powered yield prediction
- `GET /api/voice-summary` - Voice summary data

## 🎯 Usage Guide

### Dashboard
- **Location Detection**: Automatically detects farmer's location
- **Weather Cards**: Real-time temperature, humidity, and weather conditions
- **7-Day Forecast**: Extended weather predictions
- **Alert System**: Active alerts with color-coded severity

### Crop Prediction
- **Input Parameters**: Soil pH, NPK values, organic matter, irrigation quality
- **AI Prediction**: ML model provides yield estimates in tons/hectare
- **Confidence Levels**: High/Medium/Low confidence indicators
- **Recommendations**: Actionable advice based on predictions

### Crop Suitability
- **Percentage Scoring**: 0-100% suitability for selected crops
- **Visual Indicators**: Color-coded status (excellent/good/moderate/poor)
- **Real-time Analysis**: Based on current weather and soil conditions

### Voice Assistant
- **Click to Activate**: Floating voice button for audio summaries
- **Multi-language**: Speaks in selected language (English/Hindi/Marathi)
- **Weather Summary**: Current conditions and alerts
- **Accessibility**: Helps illiterate or semi-literate users

## 🌍 Multi-Language Support

The system supports three languages:
- **English**: Default language
- **Hindi (हिंदी)**: Full translation of UI and voice
- **Marathi (मराठी)**: Complete regional language support

Language can be changed from the top navigation dropdown.

## 🔧 Configuration

### Environment Variables
```bash
OPENWEATHER_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### Weather API Setup
1. Register at https://openweathermap.org/api
2. Get your free API key
3. Add it to your `.env` file
4. API provides current weather + 5-day forecast

## 📱 Features in Detail

### Real-time Weather Integration
- Current temperature, humidity, weather conditions
- 7-day forecast with daily predictions
- Weather alerts for extreme conditions
- Automatic updates every 5 minutes

### Push Notifications
- Early warnings 1-2 hours before weather changes
- Drought, flood, heat stress, and pest risk alerts
- Browser notifications with actionable information
- Multi-language alert messages

### Crop Suitability Analysis
- Analyzes soil pH, NPK levels, weather conditions
- Provides percentage-based suitability scores
- Visual color indicators for quick understanding
- Recommendations for crop optimization

### Voice Summarization
- Text-to-speech in farmer's chosen language
- Weather summary, alerts, and predictions
- Accessibility feature for all literacy levels
- Click-to-activate floating voice assistant

## 🎨 Visual Design

- **Clean Interface**: Farmer-friendly design with intuitive navigation
- **Color-coded Results**: Green (excellent), Yellow (moderate), Red (poor)
- **Responsive Layout**: Works on all device sizes
- **Visual Indicators**: Status dots, progress bars, and charts
- **Modern UI**: Professional agricultural theme

## 🔄 Data Flow

1. **Location Detection**: GPS coordinates → Region identification
2. **Weather Data**: OpenWeatherMap API → Real-time conditions
3. **ML Processing**: User inputs → Trained models → Predictions
4. **Visual Display**: Results → Color-coded UI → Voice output
5. **Alerts**: Weather monitoring → Early warnings → Notifications

## 🛠️ Development

### Adding New Features
1. Update the appropriate section (frontend/backend)
2. Add new API endpoints in `app.py`
3. Update UI components in `index.html`
4. Test with different languages and locations

### ML Model Training
The system includes a pre-trained model, but you can retrain:
```python
python CropYieldPredictor.py
```

### Testing
- Test location detection with different coordinates
- Verify weather API integration
- Check multi-language functionality
- Test voice features across browsers

## 📊 Technical Specifications

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python Flask, Node.js Express
- **ML Models**: Random Forest, Gradient Boosting
- **APIs**: OpenWeatherMap, Geolocation
- **Languages**: English, Hindi, Marathi
- **Responsive**: Mobile-first design
- **Voice**: Web Speech API

## 🎯 Target Users

- **Farmers**: Primary users needing crop guidance
- **Agricultural Advisors**: Professionals providing recommendations
- **Rural Communities**: Areas with limited internet connectivity
- **Multi-lingual Users**: Hindi and Marathi speaking farmers

## 🔒 Security & Privacy

- **Location Data**: Used only for weather/region detection
- **API Keys**: Stored securely in environment variables
- **No Personal Data**: System doesn't store personal information
- **HTTPS Ready**: Secure communication protocols

## 📈 Future Enhancements

- **Satellite Imagery**: Integration with Google Earth Engine
- **IoT Sensors**: Real-time soil and crop monitoring
- **Market Prices**: Crop price predictions and trends
- **Expert Chat**: Connect with agricultural experts
- **Offline Mode**: Basic functionality without internet

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenWeatherMap for weather data API
- Scikit-learn for machine learning capabilities
- Font Awesome for icons
- Chart.js for data visualizations

---

**AgriPredict** - Empowering farmers with AI-driven agricultural insights 🌾🤖
