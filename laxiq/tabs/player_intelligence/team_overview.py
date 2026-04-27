"""
Team Overview tab - Tier breakdown, usage vs efficiency, cumulative scoring, and roster metrics heatmap.
"""
import streamlit as st
import numpy as np
from style import (UVA_BLUE, UVA_ORANGE, UVA_BLUE_25, UVA_ORANGE_25,
                   CYAN as UVA_CYAN, GREEN as UVA_GREEN, MAGENTA as UVA_MAGENTA,
                   LIGHT_BG as LIGHT_GRAY, BORDER as MED_GRAY, TEXT_MUTED as TEXT_GRAY,
                   WHITE)
from .charts import make_usage_efficiency_chart, make_cumulative_points_chart

# extra colors not in style.py
CAV_ORANGE = "#F84C1E"


def render(filtered, sorted_players, all_data):
    """Render the Team Overview tab showing tier distributions, charts, and metrics heatmap."""
    st.markdown("## Team-Wide Impact Overview")

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
            st.markdown(f"<div style='text-align:center;padding:1.2rem;background:{WHITE};border-radius:14px;border:2px solid {color};box-shadow:0 2px 8px rgba(0,0,0,0.05);'>"
                       f"<div style='font-family:Bebas Neue;font-size:2.5rem;color:{text_col};'>{tier_counts[t]}</div>"
                       f"<div style='font-size:0.72rem;color:{TEXT_GRAY};text-transform:uppercase;letter-spacing:1px;font-weight:600;'>{label}</div>"
                       f"<div style='font-size:0.8rem;color:{UVA_BLUE};margin-top:8px;'>{'<br>'.join(tier_players[t])}</div>"
                       f"</div>", unsafe_allow_html=True)

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

    # roster metrics heatmap
    st.markdown("### Roster Metrics Heatmap")
    heatmap_data = []
    heatmap_names = []
    for name, data in sorted_players:
        p = data["player"]
        s = data["scores"]
        if p["gp"] >= 2:
            heatmap_names.append(f"#{p['num']} {name}")
            heatmap_data.append([s["overall"], s["offensive"], s["defensive"],
                               s["possession"], s["efficiency"], s["discipline"]])
    if heatmap_data:
        # normalize each column independently for per-column conditional formatting
        hm_arr = np.array(heatmap_data)
        hm_normalized = np.zeros_like(hm_arr, dtype=float)
        for col_idx in range(hm_arr.shape[1]):
            col_vals = hm_arr[:, col_idx]
            col_min, col_max = col_vals.min(), col_vals.max()
            if col_max > col_min:
                hm_normalized[:, col_idx] = (col_vals - col_min) / (col_max - col_min)
            else:
                hm_normalized[:, col_idx] = 0.5

        # build cell colors per column using the normalized values
        def _hm_color(norm_val):
            """Map 0-1 normalized value to pink → yellow → green."""
            if norm_val < 0.35:
                return "#FCE4EC"   # pink (low)
            elif norm_val < 0.6:
                return "#FFF8E1"   # yellow (mid)
            elif norm_val < 0.8:
                return "#E8F5E9"   # light green
            else:
                return "#C8E6C9"   # green (high)

        col_headers = ["Overall", "Offense", "Defense", "Possession", "Efficiency", "Discipline"]
        n_rows = len(heatmap_names)
        n_cols = len(col_headers)

        # build HTML table for per-column conditional formatting
        table_html = f"<table style='width:100%;border-collapse:collapse;font-family:DM Sans,sans-serif;'>"
        table_html += "<thead><tr>"
        table_html += f"<th style='text-align:left;padding:8px 12px;font-size:0.8rem;color:{TEXT_GRAY};font-weight:600;'>Athlete</th>"
        for h in col_headers:
            table_html += f"<th style='text-align:center;padding:8px 12px;font-size:0.8rem;color:{TEXT_GRAY};font-weight:600;'>{h}</th>"
        table_html += "</tr></thead><tbody>"
        for i in range(n_rows):
            table_html += "<tr>"
            table_html += f"<td style='text-align:left;padding:6px 12px;font-size:0.8rem;font-weight:600;color:{UVA_BLUE};white-space:nowrap;'>{heatmap_names[i]}</td>"
            for j in range(n_cols):
                bg = _hm_color(hm_normalized[i][j])
                val = heatmap_data[i][j]
                table_html += f"<td style='text-align:center;padding:6px 12px;font-size:0.85rem;font-weight:600;color:{UVA_BLUE};background:{bg};'>{val:.0f}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)

    # formula reference — only in Analyst View
    if _analyst_mode:
        st.markdown("---")
        st.markdown(f"""<div style='font-size:0.78rem;color:{TEXT_GRAY};padding:8px 12px;background:{WHITE};border-radius:8px;border:1px solid {MED_GRAY};'>
            <strong style='color:{UVA_BLUE};'>Formula Reference:</strong>&nbsp;&nbsp;
            <strong>Pts/Shot</strong> = PTS / SH &nbsp;·&nbsp;
            <strong>TO Rate</strong> = TO / (SH+TO+DC+GB) &nbsp;·&nbsp;
            <strong>Poss Impact</strong> = GB+DC+CT−TO &nbsp;·&nbsp;
            <strong>Consistency</strong> = 1 − CV(pts/game) &nbsp;·&nbsp;
            <strong>Clutch</strong> = Avg G(wins) / Avg G(losses)
        </div>""", unsafe_allow_html=True)
