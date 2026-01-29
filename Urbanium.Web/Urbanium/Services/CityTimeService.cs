namespace Urbanium.Services;

public enum Season
{
    Spring,
    Summer,
    Autumn,
    Winter
}

public enum Weather
{
    Sunny,
    Cloudy,
    Rainy,
    Stormy,
    Snowy
}

public class CityTimeService
{
    private int _currentDay = 1;
    private int _currentHour = 8;
    private Season _currentSeason = Season.Spring;
    private Weather _currentWeather = Weather.Sunny;
    
    public int CurrentDay => _currentDay;
    public int CurrentHour => _currentHour;
    public Season CurrentSeason => _currentSeason;
    public Weather CurrentWeather => _currentWeather;
    
    public string CurrentTimeString => $"{_currentHour:D2}:00";
    
    public event Action? OnTimeChanged;
    
    /// <summary>
    /// Advances time by 1 hour (called every 10 seconds real time)
    /// </summary>
    public void AdvanceHour()
    {
        _currentHour++;
        
        if (_currentHour >= 24)
        {
            _currentHour = 0;
            _currentDay++;
            UpdateSeasonAndWeather();
        }
        
        OnTimeChanged?.Invoke();
    }
    
    /// <summary>
    /// Updates season and weather based on current day
    /// Seasons change every 90 days
    /// </summary>
    private void UpdateSeasonAndWeather()
    {
        // Calculate season (90 days per season)
        var seasonCycle = (_currentDay - 1) % 360; // 4 seasons * 90 days = 360
        _currentSeason = seasonCycle switch
        {
            < 90 => Season.Spring,
            < 180 => Season.Summer,
            < 270 => Season.Autumn,
            _ => Season.Winter
        };
        
        // Update weather based on season and some variety
        UpdateWeatherForSeason();
    }
    
    private void UpdateWeatherForSeason()
    {
        // Add variety - weather changes every few days
        var dayInSeason = ((_currentDay - 1) % 90);
        var weatherCycle = dayInSeason % 5; // 5-day weather pattern
        
        _currentWeather = _currentSeason switch
        {
            Season.Spring => weatherCycle switch
            {
                0 or 1 => Weather.Sunny,
                2 => Weather.Cloudy,
                3 or 4 => Weather.Rainy,
                _ => Weather.Sunny
            },
            Season.Summer => weatherCycle switch
            {
                0 or 1 or 2 => Weather.Sunny,
                3 => Weather.Cloudy,
                4 => Weather.Stormy,
                _ => Weather.Sunny
            },
            Season.Autumn => weatherCycle switch
            {
                0 => Weather.Sunny,
                1 or 2 => Weather.Cloudy,
                3 or 4 => Weather.Rainy,
                _ => Weather.Cloudy
            },
            Season.Winter => weatherCycle switch
            {
                0 or 1 => Weather.Cloudy,
                2 or 3 => Weather.Snowy,
                4 => Weather.Sunny,
                _ => Weather.Snowy
            },
            _ => Weather.Sunny
        };
    }
    
    /// <summary>
    /// Resets the city to initial state
    /// </summary>
    public void Reset()
    {
        _currentDay = 1;
        _currentHour = 8;
        _currentSeason = Season.Spring;
        _currentWeather = Weather.Sunny;
        OnTimeChanged?.Invoke();
    }
}
