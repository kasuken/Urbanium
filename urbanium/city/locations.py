"""
City Locations - Physical places in the city.

Locations include:
- Residential (homes, apartments)
- Commercial (shops, restaurants)
- Workplaces (offices, factories)
- Public spaces (parks, community centers)
- Services (hospitals, schools)
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Tuple
import random
import math


class LocationType(Enum):
    """Types of locations in the city."""
    # Residential
    HOUSE = "house"
    APARTMENT = "apartment"
    APARTMENT_COMPLEX = "apartment_complex"
    
    # Commercial
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    BAR = "bar"
    GROCERY_STORE = "grocery_store"
    SHOPPING_MALL = "shopping_mall"
    RETAIL_STORE = "retail_store"
    
    # Workplaces
    OFFICE_BUILDING = "office_building"
    FACTORY = "factory"
    WAREHOUSE = "warehouse"
    
    # Public spaces
    PARK = "park"
    PLAZA = "plaza"
    COMMUNITY_CENTER = "community_center"
    LIBRARY = "library"
    MUSEUM = "museum"
    
    # Services
    HOSPITAL = "hospital"
    CLINIC = "clinic"
    SCHOOL = "school"
    UNIVERSITY = "university"
    GOVERNMENT_BUILDING = "government_building"
    
    # Entertainment
    GYM = "gym"
    CINEMA = "cinema"
    THEATER = "theater"
    SPORTS_VENUE = "sports_venue"
    NIGHTCLUB = "nightclub"
    
    # Transit
    BUS_STATION = "bus_station"
    TRAIN_STATION = "train_station"


class LocationCategory(Enum):
    """Categories of locations."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    WORKPLACE = "workplace"
    PUBLIC = "public"
    SERVICE = "service"
    ENTERTAINMENT = "entertainment"
    TRANSIT = "transit"


# Mapping of types to categories
LOCATION_CATEGORIES = {
    LocationType.HOUSE: LocationCategory.RESIDENTIAL,
    LocationType.APARTMENT: LocationCategory.RESIDENTIAL,
    LocationType.APARTMENT_COMPLEX: LocationCategory.RESIDENTIAL,
    LocationType.RESTAURANT: LocationCategory.COMMERCIAL,
    LocationType.CAFE: LocationCategory.COMMERCIAL,
    LocationType.BAR: LocationCategory.COMMERCIAL,
    LocationType.GROCERY_STORE: LocationCategory.COMMERCIAL,
    LocationType.SHOPPING_MALL: LocationCategory.COMMERCIAL,
    LocationType.RETAIL_STORE: LocationCategory.COMMERCIAL,
    LocationType.OFFICE_BUILDING: LocationCategory.WORKPLACE,
    LocationType.FACTORY: LocationCategory.WORKPLACE,
    LocationType.WAREHOUSE: LocationCategory.WORKPLACE,
    LocationType.PARK: LocationCategory.PUBLIC,
    LocationType.PLAZA: LocationCategory.PUBLIC,
    LocationType.COMMUNITY_CENTER: LocationCategory.PUBLIC,
    LocationType.LIBRARY: LocationCategory.PUBLIC,
    LocationType.MUSEUM: LocationCategory.PUBLIC,
    LocationType.HOSPITAL: LocationCategory.SERVICE,
    LocationType.CLINIC: LocationCategory.SERVICE,
    LocationType.SCHOOL: LocationCategory.SERVICE,
    LocationType.UNIVERSITY: LocationCategory.SERVICE,
    LocationType.GOVERNMENT_BUILDING: LocationCategory.SERVICE,
    LocationType.GYM: LocationCategory.ENTERTAINMENT,
    LocationType.CINEMA: LocationCategory.ENTERTAINMENT,
    LocationType.THEATER: LocationCategory.ENTERTAINMENT,
    LocationType.SPORTS_VENUE: LocationCategory.ENTERTAINMENT,
    LocationType.NIGHTCLUB: LocationCategory.ENTERTAINMENT,
    LocationType.BUS_STATION: LocationCategory.TRANSIT,
    LocationType.TRAIN_STATION: LocationCategory.TRANSIT,
}


@dataclass
class OpeningHours:
    """Opening hours for a location."""
    
    opens: time = field(default_factory=lambda: time(9, 0))
    closes: time = field(default_factory=lambda: time(21, 0))
    
    # Which days open (0=Monday, 6=Sunday)
    days_open: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5])  # Mon-Sat
    
    is_24_hours: bool = False
    
    def is_open(self, current_time: time, day_of_week: int) -> bool:
        """Check if location is currently open."""
        if self.is_24_hours:
            return True
        
        if day_of_week not in self.days_open:
            return False
        
        if self.opens <= self.closes:
            return self.opens <= current_time <= self.closes
        else:
            # Wraps around midnight
            return current_time >= self.opens or current_time <= self.closes


@dataclass
class Location:
    """
    A physical location in the city.
    
    Attributes:
        id: Unique identifier
        name: Location name
        location_type: Type of location
        position: (x, y) coordinates
        capacity: Maximum number of people
        current_occupants: IDs of people currently here
        owner_id: Who owns this location (if applicable)
    """
    
    id: str
    name: str
    location_type: LocationType
    
    # Position in city grid
    position: Tuple[float, float] = (0.0, 0.0)
    
    # Capacity
    capacity: int = 50
    current_occupants: Set[str] = field(default_factory=set)
    
    # Ownership
    owner_id: Optional[str] = None
    owner_company_id: Optional[str] = None
    
    # Properties
    size: float = 100.0  # Square meters
    quality: float = 0.5  # 0-1
    value: float = 100000.0
    monthly_cost: float = 1000.0  # Rent/maintenance
    
    # Hours
    opening_hours: OpeningHours = field(default_factory=OpeningHours)
    
    # Interactions
    allows_socializing: bool = True
    is_private: bool = False
    
    # Tracking
    total_visitors_today: int = 0
    
    @property
    def category(self) -> LocationCategory:
        """Get the category of this location."""
        return LOCATION_CATEGORIES.get(
            self.location_type,
            LocationCategory.PUBLIC,
        )
    
    @property
    def occupancy(self) -> float:
        """Get current occupancy rate."""
        if self.capacity <= 0:
            return 0.0
        return len(self.current_occupants) / self.capacity
    
    @property
    def is_full(self) -> bool:
        """Check if location is at capacity."""
        return len(self.current_occupants) >= self.capacity
    
    def enter(self, citizen_id: str) -> bool:
        """A citizen enters the location."""
        if self.is_full:
            return False
        self.current_occupants.add(citizen_id)
        self.total_visitors_today += 1
        return True
    
    def leave(self, citizen_id: str) -> bool:
        """A citizen leaves the location."""
        if citizen_id in self.current_occupants:
            self.current_occupants.remove(citizen_id)
            return True
        return False
    
    def get_occupants(self) -> List[str]:
        """Get all current occupants."""
        return list(self.current_occupants)
    
    def is_open_now(self, current_time: time, day_of_week: int) -> bool:
        """Check if location is currently open."""
        # Homes are always accessible
        if self.category == LocationCategory.RESIDENTIAL:
            return True
        return self.opening_hours.is_open(current_time, day_of_week)
    
    def distance_to(self, other_pos: Tuple[float, float]) -> float:
        """Calculate distance to another position."""
        dx = self.position[0] - other_pos[0]
        dy = self.position[1] - other_pos[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def reset_daily(self) -> None:
        """Reset daily counters."""
        self.total_visitors_today = 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get location summary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.location_type.value,
            "category": self.category.value,
            "position": self.position,
            "occupancy": self.occupancy,
            "capacity": self.capacity,
            "current_occupants": len(self.current_occupants),
            "quality": self.quality,
            "is_private": self.is_private,
        }


@dataclass
class Neighborhood:
    """
    A neighborhood/district in the city.
    """
    
    id: str
    name: str
    
    # Locations in this neighborhood
    location_ids: Set[str] = field(default_factory=set)
    
    # Character
    affluence: float = 0.5  # 0-1 (poor to wealthy)
    safety: float = 0.7  # 0-1
    vibrancy: float = 0.5  # 0-1 (how lively/active)
    
    # Bounds
    min_x: float = 0.0
    max_x: float = 100.0
    min_y: float = 0.0
    max_y: float = 100.0
    
    def contains_position(self, pos: Tuple[float, float]) -> bool:
        """Check if a position is in this neighborhood."""
        x, y = pos
        return (
            self.min_x <= x <= self.max_x and
            self.min_y <= y <= self.max_y
        )
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get center point of neighborhood."""
        return (
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
        )


@dataclass
class CityMap:
    """
    The city map - manages all locations and spatial queries.
    """
    
    locations: Dict[str, Location] = field(default_factory=dict)
    neighborhoods: Dict[str, Neighborhood] = field(default_factory=dict)
    
    # Citizen locations
    citizen_locations: Dict[str, str] = field(default_factory=dict)
    
    # Grid size
    width: float = 1000.0
    height: float = 1000.0
    
    _next_id: int = 1
    
    def create_location(
        self,
        name: str,
        location_type: LocationType,
        position: Optional[Tuple[float, float]] = None,
        capacity: int = 50,
        **kwargs,
    ) -> Location:
        """Create a new location."""
        location_id = f"loc_{self._next_id}"
        self._next_id += 1
        
        if position is None:
            position = (
                random.uniform(0, self.width),
                random.uniform(0, self.height),
            )
        
        location = Location(
            id=location_id,
            name=name,
            location_type=location_type,
            position=position,
            capacity=capacity,
            **kwargs,
        )
        self.locations[location_id] = location
        
        # Add to neighborhood
        for neighborhood in self.neighborhoods.values():
            if neighborhood.contains_position(position):
                neighborhood.location_ids.add(location_id)
                break
        
        return location
    
    def create_neighborhood(
        self,
        name: str,
        bounds: Tuple[float, float, float, float],  # min_x, max_x, min_y, max_y
        affluence: float = 0.5,
        safety: float = 0.7,
    ) -> Neighborhood:
        """Create a new neighborhood."""
        neighborhood_id = f"nbhd_{len(self.neighborhoods) + 1}"
        
        neighborhood = Neighborhood(
            id=neighborhood_id,
            name=name,
            min_x=bounds[0],
            max_x=bounds[1],
            min_y=bounds[2],
            max_y=bounds[3],
            affluence=affluence,
            safety=safety,
        )
        self.neighborhoods[neighborhood_id] = neighborhood
        return neighborhood
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID."""
        return self.locations.get(location_id)
    
    def get_citizen_location(self, citizen_id: str) -> Optional[Location]:
        """Get where a citizen currently is."""
        location_id = self.citizen_locations.get(citizen_id)
        if location_id:
            return self.locations.get(location_id)
        return None
    
    def move_citizen(
        self,
        citizen_id: str,
        to_location_id: str,
    ) -> bool:
        """Move a citizen to a location."""
        # Leave current location
        current_loc_id = self.citizen_locations.get(citizen_id)
        if current_loc_id:
            current_loc = self.locations.get(current_loc_id)
            if current_loc:
                current_loc.leave(citizen_id)
        
        # Enter new location
        new_loc = self.locations.get(to_location_id)
        if not new_loc:
            return False
        
        if new_loc.enter(citizen_id):
            self.citizen_locations[citizen_id] = to_location_id
            return True
        return False
    
    def find_nearby(
        self,
        position: Tuple[float, float],
        radius: float,
        location_type: Optional[LocationType] = None,
        category: Optional[LocationCategory] = None,
    ) -> List[Location]:
        """Find locations near a position."""
        results = []
        
        for location in self.locations.values():
            if location.distance_to(position) > radius:
                continue
            
            if location_type and location.location_type != location_type:
                continue
            
            if category and location.category != category:
                continue
            
            results.append(location)
        
        # Sort by distance
        results.sort(key=lambda l: l.distance_to(position))
        return results
    
    def find_by_type(self, location_type: LocationType) -> List[Location]:
        """Find all locations of a type."""
        return [
            l for l in self.locations.values()
            if l.location_type == location_type
        ]
    
    def find_by_category(self, category: LocationCategory) -> List[Location]:
        """Find all locations in a category."""
        return [
            l for l in self.locations.values()
            if l.category == category
        ]
    
    def get_people_at_location(self, location_id: str) -> List[str]:
        """Get all people at a location."""
        location = self.locations.get(location_id)
        if location:
            return location.get_occupants()
        return []
    
    def get_people_nearby(
        self,
        citizen_id: str,
        radius: float = 10.0,
    ) -> List[str]:
        """Get people near a citizen."""
        current_loc = self.get_citizen_location(citizen_id)
        if not current_loc:
            return []
        
        nearby_people = []
        nearby_locations = self.find_nearby(current_loc.position, radius)
        
        for location in nearby_locations:
            for occupant_id in location.current_occupants:
                if occupant_id != citizen_id:
                    nearby_people.append(occupant_id)
        
        return nearby_people
    
    def calculate_travel_time(
        self,
        from_pos: Tuple[float, float],
        to_pos: Tuple[float, float],
        walking_speed: float = 5.0,  # km/h
    ) -> float:
        """Calculate travel time in hours."""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Convert grid units to km (assume 1 unit = 10 meters)
        distance_km = distance * 0.01
        
        return distance_km / walking_speed
    
    def get_random_public_location(self) -> Optional[Location]:
        """Get a random public location."""
        public = self.find_by_category(LocationCategory.PUBLIC)
        public.extend(self.find_by_category(LocationCategory.COMMERCIAL))
        
        if not public:
            return None
        return random.choice(public)
    
    def get_neighborhood(self, location_id: str) -> Optional[Neighborhood]:
        """Get the neighborhood a location is in."""
        for neighborhood in self.neighborhoods.values():
            if location_id in neighborhood.location_ids:
                return neighborhood
        return None
    
    def reset_daily(self) -> None:
        """Reset daily counters for all locations."""
        for location in self.locations.values():
            location.reset_daily()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get city map statistics."""
        total_capacity = sum(l.capacity for l in self.locations.values())
        total_occupants = sum(len(l.current_occupants) for l in self.locations.values())
        
        by_type = {}
        for location in self.locations.values():
            type_name = location.location_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        by_category = {}
        for location in self.locations.values():
            cat_name = location.category.value
            by_category[cat_name] = by_category.get(cat_name, 0) + 1
        
        return {
            "total_locations": len(self.locations),
            "total_capacity": total_capacity,
            "total_occupants": total_occupants,
            "occupancy_rate": total_occupants / total_capacity if total_capacity > 0 else 0,
            "by_type": by_type,
            "by_category": by_category,
            "neighborhoods": len(self.neighborhoods),
        }


def create_default_city_map(
    num_residential: int = 100,
    num_commercial: int = 30,
    num_workplaces: int = 20,
    num_public: int = 15,
) -> CityMap:
    """
    Create a default city map with various locations.
    
    Args:
        num_residential: Number of homes
        num_commercial: Number of shops/restaurants
        num_workplaces: Number of workplaces
        num_public: Number of public spaces
        
    Returns:
        Populated CityMap
    """
    city_map = CityMap()
    
    # Create neighborhoods
    city_map.create_neighborhood(
        "Downtown",
        (400, 600, 400, 600),
        affluence=0.7,
        safety=0.6,
    )
    city_map.create_neighborhood(
        "Suburbs North",
        (0, 400, 600, 1000),
        affluence=0.6,
        safety=0.8,
    )
    city_map.create_neighborhood(
        "Suburbs South",
        (0, 400, 0, 400),
        affluence=0.5,
        safety=0.7,
    )
    city_map.create_neighborhood(
        "Industrial District",
        (600, 1000, 0, 400),
        affluence=0.4,
        safety=0.5,
    )
    city_map.create_neighborhood(
        "University Area",
        (600, 1000, 600, 1000),
        affluence=0.5,
        safety=0.7,
    )
    
    # Create residential locations
    residential_types = [LocationType.HOUSE, LocationType.APARTMENT]
    for i in range(num_residential):
        loc_type = random.choice(residential_types)
        capacity = 4 if loc_type == LocationType.HOUSE else 2
        city_map.create_location(
            name=f"Home {i+1}",
            location_type=loc_type,
            capacity=capacity,
            is_private=True,
        )
    
    # Create commercial locations
    commercial_types = [
        LocationType.RESTAURANT,
        LocationType.CAFE,
        LocationType.GROCERY_STORE,
        LocationType.RETAIL_STORE,
        LocationType.BAR,
    ]
    commercial_names = {
        LocationType.RESTAURANT: ["Bella Italia", "Golden Dragon", "The Steakhouse", "Fresh Bites"],
        LocationType.CAFE: ["Morning Brew", "Coffee Corner", "Bean Scene", "Daily Grind"],
        LocationType.GROCERY_STORE: ["Fresh Mart", "City Grocers", "Quick Shop", "Value Foods"],
        LocationType.RETAIL_STORE: ["Fashion Forward", "Tech Hub", "Home & Garden", "Sports Zone"],
        LocationType.BAR: ["The Rusty Nail", "Blue Moon", "Happy Hour", "Night Owl"],
    }
    
    for i in range(num_commercial):
        loc_type = random.choice(commercial_types)
        names = commercial_names.get(loc_type, ["Shop"])
        name = random.choice(names)
        if i > len(names):
            name = f"{name} {i // len(names)}"
        
        city_map.create_location(
            name=name,
            location_type=loc_type,
            capacity=random.randint(20, 100),
        )
    
    # Create workplaces
    workplace_types = [LocationType.OFFICE_BUILDING, LocationType.FACTORY, LocationType.WAREHOUSE]
    for i in range(num_workplaces):
        loc_type = random.choice(workplace_types)
        city_map.create_location(
            name=f"Workplace {i+1}",
            location_type=loc_type,
            capacity=random.randint(50, 200),
            is_private=True,
        )
    
    # Create public spaces
    public_types = [LocationType.PARK, LocationType.LIBRARY, LocationType.COMMUNITY_CENTER]
    public_names = {
        LocationType.PARK: ["Central Park", "Riverside Park", "Oak Grove", "Sunny Meadows"],
        LocationType.LIBRARY: ["City Library", "Community Library", "Knowledge Center"],
        LocationType.COMMUNITY_CENTER: ["Community Hub", "Recreation Center", "Civic Center"],
    }
    
    for i in range(num_public):
        loc_type = random.choice(public_types)
        names = public_names.get(loc_type, ["Public Space"])
        name = random.choice(names) if i < len(names) else f"{names[0]} {i+1}"
        
        city_map.create_location(
            name=name,
            location_type=loc_type,
            capacity=random.randint(50, 500),
        )
    
    return city_map
