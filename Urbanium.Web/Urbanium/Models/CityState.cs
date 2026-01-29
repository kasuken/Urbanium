namespace Urbanium.Models;

/// <summary>
/// Represents the overall state of Urbanium city
/// </summary>
public class CityState
{
    // Economy
    public CityEconomy Economy { get; set; } = new();
    
    // Housing market
    public HousingMarket Housing { get; set; } = new();
    
    // Job market
    public JobMarket Jobs { get; set; } = new();
    
    // City statistics
    public CityStatistics Statistics { get; set; } = new();
    
    // Mayor policies (will affect citizen decisions)
    public MayorPolicies Policies { get; set; } = new();
}

/// <summary>
/// Economic state of the city
/// </summary>
public class CityEconomy
{
    public int GdpPerCapita { get; set; } = 45000;
    public double UnemploymentRate { get; set; } = 5.0;  // Percentage
    public double InflationRate { get; set; } = 2.5;     // Percentage
    public int AverageWage { get; set; } = 3500;         // Monthly
    public int MinimumWage { get; set; } = 1500;         // Monthly
    public double TaxRate { get; set; } = 25.0;          // Percentage
    
    // Economic health indicator (0-100)
    public int EconomicHealth => CalculateEconomicHealth();
    
    private int CalculateEconomicHealth()
    {
        var score = 100;
        if (UnemploymentRate > 10) score -= 30;
        else if (UnemploymentRate > 5) score -= 15;
        if (InflationRate > 5) score -= 20;
        else if (InflationRate > 3) score -= 10;
        return Math.Max(0, Math.Min(100, score));
    }
}

/// <summary>
/// Housing market state
/// </summary>
public class HousingMarket
{
    public int TotalHousingUnits { get; set; } = 124;
    public int OccupiedUnits { get; set; } = 98;
    public int AvailableUnits => TotalHousingUnits - OccupiedUnits;
    
    // Average prices
    public int AverageRent { get; set; } = 1200;          // Monthly
    public int SmallHousePrice { get; set; } = 150000;
    public int MediumHousePrice { get; set; } = 300000;
    public int SkyscraperUnitPrice { get; set; } = 200000;
    
    // Rental availability by type
    public List<AvailableHousing> AvailableHousingList { get; set; } = new();
    
    public double OccupancyRate => TotalHousingUnits > 0 
        ? (double)OccupiedUnits / TotalHousingUnits * 100 
        : 0;
}

/// <summary>
/// Represents an available housing option
/// </summary>
public class AvailableHousing
{
    public string BuildingName { get; set; } = "";
    public string Type { get; set; } = "";  // Small House, Medium House, Skyscraper
    public int MonthlyRent { get; set; } = 0;
    public int PurchasePrice { get; set; } = 0;
    public bool ForRent { get; set; } = true;
    public bool ForSale { get; set; } = true;
}

/// <summary>
/// Job market state
/// </summary>
public class JobMarket
{
    public List<JobOpening> AvailableJobs { get; set; } = new();
    public int TotalEmployed { get; set; } = 0;
    public int TotalUnemployed { get; set; } = 0;
    
    // Jobs available by sector
    public int HealthcareJobs { get; set; } = 2;
    public int RetailJobs { get; set; } = 5;
    public int ServiceJobs { get; set; } = 4;
    public int OfficeJobs { get; set; } = 3;
    public int PublicServiceJobs { get; set; } = 2;  // Fire, Police
    
    public int TotalOpenings => AvailableJobs.Count;
}

/// <summary>
/// Represents a job opening
/// </summary>
public class JobOpening
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Title { get; set; } = "";
    public string Employer { get; set; } = "";  // Building name
    public string Sector { get; set; } = "";    // Healthcare, Retail, etc.
    public int Salary { get; set; } = 2500;     // Monthly
    public int WorkHours { get; set; } = 8;     // Per day
    public int StartHour { get; set; } = 9;
    public EducationLevel RequiredEducation { get; set; } = EducationLevel.HighSchool;
    public string Description { get; set; } = "";
}

/// <summary>
/// City statistics
/// </summary>
public class CityStatistics
{
    public int TotalPopulation { get; set; } = 6;
    public int TotalBuildings { get; set; } = 14;
    public int Births { get; set; } = 0;
    public int Deaths { get; set; } = 0;
    public int Marriages { get; set; } = 0;
    public int NewBusinesses { get; set; } = 0;
    public double AverageHappiness { get; set; } = 75.0;
    public double CrimeRate { get; set; } = 2.0;  // Per 1000 people
}

/// <summary>
/// Mayor's policies that affect citizen decisions
/// </summary>
public class MayorPolicies
{
    // Economic policies
    public int TaxRate { get; set; } = 25;              // Percentage
    public int MinimumWage { get; set; } = 1500;
    public bool BusinessIncentives { get; set; } = true;
    
    // Housing policies
    public bool RentControl { get; set; } = false;
    public int MaxRentIncrease { get; set; } = 5;       // Percentage per year
    public bool AffordableHousingProgram { get; set; } = true;
    
    // Social policies
    public bool UnemploymentBenefits { get; set; } = true;
    public int UnemploymentBenefitAmount { get; set; } = 800;
    public bool FreeEducation { get; set; } = true;
    public bool HealthcareSubsidy { get; set; } = true;
    
    // Work policies
    public int MaxWorkHours { get; set; } = 10;
    public int MandatoryVacationDays { get; set; } = 20;
    
    // Get policy summary for AI context
    public string GetPolicySummary()
    {
        var policies = new List<string>();
        policies.Add($"Tax Rate: {TaxRate}%");
        policies.Add($"Minimum Wage: ${MinimumWage}/month");
        if (BusinessIncentives) policies.Add("Business incentives available");
        if (RentControl) policies.Add($"Rent control: max {MaxRentIncrease}% increase/year");
        if (AffordableHousingProgram) policies.Add("Affordable housing program active");
        if (UnemploymentBenefits) policies.Add($"Unemployment benefits: ${UnemploymentBenefitAmount}/month");
        if (FreeEducation) policies.Add("Free public education");
        if (HealthcareSubsidy) policies.Add("Healthcare subsidy active");
        policies.Add($"Max work hours: {MaxWorkHours}/day");
        
        return string.Join("; ", policies);
    }
}
