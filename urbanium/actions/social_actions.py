"""
Social Actions - Actions for social life and relationships.

New actions for:
- Dating and romance
- Family life
- Friendships
- Social events
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from ..engine.action import Action


@dataclass
class GoOnDateAction(Action):
    """
    Go on a romantic date with a partner.
    
    Prerequisites:
    - Must have a romantic partner (dating or higher)
    - Must have some money for the date
    - Must have energy
    
    Effects:
    - Increases relationship strength
    - Increases intimacy
    - Uses money and energy
    - Can lead to engagement or moving in together
    """
    
    name: str = "go_on_date"
    description: str = "Go on a romantic date with your partner"
    
    # Action parameters
    base_cost: float = 50.0
    base_duration: float = 3.0  # hours
    energy_cost: float = 0.15
    
    def check_prerequisites(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> bool:
        """Check if citizen can go on a date."""
        # Must have a romantic partner
        if not hasattr(citizen, "relationships"):
            return False
        
        partner = citizen.relationships.get_romantic_partner()
        if partner is None:
            return False
        
        # Must have enough money
        if hasattr(citizen, "finances"):
            if citizen.finances.cash < self.base_cost:
                return False
        
        # Must have energy
        if hasattr(citizen, "needs"):
            if citizen.needs.rest < 0.2:
                return False
        
        return True
    
    def execute(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute the date."""
        result = {
            "success": True,
            "action": self.name,
            "effects": {},
        }
        
        partner = citizen.relationships.get_romantic_partner()
        if not partner:
            result["success"] = False
            result["reason"] = "No romantic partner"
            return result
        
        # Update relationship
        from ..agents.relationships import InteractionOutcome
        partner.interact(InteractionOutcome.ROMANTIC, "Went on a date")
        
        result["effects"]["relationship"] = {
            "partner_id": partner.other_id,
            "partner_name": partner.other_name,
            "new_strength": partner.strength,
            "new_intimacy": partner.intimacy,
        }
        
        # Cost money
        if hasattr(citizen, "finances"):
            citizen.finances.cash -= self.base_cost
            result["effects"]["money_spent"] = self.base_cost
        
        # Use energy
        if hasattr(citizen, "needs"):
            citizen.needs.rest = max(0, citizen.needs.rest - self.energy_cost)
            result["effects"]["energy_used"] = self.energy_cost
        
        # Happiness boost
        if hasattr(citizen, "emotions"):
            from ..agents.emotions import EmotionType
            citizen.emotions.feel(EmotionType.JOY, 0.5)
            citizen.emotions.feel(EmotionType.LOVE, 0.6)
        
        # Memory
        if hasattr(citizen, "memory"):
            citizen.memory.remember_event(
                f"Went on a date with {partner.other_name}",
                tags=["date", "romance", partner.other_id],
                emotional_valence=0.7,
            )
        
        return result
    
    def calculate_utility(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> float:
        """Calculate utility of going on a date."""
        if not self.check_prerequisites(citizen, world_state):
            return 0.0
        
        utility = 0.3  # Base desire
        
        # Higher if relationship needs strengthening
        partner = citizen.relationships.get_romantic_partner()
        if partner and partner.strength < 0.6:
            utility += 0.3
        
        # Higher if lonely
        if hasattr(citizen, "needs") and citizen.needs.social < 0.4:
            utility += 0.2
        
        return min(1.0, utility)


@dataclass
class ProposeAction(Action):
    """
    Propose marriage to a partner.
    
    Prerequisites:
    - Must be dating or partners
    - Relationship must be strong enough
    - Must have money for a ring
    """
    
    name: str = "propose"
    description: str = "Propose marriage to your partner"
    
    ring_cost: float = 2000.0
    min_relationship_strength: float = 0.7
    min_intimacy: float = 0.6
    
    def check_prerequisites(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> bool:
        """Check if citizen can propose."""
        if not hasattr(citizen, "relationships"):
            return False
        
        partner = citizen.relationships.get_romantic_partner()
        if partner is None:
            return False
        
        # Already married?
        if citizen.relationships.get_spouse() is not None:
            return False
        
        # Relationship strong enough?
        if partner.strength < self.min_relationship_strength:
            return False
        if partner.intimacy < self.min_intimacy:
            return False
        
        # Can afford ring?
        if hasattr(citizen, "finances"):
            if citizen.finances.cash < self.ring_cost:
                return False
        
        return True
    
    def execute(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute the proposal."""
        result = {
            "success": True,
            "action": self.name,
            "effects": {},
        }
        
        partner = citizen.relationships.get_romantic_partner()
        if not partner:
            result["success"] = False
            return result
        
        # Determine if partner accepts
        # Based on their feelings (in a real sim, we'd check the partner's state)
        acceptance_chance = (partner.strength + partner.intimacy + partner.trust) / 3
        import random
        accepted = random.random() < acceptance_chance
        
        result["effects"]["accepted"] = accepted
        result["effects"]["partner_name"] = partner.other_name
        
        # Buy ring
        if hasattr(citizen, "finances"):
            citizen.finances.cash -= self.ring_cost
            result["effects"]["ring_cost"] = self.ring_cost
        
        if accepted:
            # Get engaged (will become spouse through marriage action)
            partner.relationship_type = "partner"  # Engaged
            partner.trust = min(1.0, partner.trust + 0.1)
            
            # Record life event
            if hasattr(citizen, "life_events"):
                from ..agents.life_events import LifeEventType
                citizen.life_events.record_engagement(
                    partner.other_id,
                    partner.other_name,
                )
            
            # Emotions
            if hasattr(citizen, "emotions"):
                from ..agents.emotions import EmotionType
                citizen.emotions.feel(EmotionType.JOY, 0.9)
                citizen.emotions.feel(EmotionType.LOVE, 1.0)
        else:
            # Rejection
            if hasattr(citizen, "emotions"):
                from ..agents.emotions import EmotionType
                citizen.emotions.feel(EmotionType.SADNESS, 0.8)
        
        return result
    
    def calculate_utility(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> float:
        """Calculate utility of proposing."""
        if not self.check_prerequisites(citizen, world_state):
            return 0.0
        
        partner = citizen.relationships.get_romantic_partner()
        if not partner:
            return 0.0
        
        # Higher if relationship is very strong
        utility = (partner.strength + partner.intimacy + partner.trust) / 3
        
        # Consider time together
        if partner.interaction_count > 50:
            utility += 0.1
        
        return min(1.0, utility * 0.5)  # Not too eager


@dataclass
class GetMarriedAction(Action):
    """
    Get married to fiancé.
    
    Prerequisites:
    - Must be engaged (partner relationship type)
    - Must have money for wedding
    """
    
    name: str = "get_married"
    description: str = "Get married to your fiancé"
    
    wedding_cost: float = 5000.0
    
    def check_prerequisites(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> bool:
        """Check if can get married."""
        if not hasattr(citizen, "relationships"):
            return False
        
        partner = citizen.relationships.get_romantic_partner()
        if partner is None:
            return False
        
        # Must be engaged (partner type)
        from ..agents.relationships import RelationshipType
        if partner.relationship_type != RelationshipType.PARTNER:
            return False
        
        # Already married?
        if citizen.relationships.get_spouse() is not None:
            return False
        
        return True
    
    def execute(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute the wedding."""
        result = {
            "success": True,
            "action": self.name,
            "effects": {},
        }
        
        partner = citizen.relationships.get_romantic_partner()
        if not partner:
            result["success"] = False
            return result
        
        # Get married
        partner.marry()
        
        result["effects"]["spouse_id"] = partner.other_id
        result["effects"]["spouse_name"] = partner.other_name
        
        # Cost
        if hasattr(citizen, "finances"):
            cost = min(self.wedding_cost, citizen.finances.cash)
            citizen.finances.cash -= cost
            result["effects"]["wedding_cost"] = cost
        
        # Record life event
        if hasattr(citizen, "life_events"):
            citizen.life_events.record_marriage(
                partner.other_id,
                partner.other_name,
            )
        
        # Emotions
        if hasattr(citizen, "emotions"):
            from ..agents.emotions import EmotionType
            citizen.emotions.feel(EmotionType.JOY, 1.0)
            citizen.emotions.feel(EmotionType.LOVE, 1.0)
        
        return result
    
    def calculate_utility(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> float:
        """Calculate utility of getting married."""
        if not self.check_prerequisites(citizen, world_state):
            return 0.0
        
        return 0.8  # High priority if engaged


@dataclass
class VisitFriendAction(Action):
    """
    Visit a friend.
    
    Prerequisites:
    - Must have at least one friend
    - Must have energy
    """
    
    name: str = "visit_friend"
    description: str = "Visit a friend for socializing"
    
    energy_cost: float = 0.1
    social_gain: float = 0.3
    
    def check_prerequisites(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> bool:
        """Check if can visit a friend."""
        if not hasattr(citizen, "relationships"):
            return False
        
        friends = citizen.relationships.get_friends()
        if not friends:
            return False
        
        if hasattr(citizen, "needs"):
            if citizen.needs.rest < 0.15:
                return False
        
        return True
    
    def execute(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute visiting a friend."""
        result = {
            "success": True,
            "action": self.name,
            "effects": {},
        }
        
        friends = citizen.relationships.get_friends()
        if not friends:
            result["success"] = False
            return result
        
        # Pick a friend (prefer ones not seen recently)
        import random
        friend = random.choice(friends)
        
        # Update relationship
        from ..agents.relationships import InteractionOutcome
        friend.interact(InteractionOutcome.BONDING, "Had a visit")
        
        result["effects"]["friend_id"] = friend.other_id
        result["effects"]["friend_name"] = friend.other_name
        
        # Social need
        if hasattr(citizen, "needs"):
            citizen.needs.social = min(1.0, citizen.needs.social + self.social_gain)
            citizen.needs.rest = max(0, citizen.needs.rest - self.energy_cost)
        
        # Emotions
        if hasattr(citizen, "emotions"):
            from ..agents.emotions import EmotionType
            citizen.emotions.feel(EmotionType.JOY, 0.4)
        
        return result
    
    def calculate_utility(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> float:
        """Calculate utility of visiting friend."""
        if not self.check_prerequisites(citizen, world_state):
            return 0.0
        
        utility = 0.2
        
        # Higher if lonely
        if hasattr(citizen, "needs"):
            if citizen.needs.social < 0.3:
                utility += 0.4
            elif citizen.needs.social < 0.5:
                utility += 0.2
        
        return min(1.0, utility)


@dataclass
class AttendEventAction(Action):
    """
    Attend a social event.
    
    Prerequisites:
    - Must have energy
    - May require money depending on event
    """
    
    name: str = "attend_event"
    description: str = "Attend a social event in the city"
    
    energy_cost: float = 0.2
    money_cost: float = 20.0
    social_gain: float = 0.35
    
    def check_prerequisites(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> bool:
        """Check if can attend event."""
        if hasattr(citizen, "needs"):
            if citizen.needs.rest < 0.2:
                return False
        
        if hasattr(citizen, "finances"):
            if citizen.finances.cash < self.money_cost:
                return False
        
        return True
    
    def execute(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute attending an event."""
        result = {
            "success": True,
            "action": self.name,
            "effects": {},
        }
        
        # Cost
        if hasattr(citizen, "finances"):
            citizen.finances.cash -= self.money_cost
            result["effects"]["money_spent"] = self.money_cost
        
        # Social gain
        if hasattr(citizen, "needs"):
            citizen.needs.social = min(1.0, citizen.needs.social + self.social_gain)
            citizen.needs.rest = max(0, citizen.needs.rest - self.energy_cost)
        
        # Chance to meet new people
        import random
        if random.random() < 0.3:
            result["effects"]["met_someone"] = True
        
        # Emotions
        if hasattr(citizen, "emotions"):
            from ..agents.emotions import EmotionType
            citizen.emotions.feel(EmotionType.JOY, 0.3)
            citizen.emotions.feel(EmotionType.ANTICIPATION, 0.2)
        
        return result
    
    def calculate_utility(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> float:
        """Calculate utility of attending event."""
        if not self.check_prerequisites(citizen, world_state):
            return 0.0
        
        utility = 0.15
        
        if hasattr(citizen, "needs"):
            if citizen.needs.social < 0.4:
                utility += 0.3
        
        # Extroverts like events more
        if hasattr(citizen, "personality"):
            extraversion = citizen.personality.traits.get("extraversion", 0.5)
            utility += extraversion * 0.2
        
        return min(1.0, utility)


@dataclass
class GoShoppingAction(Action):
    """
    Go shopping for goods or fun.
    
    Prerequisites:
    - Must have money
    - Must have energy
    """
    
    name: str = "go_shopping"
    description: str = "Go shopping at stores"
    
    min_spend: float = 20.0
    max_spend: float = 200.0
    energy_cost: float = 0.15
    
    def check_prerequisites(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> bool:
        """Check if can go shopping."""
        if hasattr(citizen, "finances"):
            if citizen.finances.cash < self.min_spend:
                return False
        
        if hasattr(citizen, "needs"):
            if citizen.needs.rest < 0.15:
                return False
        
        return True
    
    def execute(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute shopping trip."""
        result = {
            "success": True,
            "action": self.name,
            "effects": {},
        }
        
        # Determine spending (based on available cash)
        import random
        if hasattr(citizen, "finances"):
            max_affordable = min(citizen.finances.cash, self.max_spend)
            spent = random.uniform(self.min_spend, max_affordable)
            citizen.finances.cash -= spent
            result["effects"]["money_spent"] = spent
        
        # Energy
        if hasattr(citizen, "needs"):
            citizen.needs.rest = max(0, citizen.needs.rest - self.energy_cost)
        
        # Happiness from shopping
        if hasattr(citizen, "emotions"):
            from ..agents.emotions import EmotionType
            citizen.emotions.feel(EmotionType.JOY, 0.25)
        
        return result
    
    def calculate_utility(
        self,
        citizen: Any,
        world_state: Dict[str, Any],
    ) -> float:
        """Calculate utility of shopping."""
        if not self.check_prerequisites(citizen, world_state):
            return 0.0
        
        utility = 0.1  # Base desire
        
        # Lower if finances are tight
        if hasattr(citizen, "finances"):
            if citizen.finances.cash < 200:
                utility *= 0.5
            elif citizen.finances.cash > 1000:
                utility += 0.1
        
        return min(1.0, utility)


# Export all actions
def get_social_actions() -> List[Action]:
    """Get all social actions."""
    return [
        GoOnDateAction(),
        ProposeAction(),
        GetMarriedAction(),
        VisitFriendAction(),
        AttendEventAction(),
        GoShoppingAction(),
    ]
