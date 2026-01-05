namespace Urbanium.Web.Agents;

/// <summary>
/// Citizens are structured agents, not chatbots.
/// Each citizen has stable traits, evolving needs, and a bounded decision model.
/// Decisions can be made by rules, utility functions, or AI.
/// </summary>
public class Citizen
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Name { get; set; } = string.Empty;
    public int Age { get; set; }
    
    // Stable traits and values
    public CitizenTraits Traits { get; set; } = new();
    
    // Skills and resources
    public List<Skill> Skills { get; set; } = new();
    public CitizenResources Resources { get; set; } = new();
    
    // Needs that evolve over time
    public CitizenNeeds Needs { get; set; } = new();
    
    // Social ties
    public List<SocialTie> SocialTies { get; set; } = new();
    
    // Role bindings
    public Guid? EmployerId { get; set; }
    public Guid? HouseholdId { get; set; }
    public Guid? CurrentDistrictId { get; set; }
    
    // State
    public CitizenState State { get; set; }
    public Actions.ActionType? LastAction { get; set; }
    
    // AI Decision tracking
    public bool LastDecisionWasAI { get; set; }
    public string? LastAIReasoning { get; set; }
    public float? LastAIConfidence { get; set; }
    public int TotalDecisions { get; set; }
    public int AIDecisions { get; set; }
    
    /// <summary>
    /// Get available actions for this citizen based on world state.
    /// </summary>
    public List<Actions.ActionType> GetAvailableActions(Engine.WorldState worldState)
    {
        var actions = new List<Actions.ActionType>
        {
            Actions.ActionType.Rest,
            Actions.ActionType.Eat,
            Actions.ActionType.Socialize
        };
        
        if (State == CitizenState.Employed || EmployerId.HasValue)
        {
            actions.Add(Actions.ActionType.WorkShift);
            actions.Add(Actions.ActionType.Commute);
        }
        
        if ((State == CitizenState.Unemployed || !EmployerId.HasValue) && 
            worldState.LaborMarket.OpenPositions.Count > 0)
        {
            actions.Add(Actions.ActionType.JobSearch);
        }
        
        if (worldState.HousingMarket.AvailableUnits.Any(u => !u.IsOccupied))
        {
            actions.Add(Actions.ActionType.HousingChange);
        }
        
        return actions;
    }
    
    /// <summary>
    /// Make a rule-based decision based on current state and available actions.
    /// This is used as fallback when AI is unavailable or for hybrid decisions.
    /// </summary>
    public Actions.ActionType DecideActionByRules(Engine.WorldState worldState)
    {
        var availableActions = GetAvailableActions(worldState);
        
        // Priority-based selection (simplified utility model)
        if (Needs.Hunger > 0.8 && availableActions.Contains(Actions.ActionType.Eat))
            return Actions.ActionType.Eat;
        
        if (Needs.Energy > 0.8 && availableActions.Contains(Actions.ActionType.Rest))
            return Actions.ActionType.Rest;
        
        if (!EmployerId.HasValue && availableActions.Contains(Actions.ActionType.JobSearch))
            return Actions.ActionType.JobSearch;
        
        if (worldState.IsWorkingHours && EmployerId.HasValue && 
            availableActions.Contains(Actions.ActionType.WorkShift))
            return Actions.ActionType.WorkShift;
        
        if (Needs.Social > 0.7 && availableActions.Contains(Actions.ActionType.Socialize))
            return Actions.ActionType.Socialize;
        
        return Actions.ActionType.Rest;
    }
    
    /// <summary>
    /// Record that a decision was made (for tracking AI vs rule-based).
    /// </summary>
    public void RecordDecision(Actions.ActionType action, bool wasAI, string? reasoning = null, float? confidence = null)
    {
        LastAction = action;
        LastDecisionWasAI = wasAI;
        LastAIReasoning = reasoning;
        LastAIConfidence = confidence;
        TotalDecisions++;
        if (wasAI) AIDecisions++;
    }
}

/// <summary>
/// Stable personality traits that influence decision-making.
/// </summary>
public class CitizenTraits
{
    /// <summary>Tendency to seek social interaction (0-1)</summary>
    public double Sociability { get; set; } = 0.5;
    
    /// <summary>Willingness to take risks (0-1)</summary>
    public double RiskTolerance { get; set; } = 0.5;
    
    /// <summary>Preference for saving vs spending (0-1)</summary>
    public double Frugality { get; set; } = 0.5;
    
    /// <summary>Tendency to seek career advancement (0-1)</summary>
    public double Ambition { get; set; } = 0.5;
    
    /// <summary>Preference for stability vs change (0-1)</summary>
    public double Stability { get; set; } = 0.5;
}

/// <summary>
/// Skills that can be used for employment.
/// </summary>
public class Skill
{
    public string Name { get; set; } = string.Empty;
    public double Level { get; set; } // 0-1
    public int YearsExperience { get; set; }
}

/// <summary>
/// Economic resources of a citizen.
/// </summary>
public class CitizenResources
{
    public decimal Cash { get; set; }
    public decimal MonthlyIncome { get; set; }
    public decimal MonthlyExpenses { get; set; }
}

/// <summary>
/// Needs that evolve over time and drive behavior.
/// Values range from 0 (fully satisfied) to 1 (critical need).
/// </summary>
public class CitizenNeeds
{
    public double Hunger { get; set; }
    public double Energy { get; set; }
    public double Social { get; set; }
    public double Shelter { get; set; }
    public double Income { get; set; }
    
    /// <summary>
    /// Update needs based on time passage.
    /// </summary>
    public void Decay(double hours)
    {
        Hunger = Math.Min(1.0, Hunger + (0.1 * hours / 24));
        Energy = Math.Min(1.0, Energy + (0.05 * hours / 24));
        Social = Math.Min(1.0, Social + (0.02 * hours / 24));
    }
}

/// <summary>
/// Social connection to another citizen.
/// </summary>
public class SocialTie
{
    public Guid TargetCitizenId { get; set; }
    public SocialTieType Type { get; set; }
    public double Strength { get; set; } // 0-1
    public int InteractionCount { get; set; }
}

public enum SocialTieType
{
    Family,
    Friend,
    Colleague,
    Neighbor,
    Acquaintance
}

public enum CitizenState
{
    Idle,
    Working,
    Commuting,
    Resting,
    Socializing,
    Employed,
    Unemployed,
    SearchingForHousing
}
