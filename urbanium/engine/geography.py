"""
Geography - Spatial graph and district management.

The city is represented as a graph where nodes are locations
and edges are connections (roads, transit lines, etc.).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum


class LocationType(Enum):
    """Types of locations in the city."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED = "mixed"
    PUBLIC = "public"
    TRANSPORT = "transport"


class ConnectionType(Enum):
    """Types of connections between locations."""
    ROAD = "road"
    TRANSIT = "transit"
    PEDESTRIAN = "pedestrian"


@dataclass
class Location:
    """A location in the city graph."""
    id: str
    name: str
    location_type: LocationType
    district_id: str
    capacity: int = 100
    coordinates: Tuple[float, float] = (0.0, 0.0)
    properties: Dict = field(default_factory=dict)


@dataclass
class Connection:
    """A connection between two locations."""
    source_id: str
    target_id: str
    connection_type: ConnectionType
    travel_time: int = 1  # in ticks
    capacity: int = 100
    bidirectional: bool = True


@dataclass
class District:
    """A district containing multiple locations."""
    id: str
    name: str
    locations: List[str] = field(default_factory=list)
    properties: Dict = field(default_factory=dict)


@dataclass
class Geography:
    """
    Manages the spatial structure of the city.
    
    Uses an adjacency list representation for the graph.
    """
    
    locations: Dict[str, Location] = field(default_factory=dict)
    districts: Dict[str, District] = field(default_factory=dict)
    adjacency: Dict[str, List[Connection]] = field(default_factory=dict)
    
    def initialize(self) -> None:
        """Initialize the geography with default structure."""
        # Create a simple default city structure
        self._create_default_districts()
    
    def _create_default_districts(self) -> None:
        """Create default districts for a basic city."""
        # Downtown
        downtown = District(id="downtown", name="Downtown")
        self.districts["downtown"] = downtown
        
        # Residential areas
        for i in range(4):
            district = District(id=f"residential_{i}", name=f"Residential Area {i+1}")
            self.districts[district.id] = district
    
    def add_location(self, location: Location) -> None:
        """Add a location to the geography."""
        self.locations[location.id] = location
        if location.id not in self.adjacency:
            self.adjacency[location.id] = []
        
        # Add to district
        if location.district_id in self.districts:
            self.districts[location.district_id].locations.append(location.id)
    
    def add_connection(self, connection: Connection) -> None:
        """Add a connection between locations."""
        if connection.source_id not in self.adjacency:
            self.adjacency[connection.source_id] = []
        self.adjacency[connection.source_id].append(connection)
        
        # Add reverse connection if bidirectional
        if connection.bidirectional:
            reverse = Connection(
                source_id=connection.target_id,
                target_id=connection.source_id,
                connection_type=connection.connection_type,
                travel_time=connection.travel_time,
                capacity=connection.capacity,
                bidirectional=False  # Avoid infinite recursion
            )
            if connection.target_id not in self.adjacency:
                self.adjacency[connection.target_id] = []
            self.adjacency[connection.target_id].append(reverse)
    
    def get_neighbors(self, location_id: str) -> List[str]:
        """Get all neighboring locations."""
        if location_id not in self.adjacency:
            return []
        return [conn.target_id for conn in self.adjacency[location_id]]
    
    def get_travel_time(self, from_id: str, to_id: str) -> Optional[int]:
        """Get the travel time between two adjacent locations."""
        if from_id not in self.adjacency:
            return None
        
        for connection in self.adjacency[from_id]:
            if connection.target_id == to_id:
                return connection.travel_time
        return None
    
    def find_shortest_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """Find the shortest path between two locations using BFS."""
        if from_id not in self.locations or to_id not in self.locations:
            return None
        
        if from_id == to_id:
            return [from_id]
        
        visited: Set[str] = {from_id}
        queue: List[Tuple[str, List[str]]] = [(from_id, [from_id])]
        
        while queue:
            current, path = queue.pop(0)
            
            for neighbor in self.get_neighbors(current):
                if neighbor == to_id:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # No path found
