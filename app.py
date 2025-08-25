from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import requests
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
import joblib
from datetime import datetime, timedelta
import json
from languages import COMPREHENSIVE_TRANSLATIONS, INDIAN_LANGUAGES, get_translation, get_supported_languages
import threading
import time

app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

# Global variables
predictor = None
model_loaded = False
weather_cache = {}
location_cache = {}

# Multi-language support
# Use comprehensive translations from languages.py
TRANSLATIONS = COMPREHENSIVE_TRANSLATIONS

def load_ml_model():
    """Load the trained ML model"""
    global predictor, model_loaded
    try:
        if os.path.exists('crop_yield_model.pkl'):
            predictor = joblib.load('crop_yield_model.pkl')
            model_loaded = True
            print("ML Model loaded successfully")
        else:
            print("ML Model file not found")
            model_loaded = False
    except Exception as e:
        print(f"Error loading ML model: {e}")
        model_loaded = False

def get_weather_data(lat, lon, api_key):
    """Fetch weather data from OpenWeatherMap"""
    try:
        # Current weather
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        current_response = requests.get(current_url)
        current_data = current_response.json()
        
        # 7-day forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()
        
        return {
            'current': current_data,
            'forecast': forecast_data,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def analyze_weather_alerts(weather_data, language='en'):
    """Analyze weather data for alerts"""
    alerts = []
    
    if not weather_data or 'current' not in weather_data:
        return alerts
    
    current = weather_data['current']
    forecast = weather_data.get('forecast', {})
    
    # Temperature alerts
    temp = current.get('main', {}).get('temp', 0)
    if temp > 35:
        alerts.append({
            'type': 'heat_stress',
            'severity': 'high',
            'message': LANGUAGES[language]['heat_stress'],
            'icon': 'fas fa-sun',
            'color': 'red'
        })
    
    # Rain alerts
    if 'list' in forecast:
        for item in forecast['list'][:8]:  # Next 24 hours
            if 'rain' in item:
                hours = (datetime.fromtimestamp(item['dt']) - datetime.now()).total_seconds() / 3600
                if hours <= 2:
                    alerts.append({
                        'type': 'rain',
                        'severity': 'medium',
                        'message': LANGUAGES[language]['rain_expected'].format(hours=int(hours)),
                        'icon': 'fas fa-cloud-rain',
                        'color': 'blue'
                    })
                    break
    
    # Drought conditions
    humidity = current.get('main', {}).get('humidity', 100)
    if humidity < 30 and temp > 30:
        alerts.append({
            'type': 'drought',
            'severity': 'high',
            'message': LANGUAGES[language]['drought_warning'],
            'icon': 'fas fa-sun',
            'color': 'orange'
        })
    
    return alerts

def calculate_crop_suitability(crop, weather_data, soil_data):
    """Calculate crop suitability percentage"""
    if not weather_data or not model_loaded:
        return 50  # Default
    
    try:
        temp = weather_data['current']['main']['temp']
        humidity = weather_data['current']['main']['humidity']
        
        # Simplified suitability calculation
        temp_score = max(0, 100 - abs(temp - 25) * 2)  # Optimal at 25°C
        humidity_score = max(0, 100 - abs(humidity - 60) * 1.5)  # Optimal at 60%
        
        # Soil factors
        ph_score = max(0, 100 - abs(soil_data.get('ph', 6.5) - 6.5) * 20)
        
        overall_score = (temp_score + humidity_score + ph_score) / 3
        return min(100, max(0, overall_score))
    except:
        return 50

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get all supported languages"""
    return jsonify({
        'languages': get_supported_languages(),
        'total_count': len(get_supported_languages())
    })

@app.route('/api/location', methods=['POST'])
def detect_location():
    """Detect user location and return region info"""
    try:
        data = request.json
        lat = data.get('latitude')
        lon = data.get('longitude')
        
        if not lat or not lon:
            return jsonify({'error': 'Missing coordinates'}), 400
        
        # Use Nominatim for reverse geocoding
        geolocator = Nominatim(user_agent="agripredict")
        location = geolocator.reverse(f"{lat}, {lon}")
        
        if location:
            address = location.raw.get('address', {})
            region = address.get('state', 'Unknown')
            district = address.get('county', 'Unknown')
            
            return jsonify({
                'region': region,
                'district': district,
                'latitude': lat,
                'longitude': lon,
                'address': location.address
            })
        else:
            return jsonify({'error': 'Location not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get current weather and forecast"""
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        api_key = os.getenv('OPENWEATHER_API_KEY')
        
        if not api_key:
            return jsonify({'error': 'Weather API key not configured'}), 500
        
        if not lat or not lon:
            return jsonify({'error': 'Missing coordinates'}), 400
        
        # Check cache
        cache_key = f"{lat},{lon}"
        if cache_key in weather_cache:
            cached_data = weather_cache[cache_key]
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cache_time < timedelta(minutes=10):
                return jsonify(cached_data)
        
        # Fetch new data
        weather_data = get_weather_data(lat, lon, api_key)
        if weather_data:
            weather_cache[cache_key] = weather_data
            return jsonify(weather_data)
        else:
            return jsonify({'error': 'Weather data unavailable'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get weather and farming alerts"""
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        language = request.args.get('lang', 'en')
        api_key = os.getenv('OPENWEATHER_API_KEY')
        
        if not api_key:
            return jsonify({'error': 'Weather API key not configured'}), 500
        
        if not lat or not lon:
            return jsonify({'error': 'Missing coordinates'}), 400
        
        weather_data = get_weather_data(lat, lon, api_key)
        alerts = analyze_weather_alerts(weather_data, language)
        
        return jsonify({
            'alerts': alerts,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crop-suitability', methods=['POST'])
def crop_suitability():
    """Calculate crop suitability for given conditions"""
    try:
        data = request.json
        crop = data.get('crop')
        lat = data.get('latitude')
        lon = data.get('longitude')
        soil_data = data.get('soil', {})
        language = data.get('language', 'en')
        
        if not crop or not lat or not lon:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Get weather data
        api_key = os.getenv('OPENWEATHER_API_KEY', 'demo_key')
        weather_data = get_weather_data(lat, lon, api_key)
        
        # Calculate suitability
        suitability = calculate_crop_suitability(crop, weather_data, soil_data)
        
        # Determine category
        if suitability >= 80:
            category = 'excellent'
            color = 'green'
        elif suitability >= 60:
            category = 'good'
            color = 'lightgreen'
        elif suitability >= 40:
            category = 'moderate'
            color = 'yellow'
        elif suitability >= 20:
            category = 'poor'
            color = 'orange'
        else:
            category = 'very_poor'
            color = 'red'
        
        return jsonify({
            'crop': crop,
            'suitability_percentage': round(suitability, 1),
            'category': category,
            'category_text': LANGUAGES[language][category],
            'color': color,
            'message': LANGUAGES[language]['crop_suitable'].format(percentage=round(suitability, 1))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-yield', methods=['POST'])
def predict_yield():
    """Predict crop yield using ML model"""
    try:
        data = request.json
        
        if not model_loaded or predictor is None:
            return jsonify({'error': 'ML model not available'}), 500
        
        # Extract parameters
        region = data.get('region', 'Maharashtra')
        crop = data.get('crop', 'Wheat')
        year = data.get('year', 2024)
        temperature = float(data.get('temperature', 25))
        rainfall = float(data.get('rainfall', 1000))
        soil_ph = float(data.get('soil_ph', 6.5))
        nitrogen = float(data.get('nitrogen', 50))
        phosphorus = float(data.get('phosphorus', 30))
        potassium = float(data.get('potassium', 40))
        organic_matter = float(data.get('organic_matter', 2.5))
        irrigation_quality = int(data.get('irrigation_quality', 3))
        
        # Use real ML model for prediction
        model = predictor['model']
        region_encoder = predictor['region_encoder']
        crop_encoder = predictor['crop_encoder']
        regions = predictor['regions']
        crops = predictor['crops']
        
        # Encode inputs
        if region in regions:
            region_encoded = region_encoder.transform([region])[0]
        else:
            region_encoded = 0  # Default to first region
            
        if crop in crops:
            crop_encoded = crop_encoder.transform([crop])[0]
        else:
            crop_encoded = 0  # Default to first crop
        
        # Prepare input features
        X_input = [[region_encoded, crop_encoded, year, temperature, rainfall, 
                   soil_ph, nitrogen, phosphorus, potassium, organic_matter, irrigation_quality]]
        
        # Make prediction using real ML model
        predicted_yield = model.predict(X_input)[0]
        
        # Calculate confidence and impact factors
        weather_score = min(100, max(0, 100 - abs(temperature - 25) * 2 - abs(rainfall - 1000) * 0.05))
        soil_score = min(100, max(0, 100 - abs(soil_ph - 6.5) * 10))
        irrigation_score = irrigation_quality * 20
        
        confidence = 'High' if weather_score > 70 and soil_score > 70 else 'Medium' if weather_score > 50 else 'Low'
        
        return jsonify({
            'predicted_yield': round(predicted_yield, 2),
            'unit': 'kg/hectare',
            'confidence': confidence,
            'factors': {
                'weather_impact': 'Good' if weather_score > 70 else 'Moderate' if weather_score > 50 else 'Poor',
                'soil_impact': 'Good' if soil_score > 70 else 'Moderate' if soil_score > 50 else 'Poor',
                'irrigation_impact': 'Excellent' if irrigation_quality >= 4 else 'Good' if irrigation_quality >= 3 else 'Adequate'
            },
            'model_used': 'Real ML Model (Random Forest)',
            'data_source': 'Trained on synthetic agricultural data'
        })
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': 'Prediction failed'}), 500

@app.route('/api/voice-summary', methods=['POST'])
def voice_summary():
    """Generate comprehensive voice summary of screen content"""
    try:
        data = request.json
        language = data.get('language', 'en')
        screen_content = data.get('screen_content', {})
        
        # Build comprehensive summary
        summary_parts = []
        
        # Current section
        section = screen_content.get('section', 'dashboard')
        section_name = get_translation(language, section, 'en')
        summary_parts.append(f"Current section: {section_name}.")
        
        # Weather information
        weather = screen_content.get('weather')
        if weather:
            temp = weather.get('temperature', 'N/A')
            desc = weather.get('description', 'N/A')
            if language == 'hi':
                summary_parts.append(f"वर्तमान तापमान {temp} डिग्री है। मौसम {desc} है।")
            elif language == 'mr':
                summary_parts.append(f"सध्याचे तापमान {temp} अंश आहे। हवामान {desc} आहे।")
            else:
                summary_parts.append(f"Current temperature is {temp} degrees. Weather is {desc}.")
        
        # Alerts
        alerts = screen_content.get('alerts', [])
        if alerts:
            alert_count = len(alerts)
            if language == 'hi':
                summary_parts.append(f"{alert_count} मौसम चेतावनी सक्रिय हैं।")
            elif language == 'mr':
                summary_parts.append(f"{alert_count} हवामान इशारे सक्रिय आहेत।")
            else:
                summary_parts.append(f"{alert_count} weather alerts are active.")
        
        # Crop prediction
        prediction = screen_content.get('crop_prediction')
        if prediction:
            yield_val = prediction.get('predicted_yield', 'N/A')
            if language == 'hi':
                summary_parts.append(f"अनुमानित फसल उत्पादन {yield_val} किलो प्रति हेक्टेयर है।")
            elif language == 'mr':
                summary_parts.append(f"अंदाजित पीक उत्पादन {yield_val} किलो प्रति हेक्टर आहे।")
            else:
                summary_parts.append(f"Predicted crop yield is {yield_val} kilograms per hectare.")
        
        # Location
        location = screen_content.get('location')
        if location:
            city = location.get('city', 'Unknown')
            if language == 'hi':
                summary_parts.append(f"स्थान: {city}।")
            elif language == 'mr':
                summary_parts.append(f"स्थान: {city}।")
            else:
                summary_parts.append(f"Location: {city}.")
        
        # Combine all parts
        full_summary = " ".join(summary_parts)
        
        return jsonify({
            'summary': full_summary,
            'language': language,
            'sections_covered': len(summary_parts)
        })
        
    except Exception as e:
        print(f"Voice summary error: {e}")
        return jsonify({'error': 'Voice summary generation failed'}), 500

@app.route('/api/notifications/subscribe', methods=['POST'])
def subscribe_notifications():
    """Subscribe to push notifications"""
    try:
        data = request.json
        # In a real implementation, you would store subscription data
        # and use services like Firebase Cloud Messaging
        
        return jsonify({
            'status': 'subscribed',
            'message': 'Successfully subscribed to notifications'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize ML model on startup
def initialize():
    """Initialize the application"""
    load_ml_model()

# Initialize on startup
with app.app_context():
    initialize()

if __name__ == '__main__':
    # For deployment - use PORT environment variable
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)

# For serverless deployment
application = app
