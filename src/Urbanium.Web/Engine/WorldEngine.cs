namespace Urbanium.Web.Engine;

/// <summary>
/// Represents the world engine that manages the simulation state and tick loop.
/// The world is the single source of truth - agents propose actions, the world validates and executes them.
/// </summary>
public class WorldEngine
{
    private readonly Random _random;
    private readonly object _lock = new();
    
    public WorldState State { get; private set; }
    public bool IsRunning { get; private set; }
    public int TickRate { get; set; } = 1000; // milliseconds per tick
    
    public event Action<WorldState>? OnTick;
    public event Action<string>? OnEvent;
    
    public WorldEngine()
    {
        _random = new Random(42); // Deterministic seed
        State = new WorldState(_random.Next());
    }
    
    /// <summary>
    /// Initialize the world with a specific seed for deterministic simulation.
    /// </summary>
    public void Initialize(int seed)
    {
        lock (_lock)
        {
            _random.Next(); // Advance RNG
            State = new WorldState(seed);
            OnEvent?.Invoke($"World initialized with seed {seed}");
        }
    }
    
    /// <summary>
    /// Advance the simulation by one tick.
    /// Each tick: World updates -> Agents propose -> World validates -> Metrics recorded
    /// </summary>
    public void Tick()
    {
        lock (_lock)
        {
            State.CurrentTick++;
            State.Time = State.Time.AddHours(1); // Each tick = 1 hour
            
            // 1. Update exogenous systems (time, weather, events)
            UpdateExogenousSystems();
            
            // 2. Process agent decisions (in actual implementation)
            // Agents receive local state, propose actions, world validates
            
            // 3. Update markets
            UpdateMarkets();
            
            // 4. Record metrics
            RecordMetrics();
            
            OnTick?.Invoke(State);
        }
    }
    
    private void UpdateExogenousSystems()
    {
        // Update time-based systems
        State.IsWorkingHours = State.Time.Hour >= 9 && State.Time.Hour < 17;
        State.IsDaytime = State.Time.Hour >= 6 && State.Time.Hour < 20;
    }
    
    private void UpdateMarkets()
    {
        // Placeholder for market dynamics
    }
    
    private void RecordMetrics()
    {
        // Metrics are recorded each tick
        State.Metrics.LastUpdated = State.Time;
    }
    
    public void Start()
    {
        IsRunning = true;
        OnEvent?.Invoke("Simulation started");
    }
    
    public void Stop()
    {
        IsRunning = false;
        OnEvent?.Invoke("Simulation stopped");
    }
    
    public void Reset(int? seed = null)
    {
        lock (_lock)
        {
            Initialize(seed ?? _random.Next());
            OnEvent?.Invoke("Simulation reset");
        }
    }
}
