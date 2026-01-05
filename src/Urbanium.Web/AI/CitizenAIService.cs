using System.ClientModel;
using System.Text.Json;
using Microsoft.Extensions.Options;
using OpenAI;
using OpenAI.Chat;
using Urbanium.Web.Agents;
using Urbanium.Web.Engine;

namespace Urbanium.Web.AI;

/// <summary>
/// AI-powered decision service for citizen agents.
/// Uses OpenAI-compatible endpoints (LM Studio, OpenAI, Azure OpenAI).
/// </summary>
public class CitizenAIService
{
    private readonly AIConfiguration _config;
    private readonly ChatClient? _chatClient;
    private readonly ILogger<CitizenAIService> _logger;
    private readonly Random _random = new();
    
    public CitizenAIService(IOptions<AIConfiguration> config, ILogger<CitizenAIService> logger)
    {
        _config = config.Value;
        _logger = logger;
        
        if (_config.Enabled)
        {
            try
            {
                var clientOptions = new OpenAIClientOptions
                {
                    Endpoint = new Uri(_config.Endpoint)
                };
                
                var client = new OpenAIClient(new ApiKeyCredential(_config.ApiKey), clientOptions);
                _chatClient = client.GetChatClient(_config.Model);
                
                _logger.LogInformation("CitizenAIService initialized with endpoint: {Endpoint}, model: {Model}", 
                    _config.Endpoint, _config.Model);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to initialize AI client. AI decisions will be disabled.");
                _config.Enabled = false;
            }
        }
    }
    
    /// <summary>
    /// Determine if this decision should use AI based on configuration.
    /// </summary>
    public bool ShouldUseAI()
    {
        if (!_config.Enabled || _chatClient == null)
            return false;
            
        return _random.NextDouble() < _config.AIDecisionRatio;
    }
    
    /// <summary>
    /// Get an AI-powered decision for a citizen.
    /// </summary>
    public async Task<CitizenDecisionResponse?> GetDecisionAsync(
        Citizen citizen, 
        WorldState worldState, 
        List<Actions.ActionType> availableActions,
        CancellationToken cancellationToken = default)
    {
        if (_chatClient == null)
            return null;
            
        try
        {
            var prompt = BuildDecisionPrompt(citizen, worldState, availableActions);
            var systemPrompt = BuildSystemPrompt();
            
            var messages = new List<ChatMessage>
            {
                new SystemChatMessage(systemPrompt),
                new UserChatMessage(prompt)
            };
            
            var options = new ChatCompletionOptions
            {
                MaxOutputTokenCount = _config.MaxTokens,
                Temperature = _config.Temperature,
                ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
                    "citizen_decision",
                    BinaryData.FromString(GetDecisionJsonSchema()),
                    jsonSchemaIsStrict: true)
            };
            
            var response = await _chatClient.CompleteChatAsync(messages, options, cancellationToken);
            
            if (response.Value.Content.Count > 0)
            {
                var jsonResponse = response.Value.Content[0].Text;
                var decision = JsonSerializer.Deserialize<CitizenDecisionResponse>(jsonResponse);
                
                _logger.LogDebug("AI Decision for {CitizenName}: {Action} - {Reasoning}", 
                    citizen.Name, decision?.Action, decision?.Reasoning);
                    
                return decision;
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "AI decision failed for citizen {CitizenName}. Falling back to rules.", 
                citizen.Name);
        }
        
        return null;
    }
    
    /// <summary>
    /// Analyze a citizen's personality using AI.
    /// </summary>
    public async Task<CitizenPersonalityAnalysis?> AnalyzePersonalityAsync(
        Citizen citizen,
        CancellationToken cancellationToken = default)
    {
        if (_chatClient == null)
            return null;
            
        try
        {
            var prompt = $@"Analyze this citizen's personality based on their traits:

Name: {citizen.Name}
Age: {citizen.Age}

Traits:
- Sociability: {citizen.Traits.Sociability:F2} (0=introverted, 1=extroverted)
- Risk Tolerance: {citizen.Traits.RiskTolerance:F2} (0=risk-averse, 1=risk-seeking)
- Frugality: {citizen.Traits.Frugality:F2} (0=spender, 1=saver)
- Ambition: {citizen.Traits.Ambition:F2} (0=content, 1=ambitious)
- Stability: {citizen.Traits.Stability:F2} (0=change-seeking, 1=stability-seeking)

Skills: {string.Join(", ", citizen.Skills.Select(s => $"{s.Name} ({s.Level:F1})"))}

Provide a brief personality analysis.";

            var messages = new List<ChatMessage>
            {
                new SystemChatMessage("You are a personality analyst. Provide structured personality insights."),
                new UserChatMessage(prompt)
            };
            
            var options = new ChatCompletionOptions
            {
                MaxOutputTokenCount = 300,
                Temperature = 0.5f,
                ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
                    "personality_analysis",
                    BinaryData.FromString(GetPersonalityJsonSchema()),
                    jsonSchemaIsStrict: true)
            };
            
            var response = await _chatClient.CompleteChatAsync(messages, options, cancellationToken);
            
            if (response.Value.Content.Count > 0)
            {
                var jsonResponse = response.Value.Content[0].Text;
                return JsonSerializer.Deserialize<CitizenPersonalityAnalysis>(jsonResponse);
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Personality analysis failed for {CitizenName}", citizen.Name);
        }
        
        return null;
    }
    
    private string BuildSystemPrompt()
    {
        return @"You are a decision engine for simulated city citizens in Urbanium.
Your role is to make realistic, bounded decisions based on citizen needs, traits, and available actions.

Core principles:
1. Decisions must be from the available actions list only
2. Consider the citizen's current needs (hunger, energy, social, shelter, income)
3. Factor in personality traits when making decisions
4. Be deterministic - similar situations should produce consistent decisions
5. Prioritize survival needs (hunger, energy) over social needs
6. Consider the time of day and working hours

Always respond with valid JSON matching the required schema.";
    }
    
    private string BuildDecisionPrompt(Citizen citizen, WorldState worldState, List<Actions.ActionType> availableActions)
    {
        var actionsList = string.Join(", ", availableActions.Select(a => a.ToString()));
        
        return $@"Make a decision for this citizen:

CITIZEN PROFILE:
- Name: {citizen.Name}
- Age: {citizen.Age}
- State: {citizen.State}
- Cash: {citizen.Resources.Cash:C}
- Monthly Income: {citizen.Resources.MonthlyIncome:C}

CURRENT NEEDS (0=satisfied, 1=critical):
- Hunger: {citizen.Needs.Hunger:F2}
- Energy: {citizen.Needs.Energy:F2}
- Social: {citizen.Needs.Social:F2}
- Shelter: {citizen.Needs.Shelter:F2}
- Income: {citizen.Needs.Income:F2}

PERSONALITY TRAITS (0-1 scale):
- Sociability: {citizen.Traits.Sociability:F2}
- Risk Tolerance: {citizen.Traits.RiskTolerance:F2}
- Frugality: {citizen.Traits.Frugality:F2}
- Ambition: {citizen.Traits.Ambition:F2}
- Stability: {citizen.Traits.Stability:F2}

WORLD STATE:
- Current Time: {worldState.Time:HH:mm}
- Working Hours: {worldState.IsWorkingHours}
- Daytime: {worldState.IsDaytime}
- Open Job Positions: {worldState.LaborMarket.OpenPositions.Count}
- Available Housing: {worldState.HousingMarket.AvailableUnits.Count(u => !u.IsOccupied)}

AVAILABLE ACTIONS: {actionsList}

Choose ONE action from the available actions and explain your reasoning.";
    }
    
    private string GetDecisionJsonSchema()
    {
        return @"{
            ""type"": ""object"",
            ""properties"": {
                ""action"": {
                    ""type"": ""string"",
                    ""description"": ""The chosen action (must be one of: WorkShift, Rest, Eat, Commute, Socialize, JobSearch, HousingChange)""
                },
                ""reasoning"": {
                    ""type"": ""string"",
                    ""description"": ""Brief explanation for the decision (1-2 sentences)""
                },
                ""confidence"": {
                    ""type"": ""number"",
                    ""description"": ""Confidence level in the decision (0.0 to 1.0)""
                },
                ""need_priority"": {
                    ""type"": ""string"",
                    ""description"": ""The primary need this action addresses""
                },
                ""expected_outcome"": {
                    ""type"": ""string"",
                    ""description"": ""Expected result of taking this action""
                }
            },
            ""required"": [""action"", ""reasoning"", ""confidence"", ""need_priority"", ""expected_outcome""],
            ""additionalProperties"": false
        }";
    }
    
    private string GetPersonalityJsonSchema()
    {
        return @"{
            ""type"": ""object"",
            ""properties"": {
                ""dominant_trait"": {
                    ""type"": ""string"",
                    ""description"": ""The most influential personality trait""
                },
                ""behavior_tendency"": {
                    ""type"": ""string"",
                    ""description"": ""How this citizen tends to behave""
                },
                ""risk_assessment"": {
                    ""type"": ""string"",
                    ""description"": ""Assessment of how the citizen handles risk""
                },
                ""social_style"": {
                    ""type"": ""string"",
                    ""description"": ""How the citizen interacts socially""
                }
            },
            ""required"": [""dominant_trait"", ""behavior_tendency"", ""risk_assessment"", ""social_style""],
            ""additionalProperties"": false
        }";
    }
}
