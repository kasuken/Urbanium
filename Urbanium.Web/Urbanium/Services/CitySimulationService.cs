using Microsoft.Extensions.Options;
using Urbanium.Configuration;
using Urbanium.Models;

namespace Urbanium.Services;

/// <summary>
/// Event arguments for activity log entries
/// </summary>
public class ActivityLogEventArgs : EventArgs
{
    public string Timestamp { get; set; } = "";
    public string Message { get; set; } = "";
    public string CitizenName { get; set; } = "";
    public string Emoji { get; set; } = "";
    public string Category { get; set; } = "";  // Daily, Employment, Housing, Social, Family, System
}

/// <summary>
/// Event arguments when a citizen's state changes
/// </summary>
public class CitizenStateChangedEventArgs : EventArgs
{
    public Citizen Citizen { get; set; } = null!;
    public string ChangeType { get; set; } = "";
}

/// <summary>
/// Core service that runs the city simulation
/// </summary>
public class CitySimulationService
{
    private readonly CitizenAIEngine _aiEngine;
    private readonly MayorAgentService _mayorService;
    private readonly CityTimeService _timeService;
    private readonly ILogger<CitySimulationService> _logger;
    private readonly SimulationSettings _settings;
    private readonly Random _random = new();

    // City data
    private CityState _cityState = new();
    private List<Citizen> _citizens = new();
    private List<Building> _buildings = new();
    private Mayor _mayor = new();
    private int _lastProcessedDay = 0;

    // Events for UI updates
    public event EventHandler<ActivityLogEventArgs>? OnActivityLogged;
    public event EventHandler<CitizenStateChangedEventArgs>? OnCitizenStateChanged;
    public event EventHandler? OnCityStateChanged;
    public event EventHandler<MayorDecision>? OnMayorDecision;

    public CityState CityState => _cityState;
    public IReadOnlyList<Citizen> Citizens => _citizens.AsReadOnly();
    public IReadOnlyList<Building> Buildings => _buildings.AsReadOnly();
    public Mayor Mayor => _mayor;

    public CitySimulationService(
        CitizenAIEngine aiEngine,
        MayorAgentService mayorService,
        CityTimeService timeService,
        IOptions<SimulationSettings> settings,
        ILogger<CitySimulationService> logger)
    {
        _aiEngine = aiEngine;
        _mayorService = mayorService;
        _timeService = timeService;
        _settings = settings.Value;
        _logger = logger;

        // Subscribe to time changes
        _timeService.OnTimeChanged += OnTimeChangedAsync;
    }

    /// <summary>
    /// Initialize the simulation with citizens and buildings
    /// </summary>
    public void Initialize(List<Citizen> citizens, List<Building> buildings)
    {
        _citizens = citizens;
        _buildings = buildings;
        _lastProcessedDay = 0;
        
        // Initialize mayor
        _mayor = new Mayor
        {
            Name = "Mayor Alexandra Sterling",
            Emoji = "🤖",
            Quote = "Managing Urbanium with efficiency and care.",
            ApprovalRating = _settings.InitialMayorApproval,
            DaysUntilNextDecision = _settings.MayorDecisionIntervalDays,
            PrimaryFocus = "Economic Growth",
            SecondaryFocus = "Citizen Welfare"
        };
        
        // Initialize city state
        InitializeCityState();
        
        // Initialize citizen states
        foreach (var citizen in _citizens)
        {
            InitializeCitizenState(citizen);
        }

        LogActivity("System", "🏙️", "City simulation initialized with {0} citizens", "System", _citizens.Count.ToString());
    }

    /// <summary>
    /// Initialize the city state based on buildings
    /// </summary>
    private void InitializeCityState()
    {
        var residentialBuildings = _buildings.Where(b => b.Type == BuildingType.Residential).ToList();
        
        _cityState.Housing.TotalHousingUnits = residentialBuildings.Sum(b => b.Capacity);
        _cityState.Housing.OccupiedUnits = residentialBuildings.Sum(b => b.CurrentResidents);
        
        // Create available housing list
        _cityState.Housing.AvailableHousingList = residentialBuildings
            .Where(b => b.CurrentResidents < b.Capacity)
            .Select(b => new AvailableHousing
            {
                BuildingName = b.Name,
                Type = b.Name,
                MonthlyRent = b.Name switch
                {
                    "Small House" => 800,
                    "Medium House" => 1200,
                    "Skyscraper" => 1500,
                    _ => 1000
                },
                PurchasePrice = b.Name switch
                {
                    "Small House" => 150000,
                    "Medium House" => 300000,
                    "Skyscraper" => 200000,
                    _ => 200000
                },
                ForRent = true,
                ForSale = true
            }).ToList();

        // Create initial job openings
        InitializeJobMarket();

        _cityState.Statistics.TotalPopulation = _citizens.Count;
        _cityState.Statistics.TotalBuildings = _buildings.Count;
    }

    /// <summary>
    /// Create initial job openings based on commercial buildings
    /// </summary>
    private void InitializeJobMarket()
    {
        var jobs = new List<JobOpening>();

        foreach (var building in _buildings.Where(b => b.Type == BuildingType.Commercial))
        {
            var jobInfo = GetJobInfoForBuilding(building.Name);
            if (jobInfo.HasValue)
            {
                jobs.Add(new JobOpening
                {
                    Title = jobInfo.Value.title,
                    Employer = building.Name,
                    Sector = jobInfo.Value.sector,
                    Salary = jobInfo.Value.salary,
                    WorkHours = 8,
                    StartHour = 9,
                    RequiredEducation = jobInfo.Value.education,
                    Description = $"Position at {building.Name}"
                });
            }
        }

        _cityState.Jobs.AvailableJobs = jobs;
    }

    private (string title, string sector, int salary, EducationLevel education)? GetJobInfoForBuilding(string buildingName)
    {
        return buildingName switch
        {
            "Hospital" => ("Nurse", "Healthcare", 4500, EducationLevel.Bachelors),
            "Restaurant" => ("Server", "Service", 2200, EducationLevel.HighSchool),
            "Coffee Shop" => ("Barista", "Retail", 2000, EducationLevel.HighSchool),
            "Fast Food" => ("Cashier", "Retail", 1800, EducationLevel.HighSchool),
            "Office" => ("Office Worker", "Office", 3500, EducationLevel.Bachelors),
            "Car Shop" => ("Mechanic", "Service", 3000, EducationLevel.HighSchool),
            "Fire Station" => ("Firefighter", "Public Service", 4000, EducationLevel.HighSchool),
            "Police Station" => ("Police Officer", "Public Service", 4200, EducationLevel.HighSchool),
            _ => null
        };
    }

    /// <summary>
    /// Initialize a citizen's state based on their profile
    /// </summary>
    private void InitializeCitizenState(Citizen citizen)
    {
        var state = citizen.State;

        // Assign random age based on occupation
        state.Age = citizen.Occupation switch
        {
            "Business Owner" => _random.Next(35, 55),
            "Doctor" => _random.Next(32, 50),
            "Teacher" => _random.Next(28, 55),
            "Chef" => _random.Next(28, 50),
            "Mechanic" => _random.Next(25, 55),
            "Firefighter" => _random.Next(25, 45),
            _ => _random.Next(25, 50)
        };
        state.UpdateLifeStage();

        // Set initial employment based on occupation
        state.Employment = citizen.Occupation switch
        {
            "Business Owner" => new EmploymentInfo
            {
                Status = EmploymentStatus.BusinessOwner,
                BusinessName = "Chen Enterprises",
                Salary = 8000,
                EmployeeCount = 5
            },
            "Doctor" => new EmploymentInfo
            {
                Status = EmploymentStatus.Employed,
                JobTitle = "Doctor",
                Employer = "Hospital",
                Salary = 7500,
                WorkHoursPerDay = 10
            },
            "Teacher" => new EmploymentInfo
            {
                Status = EmploymentStatus.Employed,
                JobTitle = "Teacher",
                Employer = "Public School",
                Salary = 3500,
                WorkHoursPerDay = 7,
                WorkStartHour = 8
            },
            "Chef" => new EmploymentInfo
            {
                Status = EmploymentStatus.Employed,
                JobTitle = "Head Chef",
                Employer = "Restaurant",
                Salary = 4000,
                WorkHoursPerDay = 9,
                WorkStartHour = 10
            },
            "Mechanic" => new EmploymentInfo
            {
                Status = EmploymentStatus.Employed,
                JobTitle = "Lead Mechanic",
                Employer = "Car Shop",
                Salary = 3200,
                WorkHoursPerDay = 8
            },
            "Firefighter" => new EmploymentInfo
            {
                Status = EmploymentStatus.Employed,
                JobTitle = "Firefighter",
                Employer = "Fire Station",
                Salary = 4000,
                WorkHoursPerDay = 12,
                WorkStartHour = 7
            },
            _ => new EmploymentInfo { Status = EmploymentStatus.Unemployed }
        };

        // Set initial housing
        state.Housing = new HousingInfo
        {
            Status = citizen.Personality.Pragmatism > 70 ? HousingStatus.Owner : HousingStatus.Renting,
            BuildingName = citizen.Personality.Extraversion > 60 ? "Skyscraper" : "Medium House",
            MonthlyRent = citizen.Personality.Extraversion > 60 ? 1500 : 1200
        };

        // Set initial finances based on job
        state.Finances = new FinancialInfo
        {
            Savings = state.Employment.Status == EmploymentStatus.BusinessOwner 
                ? _random.Next(30000, 100000)
                : _random.Next(5000, 30000),
            MonthlyIncome = state.Employment.Salary,
            MonthlyExpenses = state.Housing.MonthlyRent + 500
        };

        // Set education based on job
        state.Education = new EducationInfo
        {
            Level = citizen.Occupation switch
            {
                "Doctor" => EducationLevel.Doctorate,
                "Teacher" => EducationLevel.Masters,
                "Business Owner" => EducationLevel.Bachelors,
                _ => EducationLevel.HighSchool
            }
        };

        // Set initial needs
        state.Needs = new CitizenNeeds
        {
            Hunger = _random.Next(60, 90),
            Energy = _random.Next(70, 100),
            Social = _random.Next(50, 80),
            Happiness = _random.Next(60, 85),
            Health = _random.Next(80, 100)
        };

        state.Activity = CurrentActivity.AtHome;
        state.ActivityDescription = "Starting the day";

        citizen.UpdateOccupation();
    }

    /// <summary>
    /// Called every hour when time advances
    /// </summary>
    private async void OnTimeChangedAsync()
    {
        var currentHour = _timeService.CurrentHour;
        var currentDay = _timeService.CurrentDay;

        // Check if a new day has started
        if (currentDay != _lastProcessedDay && currentHour == 0)
        {
            await ProcessNewDayAsync(currentDay);
            _lastProcessedDay = currentDay;
        }

        // Update needs for all citizens each tick
        foreach (var citizen in _citizens)
        {
            UpdateCitizenNeeds(citizen, currentHour);
        }

        // Randomly select ONE citizen to make a decision this tick
        // This reduces AI load and creates more organic behavior
        if (_citizens.Count > 0)
        {
            var activeCitizen = _citizens[_random.Next(_citizens.Count)];
            
            // Configurable chance that the selected citizen actually makes a decision
            // (sometimes people just continue what they're doing)
            if (_random.Next(100) < _settings.CitizenDecisionChance)
            {
                try
                {
                    // Get AI decision
                    var decision = await _aiEngine.MakeHourlyDecisionAsync(
                        activeCitizen,
                        _cityState,
                        currentHour,
                        currentDay,
                        _timeService.CurrentSeason,
                        _timeService.CurrentWeather,
                        _citizens.ToList(),
                        CancellationToken.None);

                    // Apply the decision
                    ApplyDecision(activeCitizen, decision);

                    // Log the activity
                    if (!string.IsNullOrEmpty(decision.Action) && decision.Action != "Idle")
                    {
                        LogActivity(
                            activeCitizen.Name,
                            activeCitizen.Emoji,
                            $"{decision.Action}: {decision.Outcome}",
                            decision.DecisionType);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error processing citizen {Name}", activeCitizen.Name);
                }
            }
        }

        // Update city statistics
        UpdateCityStatistics();

        // Notify UI
        OnCityStateChanged?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>
    /// Process a new day - handle daily resets and mayor countdown
    /// </summary>
    private async Task ProcessNewDayAsync(int currentDay)
    {
        // Reset daily counters for citizens
        foreach (var citizen in _citizens)
        {
            citizen.State.HoursWorkedToday = 0;
            citizen.State.MealsEatenToday = 0;
            citizen.State.HasSleptToday = false;
        }

        // Decrement mayor countdown
        _mayor.DaysUntilNextDecision--;

        // Log day change
        LogActivity("System", "📅", $"Day {currentDay} begins. Mayor decision in {_mayor.DaysUntilNextDecision} days.", "System");

        // Check if mayor should make a decision
        if (_mayor.DaysUntilNextDecision <= 0)
        {
            await ProcessMayorDecisionAsync(currentDay);
            _mayor.DaysUntilNextDecision = _settings.MayorDecisionIntervalDays;  // Reset countdown
        }
    }

    /// <summary>
    /// Process mayor's policy decision
    /// </summary>
    private async Task ProcessMayorDecisionAsync(int currentDay)
    {
        try
        {
            LogActivity("Mayor", "🤖", "Mayor Sterling is reviewing city policies...", "Mayor");

            var decision = await _mayorService.MakePolicyDecisionAsync(_cityState, _mayor, CancellationToken.None);

            // Apply the policy changes
            ApplyMayorDecision(decision);

            // Update mayor state
            _mayor.LastDecision = decision.Action;
            _mayor.LastDecisionReason = decision.Reasoning;
            _mayor.LastDecisionDate = DateTime.Now;
            _mayor.ApprovalRating = Math.Clamp(_mayor.ApprovalRating + decision.ProjectedApprovalChange, 0, 100);
            
            _mayor.RecentDecisions.Add($"Day {currentDay}: {decision.Action}");
            if (_mayor.RecentDecisions.Count > 5)
                _mayor.RecentDecisions.RemoveAt(0);

            // Log the decision
            LogActivity("Mayor", "📜", $"Policy Change: {decision.Action}", "Mayor");
            LogActivity("Mayor", "💬", $"Reason: {decision.Reasoning}", "Mayor");

            // Notify UI
            OnMayorDecision?.Invoke(this, decision);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing mayor decision");
            LogActivity("Mayor", "⚠️", "Mayor decision delayed due to technical issues", "System");
        }
    }

    /// <summary>
    /// Apply mayor's policy decision to city state
    /// </summary>
    private void ApplyMayorDecision(MayorDecision decision)
    {
        foreach (var change in decision.Changes)
        {
            switch (change.Key.ToLower())
            {
                case "taxrate":
                    if (change.Value is int taxRate)
                        _cityState.Policies.TaxRate = Math.Clamp(taxRate, 10, 40);
                    break;
                case "minimumwage":
                    if (change.Value is int wage)
                        _cityState.Policies.MinimumWage = Math.Clamp(wage, 1000, 3000);
                    break;
                case "businessincentives":
                    if (change.Value is bool incentives)
                        _cityState.Policies.BusinessIncentives = incentives;
                    break;
                case "rentcontrol":
                    if (change.Value is bool rentControl)
                        _cityState.Policies.RentControl = rentControl;
                    break;
                case "unemploymentbenefits":
                    if (change.Value is bool benefits)
                        _cityState.Policies.UnemploymentBenefits = benefits;
                    break;
                case "unemploymentbenefitamount":
                    if (change.Value is int amount)
                        _cityState.Policies.UnemploymentBenefitAmount = Math.Clamp(amount, 500, 1500);
                    break;
                case "healthcaresubsidy":
                    if (change.Value is bool healthcare)
                        _cityState.Policies.HealthcareSubsidy = healthcare;
                    break;
                case "maxworkhours":
                    if (change.Value is int hours)
                        _cityState.Policies.MaxWorkHours = Math.Clamp(hours, 8, 12);
                    break;
            }
        }

        // Policy changes affect citizen happiness
        AdjustCitizenHappinessFromPolicy(decision);
    }

    /// <summary>
    /// Adjust citizen happiness based on policy changes
    /// </summary>
    private void AdjustCitizenHappinessFromPolicy(MayorDecision decision)
    {
        foreach (var citizen in _citizens)
        {
            var happinessChange = 0;

            // Tax changes affect everyone
            if (decision.Changes.ContainsKey("TaxRate"))
            {
                var newRate = (int)decision.Changes["TaxRate"];
                happinessChange += newRate < _cityState.Policies.TaxRate ? 5 : -3;
            }

            // Minimum wage affects employed citizens
            if (decision.Changes.ContainsKey("MinimumWage") && 
                citizen.State.Employment.Status == EmploymentStatus.Employed)
            {
                happinessChange += 3;
            }

            // Unemployment benefits affect unemployed
            if (decision.Changes.ContainsKey("UnemploymentBenefits") && 
                citizen.State.Employment.Status == EmploymentStatus.Unemployed)
            {
                happinessChange += (bool)decision.Changes["UnemploymentBenefits"] ? 5 : -5;
            }

            // Rent control affects renters
            if (decision.Changes.ContainsKey("RentControl") && 
                citizen.State.Housing.Status == HousingStatus.Renting)
            {
                happinessChange += (bool)decision.Changes["RentControl"] ? 4 : -2;
            }

            citizen.State.Needs.Happiness = Math.Clamp(citizen.State.Needs.Happiness + happinessChange, 0, 100);
        }
    }

    /// <summary>
    /// Update citizen needs based on time passage
    /// </summary>
    private void UpdateCitizenNeeds(Citizen citizen, int currentHour)
    {
        var needs = citizen.State.Needs;

        // Hunger decreases over time
        needs.Hunger = Math.Max(0, needs.Hunger - 3);

        // Energy depends on activity
        if (citizen.State.Activity == CurrentActivity.Sleeping)
        {
            needs.Energy = Math.Min(100, needs.Energy + 15);
        }
        else if (citizen.State.Activity == CurrentActivity.Working)
        {
            needs.Energy = Math.Max(0, needs.Energy - 5);
        }
        else
        {
            needs.Energy = Math.Max(0, needs.Energy - 2);
        }

        // Social needs change based on personality and activity
        if (citizen.State.Activity == CurrentActivity.Socializing ||
            citizen.State.Activity == CurrentActivity.OnDate)
        {
            needs.Social = Math.Min(100, needs.Social + 10);
        }
        else if (citizen.Personality.Extraversion > 60)
        {
            needs.Social = Math.Max(0, needs.Social - 3);
        }
        else
        {
            needs.Social = Math.Max(0, needs.Social - 1);
        }

        // Happiness affected by needs and life situation
        var avgNeeds = (needs.Hunger + needs.Energy + needs.Social + needs.Health) / 4;
        needs.Happiness = (needs.Happiness * 2 + avgNeeds) / 3; // Smoothed average
    }

    /// <summary>
    /// Apply a decision to the citizen's state
    /// </summary>
    private void ApplyDecision(Citizen citizen, CitizenDecision decision)
    {
        var state = citizen.State;

        // Apply based on action type
        switch (decision.Action.ToLower())
        {
            case "sleep":
            case "emergencysleep":
                state.Activity = CurrentActivity.Sleeping;
                state.ActivityDescription = "Sleeping";
                state.HasSleptToday = true;
                break;

            case "eat":
            case "emergencyeat":
                state.Activity = CurrentActivity.Eating;
                state.ActivityDescription = decision.Outcome;
                state.MealsEatenToday++;
                if (decision.Success && state.Finances.CanAfford(15))
                {
                    state.Finances.Savings -= 15;
                    state.Needs.Hunger = Math.Min(100, state.Needs.Hunger + 40);
                }
                break;

            case "work":
                state.Activity = CurrentActivity.Working;
                state.ActivityDescription = $"Working at {state.Employment.Employer}";
                state.HoursWorkedToday++;
                break;

            case "lookforjob":
                state.Activity = CurrentActivity.LookingForJob;
                state.ActivityDescription = "Job hunting";
                if (decision.Success && _cityState.Jobs.AvailableJobs.Any())
                {
                    var job = _cityState.Jobs.AvailableJobs.First();
                    state.Employment = new EmploymentInfo
                    {
                        Status = EmploymentStatus.Employed,
                        JobTitle = job.Title,
                        Employer = job.Employer,
                        Salary = job.Salary,
                        WorkHoursPerDay = job.WorkHours,
                        WorkStartHour = job.StartHour
                    };
                    state.Finances.MonthlyIncome = job.Salary;
                    _cityState.Jobs.AvailableJobs.Remove(job);
                    citizen.UpdateOccupation();
                    
                    LogActivity(citizen.Name, citizen.Emoji, 
                        $"🎉 Got hired as {job.Title} at {job.Employer}!", "Employment");
                }
                break;

            case "lookforhousing":
                state.Activity = CurrentActivity.LookingForHousing;
                state.ActivityDescription = "House hunting";
                if (decision.Success && _cityState.Housing.AvailableHousingList.Any())
                {
                    var housing = _cityState.Housing.AvailableHousingList.First();
                    state.Housing = new HousingInfo
                    {
                        Status = HousingStatus.Renting,
                        BuildingName = housing.BuildingName,
                        MonthlyRent = housing.MonthlyRent
                    };
                    state.Finances.MonthlyExpenses = housing.MonthlyRent + 500;
                    _cityState.Housing.AvailableHousingList.Remove(housing);
                    _cityState.Housing.OccupiedUnits++;
                    
                    LogActivity(citizen.Name, citizen.Emoji, 
                        $"🏠 Moved into {housing.BuildingName}!", "Housing");
                }
                break;

            case "socialize":
                state.Activity = CurrentActivity.Socializing;
                state.ActivityDescription = decision.Outcome;
                state.Needs.Social = Math.Min(100, state.Needs.Social + 20);
                break;

            case "getdrunk":
            case "drinkingalcohol":
                state.Activity = CurrentActivity.AtBar;
                state.ActivityDescription = "At the bar";
                state.Needs.Social = Math.Min(100, state.Needs.Social + 15);
                state.Needs.Happiness = Math.Min(100, state.Needs.Happiness + 10);
                state.Finances.Savings = Math.Max(0, state.Finances.Savings - 50);
                break;

            case "findpartner":
            case "dating":
                state.Activity = CurrentActivity.OnDate;
                state.ActivityDescription = "On a date";
                // Check if there's a potential partner
                var potential = _citizens.FirstOrDefault(c => 
                    c.Id != citizen.Id && 
                    c.State.Family.Status == RelationshipStatus.Single &&
                    c.State.Activity == CurrentActivity.Socializing);
                if (potential != null && decision.Success)
                {
                    state.Family.Status = RelationshipStatus.Dating;
                    state.Family.PartnerId = potential.Id;
                    state.Family.PartnerName = potential.Name;
                    
                    LogActivity(citizen.Name, citizen.Emoji, 
                        $"💕 Started dating {potential.Name}!", "Social");
                }
                break;

            case "havechild":
                if (state.Family.Status == RelationshipStatus.Married && decision.Success)
                {
                    // This would create a new child citizen in a full implementation
                    LogActivity(citizen.Name, citizen.Emoji, 
                        $"👶 Had a baby!", "Family");
                    _cityState.Statistics.Births++;
                }
                break;

            case "startbusiness":
                if (decision.Success && state.Finances.Savings >= 20000)
                {
                    state.Finances.Savings -= 20000;
                    state.Employment = new EmploymentInfo
                    {
                        Status = EmploymentStatus.BusinessOwner,
                        BusinessName = $"{citizen.Name.Split(' ')[1] ?? citizen.Name}'s Business",
                        Salary = 0, // Profit-based
                        EmployeeCount = 0
                    };
                    citizen.UpdateOccupation();
                    _cityState.Statistics.NewBusinesses++;
                    
                    LogActivity(citizen.Name, citizen.Emoji, 
                        $"🏪 Started a new business!", "Employment");
                }
                break;

            default:
                state.Activity = CurrentActivity.Idle;
                state.ActivityDescription = decision.Outcome;
                break;
        }

        // Apply personality changes if any
        foreach (var change in decision.PersonalityChanges)
        {
            var parts = change.Split(':');
            if (parts.Length == 2 && int.TryParse(parts[1], out var delta))
            {
                citizen.Personality.AdjustTrait(parts[0], delta);
            }
        }

        // Store recent decision
        state.RecentDecisions.Add($"{decision.Action}: {decision.Reasoning}");
        if (state.RecentDecisions.Count > 10)
            state.RecentDecisions.RemoveAt(0);

        // Notify UI of state change
        OnCitizenStateChanged?.Invoke(this, new CitizenStateChangedEventArgs
        {
            Citizen = citizen,
            ChangeType = decision.DecisionType
        });
    }

    /// <summary>
    /// Update city statistics
    /// </summary>
    private void UpdateCityStatistics()
    {
        _cityState.Statistics.AverageHappiness = _citizens.Average(c => c.State.Needs.Happiness);
        _cityState.Jobs.TotalEmployed = _citizens.Count(c => 
            c.State.Employment.Status == EmploymentStatus.Employed ||
            c.State.Employment.Status == EmploymentStatus.BusinessOwner);
        _cityState.Jobs.TotalUnemployed = _citizens.Count(c => 
            c.State.Employment.Status == EmploymentStatus.Unemployed);
        _cityState.Economy.UnemploymentRate = _citizens.Count > 0
            ? (double)_cityState.Jobs.TotalUnemployed / _citizens.Count * 100
            : 0;
    }

    /// <summary>
    /// Log an activity
    /// </summary>
    private void LogActivity(string citizenName, string emoji, string message, string category, params string[] args)
    {
        var formattedMessage = string.Format(message, args);
        OnActivityLogged?.Invoke(this, new ActivityLogEventArgs
        {
            Timestamp = $"Day {_timeService.CurrentDay} {_timeService.CurrentTimeString}",
            Message = formattedMessage,
            CitizenName = citizenName,
            Emoji = emoji,
            Category = category
        });
    }

    /// <summary>
    /// Reset the simulation to initial state
    /// </summary>
    public void Reset()
    {
        _lastProcessedDay = 0;
        
        // Reset mayor
        _mayor = new Mayor
        {
            Name = "Mayor Alexandra Sterling",
            Emoji = "🤖",
            Quote = "Managing Urbanium with efficiency and care.",
            ApprovalRating = _settings.InitialMayorApproval,
            DaysUntilNextDecision = _settings.MayorDecisionIntervalDays,
            PrimaryFocus = "Economic Growth",
            SecondaryFocus = "Citizen Welfare"
        };
        
        foreach (var citizen in _citizens)
        {
            InitializeCitizenState(citizen);
        }
        InitializeCityState();
        
        LogActivity("System", "🔄", "Simulation reset to initial state", "System");
    }

    /// <summary>
    /// Process monthly finances for all citizens
    /// </summary>
    public void ProcessMonthlyFinances()
    {
        foreach (var citizen in _citizens)
        {
            var finances = citizen.State.Finances;
            
            // Apply income
            finances.Savings += finances.MonthlyIncome;
            
            // Apply expenses
            finances.Savings -= finances.MonthlyExpenses;
            
            // Apply taxes
            var taxes = (int)(finances.MonthlyIncome * _cityState.Policies.TaxRate / 100);
            finances.Savings -= taxes;

            // Unemployment benefits
            if (citizen.State.Employment.Status == EmploymentStatus.Unemployed &&
                _cityState.Policies.UnemploymentBenefits)
            {
                finances.Savings += _cityState.Policies.UnemploymentBenefitAmount;
            }

            // Check if in debt
            if (finances.Savings < 0)
            {
                finances.Debt += Math.Abs(finances.Savings);
                finances.Savings = 0;
                LogActivity(citizen.Name, citizen.Emoji, 
                    $"💸 Went into debt (${finances.Debt})", "Financial");
            }
        }
    }
}
