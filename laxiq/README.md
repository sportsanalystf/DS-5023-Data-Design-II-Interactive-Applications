# ⚔️ LaxIQ — Cavaliers Lacrosse Analytics

**Post-game analysis dashboard for UVA Women's Lacrosse (2025-26 Season)**

LaxIQ is an advanced analytics platform built with Streamlit that transforms raw box-score data from 13 regular-season games into interactive visualizations, win probability models, player scouting reports, and game-level performance grades. Designed for coaching staff and analysts at the University of Virginia.

---

## Features

### Page 1: Season Overview
- **KPI Dashboard** — Overall record, PCT, ACC record, streak, home/away splits, GF-GA
- **Advanced Team Metrics** — Offensive/defensive efficiency, Lax-ELO, shooting pct, turnover rate, time-of-possession, and strength-of-record with national percentile rankings
- **Team Rankings Table** — Offense, Defense, and Possession Game stats with national context
- **Interactive Schedule** — Full season schedule with colored date badges, results, and one-click navigation to any game's detailed analysis

### Page 2: Game Analysis
- **Win Probability & WPA** — Hybrid logistic win probability model combining score differential with play-by-play momentum (draw controls, turnovers, saves, shots, clears). Event markers color-coded by type with interactive filters
- **Event Impact Bar Chart** — Average WP shift per event type for UVA vs opponent
- **Game Grades** — Letter grades (A+ through F) for Offense, Defense, Transition, Draw Unit, Goalkeeping, and Discipline calibrated to D1 women's lacrosse norms
- **Players & Team Stats** — Player influence rankings, stat tables, butterfly comparison charts
- **Key Moments & Film Tags** — Highest-impact positive/negative swings with organized film review tags
- **Game Comparison** — Side-by-side comparison with delta indicators across any two games

### Page 3: Player Intelligence
- **Team Overview** — Sortable roster with season totals, per-game trends, and tier classifications
- **Player Cards** — Individual scouting reports with headshots, radar charts, and game-by-game breakdowns
- **Player Comparison** — Head-to-head comparison tool for any two players
- **Draw Control Center** — Draw control analytics with JMU scouting video clips
- **Goal Tending** — Goalkeeper analysis with save percentages and shot-facing metrics

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.56+ (multipage app) |
| Visualization | Plotly (interactive charts, radar plots) |
| Data | pandas, numpy, openpyxl |
| Styling | Custom CSS with UVA brand colors (Blue #232D4B, Orange #E57200) |
| Fonts | Bebas Neue (headers), DM Sans (body) |

---

## Project Structure

```
laxiq/
├── Home.py                         # Page 1: Season Overview
├── analytics.py                    # Core analytics engine (WP model, grades, aggregation)
├── style.py                        # UVA design system (colors, CSS, component helpers)
├── pages/
│   ├── 1_Game_Analysis.py          # Page 2: Game-level analysis (4 tabs)
│   └── 2_Player_Intelligence.py    # Page 3: Player scouting (5 tabs)
├── data/
│   ├── Clemson_vs_Virginia_20260314.xlsx
│   ├── Navy_vs_Virginia_20260206.xlsx
│   └── ... (13 game files)
├── requirements.txt
└── README.md
```

---

## Data Pipeline

Each game is stored as a multi-sheet Excel workbook with standardized sheets:

| Sheet | Contents |
|-------|----------|
| `Game_Info` | Teams, scores, date, location, result |
| `Score_By_Quarter` | Quarter-by-quarter scoring breakdown |
| `Team_Stats_QoQ` | Team-level stats (shots, saves, GBs, DCs, clears, TOs) per quarter |
| `Scoring_Summary` | Every goal with scorer, assist, period, time, type (man-up, FPG) |
| `Penalty_Summary` | Penalty log with player, type, duration |
| `UVA_Players` | Virginia player box scores (G, A, PTS, SH, SOG, GB, DC, TO, CT) |
| `OPP_Players` | Opponent player box scores |
| `Goalkeepers` | GK stats (minutes, GA, saves, decision) |
| `Play_By_Play` | Full PBP text (11 of 13 games) |

The analytics engine (`analytics.py`) processes these into:
- Win probability timelines with momentum modeling
- Player efficiency scores and tier classifications
- Game grades calibrated to D1 women's lacrosse benchmarks
- Season-level aggregations for team rankings

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/laxiq.git
cd laxiq
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run Home.py
```

The app will open at `http://localhost:8501`.

---

## Win Probability Model

LaxIQ uses a hybrid win probability model:

1. **Base WP** — Logistic function of score differential and time remaining: `WP = 1 / (1 + exp(-k * score_diff * time_factor))`
2. **Momentum Modifier** — Non-goal events (draw controls, turnovers, saves, shots, clears) contribute small WP nudges that decay with a factor of 0.82 per event
3. **Event Classification** — PBP text is parsed via regex to identify event types and team attribution, with special handling for abbreviated team names (LOU, PITT, JMU, etc.)

---

## Game Grading System

Six categories graded A+ through F using D1 women's lacrosse calibration:

| Category | Primary Metric | Weight |
|----------|---------------|--------|
| Offense | Goals scored (from Game_Info) | 60% goals + 20% shot efficiency + 20% conversion |
| Defense | Goals allowed | 55% GA + 25% caused turnovers + 20% ground balls |
| Transition | Team turnovers | TO score + differential bonus |
| Draw Unit | Draw controls won | `min(100, 25 + DC * 5.3)` |
| Goalkeeping | Save percentage | `save_pct * 175 - 1.5` |
| Discipline | Penalties committed | `max(0, 97 - penalties * 14)` |

---

## Author

**Faizan Khan** — UVA Data & Scouting Analyst
DS 5023: Interactive Applications (Spring 2026)
University of Virginia, School of Data Science

---

## License

This project is for educational purposes as part of the UVA DS 5023 curriculum.
