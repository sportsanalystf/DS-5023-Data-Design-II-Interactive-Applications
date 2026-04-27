"""
Player Comparison tab - Head-to-head comparison of two players with radar charts and stat tables.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from style import (UVA_BLUE, UVA_ORANGE, UVA_BLUE_25,
                   BORDER as MED_GRAY, TEXT_MUTED as TEXT_GRAY)
from .player_cards import HEADSHOT_URLS

# get PLOTLY_LAYOUT from charts module
from .charts import PLOTLY_LAYOUT


def _warn_duplicate_player():
    """on_change callback — warn user if both dropdowns select the same player."""
    if (st.session_state.get("compare_player_1")
            and st.session_state.get("compare_player_2")
            and st.session_state["compare_player_1"] == st.session_state["compare_player_2"]):
        st.session_state["_cmp_dup_warn"] = True
    else:
        st.session_state["_cmp_dup_warn"] = False


def render(sorted_players, all_data):
    """Render the Player Comparison tab for head-to-head analysis of two players."""
    st.markdown("## Head-to-Head Comparison")

    comp_names = [n for n, _ in sorted_players]
    comp_options = [f"#{all_data[n]['player']['num']} {n} ({all_data[n]['player']['pos']})" for n in comp_names]
    if len(comp_options) < 2:
        st.warning("Need at least 2 players for comparison.")
    else:
        c1, c2 = st.columns(2)
        # warn if same player picked twice
        with c1: p1_sel = st.selectbox("Player 1", comp_options, index=0,
                                        key="compare_player_1", on_change=_warn_duplicate_player)
        with c2: p2_sel = st.selectbox("Player 2", comp_options, index=min(1, len(comp_options)-1),
                                        key="compare_player_2", on_change=_warn_duplicate_player)

        # show duplicate warning via callback flag
        if st.session_state.get("_cmp_dup_warn"):
            st.warning("⚠️ You've selected the same player in both slots. Choose two different players for a meaningful comparison.")

        p1_name = comp_names[comp_options.index(p1_sel)]
        p2_name = comp_names[comp_options.index(p2_sel)]
        d1, d2 = all_data[p1_name], all_data[p2_name]

        shared_cats = ["Offense", "Defense", "Possession", "Efficiency", "Discipline"]
        shared_keys = ["offensive", "defensive", "possession", "efficiency", "discipline"]

        # side-by-side radar charts
        rc1, rc2 = st.columns(2)
        for col, pname, pdata, color in [(rc1, p1_name, d1, UVA_ORANGE), (rc2, p2_name, d2, UVA_BLUE)]:
            with col:
                img_url = HEADSHOT_URLS.get(pname, "")
                hdr = f'<div style="text-align:center;">'
                if img_url:
                    hdr += f'<img src="{img_url}" style="width:90px;height:90px;border-radius:50%;object-fit:cover;border:3px solid {color};margin-bottom:8px;" onerror="this.style.display=\'none\'">'
                hdr += f'<h3 style="color:{color} !important;margin:0;">{pname}</h3>'
                hdr += f'<p style="color:{TEXT_GRAY};font-size:0.85rem;">#{pdata["player"]["num"]} · {pdata["player"]["pos"]} · {pdata["player"]["yr"]} · Impact: {pdata["scores"]["overall"]:.0f}</p></div>'
                st.markdown(hdr, unsafe_allow_html=True)

                vals = [pdata["scores"][k] for k in shared_keys]
                vals = [max(0, min(v, 100)) for v in vals]
                vals.append(vals[0])
                cats_closed = shared_cats + [shared_cats[0]]
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=vals, theta=cats_closed, fill='toself',
                    fillcolor=f'rgba({",".join(str(int(color[i:i+2], 16)) for i in (1,3,5))},0.15)',
                    line=dict(color=color, width=2.5), marker=dict(size=6, color=color)))
                fig.update_layout(**PLOTLY_LAYOUT, polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor=MED_GRAY),
                    angularaxis=dict(gridcolor=MED_GRAY, tickfont=dict(size=10, color=TEXT_GRAY))),
                    showlegend=False, height=280)
                st.plotly_chart(fig, use_container_width=True, key=f"cmp_r_{pname}")

        # grouped bar chart comparing impact scores
        v1 = [d1["scores"][k] for k in shared_keys]
        v2 = [d2["scores"][k] for k in shared_keys]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=shared_cats, y=v1, name=p1_name, marker_color=UVA_ORANGE))
        fig.add_trace(go.Bar(x=shared_cats, y=v2, name=p2_name, marker_color=UVA_BLUE))
        fig.update_layout(**PLOTLY_LAYOUT, height=320, barmode="group",
            yaxis=dict(gridcolor=MED_GRAY, range=[0, 100]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

        # raw stats table
        st.markdown("### Raw Stats Comparison")
        stat_keys = ["gp", "g", "a", "pts", "sh", "sh_pct", "sog_pct", "gb", "dc", "to", "ct"]
        stat_labels = ["GP", "Goals", "Assists", "Points", "Shots", "SH%", "SOG%", "GB", "DC", "TO", "CT"]
        comp_df = pd.DataFrame({
            "Stat": stat_labels,
            p1_name: [d1["player"].get(k, "—") for k in stat_keys],
            p2_name: [d2["player"].get(k, "—") for k in stat_keys],
        })
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
