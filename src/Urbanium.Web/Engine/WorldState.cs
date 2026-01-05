namespace Urbanium.Web.Engine;

/// <summary>
/// The world state is explicit and versioned.
/// It is the single source of truth for the simulation.
/// </summary>
public class WorldState
{
    public int Seed { get; }
    public long CurrentTick { get; set; }
    public DateTime Time { get; set; }
    public bool IsWorkingHours { get; set; }
    public bool IsDaytime { get; set; }
    
    // Geography
    public Geography Geography { get; set; }
    
    // Markets
    public LaborMarket LaborMarket { get; set; }
    public HousingMarket HousingMarket { get; set; }
    public GoodsMarket GoodsMarket { get; set; }
    
    // Population
    public List<Agents.Citizen> Citizens { get; set; }
    public List<Household> Households { get; set; }
    
    // Institutions
    public List<Employer> Employers { get; set; }
    public List<PublicService> PublicServices { get; set; }
    
    // Metrics
    public SimulationMetrics Metrics { get; set; }
    
    // Events
    public List<SimulationEvent> Events { get; set; }
    
    public WorldState(int seed)
    {
        Seed = seed;
        CurrentTick = 0;
        Time = new DateTime(2026, 1, 1, 8, 0, 0);
        
        Geography = new Geography();
        LaborMarket = new LaborMarket();
        HousingMarket = new HousingMarket();
        GoodsMarket = new GoodsMarket();
        Citizens = new List<Agents.Citizen>();
        Households = new List<Household>();
        Employers = new List<Employer>();
        PublicServices = new List<PublicService>();
        Metrics = new SimulationMetrics();
        Events = new List<SimulationEvent>();
    }
}

/// <summary>
/// Spatial graph representing the city geography.
/// </summary>
public class Geography
{
    public List<District> Districts { get; set; } = new();
    public List<Connection> Connections { get; set; } = new();
}

public class District
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Name { get; set; } = string.Empty;
    public DistrictType Type { get; set; }
    public double X { get; set; }
    public double Y { get; set; }
    public int Capacity { get; set; }
    public double RentIndex { get; set; } = 1.0;
}

public enum DistrictType
{
    Residential,
    Commercial,
    Industrial,
    Mixed,
    Central
}

public class Connection
{
    public Guid FromDistrictId { get; set; }
    public Guid ToDistrictId { get; set; }
    public double TravelTime { get; set; } // in minutes
    public TransportType TransportType { get; set; }
}

public enum TransportType
{
    Walking,
    PublicTransit,
    Vehicle
}

/// <summary>
/// Labor market with job listings and employment relationships.
/// </summary>
public class LaborMarket
{
    public List<JobListing> OpenPositions { get; set; } = new();
    public double AverageWage { get; set; }
    public double UnemploymentRate { get; set; }
}

public class JobListing
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid EmployerId { get; set; }
    public string Title { get; set; } = string.Empty;
    public List<string> RequiredSkills { get; set; } = new();
    public decimal Wage { get; set; }
    public Guid LocationDistrictId { get; set; }
}

/// <summary>
/// Housing market with available units and rent dynamics.
/// </summary>
public class HousingMarket
{
    public List<HousingUnit> AvailableUnits { get; set; } = new();
    public double AverageRent { get; set; }
    public double Vacancy { get; set; }
}

public class HousingUnit
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid DistrictId { get; set; }
    public int Capacity { get; set; }
    public decimal Rent { get; set; }
    public bool IsOccupied { get; set; }
}

/// <summary>
/// Goods market for consumables.
/// </summary>
public class GoodsMarket
{
    public double FoodPriceIndex { get; set; } = 1.0;
    public double SupplyLevel { get; set; } = 1.0;
}

/// <summary>
/// Household unit containing citizens.
/// </summary>
public class Household
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public List<Guid> MemberIds { get; set; } = new();
    public Guid? HousingUnitId { get; set; }
    public decimal TotalIncome { get; set; }
    public decimal Savings { get; set; }
}

/// <summary>
/// Employer entity that provides jobs.
/// </summary>
public class Employer
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Name { get; set; } = string.Empty;
    public EmployerType Type { get; set; }
    public Guid DistrictId { get; set; }
    public int EmployeeCount { get; set; }
    public int MaxEmployees { get; set; }
    public decimal WageBudget { get; set; }
}

public enum EmployerType
{
    Private,
    Public,
    NonProfit
}

/// <summary>
/// Public service institutions.
/// </summary>
public class PublicService
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Name { get; set; } = string.Empty;
    public PublicServiceType Type { get; set; }
    public Guid DistrictId { get; set; }
    public double Capacity { get; set; }
    public double Utilization { get; set; }
}

public enum PublicServiceType
{
    Healthcare,
    Education,
    PublicTransport,
    Emergency,
    Administration
}

/// <summary>
/// Simulation metrics tracked over time.
/// </summary>
public class SimulationMetrics
{
    public DateTime LastUpdated { get; set; }
    public double EmploymentRate { get; set; }
    public double AverageWage { get; set; }
    public double RentIndex { get; set; }
    public double AverageCommuteTime { get; set; }
    public double GiniCoefficient { get; set; }
    public double SocialNetworkClustering { get; set; }
    public int AgentChurn { get; set; }
    public int Bankruptcies { get; set; }
    public double HousingPressure { get; set; }
    
    public List<MetricSnapshot> History { get; set; } = new();
}

public class MetricSnapshot
{
    public long Tick { get; set; }
    public DateTime Time { get; set; }
    public double EmploymentRate { get; set; }
    public double AverageWage { get; set; }
    public double RentIndex { get; set; }
    public double GiniCoefficient { get; set; }
}

/// <summary>
/// Events that occur during simulation.
/// </summary>
public class SimulationEvent
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public long Tick { get; set; }
    public DateTime Time { get; set; }
    public string Type { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public Dictionary<string, object> Data { get; set; } = new();
}
