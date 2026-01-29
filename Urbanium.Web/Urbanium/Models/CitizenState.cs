namespace Urbanium.Models;

/// <summary>
/// Current state of a citizen's basic needs (0-100 scale, 0 = critical, 100 = fully satisfied)
/// </summary>
public class CitizenNeeds
{
    public int Hunger { get; set; } = 80;           // Need for food
    public int Energy { get; set; } = 100;          // Need for sleep/rest
    public int Social { get; set; } = 70;           // Need for social interaction
    public int Happiness { get; set; } = 75;        // Overall happiness/satisfaction
    public int Health { get; set; } = 100;          // Physical health
    
    /// <summary>
    /// Get the most critical need (lowest value)
    /// </summary>
    public string GetMostCriticalNeed()
    {
        var needs = new Dictionary<string, int>
        {
            ["Hunger"] = Hunger,
            ["Energy"] = Energy,
            ["Social"] = Social,
            ["Happiness"] = Happiness,
            ["Health"] = Health
        };
        return needs.OrderBy(n => n.Value).First().Key;
    }
    
    /// <summary>
    /// Check if any need is critical (below 20)
    /// </summary>
    public bool HasCriticalNeed() => Hunger < 20 || Energy < 20 || Health < 20;
    
    /// <summary>
    /// Get overall wellbeing score
    /// </summary>
    public int GetOverallWellbeing() => (Hunger + Energy + Social + Happiness + Health) / 5;
}

/// <summary>
/// Housing status of a citizen
/// </summary>
public enum HousingStatus
{
    Homeless,
    Renting,
    Owner,
    LivingWithFamily
}

/// <summary>
/// Employment status of a citizen
/// </summary>
public enum EmploymentStatus
{
    Unemployed,
    Employed,
    BusinessOwner,
    Student,
    Retired,
    Child
}

/// <summary>
/// Relationship status of a citizen
/// </summary>
public enum RelationshipStatus
{
    Single,
    Dating,
    Partnered,
    Married,
    Divorced,
    Widowed
}

/// <summary>
/// Education level of a citizen
/// </summary>
public enum EducationLevel
{
    None,
    Elementary,
    HighSchool,
    Bachelors,
    Masters,
    Doctorate
}

/// <summary>
/// Life stage of a citizen
/// </summary>
public enum LifeStage
{
    Child,      // 0-12
    Teen,       // 13-17
    YoungAdult, // 18-30
    Adult,      // 31-55
    Senior      // 56+
}

/// <summary>
/// Housing details for a citizen
/// </summary>
public class HousingInfo
{
    public HousingStatus Status { get; set; } = HousingStatus.Homeless;
    public string? BuildingName { get; set; }
    public int MonthlyRent { get; set; } = 0;        // If renting
    public int PropertyValue { get; set; } = 0;       // If owned
    public int MortgageRemaining { get; set; } = 0;   // If has mortgage
}

/// <summary>
/// Employment details for a citizen
/// </summary>
public class EmploymentInfo
{
    public EmploymentStatus Status { get; set; } = EmploymentStatus.Unemployed;
    public string? JobTitle { get; set; }
    public string? Employer { get; set; }           // Building name or business name
    public int Salary { get; set; } = 0;            // Monthly salary
    public int WorkHoursPerDay { get; set; } = 8;   // Hours worked per day
    public int WorkStartHour { get; set; } = 9;     // When work starts
    public int DaysWorkedThisWeek { get; set; } = 0;
    
    /// <summary>
    /// For business owners: details about their business
    /// </summary>
    public string? BusinessName { get; set; }
    public int EmployeeCount { get; set; } = 0;
    public int BusinessRevenue { get; set; } = 0;
}

/// <summary>
/// Relationship and family information
/// </summary>
public class FamilyInfo
{
    public RelationshipStatus Status { get; set; } = RelationshipStatus.Single;
    public string? PartnerId { get; set; }           // ID of partner/spouse
    public string? PartnerName { get; set; }
    public List<string> ChildrenIds { get; set; } = new();  // IDs of children
    public List<string> ChildrenNames { get; set; } = new();
    public string? ParentId { get; set; }            // For children: their parent
    public int RelationshipSatisfaction { get; set; } = 50; // 0-100
}

/// <summary>
/// Education information
/// </summary>
public class EducationInfo
{
    public EducationLevel Level { get; set; } = EducationLevel.HighSchool;
    public bool CurrentlyStudying { get; set; } = false;
    public string? CurrentDegree { get; set; }       // What they're studying
    public int StudyProgress { get; set; } = 0;      // 0-100, progress toward degree
    public List<string> Degrees { get; set; } = new(); // Completed degrees
}

/// <summary>
/// Financial information
/// </summary>
public class FinancialInfo
{
    public int Savings { get; set; } = 1000;         // Current savings
    public int MonthlyIncome { get; set; } = 0;      // From job or business
    public int MonthlyExpenses { get; set; } = 500;  // Living expenses
    public int Debt { get; set; } = 0;               // Total debt
    
    /// <summary>
    /// Calculate months of runway (how long savings will last)
    /// </summary>
    public int GetMonthsOfRunway()
    {
        var netMonthly = MonthlyIncome - MonthlyExpenses;
        if (netMonthly >= 0) return int.MaxValue;
        return Math.Max(0, Savings / Math.Abs(netMonthly));
    }
    
    /// <summary>
    /// Can afford a purchase
    /// </summary>
    public bool CanAfford(int amount) => Savings >= amount;
}

/// <summary>
/// What activity the citizen is currently doing
/// </summary>
public enum CurrentActivity
{
    Sleeping,
    Eating,
    Working,
    Studying,
    Socializing,
    AtHome,
    Shopping,
    Commuting,
    AtBar,
    OnDate,
    PlayingWithKids,
    LookingForJob,
    LookingForHousing,
    Idle
}

/// <summary>
/// Complete state of a citizen at any point in time
/// </summary>
public class CitizenState
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public int Age { get; set; } = 30;
    public LifeStage LifeStage { get; set; } = LifeStage.Adult;
    
    // Core needs
    public CitizenNeeds Needs { get; set; } = new();
    
    // Life domains
    public HousingInfo Housing { get; set; } = new();
    public EmploymentInfo Employment { get; set; } = new();
    public FamilyInfo Family { get; set; } = new();
    public EducationInfo Education { get; set; } = new();
    public FinancialInfo Finances { get; set; } = new();
    
    // Current activity
    public CurrentActivity Activity { get; set; } = CurrentActivity.Idle;
    public string ActivityDescription { get; set; } = "";
    
    // Daily tracking
    public int HoursWorkedToday { get; set; } = 0;
    public int MealsEatenToday { get; set; } = 0;
    public bool HasSleptToday { get; set; } = false;
    
    // History of recent decisions for context
    public List<string> RecentDecisions { get; set; } = new();
    
    /// <summary>
    /// Updates life stage based on age
    /// </summary>
    public void UpdateLifeStage()
    {
        LifeStage = Age switch
        {
            < 13 => LifeStage.Child,
            < 18 => LifeStage.Teen,
            < 31 => LifeStage.YoungAdult,
            < 56 => LifeStage.Adult,
            _ => LifeStage.Senior
        };
    }
    
    /// <summary>
    /// Get a status summary for the citizen
    /// </summary>
    public string GetStatusSummary()
    {
        var parts = new List<string>();
        
        parts.Add($"Age {Age} ({LifeStage})");
        parts.Add($"Housing: {Housing.Status}");
        parts.Add($"Employment: {Employment.Status}");
        parts.Add($"Relationship: {Family.Status}");
        parts.Add($"Savings: ${Finances.Savings:N0}");
        parts.Add($"Wellbeing: {Needs.GetOverallWellbeing()}%");
        
        return string.Join(" | ", parts);
    }
}
