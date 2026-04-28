# home page - season overview dashboard

import streamlit as st
from analytics import list_games, load_game
from style import (CSS, UVA_BLUE, UVA_ORANGE, POSITIVE, NEGATIVE,
                   CYAN, YELLOW, GREEN, MAGENTA, TEAL,
                   metric_card, PLOT_LAYOUT, section_header)
import pandas as pd
import re

st.set_page_config(page_title="Lax IQ - Cavaliers Lacrosse Analytics", page_icon="⚔️", layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

# sidebar setup
with st.sidebar:
    # logo
    import os
    _logo_dir = os.path.dirname(__file__)
    _logo_path = os.path.join(_logo_dir, "assets", "va_logo.png")
    if os.path.exists(_logo_path):
        st.image(_logo_path, width=180)
    st.title("⚔️ LaxIQ")
    st.caption("Cavaliers Analytics Application")
    st.divider()
    st.page_link("Home.py", label="🏠 Season Overview")
    st.page_link("pages/1_Game_Analysis.py", label="📊 Game Analysis")
    st.page_link("pages/2_Player_Intelligence.py", label="⚔️ Player Intelligence")
    st.page_link("pages/3_LaxIQ_Assistant.py", label="🤖 LaxIQ Assistant")

# Sidebar chat panel
try:
    from sidebar_chat import render_sidebar_chat
    render_sidebar_chat()
except Exception:
    pass  # chat unavailable if google-generativeai not installed

# season schedule

SEASON_SCHEDULE = [
    {"date": "JAN 23", "day": "FRI", "opponent": "Johns Hopkins", "rank": "", "conf": "EXH", "ha": "vs", "location": "Severn, MD", "loc_type": "Neutral", "result": None, "uva_score": None, "opp_score": None, "note": "Exhibition", "uva_rank": ""},
    {"date": "FEB 6",  "day": "FRI", "opponent": "Navy", "rank": "#16", "conf": "", "ha": "vs", "location": "Lower Turf Field", "loc_type": "Home", "result": "L", "uva_score": 10, "opp_score": 12, "note": "data_available", "uva_rank": "#10"},
    {"date": "FEB 11", "day": "WED", "opponent": "Richmond", "rank": "", "conf": "", "ha": "vs", "location": "Lower Turf Field", "loc_type": "Home", "result": "L", "uva_score": 11, "opp_score": 12, "note": "data_available", "uva_rank": "#12"},
    {"date": "FEB 14", "day": "SAT", "opponent": "Maryland", "rank": "#6", "conf": "", "ha": "at", "location": "College Park, Md.", "loc_type": "Away", "result": "L", "uva_score": 9, "opp_score": 17, "note": "data_available", "uva_rank": "#12"},
    {"date": "FEB 18", "day": "WED", "opponent": "Liberty", "rank": "", "conf": "", "ha": "at", "location": "Lynchburg, Va.", "loc_type": "Away", "result": "W", "uva_score": 17, "opp_score": 8, "note": "data_available", "uva_rank": "#24"},
    {"date": "FEB 22", "day": "SUN", "opponent": "Notre Dame", "rank": "#5", "conf": "ACC", "ha": "at", "location": "Notre Dame, Ind.", "loc_type": "Away", "result": "W", "uva_score": 9, "opp_score": 7, "note": "data_available", "uva_rank": "#24"},
    {"date": "FEB 28", "day": "SAT", "opponent": "Stanford", "rank": "#2", "conf": "ACC", "ha": "vs", "location": "Charlottesville, Va.", "loc_type": "Home", "result": "L", "uva_score": 8, "opp_score": 16, "note": "data_available", "uva_rank": "#21"},
    {"date": "MAR 4",  "day": "WED", "opponent": "Pitt", "rank": "#21", "conf": "ACC", "ha": "at", "location": "Pittsburgh, Pa.", "loc_type": "Away", "result": "W", "uva_score": 10, "opp_score": 7, "note": "data_available", "uva_rank": "#20"},
    {"date": "MAR 8",  "day": "SUN", "opponent": "Florida State", "rank": "", "conf": "ACC", "ha": "at", "location": "Tallahassee, Fla.", "loc_type": "Away", "result": "W", "uva_score": 15, "opp_score": 7, "note": "data_available", "uva_rank": "#20"},
    {"date": "MAR 11", "day": "WED", "opponent": "Princeton", "rank": "#19", "conf": "", "ha": "vs", "location": "Charlottesville, Va.", "loc_type": "Home", "result": "W", "uva_score": 12, "opp_score": 10, "note": "data_available", "uva_rank": "#21"},
    {"date": "MAR 14", "day": "SAT", "opponent": "Clemson", "rank": "#9", "conf": "ACC", "ha": "vs", "location": "Charlottesville, Va.", "loc_type": "Home", "result": "L", "uva_score": 10, "opp_score": 12, "note": "data_available", "uva_rank": "#21"},
    {"date": "MAR 21", "day": "SAT", "opponent": "Syracuse", "rank": "#10", "conf": "ACC", "ha": "vs", "location": "Scott Stadium", "loc_type": "Home", "result": "L", "uva_score": 5, "opp_score": 6, "note": "data_available", "uva_rank": "#19"},
    {"date": "MAR 25", "day": "WED", "opponent": "James Madison", "rank": "", "conf": "", "ha": "vs", "location": "Charlottesville, Va.", "loc_type": "Home", "result": "L", "uva_score": 10, "opp_score": 11, "note": "data_available", "uva_rank": "#19"},
    {"date": "MAR 28", "day": "SAT", "opponent": "Louisville", "rank": "", "conf": "ACC", "ha": "at", "location": "Louisville, Ky.", "loc_type": "Away", "result": "W", "uva_score": 12, "opp_score": 10, "note": "data_available", "uva_rank": "#19"},
    {"date": "APR 3",  "day": "FRI", "opponent": "North Carolina", "rank": "#2", "conf": "ACC", "ha": "vs", "location": "Charlottesville, Va.", "loc_type": "Home", "result": None, "uva_score": None, "opp_score": None, "note": "4:00 PM EDT", "uva_rank": "#22"},
    {"date": "APR 11", "day": "SAT", "opponent": "Boston College", "rank": "#13", "conf": "ACC", "ha": "vs", "location": "Charlottesville, Va.", "loc_type": "Home", "result": None, "uva_score": None, "opp_score": None, "note": "1:00 PM EDT", "uva_rank": "#22"},
    {"date": "APR 16", "day": "THU", "opponent": "Virginia Tech", "rank": "", "conf": "ACC", "ha": "at", "location": "Blacksburg, Va.", "loc_type": "Away", "result": None, "uva_score": None, "opp_score": None, "note": "6:00 PM EDT", "uva_rank": "#22"},
    {"date": "APR 22", "day": "WED", "opponent": "ACC Quarterfinals", "rank": "", "conf": "ACC", "ha": "", "location": "Charlotte, N.C.", "loc_type": "", "result": None, "uva_score": None, "opp_score": None, "note": "TBA", "uva_rank": ""},
    {"date": "APR 24", "day": "FRI", "opponent": "ACC Semifinals", "rank": "", "conf": "ACC", "ha": "", "location": "Charlotte, N.C.", "loc_type": "", "result": None, "uva_score": None, "opp_score": None, "note": "TBA", "uva_rank": ""},
    {"date": "APR 26", "day": "SUN", "opponent": "ACC Championship", "rank": "", "conf": "ACC", "ha": "", "location": "Charlotte, N.C.", "loc_type": "", "result": None, "uva_score": None, "opp_score": None, "note": "TBA", "uva_rank": ""},
    {"date": "MAY 8",  "day": "FRI", "opponent": "NCAA First Round", "rank": "", "conf": "NCAA", "ha": "", "location": "TBA", "loc_type": "", "result": None, "uva_score": None, "opp_score": None, "note": "TBA", "uva_rank": ""},
    {"date": "MAY 10", "day": "SUN", "opponent": "NCAA Second Round", "rank": "", "conf": "NCAA", "ha": "", "location": "TBA", "loc_type": "", "result": None, "uva_score": None, "opp_score": None, "note": "TBA", "uva_rank": ""},
    {"date": "MAY 14", "day": "THU", "opponent": "NCAA Quarterfinals", "rank": "", "conf": "NCAA", "ha": "", "location": "TBA", "loc_type": "", "result": None, "uva_score": None, "opp_score": None, "note": "TBA", "uva_rank": ""},
    {"date": "MAY 22-24", "day": "FRI-SUN", "opponent": "NCAA Final Four", "rank": "", "conf": "NCAA", "ha": "", "location": "Chicago, Ill.", "loc_type": "", "result": None, "uva_score": None, "opp_score": None, "note": "TBA", "uva_rank": ""},
]

# calculate season stats

played_games = [g for g in SEASON_SCHEDULE if g["result"] is not None]
upcoming_games = [g for g in SEASON_SCHEDULE if g["result"] is None and g["note"] != "Exhibition"]
wins = sum(1 for g in played_games if g["result"] == "W")
losses = sum(1 for g in played_games if g["result"] == "L")
conf_wins = sum(1 for g in played_games if g["result"] == "W" and g["conf"] == "ACC")
conf_losses = sum(1 for g in played_games if g["result"] == "L" and g["conf"] == "ACC")
home_wins = sum(1 for g in played_games if g["result"] == "W" and g["ha"] == "vs")
home_losses = sum(1 for g in played_games if g["result"] == "L" and g["ha"] == "vs")
away_wins = sum(1 for g in played_games if g["result"] == "W" and g["ha"] == "at")
away_losses = sum(1 for g in played_games if g["result"] == "L" and g["ha"] == "at")
goals_for = sum(g["uva_score"] for g in played_games)
goals_against = sum(g["opp_score"] for g in played_games)
avg_gf = goals_for / max(len(played_games), 1)
avg_ga = goals_against / max(len(played_games), 1)
win_pct = wins / max(wins + losses, 1)

streak_count = 0
streak_type = played_games[-1]["result"] if played_games else ""
for g in reversed(played_games):
    if g["result"] == streak_type:
        streak_count += 1
    else:
        break

# advanced statistics

available_games = list_games()

@st.cache_data(ttl=600)
def compute_season_advanced_stats():
    games_data = list_games()
    n = len(games_data)
    if n == 0:
        return {}

    totals = {
        "goals_for": 0, "goals_against": 0,
        "shots": 0, "sog": 0, "assists": 0,
        "turnovers": 0, "caused_to": 0, "gbs": 0,
        "dc_uva": 0, "dc_opp": 0,
        "saves_uva": 0, "saves_opp": 0,
        "clear_made": 0, "clear_att": 0,
        "opp_clear_made": 0, "opp_clear_att": 0,
        "opp_shots": 0, "opp_sog": 0,
    }

    for gd in games_data:
        s = load_game(gd["file"])
        info = s.get("Game_Info", pd.DataFrame())
        uva_p = s.get("UVA_Players", pd.DataFrame())
        opp_p = s.get("OPP_Players", pd.DataFrame())
        tsq = s.get("Team_Stats_QoQ", pd.DataFrame())

        if not info.empty:
            totals["goals_for"] += info.iloc[0].get("home_score", 0)
            totals["goals_against"] += info.iloc[0].get("away_score", 0)

        if not uva_p.empty:
            totals["shots"] += uva_p["SH"].sum() if "SH" in uva_p.columns else 0
            totals["sog"] += uva_p["SOG"].sum() if "SOG" in uva_p.columns else 0
            totals["assists"] += uva_p["A"].sum() if "A" in uva_p.columns else 0
            totals["turnovers"] += uva_p["TO"].sum() if "TO" in uva_p.columns else 0
            totals["caused_to"] += uva_p["CT"].sum() if "CT" in uva_p.columns else 0
            totals["gbs"] += uva_p["GB"].sum() if "GB" in uva_p.columns else 0

        if not opp_p.empty:
            totals["opp_shots"] += opp_p["SH"].sum() if "SH" in opp_p.columns else 0
            totals["opp_sog"] += opp_p["SOG"].sum() if "SOG" in opp_p.columns else 0

        if not tsq.empty:
            for _, row in tsq.iterrows():
                cat = str(row.get("Category", ""))
                team = str(row.get("Team", ""))
                total = row.get("Total", 0)
                is_uva = "virginia" in team.lower() or "uva" in team.lower()

                if cat == "Clears":
                    m = re.match(r"(\d+)-(\d+)", str(total))
                    if m:
                        made, att = int(m.group(1)), int(m.group(2))
                        if is_uva:
                            totals["clear_made"] += made
                            totals["clear_att"] += att
                        else:
                            totals["opp_clear_made"] += made
                            totals["opp_clear_att"] += att
                elif cat == "Draw Controls":
                    val = int(total) if pd.notna(total) else 0
                    if is_uva:
                        totals["dc_uva"] += val
                    else:
                        totals["dc_opp"] += val
                elif cat == "Saves":
                    val = int(total) if pd.notna(total) else 0
                    if is_uva:
                        totals["saves_uva"] += val
                    else:
                        totals["saves_opp"] += val

    gf = totals["goals_for"]
    ga = totals["goals_against"]
    pts = gf + totals["assists"]
    dc_total = totals["dc_uva"] + totals["dc_opp"]
    _w = sum(1 for g in played_games if g["result"] == "W")
    _l = sum(1 for g in played_games if g["result"] == "L")

    return {
        "n": n,
        "scoring_offense": round(gf / n, 1),
        "scoring_defense": round(ga / n, 1),
        "points_per_game": round(pts / n, 1),
        "assists_per_game": round(totals["assists"] / n, 1),
        "turnovers_per_game": round(totals["turnovers"] / n, 1),
        "caused_to_per_game": round(totals["caused_to"] / n, 1),
        "shots_per_game": round(totals["shots"] / n, 1),
        "sog_per_game": round(totals["sog"] / n, 1),
        "opp_shots_per_game": round(totals["opp_shots"] / n, 1),
        "opp_sog_per_game": round(totals["opp_sog"] / n, 1),
        "shooting_pct": round(gf / max(totals["shots"], 1) * 100, 1),
        "saves_per_game": round(totals["saves_uva"] / n, 1),
        "gbs_per_game": round(totals["gbs"] / n, 1),
        "dc_win_rate": round(totals["dc_uva"] / max(dc_total, 1) * 100, 1),
        "clear_rate": round(totals["clear_made"] / max(totals["clear_att"], 1) * 100, 1),
        "ride_rate": round((1 - totals["opp_clear_made"] / max(totals["opp_clear_att"], 1)) * 100, 1),
        "turnover_rate": round(totals["turnovers"] / max(totals["turnovers"] + gf, 1) * 100, 1),
        "win_pct": round(_w / max(_w + _l, 1) * 100, 1),
        "scoring_margin": round((gf - ga) / n, 1),
    }


adv = compute_season_advanced_stats()

# national rankings

NATIONAL_RANKS = {
    "offensive_efficiency": ("28.6%", "87th"),
    "defensive_efficiency": ("30.3%", "54th"),
    "offensive_pacing":     ("49.8s", "104th"),
    "lax_elo":              ("1641",  "32nd"),
    "shooting_pct":         (f"{adv.get('shooting_pct', 39.9)}%", "87th"),
    "turnover_rate":        (f"{adv.get('turnover_rate', 31.3)}%", "61st"),
    "time_of_possession":   ("52.4%", "34th"),
    "strength_of_record":   ("-2.83", "55th"),
}

# hero banner

n_games = len(played_games)
st.markdown(
    f'<div style="background:{UVA_BLUE};padding:24px 28px;border-radius:10px;margin-bottom:20px;">'
    f'<h1 style="color:white;margin:0;font-size:2rem;">⚔️ LaxIQ — Season Overview</h1>'
    f'<p style="color:{UVA_ORANGE};margin:6px 0 0 0;font-size:0.95rem;">'
    f'Record: {wins}-{losses} ({conf_wins}-{conf_losses} ACC) · {n_games} games played</p></div>',
    unsafe_allow_html=True,
)

# kpi cards
st.markdown(section_header("Season Stats"), unsafe_allow_html=True)
cols = st.columns(4)
cols[0].metric("Overall Record", f"{wins}-{losses}")
cols[1].metric("Win Percentage", f"{win_pct:.1%}")
cols[2].metric("ACC Record", f"{conf_wins}-{conf_losses}")
cols[3].metric("Current Streak", f"{streak_type}{streak_count}")

cols = st.columns(4)
cols[0].metric("Home Record", f"{home_wins}-{home_losses}")
cols[1].metric("Away Record", f"{away_wins}-{away_losses}")
cols[2].metric("Goals For-Against", f"{goals_for}-{goals_against}")
cols[3].metric("Avg GF-GA", f"{avg_gf:.1f}-{avg_ga:.1f}")

# advanced metrics

st.markdown(section_header("National Rankings"), unsafe_allow_html=True)

adv_metrics_row1 = [
    ("Offensive Efficiency", "offensive_efficiency"),
    ("Defensive Efficiency", "defensive_efficiency"),
    ("Offensive Pacing",     "offensive_pacing"),
    ("Lax-ELO Team Strength","lax_elo"),
]
adv_metrics_row2 = [
    ("Shooting Pct",         "shooting_pct"),
    ("Turnover Rate",        "turnover_rate"),
    ("Time-of-Possession",   "time_of_possession"),
    ("Strength-of-Record",   "strength_of_record"),
]

for row_metrics in [adv_metrics_row1, adv_metrics_row2]:
    cols = st.columns(4)
    for col, (label, key) in zip(cols, row_metrics):
        val, rank = NATIONAL_RANKS[key]
        col.metric(label, val, delta=rank)



# full schedule and results

st.markdown(section_header("Full Schedule & Results"), unsafe_allow_html=True)

for game in SEASON_SCHEDULE:
    opp = game["opponent"]
    rank_str = game["rank"]
    ha_str = game["ha"]
    conf_str = f'  ({game["conf"]})' if game["conf"] and game["conf"] not in ("EXH",) else ""
    uva_rank = game.get("uva_rank", "")
    loc_type = game.get("loc_type", "")
    has_data = game.get("note") == "data_available"

    # Result color
    if game["result"] == "W":
        badge_bg = POSITIVE
        result_text = f'**:green[W {game["uva_score"]}-{game["opp_score"]}]**'
    elif game["result"] == "L":
        badge_bg = NEGATIVE
        result_text = f'**:red[L {game["uva_score"]}-{game["opp_score"]}]**'
    elif game["note"] == "Exhibition":
        badge_bg = "#999999"
        result_text = "EXH"
    else:
        badge_bg = UVA_ORANGE
        result_text = game["note"]

    # match game data
    matched = None
    if has_data:
        opp_lower = opp.lower().strip()
        for ag in available_games:
            if opp_lower in ag["away_team"].lower() or ag["away_team"].lower() in opp_lower:
                matched = ag
                break
            if opp_lower in ag.get("label", "").lower():
                matched = ag
                break

    # build matchup label
    matchup_parts = []
    if uva_rank:
        matchup_parts.append(uva_rank)
    matchup_parts.append(f"V {ha_str}")
    if rank_str:
        matchup_parts.append(rank_str)
    matchup_parts.append(opp)
    if conf_str:
        matchup_parts.append(conf_str.strip())
    matchup_label = " ".join(matchup_parts)

    # display game row
    c_date, c_matchup, c_loc, c_result = st.columns([1.2, 4, 2.5, 1.5])

    with c_date:
        st.markdown(
            f'<div style="background:{badge_bg};color:white;border-radius:8px;padding:6px 10px;text-align:center;font-weight:700;font-size:0.78rem;line-height:1.3;">'
            f'<div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:1px;opacity:0.85;">{game["day"]}</div>'
            f'{game["date"]}</div>',
            unsafe_allow_html=True
        )

    with c_matchup:
        if matched:
            if st.button(f"📊 {matchup_label}", key=f"nav_{game['date']}",
                         use_container_width=False, type="tertiary"):
                st.session_state["selected_game"] = matched
                st.session_state["selected_sheets"] = load_game(matched["file"])
                st.switch_page("pages/1_Game_Analysis.py")
        else:
            md_parts = []
            if uva_rank:
                md_parts.append(f":gray[{uva_rank}]")
            md_parts.append(f"**V** {ha_str}")
            if rank_str:
                md_parts.append(f":orange[{rank_str}]")
            md_parts.append(f"**{opp}**")
            if conf_str:
                md_parts.append(f":gray[{conf_str}]")
            st.markdown(" ".join(md_parts))

    with c_loc:
        st.caption(f"{game['location']}")
        if loc_type:
            st.caption(loc_type)

    with c_result:
        st.markdown(result_text)

    st.markdown("---")


# next game banner

next_game = next((g for g in SEASON_SCHEDULE if g["result"] is None and g["note"] not in ("Exhibition", "TBA")), None)
if next_game:
    st.markdown(section_header("Next Game"), unsafe_allow_html=True)
    st.write(f"{next_game['ha']} {next_game['rank']} {next_game['opponent']}")
    st.caption(f"{next_game['day']} {next_game['date']} · {next_game['location']} · {next_game['note']}")

st.markdown("---")
st.markdown(
    f'<div style="text-align:center;padding:12px;color:#999;font-size:0.78rem;">'
    f'LaxIQ · UVA Women\'s Lacrosse Analytics · Built by Faizan Khan</div>',
    unsafe_allow_html=True,
)
