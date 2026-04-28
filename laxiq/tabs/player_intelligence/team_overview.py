"""
Team Overview tab - Tier breakdown, usage vs efficiency, cumulative scoring, and roster metrics.
"""
import streamlit as st
import pandas as pd
from style import (UVA_BLUE, UVA_ORANGE, UVA_BLUE_25, UVA_ORANGE_25,
                   CYAN as UVA_CYAN, GREEN as UVA_GREEN, MAGENTA as UVA_MAGENTA,
                   LIGHT_BG as LIGHT_GRAY, BORDER as MED_GRAY, TEXT_MUTED as TEXT_GRAY,
                   WHITE, section_header)
from .charts import make_usage_efficiency_chart, make_cumulative_points_chart

# extra colors not in style.py
CAV_ORANGE = "#F84C1E"


def render(filtered, sorted_players, all_data):
    """Render the Team Overview tab showing tier distributions, charts, and metrics heatmap."""
    st.markdown(section_header("Team-Wide Impact Overview"), unsafe_allow_html=True)

    # tier breakdown cards
    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    tier_players = {1: [], 2: [], 3: [], 4: []}
    for name, data in filtered.items():
        t = data["tier_num"]
        tier_counts[t] += 1
        tier_players[t].append(name)

    tc1, tc2, tc3, tc4 = st.columns(4)
    for col, t, label, color in [(tc1, 1, "Program Drivers", CAV_ORANGE), (tc2, 2, "System Amplifiers", UVA_CYAN),
                                  (tc3, 3, "Situational Specialists", UVA_GREEN), (tc4, 4, "Developmental", MED_GRAY)]:
        text_col = UVA_BLUE if color == MED_GRAY else color
        with col:
            st.metric(label, tier_counts[t])
            st.caption(", ".join(tier_players[t]))

    # hide advanced charts in Coach View
    _analyst_mode = st.session_state.get("view_mode", "Analyst View") == "Analyst View"

    if _analyst_mode:
        st.markdown("")
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("### Usage vs Efficiency")
            ue_fig = make_usage_efficiency_chart(filtered)
            if ue_fig:
                st.plotly_chart(ue_fig, use_container_width=True)
        with chart_col2:
            st.markdown("### Cumulative Scoring")
            cum_fig = make_cumulative_points_chart(filtered)
            if cum_fig:
                st.plotly_chart(cum_fig, use_container_width=True)
    else:
        # Coach View — show concise summary instead of scatter/bar charts
        st.info("📋 **Coach View** — Switch to Analyst View in the sidebar to see Usage vs Efficiency and Cumulative Scoring charts.")

    # roster metrics table
    st.markdown(section_header("Roster Metrics"), unsafe_allow_html=True)
    heatmap_rows = []
    for name, data in sorted_players:
        p = data["player"]
        s = data["scores"]
        if p["gp"] >= 2:
            heatmap_rows.append({
                "Athlete": f"#{p['num']} {name}",
                "Overall": round(s["overall"]),
                "Offense": round(s["offensive"]),
                "Defense": round(s["defensive"]),
                "Possession": round(s["possession"]),
                "Efficiency": round(s["efficiency"]),
                "Discipline": round(s["discipline"]),
            })
    if heatmap_rows:
        hm_df = pd.DataFrame(heatmap_rows)
        st.dataframe(hm_df, use_container_width=True, hide_index=True)

    # formula reference — only in Analyst View
    if _analyst_mode:
        st.markdown("---")
        st.caption("**Formula Reference:** Pts/Shot = PTS / SH · TO Rate = TO / (SH+TO+DC+GB) · Poss Impact = GB+DC+CT−TO · Consistency = 1 − CV(pts/game)")
