using System.Text.Json.Serialization;

namespace Urbanium.Web.AI;

/// <summary>
/// Structured output format for citizen AI decisions.
/// This format ensures deterministic, parseable responses from the AI.
/// </summary>
public class CitizenDecisionResponse
{
    /// <summary>
    /// The chosen action from the available actions.
    /// </summary>
    [JsonPropertyName("action")]
    public string Action { get; set; } = string.Empty;
    
    /// <summary>
    /// Brief reasoning for the decision (1-2 sentences).
    /// </summary>
    [JsonPropertyName("reasoning")]
    public string Reasoning { get; set; } = string.Empty;
    
    /// <summary>
    /// Confidence level in the decision (0.0 - 1.0).
    /// </summary>
    [JsonPropertyName("confidence")]
    public float Confidence { get; set; }
    
    /// <summary>
    /// Priority of needs addressed by this action.
    /// </summary>
    [JsonPropertyName("need_priority")]
    public string NeedPriority { get; set; } = string.Empty;
    
    /// <summary>
    /// Expected outcome of the action.
    /// </summary>
    [JsonPropertyName("expected_outcome")]
    public string ExpectedOutcome { get; set; } = string.Empty;
}

/// <summary>
/// Structured output for citizen personality analysis.
/// </summary>
public class CitizenPersonalityAnalysis
{
    [JsonPropertyName("dominant_trait")]
    public string DominantTrait { get; set; } = string.Empty;
    
    [JsonPropertyName("behavior_tendency")]
    public string BehaviorTendency { get; set; } = string.Empty;
    
    [JsonPropertyName("risk_assessment")]
    public string RiskAssessment { get; set; } = string.Empty;
    
    [JsonPropertyName("social_style")]
    public string SocialStyle { get; set; } = string.Empty;
}

/// <summary>
/// Structured output for market analysis by AI.
/// </summary>
public class MarketAnalysisResponse
{
    [JsonPropertyName("market_state")]
    public string MarketState { get; set; } = string.Empty;
    
    [JsonPropertyName("trend")]
    public string Trend { get; set; } = string.Empty;
    
    [JsonPropertyName("recommendation")]
    public string Recommendation { get; set; } = string.Empty;
    
    [JsonPropertyName("risk_level")]
    public string RiskLevel { get; set; } = string.Empty;
}
