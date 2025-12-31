"""
Prompt templates for AI decision making.

Builds context-rich prompts from agent state for LLM decision making.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from urbanium.agents.citizen import Citizen
    from urbanium.actions.base import Action


SYSTEM_PROMPT = """You are an AI decision-making system for a city simulation agent.

Your role is to decide what action an agent should take based on their current state, needs, personality, and circumstances.

IMPORTANT RULES:
1. You must choose from the available actions only
2. Consider the agent's needs - urgent needs take priority
3. Consider the agent's resources - don't choose actions they can't afford
4. Consider the agent's personality traits when weighing options
5. Be consistent with the agent's established patterns
6. Provide clear reasoning for your decisions

The agent's behavior should be realistic and grounded in their circumstances.
"""


@dataclass
class PromptBuilder:
    """
    Builds prompts for AI decision making.
    
    Creates context-rich prompts from agent state.
    """
    
    def build_decision_prompt(
        self,
        citizen: "Citizen",
        local_state: Dict,
        available_actions: List["Action"],
    ) -> str:
        """
        Build a prompt for action decision.
        
        Args:
            citizen: The citizen making the decision
            local_state: Local world state visible to the agent
            available_actions: List of available actions
            
        Returns:
            Formatted prompt string
        """
        sections = [
            self._build_identity_section(citizen),
            self._build_personality_section(citizen),
            self._build_needs_section(citizen),
            self._build_resources_section(citizen),
            self._build_situation_section(citizen, local_state),
            self._build_available_actions_section(available_actions),
            self._build_instruction_section(),
        ]
        
        return "\n\n".join(sections)
    
    def _build_identity_section(self, citizen: "Citizen") -> str:
        """Build the agent identity section."""
        employment = "employed" if citizen.is_employed else "unemployed"
        housing = "has a home" if citizen.has_home else "homeless"
        
        return f"""## AGENT IDENTITY
Name: {citizen.name}
Age: {citizen.age}
Status: {employment}, {housing}
Current Location: {citizen.current_location or "unknown"}"""
    
    def _build_personality_section(self, citizen: "Citizen") -> str:
        """Build the personality traits section."""
        traits = citizen.traits.get_all()
        values = citizen.values.get_all()
        
        # Interpret traits in human-readable terms
        trait_descriptions = []
        if traits["extraversion"] > 0.6:
            trait_descriptions.append("sociable and outgoing")
        elif traits["extraversion"] < 0.4:
            trait_descriptions.append("introverted and reserved")
        
        if traits["conscientiousness"] > 0.6:
            trait_descriptions.append("disciplined and organized")
        elif traits["conscientiousness"] < 0.4:
            trait_descriptions.append("flexible and spontaneous")
        
        if traits["neuroticism"] > 0.6:
            trait_descriptions.append("prone to worry and stress")
        elif traits["neuroticism"] < 0.4:
            trait_descriptions.append("emotionally stable and calm")
        
        if traits["agreeableness"] > 0.6:
            trait_descriptions.append("cooperative and trusting")
        
        if traits["openness"] > 0.6:
            trait_descriptions.append("curious and open to new experiences")
        
        personality_summary = ", ".join(trait_descriptions) if trait_descriptions else "balanced personality"
        
        # Get top values
        sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
        top_values = [v[0] for v in sorted_values[:2]]
        
        return f"""## PERSONALITY
Traits: {personality_summary}
Core Values: prioritizes {" and ".join(top_values)}
Trait Scores: O={traits['openness']:.1f} C={traits['conscientiousness']:.1f} E={traits['extraversion']:.1f} A={traits['agreeableness']:.1f} N={traits['neuroticism']:.1f}"""
    
    def _build_needs_section(self, citizen: "Citizen") -> str:
        """Build the current needs section."""
        needs = citizen.needs.get_all()
        
        # Categorize needs by urgency
        critical = []
        urgent = []
        normal = []
        
        for need_name, level in needs.items():
            if level < 20:
                critical.append(f"{need_name}: {level:.0f}% (CRITICAL)")
            elif level < 40:
                urgent.append(f"{need_name}: {level:.0f}% (urgent)")
            else:
                normal.append(f"{need_name}: {level:.0f}%")
        
        needs_text = ""
        if critical:
            needs_text += f"CRITICAL NEEDS: {', '.join(critical)}\n"
        if urgent:
            needs_text += f"Urgent needs: {', '.join(urgent)}\n"
        if normal:
            needs_text += f"Other needs: {', '.join(normal)}"
        
        overall = citizen.needs.get_overall_satisfaction()
        
        return f"""## CURRENT NEEDS
Overall satisfaction: {overall:.0%}
{needs_text}"""
    
    def _build_resources_section(self, citizen: "Citizen") -> str:
        """Build the resources section."""
        res = citizen.resources
        
        # Interpret money status
        if res.money < 20:
            money_status = "nearly broke"
        elif res.money < 100:
            money_status = "low funds"
        elif res.money < 500:
            money_status = "moderate savings"
        else:
            money_status = "financially comfortable"
        
        # Interpret energy status
        if res.energy < 20:
            energy_status = "exhausted"
        elif res.energy < 40:
            energy_status = "tired"
        elif res.energy < 70:
            energy_status = "normal"
        else:
            energy_status = "energized"
        
        return f"""## RESOURCES
Money: ${res.money:.2f} ({money_status})
Energy: {res.energy:.0f}% ({energy_status})
Health: {res.health:.0f}%"""
    
    def _build_situation_section(
        self,
        citizen: "Citizen",
        local_state: Dict,
    ) -> str:
        """Build the current situation section."""
        time_info = local_state.get("time", 0)
        if isinstance(time_info, int):
            hour = time_info % 24
            if 6 <= hour < 12:
                time_desc = f"morning (hour {hour})"
            elif 12 <= hour < 18:
                time_desc = f"afternoon (hour {hour})"
            elif 18 <= hour < 22:
                time_desc = f"evening (hour {hour})"
            else:
                time_desc = f"night (hour {hour})"
        else:
            time_desc = str(time_info)
        
        economy = local_state.get("economy", {})
        job_market = "unknown"
        if economy:
            available_jobs = economy.get("available_jobs", 0)
            if available_jobs > 50:
                job_market = "many opportunities"
            elif available_jobs > 20:
                job_market = "moderate opportunities"
            elif available_jobs > 0:
                job_market = "few opportunities"
            else:
                job_market = "no jobs available"
        
        situation_notes = []
        if not citizen.is_employed:
            situation_notes.append("Currently unemployed - finding work is important")
        if not citizen.has_home:
            situation_notes.append("Currently homeless - finding shelter is critical")
        if citizen.resources.energy < 30:
            situation_notes.append("Very tired - rest may be necessary soon")
        
        notes_text = "\n".join(f"- {note}" for note in situation_notes) if situation_notes else "No special circumstances"
        
        return f"""## CURRENT SITUATION
Time: {time_desc}
Job market: {job_market}
Notes:
{notes_text}"""
    
    def _build_available_actions_section(
        self,
        available_actions: List["Action"],
    ) -> str:
        """Build the available actions section."""
        action_lines = []
        
        for action in available_actions:
            cost = action.get_cost()
            energy = action.get_energy_cost()
            
            cost_str = f"${cost:.0f}" if cost > 0 else "free"
            energy_str = f"-{energy:.0f} energy" if energy > 0 else "no energy cost"
            
            # Get expected effects
            effects = action.get_expected_effects()
            effect_parts = []
            
            if "money_change" in effects and effects["money_change"] > 0:
                effect_parts.append(f"+${effects['money_change']:.0f}")
            if "energy_change" in effects and effects["energy_change"] > 0:
                effect_parts.append(f"+{effects['energy_change']:.0f} energy")
            if "needs_satisfied" in effects:
                for need, amt in effects["needs_satisfied"].items():
                    effect_parts.append(f"+{amt:.0f} {need}")
            
            effects_str = ", ".join(effect_parts) if effect_parts else "varies"
            
            action_lines.append(
                f"- {action.action_type.value}: cost={cost_str}, {energy_str}, benefits: {effects_str}"
            )
        
        return f"""## AVAILABLE ACTIONS
Choose ONE of the following actions:
{chr(10).join(action_lines)}"""
    
    def _build_instruction_section(self) -> str:
        """Build the instruction section."""
        return """## YOUR TASK
Based on the agent's personality, needs, resources, and current situation:
1. Assess the most pressing concerns
2. Consider which needs are most urgent
3. Evaluate which actions are feasible given resources
4. Choose the best action that aligns with the agent's personality and priorities
5. Explain your reasoning clearly

Remember: The agent should behave realistically. Critical needs (< 20%) should almost always be addressed first."""
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for decision making."""
        return SYSTEM_PROMPT
