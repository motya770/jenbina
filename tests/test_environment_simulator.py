"""Tests for core/environment/environment_simulator.py."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from core.environment.environment_simulator import (
    EnvironmentSimulator,
    WeatherData,
    TimeData,
    EnvironmentState,
)


class TestWeatherData(unittest.TestCase):
    """Tests for the WeatherData dataclass."""

    def test_creation(self):
        wd = WeatherData(
            temperature=22.5,
            humidity=65.0,
            description="Sunny",
            wind_speed=5.0,
            pressure=1013.0,
            visibility=10.0,
            sunrise="06:30",
            sunset="19:30",
            timestamp=datetime.now(),
        )
        self.assertEqual(wd.temperature, 22.5)
        self.assertEqual(wd.description, "Sunny")


class TestTimeData(unittest.TestCase):
    """Tests for the TimeData dataclass."""

    def test_creation(self):
        td = TimeData(
            current_time=datetime.now(),
            day_of_week="Monday",
            is_daytime=True,
            time_of_day="morning",
            season="spring",
            moon_phase="Full Moon",
        )
        self.assertEqual(td.day_of_week, "Monday")
        self.assertTrue(td.is_daytime)


class TestEnvironmentSimulator(unittest.TestCase):
    """Tests for EnvironmentSimulator."""

    def setUp(self):
        # Patch the location and events systems to avoid real API calls
        with patch(
            "core.environment.environment_simulator.PaloAltoLocationSystem"
        ) as mock_loc, patch(
            "core.environment.environment_simulator.DynamicEventsSystem"
        ) as mock_events:
            mock_loc.return_value = MagicMock()
            mock_loc.return_value.get_open_locations.return_value = []
            mock_loc.return_value.get_popular_locations.return_value = []
            mock_loc.return_value.get_daily_activity_suggestion.return_value = "Go for a walk"
            mock_loc.return_value.get_recommendation.return_value = None

            mock_events.return_value = MagicMock()
            mock_events.return_value.get_events.return_value = []
            mock_events.return_value.get_recommendations.return_value = {}
            mock_events.return_value.get_today_highlights.return_value = []

            self.simulator = EnvironmentSimulator("Palo Alto, CA")
            self.mock_loc = mock_loc
            self.mock_events = mock_events

    def test_default_location(self):
        self.assertEqual(self.simulator.location, "Palo Alto, CA")

    def test_simulate_weather_returns_weather_data(self):
        weather = self.simulator._simulate_weather()
        self.assertIsInstance(weather, WeatherData)
        self.assertIsInstance(weather.temperature, float)
        self.assertIsInstance(weather.humidity, float)
        self.assertTrue(len(weather.description) > 0)

    def test_simulate_weather_temperature_range(self):
        weather = self.simulator._simulate_weather()
        # Temperature should be within a reasonable range
        self.assertGreaterEqual(weather.temperature, -15.0)
        self.assertLessEqual(weather.temperature, 45.0)

    def test_get_weather_data(self):
        weather = self.simulator.get_weather_data()
        self.assertIsInstance(weather, WeatherData)

    def test_update_time_data(self):
        self.simulator.update_time_data()
        self.assertIsNotNone(self.simulator.time_data)
        self.assertIsInstance(self.simulator.time_data, TimeData)
        self.assertIn(self.simulator.time_data.time_of_day,
                      ["morning", "afternoon", "evening", "night"])
        self.assertIn(self.simulator.time_data.season,
                      ["winter", "spring", "summer", "autumn"])

    def test_calculate_mood_factors(self):
        weather = WeatherData(
            temperature=22.0, humidity=60.0, description="Sunny",
            wind_speed=5.0, pressure=1013.0, visibility=10.0,
            sunrise="06:30", sunset="19:30", timestamp=datetime.now(),
        )
        time = TimeData(
            current_time=datetime.now(), day_of_week="Monday",
            is_daytime=True, time_of_day="morning",
            season="spring", moon_phase="Full Moon",
        )
        factors = self.simulator._calculate_mood_factors(weather, time)
        self.assertIn("temperature_comfort", factors)
        self.assertIn("light_level", factors)
        self.assertIn("weather_mood", factors)
        self.assertIn("seasonal_comfort", factors)

    def test_mood_factor_temperature_comfortable(self):
        weather = WeatherData(
            temperature=20.0, humidity=60.0, description="Sunny",
            wind_speed=5.0, pressure=1013.0, visibility=10.0,
            sunrise="06:30", sunset="19:30", timestamp=datetime.now(),
        )
        time = TimeData(
            current_time=datetime.now(), day_of_week="Monday",
            is_daytime=True, time_of_day="morning",
            season="spring", moon_phase="Full Moon",
        )
        factors = self.simulator._calculate_mood_factors(weather, time)
        self.assertEqual(factors["temperature_comfort"], 1.0)

    def test_mood_factor_temperature_cold(self):
        weather = WeatherData(
            temperature=0.0, humidity=60.0, description="Cold and clear",
            wind_speed=5.0, pressure=1013.0, visibility=10.0,
            sunrise="06:30", sunset="19:30", timestamp=datetime.now(),
        )
        time = TimeData(
            current_time=datetime.now(), day_of_week="Monday",
            is_daytime=True, time_of_day="morning",
            season="winter", moon_phase="New Moon",
        )
        factors = self.simulator._calculate_mood_factors(weather, time)
        self.assertEqual(factors["temperature_comfort"], 0.4)

    def test_mood_factor_nighttime_light(self):
        weather = WeatherData(
            temperature=20.0, humidity=60.0, description="Clear",
            wind_speed=5.0, pressure=1013.0, visibility=10.0,
            sunrise="06:30", sunset="19:30", timestamp=datetime.now(),
        )
        time = TimeData(
            current_time=datetime.now(), day_of_week="Monday",
            is_daytime=False, time_of_day="night",
            season="summer", moon_phase="Full Moon",
        )
        factors = self.simulator._calculate_mood_factors(weather, time)
        self.assertEqual(factors["light_level"], 0.2)

    def test_mood_factor_evening_light(self):
        weather = WeatherData(
            temperature=20.0, humidity=60.0, description="Clear",
            wind_speed=5.0, pressure=1013.0, visibility=10.0,
            sunrise="06:30", sunset="19:30", timestamp=datetime.now(),
        )
        time = TimeData(
            current_time=datetime.now(), day_of_week="Monday",
            is_daytime=False, time_of_day="evening",
            season="summer", moon_phase="Full Moon",
        )
        factors = self.simulator._calculate_mood_factors(weather, time)
        self.assertEqual(factors["light_level"], 0.6)

    def test_mood_factor_cloudy_weather(self):
        weather = WeatherData(
            temperature=20.0, humidity=60.0, description="Partly cloudy",
            wind_speed=5.0, pressure=1013.0, visibility=10.0,
            sunrise="06:30", sunset="19:30", timestamp=datetime.now(),
        )
        time = TimeData(
            current_time=datetime.now(), day_of_week="Monday",
            is_daytime=True, time_of_day="morning",
            season="spring", moon_phase="Full Moon",
        )
        factors = self.simulator._calculate_mood_factors(weather, time)
        self.assertEqual(factors["weather_mood"], 0.7)

    def test_mood_factor_rainy_weather(self):
        weather = WeatherData(
            temperature=15.0, humidity=80.0, description="Light rain",
            wind_speed=5.0, pressure=1013.0, visibility=5.0,
            sunrise="06:30", sunset="19:30", timestamp=datetime.now(),
        )
        time = TimeData(
            current_time=datetime.now(), day_of_week="Monday",
            is_daytime=True, time_of_day="morning",
            season="spring", moon_phase="Full Moon",
        )
        factors = self.simulator._calculate_mood_factors(weather, time)
        self.assertEqual(factors["weather_mood"], 0.4)

    def test_mood_factor_seasonal_winter(self):
        weather = WeatherData(
            temperature=5.0, humidity=60.0, description="Cold and clear",
            wind_speed=5.0, pressure=1013.0, visibility=10.0,
            sunrise="07:30", sunset="17:00", timestamp=datetime.now(),
        )
        time = TimeData(
            current_time=datetime.now(), day_of_week="Monday",
            is_daytime=True, time_of_day="morning",
            season="winter", moon_phase="Full Moon",
        )
        factors = self.simulator._calculate_mood_factors(weather, time)
        self.assertEqual(factors["seasonal_comfort"], 0.6)

    def test_get_environment_state(self):
        state = self.simulator.get_environment_state()
        self.assertIsInstance(state, EnvironmentState)
        self.assertIsInstance(state.weather, WeatherData)
        self.assertIsInstance(state.time, TimeData)
        self.assertEqual(state.location, "Palo Alto, CA")

    def test_get_environment_description(self):
        desc = self.simulator.get_environment_description()
        self.assertIsInstance(desc, str)
        self.assertTrue(len(desc) > 0)
        self.assertIn("Palo Alto", desc)

    def test_update_weather_data_no_api_key(self):
        self.simulator._update_weather_data()
        self.assertIsNotNone(self.simulator.base_weather_data)
        self.assertIsNotNone(self.simulator.last_update)

    def test_get_local_events(self):
        events = self.simulator._get_local_events()
        self.assertIsInstance(events, list)


if __name__ == "__main__":
    unittest.main()
