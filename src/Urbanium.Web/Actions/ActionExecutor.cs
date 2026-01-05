using Urbanium.Web.Engine;

namespace Urbanium.Web.Actions;

/// <summary>
/// Validates and executes action proposals against the world state.
/// The world enforces legality, cost, and consequences.
/// </summary>
public class ActionExecutor
{
    /// <summary>
    /// Validate and execute an action proposal.
    /// </summary>
    public ActionResult Execute(ActionProposal proposal, WorldState worldState, Agents.Citizen citizen)
    {
        return proposal.Type switch
        {
            ActionType.WorkShift => ExecuteWorkShift((WorkShiftAction)proposal, worldState, citizen),
            ActionType.Rest => ExecuteRest((RestAction)proposal, worldState, citizen),
            ActionType.Eat => ExecuteEat((EatAction)proposal, worldState, citizen),
            ActionType.Commute => ExecuteCommute((CommuteAction)proposal, worldState, citizen),
            ActionType.Socialize => ExecuteSocialize((SocializeAction)proposal, worldState, citizen),
            ActionType.JobSearch => ExecuteJobSearch((JobSearchAction)proposal, worldState, citizen),
            ActionType.HousingChange => ExecuteHousingChange((HousingChangeAction)proposal, worldState, citizen),
            _ => new ActionResult { Success = false, FailureReason = "Unknown action type" }
        };
    }
    
    private ActionResult ExecuteWorkShift(WorkShiftAction action, WorldState worldState, Agents.Citizen citizen)
    {
        // Validate: citizen must be employed
        if (citizen.EmployerId == null)
        {
            return new ActionResult { Success = false, FailureReason = "Not employed" };
        }
        
        // Validate: must be working hours
        if (!worldState.IsWorkingHours)
        {
            return new ActionResult { Success = false, FailureReason = "Not working hours" };
        }
        
        // Execute: earn money, reduce energy
        var wage = citizen.Resources.MonthlyIncome / 160 * action.HoursWorked; // hourly rate
        citizen.Resources.Cash += wage;
        citizen.Needs.Energy = Math.Min(1.0, citizen.Needs.Energy + 0.1);
        
        return new ActionResult 
        { 
            Success = true,
            Effects = new Dictionary<string, object>
            {
                { "WageEarned", wage },
                { "HoursWorked", action.HoursWorked }
            }
        };
    }
    
    private ActionResult ExecuteRest(RestAction action, WorldState worldState, Agents.Citizen citizen)
    {
        // Rest always succeeds if citizen has shelter
        if (citizen.HouseholdId == null)
        {
            citizen.Needs.Energy = Math.Max(0, citizen.Needs.Energy - 0.2);
        }
        else
        {
            citizen.Needs.Energy = Math.Max(0, citizen.Needs.Energy - 0.5);
        }
        
        return new ActionResult 
        { 
            Success = true,
            Effects = new Dictionary<string, object>
            {
                { "EnergyRecovered", 0.5 },
                { "HoursRested", action.HoursRested }
            }
        };
    }
    
    private ActionResult ExecuteEat(EatAction action, WorldState worldState, Agents.Citizen citizen)
    {
        var foodCost = action.Cost > 0 ? action.Cost : 10m * (decimal)worldState.GoodsMarket.FoodPriceIndex;
        
        if (citizen.Resources.Cash < foodCost)
        {
            return new ActionResult { Success = false, FailureReason = "Insufficient funds" };
        }
        
        citizen.Resources.Cash -= foodCost;
        citizen.Needs.Hunger = Math.Max(0, citizen.Needs.Hunger - 0.4);
        
        return new ActionResult 
        { 
            Success = true,
            Effects = new Dictionary<string, object>
            {
                { "FoodCost", foodCost },
                { "HungerReduced", 0.4 }
            }
        };
    }
    
    private ActionResult ExecuteCommute(CommuteAction action, WorldState worldState, Agents.Citizen citizen)
    {
        var connection = worldState.Geography.Connections
            .FirstOrDefault(c => c.FromDistrictId == action.FromDistrictId && 
                                 c.ToDistrictId == action.ToDistrictId);
        
        if (connection == null)
        {
            return new ActionResult { Success = false, FailureReason = "No route available" };
        }
        
        citizen.CurrentDistrictId = action.ToDistrictId;
        citizen.Needs.Energy = Math.Min(1.0, citizen.Needs.Energy + 0.05);
        
        return new ActionResult 
        { 
            Success = true,
            Effects = new Dictionary<string, object>
            {
                { "TravelTime", connection.TravelTime },
                { "NewLocation", action.ToDistrictId }
            }
        };
    }
    
    private ActionResult ExecuteSocialize(SocializeAction action, WorldState worldState, Agents.Citizen citizen)
    {
        citizen.Needs.Social = Math.Max(0, citizen.Needs.Social - 0.3);
        citizen.Needs.Energy = Math.Min(1.0, citizen.Needs.Energy + 0.1);
        
        // Strengthen social tie if target specified
        if (action.TargetCitizenId.HasValue)
        {
            var tie = citizen.SocialTies.FirstOrDefault(t => t.TargetCitizenId == action.TargetCitizenId);
            if (tie != null)
            {
                tie.Strength = Math.Min(1.0, tie.Strength + 0.1);
                tie.InteractionCount++;
            }
        }
        
        return new ActionResult 
        { 
            Success = true,
            Effects = new Dictionary<string, object>
            {
                { "SocialNeedReduced", 0.3 },
                { "Duration", action.Duration }
            }
        };
    }
    
    private ActionResult ExecuteJobSearch(JobSearchAction action, WorldState worldState, Agents.Citizen citizen)
    {
        var matchingJobs = worldState.LaborMarket.OpenPositions
            .Where(j => j.Wage >= action.MinimumWage)
            .Where(j => j.RequiredSkills.All(s => citizen.Skills.Any(cs => cs.Name == s && cs.Level >= 0.5)))
            .ToList();
        
        if (matchingJobs.Count == 0)
        {
            return new ActionResult { Success = false, FailureReason = "No matching jobs found" };
        }
        
        // Simplified: take first matching job
        var job = matchingJobs.First();
        citizen.EmployerId = job.EmployerId;
        citizen.Resources.MonthlyIncome = job.Wage;
        citizen.State = Agents.CitizenState.Employed;
        
        // Remove job from market
        worldState.LaborMarket.OpenPositions.Remove(job);
        
        return new ActionResult 
        { 
            Success = true,
            Effects = new Dictionary<string, object>
            {
                { "NewEmployer", job.EmployerId },
                { "Wage", job.Wage }
            }
        };
    }
    
    private ActionResult ExecuteHousingChange(HousingChangeAction action, WorldState worldState, Agents.Citizen citizen)
    {
        var unit = worldState.HousingMarket.AvailableUnits
            .FirstOrDefault(u => u.Id == action.TargetHousingUnitId && !u.IsOccupied);
        
        if (unit == null)
        {
            return new ActionResult { Success = false, FailureReason = "Housing unit not available" };
        }
        
        // Check affordability (rent should be < 30% of income)
        if (unit.Rent > citizen.Resources.MonthlyIncome * 0.4m)
        {
            return new ActionResult { Success = false, FailureReason = "Cannot afford rent" };
        }
        
        unit.IsOccupied = true;
        citizen.CurrentDistrictId = unit.DistrictId;
        citizen.Resources.MonthlyExpenses = unit.Rent;
        
        return new ActionResult 
        { 
            Success = true,
            Effects = new Dictionary<string, object>
            {
                { "NewHousing", unit.Id },
                { "MonthlyRent", unit.Rent }
            }
        };
    }
}
