namespace Urbanium.Models;

public class Mayor
{
    public string Name { get; set; } = "Mayor Alexandra Sterling";
    public string Emoji { get; set; } = "🤖";
    public string Quote { get; set; } = "Managing Urbanium with efficiency and care.";
    public int ApprovalRating { get; set; } = 75;
    
    // Decision tracking
    public int DaysUntilNextDecision { get; set; } = 30;
    public string LastDecision { get; set; } = "";
    public string LastDecisionReason { get; set; } = "";
    public DateTime LastDecisionDate { get; set; } = DateTime.MinValue;
    public List<string> RecentDecisions { get; set; } = new();
    
    // Mayor's focus areas (affects decision-making)
    public string PrimaryFocus { get; set; } = "Economic Growth";
    public string SecondaryFocus { get; set; } = "Citizen Welfare";
}

/// <summary>
/// Represents a policy decision made by the mayor
/// </summary>
public class MayorDecision
{
    public string PolicyArea { get; set; } = "";    // Economy, Housing, Social, Work
    public string Action { get; set; } = "";         // What changed
    public string Reasoning { get; set; } = "";      // Why
    public Dictionary<string, object> Changes { get; set; } = new();  // Actual policy changes
    public int ProjectedApprovalChange { get; set; } = 0;  // Expected approval rating change
}
