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
    compute_game_grades, grade_color,
)

st.markdown(CSS, unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown('<h2 style="margin:0;letter-spacing:1px;font-family:Bebas Neue,sans-serif;">⚔️ LaxIQ</h2>', unsafe_allow_html=True)
    st.caption("Cavaliers Lacrosse Analytics")
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

    game_labels = [g["label"] for g in games]
    selected_idx = st.selectbox("Select Game", range(len(games)),
                                index=pre_selected_idx,
                                format_func=lambda i: game_labels[i])
    st.session_state["selected_game"] = games[selected_idx]
    st.session_state["selected_sheets"] = load_game(games[selected_idx]["file"])
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

        if pbp is None or pbp.empty:
            # Fall back to goal-only WP if no PBP
            if scoring_summary is not None and not scoring_summary.empty:
                st.info("No play-by-play data — showing goal-level win probability.")
                wp_tl = compute_wp_timeline(scoring_summary, home_team="Virginia")
                if not wp_tl.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=list(range(len(wp_tl))), y=wp_tl["WP"],
                        mode="lines+markers", name="Win Probability",
                        line=dict(color=UVA_ORANGE, width=2.5),
                        marker=dict(size=8),
                        text=[f"Q{int(r['Period'])} {r['Time']}<br>{r['Scorer']}<br>UVA {int(r['Home_Score'])}-{int(r['Away_Score'])}"
                              for _, r in wp_tl.iterrows()],
                        hovertemplate="%{text}<br>WP: %{y:.1f}%<extra></extra>",
                    ))
                    fig.add_hline(y=50, line_dash="dash", line_color="#999", opacity=0.4)
                    fig.update_layout(
                        **PLOT_LAYOUT, height=450,
                        title="Win Probability (Goal-Level)",
                        xaxis_title="Goal Number", yaxis_title="Virginia Win Probability (%)",
                        yaxis=dict(range=[0, 100], ticksuffix="%", gridcolor="#ECECEC"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No play-by-play or scoring data available for this game.")
        else:
            timeline = compute_full_wp_timeline(pbp, scoring_summary, home_team="Virginia")

            if timeline.empty:
                st.info("Could not compute win probability timeline.")
            else:
                chart_title = f"Win Probability — {'W' if result == 'W' else 'L'} {hs}-{aws} vs {opp}"

                EVENT_STYLE = {
                    "Goal":          {"color": POSITIVE,   "symbol": "star",          "size": 16},
                    "Draw Control":  {"color": CYAN,       "symbol": "diamond",       "size": 9},
                    "Turnover":      {"color": NEGATIVE,   "symbol": "x",             "size": 9},
                    "Ground Ball":   {"color": TEAL,       "symbol": "triangle-up",   "size": 8},
                    "Save":          {"color": UVA_BLUE,   "symbol": "square",        "size": 10},
                    "Shot":          {"color": UVA_ORANGE,  "symbol": "circle",       "size": 8},
                    "Clear":         {"color": "#8B8B8B",  "symbol": "triangle-down", "size": 7},
                    "Card":          {"color": YELLOW,     "symbol": "pentagon",      "size": 10},
                    "Foul":          {"color": MAGENTA,    "symbol": "hexagon",       "size": 8},
                    "Timeout":       {"color": "#AAAAAA",  "symbol": "hourglass",     "size": 8},
                    "Free Position": {"color": GREEN,      "symbol": "diamond-tall",  "size": 9},
                }

                def build_hover(row):
                    etype = row["Event_Type"]
                    if etype in ("Game Start", "Final"):
                        return f"<b>{etype}</b><br>Score: UVA {int(row['Home_Score'])} - {int(row['Away_Score'])} OPP<br>WP: {row['WP']:.1f}%"
                    team_label = "UVA" if row["Is_Home_Event"] else "OPP" if row["Is_Home_Event"] is not None else ""
                    player = row["Event_Player"] if row["Event_Player"] else ""
                    lines = [f"<b>{etype}</b>", f"Q{int(row['Period'])} {row['Time']}"]
                    if team_label and player:
                        lines.append(f"{team_label} — {player}")
                    elif team_label:
                        lines.append(team_label)
                    if etype == "Goal":
                        lines.append(f"Score: UVA {int(row['Home_Score'])} - {int(row['Away_Score'])} OPP")
                    elif etype == "Shot" and row.get("Shot_Detail"):
                        lines.append(f"Result: {row['Shot_Detail']}")
                    elif etype == "Clear" and row.get("Clear_Detail"):
                        lines.append(f"Clear: {row['Clear_Detail']}")
                    elif etype == "Turnover" and row.get("TO_Detail"):
                        lines.append(row["TO_Detail"])
                    lines.append(f"WP: {row['WP']:.1f}% ({row['WP_Delta']:+.1f})")
                    return "<br>".join(lines)

                timeline["Hover"] = timeline.apply(build_hover, axis=1)

                # Event filter control
                all_event_types = [et for et in EVENT_STYLE if et in timeline["Event_Type"].values]
                default_on = ["Goal", "Draw Control", "Turnover", "Save", "Shot"]
                selected_types = st.multiselect(
                    "Event types to display", options=all_event_types,
                    default=[t for t in default_on if t in all_event_types],
                    help="Toggle which play types appear as markers", key="wp_event_filter"
                )

                # Build WP chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timeline["Minutes_Elapsed"], y=timeline["WP"],
                    mode="lines", name="Win Probability",
                    line=dict(color=UVA_ORANGE, width=2.5),
                    hoverinfo="skip", showlegend=False,
                ))

                for etype in selected_types:
                    style = EVENT_STYLE.get(etype, {"color": "#999", "symbol": "circle", "size": 8})
                    subset = timeline[timeline["Event_Type"] == etype]
                    if subset.empty:
                        continue
                    # UVA events: Is_Home_Event == True; OPP events: everything else (False or None)
                    uva_ev = subset[subset["Is_Home_Event"] == True]
                    opp_ev = subset[subset["Is_Home_Event"] != True]
                    for ev, lbl, opacity, border in [
                        (uva_ev, "UVA", 1.0, "white"),
                        (opp_ev, "OPP", 0.5, "#333"),
                    ]:
                        if ev.empty:
                            continue
                        fig.add_trace(go.Scatter(
                            x=ev["Minutes_Elapsed"], y=ev["WP"], mode="markers",
                            name=f"{lbl} {etype}",
                            marker=dict(size=style["size"], color=style["color"],
                                        symbol=style["symbol"], opacity=opacity,
                                        line=dict(width=1, color=border)),
                            hovertemplate="%{customdata}<extra></extra>",
                            customdata=ev["Hover"].values, legendgroup=etype,
                        ))

                fig.add_hline(y=50, line_dash="dash", line_color="#999", opacity=0.4)
                for mins, label in [(15, "Q2"), (30, "Half"), (45, "Q4")]:
                    fig.add_vline(x=mins, line_dash="dot", line_color="#CCC", opacity=0.6,
                                 annotation_text=label, annotation_position="top")

                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
                    font=dict(family="DM Sans, sans-serif", color=UVA_BLUE, size=12),
                    margin=dict(l=50, r=20, t=60, b=50), height=500,
                    title=dict(text=chart_title, font=dict(size=16)),
                    xaxis=dict(title="Minutes Elapsed", range=[-0.5, 61],
                               tickvals=[0, 15, 30, 45, 60],
                               ticktext=["Start", "Q2", "Half", "Q4", "Final"],
                               gridcolor="#ECECEC", zerolinecolor=BORDER, linecolor=BORDER),
                    yaxis=dict(title="Virginia Win Probability (%)", range=[0, 100],
                               ticksuffix="%", gridcolor="#ECECEC",
                               zerolinecolor=BORDER, linecolor=BORDER),
                    hovermode="closest",
                    legend=dict(orientation="h", yanchor="bottom", y=1.03,
                                xanchor="center", x=0.5, font=dict(size=10)),
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

                # Event Impact Bar Chart
                st.markdown("#### Event Impact Breakdown")
                impact_etypes = []
                impact_uva_avg = []
                impact_opp_avg = []
                for etype in EVENT_STYLE:
                    sub = timeline[timeline["Event_Type"] == etype]
                    if sub.empty:
                        continue
                    uva_s = sub[sub["Is_Home_Event"] == True]
                    opp_s = sub[sub["Is_Home_Event"] != True]
                    uva_mean = uva_s["WP_Delta"].mean() if not uva_s.empty else 0
                    opp_mean = opp_s["WP_Delta"].mean() if not opp_s.empty else 0
                    if uva_mean == 0 and opp_mean == 0:
                        continue
                    impact_etypes.append(etype)
                    impact_uva_avg.append(round(uva_mean, 2))
                    impact_opp_avg.append(round(opp_mean, 2))

                if impact_etypes:
                    fig_impact = go.Figure()
                    fig_impact.add_trace(go.Bar(
                        x=impact_etypes, y=impact_uva_avg, name="UVA Avg WP Shift",
                        marker_color=[POSITIVE if v >= 0 else NEGATIVE for v in impact_uva_avg],
                        text=[f"{v:+.2f}%" for v in impact_uva_avg], textposition="outside",
                    ))
                    fig_impact.add_trace(go.Bar(
                        x=impact_etypes, y=impact_opp_avg, name="OPP Avg WP Shift",
                        marker_color=[f"rgba(35,45,75,0.4)" if v >= 0 else f"rgba(198,40,40,0.4)" for v in impact_opp_avg],
                        text=[f"{v:+.2f}%" for v in impact_opp_avg], textposition="outside",
                    ))
                    fig_impact.add_hline(y=0, line_color="#999", line_width=1)
                    fig_impact.update_layout(
                        **PLOT_LAYOUT, height=380, barmode="group",
                        title=dict(text="Average WP Shift by Event Type", font=dict(size=14)),
                        xaxis_title="", yaxis_title="Avg WP Shift (%)",
                        yaxis=dict(ticksuffix="%", gridcolor="#ECECEC"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
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
        # ── Player Influence ─────────────────────────────────────
        st.markdown("#### Player Influence")

        uva_players = sheets["UVA_Players"].copy()
        uva_players = compute_player_efficiency(uva_players)
        uva_players = uva_players.sort_values("Impact", ascending=False)

        top_12 = uva_players.head(12).sort_values("Impact", ascending=True)
        colors_imp = [UVA_ORANGE if x >= 0 else NEGATIVE for x in top_12["Impact"]]

        fig_impact = go.Figure(data=[go.Bar(
            y=top_12["Player"], x=top_12["Impact"], orientation="h",
            marker=dict(color=colors_imp),
            text=top_12["Impact"].round(1), textposition="auto",
            hovertemplate="<b>%{y}</b><br>Impact: %{x:.1f}<extra></extra>"
        )])
        fig_impact.update_layout(**PLOT_LAYOUT, title="Top Players by Impact Score",
                                 xaxis_title="Impact Score", yaxis_title="", height=400, showlegend=False)
        st.plotly_chart(fig_impact, use_container_width=True)

        # Player stats table
        st.markdown("#### Player Statistics")
        display_cols = ["Player", "G", "A", "PTS", "SH", "SOG", "GB", "DC", "TO", "CT", "Shot_Pct", "Impact"]
        available_cols = [c for c in display_cols if c in uva_players.columns]
        display_df = uva_players[available_cols].copy()
        if "Shot_Pct" in display_df.columns:
            display_df["Shot_Pct"] = display_df["Shot_Pct"].apply(lambda x: f"{x:.1f}%" if x > 0 else "—")
        display_df = display_df.rename(columns={
            "G": "Goals", "A": "Assists", "PTS": "Points", "SH": "Shots",
            "SOG": "SOG", "GB": "GB", "DC": "DC", "TO": "TO", "CT": "CT",
            "Shot_Pct": "Shot %", "Impact": "Impact"
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Goalkeeper
        if "Goalkeepers" in sheets:
            st.markdown("#### Goalkeeper Performance")
            gk = sheets["Goalkeepers"].copy()
            if not gk.empty:
                gk_cols = ["Player", "Minutes", "GA", "Saves", "Decision"]
                show_cols = [c for c in gk_cols if c in gk.columns]
                st.dataframe(gk[show_cols] if show_cols else gk, use_container_width=True, hide_index=True)

        # ── Statistical Comparison (butterfly bar chart) ─────────
        st.markdown("---")
        st.markdown("#### Statistical Comparison")

        stats_qoq = sheets.get("Team_Stats_QoQ")
        away_team = info.get("away_team", "Opponent")

        if stats_qoq is not None and not stats_qoq.empty:
            categories = ["Shots", "Saves", "Ground Balls", "Draw Controls", "Turnovers", "Clears"]
            stats_data = []

            def safe_int(val, default=0):
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return default

            for cat in categories:
                cat_rows = stats_qoq[stats_qoq["Category"] == cat]
                if not cat_rows.empty:
                    uva_row = cat_rows[cat_rows["Team"].str.contains("Virginia", case=False, na=False)]
                    opp_row = cat_rows[~cat_rows["Team"].str.contains("Virginia", case=False, na=False)]
                    uva_val = safe_int(uva_row.iloc[0]["Total"]) if not uva_row.empty else 0
                    opp_val = safe_int(opp_row.iloc[0]["Total"]) if not opp_row.empty else 0
                    if uva_val == 0 and opp_val == 0:
                        continue
                    stats_data.append({"category": cat, "uva": uva_val, "opponent": opp_val})

            if stats_data:
                stats_df = pd.DataFrame(stats_data)

                # Butterfly bar chart (UVA right, OPP left)
                fig_stats = go.Figure()
                fig_stats.add_trace(go.Bar(
                    name="UVA", y=stats_df["category"], x=stats_df["uva"],
                    orientation="h", marker=dict(color=UVA_ORANGE),
                    text=stats_df["uva"], textposition="outside",
                ))
                fig_stats.add_trace(go.Bar(
                    name=away_team, y=stats_df["category"], x=-stats_df["opponent"],
                    orientation="h", marker=dict(color="#C62828"),
                    text=stats_df["opponent"], textposition="outside",
                ))
                fig_stats.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#232D4B",
                    font=dict(family="DM Sans, sans-serif", color="white", size=12),
                    margin=dict(l=120, r=60, t=50, b=40), height=350,
                    title=dict(text="Statistical Comparison", font=dict(color=UVA_BLUE)),
                    xaxis=dict(showgrid=False, zeroline=True, zerolinecolor="rgba(255,255,255,0.3)",
                               showticklabels=False),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.1)", tickfont=dict(color="white")),
                    barmode="overlay", showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                xanchor="center", x=0.5, font=dict(color=UVA_BLUE)),
                )
                st.plotly_chart(fig_stats, use_container_width=True)

            # Quarter-by-quarter breakdown
            st.markdown("#### Quarter-by-Quarter Breakdown")
            quarters_data = []
            for cat in categories:
                cat_rows = stats_qoq[stats_qoq["Category"] == cat]
                if not cat_rows.empty:
                    uva_row = cat_rows[cat_rows["Team"].str.contains("Virginia", case=False, na=False)]
                    if not uva_row.empty:
                        q_vals = []
                        for q in ["Q1", "Q2", "Q3", "Q4"]:
                            try:
                                q_vals.append(int(uva_row.iloc[0][q]) if q in uva_row.columns else 0)
                            except (ValueError, TypeError):
                                q_vals.append(0)
                        quarters_data.append({"Stat": cat, "Q1": q_vals[0], "Q2": q_vals[1],
                                              "Q3": q_vals[2], "Q4": q_vals[3], "Total": sum(q_vals)})
            if quarters_data:
                st.dataframe(pd.DataFrame(quarters_data), use_container_width=True, hide_index=True)

            # Scoring by Quarter chart
            if score_qoq is not None and not score_qoq.empty:
                st.markdown("#### Scoring by Quarter")
                home_row = score_qoq[score_qoq["Team"].str.contains("Virginia", case=False, na=False)]
                away_row = score_qoq[~score_qoq["Team"].str.contains("Virginia", case=False, na=False)]
                if not home_row.empty and not away_row.empty:
                    quarters = ["Q1", "Q2", "Q3", "Q4"]
                    try:
                        uva_sc = [int(home_row.iloc[0][q]) for q in quarters]
                        opp_sc = [int(away_row.iloc[0][q]) for q in quarters]
                        fig_sq = go.Figure(data=[
                            go.Bar(name="UVA", x=quarters, y=uva_sc, marker=dict(color=UVA_ORANGE)),
                            go.Bar(name=away_team, x=quarters, y=opp_sc, marker=dict(color="#C62828")),
                        ])
                        fig_sq.update_layout(**PLOT_LAYOUT, title="Scoring by Quarter",
                                            xaxis_title="Quarter", yaxis_title="Goals",
                                            barmode="group", height=300,
                                            legend=dict(x=0.99, y=0.99, xanchor="right", yanchor="top"))
                        st.plotly_chart(fig_sq, use_container_width=True)
                    except (ValueError, TypeError):
                        pass

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
                    st.markdown("#### Biggest Positive Swings")
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
                    st.markdown("#### Biggest Negative Swings")
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
                    st.markdown("#### Scoring Runs (3+ consecutive)")
                    for run in runs:
                        is_uva = "Virginia" in run["team"]
                        variant = "pos" if is_uva else "neg"
                        title = f"{run['team']} {run['length']}-0 Run — Q{run['start_period']} {run['start_time']} to Q{run['end_period']} {run['end_time']}"
                        desc = f"Scorers: {', '.join(run['scorers'])}. Study execution, transition speed, and defensive breakdowns."
                        st.markdown(moment_card(title, desc, variant=variant), unsafe_allow_html=True)

                # ── Film Tags ────────────────────────────────────
                st.markdown("---")
                st.markdown("#### Film Tags")
                st.caption("Suggested film sequences for coaching staff review.")

                ftcol1, ftcol2 = st.columns(2)

                with ftcol1:
                    # Go-ahead goals
                    st.markdown("**Go-Ahead Goals**")
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
                    st.markdown("**Must-Show Highlights**")
                    for _, row in wpa_df.nlargest(3, "WPA").iterrows():
                        title = f"Must-Show: {row['Scorer']}'s Q{int(row['Period'])} goal ({row['WPA']:+.1f}% WPA)"
                        desc = f"Score: {row['Score']}. High-impact goal."
                        st.markdown(moment_card(title, desc, wpa=row["WPA"], variant="pos"),
                                    unsafe_allow_html=True)

                with ftcol2:
                    # Defensive Review
                    st.markdown("**Defensive Review**")
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
                        st.markdown("**Discipline Review**")
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
            st.markdown("#### Game Comparison")
            st.caption("Compare performance across two games side-by-side.")

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
                st.dataframe(comparison, use_container_width=True, hide_index=True)

                # Visual comparison cards
                stat_cols = [c for c in comparison.columns if c.startswith("UVA_")]
                if stat_cols:
                    st.markdown("#### Visual Comparison")
                    cols = st.columns(min(len(stat_cols), 4))
                    for idx, col_name in enumerate(stat_cols[:8]):
                        label = col_name.replace("UVA_", "").replace("_", " ")
                        vals = comparison[col_name].tolist()
                        if len(vals) == 2:
                            try:
                                v1, v2 = float(vals[0]), float(vals[1])
                                with cols[idx % len(cols)]:
                                    delta = v2 - v1
                                    color = "val-pos" if delta >= 0 else "val-neg"
                                    st.markdown(
                                        metric_card(f"{int(v1)} → {int(v2)}", label, color),
                                        unsafe_allow_html=True
                                    )
                            except (ValueError, TypeError):
                                pass
            else:
                st.info("Could not generate comparison.")

    except Exception as e:
        st.error(f"Error in Game Comparison tab: {e}")
        import traceback
        st.code(traceback.format_exc())
