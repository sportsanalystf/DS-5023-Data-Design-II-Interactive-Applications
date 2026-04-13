# LaxIQ — UVA Women's Lacrosse Post-Game Analytics Dashboard

**Course:** DS 5023 — Data Design II: Interactive Applications  
**Author:** Faizan Khan (xdy6sg@virginia.edu)  
**University of Virginia, School of Data Science**

---

## Overview

LaxIQ is an interactive Streamlit dashboard that provides advanced post-game analytics for the UVA Women's Lacrosse team. It transforms raw box-score data into actionable insights through dynamic visualizations, player intelligence metrics, and real-time API integrations.

## Features

### Game Analysis
- **Game-level breakdowns** — score progression, shot maps, quarter-by-quarter analysis
- **Player & team stats** — filterable tables with Player Spotlight (dependent dropdown: Position → Player)
- **Game comparison** — side-by-side metric comparison across any two games
- **Play-by-play timeline** — event sequencing and momentum tracking
- **Win Probability model** — logistic WP curve with key moment annotations
- **Weather integration** — Open-Meteo API for game-day conditions (forecast + historical archive)
- **Opponent info** — TheSportsDB API with sport-level filtering

### Player Intelligence
- **Team overview** — tier rankings, usage vs efficiency scatter, cumulative scoring
- **Player comparison** — head-to-head radar charts with duplicate selection warning
- **Draw control analysis** — UVA-perspective draw outcomes and possession impact
- **Goaltending analytics** — save rate trends, shot log, and performance grading
- **Coach View / Analyst View** — dynamic UI toggle to streamline or expand the dashboard

### Interactivity
- Widget keys with `st.session_state` bridging across all interactive elements
- `on_click` callbacks (reset filters with toast notification)
- `on_change` callbacks (duplicate player detection)
- Input validation for empty filters, over-filtering, and duplicate selections
- Progress bars, spinners, and contextual error/warning/info messages

## Tech Stack

- **Frontend:** Streamlit with custom CSS (UVA brand colors: `#232D4B`, `#E57200`)
- **Visualization:** Plotly with dark-themed layouts
- **Data Processing:** Pandas, NumPy
- **APIs:** Open-Meteo (weather), TheSportsDB (opponent info)
- **Data Source:** Excel box scores via openpyxl

## Project Structure

```
laxiq/
├── Home.py                  # Landing page with schedule and navigation
├── analytics.py             # Advanced metrics computation engine
├── api_integrations.py      # Open-Meteo + TheSportsDB with error handling
├── style.py                 # UVA-branded CSS and Plotly layout config
├── sidebar.py               # Sidebar navigation and branding
├── pages/
│   ├── 1_Game_Analysis.py   # Game-level dashboard
│   └── 2_Player_Intelligence.py  # Player analytics dashboard
├── tabs/
│   ├── game_analysis/       # Game Analysis sub-tabs
│   │   ├── player_team_stats.py
│   │   ├── game_comparison.py
│   │   ├── play_by_play.py
│   │   └── win_probability.py
│   └── player_intelligence/ # Player Intelligence sub-tabs
│       ├── team_overview.py
│       ├── player_comparison.py
│       ├── draw_control.py
│       └── goal_tending.py
├── assets/                  # Logo and static assets
├── data/                    # Excel box-score files
└── requirements.txt         # Python dependencies
```

## Setup

```bash
# Clone the repository
git clone https://github.com/sportsanalystf/DS-5023-Data-Design-II-Interactive-Applications.git
cd DS-5023-Data-Design-II-Interactive-Applications/laxiq

# Install dependencies
pip install -r requirements.txt

# Create secrets file for TheSportsDB API
mkdir -p .streamlit
echo 'SPORTSDB_API_KEY = "3"' > .streamlit/secrets.toml

# Run the dashboard
streamlit run Home.py
```

## API Configuration

| API | Purpose | Auth |
|-----|---------|------|
| Open-Meteo | Game-day weather (forecast + archive) | No key required |
| TheSportsDB | Opponent team info and logos | Free tier (key = `3`) |

Both APIs include centralized error handling for 401, 404, 429, 500+ status codes, timeouts, and connection errors, with `@st.cache_data` caching (30-minute TTL).

## License

This project was developed as part of the DS 5023 coursework at the University of Virginia.
