"""
Tests for the core engine components.
"""

import pytest
from urbanium.engine.world import World
from urbanium.engine.tick import TickLoop
from urbanium.engine.time import TimeSystem, TimeOfDay
from urbanium.engine.state import WorldState


class TestWorld:
    """Tests for the World class."""
    
    def test_world_creation(self):
        """Test that a world can be created with default settings."""
        world = World()
        assert world.seed == 42
        assert world.state is not None
        assert not world.state.initialized
    
    def test_world_initialization(self):
        """Test that world initialization sets up all systems."""
        world = World(seed=123)
        world.initialize()
        
        assert world.state.initialized
        assert world.time.current_tick == 0
    
    def test_world_determinism(self):
        """Test that same seed produces same random numbers."""
        world1 = World(seed=42)
        world2 = World(seed=42)
        
        rng1 = world1.get_random()
        rng2 = world2.get_random()
        
        # Should produce identical sequences
        for _ in range(10):
            assert rng1.random() == rng2.random()
    
    def test_world_different_seeds(self):
        """Test that different seeds produce different random numbers."""
        world1 = World(seed=42)
        world2 = World(seed=43)
        
        rng1 = world1.get_random()
        rng2 = world2.get_random()
        
        # Should produce different sequences
        values1 = [rng1.random() for _ in range(10)]
        values2 = [rng2.random() for _ in range(10)]
        
        assert values1 != values2


class TestTimeSystem:
    """Tests for the TimeSystem class."""
    
    def test_time_initialization(self):
        """Test time system initialization."""
        time = TimeSystem()
        time.initialize()
        
        assert time.current_tick == 0
        assert time.current_day == 0
    
    def test_time_advance(self):
        """Test time advancement."""
        time = TimeSystem()
        time.initialize()
        
        time.advance()
        assert time.current_tick == 1
        
        time.advance(5)
        assert time.current_tick == 6
    
    def test_time_of_day(self):
        """Test time of day calculation."""
        time = TimeSystem(ticks_per_day=24)
        time.initialize()
        
        # Morning (6-12)
        time.current_tick = 8
        assert time.time_of_day == TimeOfDay.MORNING
        
        # Afternoon (12-18)
        time.current_tick = 14
        assert time.time_of_day == TimeOfDay.AFTERNOON
        
        # Evening (18-22)
        time.current_tick = 20
        assert time.time_of_day == TimeOfDay.EVENING
        
        # Night (22-6)
        time.current_tick = 2
        assert time.time_of_day == TimeOfDay.NIGHT
    
    def test_work_hours(self):
        """Test work hours detection."""
        time = TimeSystem(ticks_per_day=24)
        
        # During work hours
        time.current_tick = 10
        assert time.is_work_hours
        
        # Outside work hours
        time.current_tick = 20
        assert not time.is_work_hours
    
    def test_weekend_detection(self):
        """Test weekend detection."""
        time = TimeSystem(ticks_per_day=24)
        
        # Monday (day 0)
        time.current_tick = 0
        assert not time.is_weekend
        
        # Saturday (day 5)
        time.current_tick = 5 * 24
        assert time.is_weekend


class TestWorldState:
    """Tests for the WorldState class."""
    
    def test_state_creation(self):
        """Test that world state can be created."""
        state = WorldState()
        assert state.version == 0
        assert not state.initialized
    
    def test_state_copy(self):
        """Test that state can be copied."""
        state = WorldState()
        state.current_tick = 100
        state.market.labor_demand["engineer"] = 10
        
        copy = state.copy()
        
        # Copies should be equal but independent
        assert copy.current_tick == state.current_tick
        assert copy.market.labor_demand == state.market.labor_demand
        
        # Modifying copy shouldn't affect original
        copy.current_tick = 200
        assert state.current_tick == 100
    
    def test_version_increment(self):
        """Test version incrementing."""
        state = WorldState()
        assert state.version == 0
        
        state.increment_version()
        assert state.version == 1
