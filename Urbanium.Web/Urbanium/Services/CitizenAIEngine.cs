using Microsoft.Extensions.Options;
using OpenAI;
using OpenAI.Chat;
using System.ClientModel;
using System.Text.Json;
using Urbanium.Configuration;
using Urbanium.Models;

namespace Urbanium.Services;

/// <summary>
/// Represents a decision made by a citizen
/// </summary>
public class CitizenDecision
{
    public string CitizenId { get; set; } = "";
    public string CitizenName { get; set; } = "";
    public string DecisionType { get; set; } = "";   // Housing, Employment, Social, Daily, Family, Education
    public string Action { get; set; } = "";          // What they decided to do
    public string Reasoning { get; set; } = "";       // Why they made this decision
    public bool Success { get; set; } = true;         // Whether the action succeeded
    public string Outcome { get; set; } = "";         // What happened as a result
    public List<string> PersonalityChanges { get; set; } = new(); // Any trait adjustments
    public string Timestamp { get; set; } = "";
}

/// <summary>
/// The core AI engine that drives citizen decision-making
/// </summary>
public class CitizenAIEngine
{
    private readonly ChatClient _chatClient;
    private readonly LMStudioSettings _settings;
    private readonly ILogger<CitizenAIEngine> _logger;
    private readonly Random _random = new();

    public CitizenAIEngine(
        IOptions<LMStudioSettings> settings,
        ILogger<CitizenAIEngine> logger)
    {
        _settings = settings.Value;
        _logger = logger;

        try
        {
            var openAIClient = new OpenAIClient(
                new ApiKeyCredential(_settings.ApiKey),
                new OpenAIClientOptions { Endpoint = new Uri(_settings.Endpoint) });

            _chatClient = openAIClient.GetChatClient(_settings.ModelName);
            _logger.LogInformation("CitizenAIEngine initialized");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize CitizenAIEngine");
            throw;
        }
    }

    /// <summary>
    /// Main decision-making method: determines what a citizen should do this hour
    /// </summary>
    public async Task<CitizenDecision> MakeHourlyDecisionAsync(
        Citizen citizen,
        CityState cityState,
        int currentHour,
        int currentDay,
        Season season,
        Weather weather,
        List<Citizen> otherCitizens,
        CancellationToken cancellationToken = default)
    {
        // First, check for critical needs that override normal decisions
        if (citizen.State.Needs.HasCriticalNeed())
        {
            return await HandleCriticalNeedAsync(citizen, cityState, currentHour, cancellationToken);
        }

        // Determine decision type based on context
        var decisionContext = DetermineDecisionContext(citizen, cityState, currentHour, currentDay);

        // Get AI decision
        var decision = await GetAIDecisionAsync(
            citizen, cityState, currentHour, currentDay, season, weather, 
            otherCitizens, decisionContext, cancellationToken);

        return decision;
    }

    /// <summary>
    /// Determines what type of decision the citizen should focus on
    /// </summary>
    private string DetermineDecisionContext(Citizen citizen, CityState cityState, int currentHour, int currentDay)
    {
        var state = citizen.State;
        var priorities = new List<(string type, int priority)>();

        // Check for immediate needs
        if (state.Needs.Energy < 30 && currentHour >= 22 || currentHour <= 6)
            return "Sleep";
        if (state.Needs.Hunger < 40 && (currentHour == 8 || currentHour == 12 || currentHour == 19))
            return "Eat";

        // Check for employment during work hours
        if (state.Employment.Status == EmploymentStatus.Employed)
        {
            var workStart = state.Employment.WorkStartHour;
            var workEnd = workStart + state.Employment.WorkHoursPerDay;
            if (currentHour >= workStart && currentHour < workEnd && state.HoursWorkedToday < state.Employment.WorkHoursPerDay)
                return "Work";
        }

        // Check for critical life situations
        if (state.Housing.Status == HousingStatus.Homeless)
            priorities.Add(("FindHousing", 100));

        if (state.Employment.Status == EmploymentStatus.Unemployed && state.LifeStage != LifeStage.Child && state.LifeStage != LifeStage.Senior)
            priorities.Add(("FindJob", 90));

        // Check for financial pressure
        if (state.Finances.GetMonthsOfRunway() < 2)
            priorities.Add(("FinancialDecision", 85));

        // Social needs
        if (state.Needs.Social < 50 && citizen.Personality.Extraversion > 60)
            priorities.Add(("Social", 70));

        // Relationship seeking
        if (state.Family.Status == RelationshipStatus.Single && 
            state.LifeStage == LifeStage.YoungAdult || state.LifeStage == LifeStage.Adult)
        {
            if (citizen.Personality.Extraversion > 50 || _random.Next(100) < 30)
                priorities.Add(("FindPartner", 50));
        }

        // Career advancement for ambitious citizens
        if (citizen.Personality.Ambition > 70 && state.Employment.Status == EmploymentStatus.Employed)
        {
            if (_random.Next(100) < citizen.Personality.Ambition / 5)
                priorities.Add(("CareerAdvancement", 60));
        }

        // Business opportunity for entrepreneurial citizens
        if (citizen.Personality.RiskTolerance > 70 && citizen.Personality.Ambition > 80)
        {
            if (state.Finances.Savings > 20000 && _random.Next(100) < 20)
                priorities.Add(("StartBusiness", 55));
        }

        // Family decisions for partnered citizens
        if ((state.Family.Status == RelationshipStatus.Married || state.Family.Status == RelationshipStatus.Partnered) &&
            state.Family.ChildrenIds.Count == 0 && state.LifeStage == LifeStage.Adult)
        {
            if (_random.Next(100) < 15 && state.Housing.Status != HousingStatus.Homeless)
                priorities.Add(("HaveChild", 40));
        }

        // Evening leisure
        if (currentHour >= 18 && currentHour <= 22)
        {
            if (citizen.Personality.Extraversion > 60)
                priorities.Add(("Socialize", 45));
            else
                priorities.Add(("Leisure", 40));
        }

        // Return highest priority or default
        return priorities.OrderByDescending(p => p.priority).FirstOrDefault().type ?? "Idle";
    }

    /// <summary>
    /// Handle critical needs that must be addressed immediately
    /// </summary>
    private async Task<CitizenDecision> HandleCriticalNeedAsync(
        Citizen citizen,
        CityState cityState,
        int currentHour,
        CancellationToken cancellationToken)
    {
        var criticalNeed = citizen.State.Needs.GetMostCriticalNeed();

        return criticalNeed switch
        {
            "Hunger" => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Critical",
                Action = "EmergencyEat",
                Reasoning = "Dangerously hungry, must eat immediately",
                Success = citizen.State.Finances.CanAfford(15),
                Outcome = citizen.State.Finances.CanAfford(15) 
                    ? "Found food and ate" 
                    : "Couldn't afford food, went to food bank"
            },
            "Energy" => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Critical",
                Action = "EmergencySleep",
                Reasoning = "Extremely exhausted, must rest",
                Success = true,
                Outcome = citizen.State.Housing.Status != HousingStatus.Homeless 
                    ? "Went home to sleep" 
                    : "Found a shelter to rest"
            },
            "Health" => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Critical",
                Action = "SeekMedicalHelp",
                Reasoning = "Health critically low, needs medical attention",
                Success = true,
                Outcome = cityState.Policies.HealthcareSubsidy 
                    ? "Received subsidized medical care" 
                    : "Went to hospital"
            },
            _ => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Critical",
                Action = "Rest",
                Reasoning = "Needs to recover",
                Success = true,
                Outcome = "Resting at home"
            }
        };
    }

    /// <summary>
    /// Gets an AI-driven decision for the citizen
    /// </summary>
    private async Task<CitizenDecision> GetAIDecisionAsync(
        Citizen citizen,
        CityState cityState,
        int currentHour,
        int currentDay,
        Season season,
        Weather weather,
        List<Citizen> otherCitizens,
        string decisionContext,
        CancellationToken cancellationToken)
    {
        try
        {
            var prompt = BuildDecisionPrompt(citizen, cityState, currentHour, currentDay, season, weather, otherCitizens, decisionContext);

            var messages = new List<ChatMessage>
            {
                new SystemChatMessage(GetSystemPrompt()),
                new UserChatMessage(prompt)
            };

            var completion = await _chatClient.CompleteChatAsync(messages, cancellationToken: cancellationToken);
            var response = completion.Value.Content[0].Text ?? "";

            return ParseAIResponse(citizen, response, decisionContext);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting AI decision for {CitizenName}", citizen.Name);
            
            // Fallback to simple decision
            return GetFallbackDecision(citizen, decisionContext, currentHour);
        }
    }

    private string GetSystemPrompt()
    {
        return """
            You are the internal decision-making engine for citizens in Urbanium, a city simulation.
            Each citizen has a unique personality and life situation. Your job is to decide what they should do based on:
            - Their personality traits (Big Five + decision traits)
            - Their current life situation (housing, job, relationships, finances)
            - Their immediate needs (hunger, energy, social, happiness)
            - The current city state (economy, job market, housing availability)
            - Mayor policies that affect their options
            - Time of day and current activities of other citizens

            Respond in this EXACT format:
            ACTION: [specific action the citizen takes]
            REASONING: [1-2 sentences explaining why based on their personality]
            OUTCOME: [what happens as a result]
            SUCCESS: [true/false]
            PERSONALITY_CHANGE: [optional: trait_name:+/-amount, e.g., "ambition:+2" or "none"]

            Be realistic and consistent with the citizen's personality. Introverts don't suddenly become party animals.
            Pragmatic people make practical choices. Risk-tolerant people might take chances others wouldn't.
            Keep responses brief and actionable.
            """;
    }

    private string BuildDecisionPrompt(
        Citizen citizen,
        CityState cityState,
        int currentHour,
        int currentDay,
        Season season,
        Weather weather,
        List<Citizen> otherCitizens,
        string decisionContext)
    {
        var state = citizen.State;
        var singleCitizens = otherCitizens
            .Where(c => c.Id != citizen.Id && c.State.Family.Status == RelationshipStatus.Single)
            .Select(c => c.Name)
            .ToList();

        return $"""
            CITIZEN: {citizen.Name} ({citizen.Emoji})
            AGE: {state.Age} ({state.LifeStage})
            
            PERSONALITY:
            - Openness: {citizen.Personality.Openness}/100
            - Conscientiousness: {citizen.Personality.Conscientiousness}/100
            - Extraversion: {citizen.Personality.Extraversion}/100
            - Agreeableness: {citizen.Personality.Agreeableness}/100
            - Emotional Stability: {citizen.Personality.EmotionalStability}/100
            - Risk Tolerance: {citizen.Personality.RiskTolerance}/100
            - Ambition: {citizen.Personality.Ambition}/100
            - Altruism: {citizen.Personality.Altruism}/100
            - Pragmatism: {citizen.Personality.Pragmatism}/100
            - Core Values: {citizen.Personality.PrimaryValue}, {citizen.Personality.SecondaryValue}
            - Decision Style: {citizen.Personality.DecisionStyle}
            
            CURRENT STATE:
            - Housing: {state.Housing.Status} {(state.Housing.BuildingName != null ? $"at {state.Housing.BuildingName}" : "")}
            - Employment: {state.Employment.Status} {(state.Employment.JobTitle != null ? $"as {state.Employment.JobTitle}" : "")}
            - Monthly Income: ${state.Finances.MonthlyIncome}, Savings: ${state.Finances.Savings}
            - Relationship: {state.Family.Status} {(state.Family.PartnerName != null ? $"with {state.Family.PartnerName}" : "")}
            - Children: {state.Family.ChildrenNames.Count}
            
            NEEDS (0-100, lower = more urgent):
            - Hunger: {state.Needs.Hunger}
            - Energy: {state.Needs.Energy}
            - Social: {state.Needs.Social}
            - Happiness: {state.Needs.Happiness}
            - Health: {state.Needs.Health}
            
            CURRENT CONTEXT:
            - Day {currentDay}, {currentHour}:00
            - Season: {season}, Weather: {weather}
            - Current Activity: {state.Activity}
            - Hours Worked Today: {state.HoursWorkedToday}
            
            CITY STATE:
            - Economy: {cityState.Economy.EconomicHealth}/100 health
            - Unemployment Rate: {cityState.Economy.UnemploymentRate}%
            - Available Jobs: {cityState.Jobs.TotalOpenings}
            - Available Housing: {cityState.Housing.AvailableUnits} units
            - Average Rent: ${cityState.Housing.AverageRent}/month
            - Mayor Policies: {cityState.Policies.GetPolicySummary()}
            
            SOCIAL CONTEXT:
            - Single citizens available to meet: {(singleCitizens.Any() ? string.Join(", ", singleCitizens) : "None")}
            
            DECISION REQUIRED: {decisionContext}
            
            What does {citizen.Name} decide to do right now?
            """;
    }

    private CitizenDecision ParseAIResponse(Citizen citizen, string response, string decisionContext)
    {
        var decision = new CitizenDecision
        {
            CitizenId = citizen.Id,
            CitizenName = citizen.Name,
            DecisionType = decisionContext
        };

        // Parse the response
        var lines = response.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        
        foreach (var line in lines)
        {
            var trimmedLine = line.Trim();
            
            if (trimmedLine.StartsWith("ACTION:", StringComparison.OrdinalIgnoreCase))
                decision.Action = trimmedLine.Substring(7).Trim();
            else if (trimmedLine.StartsWith("REASONING:", StringComparison.OrdinalIgnoreCase))
                decision.Reasoning = trimmedLine.Substring(10).Trim();
            else if (trimmedLine.StartsWith("OUTCOME:", StringComparison.OrdinalIgnoreCase))
                decision.Outcome = trimmedLine.Substring(8).Trim();
            else if (trimmedLine.StartsWith("SUCCESS:", StringComparison.OrdinalIgnoreCase))
                decision.Success = trimmedLine.ToLower().Contains("true");
            else if (trimmedLine.StartsWith("PERSONALITY_CHANGE:", StringComparison.OrdinalIgnoreCase))
            {
                var change = trimmedLine.Substring(19).Trim();
                if (!change.Equals("none", StringComparison.OrdinalIgnoreCase))
                    decision.PersonalityChanges.Add(change);
            }
        }

        // Fallback if parsing failed
        if (string.IsNullOrEmpty(decision.Action))
        {
            decision.Action = "Continue current activity";
            decision.Reasoning = "Maintaining current routine";
            decision.Outcome = "Continued with daily activities";
        }

        return decision;
    }

    private CitizenDecision GetFallbackDecision(Citizen citizen, string decisionContext, int currentHour)
    {
        // Simple rule-based fallback when AI is unavailable
        return decisionContext switch
        {
            "Sleep" => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Daily",
                Action = "Sleep",
                Reasoning = "Tired and it's late",
                Success = true,
                Outcome = "Went to sleep"
            },
            "Eat" => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Daily",
                Action = "Eat",
                Reasoning = "It's mealtime",
                Success = true,
                Outcome = "Had a meal"
            },
            "Work" => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Employment",
                Action = "Work",
                Reasoning = "It's work hours",
                Success = true,
                Outcome = "Working"
            },
            "FindJob" => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Employment",
                Action = "LookForJob",
                Reasoning = "Needs employment",
                Success = _random.Next(100) < 30,
                Outcome = "Searching job listings"
            },
            "FindHousing" => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Housing",
                Action = "LookForHousing",
                Reasoning = "Needs a place to live",
                Success = _random.Next(100) < 40,
                Outcome = "Looking at available housing"
            },
            _ => new CitizenDecision
            {
                CitizenId = citizen.Id,
                CitizenName = citizen.Name,
                DecisionType = "Daily",
                Action = "Idle",
                Reasoning = "Nothing urgent to do",
                Success = true,
                Outcome = "Relaxing at home"
            }
        };
    }
}
