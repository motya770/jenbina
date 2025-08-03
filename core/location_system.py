#!/usr/bin/env python3

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, time
import json

@dataclass
class Location:
    name: str
    type: str  # house, restaurant, park, shop, landmark, etc.
    address: str
    description: str
    coordinates: Tuple[float, float]  # lat, lng
    opening_hours: Dict[str, List[str]]  # day -> [open_time, close_time]
    features: List[str]  # ["wifi", "outdoor_seating", "parking", etc.]
    popularity: float  # 0-1, how busy it gets
    price_range: str  # "$", "$$", "$$$", "$$$$"
    mood: str  # "cozy", "energetic", "quiet", "romantic", etc.

@dataclass
class Neighborhood:
    name: str
    description: str
    vibe: str
    demographics: str
    landmarks: List[str]
    restaurants: List[str]
    parks: List[str]
    shops: List[str]

class PaloAltoLocationSystem:
    """Comprehensive location system for Palo Alto and surrounding areas"""
    
    def __init__(self):
        self.locations = self._initialize_locations()
        self.neighborhoods = self._initialize_neighborhoods()
        self.current_location = "Jenbina's House"
        
    def _initialize_locations(self) -> Dict[str, Location]:
        """Initialize all locations in Palo Alto and surrounding areas"""
        locations = {}
        
        # Jenbina's House
        locations["Jenbina's House"] = Location(
            name="Jenbina's House",
            type="house",
            address="1234 Middlefield Road, Palo Alto, CA",
            description="A cozy cottage-style house with a beautiful garden, located in the heart of Palo Alto. Features a sunny kitchen, comfortable living room, and a small backyard perfect for morning coffee.",
            coordinates=(37.4419, -122.1430),
            opening_hours={},
            features=["garden", "kitchen", "living_room", "backyard", "fireplace"],
            popularity=0.1,
            price_range="$$",
            mood="cozy"
        )
        
        # Restaurants
        locations["Coupa Cafe"] = Location(
            name="Coupa Cafe",
            type="restaurant",
            address="538 Ramona Street, Palo Alto, CA",
            description="A popular Venezuelan cafe known for its excellent coffee, arepas, and vibrant atmosphere. Great for breakfast and lunch.",
            coordinates=(37.4421, -122.1607),
            opening_hours={
                "monday": ["07:00", "22:00"],
                "tuesday": ["07:00", "22:00"],
                "wednesday": ["07:00", "22:00"],
                "thursday": ["07:00", "22:00"],
                "friday": ["07:00", "22:00"],
                "saturday": ["07:00", "22:00"],
                "sunday": ["07:00", "22:00"]
            },
            features=["wifi", "outdoor_seating", "coffee", "breakfast", "lunch"],
            popularity=0.8,
            price_range="$$",
            mood="energetic"
        )
        
        locations["Zare at Fly Trap"] = Location(
            name="Zare at Fly Trap",
            type="restaurant",
            address="606 Folsom Street, San Francisco, CA",
            description="An upscale Mediterranean restaurant with a romantic atmosphere, perfect for special occasions.",
            coordinates=(37.7849, -122.3953),
            opening_hours={
                "monday": ["17:30", "22:00"],
                "tuesday": ["17:30", "22:00"],
                "wednesday": ["17:30", "22:00"],
                "thursday": ["17:30", "22:00"],
                "friday": ["17:30", "23:00"],
                "saturday": ["17:30", "23:00"],
                "sunday": ["17:30", "22:00"]
            },
            features=["romantic", "upscale", "wine", "dinner"],
            popularity=0.7,
            price_range="$$$",
            mood="romantic"
        )
        
        locations["Stanford Shopping Center"] = Location(
            name="Stanford Shopping Center",
            type="shopping",
            address="660 Stanford Shopping Center, Palo Alto, CA",
            description="An upscale outdoor shopping mall with high-end stores, restaurants, and beautiful landscaping. Popular destination for shopping and dining.",
            coordinates=(37.4436, -122.1700),
            opening_hours={
                "monday": ["10:00", "21:00"],
                "tuesday": ["10:00", "21:00"],
                "wednesday": ["10:00", "21:00"],
                "thursday": ["10:00", "21:00"],
                "friday": ["10:00", "21:00"],
                "saturday": ["10:00", "21:00"],
                "sunday": ["11:00", "19:00"]
            },
            features=["shopping", "restaurants", "outdoor", "parking", "luxury_stores"],
            popularity=0.9,
            price_range="$$$",
            mood="luxurious"
        )
        
        locations["Stanford University"] = Location(
            name="Stanford University",
            type="landmark",
            address="450 Serra Mall, Stanford, CA",
            description="A prestigious university with beautiful Spanish colonial architecture, extensive gardens, and the iconic Hoover Tower. Great for walking tours and cultural events.",
            coordinates=(37.4275, -122.1697),
            opening_hours={},
            features=["campus", "gardens", "architecture", "museums", "events"],
            popularity=0.8,
            price_range="$",
            mood="academic"
        )
        
        locations["Baylands Nature Preserve"] = Location(
            name="Baylands Nature Preserve",
            type="park",
            address="2775 Embarcadero Road, Palo Alto, CA",
            description="A beautiful nature preserve with walking trails, bird watching, and stunning bay views. Perfect for peaceful walks and nature observation.",
            coordinates=(37.4567, -122.1089),
            opening_hours={
                "monday": ["06:00", "22:00"],
                "tuesday": ["06:00", "22:00"],
                "wednesday": ["06:00", "22:00"],
                "thursday": ["06:00", "22:00"],
                "friday": ["06:00", "22:00"],
                "saturday": ["06:00", "22:00"],
                "sunday": ["06:00", "22:00"]
            },
            features=["hiking", "bird_watching", "nature", "peaceful", "bay_views"],
            popularity=0.6,
            price_range="$",
            mood="peaceful"
        )
        
        locations["University Avenue"] = Location(
            name="University Avenue",
            type="district",
            address="University Avenue, Palo Alto, CA",
            description="The main downtown street of Palo Alto, lined with restaurants, cafes, shops, and historic buildings. The heart of the city's social life.",
            coordinates=(37.4421, -122.1607),
            opening_hours={},
            features=["dining", "shopping", "historic", "walkable", "cafes"],
            popularity=0.9,
            price_range="$$",
            mood="vibrant"
        )
        
        locations["Computer History Museum"] = Location(
            name="Computer History Museum",
            type="museum",
            address="1401 N Shoreline Blvd, Mountain View, CA",
            description="A fascinating museum dedicated to the history of computing, featuring vintage computers, interactive exhibits, and the history of Silicon Valley.",
            coordinates=(37.4144, -122.0769),
            opening_hours={
                "monday": ["10:00", "17:00"],
                "tuesday": ["10:00", "17:00"],
                "wednesday": ["10:00", "17:00"],
                "thursday": ["10:00", "17:00"],
                "friday": ["10:00", "17:00"],
                "saturday": ["10:00", "17:00"],
                "sunday": ["10:00", "17:00"]
            },
            features=["museum", "interactive", "history", "technology", "educational"],
            popularity=0.5,
            price_range="$$",
            mood="educational"
        )
        
        locations["Santana Row"] = Location(
            name="Santana Row",
            type="district",
            address="377 Santana Row, San Jose, CA",
            description="A luxury shopping and dining district with European-style architecture, high-end boutiques, and excellent restaurants.",
            coordinates=(37.3219, -121.9477),
            opening_hours={},
            features=["luxury_shopping", "dining", "european_style", "boutiques", "nightlife"],
            popularity=0.8,
            price_range="$$$",
            mood="sophisticated"
        )
        
        locations["Half Moon Bay"] = Location(
            name="Half Moon Bay",
            type="coastal",
            address="Half Moon Bay, CA",
            description="A charming coastal town known for its beautiful beaches, pumpkin farms, and relaxed atmosphere. Perfect for day trips and ocean views.",
            coordinates=(37.4635, -122.4286),
            opening_hours={},
            features=["beach", "coastal", "relaxed", "scenic", "farms"],
            popularity=0.7,
            price_range="$$",
            mood="relaxed"
        )
        
        locations["Filoli Gardens"] = Location(
            name="Filoli Gardens",
            type="garden",
            address="86 Cañada Road, Woodside, CA",
            description="A stunning historic estate with magnificent gardens, walking trails, and beautiful architecture. Perfect for peaceful walks and photography.",
            coordinates=(37.4635, -122.4286),
            opening_hours={
                "tuesday": ["10:00", "17:00"],
                "wednesday": ["10:00", "17:00"],
                "thursday": ["10:00", "17:00"],
                "friday": ["10:00", "17:00"],
                "saturday": ["10:00", "17:00"],
                "sunday": ["10:00", "17:00"]
            },
            features=["gardens", "historic", "walking", "photography", "peaceful"],
            popularity=0.6,
            price_range="$$",
            mood="serene"
        )
        
        return locations
    
    def _initialize_neighborhoods(self) -> Dict[str, Neighborhood]:
        """Initialize neighborhoods in Palo Alto and surrounding areas"""
        neighborhoods = {}
        
        neighborhoods["Downtown Palo Alto"] = Neighborhood(
            name="Downtown Palo Alto",
            description="The vibrant heart of Palo Alto with University Avenue as its main street. Home to excellent restaurants, cafes, and boutique shops.",
            vibe="urban, sophisticated, tech-savvy",
            demographics="Young professionals, tech workers, students",
            landmarks=["University Avenue", "Coupa Cafe", "Stanford Shopping Center"],
            restaurants=["Coupa Cafe", "Zare at Fly Trap", "Palo Alto Creamery"],
            parks=["Heritage Park", "Johnson Park"],
            shops=["Stanford Shopping Center", "University Avenue shops"]
        )
        
        neighborhoods["Stanford"] = Neighborhood(
            name="Stanford",
            description="Home to Stanford University, featuring beautiful campus architecture, museums, and academic atmosphere.",
            vibe="academic, intellectual, peaceful",
            demographics="Students, professors, academics",
            landmarks=["Stanford University", "Hoover Tower", "Cantor Arts Center"],
            restaurants=["Stanford Dining", "Coupa Cafe Stanford"],
            parks=["Stanford Campus", "Stanford Arboretum"],
            shops=["Stanford Bookstore", "Stanford Shopping Center"]
        )
        
        neighborhoods["Mountain View"] = Neighborhood(
            name="Mountain View",
            description="A tech hub with Google headquarters, featuring Castro Street's diverse dining scene and the Computer History Museum.",
            vibe="tech-focused, diverse, innovative",
            demographics="Tech workers, engineers, families",
            landmarks=["Google Campus", "Computer History Museum", "Castro Street"],
            restaurants=["Castro Street restaurants", "Google cafes"],
            parks=["Shoreline Park", "Cuesta Park"],
            shops=["Castro Street shops", "San Antonio Shopping Center"]
        )
        
        neighborhoods["San Jose"] = Neighborhood(
            name="San Jose",
            description="The largest city in the Bay Area, featuring diverse neighborhoods, cultural attractions, and Santana Row luxury district.",
            vibe="diverse, urban, cultural",
            demographics="Families, professionals, diverse communities",
            landmarks=["Santana Row", "San Jose Museum of Art", "Tech Museum"],
            restaurants=["Santana Row restaurants", "San Pedro Square Market"],
            parks=["Guadalupe River Park", "Alum Rock Park"],
            shops=["Santana Row", "Westfield Valley Fair"]
        )
        
        return neighborhoods
    
    def get_location(self, name: str) -> Optional[Location]:
        """Get a specific location by name"""
        return self.locations.get(name)
    
    def get_neighborhood(self, name: str) -> Optional[Neighborhood]:
        """Get a specific neighborhood by name"""
        return self.neighborhoods.get(name)
    
    def get_locations_by_type(self, location_type: str) -> List[Location]:
        """Get all locations of a specific type"""
        return [loc for loc in self.locations.values() if loc.type == location_type]
    
    def get_nearby_locations(self, current_location: str, radius_km: float = 5.0) -> List[Location]:
        """Get locations within a certain radius of current location"""
        # Simplified distance calculation (in real implementation, use proper geolocation)
        current = self.locations.get(current_location)
        if not current:
            return []
        
        nearby = []
        for location in self.locations.values():
            if location.name != current_location:
                # Simple distance calculation (lat/lng difference)
                lat_diff = abs(location.coordinates[0] - current.coordinates[0])
                lng_diff = abs(location.coordinates[1] - current.coordinates[1])
                distance = (lat_diff + lng_diff) * 111  # Rough km conversion
                
                if distance <= radius_km:
                    nearby.append(location)
        
        return nearby
    
    def get_locations_by_mood(self, mood: str) -> List[Location]:
        """Get locations that match a specific mood"""
        return [loc for loc in self.locations.values() if loc.mood == mood]
    
    def get_open_locations(self, current_time: datetime = None) -> List[Location]:
        """Get locations that are currently open"""
        if current_time is None:
            current_time = datetime.now()
        
        day = current_time.strftime('%A').lower()
        time_str = current_time.strftime('%H:%M')
        
        open_locations = []
        for location in self.locations.values():
            if not location.opening_hours:  # Always open (like parks, landmarks)
                open_locations.append(location)
            elif day in location.opening_hours:
                hours = location.opening_hours[day]
                if len(hours) >= 2:
                    open_time, close_time = hours[0], hours[1]
                    if open_time <= time_str <= close_time:
                        open_locations.append(location)
        
        return open_locations
    
    def get_popular_locations(self, min_popularity: float = 0.7) -> List[Location]:
        """Get popular locations above a certain popularity threshold"""
        return [loc for loc in self.locations.values() if loc.popularity >= min_popularity]
    
    def get_location_description(self, location_name: str) -> str:
        """Get a natural language description of a location"""
        location = self.get_location(location_name)
        if not location:
            return f"I don't know about {location_name}."
        
        description = f"{location.name} is a {location.type} located at {location.address}. "
        description += location.description
        
        if location.opening_hours:
            description += f" It's typically open during business hours."
        
        if location.features:
            features_str = ", ".join(location.features)
            description += f" It features {features_str}."
        
        return description
    
    def get_recommendation(self, mood: str = None, location_type: str = None, 
                          max_price: str = "$$$") -> Optional[Location]:
        """Get a location recommendation based on criteria"""
        candidates = self.locations.values()
        
        if mood:
            candidates = [loc for loc in candidates if loc.mood == mood]
        
        if location_type:
            candidates = [loc for loc in candidates if loc.type == location_type]
        
        # Filter by price range
        price_levels = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        max_price_level = price_levels.get(max_price, 3)
        candidates = [loc for loc in candidates if price_levels.get(loc.price_range, 2) <= max_price_level]
        
        if candidates:
            # Return a random candidate, weighted by popularity
            weights = [loc.popularity for loc in candidates]
            return random.choices(candidates, weights=weights)[0]
        
        return None
    
    def get_daily_activity_suggestion(self, current_time: datetime = None) -> Dict[str, any]:
        """Get a suggested activity based on current time and mood"""
        if current_time is None:
            current_time = datetime.now()
        
        hour = current_time.hour
        day = current_time.strftime('%A').lower()
        
        suggestions = {
            "morning": {
                "cozy": "Coupa Cafe",
                "energetic": "Stanford Shopping Center",
                "peaceful": "Baylands Nature Preserve"
            },
            "afternoon": {
                "cozy": "University Avenue",
                "energetic": "Stanford Shopping Center",
                "peaceful": "Filoli Gardens"
            },
            "evening": {
                "cozy": "Coupa Cafe",
                "romantic": "Zare at Fly Trap",
                "energetic": "Santana Row"
            },
            "night": {
                "cozy": "Jenbina's House",
                "energetic": "Santana Row",
                "peaceful": "Baylands Nature Preserve"
            }
        }
        
        # Determine time of day
        if 6 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Get mood-based suggestions
        mood_suggestions = suggestions.get(time_of_day, {})
        
        # Check what's open
        open_locations = self.get_open_locations(current_time)
        open_names = [loc.name for loc in open_locations]
        
        # Find a suitable suggestion that's open
        for mood, location_name in mood_suggestions.items():
            if location_name in open_names:
                location = self.get_location(location_name)
                return {
                    "activity": f"Visit {location_name}",
                    "location": location,
                    "reason": f"It's {time_of_day} and {location_name} has a {mood} atmosphere",
                    "time_of_day": time_of_day,
                    "mood": mood
                }
        
        # Fallback to home
        return {
            "activity": "Stay at home",
            "location": self.get_location("Jenbina's House"),
            "reason": "It's a good time to relax at home",
            "time_of_day": time_of_day,
            "mood": "cozy"
        }

# Example usage
if __name__ == "__main__":
    location_system = PaloAltoLocationSystem()
    
    print("🏠 Jenbina's World - Palo Alto Locations:")
    print()
    
    # Show all locations
    for name, location in location_system.locations.items():
        print(f"📍 {name}")
        print(f"   Type: {location.type}")
        print(f"   Address: {location.address}")
        print(f"   Mood: {location.mood}")
        print(f"   Popularity: {location.popularity:.1f}")
        print()
    
    # Get a recommendation
    recommendation = location_system.get_recommendation(mood="cozy", max_price="$$")
    if recommendation:
        print(f"💡 Recommendation: {recommendation.name}")
        print(f"   {recommendation.description}")
    
    # Get daily activity suggestion
    suggestion = location_system.get_daily_activity_suggestion()
    print(f"\n🎯 Today's Activity: {suggestion['activity']}")
    print(f"   Reason: {suggestion['reason']}") 