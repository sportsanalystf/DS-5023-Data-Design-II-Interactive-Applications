# api_integrations.py - weather data (Open-Meteo) and team info (TheSportsDB)
import streamlit as st
import requests
import time
from datetime import datetime, date

# API endpoints
OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE  = "https://archive-api.open-meteo.com/v1/archive"
# UVA Klöckner Stadium coordinates (Charlottesville, VA)
UVA_LAT = 38.0336
UVA_LON = -78.5140

# Game location coordinates for away games
VENUE_COORDS = {
    "Charlottesville":  (38.0336, -78.5140),
    "Harrisonburg":     (38.4496, -78.8689),   # JMU
    "Louisville":       (38.2070, -85.7554),
    "Pittsburgh":       (40.4437, -79.9625),
    "Stanford":         (37.4346, -122.1609),
    "South Bend":       (41.6987, -86.2340),    # Notre Dame
    "College Park":     (38.9897, -76.9378),    # Maryland
    "Clemson":          (34.6834, -82.8374),
    "Princeton":        (40.3460, -74.6551),
    "Tallahassee":      (30.4383, -84.2807),    # FSU
    "Durham":           (35.9940, -78.9003),    # Duke
    "Syracuse":         (43.0481, -76.1474),
    "Boston":           (42.3355, -71.1685),    # BC
}


class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def _handle_response(resp, api_name="API"):
    """Check the HTTP response and raise errors if needed."""
    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 401:
        raise APIError(f"{api_name}: Unauthorized — check your API key in st.secrets.", 401)
    elif resp.status_code == 404:
        raise APIError(f"{api_name}: Resource not found (404). The endpoint may have changed.", 404)
    elif resp.status_code == 429:
        raise APIError(f"{api_name}: Rate limit exceeded (429). Please wait a moment and try again.", 429)
    elif resp.status_code >= 500:
        raise APIError(f"{api_name}: Server error ({resp.status_code}). The service may be temporarily down.", resp.status_code)
    else:
        raise APIError(f"{api_name}: Unexpected HTTP {resp.status_code}.", resp.status_code)


# --- Weather API (Open-Meteo) ---

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_game_weather(location_name: str, game_date: str = None):
    """Fetch weather for a game location. Returns temp, wind, humidity, conditions."""
    # input validation
    if not location_name or not isinstance(location_name, str):
        return {"error": "Invalid location name.", "data": None}

    # resolve coordinates
    coords = VENUE_COORDS.get(location_name)
    if not coords:
        # try fuzzy match
        for key, val in VENUE_COORDS.items():
            if key.lower() in location_name.lower() or location_name.lower() in key.lower():
                coords = val
                break
    if not coords:
        # default to UVA
        coords = (UVA_LAT, UVA_LON)

    lat, lon = coords

    # figure out if this is a past game or upcoming
    iso_date = None
    is_historical = False
    if game_date:
        try:
            # try M/D/YYYY format first (how our data stores dates)
            parsed = datetime.strptime(game_date.strip(), "%m/%d/%Y")
            iso_date = parsed.strftime("%Y-%m-%d")
        except ValueError:
            try:
                parsed = datetime.strptime(game_date.strip(), "%Y-%m-%d")
                iso_date = game_date.strip()
            except ValueError:
                iso_date = None
        if iso_date:
            is_historical = datetime.strptime(iso_date, "%Y-%m-%d").date() < date.today()

    if is_historical and iso_date:
        # use the archive endpoint for past dates
        url = OPEN_METEO_ARCHIVE
        params = {
            "latitude": lat, "longitude": lon,
            "start_date": iso_date, "end_date": iso_date,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "America/New_York",
        }
    else:
        # current / forecast endpoint
        url = OPEN_METEO_FORECAST
        params = {
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "America/New_York",
        }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = _handle_response(resp, "Open-Meteo")
    except requests.exceptions.Timeout:
        return {"error": "Weather API timed out. Please try again.", "data": None}
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to weather service. Check your internet connection.", "data": None}
    except APIError as e:
        return {"error": e.message, "data": None}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "data": None}

    # parse response
    if not data:
        return {"error": "Empty response from weather API.", "data": None}

    # weather code lookup
    WMO_CODES = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }

    try:
        if "current" in data:
            cur = data["current"]
            return {
                "error": None,
                "data": {
                    "temp_f": cur.get("temperature_2m"),
                    "humidity": cur.get("relative_humidity_2m"),
                    "wind_mph": cur.get("wind_speed_10m"),
                    "condition": WMO_CODES.get(cur.get("weather_code", -1), "Unknown"),
                    "location": location_name,
                    "type": "current",
                }
            }
        elif "hourly" in data:
            # historical — take midday (12:00) values
            hourly = data["hourly"]
            idx = 12 if len(hourly.get("temperature_2m", [])) > 12 else 0
            return {
                "error": None,
                "data": {
                    "temp_f": hourly["temperature_2m"][idx] if hourly.get("temperature_2m") else None,
                    "humidity": hourly["relative_humidity_2m"][idx] if hourly.get("relative_humidity_2m") else None,
                    "wind_mph": hourly["wind_speed_10m"][idx] if hourly.get("wind_speed_10m") else None,
                    "condition": WMO_CODES.get(
                        hourly["weather_code"][idx] if hourly.get("weather_code") else -1, "Unknown"),
                    "location": location_name,
                    "date": game_date,
                    "type": "historical",
                }
            }
        else:
            return {"error": "Unexpected weather API response format.", "data": None}
    except (KeyError, IndexError, TypeError) as e:
        return {"error": f"Error parsing weather data: {e}", "data": None}


# --- Team Info API (TheSportsDB) ---

SPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_team_info(team_name: str = "Virginia Cavaliers"):
    """Look up basic team info from TheSportsDB."""
    # load API key, default to free tier
    try:
        api_key = st.secrets.get("SPORTSDB_API_KEY", "3")  # "3" is the free-tier test key
    except Exception:
        api_key = "3"

    if not team_name or not isinstance(team_name, str):
        return {"error": "Invalid team name.", "data": None}

    url = f"{SPORTSDB_BASE}/{api_key}/searchteams.php"
    params = {"t": team_name}

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = _handle_response(resp, "TheSportsDB")
    except requests.exceptions.Timeout:
        return {"error": "Sports API timed out. Please try again.", "data": None}
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to sports data service.", "data": None}
    except APIError as e:
        return {"error": e.message, "data": None}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "data": None}

    if not data or not data.get("teams"):
        return {"error": f"No results found for '{team_name}'.", "data": None}

    team = data["teams"][0]
    return {
        "error": None,
        "data": {
            "name": team.get("strTeam", ""),
            "sport": team.get("strSport", ""),
            "league": team.get("strLeague", ""),
            "stadium": team.get("strStadium", ""),
            "description": team.get("strDescriptionEN", ""),
            "badge_url": team.get("strBadge", ""),
            "banner_url": team.get("strBanner", ""),
            "year_formed": team.get("intFormedYear", ""),
            "country": team.get("strCountry", ""),
        }
    }


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_past_events(team_id: str = None, team_name: str = "Virginia"):
    """Fetch recent results for a team."""
    try:
        api_key = st.secrets.get("SPORTSDB_API_KEY", "3")
    except Exception:
        api_key = "3"

    if not team_name:
        return {"error": "Team name is required.", "data": None}

    # search for team ID first if not provided
    if not team_id:
        team_info = fetch_team_info(team_name)
        if team_info.get("error"):
            return team_info

    url = f"{SPORTSDB_BASE}/{api_key}/searchteams.php"
    params = {"t": team_name}

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = _handle_response(resp, "TheSportsDB")
    except requests.exceptions.Timeout:
        return {"error": "Sports API timed out.", "data": None}
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to sports data service.", "data": None}
    except APIError as e:
        return {"error": e.message, "data": None}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "data": None}

    if not data:
        return {"error": "Empty response from sports API.", "data": None}

    return {"error": None, "data": data}


# --- UI rendering ---

def render_weather_card(weather_data: dict):
    """Show the weather card on the page."""
    if not weather_data or weather_data.get("error"):
        st.warning(weather_data.get("error", "No weather data available."))
        return

    d = weather_data["data"]
    if not d:
        st.warning("No weather data returned.")
        return

    # weather emoji mapping
    condition = d.get("condition", "Unknown")
    emoji_map = {
        "Clear sky": "☀️", "Mainly clear": "🌤️", "Partly cloudy": "⛅",
        "Overcast": "☁️", "Fog": "🌫️", "Light drizzle": "🌦️",
        "Slight rain": "🌧️", "Moderate rain": "🌧️", "Heavy rain": "⛈️",
        "Thunderstorm": "⛈️", "Slight snow": "🌨️",
    }
    emoji = emoji_map.get(condition, "🌡️")

    temp = d.get("temp_f")
    humidity = d.get("humidity")
    wind = d.get("wind_mph")
    loc = d.get("location", "")
    data_type = d.get("type", "current")
    date_str = d.get("date", "")

    label = f"Game Day Weather — {loc}" if data_type == "historical" else f"Current Weather — {loc}"
    if date_str:
        label += f" ({date_str})"

    st.write(f"**{label}**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{temp:.0f}°F" if temp is not None else "N/A")
    col2.metric("Wind", f"{wind:.0f} mph" if wind is not None else "N/A")
    col3.metric("Humidity", f"{humidity:.0f}%" if humidity is not None else "N/A")
    st.caption(f"{emoji} {condition}")


def render_team_info_card(team_data: dict):
    """Show the team info card on the page."""
    if not team_data or team_data.get("error"):
        st.info(team_data.get("error", "No team data available."))
        return

    d = team_data["data"]
    if not d:
        st.info("No team info returned.")
        return

    desc = d.get("description", "")
    # truncate long descriptions
    if desc and len(desc) > 300:
        desc = desc[:300] + "…"

    st.write(f"**Team Profile — {d.get('name', '')}**")
    col1, col2 = st.columns(2)
    col1.write(f"**Sport:** {d.get('sport', 'N/A')}")
    col1.write(f"**Stadium:** {d.get('stadium', 'N/A')}")
    col2.write(f"**League:** {d.get('league', 'N/A')}")
    col2.write(f"**Founded:** {d.get('year_formed', 'N/A')}")
    if desc:
        st.caption(desc)
