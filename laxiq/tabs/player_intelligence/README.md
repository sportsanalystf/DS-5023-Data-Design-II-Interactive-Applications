# Player Intelligence Tab Modules

Modular components for the Lax IQ Player Intelligence dashboard. Each tab is self-contained and can be developed/tested independently.

## Module Overview

### `metrics.py`
Scoring and evaluation functions.
- `compute_advanced_metrics(p)` - Calculate PPG, consistency, clutch ratio, etc.
- `compute_impact_scores(p, metrics, team_avg)` - Generate 5 impact dimensions (offensive, defensive, possession, efficiency, discipline)
- `get_development_flags(p, metrics, scores)` - Identify strengths/weaknesses
- `get_tier(scores, p)` - Classify players into Tier 1-4
- `generate_coaching_notes(name, p, metrics, scores, tier_num, flags)` - Create player evaluation summary
- `generate_recommendations(name, p, metrics, scores, tier_num, flags)` - Generate coaching recommendations

### `charts.py`
Chart builders for Plotly visualizations.
- `make_radar_chart(scores, pos, height=300)` - Position-specific radar (adaptive for A/M/D/GK)
- `make_game_log_chart(p, games)` - Game-by-game points and goals trend
- `make_shot_efficiency_bar(p)` - Shot funnel (Shots → SOG → Goals)
- `make_percentile_bars(scores, pos)` - Impact score comparison bars
- `make_rolling_avg_chart(p)` - 3-game rolling average for goals
- `make_cumulative_points_chart(all_data, top_n=6)` - Top scorers cumulative line
- `make_usage_efficiency_chart(all_data)` - Scatter plot (Shots/game vs Shooting %)
- `make_draw_control_chart(all_data)` - Top draw control players bar chart

### `team_overview.py`
**Tab 1: Team-Wide Impact Overview**

Renders:
- Tier distribution cards (Tier 1-4 breakdown)
- Usage vs Efficiency quadrant plot
- Cumulative Scoring multi-line chart
- Roster Metrics Heatmap (6 dimensions × roster)

```python
team_overview.render(filtered, sorted_players, all_data)
```

### `player_cards.py`
**Tab 2: Player Performance Cards**

Renders individual player profiles with:
- Headshot & impact score
- Position-specific radar chart
- Core stats metrics
- Game-by-game trend
- Shot funnel visualization
- Development flags
- Coaching notes & recommendations

Includes: `HEADSHOT_URLS` dict for all roster players

```python
player_cards.render(filtered, sorted_players, games)
```

### `player_comparison.py`
**Tab 3: Head-to-Head Comparison**

Renders 1v1 player analysis:
- Side-by-side radar charts
- Grouped bar comparison (5 impact dimensions)
- Raw stats table

```python
player_comparison.render(sorted_players, all_data)
```

### `draw_control.py`
**Tab 4: Draw Control Center** (3 sub-tabs)

1. **UVA Draw Analysis**
   - Kate Galica deep dive
   - Draw control distribution
   - Draw-to-goal conversion pipeline

2. **Opponent Scouting (JMU)**
   - 32 draw clips analyzed
   - Win/loss breakdown by technique
   - Technique frequency chart
   - Key observations

3. **Strategy & Counter-Tactics**
   - 5 counter-draw strategies
   - Specific personnel recommendations
   - Pattern exploitation tips

Includes: `JMU_DRAW_CLIPS` list (32 draw control film clips)

```python
draw_control.render(all_data)
```

### `goal_tending.py`
**Tab 5: Goal Tending Analysis** (4 sub-tabs)

1. **GK Comparison**
   - Elyse Finnelle vs Mel Josephson
   - Side-by-side stats & headshots
   - Save % & GAA comparison chart

2. **Shot Intelligence (Finnelle)**
   - Shot-level data (166 clips)
   - Zone danger analysis
   - Release type effectiveness

3. **Scouting Report**
   - Strengths & development areas
   - Game prep recommendations

4. **Development Plan**
   - 3-phase technical training
   - Weekly milestones
   - Success metrics table

```python
goal_tending.render(all_data)
```

## Usage in Main Page

```python
# In pages/2_Player_Intelligence.py
from tabs.player_intelligence import (
    team_overview, player_cards, player_comparison, draw_control, goal_tending
)

# Create tabs and render
tab1, tab2, tab3, tab4, tab5 = st.tabs([...])

with tab1:
    team_overview.render(filtered, sorted_players, all_data)
with tab2:
    player_cards.render(filtered, sorted_players, games)
with tab3:
    player_comparison.render(sorted_players, all_data)
with tab4:
    draw_control.render(all_data)
with tab5:
    goal_tending.render(all_data)
```

## Design Notes

- **Position-specific logic**: Radar charts adapt to A/M/D/GK roles
- **Tier system**: 4-tier classification (1=Driver, 2=Amplifier, 3=Specialist, 4=Developmental)
- **Impact scoring**: Weighted by position (e.g., attackers value offense > defense)
- **Scouting data**: JMU clips (32) and Finnelle shots (166) embedded for film study context
- **Styling**: All CSS kept in main page; tabs use shared classes (.player-card, .rec-box, etc.)

## Future Enhancements

- Unit tests for metrics.py functions
- CSV export of filtered player data
- PDF scouting reports
- Comparison of player against team averages
- Historical trends (if multi-season data added)
- Live score integration during games
