"""core/services/weather.py — OpenWeather API Integration"""
import streamlit as st
import random
from typing import Dict, Any


@st.cache_data(ttl=900)
def get_vessel_weather(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch weather information for a given coordinate.
    In phase 2, this is a mock returning plausible marine weather.
    For production, integrate with OpenWeatherMap Marine API.
    """
    conditions = ["Clear", "Clouds", "Rain", "Windy", "Storm"]
    cond = random.choices(conditions, weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
    
    icons = {
        "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", 
        "Windy": "💨", "Storm": "⛈️"
    }

    return {
        "condition": cond,
        "icon": icons[cond],
        "temperature": round(random.uniform(25.0, 32.0), 1),
        "wind_speed": round(random.uniform(5.0, 25.0), 1), # knots
        "wind_deg": random.randint(0, 359),
        "wave_height": round(random.uniform(0.5, 3.5), 1) # meters
    }
