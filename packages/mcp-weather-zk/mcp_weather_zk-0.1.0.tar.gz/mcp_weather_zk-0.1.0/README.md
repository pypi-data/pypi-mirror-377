# MCP Weather Server

A simple MCP server that provides hourly weather forecasts using the AccuWeather API.

## Setup

1. Install dependencies using `uv`:
```bash
uv venv
uv sync
```

2. Create a `.env` file with your AccuWeather API key:
```
ACCUWEATHER_API_KEY=your_api_key_here
```

You can get an API key by registering at [AccuWeather API](https://developer.accuweather.com/).

## Running the Server

```json
{
    "mcpServers": {
        "weather": {
            "command": "uvx",
            "args": ["--from", "git+https://github.com/CreateModel/mcp-weather.git", "mcp-weather"],
            "env": {
                "ACCUWEATHER_API_KEY": "zpka_787d7e4f665b43b6b8b7b7b67ab2eb45_812b9cc3"
            }
        }
    }
}
```

## API Usage

### Get Hourly Weather Forecast

Response:
```json
{
    "location": "Jakarta",
    "location_key": "208971",
    "country": "Indonesia",
    "current_conditions": {
        "temperature": {
            "value": 32.2,
            "unit": "C"
        },
        "weather_text": "Partly sunny",
        "relative_humidity": 75,
        "precipitation": false,
        "observation_time": "2024-01-01T12:00:00+07:00"
    },
    "hourly_forecast": [
        {
            "relative_time": "+1 hour",
            "temperature": {
                "value": 32.2,
                "unit": "C"
            },
            "weather_text": "Partly sunny",
            "precipitation_probability": 40,
            "precipitation_type": "Rain",
            "precipitation_intensity": "Light"
        }
    ]
}
```

The API provides:
- Current weather conditions including temperature, weather description, humidity, and precipitation status
- 12-hour forecast with hourly data including:
  - Relative time from current time
  - Temperature in Celsius
  - Weather description
  - Precipitation probability, type, and intensity