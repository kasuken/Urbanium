"""
Emotions & Mood System - How citizens feel.

Citizens have:
- Emotions: Temporary emotional states (joy, anger, fear, etc.)
- Mood: Long-term emotional baseline
- Emotional reactions: How events affect feelings
- Emotional influence: How feelings affect decisions

Based on psychological models (Plutchik's wheel, PAD model).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple
import math
import random


class EmotionType(Enum):
    """Primary emotions (Plutchik's wheel)."""
    # Primary emotions
    JOY = "joy"
    TRUST = "trust"
    FEAR = "fear"
    SURPRISE = "surprise"
    SADNESS = "sadness"
    DISGUST = "disgust"
    ANGER = "anger"
    ANTICIPATION = "anticipation"
    
    # Secondary emotions (combinations)
    LOVE = "love"           # Joy + Trust
    SUBMISSION = "submission"  # Trust + Fear
    AWE = "awe"             # Fear + Surprise
    DISAPPROVAL = "disapproval"  # Surprise + Sadness
    REMORSE = "remorse"     # Sadness + Disgust
    CONTEMPT = "contempt"   # Disgust + Anger
    AGGRESSIVENESS = "aggressiveness"  # Anger + Anticipation
    OPTIMISM = "optimism"   # Anticipation + Joy


@dataclass
class Emotion:
    """
    A single emotion with intensity and decay.
    
    Attributes:
        emotion_type: Type of emotion
        intensity: How strong (0-1)
        source: What caused this emotion
        timestamp: When it started
        decay_rate: How fast it fades
    """
    
    emotion_type: EmotionType
    intensity: float = 0.5
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    decay_rate: float = 0.1  # Per hour
    
    def decay(self, hours: float) -> None:
        """Apply time-based decay."""
        self.intensity = max(0.0, self.intensity - self.decay_rate * hours)
    
    def intensify(self, amount: float) -> None:
        """Increase emotion intensity."""
        self.intensity = min(1.0, self.intensity + amount)
    
    @property
    def is_faded(self) -> bool:
        """Check if emotion has faded away."""
        return self.intensity < 0.05


@dataclass
class Mood:
    """
    Long-term emotional state using PAD model.
    
    Pleasure-Arousal-Dominance model:
    - Pleasure: Happy vs Unhappy (-1 to 1)
    - Arousal: Excited vs Calm (-1 to 1)
    - Dominance: In control vs Submissive (-1 to 1)
    """
    
    pleasure: float = 0.0
    arousal: float = 0.0
    dominance: float = 0.0
    
    # Mood changes slowly
    change_rate: float = 0.1
    
    def update_from_emotion(self, emotion: Emotion) -> None:
        """Update mood based on current emotion."""
        # Emotion to PAD mapping
        pad_map = {
            EmotionType.JOY: (0.8, 0.5, 0.3),
            EmotionType.TRUST: (0.6, -0.2, 0.2),
            EmotionType.FEAR: (-0.6, 0.7, -0.5),
            EmotionType.SURPRISE: (0.2, 0.8, 0.0),
            EmotionType.SADNESS: (-0.7, -0.4, -0.3),
            EmotionType.DISGUST: (-0.5, 0.3, 0.2),
            EmotionType.ANGER: (-0.4, 0.8, 0.5),
            EmotionType.ANTICIPATION: (0.4, 0.5, 0.4),
            EmotionType.LOVE: (0.9, 0.4, 0.2),
            EmotionType.OPTIMISM: (0.7, 0.3, 0.4),
            EmotionType.REMORSE: (-0.6, -0.2, -0.4),
            EmotionType.CONTEMPT: (-0.3, 0.2, 0.6),
        }
        
        if emotion.emotion_type in pad_map:
            p, a, d = pad_map[emotion.emotion_type]
            influence = emotion.intensity * self.change_rate
            
            self.pleasure = self._blend(self.pleasure, p, influence)
            self.arousal = self._blend(self.arousal, a, influence)
            self.dominance = self._blend(self.dominance, d, influence)
    
    def _blend(self, current: float, target: float, rate: float) -> float:
        """Blend current value toward target."""
        return current + (target - current) * rate
    
    def decay_toward_baseline(self, baseline: "Mood", hours: float) -> None:
        """Slowly return to baseline mood."""
        rate = 0.02 * hours
        self.pleasure = self._blend(self.pleasure, baseline.pleasure, rate)
        self.arousal = self._blend(self.arousal, baseline.arousal, rate)
        self.dominance = self._blend(self.dominance, baseline.dominance, rate)
    
    @property
    def label(self) -> str:
        """Get a human-readable mood label."""
        if self.pleasure > 0.5 and self.arousal > 0.3:
            return "excited"
        elif self.pleasure > 0.5 and self.arousal < -0.3:
            return "content"
        elif self.pleasure > 0.3:
            return "happy"
        elif self.pleasure < -0.5 and self.arousal > 0.3:
            return "angry"
        elif self.pleasure < -0.5 and self.arousal < -0.3:
            return "depressed"
        elif self.pleasure < -0.3:
            return "sad"
        elif self.arousal > 0.5:
            return "tense"
        elif self.arousal < -0.5:
            return "calm"
        else:
            return "neutral"
    
    @property
    def valence(self) -> float:
        """Get overall positive/negative valence."""
        return self.pleasure


@dataclass
class EmotionalState:
    """
    Complete emotional state for a citizen.
    
    Manages current emotions, mood, and emotional reactions.
    """
    
    # Current active emotions
    emotions: Dict[EmotionType, Emotion] = field(default_factory=dict)
    
    # Current mood (PAD)
    mood: Mood = field(default_factory=Mood)
    
    # Baseline mood (personality-based)
    baseline_mood: Mood = field(default_factory=Mood)
    
    # Emotional sensitivity (how strongly events affect us)
    sensitivity: float = 0.5
    
    # Emotional stability (how quickly emotions fade)
    stability: float = 0.5
    
    # Recent emotional experiences
    emotional_history: List[Tuple[datetime, EmotionType, float]] = field(default_factory=list)
    max_history: int = 50
    
    def feel(
        self,
        emotion_type: EmotionType,
        intensity: float,
        source: str = "",
    ) -> Emotion:
        """
        Feel an emotion.
        
        Args:
            emotion_type: What emotion
            intensity: How strong (0-1)
            source: What caused it
            
        Returns:
            The Emotion object
        """
        # Apply sensitivity
        adjusted_intensity = min(1.0, intensity * (0.5 + self.sensitivity))
        
        # If we already feel this emotion, intensify it
        if emotion_type in self.emotions:
            existing = self.emotions[emotion_type]
            existing.intensify(adjusted_intensity * 0.5)
            existing.source = source
            return existing
        
        # Create new emotion
        decay_rate = 0.1 * (0.5 + self.stability)  # More stable = faster decay
        emotion = Emotion(
            emotion_type=emotion_type,
            intensity=adjusted_intensity,
            source=source,
            decay_rate=decay_rate,
        )
        
        self.emotions[emotion_type] = emotion
        
        # Record in history
        self.emotional_history.append((datetime.now(), emotion_type, adjusted_intensity))
        if len(self.emotional_history) > self.max_history:
            self.emotional_history = self.emotional_history[-self.max_history:]
        
        # Update mood
        self.mood.update_from_emotion(emotion)
        
        return emotion
    
    def react_to_event(
        self,
        event_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Emotion]:
        """
        Generate emotional reaction to an event.
        
        Args:
            event_type: Type of event
            context: Additional context
            
        Returns:
            List of emotions triggered
        """
        context = context or {}
        reactions = []
        
        # Event to emotion mapping
        event_emotions = {
            # Positive events
            "meet_friend": [(EmotionType.JOY, 0.4), (EmotionType.TRUST, 0.3)],
            "get_paid": [(EmotionType.JOY, 0.5)],
            "promotion": [(EmotionType.JOY, 0.8), (EmotionType.ANTICIPATION, 0.5)],
            "fall_in_love": [(EmotionType.LOVE, 0.9), (EmotionType.JOY, 0.7)],
            "have_child": [(EmotionType.LOVE, 0.9), (EmotionType.JOY, 0.8), (EmotionType.ANTICIPATION, 0.6)],
            "wedding": [(EmotionType.LOVE, 0.9), (EmotionType.JOY, 0.9)],
            "compliment": [(EmotionType.JOY, 0.3), (EmotionType.TRUST, 0.2)],
            "success": [(EmotionType.JOY, 0.6), (EmotionType.ANTICIPATION, 0.4)],
            "gift": [(EmotionType.JOY, 0.5), (EmotionType.SURPRISE, 0.4)],
            
            # Negative events
            "rejection": [(EmotionType.SADNESS, 0.6), (EmotionType.FEAR, 0.3)],
            "job_loss": [(EmotionType.SADNESS, 0.7), (EmotionType.FEAR, 0.6), (EmotionType.ANGER, 0.4)],
            "breakup": [(EmotionType.SADNESS, 0.8), (EmotionType.ANGER, 0.4)],
            "death_loved_one": [(EmotionType.SADNESS, 1.0), (EmotionType.FEAR, 0.3)],
            "conflict": [(EmotionType.ANGER, 0.6), (EmotionType.DISGUST, 0.3)],
            "betrayal": [(EmotionType.ANGER, 0.8), (EmotionType.SADNESS, 0.5), (EmotionType.DISGUST, 0.4)],
            "insult": [(EmotionType.ANGER, 0.5), (EmotionType.SADNESS, 0.3)],
            "failure": [(EmotionType.SADNESS, 0.5), (EmotionType.DISGUST, 0.3)],
            
            # Neutral/Mixed events
            "stranger_approach": [(EmotionType.SURPRISE, 0.3), (EmotionType.ANTICIPATION, 0.2)],
            "new_situation": [(EmotionType.ANTICIPATION, 0.4), (EmotionType.FEAR, 0.2)],
            "waiting": [(EmotionType.ANTICIPATION, 0.3)],
        }
        
        if event_type in event_emotions:
            for emotion_type, base_intensity in event_emotions[event_type]:
                emotion = self.feel(emotion_type, base_intensity, source=event_type)
                reactions.append(emotion)
        
        return reactions
    
    def get_dominant_emotion(self) -> Optional[Emotion]:
        """Get the strongest current emotion."""
        active = [e for e in self.emotions.values() if not e.is_faded]
        if not active:
            return None
        return max(active, key=lambda e: e.intensity)
    
    def get_emotional_valence(self) -> float:
        """Get overall emotional valence (-1 to 1)."""
        if not self.emotions:
            return self.mood.valence
        
        # Weight by intensity
        positive_emotions = {
            EmotionType.JOY, EmotionType.TRUST, EmotionType.LOVE,
            EmotionType.OPTIMISM, EmotionType.ANTICIPATION
        }
        negative_emotions = {
            EmotionType.FEAR, EmotionType.SADNESS, EmotionType.DISGUST,
            EmotionType.ANGER, EmotionType.REMORSE, EmotionType.CONTEMPT
        }
        
        total_positive = sum(
            e.intensity for e in self.emotions.values()
            if e.emotion_type in positive_emotions and not e.is_faded
        )
        total_negative = sum(
            e.intensity for e in self.emotions.values()
            if e.emotion_type in negative_emotions and not e.is_faded
        )
        
        total = total_positive + total_negative
        if total == 0:
            return self.mood.valence
        
        return (total_positive - total_negative) / total
    
    def is_feeling(self, emotion_type: EmotionType, min_intensity: float = 0.2) -> bool:
        """Check if currently feeling a specific emotion."""
        if emotion_type not in self.emotions:
            return False
        return self.emotions[emotion_type].intensity >= min_intensity
    
    def get_decision_modifier(self) -> Dict[str, float]:
        """
        Get modifiers for decision making based on emotional state.
        
        Returns:
            Dict of decision factor modifiers
        """
        modifiers = {
            "risk_taking": 0.0,
            "social_seeking": 0.0,
            "work_motivation": 0.0,
            "patience": 0.0,
            "trust": 0.0,
        }
        
        dominant = self.get_dominant_emotion()
        if dominant:
            if dominant.emotion_type == EmotionType.JOY:
                modifiers["social_seeking"] += 0.3
                modifiers["risk_taking"] += 0.1
            elif dominant.emotion_type == EmotionType.FEAR:
                modifiers["risk_taking"] -= 0.4
                modifiers["social_seeking"] += 0.2
            elif dominant.emotion_type == EmotionType.ANGER:
                modifiers["patience"] -= 0.4
                modifiers["risk_taking"] += 0.2
            elif dominant.emotion_type == EmotionType.SADNESS:
                modifiers["social_seeking"] -= 0.2
                modifiers["work_motivation"] -= 0.3
            elif dominant.emotion_type == EmotionType.TRUST:
                modifiers["trust"] += 0.3
                modifiers["social_seeking"] += 0.2
        
        # Mood also affects decisions
        modifiers["risk_taking"] += self.mood.dominance * 0.2
        modifiers["social_seeking"] += self.mood.pleasure * 0.2
        modifiers["patience"] -= self.mood.arousal * 0.2
        
        return modifiers
    
    def update(self, hours: float = 1.0) -> None:
        """
        Update emotional state over time.
        
        Args:
            hours: Hours passed
        """
        # Decay emotions
        faded = []
        for emotion_type, emotion in self.emotions.items():
            emotion.decay(hours)
            if emotion.is_faded:
                faded.append(emotion_type)
        
        # Remove faded emotions
        for emotion_type in faded:
            del self.emotions[emotion_type]
        
        # Mood decays toward baseline
        self.mood.decay_toward_baseline(self.baseline_mood, hours)
    
    @classmethod
    def from_personality(
        cls,
        extraversion: float,
        neuroticism: float,
        agreeableness: float,
    ) -> "EmotionalState":
        """
        Create emotional state based on personality traits.
        
        Args:
            extraversion: Big Five extraversion (0-1)
            neuroticism: Big Five neuroticism (0-1)
            agreeableness: Big Five agreeableness (0-1)
            
        Returns:
            Configured EmotionalState
        """
        # Baseline mood from personality
        baseline = Mood(
            pleasure=(extraversion - 0.5) * 0.4 + (1 - neuroticism - 0.5) * 0.3,
            arousal=(extraversion - 0.5) * 0.3,
            dominance=(extraversion - 0.5) * 0.2 + (1 - agreeableness - 0.5) * 0.2,
        )
        
        return cls(
            mood=Mood(
                pleasure=baseline.pleasure,
                arousal=baseline.arousal,
                dominance=baseline.dominance,
            ),
            baseline_mood=baseline,
            sensitivity=0.3 + neuroticism * 0.4,
            stability=0.7 - neuroticism * 0.4,
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of emotional state."""
        dominant = self.get_dominant_emotion()
        return {
            "mood": self.mood.label,
            "mood_valence": self.mood.valence,
            "dominant_emotion": dominant.emotion_type.value if dominant else None,
            "dominant_intensity": dominant.intensity if dominant else 0,
            "active_emotions": [
                {"type": e.emotion_type.value, "intensity": e.intensity}
                for e in self.emotions.values() if not e.is_faded
            ],
            "overall_valence": self.get_emotional_valence(),
        }
