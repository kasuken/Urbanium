namespace Urbanium.Web.Actions;

/// <summary>
/// Available actions in Urbanium v0.
/// Actions are proposals - the world enforces legality, cost, and consequences.
/// </summary>
public enum ActionType
{
    /// <summary>Perform work at current employer</summary>
    WorkShift,
    
    /// <summary>Rest and recover energy</summary>
    Rest,
    
    /// <summary>Consume food to reduce hunger</summary>
    Eat,
    
    /// <summary>Travel between districts</summary>
    Commute,
    
    /// <summary>Interact with social connections</summary>
    Socialize,
    
    /// <summary>Search for employment opportunities</summary>
    JobSearch,
    
    /// <summary>Change housing situation</summary>
    HousingChange
}

/// <summary>
/// Base class for action proposals from citizens.
/// </summary>
public abstract class ActionProposal
{
    public Guid CitizenId { get; set; }
    public ActionType Type { get; set; }
    public long Tick { get; set; }
}

/// <summary>
/// Result of action validation and execution by the world.
/// </summary>
public class ActionResult
{
    public bool Success { get; set; }
    public string? FailureReason { get; set; }
    public Dictionary<string, object> Effects { get; set; } = new();
}

public class WorkShiftAction : ActionProposal
{
    public WorkShiftAction() => Type = ActionType.WorkShift;
    
    public Guid EmployerId { get; set; }
    public int HoursWorked { get; set; } = 8;
}

public class RestAction : ActionProposal
{
    public RestAction() => Type = ActionType.Rest;
    
    public int HoursRested { get; set; } = 8;
}

public class EatAction : ActionProposal
{
    public EatAction() => Type = ActionType.Eat;
    
    public decimal Cost { get; set; }
}

public class CommuteAction : ActionProposal
{
    public CommuteAction() => Type = ActionType.Commute;
    
    public Guid FromDistrictId { get; set; }
    public Guid ToDistrictId { get; set; }
    public Engine.TransportType TransportType { get; set; }
}

public class SocializeAction : ActionProposal
{
    public SocializeAction() => Type = ActionType.Socialize;
    
    public Guid? TargetCitizenId { get; set; }
    public int Duration { get; set; } // hours
}

public class JobSearchAction : ActionProposal
{
    public JobSearchAction() => Type = ActionType.JobSearch;
    
    public List<string> TargetSkills { get; set; } = new();
    public decimal MinimumWage { get; set; }
}

public class HousingChangeAction : ActionProposal
{
    public HousingChangeAction() => Type = ActionType.HousingChange;
    
    public Guid TargetHousingUnitId { get; set; }
}
