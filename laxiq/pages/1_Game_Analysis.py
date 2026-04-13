# game analysis page - win probability, player stats, key moments, game comparison

import streamlit as st
st.set_page_config(page_title="Lax IQ - Game Analysis", page_icon="⚔️", layout="wide")

from style import *
from analytics import *
from sidebar import render_sidebar
from api_integrations import (fetch_game_weather, fetch_team_info,
                               render_weather_card, render_team_info_card)

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(f"""<style>
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
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.95rem;
    margin: 0.25rem 0 0 0;
}}
</style>""", unsafe_allow_html=True)

# --- sidebar with game selector ---
render_sidebar(show_game_selector=True)

sheets = st.session_state["selected_sheets"]
game = st.session_state["selected_game"]
info = sheets["Game_Info"].iloc[0]
home_team = info.get("home_team", "Virginia")
opp = info.get("away_team", "Opponent")
hs = int(info.get("home_score", 0))
aws = int(info.get("away_score", 0))
result = info.get("result", "")
game_date = str(info.get("date", ""))
location = str(info.get("location", ""))

# compute record for header banner
try:
    _game_list = list_games()
    _n_games = len(_game_list)
    _wins = sum(1 for g in _game_list if g["result"] == "W")
    _losses = _n_games - _wins
except Exception:
    _n_games = 13
    _wins, _losses = 6, 7

# --- page header banner ---
st.markdown(f"""
<div class="main-header">
    <div>
        <h1>LaxIQ — Game Analysis</h1>
        <p>Women's Lacrosse · 2026 Season ({_n_games} Games) · Record: {_wins}-{_losses} · Post-Game Breakdown Dashboard</p>
    </div>
</div>
""", unsafe_allow_html=True)

# build quarter scores for header
quarter_scores = None
score_qoq = sheets.get("Score_By_Quarter")
if score_qoq is not None and not score_qoq.empty:
    try:
        home_row = score_qoq[score_qoq["Team"].str.contains("Virginia", case=False, na=False)]
        away_row = score_qoq[~score_qoq["Team"].str.contains("Virginia", case=False, na=False)]
        if not home_row.empty and not away_row.empty:
            quarter_scores = []
            for q in ["Q1", "Q2", "Q3", "Q4"]:
                hq = int(home_row.iloc[0].get(q, 0))
                aq = int(away_row.iloc[0].get(q, 0))
                quarter_scores.append((hq, aq))
    except Exception:
        pass

# --- game header ---
badge_bg = POSITIVE if result == "W" else NEGATIVE
badge_text = "WIN" if result == "W" else "LOSS"
winner_color = "white"
loser_color = "rgba(255,255,255,0.35)"

st.markdown(f"""<div style="background:linear-gradient(135deg, {UVA_BLUE} 0%, #3A4F7A 50%, {UVA_ORANGE} 100%);
    border-radius:14px;padding:20px 28px;color:white;text-align:center;position:relative;margin-bottom:0;">
    <div style="font-size:0.7rem;opacity:0.6;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">
        Women's Lacrosse &middot; {game_date} &middot; {location}</div>
    <span style="position:absolute;right:28px;top:20px;background:{badge_bg};padding:3px 14px;
        border-radius:20px;font-size:0.68rem;font-weight:700;letter-spacing:1.5px;">{badge_text}</span>
</div>""", unsafe_allow_html=True)

# score row using st.columns
h_col, vs_col, a_col = st.columns([3, 1, 3])
with h_col:
    h_score_color = "white" if result == "W" else "gray"
    st.markdown(f"""<div style="text-align:center;padding:10px 0;">
        <div style="font-size:0.9rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{UVA_ORANGE};">Virginia</div>
        <div style="font-size:3rem;font-weight:700;color:{UVA_BLUE};line-height:1;">{hs}</div>
    </div>""", unsafe_allow_html=True)
with vs_col:
    st.markdown(f'<div style="text-align:center;padding-top:24px;font-size:0.75rem;color:#999;letter-spacing:2px;font-weight:600;">FINAL</div>', unsafe_allow_html=True)
with a_col:
    st.markdown(f"""<div style="text-align:center;padding:10px 0;">
        <div style="font-size:0.9rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#999;">{opp}</div>
        <div style="font-size:3rem;font-weight:700;color:{'#999' if result == 'W' else UVA_BLUE};line-height:1;">{aws}</div>
    </div>""", unsafe_allow_html=True)

# quarter scores
if quarter_scores:
    q_cols = st.columns(4)
    for i, (col, (hq, aq)) in enumerate(zip(q_cols, quarter_scores)):
        col.markdown(f"""<div style="text-align:center;background:white;border:1px solid #DADADA;border-radius:8px;padding:6px 4px;">
            <div style="font-size:0.65rem;color:#999;font-weight:600;">Q{i+1}</div>
            <div style="font-size:0.9rem;font-weight:700;color:{UVA_BLUE};">{hq}-{aq}</div>
        </div>""", unsafe_allow_html=True)

# grade strip — using st.columns
grades = compute_game_grades(sheets)
grade_cats = ["Offense", "Defense", "Transition", "Draw Unit", "Goalkeeping", "Discipline"]
g_cols = st.columns(len(grade_cats))
for col, cat in zip(g_cols, grade_cats):
    g = grades.get(cat, "N/A")
    gc = grade_color(g)
    col.markdown(f"""<div style="text-align:center;background:white;border:1px solid #DADADA;
        border-radius:8px;padding:10px 4px;box-shadow:0 1px 4px rgba(35,45,75,0.04);">
        <div style="font-size:0.65rem;color:#999;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">{cat}</div>
        <div style="font-size:1.6rem;font-weight:700;color:{gc};">{g}</div>
    </div>""", unsafe_allow_html=True)

# ── Milestone 3: API Integration — Weather & Team Info ──
# Weather card for the game location — extract city from "Stadium, City, State" format
with st.spinner("Loading weather data..."):
    _loc_parts = [p.strip() for p in location.split(",")] if location else ["Charlottesville"]
    # city is typically the second part: "Klockner Stadium, Charlottesville, Va."
    _loc = _loc_parts[1] if len(_loc_parts) >= 2 else _loc_parts[0]
    _weather = fetch_game_weather(_loc, game_date if game_date else None)
    render_weather_card(_weather)

# Opponent team info from TheSportsDB — search with "Lacrosse" qualifier
with st.spinner("Loading opponent info..."):
    _team_info = fetch_team_info(f"{opp}")
    # Only show if the result is actually relevant (lacrosse or generic)
    if (_team_info and not _team_info.get("error")
            and _team_info.get("data", {}).get("sport", "").lower() in ("lacrosse", "")):
        render_team_info_card(_team_info)

# --- tabs ---
# Milestone 3: widget key enables programmatic tab tracking via st.session_state
tab_wp, tab_players, tab_moments, tab_compare = st.tabs([
    "📈 Win Probability & WPA",
    "👤 Players & Team Stats",
    "🔥 Key Moments & Film Tags",
    "🔄 Game Comparison",
])

# import tab modules
from tabs.game_analysis import win_probability, player_team_stats, key_moments, game_comparison

with tab_wp:
    win_probability.render(sheets, game, info, home_team, opp, hs, aws, result, quarter_scores)

with tab_players:
    player_team_stats.render(sheets, game, info, home_team, opp, hs, aws)

with tab_moments:
    key_moments.render(sheets, game, info, home_team, opp, hs, aws, result)

with tab_compare:
    game_comparison.render(sheets, game, info, home_team, opp, hs, aws)
