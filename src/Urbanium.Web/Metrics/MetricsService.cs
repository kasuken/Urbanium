namespace Urbanium.Web.Metrics;

/// <summary>
/// Service for tracking and aggregating simulation metrics.
/// Metrics matter more than stories - Urbanium tracks measurable outcomes.
/// </summary>
public class MetricsService
{
    private readonly List<MetricDataPoint> _employmentHistory = new();
    private readonly List<MetricDataPoint> _wageHistory = new();
    private readonly List<MetricDataPoint> _rentHistory = new();
    private readonly List<MetricDataPoint> _commuteHistory = new();
    private readonly List<MetricDataPoint> _giniHistory = new();
    private readonly List<MetricDataPoint> _housingPressureHistory = new();
    
    public event Action? OnMetricsUpdated;
    
    /// <summary>
    /// Record metrics for the current tick.
    /// </summary>
    public void RecordMetrics(Engine.WorldState worldState)
    {
        var tick = worldState.CurrentTick;
        var time = worldState.Time;
        
        // Employment rate
        var totalCitizens = worldState.Citizens.Count;
        var employed = worldState.Citizens.Count(c => c.EmployerId.HasValue);
        var employmentRate = totalCitizens > 0 ? (double)employed / totalCitizens : 0;
        _employmentHistory.Add(new MetricDataPoint(tick, time, employmentRate));
        worldState.Metrics.EmploymentRate = employmentRate;
        
        // Average wage
        var avgWage = worldState.Citizens
            .Where(c => c.Resources.MonthlyIncome > 0)
            .Select(c => (double)c.Resources.MonthlyIncome)
            .DefaultIfEmpty(0)
            .Average();
        _wageHistory.Add(new MetricDataPoint(tick, time, avgWage));
        worldState.Metrics.AverageWage = avgWage;
        
        // Rent index
        var avgRent = worldState.HousingMarket.AvailableUnits
            .Select(u => (double)u.Rent)
            .DefaultIfEmpty(0)
            .Average();
        _rentHistory.Add(new MetricDataPoint(tick, time, avgRent));
        worldState.Metrics.RentIndex = avgRent;
        
        // Gini coefficient
        var gini = CalculateGini(worldState.Citizens.Select(c => (double)c.Resources.Cash).ToList());
        _giniHistory.Add(new MetricDataPoint(tick, time, gini));
        worldState.Metrics.GiniCoefficient = gini;
        
        // Housing pressure
        var totalUnits = worldState.HousingMarket.AvailableUnits.Count;
        var occupiedUnits = worldState.HousingMarket.AvailableUnits.Count(u => u.IsOccupied);
        var housingPressure = totalUnits > 0 ? (double)occupiedUnits / totalUnits : 1.0;
        _housingPressureHistory.Add(new MetricDataPoint(tick, time, housingPressure));
        worldState.Metrics.HousingPressure = housingPressure;
        
        // Store snapshot
        worldState.Metrics.History.Add(new Engine.MetricSnapshot
        {
            Tick = tick,
            Time = time,
            EmploymentRate = employmentRate,
            AverageWage = avgWage,
            RentIndex = avgRent,
            GiniCoefficient = gini
        });
        
        // Keep only last 1000 snapshots
        if (worldState.Metrics.History.Count > 1000)
        {
            worldState.Metrics.History.RemoveAt(0);
        }
        
        OnMetricsUpdated?.Invoke();
    }
    
    /// <summary>
    /// Calculate Gini coefficient for wealth distribution.
    /// </summary>
    private double CalculateGini(List<double> values)
    {
        if (values.Count == 0) return 0;
        
        values.Sort();
        int n = values.Count;
        double sum = values.Sum();
        
        if (sum == 0) return 0;
        
        double cumulative = 0;
        double giniSum = 0;
        
        for (int i = 0; i < n; i++)
        {
            cumulative += values[i];
            giniSum += (2 * (i + 1) - n - 1) * values[i];
        }
        
        return giniSum / (n * sum);
    }
    
    public List<MetricDataPoint> GetEmploymentHistory() => _employmentHistory.ToList();
    public List<MetricDataPoint> GetWageHistory() => _wageHistory.ToList();
    public List<MetricDataPoint> GetRentHistory() => _rentHistory.ToList();
    public List<MetricDataPoint> GetCommuteHistory() => _commuteHistory.ToList();
    public List<MetricDataPoint> GetGiniHistory() => _giniHistory.ToList();
    public List<MetricDataPoint> GetHousingPressureHistory() => _housingPressureHistory.ToList();
    
    public void Clear()
    {
        _employmentHistory.Clear();
        _wageHistory.Clear();
        _rentHistory.Clear();
        _commuteHistory.Clear();
        _giniHistory.Clear();
        _housingPressureHistory.Clear();
    }
}

public record MetricDataPoint(long Tick, DateTime Time, double Value);
