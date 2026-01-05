namespace Urbanium.Web.Scenarios;

/// <summary>
/// Defines initial conditions for simulation experiments.
/// </summary>
public class Scenario
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    
    public int Seed { get; set; } = 42;
    public int InitialPopulation { get; set; } = 100;
    public int DistrictCount { get; set; } = 5;
    public int EmployerCount { get; set; } = 10;
    public int HousingUnits { get; set; } = 120;
    
    public ScenarioEconomySettings Economy { get; set; } = new();
    public List<ScenarioIntervention> Interventions { get; set; } = new();
}

public class ScenarioEconomySettings
{
    public decimal MinimumWage { get; set; } = 2000m;
    public decimal AverageRent { get; set; } = 800m;
    public double UnemploymentBenefit { get; set; } = 0.4; // % of min wage
    public double TaxRate { get; set; } = 0.25;
}

/// <summary>
/// Policy intervention that can be applied during simulation.
/// </summary>
public class ScenarioIntervention
{
    public long ApplyAtTick { get; set; }
    public string Type { get; set; } = string.Empty;
    public Dictionary<string, object> Parameters { get; set; } = new();
}

/// <summary>
/// Factory for creating predefined scenarios.
/// </summary>
public static class ScenarioFactory
{
    public static Scenario CreateDefault()
    {
        return new Scenario
        {
            Id = "default",
            Name = "Default City",
            Description = "A balanced city with standard economic parameters.",
            Seed = 42,
            InitialPopulation = 100,
            DistrictCount = 5,
            EmployerCount = 10,
            HousingUnits = 120
        };
    }
    
    public static Scenario CreateHighDensity()
    {
        return new Scenario
        {
            Id = "high-density",
            Name = "High Density Urban",
            Description = "A densely populated city with housing pressure.",
            Seed = 123,
            InitialPopulation = 200,
            DistrictCount = 3,
            EmployerCount = 15,
            HousingUnits = 150,
            Economy = new ScenarioEconomySettings
            {
                AverageRent = 1200m
            }
        };
    }
    
    public static Scenario CreateEconomicCrisis()
    {
        return new Scenario
        {
            Id = "economic-crisis",
            Name = "Economic Crisis",
            Description = "A city experiencing economic downturn with high unemployment.",
            Seed = 456,
            InitialPopulation = 100,
            DistrictCount = 5,
            EmployerCount = 5,
            HousingUnits = 100,
            Economy = new ScenarioEconomySettings
            {
                MinimumWage = 1500m,
                AverageRent = 900m
            }
        };
    }
    
    public static List<Scenario> GetAllScenarios()
    {
        return new List<Scenario>
        {
            CreateDefault(),
            CreateHighDensity(),
            CreateEconomicCrisis()
        };
    }
}
