namespace Urbanium.Web.AI;

/// <summary>
/// Configuration for AI services, supporting OpenAI-compatible endpoints like LM Studio.
/// </summary>
public class AIConfiguration
{
    public const string SectionName = "AI";
    
    /// <summary>
    /// The base endpoint URL for the AI service.
    /// For LM Studio: http://localhost:1234/v1
    /// For OpenAI: https://api.openai.com/v1
    /// For Azure OpenAI: https://your-resource.openai.azure.com/
    /// </summary>
    public string Endpoint { get; set; } = "http://localhost:1234/v1";
    
    /// <summary>
    /// API key for authentication. Leave empty for local LM Studio.
    /// </summary>
    public string ApiKey { get; set; } = "lm-studio";
    
    /// <summary>
    /// The model identifier to use.
    /// For LM Studio: use the model name loaded in LM Studio
    /// For OpenAI: gpt-4o, gpt-4o-mini, etc.
    /// </summary>
    public string Model { get; set; } = "local-model";
    
    /// <summary>
    /// Maximum tokens for AI responses.
    /// </summary>
    public int MaxTokens { get; set; } = 500;
    
    /// <summary>
    /// Temperature for response generation (0.0 - 2.0).
    /// Lower = more deterministic, higher = more creative.
    /// </summary>
    public float Temperature { get; set; } = 0.7f;
    
    /// <summary>
    /// Whether AI decision-making is enabled.
    /// When disabled, citizens use rule-based decisions only.
    /// </summary>
    public bool Enabled { get; set; } = true;
    
    /// <summary>
    /// Percentage of decisions that should use AI (0.0 - 1.0).
    /// Allows hybrid rule-based + AI decision making.
    /// </summary>
    public float AIDecisionRatio { get; set; } = 0.3f;
}
