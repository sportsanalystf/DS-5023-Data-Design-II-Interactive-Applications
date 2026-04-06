"""LaxIQ — Game Analysis (redesigned to match design mockups)"""

import streamlit as st
st.set_page_config(page_title="Lax IQ - Game Analysis", page_icon="⚔️", layout="wide")

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from style import (CSS, UVA_BLUE, UVA_ORANGE, PLOT_LAYOUT, POSITIVE, NEGATIVE,
                   CYAN, YELLOW, TEAL, GREEN, MAGENTA, WHITE, BORDER, LIGHT_BG,
                   metric_card, insight_box, moment_card, game_header_v2, grade_strip)
from analytics import (
    compute_full_wp_timeline, compute_wp_timeline, compute_wpa,
    compute_quarter_momentum, detect_scoring_runs,
    compute_play_type_impact, classify_pbp_events, compute_turnover_analysis,
    compute_player_efficiency, compare_games, load_game, list_games,
    compute_game_grades, grade_color, synthesize_pbp,
)

st.markdown(CSS, unsafe_allow_html=True)

# ── Sidebar ──
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
        st.markdown(f"""<a href="https://virginiasports.com" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg, {UVA_ORANGE} 0%, #c75b00 100%);
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
    st.divider()

    games = list_games()
    if not games:
        st.error("No game data found in data/ folder.")
        st.stop()

    # Pre-select from Home page navigation
    pre_selected_idx = 0
    if "selected_game" in st.session_state:
        for i, g in enumerate(games):
            if g["file"] == st.session_state["selected_game"].get("file"):
                pre_selected_idx = i
                break

    # Build labels with W/L prefix for clarity in the dropdown
    game_labels = []
    for g in games:
        r = g.get("result", "")
        prefix = "W" if r == "W" else "L"
        game_labels.append(f"[{prefix}] {g['label']}")

    selected_idx = st.selectbox("Select Game", range(len(games)),
                                index=pre_selected_idx,
                                format_func=lambda i: game_labels[i],
                                key="game_selector")
    st.session_state["selected_game"] = games[selected_idx]
    st.session_state["selected_sheets"] = load_game(games[selected_idx]["file"])

    # Visible selected-game indicator (failsafe for dropdown visibility)
    sel_r = games[selected_idx].get("result", "")
    sel_badge_bg = "#2E7D32" if sel_r == "W" else "#C62828"
    sel_badge = "W" if sel_r == "W" else "L"
    st.markdown(f"""<div style="background:rgba(255,255,255,0.12);border-radius:8px;padding:8px 12px;
        margin-top:4px;text-align:center;">
        <span style="background:{sel_badge_bg};padding:2px 8px;border-radius:10px;
            font-size:0.6rem;font-weight:700;letter-spacing:1px;color:white;">{sel_badge}</span>
        <span style="color:white;font-weight:600;font-size:0.8rem;margin-left:6px;">{games[selected_idx]['label']}</span>
    </div>""", unsafe_allow_html=True)
    st.divider()

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

# ── Build quarter scores for header ──
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

# ── Game Header — built with Streamlit native components ──
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

# Score row using st.columns
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

# Quarter scores
if quarter_scores:
    q_cols = st.columns(4)
    for i, (col, (hq, aq)) in enumerate(zip(q_cols, quarter_scores)):
        col.markdown(f"""<div style="text-align:center;background:white;border:1px solid #DADADA;border-radius:8px;padding:6px 4px;">
            <div style="font-size:0.65rem;color:#999;font-weight:600;">Q{i+1}</div>
            <div style="font-size:0.9rem;font-weight:700;color:{UVA_BLUE};">{hq}-{aq}</div>
        </div>""", unsafe_allow_html=True)

# ── Letter Grade Strip — using st.columns ──
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

# ══════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════

tab_wp, tab_players, tab_moments, tab_compare = st.tabs([
    "📈 Win Probability & WPA",
    "👤 Players & Team Stats",
    "🔥 Key Moments & Film Tags",
    "🔄 Game Comparison",
])


# ══════════════════════════════════════════════════════════════════
# TAB 1 — WIN PROBABILITY & WPA
# ══════════════════════════════════════════════════════════════════

with tab_wp:
    try:
        pbp = sheets.get("Play_By_Play")
        scoring_summary = sheets.get("Scoring_Summary")

        # Chart theme constants
        # Plot area is dark; but titles, axis labels, legends sit on the
        # light page background (transparent paper), so they must be dark.
        DARK_BG = "#2A3142"
        GRID_DARK = "rgba(255,255,255,0.08)"
        LABEL_DARK = "#232D4B"       # dark navy for text on light bg
        LABEL_MED  = "#4A5568"       # medium gray-blue for secondary text

        # If PBP is empty, try to synthesize from box score stats
        if pbp is None or pbp.empty:
            stats_qoq = sheets.get("Team_Stats_QoQ")
            if (scoring_summary is not None and not scoring_summary.empty
                    and stats_qoq is not None and not stats_qoq.empty):
                st.caption("No raw play-by-play — synthesized from box score statistics.")
                pbp = synthesize_pbp(scoring_summary, stats_qoq,
                                     sheets.get("UVA_Players"), sheets.get("OPP_Players"),
                                     home_team="Virginia", away_team=opp)

        if pbp is None or pbp.empty:
            # Absolute fallback: no PBP and no stats to synthesize
            if scoring_summary is not None and not scoring_summary.empty:
                st.info("Limited data — showing goal-level win probability only.")
            else:
                st.info("No play-by-play or scoring data available for this game.")
        else:
            timeline = compute_full_wp_timeline(pbp, scoring_summary, home_team="Virginia")

            if timeline.empty:
                st.info("Could not compute win probability timeline.")
            else:
                # ── Dark-themed WP chart matching design mockup ──
                # Build narrative title from game story
                min_wp = timeline["WP"].min()
                max_wp = timeline["WP"].max()
                # Find top UVA scorer
                uva_goals_tl = timeline[(timeline["Event_Type"] == "Goal") & (timeline["Is_Home_Event"] == True)]
                top_scorer = ""
                if not uva_goals_tl.empty and "Event_Player" in uva_goals_tl.columns:
                    scorer_counts = uva_goals_tl["Event_Player"].value_counts()
                    if len(scorer_counts) > 0:
                        top_scorer = scorer_counts.index[0]
                        top_count = scorer_counts.iloc[0]

                if result == "W" and min_wp < 40:
                    chart_title = f"Win Probability — Trailed early, {top_scorer if top_scorer else 'Virginia'} comeback seals win"
                elif result == "W":
                    chart_title = f"Win Probability — Virginia controlled for {hs}-{aws} victory"
                elif result == "L" and max_wp > 60:
                    chart_title = f"Win Probability — Led early but couldn't hold on, falls {hs}-{aws}"
                else:
                    chart_title = f"Win Probability — {'L' if result == 'L' else 'W'} {hs}-{aws} vs {opp}"

                EVENT_STYLE = {
                    # Scoring & Offensive
                    "Goal":               {"color": "#4CAF50", "symbol": "circle",          "size": 14},
                    "Shot":               {"color": UVA_ORANGE,"symbol": "circle-open",     "size": 8},
                    "Free Position":      {"color": "#AB47BC", "symbol": "diamond-tall",    "size": 9},
                    "Blocked Shot":       {"color": "#78909C", "symbol": "octagon",         "size": 8},
                    # Possession & Transition
                    "Draw Control":       {"color": CYAN,      "symbol": "diamond",         "size": 9},
                    "Ground Ball":        {"color": TEAL,      "symbol": "triangle-up",     "size": 8},
                    "Turnover":           {"color": NEGATIVE,  "symbol": "x",               "size": 10},
                    "Clear":              {"color": "#8B8B8B", "symbol": "triangle-down",   "size": 7},
                    # Defensive & Goalie
                    "Save":               {"color": "#42A5F5", "symbol": "square",          "size": 10},
                    # Administrative & Penalty
                    "Card":               {"color": YELLOW,    "symbol": "pentagon",         "size": 10},
                    "Foul":               {"color": MAGENTA,   "symbol": "hexagon",          "size": 7},
                    "Shot Clock Violation": {"color": "#FF7043","symbol": "x-thin",          "size": 8},
                    "Draw Violation":     {"color": "#BCAAA4", "symbol": "diamond-open",     "size": 7},
                    "Timeout":            {"color": "#BDBDBD", "symbol": "hourglass",        "size": 7},
                }

                def build_hover(row):
                    etype = row["Event_Type"]
                    if etype in ("Game Start", "Final"):
                        return f"<b>{etype}</b><br>Score: UVA {int(row['Home_Score'])} - {int(row['Away_Score'])} OPP<br>WP: {row['WP']:.1f}%"
                    team_label = "UVA" if row["Is_Home_Event"] else "OPP" if row["Is_Home_Event"] is not None else ""
                    player = row["Event_Player"] if row["Event_Player"] else ""
                    # Compact hover: "Q3 04:47 | SAVE"
                    q_time = f"Q{int(row['Period'])} {row['Time']}" if row['Time'] else f"Q{int(row['Period'])}"
                    lines = [f"<b>{q_time} | {etype.upper()}</b>"]
                    if team_label and player:
                        lines.append(f"{team_label}: {player}")
                    elif team_label:
                        lines.append(team_label)
                    if etype == "Goal":
                        lines.append(f"Score: UVA {int(row['Home_Score'])} - {int(row['Away_Score'])} OPP")
                    elif etype == "Shot" and row.get("Shot_Detail"):
                        lines.append(row["Shot_Detail"])
                    elif etype == "Clear" and row.get("Clear_Detail"):
                        lines.append(row["Clear_Detail"])
                    elif etype == "Turnover":
                        # Check for caused-by info in play text
                        play_text = str(row.get("Play", ""))
                        import re as _re
                        ct_match = _re.search(r'\(caused by ([^)]+)\)', play_text, _re.IGNORECASE)
                        if ct_match:
                            lines.append(f"Caused by: {ct_match.group(1).strip()}")
                        elif row.get("TO_Detail"):
                            lines.append(row["TO_Detail"])
                    wp_pct = f"WP: {row['WP']:.1f}%"
                    delta = f"WPA: {row['WP_Delta']:+.1f}%"
                    lines.append(f"{wp_pct} | {delta}")
                    return "<br>".join(lines)

                timeline["Hover"] = timeline.apply(build_hover, axis=1)

                # Event filter control
                all_event_types = [et for et in EVENT_STYLE if et in timeline["Event_Type"].values]
                default_on = ["Goal", "Draw Control", "Turnover",
                              "Save", "Shot", "Ground Ball", "Clear", "Card",
                              "Free Position", "Blocked Shot", "Shot Clock Violation"]
                selected_types = st.multiselect(
                    "Event types to display", options=all_event_types,
                    default=[t for t in default_on if t in all_event_types],
                    help="Toggle which play types appear as markers", key="wp_event_filter"
                )

                # Build dark-themed WP chart
                fig = go.Figure()

                # Main WP line — orange, smooth spline
                fig.add_trace(go.Scatter(
                    x=timeline["Minutes_Elapsed"], y=timeline["WP"],
                    mode="lines", name="Win Probability",
                    line=dict(color=UVA_ORANGE, width=2.5, shape="spline",
                              smoothing=0.8),
                    hoverinfo="skip", showlegend=False,
                ))

                # Event markers
                for etype in selected_types:
                    style = EVENT_STYLE.get(etype, {"color": "#999", "symbol": "circle", "size": 8})
                    subset = timeline[timeline["Event_Type"] == etype]
                    if subset.empty:
                        continue
                    uva_ev = subset[subset["Is_Home_Event"] == True]
                    opp_ev = subset[subset["Is_Home_Event"] != True]

                    # UVA goals get green, OPP goals get red
                    uva_color = "#4CAF50" if etype == "Goal" else style["color"]
                    opp_color = "#EF5350" if etype == "Goal" else style["color"]

                    for ev, lbl, mcolor, opacity, border in [
                        (uva_ev, "UVA", uva_color, 1.0, "white"),
                        (opp_ev, "OPP", opp_color, 0.7, DARK_BG),
                    ]:
                        if ev.empty:
                            continue
                        fig.add_trace(go.Scatter(
                            x=ev["Minutes_Elapsed"], y=ev["WP"], mode="markers",
                            name=f"{lbl} {etype}",
                            marker=dict(size=style["size"], color=mcolor,
                                        symbol=style["symbol"], opacity=opacity,
                                        line=dict(width=1.5, color=border)),
                            hovertemplate="%{customdata}<extra></extra>",
                            customdata=ev["Hover"].values, legendgroup=etype,
                        ))

                # 50% reference line
                fig.add_hline(y=50, line_dash="dash", line_color="rgba(255,255,255,0.25)", line_width=1)
                # Quarter dividers
                for mins, label in [(15, ""), (30, "Half"), (45, "")]:
                    fig.add_vline(x=mins, line_dash="dot", line_color="rgba(255,255,255,0.15)", line_width=1,
                                  annotation_text=label, annotation_position="top",
                                  annotation_font_color=LABEL_MED)

                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=DARK_BG,
                    font=dict(family="DM Sans, sans-serif", color=LABEL_DARK, size=12),
                    margin=dict(l=60, r=20, t=70, b=55), height=500,
                    title=dict(text=chart_title, font=dict(size=15, color=LABEL_DARK),
                               x=0.01, xanchor="left"),
                    xaxis=dict(title="Minutes Elapsed", range=[-0.5, 61],
                               tickvals=[0, 15, 30, 45, 60],
                               ticktext=["Start", "Q2", "Half", "Q4", "Final"],
                               gridcolor=GRID_DARK, zerolinecolor=GRID_DARK,
                               linecolor="rgba(255,255,255,0.2)",
                               tickfont=dict(color=LABEL_DARK, size=12),
                               title_font=dict(color=LABEL_MED, size=13)),
                    yaxis=dict(title="Virginia Win Probability (%)", range=[0, 100],
                               ticksuffix="%", gridcolor=GRID_DARK, zerolinecolor=GRID_DARK,
                               linecolor="rgba(255,255,255,0.2)",
                               tickfont=dict(color=LABEL_DARK, size=12),
                               title_font=dict(color=LABEL_MED, size=13)),
                    hovermode="closest",
                    legend=dict(orientation="h", yanchor="bottom", y=1.06,
                                xanchor="center", x=0.5, font=dict(size=10, color=LABEL_DARK),
                                bgcolor="rgba(255,255,255,0.9)", bordercolor=BORDER,
                                borderwidth=1),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Summary metrics row
                goals_only = timeline[timeline["Event_Type"] == "Goal"]
                uva_goals = goals_only[goals_only["Is_Home_Event"] == True]
                opp_goals = goals_only[goals_only["Is_Home_Event"] != True]
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.markdown(metric_card(f"{timeline['WP'].min():.0f}%", "Lowest WP"), unsafe_allow_html=True)
                mc2.markdown(metric_card(f"{timeline['WP'].max():.0f}%", "Highest WP"), unsafe_allow_html=True)
                mc3.markdown(metric_card(str(hs), "UVA Goals"), unsafe_allow_html=True)
                mc4.markdown(metric_card(str(aws), "OPP Goals"), unsafe_allow_html=True)

                # Event Impact Bar Chart — UVA perspective only
                st.markdown('<h4 style="color:#232D4B;">UVA Event Impact Breakdown</h4>', unsafe_allow_html=True)
                impact_etypes = []
                impact_uva_avg = []
                impact_uva_count = []
                for etype in EVENT_STYLE:
                    sub = timeline[timeline["Event_Type"] == etype]
                    if sub.empty:
                        continue
                    uva_s = sub[sub["Is_Home_Event"] == True]
                    if uva_s.empty:
                        continue
                    uva_mean = uva_s["WP_Delta"].mean()
                    if abs(uva_mean) < 0.001:
                        continue
                    impact_etypes.append(etype)
                    impact_uva_avg.append(round(uva_mean, 2))
                    impact_uva_count.append(len(uva_s))

                if impact_etypes:
                    # Sort by absolute impact descending
                    sorted_idx = sorted(range(len(impact_etypes)),
                                        key=lambda i: abs(impact_uva_avg[i]), reverse=True)
                    impact_etypes = [impact_etypes[i] for i in sorted_idx]
                    impact_uva_avg = [impact_uva_avg[i] for i in sorted_idx]
                    impact_uva_count = [impact_uva_count[i] for i in sorted_idx]

                    fig_impact = go.Figure()
                    fig_impact.add_trace(go.Bar(
                        x=impact_etypes, y=impact_uva_avg, name="UVA Avg WP Shift",
                        marker_color=[POSITIVE if v >= 0 else NEGATIVE for v in impact_uva_avg],
                        text=[f"{v:+.2f}% ({n})" for v, n in zip(impact_uva_avg, impact_uva_count)],
                        textposition="outside", showlegend=False,
                    ))
                    fig_impact.add_hline(y=0, line_color="#999", line_width=1)
                    fig_impact.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
                        font=dict(family="DM Sans, sans-serif", color=UVA_BLUE, size=12),
                        margin=dict(l=50, r=20, t=60, b=50), height=360,
                        title=dict(text="UVA Average WP Shift by Event Type", font=dict(size=14)),
                        xaxis=dict(title="", gridcolor="#ECECEC",
                                   zerolinecolor=BORDER, linecolor=BORDER),
                        yaxis=dict(title="Avg WP Shift (%)", ticksuffix="%",
                                   gridcolor="#ECECEC", zerolinecolor=BORDER, linecolor=BORDER),
                    )
                    st.plotly_chart(fig_impact, use_container_width=True)

    except Exception as e:
        st.error(f"Error in Win Probability & WPA tab: {e}")
        import traceback
        st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════════
# TAB 2 — PLAYERS & TEAM STATS
# ══════════════════════════════════════════════════════════════════

with tab_players:
    try:
        DARK_BG_T2 = "#2A3142"
        GRID_DARK_T2 = "rgba(255,255,255,0.08)"
        LABEL_DARK_T2 = "#232D4B"
        LABEL_MED_T2 = "#4A5568"
        UVA_BAR = "#3A5A8C"   # steel blue for UVA bars
        OPP_BAR = "#C62828"   # red for opponent bars

        stats_qoq = sheets.get("Team_Stats_QoQ")
        away_team = info.get("away_team", "Opponent")

        def safe_int(val, default=0):
            try:
                return int(val)
            except (ValueError, TypeError):
                return default

        # ────────────────────────────────────────────────────────
        # SECTION 1 — Overall Statistical Comparison
        # ────────────────────────────────────────────────────────

        if stats_qoq is not None and not stats_qoq.empty:
            # Build comprehensive stat list (matching mockup)
            stat_categories = [
                "Goals", "Shots", "Shots On Goal", "Draw Controls",
                "Ground Balls", "Turnovers", "Saves", "Clears",
                "Free-Position Shots", "Fouls",
            ]
            # Add player-derived stats: Assists, Caused TOs
            uva_players_raw = sheets.get("UVA_Players")
            opp_players_raw = sheets.get("OPP_Players")
            uva_assists = int(uva_players_raw["A"].sum()) if uva_players_raw is not None and "A" in uva_players_raw.columns else 0
            opp_assists = int(opp_players_raw["A"].sum()) if opp_players_raw is not None and "A" in opp_players_raw.columns else 0
            uva_ct = int(uva_players_raw["CT"].sum()) if uva_players_raw is not None and "CT" in uva_players_raw.columns else 0
            opp_ct = int(opp_players_raw["CT"].sum()) if opp_players_raw is not None and "CT" in opp_players_raw.columns else 0

            stats_data = []
            for cat in stat_categories:
                cat_rows = stats_qoq[stats_qoq["Category"] == cat]
                if not cat_rows.empty:
                    uva_row = cat_rows[cat_rows["Team"].str.contains("Virginia", case=False, na=False)]
                    opp_row = cat_rows[~cat_rows["Team"].str.contains("Virginia", case=False, na=False)]
                    uva_total = str(uva_row.iloc[0]["Total"]) if not uva_row.empty else "0"
                    opp_total = str(opp_row.iloc[0]["Total"]) if not opp_row.empty else "0"
                    # Handle Clears format "15-17" → extract made/failed
                    if cat == "Clears":
                        try:
                            uva_parts = uva_total.split("-")
                            opp_parts = opp_total.split("-")
                            uva_made, uva_att = int(uva_parts[0]), int(uva_parts[1])
                            opp_made, opp_att = int(opp_parts[0]), int(opp_parts[1])
                            stats_data.append({"category": "Clears (made)", "uva": uva_made, "opponent": opp_made})
                            stats_data.append({"category": "Failed Clears", "uva": uva_att - uva_made, "opponent": opp_att - opp_made})
                        except (ValueError, IndexError):
                            stats_data.append({"category": cat, "uva": safe_int(uva_total), "opponent": safe_int(opp_total)})
                    else:
                        uv = safe_int(uva_total)
                        ov = safe_int(opp_total)
                        stats_data.append({"category": cat, "uva": uv, "opponent": ov})

            # Insert player-derived stats
            # Goals first from scoring
            # Add Assists and Caused TOs (from player sheets)
            stats_data.append({"category": "Assists", "uva": uva_assists, "opponent": opp_assists})
            stats_data.append({"category": "Caused TOs", "uva": uva_ct, "opponent": opp_ct})

            # Also add Cards from Penalty_Summary if available
            penalties = sheets.get("Penalty_Summary")
            if penalties is not None and not penalties.empty:
                uva_cards = len(penalties[penalties["Team"].str.contains("Virginia", case=False, na=False)])
                opp_cards = len(penalties[~penalties["Team"].str.contains("Virginia", case=False, na=False)])
                stats_data.append({"category": "Cards", "uva": uva_cards, "opponent": opp_cards})

            if stats_data:
                stats_df = pd.DataFrame(stats_data)
                # Reverse order so first category is at top
                stats_df = stats_df.iloc[::-1].reset_index(drop=True)

                max_val = max(stats_df["uva"].max(), stats_df["opponent"].max(), 1)

                fig_stats = go.Figure()
                # UVA bars (left, positive direction)
                fig_stats.add_trace(go.Bar(
                    name="Virginia", y=stats_df["category"], x=stats_df["uva"],
                    orientation="h", marker=dict(color=UVA_BAR),
                    text=stats_df["uva"].apply(lambda v: f"<b>{v}</b>"),
                    textposition="outside", textfont=dict(color=LABEL_DARK_T2, size=12),
                    hovertemplate="<b>%{y}</b><br>UVA: %{x}<extra></extra>",
                ))
                # OPP bars (right, negative direction)
                fig_stats.add_trace(go.Bar(
                    name=away_team, y=stats_df["category"], x=-stats_df["opponent"],
                    orientation="h", marker=dict(color=OPP_BAR),
                    text=stats_df["opponent"].apply(lambda v: f"<b>{v}</b>"),
                    textposition="outside", textfont=dict(color=LABEL_DARK_T2, size=12),
                    hovertemplate="<b>%{y}</b><br>" + away_team + ": %{text}<extra></extra>",
                ))

                n_cats = len(stats_df)
                chart_h = max(400, n_cats * 34 + 80)

                fig_stats.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=DARK_BG_T2,
                    font=dict(family="DM Sans, sans-serif", color=LABEL_DARK_T2, size=12),
                    margin=dict(l=130, r=60, t=50, b=30), height=chart_h,
                    title=dict(text="Statistical Comparison", font=dict(size=15, color=LABEL_DARK_T2),
                               x=0.01, xanchor="left"),
                    xaxis=dict(showgrid=False, zeroline=True,
                               zerolinecolor="rgba(255,255,255,0.3)", zerolinewidth=1,
                               showticklabels=False, range=[-(max_val * 1.25), max_val * 1.25]),
                    yaxis=dict(gridcolor=GRID_DARK_T2,
                               tickfont=dict(color=LABEL_DARK_T2, size=12)),
                    barmode="overlay", showlegend=True, bargap=0.25,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                xanchor="center", x=0.5,
                                font=dict(color=LABEL_DARK_T2, size=11),
                                bgcolor="rgba(255,255,255,0.9)",
                                bordercolor=BORDER, borderwidth=1),
                )
                st.plotly_chart(fig_stats, use_container_width=True)

            # ────────────────────────────────────────────────────────
            # SECTION 2 — Quarter-by-Quarter Breakdown
            # ────────────────────────────────────────────────────────

            st.markdown(f'<h4 style="color:{UVA_BLUE};">Quarter-by-Quarter Breakdown</h4>',
                        unsafe_allow_html=True)

            # Build QoQ data for both teams
            qoq_categories = [
                "Goals", "Shots", "Draw Controls",
                "Ground Balls", "Turnovers", "Saves",
            ]

            # Collect per-quarter stats
            qoq_data = {}  # {quarter: {cat: (uva, opp)}}
            for q_i in range(1, 5):
                q_label = f"Q{q_i}"
                qoq_data[q_label] = {}

            # Goals from Score_By_Quarter
            if score_qoq is not None and not score_qoq.empty:
                home_row = score_qoq[score_qoq["Team"].str.contains("Virginia", case=False, na=False)]
                away_row = score_qoq[~score_qoq["Team"].str.contains("Virginia", case=False, na=False)]
                if not home_row.empty and not away_row.empty:
                    for q_label in ["Q1", "Q2", "Q3", "Q4"]:
                        uv = safe_int(home_row.iloc[0].get(q_label, 0))
                        ov = safe_int(away_row.iloc[0].get(q_label, 0))
                        qoq_data[q_label]["Goals"] = (uv, ov)

            for cat in qoq_categories:
                if cat == "Goals":
                    continue
                cat_rows = stats_qoq[stats_qoq["Category"] == cat]
                if cat_rows.empty:
                    continue
                uva_row = cat_rows[cat_rows["Team"].str.contains("Virginia", case=False, na=False)]
                opp_row = cat_rows[~cat_rows["Team"].str.contains("Virginia", case=False, na=False)]
                for q_label in ["Q1", "Q2", "Q3", "Q4"]:
                    uv = safe_int(uva_row.iloc[0].get(q_label, 0)) if not uva_row.empty else 0
                    ov = safe_int(opp_row.iloc[0].get(q_label, 0)) if not opp_row.empty else 0
                    qoq_data[q_label][cat] = (uv, ov)

            # Render as 4 dark quarter cards side by side
            q_cols = st.columns(4)
            short_labels = {"Goals": "G", "Shots": "SH", "Draw Controls": "DC",
                            "Ground Balls": "GB", "Turnovers": "TO", "Saves": "SV"}
            for col, q_label in zip(q_cols, ["Q1", "Q2", "Q3", "Q4"]):
                q_stats_map = qoq_data.get(q_label, {})
                # Score line
                g_uva, g_opp = q_stats_map.get("Goals", (0, 0))
                score_color = "#4CAF50" if g_uva > g_opp else "#EF5350" if g_opp > g_uva else "white"

                stat_rows_html = ""
                for cat in qoq_categories:
                    uv, ov = q_stats_map.get(cat, (0, 0))
                    sl = short_labels.get(cat, cat[:2])
                    # Highlight advantage
                    uv_w = "font-weight:700;color:white;" if uv > ov else "color:rgba(255,255,255,0.5);"
                    ov_w = "font-weight:700;color:white;" if ov > uv else "color:rgba(255,255,255,0.5);"
                    if uv == ov:
                        uv_w = ov_w = "color:rgba(255,255,255,0.7);"
                    stat_rows_html += f"""<div style="display:flex;justify-content:space-between;
                        padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.06);font-size:0.75rem;">
                        <span style="{uv_w}">{uv}</span>
                        <span style="color:rgba(255,255,255,0.35);font-size:0.65rem;text-transform:uppercase;
                            letter-spacing:0.5px;">{sl}</span>
                        <span style="{ov_w}">{ov}</span>
                    </div>"""

                card_html = f"""<div style="background:{DARK_BG_T2};border-radius:10px;padding:14px 16px;
                    border:1px solid rgba(255,255,255,0.08);">
                    <div style="text-align:center;margin-bottom:10px;">
                        <div style="font-size:0.6rem;color:rgba(255,255,255,0.4);text-transform:uppercase;
                            letter-spacing:1.5px;font-weight:600;">{q_label}</div>
                        <div style="font-size:1.4rem;font-weight:700;color:{score_color};margin-top:2px;">
                            {g_uva} — {g_opp}</div>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:0 2px 4px;
                        font-size:0.6rem;color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:0.5px;">
                        <span>UVA</span><span>{away_team[:3].upper()}</span>
                    </div>
                    {stat_rows_html}
                </div>"""
                with col:
                    st.markdown(card_html, unsafe_allow_html=True)

        # ────────────────────────────────────────────────────────
        # SECTION 3 — Virginia Player Influence (WPA-based)
        # ────────────────────────────────────────────────────────

        st.markdown("---")

        uva_players_df = sheets["UVA_Players"].copy()
        uva_players_df = compute_player_efficiency(uva_players_df)

        # Try to compute real WPA from PBP timeline
        pbp_t2 = sheets.get("Play_By_Play")
        scoring_t2 = sheets.get("Scoring_Summary")
        player_wpa = {}

        if pbp_t2 is None or (hasattr(pbp_t2, "empty") and pbp_t2.empty):
            sqoq_t2 = sheets.get("Team_Stats_QoQ")
            if (scoring_t2 is not None and not scoring_t2.empty
                    and sqoq_t2 is not None and not sqoq_t2.empty):
                pbp_t2 = synthesize_pbp(scoring_t2, sqoq_t2,
                                         sheets.get("UVA_Players"), sheets.get("OPP_Players"),
                                         home_team="Virginia", away_team=opp)

        if pbp_t2 is not None and not pbp_t2.empty:
            try:
                tl_t2 = compute_full_wp_timeline(pbp_t2, scoring_t2, home_team="Virginia")
                if tl_t2 is not None and not tl_t2.empty:
                    uva_ev = tl_t2[(tl_t2["Is_Home_Event"] == True)
                                   & (tl_t2["Event_Player"].notna())
                                   & (tl_t2["Event_Player"] != "")
                                   & (tl_t2["Event_Player"] != "Team")]
                    player_wpa = uva_ev.groupby("Event_Player")["WP_Delta"].sum().to_dict()
            except Exception:
                pass

        # Attach WPA to player rows (fall back to scaled Impact)
        wpa_col = []
        for _, row in uva_players_df.iterrows():
            name = row["Player"]
            if name in player_wpa:
                wpa_col.append(round(player_wpa[name], 1))
            else:
                wpa_col.append(round(row["Impact"] * 0.5, 1))  # scaled fallback
        uva_players_df["WPA"] = wpa_col

        # Filter to players with any activity
        active_players = uva_players_df[
            (uva_players_df["G"] + uva_players_df["A"] + uva_players_df["GB"]
             + uva_players_df["DC"] + uva_players_df["TO"] + uva_players_df["CT"]
             + uva_players_df["SH"] > 0)
            | (uva_players_df["WPA"].abs() > 0.05)
        ].copy()
        active_players = active_players.sort_values("WPA", ascending=True)

        if not active_players.empty:
            bar_colors = [UVA_BAR if v >= 0 else "#B71C1C" for v in active_players["WPA"]]

            fig_inf = go.Figure(data=[go.Bar(
                y=active_players["Player"], x=active_players["WPA"],
                orientation="h", marker=dict(color=bar_colors),
                text=active_players["WPA"].apply(lambda v: f"{v:+.1f}%"),
                textposition="outside", textfont=dict(color=LABEL_DARK_T2, size=11),
                hovertemplate="<b>%{y}</b><br>WPA: %{x:+.1f}%<extra></extra>",
            )])

            n_players = len(active_players)
            inf_h = max(350, n_players * 32 + 80)

            fig_inf.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=DARK_BG_T2,
                font=dict(family="DM Sans, sans-serif", color=LABEL_DARK_T2, size=12),
                margin=dict(l=150, r=60, t=50, b=30), height=inf_h,
                title=dict(text="Virginia Player Influence", font=dict(size=15, color=LABEL_DARK_T2),
                           x=0.01, xanchor="left"),
                xaxis=dict(title="WPA (%)", gridcolor=GRID_DARK_T2,
                           zerolinecolor="rgba(255,255,255,0.3)", zerolinewidth=1,
                           linecolor="rgba(255,255,255,0.2)",
                           tickfont=dict(color=LABEL_DARK_T2, size=11),
                           title_font=dict(color=LABEL_MED_T2, size=13),
                           ticksuffix="%"),
                yaxis=dict(gridcolor=GRID_DARK_T2,
                           tickfont=dict(color=LABEL_DARK_T2, size=12)),
                showlegend=False,
            )
            st.plotly_chart(fig_inf, use_container_width=True)

        # ────────────────────────────────────────────────────────
        # SECTION 4 — Player Statistics Cards
        # ────────────────────────────────────────────────────────

        st.markdown("---")
        st.markdown('<h4 style="color:#232D4B;">Player Statistics</h4>', unsafe_allow_html=True)

        # Sort by WPA descending for card layout
        card_players = uva_players_df[
            (uva_players_df["G"] + uva_players_df["A"] + uva_players_df["GB"]
             + uva_players_df["DC"] + uva_players_df["TO"] + uva_players_df["CT"]
             + uva_players_df["SH"] > 0)
            | (uva_players_df["WPA"].abs() > 0.05)
        ].copy().sort_values("WPA", ascending=False)

        if not card_players.empty:
            # Render 4-column grid of player cards
            cols_per_row = 4
            rows_needed = (len(card_players) + cols_per_row - 1) // cols_per_row
            p_idx = 0
            for row_i in range(rows_needed):
                cols = st.columns(cols_per_row)
                for col in cols:
                    if p_idx >= len(card_players):
                        break
                    p = card_players.iloc[p_idx]
                    name = p["Player"]
                    number = int(p["Number"]) if pd.notna(p.get("Number")) else ""
                    wpa_val = p["WPA"]
                    wpa_color = "#4CAF50" if wpa_val >= 0 else "#EF5350"
                    g_val = int(p["G"])
                    a_val = int(p["A"])
                    dc_val = int(p["DC"])
                    to_val = int(p["TO"])
                    ct_val = int(p["CT"])

                    # Determine which stat to highlight as the key driver
                    # Positive players: highlight their best positive contribution
                    # Negative players: highlight the stat dragging them down
                    stats_list = [("G", g_val), ("A", a_val), ("DC", dc_val), ("TO", to_val), ("CT", ct_val)]
                    highlight_stat = None
                    if wpa_val >= 0:
                        # Positive: pick the highest-value positive stat (G > DC > CT > A)
                        pos_weights = {"G": 5, "DC": 2.5, "CT": 2, "A": 3}
                        best_score, best_label = 0, None
                        for sl, sv in stats_list:
                            if sl == "TO":
                                continue
                            weighted = sv * pos_weights.get(sl, 1)
                            if weighted > best_score:
                                best_score, best_label = weighted, sl
                        if best_score > 0:
                            highlight_stat = (best_label, "#4CAF50")  # green
                    else:
                        # Negative: turnovers are usually the culprit
                        if to_val > 0:
                            highlight_stat = ("TO", "#EF5350")  # red
                        else:
                            # No TOs — check if low production is the issue
                            neg_weights = {"G": 5, "DC": 2.5, "CT": 2, "A": 3}
                            worst_label = None
                            for sl, sv in stats_list:
                                if sl == "TO":
                                    continue
                                if sv == 0 and neg_weights.get(sl, 0) > 0:
                                    worst_label = sl
                                    break
                            if worst_label:
                                highlight_stat = (worst_label, "#EF5350")

                    stat_boxes = ""
                    for stat_label, stat_val in stats_list:
                        is_highlighted = highlight_stat and stat_label == highlight_stat[0]
                        if is_highlighted:
                            hl_color = highlight_stat[1]
                            val_style = f"font-size:1.1rem;font-weight:700;color:{hl_color};"
                            lbl_style = f"font-size:0.55rem;color:{hl_color};text-transform:uppercase;letter-spacing:0.5px;margin-top:2px;font-weight:600;"
                            box_bg = f"background:{'rgba(76,175,80,0.12)' if hl_color == '#4CAF50' else 'rgba(239,83,80,0.12)'};border-radius:6px;"
                        else:
                            val_style = "font-size:1.1rem;font-weight:700;color:white;"
                            lbl_style = "font-size:0.55rem;color:rgba(255,255,255,0.45);text-transform:uppercase;letter-spacing:0.5px;margin-top:2px;"
                            box_bg = ""
                        stat_boxes += f"""<div style="text-align:center;flex:1;padding:3px 2px;{box_bg}">
                            <div style="{val_style}">{stat_val}</div>
                            <div style="{lbl_style}">{stat_label}</div>
                        </div>"""

                    card_html = f"""<div style="background:{DARK_BG_T2};border-radius:10px;padding:14px 16px;
                        margin-bottom:10px;border:1px solid rgba(255,255,255,0.08);">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                            <div>
                                <div style="font-size:0.95rem;font-weight:700;color:white;">{name}</div>
                                <div style="font-size:0.65rem;color:rgba(255,255,255,0.4);">#{number}</div>
                            </div>
                            <div style="font-size:1rem;font-weight:700;color:{wpa_color};
                                font-family:'Courier New',monospace;">{wpa_val:+.1f}%</div>
                        </div>
                        <div style="display:flex;gap:4px;margin-top:12px;background:rgba(0,0,0,0.25);
                            border-radius:8px;padding:8px 4px;">
                            {stat_boxes}
                        </div>
                    </div>"""
                    with col:
                        st.markdown(card_html, unsafe_allow_html=True)
                    p_idx += 1

        # Goalkeeper section
        if "Goalkeepers" in sheets:
            gk = sheets["Goalkeepers"].copy()
            if not gk.empty:
                st.markdown('<h4 style="color:#232D4B;">Goalkeeper Performance</h4>', unsafe_allow_html=True)
                uva_gk = gk[gk["Team"].str.contains("Virginia", case=False, na=False)] if "Team" in gk.columns else gk
                if not uva_gk.empty:
                    for _, gk_row in uva_gk.iterrows():
                        gk_name = gk_row.get("Player", "GK")
                        gk_num = gk_row.get("Number", "")
                        gk_min = gk_row.get("Minutes", "")
                        gk_ga = gk_row.get("GA", 0)
                        gk_sv = gk_row.get("Saves", 0)
                        gk_dec = gk_row.get("Decision", "")
                        dec_color = "#4CAF50" if gk_dec == "W" else "#EF5350"

                        gk_stat_boxes = ""
                        for sl, sv in [("MIN", gk_min), ("GA", gk_ga), ("SV", gk_sv)]:
                            gk_stat_boxes += f"""<div style="text-align:center;flex:1;">
                                <div style="font-size:1.1rem;font-weight:700;color:white;">{sv}</div>
                                <div style="font-size:0.55rem;color:rgba(255,255,255,0.45);text-transform:uppercase;
                                    letter-spacing:0.5px;margin-top:2px;">{sl}</div>
                            </div>"""

                        gk_html = f"""<div style="background:{DARK_BG_T2};border-radius:10px;padding:14px 16px;
                            margin-bottom:10px;border:1px solid rgba(255,255,255,0.08);max-width:320px;">
                            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                                <div>
                                    <div style="font-size:0.95rem;font-weight:700;color:white;">{gk_name}</div>
                                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.4);">#{gk_num}</div>
                                </div>
                                <div style="font-size:0.85rem;font-weight:700;color:{dec_color};
                                    letter-spacing:1px;">{gk_dec}</div>
                            </div>
                            <div style="display:flex;gap:4px;margin-top:12px;background:rgba(0,0,0,0.25);
                                border-radius:8px;padding:8px 4px;">
                                {gk_stat_boxes}
                            </div>
                        </div>"""
                        st.markdown(gk_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error in Players & Team Stats tab: {e}")
        import traceback
        st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════════
# TAB 3 — KEY MOMENTS & FILM TAGS
# ══════════════════════════════════════════════════════════════════

with tab_moments:
    try:
        scoring_summary = sheets.get("Scoring_Summary")
        if scoring_summary is None or scoring_summary.empty:
            st.info("No scoring data available for this game.")
        else:
            wp_tl = compute_wp_timeline(scoring_summary, home_team="Virginia")
            wpa_df = compute_wpa(wp_tl)

            if wpa_df.empty:
                st.info("No goals recorded.")
            else:
                # ── Key Moments (narrative cards with WPA) ──────────
                col_pos, col_neg = st.columns(2)

                with col_pos:
                    st.markdown('<h4 style="color:#232D4B;">Biggest Positive Swings</h4>', unsafe_allow_html=True)
                    for _, row in wpa_df.nlargest(3, "WPA").iterrows():
                        is_uva = "virginia" in str(row["Team"]).lower()
                        team_lbl = "UVA" if is_uva else opp
                        title = f"Q{int(row['Period'])} {row['Time']} — {row['Scorer']}"
                        desc = (f"<b>{team_lbl}</b> scores to make it "
                                f"<b>{row['Score']}</b>, shifting win probability "
                                f"by <span style='color:{POSITIVE};font-weight:700;'>{row['WPA']:+.1f}%</span>")
                        st.markdown(moment_card(title, desc, wpa=row["WPA"], variant="pos"),
                                    unsafe_allow_html=True)

                with col_neg:
                    st.markdown('<h4 style="color:#232D4B;">Biggest Negative Swings</h4>', unsafe_allow_html=True)
                    for _, row in wpa_df.nsmallest(3, "WPA").iterrows():
                        is_uva = "virginia" in str(row["Team"]).lower()
                        team_lbl = "UVA" if is_uva else opp
                        title = f"Q{int(row['Period'])} {row['Time']} — {row['Scorer']}"
                        desc = (f"<b>{team_lbl}</b> scores to make it "
                                f"<b>{row['Score']}</b>, shifting win probability "
                                f"by <span style='color:{NEGATIVE};font-weight:700;'>{row['WPA']:+.1f}%</span>")
                        st.markdown(moment_card(title, desc, wpa=row["WPA"], variant="neg"),
                                    unsafe_allow_html=True)

                # Scoring runs
                runs = detect_scoring_runs(scoring_summary, min_run=3)
                if runs:
                    st.markdown('<h4 style="color:#232D4B;">Scoring Runs (3+ consecutive)</h4>', unsafe_allow_html=True)
                    for run in runs:
                        is_uva = "Virginia" in run["team"]
                        variant = "pos" if is_uva else "neg"
                        title = f"{run['team']} {run['length']}-0 Run — Q{run['start_period']} {run['start_time']} to Q{run['end_period']} {run['end_time']}"
                        desc = f"Scorers: {', '.join(run['scorers'])}. Study execution, transition speed, and defensive breakdowns."
                        st.markdown(moment_card(title, desc, variant=variant), unsafe_allow_html=True)

                # ── Film Tags ────────────────────────────────────
                st.markdown("---")
                st.markdown('<h4 style="color:#232D4B;">Film Tags</h4>', unsafe_allow_html=True)
                st.caption("Suggested film sequences for coaching staff review.")

                ftcol1, ftcol2 = st.columns(2)

                with ftcol1:
                    # Go-ahead goals
                    st.markdown(f'<p style="color:{UVA_BLUE};font-weight:700;margin-bottom:8px;">Go-Ahead Goals</p>', unsafe_allow_html=True)
                    go_ahead = []
                    for _, row in wpa_df.iterrows():
                        sp = row["Score"].split("-")
                        try:
                            h_sc, a_sc = int(sp[0]), int(sp[1])
                        except (ValueError, IndexError):
                            continue
                        is_uva = "Virginia" in row["Team"]
                        if is_uva and h_sc > a_sc and h_sc - 1 <= a_sc:
                            go_ahead.append(row)
                    if go_ahead:
                        for row in go_ahead:
                            title = f"Go-Ahead: {row['Scorer']} — Q{int(row['Period'])} {row['Time']}"
                            desc = f"Score: {row['Score']}. Momentum shift goal."
                            st.markdown(moment_card(title, desc, wpa=row["WPA"], variant="pos"),
                                        unsafe_allow_html=True)
                    else:
                        st.caption("No go-ahead goals detected.")

                    # Must-Show Highlights
                    st.markdown(f'<p style="color:{UVA_BLUE};font-weight:700;margin-bottom:8px;">Must-Show Highlights</p>', unsafe_allow_html=True)
                    for _, row in wpa_df.nlargest(3, "WPA").iterrows():
                        title = f"Must-Show: {row['Scorer']}'s Q{int(row['Period'])} goal ({row['WPA']:+.1f}% WPA)"
                        desc = f"Score: {row['Score']}. High-impact goal."
                        st.markdown(moment_card(title, desc, wpa=row["WPA"], variant="pos"),
                                    unsafe_allow_html=True)

                with ftcol2:
                    # Defensive Review
                    st.markdown(f'<p style="color:{UVA_BLUE};font-weight:700;margin-bottom:8px;">Defensive Review</p>', unsafe_allow_html=True)
                    opp_wpa_goals = wpa_df[~wpa_df["Team"].str.contains("Virginia", case=False)]
                    if not opp_wpa_goals.empty:
                        for _, row in opp_wpa_goals.nsmallest(2, "WPA").iterrows():
                            title = f"Defensive Review: {row['Scorer']}'s Q{int(row['Period'])} goal ({row['WPA']:+.1f}% WPA)"
                            desc = f"Score: {row['Score']}. Analyze defensive positioning."
                            st.markdown(moment_card(title, desc, wpa=row["WPA"], variant="neg"),
                                        unsafe_allow_html=True)

                    # Discipline
                    penalties = sheets.get("Penalty_Summary")
                    if penalties is not None and not penalties.empty:
                        st.markdown(f'<p style="color:{UVA_BLUE};font-weight:700;margin-bottom:8px;">Discipline Review</p>', unsafe_allow_html=True)
                        uva_pens = penalties[penalties["Team"].str.contains("Virginia", case=False)]
                        if not uva_pens.empty:
                            title = f"Discipline — {len(uva_pens)} UVA Card(s)"
                            desc = "Review card sequences, positioning, and rule interpretation."
                            st.markdown(moment_card(title, desc, variant="neg"), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error in Key Moments & Film Tags tab: {e}")
        import traceback
        st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════════
# TAB 4 — GAME COMPARISON
# ══════════════════════════════════════════════════════════════════

with tab_compare:
    try:
        all_games = list_games()
        if len(all_games) < 2:
            st.info("Need at least 2 games for comparison.")
        else:
            st.markdown('<h4 style="color:#232D4B;">Game Comparison</h4>', unsafe_allow_html=True)
            st.caption("Compare Virginia's performance across two games side-by-side.")

            gc1, gc2 = st.columns(2)
            with gc1:
                game_a_idx = st.selectbox("Game A", range(len(all_games)),
                                          format_func=lambda i: all_games[i]["label"], key="cmp_a")
            with gc2:
                default_b = min(1, len(all_games) - 1)
                game_b_idx = st.selectbox("Game B", range(len(all_games)),
                                          format_func=lambda i: all_games[i]["label"],
                                          index=default_b, key="cmp_b")

            sheets_a = load_game(all_games[game_a_idx]["file"])
            sheets_b = load_game(all_games[game_b_idx]["file"])
            comparison = compare_games(sheets_a, sheets_b)

            if not comparison.empty:
                # Game result headers
                hdr_a, hdr_b = st.columns(2)
                info_a = sheets_a["Game_Info"].iloc[0]
                info_b = sheets_b["Game_Info"].iloc[0]
                for col, info_row, label in [(hdr_a, info_a, "Game A"), (hdr_b, info_b, "Game B")]:
                    res = info_row.get("result", "")
                    badge_bg = POSITIVE if res == "W" else NEGATIVE
                    badge = "WIN" if res == "W" else "LOSS"
                    opp_name = info_row.get("away_team", "Opponent")
                    h_sc = int(info_row.get("home_score", 0))
                    a_sc = int(info_row.get("away_score", 0))
                    with col:
                        st.markdown(f"""<div style="background:{UVA_BLUE};border-radius:10px;padding:14px 18px;
                            color:white;text-align:center;margin-bottom:8px;">
                            <span style="background:{badge_bg};padding:2px 10px;border-radius:12px;
                                font-size:0.65rem;font-weight:700;letter-spacing:1px;">{badge}</span>
                            <div style="font-size:1.4rem;font-weight:700;margin-top:6px;">Virginia {h_sc} — {a_sc} {opp_name}</div>
                            <div style="font-size:0.7rem;opacity:0.6;">{info_row.get('date', '')} · {info_row.get('location', '')}</div>
                        </div>""", unsafe_allow_html=True)

                # Statistical comparison bar chart — consistent metrics
                # Define ordered metric columns matching team stats
                metric_order = [
                    ("UVA_Goals", "Goals"), ("UVA_Shots", "Shots"), ("UVA_SOG", "SOG"),
                    ("UVA_Draw Controls", "Draw Controls"), ("UVA_Ground Balls", "Ground Balls"),
                    ("UVA_Turnovers", "Turnovers"), ("UVA_Caused TOs", "Caused TOs"),
                    ("UVA_Saves", "Saves"), ("UVA_Assists", "Assists"),
                    ("UVA_Clears", "Clears"), ("UVA_Cards", "Cards"), ("UVA_Fouls", "Fouls"),
                ]
                chart_cats = []
                vals_a = []
                vals_b = []
                for col_name, display_name in metric_order:
                    if col_name not in comparison.columns:
                        continue
                    v1 = comparison.iloc[0].get(col_name, 0)
                    v2 = comparison.iloc[1].get(col_name, 0)
                    # Convert NaN to 0
                    v1 = 0 if pd.isna(v1) else int(v1)
                    v2 = 0 if pd.isna(v2) else int(v2)
                    chart_cats.append(display_name)
                    vals_a.append(v1)
                    vals_b.append(v2)

                if chart_cats:
                    opp_a = info_a.get("away_team", "Game A")
                    opp_b = info_b.get("away_team", "Game B")
                    fig_cmp = go.Figure()
                    fig_cmp.add_trace(go.Bar(
                        x=chart_cats, y=vals_a, name=f"vs {opp_a}",
                        marker=dict(color=UVA_ORANGE),
                        text=[str(v) for v in vals_a], textposition="outside",
                    ))
                    fig_cmp.add_trace(go.Bar(
                        x=chart_cats, y=vals_b, name=f"vs {opp_b}",
                        marker=dict(color=UVA_BLUE),
                        text=[str(v) for v in vals_b], textposition="outside",
                    ))
                    fig_cmp.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
                        font=dict(family="DM Sans, sans-serif", color=UVA_BLUE, size=12),
                        margin=dict(l=40, r=20, t=50, b=50), height=400, barmode="group",
                        title=dict(text="UVA Stat Comparison", font=dict(size=14, color=UVA_BLUE)),
                        xaxis=dict(gridcolor="#ECECEC", zerolinecolor=BORDER, linecolor=BORDER,
                                   tickfont=dict(size=10)),
                        yaxis=dict(gridcolor="#ECECEC", zerolinecolor=BORDER, linecolor=BORDER),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                    xanchor="center", x=0.5,
                                    font=dict(color=UVA_BLUE)),
                    )
                    st.plotly_chart(fig_cmp, use_container_width=True)

                    # Delta cards — show first row of key stats
                    st.markdown('<h4 style="color:#232D4B;">Stat Deltas</h4>', unsafe_allow_html=True)
                    n_cards = min(len(chart_cats), 6)
                    delta_cols = st.columns(n_cards)
                    for idx in range(n_cards):
                        delta = vals_b[idx] - vals_a[idx]
                        # Turnovers, Cards, Fouls: lower is better
                        is_inverse = chart_cats[idx] in ("Turnovers", "Cards", "Fouls")
                        color = POSITIVE if (delta < 0 if is_inverse else delta > 0) else (NEGATIVE if delta != 0 else "#999")
                        arrow = "+" if delta > 0 else ""
                        with delta_cols[idx]:
                            st.markdown(f"""<div style="text-align:center;background:white;border:1px solid #DADADA;
                                border-radius:10px;padding:10px 6px;">
                                <div style="font-size:0.65rem;color:#999;font-weight:600;text-transform:uppercase;
                                    letter-spacing:0.5px;">{chart_cats[idx]}</div>
                                <div style="font-size:1.2rem;font-weight:700;color:{UVA_BLUE};">
                                    {vals_a[idx]} vs {vals_b[idx]}</div>
                                <div style="font-size:0.85rem;font-weight:700;color:{color};">{arrow}{delta}</div>
                            </div>""", unsafe_allow_html=True)

                # Full comparison table
                st.markdown('<h4 style="color:#232D4B;">Full Comparison Data</h4>', unsafe_allow_html=True)
                # Clean NaN values for display
                display_cmp = comparison.fillna(0)
                st.dataframe(display_cmp, use_container_width=True, hide_index=True)
            else:
                st.info("Could not generate comparison.")

    except Exception as e:
        st.error(f"Error in Game Comparison tab: {e}")
        import traceback
        st.code(traceback.format_exc())
