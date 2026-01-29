using Urbanium.Models;

namespace Urbanium.Services;

/// <summary>
/// Service for making autonomous decisions based on citizen personalities.
/// This will be integrated with the AI engine for realistic citizen behavior.
/// </summary>
public class CitizenDecisionService
{
    private readonly ILogger<CitizenDecisionService> _logger;

    public CitizenDecisionService(ILogger<CitizenDecisionService> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Generates a personality profile summary for AI prompts
    /// </summary>
    public string GetPersonalityPrompt(Citizen citizen)
    {
        return $"""
            Citizen Profile: {citizen.Name}
            Occupation: {citizen.Occupation}
            
            Personality Traits (0-100 scale):
            - Openness: {citizen.Personality.Openness} (creativity, curiosity)
            - Conscientiousness: {citizen.Personality.Conscientiousness} (organization, discipline)
            - Extraversion: {citizen.Personality.Extraversion} (sociability, energy)
            - Agreeableness: {citizen.Personality.Agreeableness} (compassion, cooperation)
            - Emotional Stability: {citizen.Personality.EmotionalStability} (calmness, resilience)
            
            Decision-Making Traits:
            - Risk Tolerance: {citizen.Personality.RiskTolerance}
            - Ambition: {citizen.Personality.Ambition}
            - Altruism: {citizen.Personality.Altruism}
            - Pragmatism: {citizen.Personality.Pragmatism}
            
            Core Values:
            - Primary Value: {citizen.Personality.PrimaryValue}
            - Secondary Value: {citizen.Personality.SecondaryValue}
            
            Background: {citizen.Personality.Background}
            Core Motivation: {citizen.Personality.CoreMotivation}
            Decision Style: {citizen.Personality.DecisionStyle}
            """;
    }

    /// <summary>
    /// Determines if a citizen would likely accept a job offer based on personality
    /// </summary>
    public bool WouldAcceptJobOffer(Citizen citizen, string jobType, int salary, string workEnvironment)
    {
        var score = 0;

        // High ambition increases job seeking
        if (citizen.Personality.Ambition > 70) score += 2;
        
        // Pragmatism affects salary importance
        if (citizen.Personality.Pragmatism > 70 && salary > 50000) score += 2;
        
        // Agreeableness affects team environment preference
        if (citizen.Personality.Agreeableness > 70 && workEnvironment == "collaborative") score += 1;
        
        // Openness affects willingness to try new things
        if (citizen.Personality.Openness > 70) score += 1;

        return score >= 3;
    }

    /// <summary>
    /// Determines housing preference based on personality
    /// </summary>
    public string GetPreferredHousingType(Citizen citizen)
    {
        // Extraverts prefer social environments (apartments/skyscrapers)
        if (citizen.Personality.Extraversion > 70)
            return "Skyscraper";
        
        // Family-oriented prefer medium houses
        if (citizen.Personality.PrimaryValue == "Family" || citizen.Personality.SecondaryValue == "Family")
            return "Medium House";
        
        // Pragmatic types prefer efficient housing
        if (citizen.Personality.Pragmatism > 80)
            return "Medium House";
        
        // Default to small house
        return "Small House";
    }

    /// <summary>
    /// Predicts reaction to city event based on personality
    /// </summary>
    public string PredictEventReaction(Citizen citizen, string eventType, string eventDescription)
    {
        var reactions = new List<string>();

        switch (eventType.ToLower())
        {
            case "crisis":
                if (citizen.Personality.EmotionalStability > 80)
                    reactions.Add("remains calm and helps coordinate response");
                else if (citizen.Personality.Altruism > 80)
                    reactions.Add("immediately volunteers to help affected citizens");
                else if (citizen.Personality.EmotionalStability < 40)
                    reactions.Add("feels anxious but focuses on protecting family");
                break;

            case "opportunity":
                if (citizen.Personality.Ambition > 80 && citizen.Personality.RiskTolerance > 70)
                    reactions.Add("eagerly pursues the opportunity");
                else if (citizen.Personality.Pragmatism > 80)
                    reactions.Add("carefully analyzes pros and cons before deciding");
                else if (citizen.Personality.RiskTolerance < 40)
                    reactions.Add("hesitates and prefers to stick with current situation");
                break;

            case "social":
                if (citizen.Personality.Extraversion > 70)
                    reactions.Add("actively participates and brings others together");
                else if (citizen.Personality.Extraversion < 40)
                    reactions.Add("attends but prefers to observe from the sidelines");
                else if (citizen.Personality.Agreeableness > 80)
                    reactions.Add("helps organize and ensures everyone feels welcome");
                break;
        }

        return reactions.Any() ? reactions.First() : "reacts according to their personal values";
    }

    /// <summary>
    /// Generates decision weights for AI decision-making
    /// </summary>
    public Dictionary<string, double> GetDecisionWeights(Citizen citizen)
    {
        return new Dictionary<string, double>
        {
            ["financial_gain"] = citizen.Personality.Ambition / 100.0 * citizen.Personality.Pragmatism / 100.0,
            ["social_impact"] = citizen.Personality.Altruism / 100.0 * citizen.Personality.Agreeableness / 100.0,
            ["personal_growth"] = citizen.Personality.Openness / 100.0 * citizen.Personality.Ambition / 100.0,
            ["stability"] = citizen.Personality.Conscientiousness / 100.0 * (100 - citizen.Personality.RiskTolerance) / 100.0,
            ["relationships"] = citizen.Personality.Agreeableness / 100.0 * citizen.Personality.Extraversion / 100.0,
            ["adventure"] = citizen.Personality.Openness / 100.0 * citizen.Personality.RiskTolerance / 100.0
        };
    }

    /// <summary>
    /// Validates personality coherence (for debugging/testing)
    /// </summary>
    public List<string> ValidatePersonality(Citizen citizen)
    {
        var issues = new List<string>();

        // Check for contradictory traits
        if (citizen.Personality.Ambition > 80 && citizen.Personality.RiskTolerance < 30)
            issues.Add($"{citizen.Name}: High ambition but very low risk tolerance may create internal conflict");

        if (citizen.Personality.Altruism > 80 && citizen.Personality.Pragmatism > 80)
            issues.Add($"{citizen.Name}: Very high altruism and pragmatism might clash in resource allocation decisions");

        if (citizen.Personality.Extraversion > 80 && citizen.Personality.EmotionalStability < 30)
            issues.Add($"{citizen.Name}: High extraversion with low emotional stability might lead to social exhaustion");

        return issues;
    }
}
