# player intelligence dashboard
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math

# page config
st.set_page_config(
    page_title="Lax IQ - Player Intelligence",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# import colors from style module
from style import (UVA_BLUE, UVA_ORANGE, UVA_BLUE_25, UVA_ORANGE_25,
                   CYAN as UVA_CYAN, YELLOW as UVA_YELLOW, TEAL as UVA_TEAL,
                   GREEN as UVA_GREEN, MAGENTA as UVA_MAGENTA,
                   LIGHT_BG as LIGHT_GRAY, BORDER as MED_GRAY, TEXT_MUTED as TEXT_GRAY,
                   WHITE, PLOT_LAYOUT)

# import tab modules
from tabs.player_intelligence import (
    team_overview, player_cards, player_comparison, draw_control, goal_tending
)
from tabs.player_intelligence.metrics import (
    compute_advanced_metrics, compute_impact_scores, get_development_flags, get_tier,
    generate_coaching_notes, generate_recommendations
)

# extra colors
CAV_ORANGE = "#F84C1E"

# tier system
TIER_COLORS = {1: CAV_ORANGE, 2: UVA_CYAN, 3: UVA_GREEN, 4: MED_GRAY}
# flag colors
FLAG_COLORS = {"positive": UVA_GREEN, "negative": UVA_MAGENTA, "warning": UVA_YELLOW, "info": UVA_CYAN}

# custom styles
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=Bebas+Neue&display=swap');

:root {{
    --uva-blue: {UVA_BLUE};
    --uva-orange: {UVA_ORANGE};
    --cav-orange: {CAV_ORANGE};
}}

.stApp {{
    background-color: {LIGHT_GRAY};
    font-family: 'DM Sans', sans-serif;
    color: {UVA_BLUE};
}}

h1, h2, h3 {{
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 1.5px;
    color: {UVA_BLUE} !important;
}}

section[data-testid="stSidebar"] {{
    background: #FFFFFF !important;
    border-right: 1px solid #DADADA;
}}
section[data-testid="stSidebar"] * {{
    color: {UVA_BLUE} !important;
}}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h4 {{
    color: {UVA_BLUE} !important;
}}
/* hide auto navigation */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{ display: none !important; }}
section[data-testid="stSidebar"] nav {{ display: none !important; }}
section[data-testid="stSidebar"] ul[data-testid="stSidebarNavItems"] {{ display: none !important; }}

.main-header {{
    background: linear-gradient(135deg, {UVA_BLUE} 0%, #1a2238 50%, {UVA_ORANGE} 100%);
    padding: 1.5rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}}
.main-header h1 {{
    color: white !important;
    font-size: 2.5rem;
    margin: 0;
    font-family: 'Bebas Neue', sans-serif !important;
    line-height: 1;
}}
.main-header p {{
    color: rgba(255,255,255,0.75);
    font-size: 0.95rem;
    margin: 0.25rem 0 0 0;
}}

.player-card {{
    background: {WHITE};
    border: 1px solid {MED_GRAY};
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 12px rgba(35,45,75,0.06);
    transition: all 0.25s ease;
    border-left: 5px solid {UVA_ORANGE};
}}
.player-card:hover {{
    box-shadow: 0 4px 24px rgba(35,45,75,0.12);
    border-left-color: {CAV_ORANGE};
}}

.player-name {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: {UVA_BLUE};
    letter-spacing: 2px;
    margin: 0;
    line-height: 1.1;
}}
.player-meta {{
    color: {UVA_ORANGE};
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 3px;
}}

.impact-score-box {{
    background: linear-gradient(135deg, {UVA_ORANGE} 0%, {CAV_ORANGE} 100%);
    border-radius: 14px;
    padding: 1rem 0.8rem;
    text-align: center;
    min-width: 90px;
}}
.impact-score-num {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.8rem;
    color: white;
    line-height: 1;
}}
.impact-score-label {{
    color: rgba(255,255,255,0.9);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
}}

.stat-box {{
    background: {WHITE};
    border: 1px solid {MED_GRAY};
    border-radius: 12px;
    padding: 0.8rem;
    text-align: center;
}}
.stat-val {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    line-height: 1;
}}
.stat-label {{
    font-size: 0.65rem;
    color: {TEXT_GRAY};
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-top: 4px;
}}

.tier-badge {{
    display: inline-block;
    padding: 3px 14px;
    border-radius: 50px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: white;
    vertical-align: middle;
    margin-left: 8px;
}}
.tier-1 {{ background: {CAV_ORANGE}; }}
.tier-2 {{ background: {UVA_CYAN}; }}
.tier-3 {{ background: {UVA_GREEN}; }}
.tier-4 {{ background: {MED_GRAY}; color: {UVA_BLUE}; }}

.flag-tag {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 50px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 3px 4px;
    letter-spacing: 0.5px;
}}
.flag-positive {{ background: #E8F5E9; color: #2E7D32; border: 1px solid #A5D6A7; }}
.flag-negative {{ background: #FCE4EC; color: #C62828; border: 1px solid #EF9A9A; }}
.flag-warning {{ background: #FFF8E1; color: #E65100; border: 1px solid #FFE082; }}
.flag-info {{ background: #E3F2FD; color: #1565C0; border: 1px solid #90CAF9; }}

.coaching-notes {{
    background: #F8F8FC;
    border-left: 4px solid {UVA_BLUE};
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: {UVA_BLUE};
    line-height: 1.65;
    margin-top: 0.8rem;
}}

.rec-box {{
    background: linear-gradient(135deg, #FFF3E0 0%, #FFF8E1 100%);
    border-left: 4px solid {UVA_ORANGE};
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: {UVA_BLUE};
    line-height: 1.65;
    margin-top: 0.5rem;
}}
.rec-box strong {{ color: {CAV_ORANGE}; }}

.section-divider {{
    border: none;
    border-top: 1px solid {MED_GRAY};
    margin: 1rem 0;
}}

.headshot-circle {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid {UVA_ORANGE};
    background: {LIGHT_GRAY};
}}

div[data-testid="stMetric"] {{
    background: {WHITE};
    border: 1px solid {MED_GRAY};
    border-radius: 10px;
    padding: 0.6rem;
}}
div[data-testid="stMetric"] label {{
    color: {TEXT_GRAY} !important;
}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    color: {UVA_BLUE} !important;
}}

.stDataFrame {{ border-radius: 10px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)

# sidebar setup
with st.sidebar:
    import os as _os, base64 as _b64mod
    _logo_path = _os.path.join(_os.path.dirname(__file__), "..", "assets", "va_logo.png")
    if _os.path.exists(_logo_path):
        with open(_logo_path, "rb") as _f:
            _b64 = _b64mod.b64encode(_f.read()).decode()
        st.markdown(f"""<a href="https://virginiasports.com" target="_blank" style="display:block;text-align:center;margin-bottom:8px;">
            <img src="data:image/png;base64,{_b64}" style="max-width:180px;margin:0 auto;" />
        </a>""", unsafe_allow_html=True)
    else:
        st.markdown("""<a href="https://virginiasports.com" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg, #E57200 0%, #c75b00 100%);
                border-radius:10px;padding:12px 16px;text-align:center;margin-bottom:8px;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;letter-spacing:2px;
                    color:white;line-height:1.1;">VIRGINIA ATHLETICS</div>
            </div>
        </a>""", unsafe_allow_html=True)
    st.markdown(f'<h2 style="margin:0;letter-spacing:1px;font-family:Bebas Neue,sans-serif;color:{UVA_BLUE} !important;">⚔️ LaxIQ</h2>', unsafe_allow_html=True)
    st.caption("Cavaliers Analytics Application")
    st.divider()
    st.page_link("Home.py", label="🏠 Season Overview")
    st.page_link("pages/1_Game_Analysis.py", label="📊 Game Analysis")
    st.page_link("pages/2_Player_Intelligence.py", label="⚔️ Player Intelligence")
    st.page_link("pages/3_LaxIQ_Assistant.py", label="🤖 LaxIQ Assistant")
    st.divider()
    # view mode toggle
    view_mode = st.radio("Dashboard Mode", ["Coach View", "Analyst View"],
                         index=1, key="view_mode",
                         help="Coach View: streamlined game-day summaries. Analyst View: full advanced metrics.")
    st.caption("Coach View hides advanced analytics for a cleaner experience.")

# sidebar chat
try:
    from sidebar_chat import render_sidebar_chat
    render_sidebar_chat()
except Exception:
    pass

# data loading
def load_data():
    # load player data from game files
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from analytics import (list_games, load_game, aggregate_player_stats,
                          player_season_totals, get_position, get_number, get_year,
                          POSITION_MAP, PLAYER_NUMBERS, PLAYER_YEARS)

    game_list = list_games()
    if not game_list:
        return _load_data_fallback()

    multi_game_df = aggregate_player_stats(game_list, team="uva")
    if multi_game_df.empty:
        return _load_data_fallback()

    season_totals = player_season_totals(multi_game_df)
    n_games = len(game_list)

    players = {}
    games_labels = [g["label"] for g in game_list]
    game_results = [g["result"] for g in game_list]

    for _, row in season_totals.iterrows():
        name = row["Player"]
        pos = get_position(name)
        if pos == "?":
            continue  # Skip non-roster players
        num = get_number(name)
        yr = get_year(name)
        gp = int(row.get("Games", 1))

        g = int(row.get("G", 0))
        a = int(row.get("A", 0))
        pts = int(row.get("PTS", 0))
        sh = int(row.get("SH", 0))
        sog = int(row.get("SOG", 0))
        gb = int(row.get("GB", 0))
        dc = int(row.get("DC", 0))
        to = int(row.get("TO", 0))
        ct = int(row.get("CT", 0))

        sh_pct = round(g / sh * 100, 1) if sh > 0 else 0
        sog_pct = round(sog / sh * 100, 1) if sh > 0 else 0

        player_games = multi_game_df[multi_game_df["Player"] == name].sort_values("Date")
        game_g = player_games["G"].tolist() if "G" in player_games.columns else []
        game_a = player_games["A"].tolist() if "A" in player_games.columns else []
        game_pts = player_games["PTS"].tolist() if "PTS" in player_games.columns else []
        game_sh = player_games["SH"].tolist() if "SH" in player_games.columns else []
        game_to = player_games["TO"].tolist() if "TO" in player_games.columns else []

        players[name] = {
            "num": num if num else 0, "pos": pos if pos != "?" else "M", "yr": yr if yr else "—",
            "gp": gp, "gs": gp,
            "g": g, "a": a, "pts": pts, "sh": sh, "sh_pct": sh_pct, "sog": sog, "sog_pct": sog_pct,
            "gb": gb, "dc": dc, "to": to, "ct": ct,
            "fpg": 0, "fps": 0,
            "yc": 0, "gc": 0,
            "game_g": [int(x) for x in game_g],
            "game_a": [int(x) for x in game_a],
            "game_pts": [int(x) for x in game_pts],
            "game_sh": [int(x) for x in game_sh],
            "game_to": [int(x) for x in game_to],
        }

        # Check if goalkeeper
        if pos == "GK":
            total_saves = 0
            total_ga = 0
            total_min = 0
            total_w = 0
            total_l = 0
            for gl in game_list:
                gsheets = load_game(gl["file"])
                gk_df = gsheets.get("Goalkeepers", pd.DataFrame())
                if not gk_df.empty and "Player" in gk_df.columns:
                    pk = gk_df[gk_df["Player"].str.contains(name.split()[-1], case=False, na=False)]
                    if not pk.empty:
                        total_saves += int(pk["Saves"].sum()) if "Saves" in pk.columns else 0
                        total_ga += int(pk["GA"].sum()) if "GA" in pk.columns else 0
                        mins_val = pk["Minutes"].sum() if "Minutes" in pk.columns else 0
                        try:
                            total_min += float(mins_val)
                        except (ValueError, TypeError):
                            pass
                        if "Decision" in pk.columns:
                            for d in pk["Decision"]:
                                if str(d).upper() == "W":
                                    total_w += 1
                                elif str(d).upper() == "L":
                                    total_l += 1

            if total_saves + total_ga > 0:
                players[name]["gk_sv"] = total_saves
                players[name]["gk_ga"] = total_ga
                players[name]["gk_min"] = total_min
                players[name]["gk_sv_pct"] = round(total_saves / (total_saves + total_ga) * 100, 1)
                players[name]["gk_gaa"] = round(total_ga / max(total_min / 60, 0.1), 2) if total_min > 0 else 0
                players[name]["gk_w"] = total_w
                players[name]["gk_l"] = total_l

    return players, games_labels, game_results


def _load_data_fallback():
    # fallback demo data
    players = {
        "Madison Alaimo": {"num": 16, "pos": "A", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 10, "a": 15, "pts": 25, "sh": 18, "sh_pct": 55.6, "sog": 16, "sog_pct": 88.9,
            "gb": 4, "dc": 0, "to": 11, "ct": 1, "fpg": 3, "fps": 4, "yc": 0, "gc": 2,
            "game_g": [0,5,3,4,2], "game_a": [4,1,2,3,3], "game_pts": [4,6,5,7,5],
            "game_sh": [3,5,5,4,3], "game_to": [4,2,0,1,4]},
        "Jenna Dinardo": {"num": 4, "pos": "A", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 9, "a": 2, "pts": 11, "sh": 29, "sh_pct": 31.0, "sog": 26, "sog_pct": 89.7,
            "gb": 3, "dc": 8, "to": 10, "ct": 2, "fpg": 3, "fps": 9, "yc": 1, "gc": 3,
            "game_g": [1,3,3,1,1], "game_a": [0,1,1,0,0], "game_pts": [1,4,4,1,1],
            "game_sh": [4,10,8,6,5], "game_to": [3,2,2,1,4]},
        "Addi Foster": {"num": 15, "pos": "A", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 10, "a": 2, "pts": 12, "sh": 24, "sh_pct": 41.7, "sog": 20, "sog_pct": 83.3,
            "gb": 2, "dc": 0, "to": 3, "ct": 0, "fpg": 2, "fps": 2, "yc": 1, "gc": 1,
            "game_g": [0,4,2,3,1], "game_a": [0,1,0,0,1], "game_pts": [0,5,2,3,2],
            "game_sh": [1,5,3,6,6], "game_to": [1,1,0,1,0]},
        "Kate Galica": {"num": 5, "pos": "M", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 6, "a": 5, "pts": 11, "sh": 24, "sh_pct": 25.0, "sog": 17, "sog_pct": 70.8,
            "gb": 13, "dc": 35, "to": 13, "ct": 10, "fpg": 1, "fps": 4, "yc": 0, "gc": 3,
            "game_g": [2,1,0,1,3], "game_a": [0,1,0,2,2], "game_pts": [2,2,0,3,5],
            "game_sh": [3,5,5,6,7], "game_to": [1,4,4,4,2]},
        "Cady Flaherty": {"num": 6, "pos": "M", "yr": "Fr", "gp": 5, "gs": 2,
            "g": 4, "a": 1, "pts": 5, "sh": 7, "sh_pct": 57.1, "sog": 6, "sog_pct": 85.7,
            "gb": 3, "dc": 1, "to": 1, "ct": 2, "fpg": 3, "fps": 3, "yc": 0, "gc": 3,
            "game_g": [2,0,1,1,0], "game_a": [0,1,1,0,0], "game_pts": [2,1,2,1,0],
            "game_sh": [2,1,2,2,1], "game_to": [0,0,0,1,0]},
        "Kate Demark": {"num": 3, "pos": "D", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 3, "dc": 0, "to": 0, "ct": 10, "fpg": 0, "fps": 0, "yc": 0, "gc": 2,
            "game_g": [0,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [0,0,0,0,0],
            "game_sh": [0,0,0,0,0], "game_to": [0,0,0,0,0]},
        "Elyse Finnelle": {"num": 34, "pos": "GK", "yr": "Sr", "gp": 5, "gs": 3,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 10, "dc": 0, "to": 0, "ct": 1, "fpg": 0, "fps": 0, "yc": 0, "gc": 0,
            "gk_min": 230.82, "gk_ga": 39, "gk_gaa": 10.14, "gk_sv": 23, "gk_sv_pct": 37.1,
            "gk_w": 2, "gk_l": 1,
            "game_g": [0,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [0,0,0,0,0],
            "game_sh": [0,0,0,0,0], "game_to": [0,0,0,0,0]},
        "Mel Josephson": {"num": 26, "pos": "GK", "yr": "Sr", "gp": 3, "gs": 2,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 3, "dc": 0, "to": 0, "ct": 0, "fpg": 0, "fps": 0, "yc": 0, "gc": 0,
            "gk_min": 68.47, "gk_ga": 17, "gk_gaa": 14.90, "gk_sv": 10, "gk_sv_pct": 37.0,
            "gk_w": 0, "gk_l": 2,
            "game_g": [0,0,0], "game_a": [0,0,0], "game_pts": [0,0,0],
            "game_sh": [0,0,0], "game_to": [0,0,0]},
        "Alex Reilly": {"num": 23, "pos": "M", "yr": "So", "gp": 5, "gs": 5,
            "g": 1, "a": 0, "pts": 1, "sh": 5, "sh_pct": 20.0, "sog": 3, "sog_pct": 60.0,
            "gb": 2, "dc": 6, "to": 3, "ct": 2, "fpg": 0, "fps": 0, "yc": 2, "gc": 1,
            "game_g": [1,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [1,0,0,0,0],
            "game_sh": [3,0,0,0,0], "game_to": [0,0,0,0,1]},
    }
    games_labels = [f"Game {i+1}" for i in range(5)]
    game_results = ["W", "W", "L", "W", "W"]
    return players, games_labels, game_results


# load data with progress
with st.spinner("Loading player analytics data..."):
    players, games, game_results = load_data()
    _load_progress = st.progress(0, text="Computing metrics...")


team_avg = {}
active = {k: v for k, v in players.items() if v["gp"] >= 2}
team_avg["max_gpg"] = max(v["g"]/v["gp"] for v in active.values())
team_avg["max_ppg"] = max(v["pts"]/v["gp"] for v in active.values())
team_avg["max_apg"] = max(v["a"]/v["gp"] for v in active.values())
team_avg["max_ctpg"] = max(v["ct"]/v["gp"] for v in active.values())
team_avg["max_gbpg"] = max(v["gb"]/v["gp"] for v in active.values())
team_avg["max_dcpg"] = max(v["dc"]/v["gp"] for v in active.values())
team_avg["max_poss_impact"] = max(v["gb"]+v["dc"]+v["ct"]-v["to"] for v in active.values())

all_data = {}
_total_players = len(players)
for _idx, (name, p) in enumerate(players.items()):
    m = compute_advanced_metrics(p)
    s = compute_impact_scores(p, m, team_avg)
    flags = get_development_flags(p, m, s)
    tier_num, tier_label = get_tier(s, p)
    notes = generate_coaching_notes(name, p, m, s, tier_num, flags)
    recs = generate_recommendations(name, p, m, s, tier_num, flags)
    all_data[name] = {"player": p, "metrics": m, "scores": s, "flags": flags,
                      "tier_num": tier_num, "tier_label": tier_label, "notes": notes, "recs": recs}
    _load_progress.progress((_idx + 1) / _total_players, text=f"Analyzing {name}...")
_load_progress.empty()

# Compute season record for header
_wins = sum(1 for g in (list(all_data.values())[0]["player"]["game_g"] if all_data else []) for _ in [0])
try:
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from analytics import list_games as _lg
    _gl = _lg()
    _n_games = len(_gl)
    _wins = sum(1 for g in _gl if g["result"] == "W")
    _losses = _n_games - _wins
    _record_str = f"{_wins}-{_losses}"
except Exception:
    _n_games = len(games)
    _record_str = f"{sum(1 for r in game_results if r=='W')}-{sum(1 for r in game_results if r!='W')}"

st.markdown(f"""
<div class="main-header">
    <div>
        <h1>LaxIQ — PLAYER INTELLIGENCE</h1>
        <p>Women's Lacrosse · 2026 Season ({_n_games} Games) · Record: {_record_str} · Advanced Player Analytics Dashboard</p>
    </div>
</div>
""", unsafe_allow_html=True)

# reset filters callback
def _reset_filters():
    # reset filters to defaults
    st.session_state["filter_position"] = ["A", "M", "D", "GK"]
    st.session_state["filter_tier"]     = [1, 2, 3, 4]
    st.session_state["filter_min_gp"]   = 1
    st.toast("Filters reset!", icon="🔄")

# filters
f1, f2, f3, f4 = st.columns([3, 3, 3, 1])
with f1:
    pos_filter = st.multiselect("Position", ["A", "M", "D", "GK"], default=["A", "M", "D", "GK"],
        key="filter_position")
with f2:
    tier_filter = st.multiselect("Tier", [1, 2, 3, 4], default=[1, 2, 3, 4],
        format_func=lambda x: {1:"Tier 1: Driver", 2:"Tier 2: Amplifier", 3:"Tier 3: Specialist", 4:"Tier 4: Dev"}[x],
        key="filter_tier")
with f3:
    min_gp = st.slider("Min Games Played", 1, 5, 1, key="filter_min_gp")
with f4:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔄 Reset", on_click=_reset_filters, key="reset_filters_btn",
              help="Reset filters")

# input validation
if not pos_filter:
    st.error("⚠️ **No positions selected.** Select at least one position.")
if not tier_filter:
    st.error("⚠️ **No tiers selected.** Select at least one tier.")

filtered = {k: v for k, v in all_data.items()
            if v["player"]["pos"] in pos_filter
            and v["tier_num"] in tier_filter
            and v["player"]["gp"] >= min_gp}
sorted_players = sorted(filtered.items(), key=lambda x: x[1]["scores"]["overall"], reverse=True)

if not filtered and (pos_filter and tier_filter):
    st.warning(f"⚠️ No players found. Try lowering minimum games played.")

# tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Team Overview", "Player Cards", "Player Comparison", "Draw Control Center", "Goal Tending"])

# Render each tab module
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
