using MudBlazor;

namespace Urbanium.Models;

public enum BuildingType
{
    Commercial,
    Residential
}

public class Building
{
    public string Name { get; set; } = "";
    public string Icon { get; set; } = "";
    public int Occupancy { get; set; }
    public Color StatusColor { get; set; }
    public BuildingType Type { get; set; } = BuildingType.Commercial;
    public int Capacity { get; set; } = 0;
    public int CurrentResidents { get; set; } = 0;
}
