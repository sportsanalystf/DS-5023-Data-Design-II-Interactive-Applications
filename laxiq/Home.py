"""LaxIQ — Home: Season Overview Dashboard"""

import streamlit as st
from analytics import list_games, load_game
from style import (CSS, UVA_BLUE, UVA_ORANGE, POSITIVE, NEGATIVE,
                   CYAN, YELLOW, GREEN, MAGENTA, TEAL,
                   metric_card, PLOT_LAYOUT)
import pandas as pd
import re

st.set_page_config(page_title="Lax IQ - Cavaliers Lacrosse Analytics", page_icon="⚔️", layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

# Extra CSS for this page
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;600;700&display=swap');

.hero-banner {{
    background: linear-gradient(135deg, {UVA_BLUE} 0%, #1a2238 40%, {UVA_ORANGE} 100%);
    border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    color: white; position: relative; overflow: hidden;
}}
.hero-banner h1 {{
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 3.2rem; letter-spacing: 3px; margin: 0; line-height: 1;
    color: white !important;
}}
.hero-banner .sub {{ color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 6px; }}
.hero-banner .record-badge {{
    display: inline-block; background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3); border-radius: 12px;
    padding: 8px 20px; margin-top: 12px; font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem; letter-spacing: 2px;
}}
.adv-card {{
    background: white; border: 1px solid #DADADA; border-radius: 10px;
    padding: 14px 12px; box-shadow: 0 1px 4px rgba(35,45,75,0.04);
    margin-bottom: 4px;
}}
.adv-card .amc-label {{
    font-size: 0.72rem; color: #999; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;
}}
.adv-card .amc-value {{
    font-size: 1.4rem; font-weight: 700; color: {UVA_BLUE};
}}
.adv-card .amc-rank {{
    font-size: 0.85rem; font-weight: 600; color: {UVA_ORANGE}; float: right;
    margin-top: 4px;
}}
.rank-row {{
    background: white; border: 1px solid #ECECEC; padding: 8px 14px;
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: none;
}}
.rank-row:last-child {{ border-bottom: 1px solid #ECECEC; }}
.rank-row:first-child {{ border-radius: 8px 8px 0 0; }}
.rank-row:last-child {{ border-radius: 0 0 8px 8px; border-bottom: 1px solid #ECECEC; }}
.rank-row .rl {{ font-size: 0.8rem; color: #666; }}
.rank-row .rv {{ font-size: 0.9rem; font-weight: 700; color: {UVA_BLUE}; }}
.rank-row .rr {{ font-size: 0.78rem; font-weight: 600; color: {UVA_ORANGE}; margin-left: 8px; }}

.section-label {{
    font-family: 'Bebas Neue', sans-serif; font-size: 1.3rem;
    letter-spacing: 1.5px; color: {UVA_BLUE}; margin: 1.5rem 0 0.8rem 0;
}}

/* Responsive: keep metric cards from wrapping text oddly */
.metric-card {{
    min-width: 0;
    overflow: hidden;
}}
.metric-value {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.adv-card .amc-value {{
    white-space: nowrap;
}}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    # Virginia Athletics logo
    import os, base64
    _logo_dir = os.path.dirname(__file__)
    _logo_path = os.path.join(_logo_dir, "assets", "va_logo.png")
    if os.path.exists(_logo_path):
        with open(_logo_path, "rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode()
        st.markdown(f"""<a href="https://virginiasports.com" target="_blank" style="display:block;text-align:center;margin-bottom:8px;">
            <img src="data:image/png;base64,{_b64}" style="max-width:180px;margin:0 auto;" />
        </a>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<a href="https://virginiasports.com" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg, {UVA_ORANGE} 0%, #c75b00 100%);
                border-radius:10px;padding:12px 16px;text-align:center;margin-bottom:8px;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;letter-spacing:2px;
                    color:white;line-height:1.1;">VIRGINIA ATHLETICS</div>
            </div>
        </a>""", unsafe_allow_html=True)
    st.markdown(f'<h2 style="margin:0;letter-spacing:1px;font-family:Bebas Neue,sans-serif;">⚔️ LaxIQ</h2>', unsafe_allow_html=True)
    st.caption("Cavaliers Analytics Dashboard")
    st.divider()
    st.page_link("Home.py", label="🏠 Season Overview")
    st.page_link("pages/1_Game_Analysis.py", label="📊 Game Analysis")
    st.page_link("pages/2_Player_Intelligence.py", label="⚔️ Player Intelligence")

# ═══════════════════════════════════════════════════════════════
# FULL SEASON SCHEDULE DATA
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# COMPUTE SEASON STATS
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# COMPUTE ADVANCED STATS FROM GAME DATA
# ═══════════════════════════════════════════════════════════════

available_games = list_games()

@st.cache_data(ttl=600)
def compute_season_advanced_stats():
    """Compute advanced season-level stats from all game data files."""
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

# National percentile rankings (external source — cannot be computed from box scores)
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

# ═══════════════════════════════════════════════════════════════
# HERO BANNER
# ═══════════════════════════════════════════════════════════════

n_games = len(played_games)
st.markdown(f"""<div class="hero-banner">
    <h1>⚔️ Virginia Cavaliers — Player Intelligence</h1>
    <div class="sub">Women's Lacrosse · 2026 Season ({n_games} Games) · Record: {wins}-{losses} · Advanced Analytics Dashboard</div>
    <div class="record-badge">{wins}-{losses} ({conf_wins}-{conf_losses} ACC)</div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# KPI ROW
# ═══════════════════════════════════════════════════════════════

# Use two rows of 4 for better responsiveness on smaller screens
kpi_data = [
    (f"{wins}-{losses}", "Overall", "val-neg" if losses > wins else "val-pos"),
    (f".{int(win_pct * 1000):03d}", "PCT", ""),
    (f"{conf_wins}-{conf_losses}", "ACC", "val-pos" if conf_wins > conf_losses else "val-neg"),
    (f"{streak_type}{streak_count}", "Streak", "val-pos" if streak_type == "W" else "val-neg"),
    (f"{home_wins}-{home_losses}", "Home", "val-neg" if home_losses > home_wins else "val-pos"),
    (f"{away_wins}-{away_losses}", "Away", "val-pos" if away_wins > away_losses else "val-neg"),
    (f"{goals_for}-{goals_against}", "GF-GA", "val-pos" if goals_for > goals_against else "val-neg"),
    (f"{avg_gf:.1f}-{avg_ga:.1f}", "Avg GF-GA", ""),
]
cols = st.columns(len(kpi_data))
for col, (val, label, cls) in zip(cols, kpi_data):
    col.markdown(metric_card(val, label, cls), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# ADVANCED TEAM METRICS — 2 × 4 GRID  (using st.columns)
# ═══════════════════════════════════════════════════════════════

st.markdown(f'<p style="font-family:Bebas Neue,sans-serif;font-size:1.6rem;letter-spacing:1px;color:{UVA_ORANGE};margin:1.2rem 0 0.5rem 0;">Virginia ({wins} – {losses})</p>', unsafe_allow_html=True)

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
        col.markdown(f"""<div class="adv-card">
<div class="amc-label">{label}</div>
<span class="amc-rank">{rank}</span>
<span class="amc-value">{val}</span>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TEAM RANKINGS TABLE (using st.columns for layout)
# ═══════════════════════════════════════════════════════════════

st.markdown(f'<p style="font-family:Bebas Neue,sans-serif;font-size:1.5rem;letter-spacing:1px;color:{UVA_BLUE};margin:1.5rem 0 0.3rem 0;">Team Rankings</p>', unsafe_allow_html=True)


def render_rank_rows(items):
    """Render a list of (label, value, rank) as styled rows."""
    html = ""
    for label, value, rank in items:
        html += f'<div class="rank-row"><span class="rl">{label}</span><span><span class="rv">{value}</span><span class="rr">{rank}</span></span></div>'
    return html


# ── Team section ──
st.markdown(f'<p style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:1px;color:{UVA_BLUE};text-align:center;margin:8px 0 4px 0;">Team</p>', unsafe_allow_html=True)
tc1, tc2 = st.columns(2)
tc1.markdown(render_rank_rows([("Winning Percentage", f"{adv.get('win_pct', 46.2)}%", "77th")]), unsafe_allow_html=True)
tc2.markdown(render_rank_rows([("Scoring Margin", f"{adv.get('scoring_margin', 0.2)}", "71st")]), unsafe_allow_html=True)

# ── Offense & Defense side by side ──
off_col, def_col = st.columns(2)

with off_col:
    st.markdown(f'<p style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:1px;color:{UVA_ORANGE};text-align:center;margin:12px 0 4px 0;">Offense</p>', unsafe_allow_html=True)
    st.markdown(render_rank_rows([
        ("Scoring Offense",  str(adv.get("scoring_offense", 10.6)),  "64th"),
        ("Man-Up Offense",   "35.0%",                                "79th"),
        ("Points / Game",    str(adv.get("points_per_game", 15.0)),  "64th"),
        ("Assists / Game",   str(adv.get("assists_per_game", 4.4)),  "62nd"),
        ("Turnovers / Game", str(adv.get("turnovers_per_game", 12.5)), "96th"),
        ("Shots / Game",     str(adv.get("shots_per_game", 23.7)),   "55th"),
        ("SOG / Game",       str(adv.get("sog_per_game", 16.2)),     "48th"),
    ]), unsafe_allow_html=True)

with def_col:
    st.markdown(f'<p style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:1px;color:{UVA_ORANGE};text-align:center;margin:12px 0 4px 0;">Defense</p>', unsafe_allow_html=True)
    st.markdown(render_rank_rows([
        ("Scoring Defense",   str(adv.get("scoring_defense", 10.4)),     "73rd"),
        ("Man-Down Defense",  "45.8%",                                    "104th"),
        ("Caused TO / Game",  str(adv.get("caused_to_per_game", 7.2)),   "62nd"),
        ("Saves / Game",      str(adv.get("saves_per_game", 6.5)),       "117th"),
        ("Shots / Game",      str(adv.get("opp_shots_per_game", 23.1)),  "50th"),
        ("SOG / Game",        str(adv.get("opp_sog_per_game", 18.2)),    "48th"),
    ]), unsafe_allow_html=True)

# ── Possession Game ──
st.markdown(f'<p style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:1px;color:{UVA_ORANGE};text-align:center;margin:12px 0 4px 0;">Possession Game</p>', unsafe_allow_html=True)
pc1, pc2, pc3, pc4 = st.columns(4)
pc1.markdown(render_rank_rows([("DC Win Rate", f"{adv.get('dc_win_rate', 57.7)}%", "34th")]), unsafe_allow_html=True)
pc2.markdown(render_rank_rows([("GBs / Game", str(adv.get("gbs_per_game", 12.2)), "75th")]), unsafe_allow_html=True)
pc3.markdown(render_rank_rows([("Clear Rate", f"{adv.get('clear_rate', 94.5)}%", "3rd")]), unsafe_allow_html=True)
pc4.markdown(render_rank_rows([("Ride Rate", f"{adv.get('ride_rate', 13.0)}%", "78th")]), unsafe_allow_html=True)

st.markdown('<p style="text-align:center;font-size:0.75rem;color:#999;margin-top:6px;font-style:italic;">If there are terms or concepts that are unfamiliar, a fuller explanation may be available in the glossary.</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# FULL SCHEDULE & RESULTS
# ═══════════════════════════════════════════════════════════════

st.markdown('<div class="section-label">Full Schedule & Results</div>', unsafe_allow_html=True)

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

    # Pre-match the game data for clickable rows
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

    # Build matchup display string
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

    # Use st.columns for each game row
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
            # Make the entire matchup a clickable button
            if st.button(f"📊 {matchup_label}", key=f"nav_{game['date']}",
                         use_container_width=False, type="tertiary"):
                st.session_state["selected_game"] = matched
                st.session_state["selected_sheets"] = load_game(matched["file"])
                st.switch_page("pages/1_Game_Analysis.py")
        else:
            # Non-clickable — just display as text
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


# ═══════════════════════════════════════════════════════════════
# NEXT GAME BANNER
# ═══════════════════════════════════════════════════════════════

next_game = next((g for g in SEASON_SCHEDULE if g["result"] is None and g["note"] not in ("Exhibition", "TBA")), None)
if next_game:
    st.markdown(f"""<div style="background:linear-gradient(135deg, {UVA_BLUE}, #1a2238);
        border-radius:12px;padding:1.2rem 2rem;color:white;text-align:center;">
        <div style="font-size:0.75rem;opacity:0.6;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">Next Game</div>
        <div style="font-size:1.8rem;font-family:'Bebas Neue',sans-serif;letter-spacing:2px;margin:6px 0;">
            {next_game['ha']} {next_game['rank']} {next_game['opponent']}</div>
        <div style="font-size:0.85rem;opacity:0.7;">
            {next_game['day']} {next_game['date']} · {next_game['location']} · {next_game['note']}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f'<div style="text-align:center;font-size:0.75rem;color:#999;padding:8px;">LaxIQ · UVA Women\'s Lacrosse Analytics · Built by Faizan Khan</div>', unsafe_allow_html=True)
