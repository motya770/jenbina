#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import random
import os

@dataclass
class Event:
    name: str
    type: str  # concert, bar, restaurant, landmark, etc.
    description: str
    location: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    price: Optional[str]
    popularity: float  # 0-1
    source: str  # which API provided this
    url: Optional[str]
    coordinates: Optional[tuple] = None

@dataclass
class Venue:
    name: str
    type: str
    address: str
    description: str
    rating: Optional[float]
    price_level: Optional[str]
    opening_hours: Optional[Dict]
    features: List[str]
    coordinates: Optional[tuple] = None

class DynamicEventsSystem:
    """Flexible system to fetch real-time events and venue information"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Fallback data for when APIs are unavailable
        self.fallback_events = self._initialize_fallback_events()
        self.fallback_venues = self._initialize_fallback_venues()
    
    def _initialize_fallback_events(self) -> List[Event]:
        """Initialize fallback events when APIs are unavailable"""
        current_time = datetime.now()
        
        events = [
            Event(
                name="Live Music at Coupa Cafe",
                type="concert",
                description="Local jazz band performing live music in the cozy atmosphere of Coupa Cafe",
                location="Coupa Cafe, 538 Ramona Street, Palo Alto",
                start_time=current_time.replace(hour=19, minute=0, second=0, microsecond=0),
                end_time=current_time.replace(hour=22, minute=0, second=0, microsecond=0),
                price="$15",
                popularity=0.8,
                source="fallback",
                url=None
            ),
            Event(
                name="Stanford Shopping Center Art Walk",
                type="cultural",
                description="Monthly art walk featuring local artists and galleries",
                location="Stanford Shopping Center, Palo Alto",
                start_time=current_time.replace(hour=18, minute=0, second=0, microsecond=0),
                end_time=current_time.replace(hour=21, minute=0, second=0, microsecond=0),
                price="Free",
                popularity=0.6,
                source="fallback",
                url=None
            ),
            Event(
                name="Baylands Nature Photography Workshop",
                type="workshop",
                description="Photography workshop in the beautiful Baylands Nature Preserve",
                location="Baylands Nature Preserve, Palo Alto",
                start_time=current_time.replace(hour=9, minute=0, second=0, microsecond=0),
                end_time=current_time.replace(hour=12, minute=0, second=0, microsecond=0),
                price="$45",
                popularity=0.7,
                source="fallback",
                url=None
            )
        ]
        
        return events
    
    def _initialize_fallback_venues(self) -> List[Venue]:
        """Initialize fallback venues when APIs are unavailable"""
        venues = [
            Venue(
                name="The Rosewood",
                type="bar",
                address="2825 Sand Hill Road, Menlo Park",
                description="Upscale bar and restaurant with craft cocktails and fine dining",
                rating=4.5,
                price_level="$$$",
                opening_hours={
                    "monday": ["17:00", "23:00"],
                    "tuesday": ["17:00", "23:00"],
                    "wednesday": ["17:00", "23:00"],
                    "thursday": ["17:00", "23:00"],
                    "friday": ["17:00", "00:00"],
                    "saturday": ["17:00", "00:00"],
                    "sunday": ["17:00", "23:00"]
                },
                features=["craft_cocktails", "fine_dining", "outdoor_seating", "live_music"]
            ),
            Venue(
                name="The Patio",
                type="bar",
                address="531 Emerson Street, Palo Alto",
                description="Popular sports bar with great food and drinks, perfect for watching games",
                rating=4.2,
                price_level="$$",
                opening_hours={
                    "monday": ["11:00", "02:00"],
                    "tuesday": ["11:00", "02:00"],
                    "wednesday": ["11:00", "02:00"],
                    "thursday": ["11:00", "02:00"],
                    "friday": ["11:00", "02:00"],
                    "saturday": ["11:00", "02:00"],
                    "sunday": ["11:00", "02:00"]
                },
                features=["sports_bar", "pub_food", "beer", "tv_screens"]
            ),
            Venue(
                name="Stanford Theatre",
                type="landmark",
                address="221 University Avenue, Palo Alto",
                description="Historic movie theatre showing classic films in a beautiful Art Deco setting",
                rating=4.7,
                price_level="$$",
                opening_hours={
                    "monday": ["19:00", "23:00"],
                    "tuesday": ["19:00", "23:00"],
                    "wednesday": ["19:00", "23:00"],
                    "thursday": ["19:00", "23:00"],
                    "friday": ["19:00", "23:00"],
                    "saturday": ["14:00", "23:00"],
                    "sunday": ["14:00", "23:00"]
                },
                features=["classic_films", "art_deco", "historic", "organ_music"]
            )
        ]
        
        return venues
    
    def get_events(self, event_type: str = None, location: str = "Palo Alto", 
                   date_range: int = 7) -> List[Event]:
        """Get events from multiple sources"""
        cache_key = f"events_{event_type}_{location}_{date_range}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_time, cached_events = self.cache[cache_key]
            if (datetime.now() - cache_time).seconds < self.cache_duration:
                return cached_events
        
        events = []
        
        # Try to get real events from APIs
        try:
            # Try Eventbrite API
            if 'eventbrite' in self.api_keys:
                eventbrite_events = self._fetch_eventbrite_events(location, event_type, date_range)
                events.extend(eventbrite_events)
            
            # Try Ticketmaster API
            if 'ticketmaster' in self.api_keys:
                ticketmaster_events = self._fetch_ticketmaster_events(location, event_type, date_range)
                events.extend(ticketmaster_events)
            
            # Try Yelp API for venue events
            if 'yelp' in self.api_keys:
                yelp_events = self._fetch_yelp_events(location, event_type)
                events.extend(yelp_events)
                
        except Exception as e:
            print(f"API error fetching events: {e}")
        
        # If no real events, use fallback
        if not events:
            events = self.fallback_events.copy()
            # Filter by type if specified
            if event_type:
                events = [e for e in events if e.type == event_type]
        
        # Cache the results
        self.cache[cache_key] = (datetime.now(), events)
        
        return events
    
    def get_venues(self, venue_type: str = None, location: str = "Palo Alto") -> List[Venue]:
        """Get venues from multiple sources"""
        cache_key = f"venues_{venue_type}_{location}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_time, cached_venues = self.cache[cache_key]
            if (datetime.now() - cache_time).seconds < self.cache_duration:
                return cached_venues
        
        venues = []
        
        # Try to get real venues from APIs
        try:
            # Try Yelp API
            if 'yelp' in self.api_keys:
                yelp_venues = self._fetch_yelp_venues(location, venue_type)
                venues.extend(yelp_venues)
            
            # Try Google Places API
            if 'google_places' in self.api_keys:
                google_venues = self._fetch_google_venues(location, venue_type)
                venues.extend(google_venues)
                
        except Exception as e:
            print(f"API error fetching venues: {e}")
        
        # If no real venues, use fallback
        if not venues:
            venues = self.fallback_venues.copy()
            # Filter by type if specified
            if venue_type:
                venues = [v for v in venues if v.type == venue_type]
        
        # Cache the results
        self.cache[cache_key] = (datetime.now(), venues)
        
        return venues
    
    def _fetch_eventbrite_events(self, location: str, event_type: str = None, 
                                date_range: int = 7) -> List[Event]:
        """Fetch events from Eventbrite API"""
        api_key = self.api_keys['eventbrite']
        url = "https://www.eventbriteapi.com/v3/events/search/"
        
        params = {
            'location.address': location,
            'start_date.range_start': datetime.now().isoformat(),
            'start_date.range_end': (datetime.now() + timedelta(days=date_range)).isoformat(),
            'expand': 'venue'
        }
        
        if event_type:
            params['q'] = event_type
        
        headers = {'Authorization': f'Bearer {api_key}'}
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        events = []
        for event_data in data.get('events', []):
            event = Event(
                name=event_data['name']['text'],
                type=event_type or 'event',
                description=event_data.get('description', {}).get('text', ''),
                location=event_data.get('venue', {}).get('name', ''),
                start_time=datetime.fromisoformat(event_data['start']['utc']),
                end_time=datetime.fromisoformat(event_data['end']['utc']),
                price=event_data.get('ticket_availability', {}).get('minimum_ticket_price', {}).get('display', 'Free'),
                popularity=0.7,  # Default popularity
                source="eventbrite",
                url=event_data.get('url'),
                coordinates=(
                    float(event_data['venue']['latitude']),
                    float(event_data['venue']['longitude'])
                ) if event_data.get('venue') else None
            )
            events.append(event)
        
        return events
    
    def _fetch_ticketmaster_events(self, location: str, event_type: str = None,
                                  date_range: int = 7) -> List[Event]:
        """Fetch events from Ticketmaster API"""
        api_key = self.api_keys['ticketmaster']
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        
        params = {
            'apikey': api_key,
            'city': location,
            'startDateTime': datetime.now().isoformat(),
            'endDateTime': (datetime.now() + timedelta(days=date_range)).isoformat(),
            'size': 20
        }
        
        if event_type:
            params['keyword'] = event_type
        
        response = requests.get(url, params=params)
        data = response.json()
        
        events = []
        for event_data in data.get('_embedded', {}).get('events', []):
            event = Event(
                name=event_data['name'],
                type=event_type or 'concert',
                description=event_data.get('info', ''),
                location=event_data.get('_embedded', {}).get('venues', [{}])[0].get('name', ''),
                start_time=datetime.fromisoformat(event_data['dates']['start']['dateTime']),
                end_time=None,  # Ticketmaster doesn't provide end time
                price=event_data.get('priceRanges', [{}])[0].get('min', 'Varies'),
                popularity=0.8,  # Default popularity
                source="ticketmaster",
                url=event_data.get('url'),
                coordinates=(
                    float(event_data['_embedded']['venues'][0]['location']['latitude']),
                    float(event_data['_embedded']['venues'][0]['location']['longitude'])
                ) if event_data.get('_embedded', {}).get('venues') else None
            )
            events.append(event)
        
        return events
    
    def _fetch_yelp_events(self, location: str, event_type: str = None) -> List[Event]:
        """Fetch events from Yelp API"""
        api_key = self.api_keys['yelp']
        url = "https://api.yelp.com/v3/events"
        
        headers = {'Authorization': f'Bearer {api_key}'}
        params = {'location': location, 'limit': 20}
        
        if event_type:
            params['categories'] = event_type
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        events = []
        for event_data in data.get('events', []):
            event = Event(
                name=event_data['name'],
                type=event_type or 'event',
                description=event_data.get('description', ''),
                location=event_data.get('location', {}).get('address1', ''),
                start_time=datetime.fromisoformat(event_data['time_start']),
                end_time=datetime.fromisoformat(event_data['time_end']) if event_data.get('time_end') else None,
                price=event_data.get('cost', 'Free'),
                popularity=event_data.get('popularity', 0.5),
                source="yelp",
                url=event_data.get('event_site_url'),
                coordinates=(
                    float(event_data['location']['latitude']),
                    float(event_data['location']['longitude'])
                ) if event_data.get('location') else None
            )
            events.append(event)
        
        return events
    
    def _fetch_yelp_venues(self, location: str, venue_type: str = None) -> List[Venue]:
        """Fetch venues from Yelp API"""
        api_key = self.api_keys['yelp']
        url = "https://api.yelp.com/v3/businesses/search"
        
        headers = {'Authorization': f'Bearer {api_key}'}
        params = {'location': location, 'limit': 20}
        
        if venue_type:
            params['categories'] = venue_type
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        venues = []
        for venue_data in data.get('businesses', []):
            venue = Venue(
                name=venue_data['name'],
                type=venue_type or 'venue',
                address=venue_data['location']['address1'],
                description=venue_data.get('snippet_text', ''),
                rating=venue_data.get('rating'),
                price_level=venue_data.get('price'),
                opening_hours=venue_data.get('hours', [{}])[0].get('open') if venue_data.get('hours') else None,
                features=venue_data.get('categories', []),
                coordinates=(
                    float(venue_data['coordinates']['latitude']),
                    float(venue_data['coordinates']['longitude'])
                ) if venue_data.get('coordinates') else None
            )
            venues.append(venue)
        
        return venues
    
    def _fetch_google_venues(self, location: str, venue_type: str = None) -> List[Venue]:
        """Fetch venues from Google Places API"""
        api_key = self.api_keys['google_places']
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        
        params = {
            'query': f"{venue_type or 'venue'} in {location}",
            'key': api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        venues = []
        for venue_data in data.get('results', []):
            venue = Venue(
                name=venue_data['name'],
                type=venue_type or 'venue',
                address=venue_data.get('formatted_address', ''),
                description=venue_data.get('types', []),
                rating=venue_data.get('rating'),
                price_level=venue_data.get('price_level'),
                opening_hours=None,  # Would need additional API call
                features=venue_data.get('types', []),
                coordinates=(
                    venue_data['geometry']['location']['lat'],
                    venue_data['geometry']['location']['lng']
                ) if venue_data.get('geometry') else None
            )
            venues.append(venue)
        
        return venues
    
    def get_recommendations(self, mood: str = None, activity_type: str = None,
                           max_price: str = "$$$") -> Dict[str, List]:
        """Get personalized recommendations"""
        recommendations = {
            'events': [],
            'venues': [],
            'activities': []
        }
        
        # Get events
        events = self.get_events(event_type=activity_type)
        if mood:
            # Filter events by mood (simplified)
            mood_keywords = {
                'cozy': ['cafe', 'restaurant', 'bar'],
                'energetic': ['concert', 'party', 'sports'],
                'peaceful': ['workshop', 'nature', 'museum'],
                'romantic': ['dinner', 'theatre', 'concert']
            }
            keywords = mood_keywords.get(mood, [])
            events = [e for e in events if any(kw in e.type.lower() for kw in keywords)]
        
        recommendations['events'] = events[:3]
        
        # Get venues
        venue_type = activity_type if activity_type in ['bar', 'restaurant', 'landmark'] else None
        venues = self.get_venues(venue_type=venue_type)
        
        # Filter by price
        price_levels = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        max_price_level = price_levels.get(max_price, 3)
        venues = [v for v in venues if price_levels.get(v.price_level, 2) <= max_price_level]
        
        recommendations['venues'] = venues[:3]
        
        return recommendations
    
    def get_today_highlights(self) -> List[str]:
        """Get today's highlights and recommendations"""
        highlights = []
        
        # Get today's events
        today_events = self.get_events(date_range=1)
        if today_events:
            highlights.append(f"Today's events: {len(today_events)} events happening")
        
        # Get popular venues
        popular_venues = [v for v in self.get_venues() if v.rating and v.rating > 4.0]
        if popular_venues:
            highlights.append(f"Top-rated venues: {len(popular_venues)} highly rated places to visit")
        
        # Get specific recommendations
        recommendations = self.get_recommendations(mood='energetic', max_price='$$')
        if recommendations['events']:
            highlights.append(f"Recommended: {recommendations['events'][0].name}")
        
        return highlights

# Example usage
if __name__ == "__main__":
    # Initialize with optional API keys
    api_keys = {
        # 'eventbrite': 'your_eventbrite_token',
        # 'ticketmaster': 'your_ticketmaster_key',
        # 'yelp': 'your_yelp_token',
        # 'google_places': 'your_google_places_key'
    }
    
    events_system = DynamicEventsSystem(api_keys)
    
    print("🎉 Dynamic Events System - Palo Alto")
    print()
    
    # Get events
    events = events_system.get_events(event_type="concert")
    print(f"🎵 Found {len(events)} events:")
    for event in events[:3]:
        print(f"  • {event.name} at {event.location}")
        print(f"    {event.start_time.strftime('%Y-%m-%d %H:%M')} - {event.price}")
        print()
    
    # Get venues
    venues = events_system.get_venues(venue_type="bar")
    print(f"🍺 Found {len(venues)} venues:")
    for venue in venues[:3]:
        print(f"  • {venue.name} - {venue.rating}⭐ ({venue.price_level})")
        print(f"    {venue.address}")
        print()
    
    # Get recommendations
    recommendations = events_system.get_recommendations(mood="energetic", max_price="$$")
    print("💡 Recommendations:")
    if recommendations['events']:
        print(f"  Events: {recommendations['events'][0].name}")
    if recommendations['venues']:
        print(f"  Venues: {recommendations['venues'][0].name}")
    
    # Get today's highlights
    highlights = events_system.get_today_highlights()
    print(f"\n🌟 Today's Highlights:")
    for highlight in highlights:
        print(f"  • {highlight}") 