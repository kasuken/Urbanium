namespace Urbanium.Models;

public class CitizenPersonality
{
    // Big Five Personality Traits (0-100 scale)
    public int Openness { get; set; } = 50;           // Creativity, curiosity, openness to new experiences
    public int Conscientiousness { get; set; } = 50;  // Organization, dependability, discipline
    public int Extraversion { get; set; } = 50;       // Sociability, assertiveness, energy
    public int Agreeableness { get; set; } = 50;      // Compassion, cooperation, trust
    public int EmotionalStability { get; set; } = 50; // Calmness, resilience (inverse of neuroticism)
    
    // Decision-Making Traits (0-100 scale)
    public int RiskTolerance { get; set; } = 50;      // Willingness to take risks
    public int Ambition { get; set; } = 50;           // Drive for success and achievement
    public int Altruism { get; set; } = 50;           // Concern for others' wellbeing
    public int Pragmatism { get; set; } = 50;         // Practical vs idealistic thinking
    
    // Values & Priorities
    public string PrimaryValue { get; set; } = "";    // What matters most (e.g., "Family", "Career", "Community")
    public string SecondaryValue { get; set; } = "";  // Second priority
    
    // Background & Motivation
    public string Background { get; set; } = "";      // Brief personal history
    public string CoreMotivation { get; set; } = "";  // What drives their decisions
    public string DecisionStyle { get; set; } = "";   // How they approach choices
    
    /// <summary>
    /// Adjust personality trait based on life experience
    /// </summary>
    public void AdjustTrait(string trait, int delta)
    {
        switch (trait.ToLower())
        {
            case "openness":
                Openness = Math.Clamp(Openness + delta, 0, 100);
                break;
            case "conscientiousness":
                Conscientiousness = Math.Clamp(Conscientiousness + delta, 0, 100);
                break;
            case "extraversion":
                Extraversion = Math.Clamp(Extraversion + delta, 0, 100);
                break;
            case "agreeableness":
                Agreeableness = Math.Clamp(Agreeableness + delta, 0, 100);
                break;
            case "emotionalstability":
                EmotionalStability = Math.Clamp(EmotionalStability + delta, 0, 100);
                break;
            case "risktolerance":
                RiskTolerance = Math.Clamp(RiskTolerance + delta, 0, 100);
                break;
            case "ambition":
                Ambition = Math.Clamp(Ambition + delta, 0, 100);
                break;
            case "altruism":
                Altruism = Math.Clamp(Altruism + delta, 0, 100);
                break;
            case "pragmatism":
                Pragmatism = Math.Clamp(Pragmatism + delta, 0, 100);
                break;
        }
    }
}

public class Citizen
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = "";
    public string Emoji { get; set; } = "";
    public string Occupation { get; set; } = "";
    public CitizenPersonality Personality { get; set; } = new();
    public CitizenState State { get; set; } = new();
    
    /// <summary>
    /// Updates citizen's occupation based on employment state
    /// </summary>
    public void UpdateOccupation()
    {
        Occupation = State.Employment.Status switch
        {
            EmploymentStatus.Unemployed => "Unemployed",
            EmploymentStatus.Student => "Student",
            EmploymentStatus.Retired => "Retired",
            EmploymentStatus.Child => "Child",
            EmploymentStatus.BusinessOwner => $"Owner of {State.Employment.BusinessName}",
            EmploymentStatus.Employed => State.Employment.JobTitle ?? "Employed",
            _ => "Unknown"
        };
    }
    
    /// <summary>
    /// Get a brief status for activity log
    /// </summary>
    public string GetBriefStatus()
    {
        return $"{Emoji} {Name}: {State.Activity} ({State.ActivityDescription})";
    }
}
