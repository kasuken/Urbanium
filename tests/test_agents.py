"""
Tests for the agent components.
"""

import pytest
import random
from urbanium.agents.citizen import Citizen, Resources, RoleBindings
from urbanium.agents.traits import Traits, Values, TraitType, ValueType
from urbanium.agents.needs import Needs, NeedType
from urbanium.agents.skills import Skills, SkillCategory
from urbanium.agents.social import SocialNetwork, SocialTie, RelationshipType
from urbanium.agents.decision import DecisionModel, DecisionStrategy


class TestCitizen:
    """Tests for the Citizen class."""
    
    def test_citizen_creation(self):
        """Test that a citizen can be created."""
        citizen = Citizen(name="Test Citizen", age=30)
        
        assert citizen.name == "Test Citizen"
        assert citizen.age == 30
        assert citizen.id is not None
    
    def test_citizen_default_resources(self):
        """Test default resource values."""
        citizen = Citizen()
        
        assert citizen.resources.money == 0.0
        assert citizen.resources.energy == 100.0
        assert citizen.resources.health == 100.0
    
    def test_citizen_employment_status(self):
        """Test employment status checks."""
        citizen = Citizen()
        
        assert not citizen.is_employed
        
        citizen.roles.job_id = "job_1"
        assert citizen.is_employed
    
    def test_citizen_housing_status(self):
        """Test housing status checks."""
        citizen = Citizen()
        
        assert not citizen.has_home
        
        citizen.roles.home_id = "house_1"
        assert citizen.has_home


class TestResources:
    """Tests for the Resources class."""
    
    def test_afford_check(self):
        """Test affordability checking."""
        resources = Resources(money=100.0)
        
        assert resources.can_afford(50.0)
        assert resources.can_afford(100.0)
        assert not resources.can_afford(150.0)
    
    def test_spending(self):
        """Test spending money."""
        resources = Resources(money=100.0)
        
        assert resources.spend(30.0)
        assert resources.money == 70.0
        
        assert not resources.spend(100.0)
        assert resources.money == 70.0  # Unchanged
    
    def test_earning(self):
        """Test earning money."""
        resources = Resources(money=50.0)
        
        resources.earn(25.0)
        assert resources.money == 75.0
    
    def test_energy_management(self):
        """Test energy consumption and restoration."""
        resources = Resources(energy=100.0)
        
        resources.consume_energy(30.0)
        assert resources.energy == 70.0
        
        resources.restore_energy(20.0)
        assert resources.energy == 90.0
        
        # Should cap at 100
        resources.restore_energy(50.0)
        assert resources.energy == 100.0
        
        # Should not go below 0
        resources.consume_energy(150.0)
        assert resources.energy == 0.0


class TestTraits:
    """Tests for the Traits class."""
    
    def test_traits_defaults(self):
        """Test default trait values."""
        traits = Traits()
        
        assert traits.openness == 0.5
        assert traits.conscientiousness == 0.5
    
    def test_traits_get(self):
        """Test getting trait values."""
        traits = Traits(openness=0.8)
        
        assert traits.get(TraitType.OPENNESS) == 0.8
    
    def test_traits_random(self):
        """Test random trait generation."""
        rng = random.Random(42)
        traits = Traits.random(rng)
        
        # All values should be between 0 and 1
        for value in traits.get_all().values():
            assert 0.0 <= value <= 1.0
    
    def test_personality_checks(self):
        """Test personality helper methods."""
        introvert = Traits(extraversion=0.2)
        assert introvert.is_introverted()
        
        extrovert = Traits(extraversion=0.8)
        assert not extrovert.is_introverted()
        
        risk_averse = Traits(neuroticism=0.8)
        assert risk_averse.is_risk_averse()


class TestNeeds:
    """Tests for the Needs class."""
    
    def test_needs_initialization(self):
        """Test needs initialization."""
        needs = Needs()
        
        assert needs.get(NeedType.FOOD) is not None
        assert needs.get(NeedType.REST) is not None
    
    def test_needs_update(self):
        """Test needs decay."""
        needs = Needs()
        initial_food = needs.get_level(NeedType.FOOD)
        
        needs.update()
        
        assert needs.get_level(NeedType.FOOD) < initial_food
    
    def test_needs_satisfaction(self):
        """Test satisfying needs."""
        needs = Needs()
        needs.update()  # Decay first
        needs.update()
        
        low_level = needs.get_level(NeedType.FOOD)
        needs.satisfy(NeedType.FOOD, 50.0)
        
        assert needs.get_level(NeedType.FOOD) > low_level
    
    def test_urgent_needs(self):
        """Test urgent need detection."""
        needs = Needs()
        
        # Force low need
        food_need = needs.get(NeedType.FOOD)
        food_need.current_level = 20.0
        
        urgent = needs.get_urgent_needs()
        assert food_need in urgent
    
    def test_most_pressing_need(self):
        """Test finding most pressing need."""
        needs = Needs()
        
        # Set food to be most pressing
        needs.get(NeedType.FOOD).current_level = 10.0
        needs.get(NeedType.REST).current_level = 50.0
        
        most_pressing = needs.get_most_pressing()
        assert most_pressing.need_type == NeedType.FOOD


class TestSkills:
    """Tests for the Skills class."""
    
    def test_skills_initialization(self):
        """Test skills initialization."""
        skills = Skills()
        
        assert skills.get("communication") is not None
    
    def test_skill_experience(self):
        """Test gaining experience."""
        skills = Skills()
        skill = skills.get("communication")
        initial_level = skill.level
        
        # Add experience
        skills.gain_experience("communication", 50.0)
        
        assert skill.experience > 0
    
    def test_skill_level_up(self):
        """Test leveling up."""
        skills = Skills()
        skill = skills.get("communication")
        skill.level = 0
        
        # Add enough experience to level up
        leveled = skill.add_experience(100.0)
        
        assert leveled
        assert skill.level == 1
    
    def test_requirements_check(self):
        """Test skill requirements checking."""
        skills = Skills()
        skills.get("communication").level = 30.0
        skills.get("technical").level = 20.0
        
        # Should meet these requirements
        assert skills.meets_requirements({"communication": 25.0})
        
        # Should not meet these
        assert not skills.meets_requirements({"communication": 50.0})


class TestSocialNetwork:
    """Tests for the SocialNetwork class."""
    
    def test_network_creation(self):
        """Test network creation."""
        network = SocialNetwork()
        
        assert network.network_size == 0
    
    def test_adding_ties(self):
        """Test adding social ties."""
        network = SocialNetwork()
        
        tie = SocialTie(
            target_id="citizen_2",
            relationship_type=RelationshipType.FRIEND,
            strength=0.5,
        )
        network.add_tie(tie)
        
        assert network.network_size == 1
        assert network.has_tie("citizen_2")
    
    def test_tie_strength_categories(self):
        """Test categorizing ties by strength."""
        network = SocialNetwork()
        
        network.add_tie(SocialTie("strong", RelationshipType.FRIEND, strength=0.9))
        network.add_tie(SocialTie("weak", RelationshipType.ACQUAINTANCE, strength=0.2))
        
        strong = network.get_strong_ties()
        weak = network.get_weak_ties()
        
        assert len(strong) == 1
        assert len(weak) == 1
    
    def test_social_capital(self):
        """Test social capital calculation."""
        network = SocialNetwork()
        
        # Empty network has zero capital
        assert network.get_social_capital() == 0.0
        
        # Add ties
        network.add_tie(SocialTie("friend", RelationshipType.FRIEND, strength=0.8))
        network.add_tie(SocialTie("family", RelationshipType.FAMILY, strength=0.9))
        
        # Should have positive capital
        assert network.get_social_capital() > 0.0


class TestDecisionModel:
    """Tests for the DecisionModel class."""
    
    def test_decision_model_creation(self):
        """Test decision model creation."""
        model = DecisionModel()
        
        assert model.strategy == DecisionStrategy.UTILITY
        assert len(model.utility_weights) > 0
    
    def test_different_strategies(self):
        """Test different decision strategies."""
        utility_model = DecisionModel(strategy=DecisionStrategy.UTILITY)
        rule_model = DecisionModel(strategy=DecisionStrategy.RULE_BASED)
        
        assert utility_model.strategy != rule_model.strategy
