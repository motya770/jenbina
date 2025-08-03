#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import os
from dataclasses import dataclass
import random
from location_system import PaloAltoLocationSystem
from dynamic_events import DynamicEventsSystem

@dataclass
class WeatherData:
    temperature: float
    humidity: float
    description: str
    wind_speed: float
    pressure: float
    visibility: float
    sunrise: str
    sunset: str
    timestamp: datetime

@dataclass
class TimeData:
    current_time: datetime
    day_of_week: str
    is_daytime: bool
    time_of_day: str  # morning, afternoon, evening, night
    season: str
    moon_phase: str

@dataclass
class EnvironmentState:
    weather: WeatherData
    time: TimeData
    location: str
    events: list
    mood_factors: Dict[str, float]

class EnvironmentSimulator:
    """Simulates a realistic environment for Jenbina"""
    
    def __init__(self, location: str = "Palo Alto, CA", api_keys: Dict[str, str] = None):
        self.location = location
        self.api_keys = api_keys or {}
        self.base_weather_data = None
        self.last_update = None
        self.update_interval = 300  # 5 minutes
        
        # Initialize location system
        self.location_system = PaloAltoLocationSystem()
        
        # Initialize dynamic events system
        self.events_system = DynamicEventsSystem()
        
        # Fallback data for when APIs are unavailable
        self.fallback_weather = {
            "temperature": 20.0,
            "humidity": 65.0,
            "description": "Partly cloudy",
            "wind_speed": 5.0,
            "pressure": 1013.0,
            "visibility": 10.0,
            "sunrise": "06:30",
            "sunset": "19:30"
        }
        
        # Initialize with current time
        self.update_time_data()
    
    def get_weather_data(self) -> WeatherData:
        """Get current weather data (real or simulated)"""
        current_time = datetime.now()
        
        # Update if needed
        if (self.last_update is None or 
            (current_time - self.last_update).seconds > self.update_interval):
            self._update_weather_data()
        
        if self.base_weather_data:
            return self.base_weather_data
        else:
            # Return simulated weather based on time and season
            return self._simulate_weather()
    
    def _update_weather_data(self):
        """Try to get real weather data, fallback to simulation"""
        try:
            # Try to get real weather data (if API key available)
            if 'openweathermap' in self.api_keys:
                self.base_weather_data = self._fetch_real_weather()
            else:
                self.base_weather_data = self._simulate_weather()
        except Exception as e:
            print(f"Weather API error: {e}")
            self.base_weather_data = self._simulate_weather()
        
        self.last_update = datetime.now()
    
    def _fetch_real_weather(self) -> WeatherData:
        """Fetch real weather data from OpenWeatherMap"""
        api_key = self.api_keys['openweathermap']
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': self.location,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        return WeatherData(
            temperature=data['main']['temp'],
            humidity=data['main']['humidity'],
            description=data['weather'][0]['description'],
            wind_speed=data['wind']['speed'],
            pressure=data['main']['pressure'],
            visibility=data.get('visibility', 10000) / 1000,  # Convert to km
            sunrise=datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
            sunset=datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
            timestamp=datetime.now()
        )
    
    def _simulate_weather(self) -> WeatherData:
        """Simulate realistic weather based on time and season"""
        current_time = datetime.now()
        hour = current_time.hour
        month = current_time.month
        
        # Seasonal temperature variations
        base_temp = 20.0
        if month in [12, 1, 2]:  # Winter
            base_temp = 2.0
        elif month in [3, 4, 5]:  # Spring
            base_temp = 15.0
        elif month in [6, 7, 8]:  # Summer
            base_temp = 25.0
        elif month in [9, 10, 11]:  # Fall
            base_temp = 15.0
        
        # Daily temperature cycle
        temp_variation = 8.0 * (1 - abs(hour - 12) / 12)
        temperature = base_temp + temp_variation + random.uniform(-2, 2)
        
        # Weather conditions based on time and temperature
        if temperature < 5:
            description = "Cold and clear"
            humidity = random.uniform(40, 60)
        elif temperature > 25:
            description = "Warm and sunny"
            humidity = random.uniform(30, 50)
        else:
            descriptions = ["Partly cloudy", "Sunny", "Light breeze", "Clear skies"]
            description = random.choice(descriptions)
            humidity = random.uniform(50, 70)
        
        # Simulate sunrise/sunset times
        sunrise_hour = 6 + random.uniform(-0.5, 0.5)
        sunset_hour = 19 + random.uniform(-0.5, 0.5)
        
        return WeatherData(
            temperature=round(temperature, 1),
            humidity=round(humidity, 1),
            description=description,
            wind_speed=round(random.uniform(2, 8), 1),
            pressure=round(random.uniform(1000, 1020), 1),
            visibility=round(random.uniform(8, 12), 1),
            sunrise=f"{int(sunrise_hour):02d}:{int((sunrise_hour % 1) * 60):02d}",
            sunset=f"{int(sunset_hour):02d}:{int((sunset_hour % 1) * 60):02d}",
            timestamp=current_time
        )
    
    def update_time_data(self):
        """Update time-related data"""
        current_time = datetime.now()
        
        # Determine time of day
        hour = current_time.hour
        if 6 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Determine season
        month = current_time.month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "autumn"
        
        # Determine if it's daytime
        weather = self.get_weather_data()
        sunrise_hour = int(weather.sunrise.split(':')[0])
        sunset_hour = int(weather.sunset.split(':')[0])
        is_daytime = sunrise_hour <= hour <= sunset_hour
        
        # Moon phases (simplified)
        moon_phases = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", 
                      "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
        moon_phase = moon_phases[(current_time.day % 8)]
        
        self.time_data = TimeData(
            current_time=current_time,
            day_of_week=current_time.strftime('%A'),
            is_daytime=is_daytime,
            time_of_day=time_of_day,
            season=season,
            moon_phase=moon_phase
        )
    
    def get_environment_state(self) -> EnvironmentState:
        """Get complete environment state"""
        self.update_time_data()
        weather = self.get_weather_data()
        
        # Calculate mood factors based on environment
        mood_factors = self._calculate_mood_factors(weather, self.time_data)
        
        # Get local events and location-based activities
        events = self._get_local_events()
        
        # Get dynamic events from APIs
        dynamic_events = self.events_system.get_events(date_range=7)
        if dynamic_events:
            events.extend([f"{event.name} at {event.location} ({event.price})" for event in dynamic_events[:3]])
        
        # Get location-based activity suggestion
        activity_suggestion = self.location_system.get_daily_activity_suggestion()
        
        return EnvironmentState(
            weather=weather,
            time=self.time_data,
            location=self.location,
            events=events,
            mood_factors=mood_factors
        )
    
    def _calculate_mood_factors(self, weather: WeatherData, time: TimeData) -> Dict[str, float]:
        """Calculate how environment affects mood"""
        factors = {}
        
        # Temperature comfort (0-1, 1 being most comfortable)
        if 18 <= weather.temperature <= 24:
            factors['temperature_comfort'] = 1.0
        elif 15 <= weather.temperature <= 27:
            factors['temperature_comfort'] = 0.8
        else:
            factors['temperature_comfort'] = 0.4
        
        # Light levels
        if time.is_daytime:
            factors['light_level'] = 1.0
        elif time.time_of_day == "evening":
            factors['light_level'] = 0.6
        else:
            factors['light_level'] = 0.2
        
        # Weather mood
        if "sunny" in weather.description.lower():
            factors['weather_mood'] = 1.0
        elif "cloudy" in weather.description.lower():
            factors['weather_mood'] = 0.7
        elif "rain" in weather.description.lower():
            factors['weather_mood'] = 0.4
        else:
            factors['weather_mood'] = 0.8
        
        # Seasonal comfort
        if time.season in ["spring", "autumn"]:
            factors['seasonal_comfort'] = 1.0
        elif time.season == "summer":
            factors['seasonal_comfort'] = 0.8
        else:
            factors['seasonal_comfort'] = 0.6
        
        return factors
    
    def _get_local_events(self) -> list:
        """Get local events based on Palo Alto location system"""
        events = []
        current_time = datetime.now()
        
        # Get open locations and popular activities
        open_locations = self.location_system.get_open_locations(current_time)
        popular_locations = self.location_system.get_popular_locations(0.7)
        
        # Add location-based events
        if open_locations:
            # Add a popular open location as an event
            for location in popular_locations:
                if location in open_locations:
                    events.append(f"{location.name} is open and popular")
                    break
        
        # Time-based events
        if current_time.hour == 12:
            events.append("Lunch time - restaurants in University Avenue are busy")
        
        if current_time.hour == 18:
            events.append("Evening rush - people heading to Santana Row and downtown")
        
        if current_time.weekday() == 5:  # Saturday
            events.append("Weekend shopping at Stanford Shopping Center")
        
        if current_time.month == 12:
            events.append("Holiday season - festive decorations in downtown Palo Alto")
        
        return events
    
    def get_environment_description(self) -> str:
        """Get a natural language description of the current environment"""
        state = self.get_environment_state()
        
        description_parts = []
        
        # Time description
        time_desc = f"It's {state.time.time_of_day} on a {state.time.day_of_week.lower()}"
        if state.time.is_daytime:
            time_desc += " and the sun is shining"
        else:
            time_desc += " and the stars are visible"
        description_parts.append(time_desc)
        
        # Weather description
        weather_desc = f"The weather is {state.weather.description.lower()}"
        weather_desc += f" with a temperature of {state.weather.temperature}°C"
        if state.weather.humidity > 70:
            weather_desc += " and it feels quite humid"
        elif state.weather.humidity < 40:
            weather_desc += " and the air is quite dry"
        description_parts.append(weather_desc)
        
        # Location context with Palo Alto details
        location_desc = f"We're in {state.location}, a vibrant tech hub in the heart of Silicon Valley"
        description_parts.append(location_desc)
        
        # Events
        if state.events:
            events_desc = f"Currently, {', '.join(state.events).lower()}"
            description_parts.append(events_desc)
        
        return ". ".join(description_parts) + "."
    
    def get_dynamic_recommendations(self, mood: str = None) -> Dict[str, any]:
        """Get dynamic recommendations based on current mood and environment"""
        recommendations = self.events_system.get_recommendations(mood=mood, max_price="$$$")
        
        # Add location-based recommendations
        location_recommendation = self.location_system.get_recommendation(mood=mood, max_price="$$$")
        if location_recommendation:
            recommendations['location'] = location_recommendation
        
        return recommendations
    
    def get_today_highlights(self) -> List[str]:
        """Get today's highlights including dynamic events"""
        highlights = self.events_system.get_today_highlights()
        
        # Add location-based highlights
        open_locations = self.location_system.get_open_locations()
        if open_locations:
            highlights.append(f"Open locations: {len(open_locations)} places currently open")
        
        return highlights

# Example usage
if __name__ == "__main__":
    # Initialize with optional API keys
    api_keys = {
        # 'openweathermap': 'your_api_key_here'  # Uncomment and add your key
    }
    
    simulator = EnvironmentSimulator("Palo Alto, CA", api_keys)
    
    # Get current environment state
    state = simulator.get_environment_state()
    
    print("🌍 Current Environment State:")
    print(f"Location: {state.location}")
    print(f"Time: {state.time.current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Day: {state.time.day_of_week}, {state.time.time_of_day}")
    print(f"Weather: {state.weather.description}, {state.weather.temperature}°C")
    print(f"Humidity: {state.weather.humidity}%")
    print(f"Season: {state.time.season}")
    print(f"Events: {state.events}")
    print(f"Mood Factors: {state.mood_factors}")
    print()
    print("📝 Natural Description:")
    print(simulator.get_environment_description()) 