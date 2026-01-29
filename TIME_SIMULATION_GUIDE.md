# Time Simulation System - Urbanium

## Overview
The time simulation system in Urbanium allows the city to progress through days, hours, seasons, and weather patterns. Time advances automatically when started, with a configurable rate where real time maps to Urbanium time.

## Time Scale
- **10 real seconds = 1 Urbanium hour**
- 24 hours = 1 day
- 90 days = 1 season (360 days per year)

## Features

### Time Controls
Located at the top of the homepage, the time control widget provides three buttons:

1. **Start Button** (Green)
   - Starts the city simulation timer
   - Disabled when time is already running
   - Time advances every 10 seconds

2. **Pause Button** (Yellow)
   - Pauses the simulation without resetting
   - City state is preserved
   - Can be resumed with Start button
   - Only enabled when time is running

3. **Stop & Reset Button** (Red)
   - Stops the timer completely
   - Resets the city to initial state:
     - Day 1
     - 8:00 AM
     - Spring season
     - Sunny weather
     - All citizens reset to initial state
     - All buildings reset to initial capacities
     - Mayor reset to initial approval rating
   - Enabled when time is running or paused

### Time Display
The widget shows real-time information:
- **Current Day**: Displays day number (e.g., "Day 1", "Day 42")
- **Current Time**: Shows hour in 24-hour format (e.g., "08:00", "14:00")
- **Current Weather**: Shows weather condition with icon
- **Current Season**: Shows current season with icon

## Seasonal Cycle

### Duration
- Each season lasts 90 days
- Complete year = 360 days (4 seasons)
- Seasons cycle continuously

### Season Order
1. **Spring** (Days 1-90) 🌸
2. **Summer** (Days 91-180) 🏖️
3. **Autumn** (Days 181-270) 🍂
4. **Winter** (Days 271-360) ❄️

## Weather System

### Weather Patterns
Weather changes every 5 days within each season, following realistic patterns:

**Spring Weather Cycle:**
1. Days 1-5: Sunny ☀️
2. Days 6-10: Rainy 💧
3. Days 11-15: Cloudy ☁️
4. Days 16-20: Sunny ☀️
5. (Repeats)

**Summer Weather Cycle:**
1. Days 1-5: Sunny ☀️
2. Days 6-10: Sunny ☀️
3. Days 11-15: Cloudy ☁️
4. Days 16-20: Stormy ⛈️
5. (Repeats)

**Autumn Weather Cycle:**
1. Days 1-5: Cloudy ☁️
2. Days 6-10: Rainy 💧
3. Days 11-15: Sunny ☀️
4. Days 16-20: Cloudy ☁️
5. (Repeats)

**Winter Weather Cycle:**
1. Days 1-5: Snowy ❄️
2. Days 6-10: Cloudy ☁️
3. Days 11-15: Snowy ❄️
4. Days 16-20: Sunny ☀️
5. (Repeats)

## Implementation Details

### CityTimeService
Located in `/Services/CityTimeService.cs`, this singleton service manages time progression:

**Properties:**
- `CurrentDay`: Current day number
- `CurrentHour`: Current hour (0-23)
- `CurrentTimeString`: Formatted time string (e.g., "08:00")
- `CurrentSeason`: Current season enum value
- `CurrentWeather`: Current weather enum value

**Methods:**
- `AdvanceHour()`: Advances time by 1 hour, updates day/season/weather as needed
- `Reset()`: Resets to initial state (Day 1, 8:00, Spring, Sunny)
- `OnTimeChanged`: Event raised when time updates (for UI refresh)

### Home Component Integration
The Home.razor component:
- Injects `CityTimeService` 
- Creates a `System.Threading.Timer` that fires every 10 seconds
- Calls `AdvanceHour()` on each timer tick
- Subscribes to `OnTimeChanged` event to refresh UI
- Properly disposes timer when component is destroyed

### Reset Functionality
When Stop & Reset is pressed:
1. Timer is stopped and disposed
2. `CityTimeService.Reset()` is called
3. `ResetCityState()` reinitializes:
   - 6 citizens with their original personalities
   - 14 buildings (6 residential, 8 commercial)
   - Mayor with 87% approval rating
4. UI refreshes to show initial state

## Usage Example

1. **Start Working Day**
   - Press "Start" button
   - Watch as time advances from 08:00 → 09:00 → 10:00 (every 10 seconds)
   - Observe day counter increment at midnight (00:00)

2. **Observe Seasonal Changes**
   - Let simulation run to day 91
   - Season automatically changes from Spring to Summer
   - Weather pattern updates to summer cycle

3. **Pause for Analysis**
   - Press "Pause" to stop time progression
   - Analyze current city state
   - Press "Start" to resume

4. **Complete Reset**
   - Press "Stop & Reset"
   - City returns to Day 1, 8:00 AM, Spring, Sunny
   - All entities reset to original state

## Future Enhancements

Potential additions to the time system:
- Citizen schedules (wake up, work, sleep times)
- Building operations affected by time of day
- Special events tied to specific days/seasons
- Weather effects on citizen behavior
- Holiday system
- Time speed controls (1x, 2x, 5x)
- Save/load simulation state

## Technical Notes

- Timer runs on a background thread, uses `InvokeAsync` for UI updates
- Event-driven architecture ensures UI stays synchronized
- IDisposable pattern properly cleans up timer resources
- Singleton service ensures consistent time across all components
