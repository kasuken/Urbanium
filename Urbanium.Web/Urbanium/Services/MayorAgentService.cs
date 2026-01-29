using Microsoft.Extensions.Options;
using OpenAI;
using OpenAI.Chat;
using System.ClientModel;
using System.Runtime.CompilerServices;
using System.Text.Json;
using Urbanium.Configuration;
using Urbanium.Models;

namespace Urbanium.Services;

public class MayorAgentService
{
    private readonly ChatClient _chatClient;
    private readonly LMStudioSettings _settings;
    private readonly ILogger<MayorAgentService> _logger;
    private readonly Random _random = new();

    public MayorAgentService(
        IOptions<LMStudioSettings> settings,
        ILogger<MayorAgentService> logger)
    {
        _settings = settings.Value;
        _logger = logger;

        try
        {
            // Create OpenAI client for LM Studio (OpenAI-compatible endpoint)
            var openAIClient = new OpenAIClient(
                new ApiKeyCredential(_settings.ApiKey),
                new OpenAIClientOptions { Endpoint = new Uri(_settings.Endpoint) });

            // Get the chat client for the specified model
            _chatClient = openAIClient.GetChatClient(_settings.ModelName);

            _logger.LogInformation("MayorAgentService initialized with endpoint: {Endpoint}, model: {Model}",
                _settings.Endpoint, _settings.ModelName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize MayorAgentService");
            throw;
        }
    }

    /// <summary>
    /// Makes a policy decision based on current city state
    /// </summary>
    public async Task<MayorDecision> MakePolicyDecisionAsync(
        CityState cityState,
        Mayor mayor,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var prompt = BuildPolicyPrompt(cityState, mayor);

            var messages = new List<ChatMessage>
            {
                new SystemChatMessage(GetMayorSystemPrompt()),
                new UserChatMessage(prompt)
            };

            var completion = await _chatClient.CompleteChatAsync(messages, cancellationToken: cancellationToken);
            var response = completion.Value.Content[0].Text ?? "";

            return ParseMayorDecision(response, cityState);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting Mayor policy decision");
            return GetFallbackDecision(cityState);
        }
    }

    private string GetMayorSystemPrompt()
    {
        return """
            You are Mayor Alexandra Sterling, the AI Mayor of Urbanium.
            Every 30 days, you review the city's state and make ONE policy decision.
            You must balance economic growth with citizen welfare.
            
            Available policy changes you can make:
            - TaxRate: 10-40% (affects city revenue and citizen happiness)
            - MinimumWage: 1000-3000/month (affects employment and business costs)
            - BusinessIncentives: true/false (attracts businesses but costs money)
            - RentControl: true/false (helps renters but may reduce housing supply)
            - UnemploymentBenefits: true/false (helps unemployed but costs money)
            - UnemploymentBenefitAmount: 500-1500/month
            - HealthcareSubsidy: true/false (improves health but costs money)
            - MaxWorkHours: 8-12/day (affects productivity and citizen health)
            
            Respond in this EXACT format:
            POLICY_AREA: [Economy/Housing/Social/Work]
            ACTION: [Brief description of what you're changing]
            CHANGE: [policy_name]=[new_value]
            REASONING: [2-3 sentences explaining why this helps Urbanium]
            APPROVAL_IMPACT: [number between -10 and +10]
            """;
    }

    private string BuildPolicyPrompt(CityState cityState, Mayor mayor)
    {
        return $"""
            MONTHLY CITY REPORT - DAY 30 REVIEW
            
            ECONOMY:
            - Unemployment Rate: {cityState.Economy.UnemploymentRate:F1}%
            - Economic Health: {cityState.Economy.EconomicHealth}/100
            - Average Wage: ${cityState.Economy.AverageWage}/month
            - Current Tax Rate: {cityState.Policies.TaxRate}%
            
            HOUSING:
            - Total Units: {cityState.Housing.TotalHousingUnits}
            - Occupied: {cityState.Housing.OccupiedUnits}
            - Vacancy Rate: {100 - cityState.Housing.OccupancyRate:F1}%
            - Average Rent: ${cityState.Housing.AverageRent}/month
            - Rent Control Active: {cityState.Policies.RentControl}
            
            CITIZENS:
            - Population: {cityState.Statistics.TotalPopulation}
            - Average Happiness: {cityState.Statistics.AverageHappiness:F0}%
            - New Businesses This Month: {cityState.Statistics.NewBusinesses}
            - Births This Month: {cityState.Statistics.Births}
            
            CURRENT POLICIES:
            - Minimum Wage: ${cityState.Policies.MinimumWage}/month
            - Business Incentives: {cityState.Policies.BusinessIncentives}
            - Unemployment Benefits: {cityState.Policies.UnemploymentBenefits} (${cityState.Policies.UnemploymentBenefitAmount}/month)
            - Healthcare Subsidy: {cityState.Policies.HealthcareSubsidy}
            - Max Work Hours: {cityState.Policies.MaxWorkHours}/day
            
            YOUR PRIORITIES:
            - Primary Focus: {mayor.PrimaryFocus}
            - Secondary Focus: {mayor.SecondaryFocus}
            - Current Approval Rating: {mayor.ApprovalRating}%
            
            Based on this data, what ONE policy change will you make today?
            """;
    }

    private MayorDecision ParseMayorDecision(string response, CityState cityState)
    {
        var decision = new MayorDecision();

        var lines = response.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        
        foreach (var line in lines)
        {
            var trimmedLine = line.Trim();
            
            if (trimmedLine.StartsWith("POLICY_AREA:", StringComparison.OrdinalIgnoreCase))
                decision.PolicyArea = trimmedLine.Substring(12).Trim();
            else if (trimmedLine.StartsWith("ACTION:", StringComparison.OrdinalIgnoreCase))
                decision.Action = trimmedLine.Substring(7).Trim();
            else if (trimmedLine.StartsWith("REASONING:", StringComparison.OrdinalIgnoreCase))
                decision.Reasoning = trimmedLine.Substring(10).Trim();
            else if (trimmedLine.StartsWith("APPROVAL_IMPACT:", StringComparison.OrdinalIgnoreCase))
            {
                if (int.TryParse(trimmedLine.Substring(16).Trim().Replace("+", ""), out var impact))
                    decision.ProjectedApprovalChange = Math.Clamp(impact, -10, 10);
            }
            else if (trimmedLine.StartsWith("CHANGE:", StringComparison.OrdinalIgnoreCase))
            {
                var changeStr = trimmedLine.Substring(7).Trim();
                var parts = changeStr.Split('=');
                if (parts.Length == 2)
                {
                    var policyName = parts[0].Trim();
                    var valueStr = parts[1].Trim();
                    
                    // Parse and store the change
                    if (int.TryParse(valueStr, out var intValue))
                        decision.Changes[policyName] = intValue;
                    else if (bool.TryParse(valueStr, out var boolValue))
                        decision.Changes[policyName] = boolValue;
                    else
                        decision.Changes[policyName] = valueStr;
                }
            }
        }

        // Fallback if parsing failed
        if (string.IsNullOrEmpty(decision.Action))
        {
            return GetFallbackDecision(cityState);
        }

        return decision;
    }

    private MayorDecision GetFallbackDecision(CityState cityState)
    {
        // Simple rule-based fallback
        var decision = new MayorDecision();

        if (cityState.Economy.UnemploymentRate > 10)
        {
            decision.PolicyArea = "Economy";
            decision.Action = "Lowering taxes to stimulate job creation";
            decision.Changes["TaxRate"] = Math.Max(10, cityState.Policies.TaxRate - 3);
            decision.Reasoning = "High unemployment requires economic stimulus.";
            decision.ProjectedApprovalChange = 3;
        }
        else if (cityState.Statistics.AverageHappiness < 50)
        {
            decision.PolicyArea = "Social";
            decision.Action = "Increasing unemployment benefits";
            decision.Changes["UnemploymentBenefitAmount"] = Math.Min(1500, cityState.Policies.UnemploymentBenefitAmount + 100);
            decision.Reasoning = "Citizens are unhappy, need more social support.";
            decision.ProjectedApprovalChange = 5;
        }
        else if (cityState.Housing.OccupancyRate > 95)
        {
            decision.PolicyArea = "Housing";
            decision.Action = "Enabling rent control to help renters";
            decision.Changes["RentControl"] = true;
            decision.Reasoning = "Housing market is tight, protecting tenants.";
            decision.ProjectedApprovalChange = 2;
        }
        else
        {
            decision.PolicyArea = "Economy";
            decision.Action = "Maintaining current policies - city is stable";
            decision.Reasoning = "Current policies are working well.";
            decision.ProjectedApprovalChange = 1;
        }

        return decision;
    }

    public async Task<string> AskMayorAsync(string question, CancellationToken cancellationToken = default)
    {
        try
        {
            var messages = new List<ChatMessage>
            {
                new SystemChatMessage(
                    """
                    You are the AI Mayor of Urbanium, a simulated city. Your name is Mayor Alexandra Sterling.
                    You are responsible, efficient, and care deeply about all citizens.
                    You make decisions based on data and the wellbeing of the community.
                    Keep your responses concise and professional, but warm and approachable.
                    """),
                new UserChatMessage(question)
            };

            var completion = await _chatClient.CompleteChatAsync(messages, cancellationToken: cancellationToken);

            return completion.Value.Content[0].Text ?? "I apologize, but I couldn't process that request.";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error communicating with AI Mayor");
            return "I apologize, but I'm having trouble responding right now. Please ensure LM Studio is running.";
        }
    }

    public async IAsyncEnumerable<string> AskMayorStreamingAsync(
        string question,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var messages = new List<ChatMessage>
        {
            new SystemChatMessage(
                """
                You are the AI Mayor of Urbanium, a simulated city. Your name is Mayor Alexandra Sterling.
                You are responsible, efficient, and care deeply about all citizens.
                You make decisions based on data and the wellbeing of the community.
                Keep your responses concise and professional, but warm and approachable.
                """),
            new UserChatMessage(question)
        };

        await foreach (var streamPart in _chatClient.CompleteChatStreamingAsync(messages, cancellationToken: cancellationToken))
        {
            foreach (var contentPart in streamPart.ContentUpdate)
            {
                if (!string.IsNullOrEmpty(contentPart.Text))
                {
                    yield return contentPart.Text;
                }
            }
        }
    }

    public async Task<string> GetMayorDecisionAsync(
        string scenario,
        List<string> options,
        CancellationToken cancellationToken = default)
    {
        var optionsList = string.Join("\n", options.Select((opt, idx) => $"{idx + 1}. {opt}"));

        var question = $"""
            As the Mayor of Urbanium, you need to make a decision:

            Scenario: {scenario}

            Options:
            {optionsList}

            Please choose the best option and explain your reasoning briefly.
            """;

        return await AskMayorAsync(question, cancellationToken);
    }
}
