namespace Urbanium.Configuration;

public class SimulationSettings
{
    /// <summary>
    /// Percentage chance (0-100) that a selected citizen makes an AI decision each tick
    /// </summary>
    public int CitizenDecisionChance { get; set; } = 40;
    
    /// <summary>
    /// Number of days between mayor policy decisions
    /// </summary>
    public int MayorDecisionIntervalDays { get; set; } = 30;
    
    /// <summary>
    /// Number of seconds per game hour (real time)
    /// </summary>
    public int SecondsPerHour { get; set; } = 10;
    
    /// <summary>
    /// Maximum number of activity log entries to keep
    /// </summary>
    public int MaxActivityLogEntries { get; set; } = 100;
    
    /// <summary>
    /// Initial mayor approval rating (0-100)
    /// </summary>
    public int InitialMayorApproval { get; set; } = 75;
}
