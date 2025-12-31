"""
Tests for the action components.
"""

import pytest
from urbanium.actions.base import Action, ActionType
from urbanium.actions.work import WorkShiftAction
from urbanium.actions.rest import RestAction
from urbanium.actions.eat import EatAction, MealType
from urbanium.actions.socialize import SocializeAction, SocialActivity
from urbanium.agents.citizen import Citizen


class TestActionBase:
    """Tests for the base Action class."""
    
    def test_action_type_enum(self):
        """Test that all action types are defined."""
        assert ActionType.WORK_SHIFT.value == "work_shift"
        assert ActionType.REST.value == "rest"
        assert ActionType.EAT.value == "eat"
        assert ActionType.COMMUTE.value == "commute"
        assert ActionType.SOCIALIZE.value == "socialize"
        assert ActionType.JOB_SEARCH.value == "job_search"
        assert ActionType.HOUSING_CHANGE.value == "housing_change"


class TestWorkShiftAction:
    """Tests for the WorkShiftAction class."""
    
    def test_work_creation(self):
        """Test work action creation."""
        action = WorkShiftAction()
        
        assert action.action_type == ActionType.WORK_SHIFT
        assert action.energy_cost > 0
    
    def test_work_prerequisites_unemployed(self):
        """Test that unemployed citizens can't work."""
        action = WorkShiftAction()
        citizen = Citizen()
        
        # Unemployed
        assert not action.check_prerequisites(citizen, {})
    
    def test_work_prerequisites_employed(self):
        """Test that employed citizens can work."""
        action = WorkShiftAction()
        citizen = Citizen()
        citizen.roles.job_id = "job_1"
        citizen.resources.energy = 100.0
        
        assert action.check_prerequisites(citizen, {})
    
    def test_work_expected_effects(self):
        """Test expected effects calculation."""
        action = WorkShiftAction()
        effects = action.get_expected_effects()
        
        assert "money_change" in effects
        assert effects["money_change"] > 0
        assert "energy_change" in effects
        assert effects["energy_change"] < 0


class TestRestAction:
    """Tests for the RestAction class."""
    
    def test_rest_creation(self):
        """Test rest action creation."""
        action = RestAction()
        
        assert action.action_type == ActionType.REST
        assert action.energy_cost == 0
    
    def test_rest_always_available(self):
        """Test that rest is always available."""
        action = RestAction()
        citizen = Citizen()
        citizen.resources.energy = 0  # Even with no energy
        
        assert action.check_prerequisites(citizen, {})
    
    def test_rest_expected_effects(self):
        """Test expected effects calculation."""
        action = RestAction()
        effects = action.get_expected_effects()
        
        assert "energy_change" in effects
        assert effects["energy_change"] > 0
        assert "needs_satisfied" in effects
        assert "rest" in effects["needs_satisfied"]


class TestEatAction:
    """Tests for the EatAction class."""
    
    def test_eat_creation(self):
        """Test eat action creation."""
        action = EatAction()
        
        assert action.action_type == ActionType.EAT
        assert action.money_cost > 0
    
    def test_eat_meal_types(self):
        """Test different meal types have different costs."""
        basic = EatAction(meal_type=MealType.BASIC)
        quality = EatAction(meal_type=MealType.QUALITY)
        
        assert basic.money_cost < quality.money_cost
    
    def test_eat_prerequisites_affordability(self):
        """Test eat action affordability check."""
        action = EatAction(meal_type=MealType.STANDARD)
        
        poor_citizen = Citizen()
        poor_citizen.resources.money = 0.0
        assert not action.check_prerequisites(poor_citizen, {})
        
        rich_citizen = Citizen()
        rich_citizen.resources.money = 100.0
        assert action.check_prerequisites(rich_citizen, {})


class TestSocializeAction:
    """Tests for the SocializeAction class."""
    
    def test_socialize_creation(self):
        """Test socialize action creation."""
        action = SocializeAction()
        
        assert action.action_type == ActionType.SOCIALIZE
    
    def test_socialize_activities(self):
        """Test different social activities."""
        casual = SocializeAction(activity=SocialActivity.CASUAL)
        entertainment = SocializeAction(activity=SocialActivity.ENTERTAINMENT)
        
        assert casual.money_cost < entertainment.money_cost
    
    def test_socialize_expected_effects(self):
        """Test expected effects include social satisfaction."""
        action = SocializeAction()
        effects = action.get_expected_effects()
        
        assert "needs_satisfied" in effects
        assert "social" in effects["needs_satisfied"]
