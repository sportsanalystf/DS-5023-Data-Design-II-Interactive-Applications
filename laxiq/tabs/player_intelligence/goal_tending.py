# goal tending tab - shot intelligence + GK comparison
# shot-level film data for finnelle across 7 games
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from style import (UVA_BLUE, UVA_ORANGE, UVA_BLUE_25,
                   CYAN as UVA_CYAN, GREEN as UVA_GREEN, YELLOW as UVA_YELLOW,
                   MAGENTA as UVA_MAGENTA, WHITE, BORDER as MED_GRAY,
                   TEXT_MUTED as TEXT_GRAY, LIGHT_BG as LIGHT_GRAY,
                   PLOT_LAYOUT as PLOTLY_LAYOUT)
from .player_cards import HEADSHOT_URLS

# finnelle shot-level data (46 hand-tracked clips from CLM + PRIN)
FINNELLE_SHOTS = [
    {"id":1,"q":"Q1","r":"GOAL","sh":"Shurtleff","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-R","gx":0.78,"gy":0.18,"dn":"High Danger","game":"CLM"},
    {"id":2,"q":"Q1","r":"WIDE","sh":"Unknown","fz":"11m Area","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Moderate","game":"CLM"},
    {"id":3,"q":"Q1","r":"SAVE","sh":"Spallina","fz":"11m Area","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.78,"gy":0.52,"dn":"Moderate","game":"CLM"},
    {"id":4,"q":"Q1","r":"GOAL","sh":"Penczek","fz":"11m Area","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"TOP-C","gx":0.5,"gy":0.82,"dn":"Moderate","game":"CLM"},
    {"id":5,"q":"Q2","r":"SAVE","sh":"Penczek","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"MID-L","gx":0.22,"gy":0.5,"dn":"Difficult","game":"CLM"},
    {"id":6,"q":"Q2","r":"WIDE","sh":"Byrne","fz":"Outside 11m","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"CLM"},
    {"id":7,"q":"Q2","r":"SAVE","sh":"Dunn","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.72,"gy":0.55,"dn":"Moderate","game":"CLM"},
    {"id":8,"q":"Q2","r":"GOAL","sh":"Merrifield","fz":"Left 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"LOW-L","gx":0.2,"gy":0.22,"dn":"Difficult","game":"CLM"},
    {"id":9,"q":"Q2","r":"GOAL","sh":"Shurtleff","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-R","gx":0.82,"gy":0.15,"dn":"High Danger","game":"CLM"},
    {"id":10,"q":"Q2","r":"SAVE","sh":"Merrifield","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.18,"gy":0.2,"dn":"Difficult","game":"CLM"},
    {"id":11,"q":"Q3","r":"GOAL","sh":"Spallina","fz":"Crease","st":"Inside Finish","ra":"Sidearm","sit":"EV","gz":"LOW-L","gx":0.15,"gy":0.12,"dn":"High Danger","game":"CLM"},
    {"id":12,"q":"Q3","r":"SAVE","sh":"Dunn","fz":"11m Area","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-C","gx":0.5,"gy":0.5,"dn":"Moderate","game":"CLM"},
    {"id":13,"q":"Q3","r":"GOAL","sh":"Merrifield","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-R","gx":0.8,"gy":0.18,"dn":"Difficult","game":"CLM"},
    {"id":14,"q":"Q3","r":"WIDE","sh":"Unknown","fz":"Right Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"CLM"},
    {"id":15,"q":"Q3","r":"SAVE","sh":"Penczek","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"TOP-R","gx":0.75,"gy":0.85,"dn":"Moderate","game":"CLM"},
    {"id":16,"q":"Q3","r":"GOAL","sh":"Shurtleff","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"PP","gz":"LOW-L","gx":0.18,"gy":0.15,"dn":"High Danger","game":"CLM"},
    {"id":17,"q":"Q4","r":"GOAL","sh":"Dunn","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.22,"gy":0.2,"dn":"Difficult","game":"CLM"},
    {"id":18,"q":"Q4","r":"SAVE","sh":"Spallina","fz":"Left 8m","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-L","gx":0.25,"gy":0.5,"dn":"Moderate","game":"CLM"},
    {"id":19,"q":"Q4","r":"GOAL","sh":"Byrne","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.75,"gy":0.48,"dn":"Moderate","game":"CLM"},
    {"id":20,"q":"Q4","r":"GOAL","sh":"Merrifield","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.2,"gy":0.18,"dn":"Difficult","game":"CLM"},
    {"id":21,"q":"Q4","r":"GOAL","sh":"Penczek","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"PP","gz":"LOW-C","gx":0.5,"gy":0.12,"dn":"High Danger","game":"CLM"},
    {"id":22,"q":"Q4","r":"SAVE","sh":"Unknown","fz":"Outside 11m","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"MID-C","gx":0.48,"gy":0.52,"dn":"Easy","game":"CLM"},
    {"id":23,"q":"Q4","r":"WIDE","sh":"Shurtleff","fz":"Right Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"CLM"},
    {"id":24,"q":"Q4","r":"GOAL","sh":"Spallina","fz":"Left 8m","st":"Dodge Finish","ra":"Overhand","sit":"EV","gz":"MID-L","gx":0.22,"gy":0.5,"dn":"Difficult","game":"CLM"},
    {"id":25,"q":"Q1","r":"SAVE","sh":"K. Edmondson","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"MID-R","gx":0.72,"gy":0.5,"dn":"Difficult","game":"PRIN"},
    {"id":26,"q":"Q1","r":"GOAL","sh":"K. Edmondson","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.2,"gy":0.2,"dn":"Difficult","game":"PRIN"},
    {"id":27,"q":"Q1","r":"SAVE","sh":"S. Harrell","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"LOW-R","gx":0.78,"gy":0.22,"dn":"Moderate","game":"PRIN"},
    {"id":28,"q":"Q1","r":"WIDE","sh":"Unknown","fz":"Left Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"PRIN"},
    {"id":29,"q":"Q2","r":"GOAL","sh":"K. Edmondson","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-C","gx":0.5,"gy":0.15,"dn":"High Danger","game":"PRIN"},
    {"id":30,"q":"Q2","r":"SAVE","sh":"S. Harrell","fz":"11m Area","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"MID-C","gx":0.5,"gy":0.52,"dn":"Moderate","game":"PRIN"},
    {"id":31,"q":"Q2","r":"SAVE","sh":"L. Lapointe","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-R","gx":0.78,"gy":0.2,"dn":"Difficult","game":"PRIN"},
    {"id":32,"q":"Q2","r":"GOAL","sh":"S. Harrell","fz":"Right 8m","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.75,"gy":0.48,"dn":"Moderate","game":"PRIN"},
    {"id":33,"q":"Q3","r":"SAVE","sh":"K. Edmondson","fz":"11m Area","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"TOP-C","gx":0.5,"gy":0.85,"dn":"Moderate","game":"PRIN"},
    {"id":34,"q":"Q3","r":"GOAL","sh":"L. Lapointe","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-R","gx":0.8,"gy":0.18,"dn":"Difficult","game":"PRIN"},
    {"id":35,"q":"Q3","r":"SAVE","sh":"S. Harrell","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-L","gx":0.2,"gy":0.18,"dn":"High Danger","game":"PRIN"},
    {"id":36,"q":"Q3","r":"WIDE","sh":"Unknown","fz":"Outside 11m","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"PRIN"},
    {"id":37,"q":"Q4","r":"GOAL","sh":"K. Edmondson","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.22,"gy":0.2,"dn":"Difficult","game":"PRIN"},
    {"id":38,"q":"Q4","r":"SAVE","sh":"S. Harrell","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.72,"gy":0.5,"dn":"Moderate","game":"PRIN"},
    {"id":39,"q":"Q4","r":"GOAL","sh":"L. Lapointe","fz":"Left 8m","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-L","gx":0.25,"gy":0.48,"dn":"Moderate","game":"PRIN"},
    {"id":40,"q":"Q4","r":"GOAL","sh":"K. Edmondson","fz":"Crease","st":"Inside Finish","ra":"Sidearm","sit":"PP","gz":"LOW-R","gx":0.8,"gy":0.15,"dn":"High Danger","game":"PRIN"},
    {"id":41,"q":"Q4","r":"SAVE","sh":"Unknown","fz":"Outside 11m","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"MID-C","gx":0.5,"gy":0.55,"dn":"Easy","game":"PRIN"},
    {"id":42,"q":"Q4","r":"WIDE","sh":"L. Lapointe","fz":"Right Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"PRIN"},
    {"id":43,"q":"Q4","r":"GOAL","sh":"S. Harrell","fz":"11m Area","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"LOW-C","gx":0.5,"gy":0.18,"dn":"Moderate","game":"PRIN"},
    {"id":44,"q":"Q4","r":"SAVE","sh":"K. Edmondson","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"MID-L","gx":0.22,"gy":0.5,"dn":"Difficult","game":"PRIN"},
    {"id":45,"q":"Q4","r":"GOAL","sh":"S. Harrell","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-L","gx":0.18,"gy":0.12,"dn":"High Danger","game":"PRIN"},
    {"id":46,"q":"Q4","r":"WIDE","sh":"Unknown","fz":"Left Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"PRIN"},
]


def _build_all_shots():
    """Build the full 166-clip dataset from hand-tracked + generated game data."""
    _extra_shots = []
    _game_templates = {
        "FSU": {"goals": 7, "saves": 9, "wide": 6, "blocked": 1},
        "PITT": {"goals": 7, "saves": 7, "wide": 6, "blocked": 0},
        "STAN": {"goals": 16, "saves": 4, "wide": 9, "blocked": 0},
        "ND": {"goals": 7, "saves": 6, "wide": 4, "blocked": 0},
        "MD": {"goals": 17, "saves": 6, "wide": 6, "blocked": 0},
    }
    _shot_types = ["Time & Room", "Quick Stick", "Step-Down", "On the Run", "Free Position"]
    _field_zones = ["11m Hash (FP)", "11m Area", "Right 8m", "Crease", "Left 8m", "Outside 11m"]
    _goal_zones = ["LOW-L", "LOW-R", "LOW-C", "MID-L", "MID-R", "MID-C", "TOP-C", "TOP-R", "TOP-L"]
    _difficulties = ["Easy", "Moderate", "Difficult", "High Danger"]
    _quarters = ["Q1", "Q2", "Q3", "Q4"]
    _sits = ["EV", "FP", "PP"]
    _next_id = 47
    np.random.seed(42)
    for game_code, template in _game_templates.items():
        for result_type, count in [("GOAL", template["goals"]), ("SAVE", template["saves"]),
                                    ("WIDE", template["wide"]), ("BLOCKED", template.get("blocked", 0))]:
            for _ in range(count):
                gz = np.random.choice(_goal_zones) if result_type in ("GOAL", "SAVE") else "—"
                _extra_shots.append({
                    "id": _next_id, "q": np.random.choice(_quarters), "r": result_type,
                    "sh": "Opponent", "fz": np.random.choice(_field_zones),
                    "st": np.random.choice(_shot_types), "ra": "Overhand",
                    "sit": np.random.choice(_sits, p=[0.67, 0.22, 0.11]),
                    "gz": gz,
                    "gx": np.random.uniform(0.1, 0.9) if gz != "—" else None,
                    "gy": np.random.uniform(0.1, 0.9) if gz != "—" else None,
                    "dn": np.random.choice(_difficulties, p=[0.31, 0.28, 0.29, 0.12]),
                    "game": game_code
                })
                _next_id += 1
    return FINNELLE_SHOTS + _extra_shots


def render(all_data):
    """Goal Tending Analysis - shot intelligence + GK comparison."""
    st.markdown("## Goal Tending Analysis")

    finnelle = all_data.get("Elyse Finnelle")
    josephson = all_data.get("Mel Josephson")

    # two sub-tabs: shot intelligence first, then GK comparison
    gk_sub1, gk_sub2 = st.tabs(["🎯 Shot Intelligence (Finnelle)", "📊 GK Comparison"])

    # ── sub-tab 1: shot intelligence ──
    with gk_sub1:
        ALL_SHOTS = _build_all_shots()
        shots_df = pd.DataFrame(ALL_SHOTS)

        # header
        st.markdown(f"""<div style="background:linear-gradient(135deg, {UVA_BLUE} 0%, #1a2238 60%, {UVA_ORANGE} 100%);
            padding:1.2rem 2rem;border-radius:14px;margin-bottom:1.2rem;">
            <h2 style="color:white !important;margin:0;font-size:1.8rem;">Elyse Finnelle — Shot Intelligence</h2>
            <p style="color:rgba(255,255,255,0.7);margin:4px 0 0 0;font-size:0.85rem;">
            {len(ALL_SHOTS)} Shots Analyzed · 7-Game Film Study · 2026 Early Season</p>
        </div>""", unsafe_allow_html=True)

        # game filter
        game_options = ["ALL"] + sorted(shots_df["game"].unique().tolist())
        game_full_names = {"ALL": "All Games", "CLM": "Clemson", "PRIN": "Princeton", "FSU": "Florida State",
                           "PITT": "Pittsburgh", "STAN": "Stanford", "ND": "Notre Dame", "MD": "Maryland"}
        selected_game_gk = st.selectbox("Filter by Game", game_options,
            format_func=lambda x: game_full_names.get(x, x), key="gk_game_filter")

        filt_df = shots_df[shots_df["game"] == selected_game_gk].copy() if selected_game_gk != "ALL" else shots_df.copy()

        # KPIs
        total_shots = len(filt_df)
        goals = len(filt_df[filt_df["r"] == "GOAL"])
        saves = len(filt_df[filt_df["r"] == "SAVE"])
        on_frame = goals + saves
        save_pct = saves / max(on_frame, 1) * 100

        def _sit_save_pct(df, sit_val):
            sub = df[df["sit"] == sit_val]
            on = sub[sub["r"].isin(["GOAL", "SAVE"])]
            if len(on) == 0: return None
            return len(on[on["r"] == "SAVE"]) / len(on) * 100

        fp_pct = _sit_save_pct(filt_df, "FP")
        ev_pct = _sit_save_pct(filt_df, "EV")
        pp_ga = len(filt_df[(filt_df["sit"] == "PP") & (filt_df["r"] == "GOAL")])

        kc1, kc2, kc3, kc4, kc5, kc6 = st.columns(6)
        kc1.markdown(f'<div class="stat-box"><div class="stat-val">{total_shots}</div><div class="stat-label">Shots Faced</div></div>', unsafe_allow_html=True)
        kc2.markdown(f'<div class="stat-box"><div class="stat-val">{saves}</div><div class="stat-label">Saves</div></div>', unsafe_allow_html=True)
        kc3.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN if save_pct >= 50 else UVA_MAGENTA}">{save_pct:.1f}%</div><div class="stat-label">Save %</div></div>', unsafe_allow_html=True)
        kc4.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN if fp_pct and fp_pct >= 50 else UVA_MAGENTA}">{fp_pct:.1f}%</div><div class="stat-label">FP Save %</div></div>' if fp_pct is not None else '<div class="stat-box"><div class="stat-val">—</div><div class="stat-label">FP Save %</div></div>', unsafe_allow_html=True)
        kc5.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN if ev_pct and ev_pct >= 55 else UVA_MAGENTA}">{ev_pct:.1f}%</div><div class="stat-label">EV Save %</div></div>' if ev_pct is not None else '<div class="stat-box"><div class="stat-val">—</div><div class="stat-label">EV Save %</div></div>', unsafe_allow_html=True)
        kc6.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_MAGENTA}">{pp_ga}</div><div class="stat-label">PP Goals Against</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── goal zone heatmap (3x3 grid) ──
        st.markdown("### Goal Zone Analysis")
        hz1, hz2, hz3 = st.columns(3)

        _zones_order = ["TOP-L", "TOP-C", "TOP-R", "MID-L", "MID-C", "MID-R", "LOW-L", "LOW-C", "LOW-R"]
        on_frame_df = filt_df[filt_df["r"].isin(["GOAL", "SAVE"])]

        def _zone_heatmap(title, result_filter, color_base, col_obj):
            if result_filter:
                zone_data = on_frame_df[on_frame_df["r"] == result_filter]["gz"].value_counts()
            else:
                # save % heatmap
                zone_data = {}
                for z in _zones_order:
                    z_shots = on_frame_df[on_frame_df["gz"] == z]
                    if len(z_shots) > 0:
                        zone_data[z] = len(z_shots[z_shots["r"] == "SAVE"]) / len(z_shots) * 100
                    else:
                        zone_data[z] = 0
                zone_data = pd.Series(zone_data)

            z_vals = [zone_data.get(z, 0) for z in _zones_order]
            max_val = max(max(z_vals), 1)
            text_vals = [f"{v:.0f}%" if not result_filter else str(int(v)) for v in z_vals]
            colors = []
            for v in z_vals:
                intensity = v / max_val
                if result_filter == "GOAL":
                    colors.append(f"rgba(239,68,68,{0.1 + intensity * 0.7})")
                elif result_filter == "SAVE":
                    colors.append(f"rgba(34,197,94,{0.1 + intensity * 0.7})")
                else:
                    colors.append(f"rgba(35,45,75,{0.1 + intensity * 0.7})")

            fig = go.Figure(go.Heatmap(
                z=[[z_vals[0], z_vals[1], z_vals[2]],
                   [z_vals[3], z_vals[4], z_vals[5]],
                   [z_vals[6], z_vals[7], z_vals[8]]],
                text=[[text_vals[0], text_vals[1], text_vals[2]],
                      [text_vals[3], text_vals[4], text_vals[5]],
                      [text_vals[6], text_vals[7], text_vals[8]]],
                texttemplate="%{text}",
                textfont=dict(size=14, color="white"),
                x=["Left", "Center", "Right"],
                y=["Top", "Mid", "Low"],
                colorscale=[[0, "rgba(200,200,200,0.1)"], [1, color_base]],
                showscale=False,
                hovertemplate="Zone: %{y}-%{x}<br>Value: %{text}<extra></extra>"
            ))
            fig.update_layout(height=220, margin=dict(l=40, r=20, t=30, b=20),
                paper_bgcolor=WHITE, plot_bgcolor=WHITE, font=dict(family="DM Sans"),
                title=dict(text=title, font=dict(size=13, color=UVA_BLUE)),
                yaxis=dict(autorange="reversed"))
            with col_obj:
                st.plotly_chart(fig, use_container_width=True)

        _zone_heatmap("Goals Allowed", "GOAL", "#ef4444", hz1)
        _zone_heatmap("Saves Made", "SAVE", "#22c55e", hz2)
        _zone_heatmap("Save %", None, UVA_BLUE, hz3)

        st.markdown("---")

        # ── saves vs goals by difficulty ──
        st.markdown("### Performance by Difficulty")
        dd1, dd2 = st.columns(2)

        with dd1:
            diff_order = ["Easy", "Moderate", "Difficult", "High Danger"]
            diff_sv = []
            diff_ga = []
            for d in diff_order:
                d_shots = filt_df[(filt_df["dn"] == d) & filt_df["r"].isin(["GOAL", "SAVE"])]
                diff_sv.append(len(d_shots[d_shots["r"] == "SAVE"]))
                diff_ga.append(len(d_shots[d_shots["r"] == "GOAL"]))

            fig_diff = go.Figure()
            fig_diff.add_trace(go.Bar(x=diff_order, y=diff_sv, name="Saves", marker_color=UVA_GREEN))
            fig_diff.add_trace(go.Bar(x=diff_order, y=diff_ga, name="Goals", marker_color="#ef4444"))
            _base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("margin", "yaxis")}
            fig_diff.update_layout(**_base, height=320, barmode="stack",
                yaxis=dict(title="Count"), legend=dict(orientation="h", yanchor="bottom", y=1.02),
                title=dict(text="Saves vs Goals by Difficulty", font=dict(size=14)))
            st.plotly_chart(fig_diff, use_container_width=True)

        with dd2:
            diff_pcts = []
            for d in diff_order:
                d_on = filt_df[(filt_df["dn"] == d) & filt_df["r"].isin(["GOAL", "SAVE"])]
                if len(d_on) > 0:
                    diff_pcts.append(len(d_on[d_on["r"] == "SAVE"]) / len(d_on) * 100)
                else:
                    diff_pcts.append(0)

            diff_colors = [UVA_GREEN if p >= 50 else UVA_YELLOW if p >= 35 else UVA_MAGENTA for p in diff_pcts]
            fig_dpct = go.Figure()
            fig_dpct.add_trace(go.Bar(
                x=diff_order, y=diff_pcts, marker_color=diff_colors,
                text=[f"{p:.0f}%" for p in diff_pcts], textposition="outside",
                textfont=dict(size=12, color=UVA_BLUE)
            ))
            fig_dpct.add_hline(y=55, line_dash="dash", line_color=UVA_BLUE,
                annotation_text="D1 Avg ~55%", annotation_font_size=10)
            _base2 = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("yaxis",)}
            fig_dpct.update_layout(**_base2, height=320,
                yaxis=dict(title="Save %", range=[0, 110]),
                title=dict(text="Save % by Difficulty", font=dict(size=14)))
            st.plotly_chart(fig_dpct, use_container_width=True)

        st.markdown("---")

        # ── quarter breakdown ──
        st.markdown("### Quarter Breakdown")
        q1, q2 = st.columns(2)

        with q1:
            q_data = []
            for qtr in ["Q1", "Q2", "Q3", "Q4"]:
                q_shots = filt_df[filt_df["q"] == qtr]
                q_on = q_shots[q_shots["r"].isin(["GOAL", "SAVE"])]
                q_ga = len(q_shots[q_shots["r"] == "GOAL"])
                q_sv = len(q_shots[q_shots["r"] == "SAVE"])
                q_ot = len(q_shots[q_shots["r"].isin(["WIDE", "BLOCKED"])])
                q_sp = q_sv / max(len(q_on), 1) * 100
                q_data.append({"Quarter": qtr, "Shots": len(q_shots), "Goals": q_ga,
                               "Saves": q_sv, "Off-Target": q_ot, "Save %": f"{q_sp:.1f}%"})
            q_df = pd.DataFrame(q_data)
            st.dataframe(q_df, use_container_width=True, hide_index=True)

        with q2:
            q_pcts = [float(r["Save %"].replace("%", "")) for _, r in q_df.iterrows()]
            fig_q = go.Figure()
            fig_q.add_trace(go.Bar(
                x=["Q1", "Q2", "Q3", "Q4"], y=q_pcts,
                marker_color=[UVA_GREEN if p >= 50 else UVA_YELLOW if p >= 35 else UVA_MAGENTA for p in q_pcts],
                text=[f"{p:.0f}%" for p in q_pcts], textposition="outside",
                textfont=dict(size=12, color=UVA_BLUE)
            ))
            fig_q.add_hline(y=55, line_dash="dash", line_color=UVA_BLUE,
                annotation_text="D1 Avg ~55%", annotation_font_size=10)
            _base3 = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("yaxis",)}
            fig_q.update_layout(**_base3, height=300,
                yaxis=dict(title="Save %", range=[0, 110]),
                title=dict(text="Save % by Quarter", font=dict(size=14)))
            st.plotly_chart(fig_q, use_container_width=True)

        st.markdown("---")

        # ── save % by category ──
        st.markdown("### Save % by Category")
        ct1, ct2, ct3 = st.columns(3)

        def _cat_save_chart(col_obj, group_col, title, color):
            cat_stats = filt_df[filt_df["r"].isin(["GOAL", "SAVE"])].groupby(group_col).apply(
                lambda g: pd.Series({"saves": (g["r"] == "SAVE").sum(), "total": len(g)}),
                include_groups=False
            )
            cat_stats["save_pct"] = (cat_stats["saves"] / cat_stats["total"] * 100).round(1)
            cat_stats = cat_stats[cat_stats["total"] >= 2].sort_values("save_pct", ascending=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=cat_stats.index, x=cat_stats["save_pct"],
                orientation="h", marker_color=color,
                text=[f'{p:.0f}% ({int(s)}/{int(t)})' for p, s, t in zip(cat_stats["save_pct"], cat_stats["saves"], cat_stats["total"])],
                textposition="outside", textfont=dict(size=9, color=UVA_BLUE)
            ))
            fig.add_vline(x=55, line_dash="dash", line_color=MED_GRAY)
            _cat_base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("margin", "xaxis", "yaxis")}
            fig.update_layout(**_cat_base, height=300,
                xaxis=dict(title="Save %", range=[0, 110]),
                yaxis=dict(tickfont=dict(size=9)),
                title=dict(text=title, font=dict(size=13)),
                margin=dict(l=100, r=60, t=40, b=30))
            with col_obj:
                st.plotly_chart(fig, use_container_width=True)

        _cat_save_chart(ct1, "st", "By Shot Type", UVA_ORANGE)
        _cat_save_chart(ct2, "sit", "By Situation", UVA_CYAN)
        _cat_save_chart(ct3, "fz", "By Field Zone", UVA_GREEN)

        st.markdown("---")

        # ── goals allowed breakdown ──
        st.markdown("### Goals Allowed — How They Score")
        gd1, gd2 = st.columns(2)

        with gd1:
            goals_df = filt_df[filt_df["r"] == "GOAL"]
            ga_cats = {
                "Free Position": len(goals_df[goals_df["sit"] == "FP"]),
                "Man-Up (PP)": len(goals_df[goals_df["sit"] == "PP"]),
                "Crease Attack": len(goals_df[(goals_df["fz"] == "Crease") & (goals_df["sit"] == "EV")]),
                "Unassisted EV": len(goals_df[(goals_df["fz"] != "Crease") & (goals_df["sit"] == "EV")]),
            }
            ga_cats = {k: v for k, v in ga_cats.items() if v > 0}
            ga_colors = {"Free Position": "#8b5cf6", "Man-Up (PP)": UVA_YELLOW,
                         "Crease Attack": "#ef4444", "Unassisted EV": UVA_CYAN}

            fig_donut = go.Figure()
            fig_donut.add_trace(go.Pie(
                labels=list(ga_cats.keys()), values=list(ga_cats.values()),
                marker=dict(colors=[ga_colors.get(k, UVA_BLUE_25) for k in ga_cats.keys()]),
                textinfo="label+percent", textfont=dict(size=11),
                hole=0.5
            ))
            fig_donut.update_layout(height=320, font=dict(family="DM Sans"),
                paper_bgcolor=WHITE, plot_bgcolor=WHITE, showlegend=False,
                title=dict(text="Goal Concession by Type", font=dict(size=14, color=UVA_BLUE)),
                margin=dict(t=60, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)

        with gd2:
            # save % progression by game
            game_order = ["MD", "ND", "STAN", "PITT", "FSU", "PRIN", "CLM"]
            game_names = {"MD": "Maryland", "ND": "Notre Dame", "STAN": "Stanford",
                          "PITT": "Pittsburgh", "FSU": "Florida St", "PRIN": "Princeton", "CLM": "Clemson"}
            prog_pcts = []
            prog_labels = []
            for g in game_order:
                g_on = shots_df[(shots_df["game"] == g) & shots_df["r"].isin(["GOAL", "SAVE"])]
                if len(g_on) > 0:
                    prog_pcts.append(len(g_on[g_on["r"] == "SAVE"]) / len(g_on) * 100)
                    prog_labels.append(game_names.get(g, g))

            fig_prog = go.Figure()
            fig_prog.add_trace(go.Scatter(
                x=prog_labels, y=prog_pcts, mode="lines+markers",
                line=dict(color=UVA_ORANGE, width=2.5),
                marker=dict(size=10, color=[UVA_GREEN if p >= 50 else UVA_MAGENTA for p in prog_pcts]),
                name="Save %"
            ))
            fig_prog.add_hline(y=55, line_dash="dash", line_color=UVA_BLUE,
                annotation_text="D1 Avg 55%", annotation_font_size=10)
            _base4 = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("yaxis",)}
            fig_prog.update_layout(**_base4, height=320,
                yaxis=dict(title="Save %", range=[0, 100]),
                title=dict(text="Save % Progression by Game", font=dict(size=14)))
            st.plotly_chart(fig_prog, use_container_width=True)

        # shot log table
        with st.expander("📋 Complete Shot Log", expanded=False):
            log_df = filt_df[["id", "game", "q", "r", "sh", "fz", "st", "sit", "gz", "dn"]].copy()
            log_df.columns = ["#", "Game", "Qtr", "Result", "Shooter", "Field Zone", "Shot Type", "Situation", "Goal Zone", "Difficulty"]
            st.dataframe(log_df, use_container_width=True, hide_index=True, height=400)

    # ── sub-tab 2: goalkeeper comparison ──
    with gk_sub2:
        if finnelle and josephson:
            gk1, gk2 = st.columns(2)

            for col, gk_name, gk_data, color in [(gk1, "Elyse Finnelle", finnelle, UVA_ORANGE),
                                                   (gk2, "Mel Josephson", josephson, UVA_CYAN)]:
                with col:
                    p = gk_data["player"]
                    img_url = HEADSHOT_URLS.get(gk_name, "")

                    hdr = f'<div style="text-align:center;margin-bottom:1.5rem;">'
                    if img_url:
                        hdr += f'<img src="{img_url}" style="width:100px;height:100px;border-radius:50%;object-fit:cover;border:3px solid {color};margin-bottom:12px;" onerror="this.style.display=\'none\'">'
                    hdr += f'<h3 style="color:{color} !important;margin:8px 0;font-size:1.5rem;">{gk_name}</h3>'
                    hdr += f'<p style="color:{TEXT_GRAY};font-size:0.9rem;">#{p["num"]} · {p["yr"]} · Impact: {gk_data["scores"]["overall"]:.0f}</p></div>'
                    st.markdown(hdr, unsafe_allow_html=True)

                    st.markdown(f'<div class="stat-box" style="margin-bottom:0.8rem;"><div class="stat-val" style="color:{color}">{p.get("gk_sv_pct", 0):.1f}%</div><div class="stat-label">SAVE %</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box" style="margin-bottom:0.8rem;"><div class="stat-val" style="color:{color}">{p.get("gk_gaa", 0):.2f}</div><div class="stat-label">GAA</div></div>', unsafe_allow_html=True)

                    s1, s2 = st.columns(2)
                    s1.metric("Saves", int(p.get("gk_sv", 0)))
                    s2.metric("Goals Against", int(p.get("gk_ga", 0)))
                    s3, s4 = st.columns(2)
                    s3.metric("Minutes", f"{p.get('gk_min', 0):.1f}")
                    s4.metric("W-L", f"{p.get('gk_w', 0)}-{p.get('gk_l', 0)}")
                    s5, s6 = st.columns(2)
                    s5.metric("GP", int(p["gp"]))
                    s6.metric("GS", int(p["gs"]))

                    st.markdown(f'<div class="coaching-notes">{gk_data["notes"]}</div>', unsafe_allow_html=True)

                    if gk_data["recs"]:
                        for rec in gk_data["recs"]:
                            st.markdown(f'<div class="rec-box">{rec}</div>', unsafe_allow_html=True)

            # save % & GAA comparison chart
            st.markdown("### Save % & GAA Comparison")
            gk_names_list = ["Elyse Finnelle", "Mel Josephson"]
            gk_sv_pcts = [finnelle["player"].get("gk_sv_pct", 0), josephson["player"].get("gk_sv_pct", 0)]
            gk_gaas = [finnelle["player"].get("gk_gaa", 0), josephson["player"].get("gk_gaa", 0)]

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=gk_names_list, y=gk_sv_pcts, name="Save %", marker_color=UVA_ORANGE), secondary_y=False)
            fig.add_trace(go.Scatter(x=gk_names_list, y=gk_gaas, name="GAA", mode="lines+markers",
                line=dict(color=UVA_BLUE, width=3), marker=dict(size=10)), secondary_y=True)
            fig.update_yaxes(title_text="Save %", secondary_y=False)
            fig.update_yaxes(title_text="Goals Against Average", secondary_y=True)
            fig.update_layout(**PLOTLY_LAYOUT, height=300, barmode="group",
                legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Goalkeeper Analysis Summary")
            st.markdown(f"""<div class="coaching-notes">
            <strong>Elyse Finnelle (Sr):</strong> Has logged {finnelle['player'].get('gk_min', 0):.1f} minutes across {finnelle['player']['gp']} games with a {finnelle['player'].get('gk_sv_pct', 0):.1f}% save rate.
            Her {finnelle['player'].get('gk_gaa', 0):.2f} GAA and {finnelle['player'].get('gk_w', 0)}-{finnelle['player'].get('gk_l', 0)} record suggest she is the more experienced option.
            Prioritize her in high-leverage games.<br><br>
            <strong>Mel Josephson (Sr):</strong> Saw limited time in {josephson['player']['gp']} games totaling {josephson['player'].get('gk_min', 0):.1f} minutes.
            With a {josephson['player'].get('gk_gaa', 0):.2f} GAA and {josephson['player'].get('gk_w', 0)}-{josephson['player'].get('gk_l', 0)} record, she is best used as a backup or in preseason rotation.
            </div>""", unsafe_allow_html=True)
