# game analysis page - win probability, player stats, key moments, game comparison

import streamlit as st
st.set_page_config(page_title="Lax IQ - Game Analysis", page_icon="⚔️", layout="wide")

from style import CSS, UVA_BLUE, UVA_ORANGE, section_header
from analytics import *
from sidebar import render_sidebar
from api_integrations import (fetch_game_weather, fetch_team_info,
                               render_weather_card, render_team_info_card)

# Hide Streamlit's auto-navigation
st.markdown(CSS, unsafe_allow_html=True)

# --- sidebar with game selector ---
render_sidebar(show_game_selector=True)

# sidebar chat
try:
    from sidebar_chat import render_sidebar_chat
    render_sidebar_chat()
except Exception:
    pass

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

# --- page title and subtitle ---
st.markdown(
    f'<div style="background:{UVA_BLUE};padding:24px 28px;border-radius:10px;margin-bottom:20px;">'
    f'<h1 style="color:white;margin:0;font-size:2rem;">📊 LaxIQ — Game Analysis</h1>'
    f'<p style="color:{UVA_ORANGE};margin:6px 0 0 0;font-size:0.95rem;">'
    f'Women\'s Lacrosse · 2026 Season ({_n_games} Games) · Record: {_wins}-{_losses}</p></div>',
    unsafe_allow_html=True,
)

# build quarter scores
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
result_text = "WIN" if result == "W" else "LOSS"
_result_color = "#2E7D32" if result == "W" else "#C62828"
st.markdown(
    f'<div style="background:white;border:1px solid #E0E0E0;border-radius:10px;padding:20px;text-align:center;margin-bottom:16px;">'
    f'<h2 style="color:{UVA_BLUE};margin:0;">Virginia {hs} - {aws} {opp}</h2>'
    f'<p style="color:#666;margin:6px 0 0 0;">{game_date} · {location} · '
    f'<span style="color:{_result_color};font-weight:700;">{result_text}</span></p></div>',
    unsafe_allow_html=True,
)

# score display using st.metric
h_col, vs_col, a_col = st.columns(3)
with h_col:
    h_col.metric("Virginia", hs)
with vs_col:
    vs_col.text("FINAL")
with a_col:
    a_col.metric(opp, aws)

# quarter scores using st.metric
if quarter_scores:
    st.markdown(section_header("Quarter Scores"), unsafe_allow_html=True)
    q_cols = st.columns(4)
    for i, (col, (hq, aq)) in enumerate(zip(q_cols, quarter_scores)):
        col.metric(f"Q{i+1}", f"{hq}-{aq}")

# game grades using st.metric
grades = compute_game_grades(sheets)
grade_cats = ["Offense", "Defense", "Transition", "Draw Unit", "Goalkeeping", "Discipline"]
st.markdown(section_header("Game Grades"), unsafe_allow_html=True)
g_cols = st.columns(len(grade_cats))
for col, cat in zip(g_cols, grade_cats):
    g = grades.get(cat, "N/A")
    col.metric(cat, g)

# weather card for game location
with st.spinner("Loading weather data..."):
    _loc_parts = [p.strip() for p in location.split(",")] if location else ["Charlottesville"]
    _loc = _loc_parts[1] if len(_loc_parts) >= 2 else _loc_parts[0]
    _weather = fetch_game_weather(_loc, game_date if game_date else None)
    render_weather_card(_weather)

# opponent team info
with st.spinner("Loading opponent info..."):
    _team_info = fetch_team_info(f"{opp}")
    # only show if relevant
    if (_team_info and not _team_info.get("error")
            and _team_info.get("data", {}).get("sport", "").lower() in ("lacrosse", "")):
        render_team_info_card(_team_info)

# tabs
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
