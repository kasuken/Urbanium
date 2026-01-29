# Citizen Personality System

This document describes the comprehensive personality system implemented for Urbanium citizens, designed for AI-driven autonomous decision-making.

## Overview

Each citizen has a detailed personality profile based on the **Big Five personality traits** plus additional decision-making characteristics. These profiles enable realistic, consistent autonomous behavior when integrated with the AI engine.

## Personality Components

### 1. Big Five Personality Traits (0-100 scale)

- **Openness**: Creativity, curiosity, openness to new experiences
  - High: Embraces change, seeks novelty, creative problem-solving
  - Low: Prefers routine, traditional approaches, proven methods

- **Conscientiousness**: Organization, dependability, discipline
  - High: Organized, reliable, follows through on commitments
  - Low: Flexible, spontaneous, adaptable

- **Extraversion**: Sociability, assertiveness, energy from social interaction
  - High: Outgoing, energized by groups, assertive
  - Low: Reserved, prefers solitude, thoughtful

- **Agreeableness**: Compassion, cooperation, trust in others
  - High: Cooperative, empathetic, team-oriented
  - Low: Competitive, skeptical, independent

- **Emotional Stability**: Calmness, resilience (inverse of neuroticism)
  - High: Calm under pressure, emotionally resilient
  - Low: Sensitive, reactive, emotionally expressive

### 2. Decision-Making Traits (0-100 scale)

- **Risk Tolerance**: Willingness to take risks
- **Ambition**: Drive for success and achievement
- **Altruism**: Concern for others' wellbeing
- **Pragmatism**: Practical vs idealistic thinking

### 3. Values & Background

- **Primary Value**: What matters most to the citizen
- **Secondary Value**: Second priority
- **Background**: Personal history and formative experiences
- **Core Motivation**: What drives their decisions
- **Decision Style**: How they approach choices

## Citizen Profiles

### James Chen - Business Owner
**Archetype**: Ambitious Entrepreneur

- High conscientiousness (85) and ambition (90)
- High risk tolerance (80) - calculated risks
- Values: Success, Innovation
- Decision style: Analytical and data-driven
- **AI Behavior**: Seeks growth opportunities, weighs costs vs benefits, makes strategic long-term investments

### Maria Rodriguez - Doctor
**Archetype**: Compassionate Healer

- Very high conscientiousness (95) and altruism (95)
- Low risk tolerance (30) - safety-first approach
- Values: Health & Wellbeing, Community
- Decision style: Careful and methodical
- **AI Behavior**: Prioritizes public health, advocates for safety measures, evidence-based decisions

### Robert Williams - Chef
**Archetype**: Creative Artist

- Very high openness (90)
- Medium risk tolerance (65) - willing to experiment
- Values: Creativity, Joy & Connection
- Decision style: Follows intuition and passion
- **AI Behavior**: Seeks unique experiences, values quality over profit, brings community together

### Sarah Johnson - Teacher
**Archetype**: Dedicated Educator

- High agreeableness (90) and altruism (90)
- Moderate risk tolerance (40)
- Values: Education, Equity
- Decision style: Collaborative and inclusive
- **AI Behavior**: Advocates for children and underserved populations, seeks consensus, long-term thinking

### Michael Park - Mechanic
**Archetype**: Reliable Craftsman

- Very high pragmatism (90) and emotional stability (85)
- Balanced traits overall
- Values: Reliability, Family
- Decision style: Practical and grounded
- **AI Behavior**: Focuses on proven solutions, values sustainability, prioritizes family security

### Emily Davis - Firefighter
**Archetype**: Courageous Protector

- Very high emotional stability (95) and risk tolerance (85)
- High conscientiousness (90)
- Values: Service & Protection, Courage
- Decision style: Quick and decisive under pressure
- **AI Behavior**: Takes charge in crises, protective of community, leads by example

## Using Personalities for AI Decision-Making

### CitizenDecisionService

The `CitizenDecisionService` provides methods to integrate personalities into AI-driven decisions:

#### 1. GetPersonalityPrompt(Citizen)
Generates a complete personality profile formatted for LLM prompts. Use this when asking the AI to make decisions as a specific citizen.

```csharp
var prompt = decisionService.GetPersonalityPrompt(citizen);
// Feed to AI along with scenario for authentic responses
```

#### 2. GetDecisionWeights(Citizen)
Returns weighted priorities for algorithmic decision-making:

- `financial_gain`: Money and economic advancement
- `social_impact`: Community benefit and helping others
- `personal_growth`: Learning and self-improvement
- `stability`: Security and predictability
- `relationships`: Social connections and collaboration
- `adventure`: New experiences and excitement

```csharp
var weights = decisionService.GetDecisionWeights(citizen);
// Use weights to score different decision options
```

#### 3. Specialized Decision Methods

- `WouldAcceptJobOffer()`: Job acceptance logic
- `GetPreferredHousingType()`: Housing preferences
- `PredictEventReaction()`: Response to city events

#### 4. ValidatePersonality()
Checks for contradictory traits that might need review.

## Integration with AI Engine

### For LLM-based Decisions (e.g., LM Studio)

```csharp
var personalityPrompt = citizenDecisionService.GetPersonalityPrompt(citizen);
var scenario = "The city is voting on a new tax to fund public parks.";

var prompt = $"""
    {personalityPrompt}
    
    Scenario: {scenario}
    
    Based on this citizen's personality, values, and decision-making style,
    how would they vote and why? Provide reasoning that aligns with their character.
    """;

var decision = await mayorAgentService.AskMayorAsync(prompt);
```

### For Weighted Decision Algorithms

```csharp
var weights = citizenDecisionService.GetDecisionWeights(citizen);

var options = new Dictionary<string, Dictionary<string, double>>
{
    ["Option A"] = new() { ["financial_gain"] = 0.8, ["social_impact"] = 0.3 },
    ["Option B"] = new() { ["financial_gain"] = 0.4, ["social_impact"] = 0.9 }
};

// Calculate weighted scores
var bestOption = options
    .Select(opt => new {
        Option = opt.Key,
        Score = opt.Value.Sum(attr => attr.Value * weights[attr.Key])
    })
    .OrderByDescending(x => x.Score)
    .First();
```

## Future Enhancements

1. **Dynamic Personality Evolution**: Personalities change based on experiences
2. **Relationship Networks**: Track relationships between citizens
3. **Emotional States**: Short-term moods affecting decisions
4. **Learning from Outcomes**: Citizens learn from decision consequences
5. **Cultural Background**: Add cultural context to decision-making
6. **Goals & Aspirations**: Short and long-term personal goals

## Best Practices

1. **Consistency**: Always reference personality when making decisions for a citizen
2. **Nuance**: Use multiple traits together (e.g., high ambition + low risk = frustrated)
3. **Growth**: Allow personalities to evolve slightly based on major life events
4. **Validation**: Use `ValidatePersonality()` to check for contradictions
5. **Context**: Consider occupation and background along with traits

## Example Scenarios

### Scenario: New Business Opportunity

**James Chen** (Ambitious Entrepreneur)
- Decision: Invests after thorough analysis
- Reasoning: High ambition + risk tolerance + pragmatism

**Michael Park** (Reliable Craftsman)
- Decision: Declines, focuses on current work
- Reasoning: High pragmatism + family values + moderate risk tolerance

### Scenario: Community Crisis

**Maria Rodriguez** (Compassionate Healer)
- Reaction: Immediately organizes medical response
- Reasoning: Very high altruism + conscientiousness + medical expertise

**Emily Davis** (Courageous Protector)
- Reaction: Takes charge of emergency coordination
- Reasoning: Very high emotional stability + service values + crisis experience

### Scenario: Social Event

**Robert Williams** (Creative Artist)
- Behavior: Hosts and brings people together
- Reasoning: High openness + extraversion + values connection

**Michael Park** (Reliable Craftsman)
- Behavior: Attends but stays with close friends
- Reasoning: Moderate extraversion + family values

## Technical Notes

- All trait values are 0-100 integers for consistency
- Trait combinations create emergent behaviors
- Use `CitizenDecisionService` for standard operations
- Feed `GetPersonalityPrompt()` output to LLMs for authentic dialogue
- Decision weights are normalized (0.0-1.0) for algorithmic scoring
