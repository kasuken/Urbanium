"""
Example: Full Life Simulation Demo

This example demonstrates all the new life simulation systems:
- Memory (citizens remember events and people)
- Emotions (Plutchik's wheel + PAD mood model)
- Relationships (friendships, romance, family)
- Life Events (marriage, children, career)
- Life Cycle (aging through life stages)
- City Locations (where citizens go)
- Workplaces (jobs and careers)
"""

import asyncio
from datetime import datetime
from urbanium.agents.citizen import Citizen
from urbanium.agents.traits import Traits
from urbanium.agents.emotions import EmotionType
from urbanium.agents.relationships import InteractionOutcome, RelationshipType
from urbanium.agents.life_events import LifeEventType
from urbanium.agents.lifecycle import LifeStage
from urbanium.city.locations import create_default_city_map, LocationType
from urbanium.city.workplace import JobMarket, IndustryType


def create_citizen(name: str, age: float = 25.0) -> Citizen:
    """Create a citizen with given name and age."""
    citizen = Citizen(
        name=name,
        age=age,
    )
    # Give some starting money
    citizen.finances.cash = 1000.0
    citizen.resources.money = 1000.0
    return citizen


def demo_memory_system():
    """Demonstrate the memory system."""
    print("\n" + "="*60)
    print("MEMORY SYSTEM DEMO")
    print("="*60)
    
    alice = create_citizen("Alice", 28)
    
    # Remember events
    alice.memory.remember_event(
        "Had a great day at work today",
        tags=["work", "positive"],
        emotional_valence=0.7,
    )
    
    alice.memory.remember_event(
        "Met Bob at the coffee shop",
        tags=["meeting", "bob"],
        emotional_valence=0.5,
    )
    
    alice.memory.remember_event(
        "Got a raise at work!",
        tags=["work", "promotion"],
        emotional_valence=0.9,
    )
    
    # Learn facts
    alice.memory.learn_fact(
        "Bob works at TechCorp",
        category="people",
        entity_id="bob_123",
    )
    
    # Recall memories
    print(f"\n{alice.name}'s Memories:")
    print(f"  Total memories: {len(alice.memory.memories)}")
    
    work_memories = alice.memory.recall_by_tag("work")
    print(f"  Work memories: {len(work_memories)}")
    for mem in work_memories:
        print(f"    - {mem.content}")
    
    # Check what Alice knows about Bob
    bob_impression = alice.memory.get_impression_of("bob_123")
    print(f"\n  Impression of Bob: {bob_impression:.2f}")


def demo_emotion_system():
    """Demonstrate the emotion system."""
    print("\n" + "="*60)
    print("EMOTION SYSTEM DEMO")
    print("="*60)
    
    bob = create_citizen("Bob", 30)
    
    print(f"\n{bob.name}'s Initial Mood:")
    print(f"  {bob.emotions.mood}")
    
    # Experience emotions
    bob.emotions.feel(EmotionType.JOY, 0.8)
    print(f"\nAfter feeling Joy (0.8):")
    print(f"  Active emotions: {[e.emotion_type.value for e in bob.emotions.active_emotions]}")
    
    bob.emotions.feel(EmotionType.LOVE, 0.6)
    print(f"\nAfter also feeling Love (0.6):")
    print(f"  Active emotions: {[e.emotion_type.value for e in bob.emotions.active_emotions]}")
    print(f"  Dominant emotion: {bob.emotions.dominant_emotion}")
    
    # React to events
    bob.emotions.react_to_event("promotion", 0.9)
    print(f"\nAfter reacting to 'promotion':")
    print(f"  Active emotions: {[e.emotion_type.value for e in bob.emotions.active_emotions]}")
    
    # Check decision modifiers
    modifiers = bob.emotions.get_decision_modifier()
    print(f"\nDecision modifiers from emotions:")
    for key, value in modifiers.items():
        print(f"  {key}: {value:+.2f}")


def demo_relationship_system():
    """Demonstrate the relationship system."""
    print("\n" + "="*60)
    print("RELATIONSHIP SYSTEM DEMO")
    print("="*60)
    
    carol = create_citizen("Carol", 26)
    david_id = "david_456"
    
    # First meeting
    carol.meet(david_id, "David")
    print(f"\n{carol.name} meets David:")
    rel = carol.relationships.get(david_id)
    print(f"  Relationship type: {rel.relationship_type.value}")
    print(f"  Strength: {rel.strength:.2f}")
    
    # Multiple positive interactions -> friendship
    for i in range(5):
        rel.interact(InteractionOutcome.POSITIVE, f"Had lunch together #{i+1}")
    
    print(f"\nAfter 5 positive interactions:")
    print(f"  Relationship type: {rel.relationship_type.value}")
    print(f"  Strength: {rel.strength:.2f}")
    print(f"  Trust: {rel.trust:.2f}")
    
    # Romantic interactions
    rel.interact(InteractionOutcome.ROMANTIC, "First date")
    rel.interact(InteractionOutcome.ROMANTIC, "Second date")
    rel.interact(InteractionOutcome.ROMANTIC, "Third date")
    
    print(f"\nAfter romantic interactions:")
    print(f"  Relationship type: {rel.relationship_type.value}")
    print(f"  Attraction: {rel.attraction:.2f}")
    print(f"  Intimacy: {rel.intimacy:.2f}")
    
    # More bonding
    for _ in range(10):
        rel.interact(InteractionOutcome.BONDING, "Deep conversation")
        rel.interact(InteractionOutcome.ROMANTIC, "Spent time together")
    
    print(f"\nAfter more bonding:")
    print(f"  Relationship type: {rel.relationship_type.value}")
    print(f"  Strength: {rel.strength:.2f}")
    
    # Marriage
    rel.marry()
    print(f"\nAfter marriage:")
    print(f"  Relationship type: {rel.relationship_type.value}")
    print(f"  Is romantic: {rel.is_romantic}")
    print(f"  Is family: {rel.is_family}")


def demo_life_events():
    """Demonstrate life events."""
    print("\n" + "="*60)
    print("LIFE EVENTS DEMO")
    print("="*60)
    
    emma = create_citizen("Emma", 28)
    
    # Record various life events
    emma.life_events.record_job_start("TechCorp", "Software Engineer", 75000)
    emma.life_events.record_first_meeting("frank_789", "Frank")
    emma.life_events.record_start_dating("frank_789", "Frank")
    emma.life_events.record_engagement("frank_789", "Frank")
    emma.life_events.record_marriage("frank_789", "Frank")
    emma.life_events.record_move("Downtown Apartment", "Suburban House")
    emma.life_events.record_birth("baby_001", "Baby Emma Jr", "frank_789")
    emma.life_events.record_promotion("Senior Engineer", 15000)
    
    print(f"\n{emma.name}'s Life Events:")
    for event in emma.life_events.event_history:
        print(f"  [{event.event_type.value}] {event.description}")
    
    print(f"\nLife Summary:")
    summary = emma.life_events.get_life_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


def demo_lifecycle():
    """Demonstrate life cycle and aging."""
    print("\n" + "="*60)
    print("LIFE CYCLE DEMO")
    print("="*60)
    
    george = create_citizen("George", 0)  # Newborn
    
    print(f"\n{george.name}'s Life Cycle:")
    print(f"  Current age: {george.age}")
    print(f"  Life stage: {george.lifecycle.life_stage.value}")
    
    ages_to_check = [5, 15, 20, 30, 50, 70]
    
    for target_age in ages_to_check:
        years_to_age = target_age - george.age
        events = george.age_by(years_to_age)
        
        print(f"\n  At age {george.age:.0f}:")
        print(f"    Life stage: {george.lifecycle.life_stage.value}")
        print(f"    Can work: {george.lifecycle.stats.can_work}")
        print(f"    Can marry: {george.lifecycle.stats.can_marry}")
        print(f"    Physical health: {george.lifecycle.stats.physical_health:.2f}")
        print(f"    Wisdom: {george.lifecycle.stats.wisdom:.2f}")
        if events:
            print(f"    Events: {events}")


def demo_city_and_work():
    """Demonstrate city locations and workplaces."""
    print("\n" + "="*60)
    print("CITY & WORKPLACE DEMO")
    print("="*60)
    
    # Create city
    city_map = create_default_city_map(
        num_residential=20,
        num_commercial=10,
        num_workplaces=5,
        num_public=5,
    )
    
    print(f"\nCity Statistics:")
    stats = city_map.get_statistics()
    print(f"  Total locations: {stats['total_locations']}")
    print(f"  Neighborhoods: {stats['neighborhoods']}")
    print(f"  By category:")
    for cat, count in stats['by_category'].items():
        print(f"    {cat}: {count}")
    
    # Create job market
    job_market = JobMarket()
    
    # Create companies
    tech_company = job_market.create_company(
        "TechCorp",
        IndustryType.TECHNOLOGY,
        max_employees=50,
    )
    tech_company.open_position("Software Engineer", 5)
    tech_company.open_position("Manager", 2)
    
    retail_company = job_market.create_company(
        "RetailMart",
        IndustryType.RETAIL,
        max_employees=100,
    )
    retail_company.open_position("Sales Associate", 20)
    retail_company.open_position("Store Manager", 3)
    
    print(f"\nJob Market:")
    print(f"  Companies: {len(job_market.companies)}")
    
    # Hire a citizen
    helen = create_citizen("Helen", 25)
    employee = job_market.hire_citizen(
        helen.id,
        helen.name,
        tech_company.id,
        "Software Engineer",
        70000,
    )
    
    print(f"\n{helen.name} hired at TechCorp:")
    print(f"  Position: {employee.position}")
    print(f"  Salary: ${employee.salary:,.0f}")
    
    # Find available jobs
    print(f"\nAvailable Jobs:")
    jobs = job_market.find_jobs()
    for company, position, pos_obj in jobs[:5]:
        print(f"  {company.name}: {position}")
    
    # Move citizen to a location
    home = city_map.find_by_type(LocationType.HOUSE)[0]
    city_map.move_citizen(helen.id, home.id)
    
    print(f"\n{helen.name}'s Location:")
    current_loc = city_map.get_citizen_location(helen.id)
    print(f"  At: {current_loc.name} ({current_loc.location_type.value})")


def demo_full_day():
    """Demonstrate a full day in a citizen's life."""
    print("\n" + "="*60)
    print("FULL DAY SIMULATION")
    print("="*60)
    
    # Create citizen with full setup
    iris = create_citizen("Iris", 32)
    iris.finances.cash = 5000
    
    # Setup relationships
    iris.meet("jack_001", "Jack")
    spouse_rel = iris.relationships.get("jack_001")
    spouse_rel.marry()
    iris.roles.spouse_id = "jack_001"
    
    iris.meet("kate_002", "Kate")  # Friend
    for _ in range(5):
        iris.relationships.interact_with(
            "kate_002", "Kate", InteractionOutcome.POSITIVE, "Chat"
        )
    
    print(f"\n{iris.name}'s Day:")
    print(f"  Age: {iris.age}")
    print(f"  Married to: Jack")
    print(f"  Cash: ${iris.finances.cash:,.0f}")
    
    # Morning routine
    print("\n  Morning:")
    iris.memory.remember_event("Woke up feeling refreshed", tags=["morning"])
    iris.emotions.feel(EmotionType.JOY, 0.3)
    print(f"    Mood: {iris.emotions.mood.pleasure:.2f} pleasure")
    
    # Work
    print("\n  At Work:")
    iris.memory.remember_event("Had productive meeting", tags=["work"])
    iris.emotions.feel(EmotionType.ANTICIPATION, 0.4)
    print(f"    Active emotions: {[e.emotion_type.value for e in iris.emotions.active_emotions]}")
    
    # Social lunch
    print("\n  Lunch with Kate:")
    iris.relationships.interact_with(
        "kate_002", "Kate", InteractionOutcome.BONDING, "Shared stories"
    )
    kate_rel = iris.relationships.get("kate_002")
    print(f"    Friendship strength: {kate_rel.strength:.2f}")
    
    # Evening with spouse
    print("\n  Evening with Jack:")
    spouse_rel.interact(InteractionOutcome.ROMANTIC, "Nice dinner together")
    iris.emotions.feel(EmotionType.LOVE, 0.7)
    print(f"    Marriage strength: {spouse_rel.strength:.2f}")
    
    # End of day summary
    print(f"\n  End of Day Summary:")
    print(f"    Memories created: {len(iris.memory.memories)}")
    print(f"    Relationships: {iris.relationships.get_summary()['total']}")
    print(f"    Current mood: P={iris.emotions.mood.pleasure:.2f}, A={iris.emotions.mood.arousal:.2f}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("URBANIUM LIFE SIMULATION DEMO")
    print("="*60)
    print("This demo showcases all the life simulation systems.")
    
    demo_memory_system()
    demo_emotion_system()
    demo_relationship_system()
    demo_life_events()
    demo_lifecycle()
    demo_city_and_work()
    demo_full_day()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nAll life simulation systems are working!")
    print("Citizens can now:")
    print("  - Remember events and people")
    print("  - Feel and express emotions")
    print("  - Form relationships (friendships, romance, family)")
    print("  - Experience life events (marriage, children, career)")
    print("  - Age through life stages")
    print("  - Work at companies and earn money")
    print("  - Visit locations around the city")


if __name__ == "__main__":
    main()
