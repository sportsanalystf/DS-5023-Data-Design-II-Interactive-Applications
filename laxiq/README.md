# LaxIQ - UVA Women's Lacrosse Analytics

Post-game analytics dashboard for UVA Women's Lacrosse (2026 season). Built with Streamlit.

## Pages

- **Home** - Season overview with record, KPIs, schedule
- **Game Analysis** - Per-game breakdown with win probability, player stats, key moments, game comparison
- **Player Intelligence** - Player tiers, radar charts, comparisons, draw control analysis, goaltending
- **LaxIQ Assistant** - Chat with an AI assistant about team stats (powered by Gemini)

## How to Run

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## Data

Game data is stored as Excel files in `data/` - one file per game with multiple sheets (box scores, play-by-play, quarter scores, etc).

## Author

Faizan Khan - DS 5023, UVA School of Data Science (Spring 2026)
