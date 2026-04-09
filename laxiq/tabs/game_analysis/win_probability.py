# win probability & WPA tab
import streamlit as st
import re
import plotly.graph_objects as go
from style import *
from analytics import *


def render(sheets, game, info, home_team, opp, hs, aws, result, quarter_scores):
    """Render the win probability and WPA analysis tab."""
    try:
        pbp = sheets.get("Play_By_Play")
        scoring_summary = sheets.get("Scoring_Summary")

        # chart theme constants
        # plot area is dark; but titles, axis labels, legends sit on the
        # light page background (transparent paper), so they must be dark.
        DARK_BG = "#2A3142"
        GRID_DARK = "rgba(255,255,255,0.08)"
        LABEL_DARK = "#232D4B"       # dark navy for text on light bg
        LABEL_MED  = "#4A5568"       # medium gray-blue for secondary text

        # had to handle the case where PBP data isn't available
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
                # wp chart - this is the main visualization
                # build narrative title from game story
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
                        ct_match = re.search(r'\(caused by ([^)]+)\)', play_text, re.IGNORECASE)
                        if ct_match:
                            lines.append(f"Caused by: {ct_match.group(1).strip()}")
                        elif row.get("TO_Detail"):
                            lines.append(row["TO_Detail"])
                    wp_pct = f"WP: {row['WP']:.1f}%"
                    delta = f"WPA: {row['WP_Delta']:+.1f}%"
                    lines.append(f"{wp_pct} | {delta}")
                    return "<br>".join(lines)

                timeline["Hover"] = timeline.apply(build_hover, axis=1)

                # event filter control
                all_event_types = [et for et in EVENT_STYLE if et in timeline["Event_Type"].values]
                default_on = ["Goal", "Draw Control", "Turnover",
                              "Save", "Shot", "Ground Ball", "Clear", "Card",
                              "Free Position", "Blocked Shot", "Shot Clock Violation"]
                selected_types = st.multiselect(
                    "Event types to display", options=all_event_types,
                    default=[t for t in default_on if t in all_event_types],
                    help="Toggle which play types appear as markers", key="wp_event_filter"
                )

                # build dark-themed WP chart
                fig = go.Figure()

                # main WP line — orange, smooth spline
                fig.add_trace(go.Scatter(
                    x=timeline["Minutes_Elapsed"], y=timeline["WP"],
                    mode="lines", name="Win Probability",
                    line=dict(color=UVA_ORANGE, width=2.5, shape="spline",
                              smoothing=0.8),
                    hoverinfo="skip", showlegend=False,
                ))

                # building the event markers for the chart
                for etype in selected_types:
                    style = EVENT_STYLE.get(etype, {"color": "#999", "symbol": "circle", "size": 8})
                    subset = timeline[timeline["Event_Type"] == etype]
                    if subset.empty:
                        continue
                    uva_ev = subset[subset["Is_Home_Event"] == True]
                    opp_ev = subset[subset["Is_Home_Event"] != True]

                    # color based on whether it helped or hurt UVA
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
                # quarter dividers
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

                # summary metrics row
                goals_only = timeline[timeline["Event_Type"] == "Goal"]
                uva_goals = goals_only[goals_only["Is_Home_Event"] == True]
                opp_goals = goals_only[goals_only["Is_Home_Event"] != True]
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.markdown(metric_card(f"{timeline['WP'].min():.0f}%", "Lowest WP"), unsafe_allow_html=True)
                mc2.markdown(metric_card(f"{timeline['WP'].max():.0f}%", "Highest WP"), unsafe_allow_html=True)
                mc3.markdown(metric_card(str(hs), "UVA Goals"), unsafe_allow_html=True)
                mc4.markdown(metric_card(str(aws), "OPP Goals"), unsafe_allow_html=True)

                # event impact bar chart — UVA perspective only
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
                    # sort by absolute impact descending
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
