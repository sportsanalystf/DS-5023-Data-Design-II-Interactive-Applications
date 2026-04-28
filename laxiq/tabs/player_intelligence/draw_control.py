# draw control center - UVA draw analysis + UVA scouting report
# uses same clip-level film study format but from our perspective
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from style import (UVA_BLUE, UVA_ORANGE, UVA_BLUE_25, UVA_ORANGE_25,
                   CYAN as UVA_CYAN, GREEN as UVA_GREEN, YELLOW as UVA_YELLOW,
                   MAGENTA as UVA_MAGENTA, TEAL as UVA_TEAL,
                   WHITE, BORDER as MED_GRAY, TEXT_MUTED as TEXT_GRAY,
                   PLOT_LAYOUT as PLOTLY_LAYOUT)
from .charts import make_draw_control_chart, make_rolling_avg_chart

# UVA draw control scouting data (32 clips from film study)
# primary: Galica #5, backup: Dinardo #4, tertiary: Reilly #23
UVA_DRAW_CLIPS = [
    {"id":1,"p":"#5","tech":"Forward Clamp","dir":"Fwd-Right","clk":2,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Right Wing","wing":"#4","ttp":2.8,"spd":"Fast"},
    {"id":2,"p":"#5","tech":"Forward Clamp","dir":"Fwd-Right","clk":2,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Right Wing","wing":"#4","ttp":3.1,"spd":"Avg"},
    {"id":3,"p":"#5","tech":"Forward Clamp","dir":"Fwd-Left","clk":10,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"#23","ttp":3.0,"spd":"Fast"},
    {"id":4,"p":"#5","tech":"Forward Clamp + DL","dir":"Fwd-Right","clk":2,"dist":"Med","ht":"Bounce","out":"Win","poss":"Wing","who":"Right Wing","wing":"#4","ttp":3.5,"spd":"Avg"},
    {"id":5,"p":"#5","tech":"Physical Clamp","dir":"Fwd-Right","clk":3,"dist":"Short","ht":"Ground","out":"Win","poss":"Scramble","who":"Draw Taker","wing":"-","ttp":4.0,"spd":"Slow"},
    {"id":6,"p":"#5","tech":"Delayed Clamp","dir":"Fwd-Right","clk":2,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Right Wing","wing":"#4","ttp":3.2,"spd":"Avg"},
    {"id":7,"p":"#5","tech":"Draw Right Clamp","dir":"Right","clk":3,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Right Wing","wing":"#4","ttp":2.7,"spd":"Fast"},
    {"id":8,"p":"#5","tech":"Forward Clamp","dir":"Backward","clk":6,"dist":"Med","ht":"Bounce","out":"Win","poss":"Wing","who":"Left Wing","wing":"-","ttp":4.5,"spd":"Slow"},
    {"id":9,"p":"#5","tech":"Backward Push","dir":"Back-Right","clk":4,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Right Wing","wing":"-","ttp":3.4,"spd":"Avg"},
    {"id":10,"p":"#5","tech":"Backward Push","dir":"Back-Right","clk":4,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Right Wing","wing":"-","ttp":3.6,"spd":"Avg"},
    {"id":11,"p":"#5","tech":"Go-With Grab","dir":"Forward","clk":12,"dist":"Short","ht":"Air","out":"Win","poss":"Clean","who":"Draw Taker","wing":"-","ttp":1.8,"spd":"Fast"},
    {"id":12,"p":"#5","tech":"Directed Forward","dir":"Forward","clk":12,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Right Wing","wing":"#4","ttp":2.0,"spd":"Fast"},
    {"id":13,"p":"#5","tech":"Forward Power","dir":"Fwd-Right","clk":2,"dist":"Long","ht":"Air","out":"Win","poss":"Wing","who":"Right Wing","wing":"-","ttp":3.8,"spd":"Avg"},
    {"id":14,"p":"#5","tech":"Open Up","dir":"Fwd-Left","clk":10,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Left Wing","wing":"#23","ttp":2.4,"spd":"Fast"},
    {"id":15,"p":"#5","tech":"Open Up","dir":"Forward","clk":12,"dist":"Med","ht":"Air","out":"Win","poss":"Wing","who":"Draw Taker","wing":"-","ttp":2.9,"spd":"Fast"},
    {"id":16,"p":"#5","tech":"Open Up","dir":"Right","clk":3,"dist":"Med","ht":"Air","out":"Win","poss":"Wing","who":"Right Wing","wing":"-","ttp":3.1,"spd":"Avg"},
    {"id":17,"p":"#5","tech":"Aggressive Clamp","dir":"Forward","clk":12,"dist":"Short","ht":"Ground","out":"Win","poss":"Scramble","who":"Ground Ball","wing":"-","ttp":4.8,"spd":"Slow"},
    {"id":18,"p":"#5","tech":"Go-With Pop","dir":"Forward","clk":12,"dist":"Short","ht":"Air","out":"50-50","poss":"Scramble","who":"Scramble","wing":"-","ttp":5.5,"spd":"Slow"},
    {"id":19,"p":"#5","tech":"Fwd Clamp (COUNTERED)","dir":"Fwd-Right","clk":2,"dist":"Short","ht":"Ground","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
    {"id":20,"p":"#5","tech":"Fwd Clamp (COUNTERED)","dir":"Forward","clk":12,"dist":"Med","ht":"Ground","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
    {"id":21,"p":"#5","tech":"Backward Push","dir":"Back-Right","clk":4,"dist":"Med","ht":"Ground","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
    {"id":22,"p":"#5","tech":"Forward Clamp","dir":"Forward","clk":12,"dist":"Long","ht":"Air","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
    {"id":23,"p":"#5","tech":"Backward Push","dir":"Back-Right","clk":4,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Right Wing","wing":"-","ttp":3.5,"spd":"Avg"},
    {"id":24,"p":"#5","tech":"Backward Push","dir":"Back-Right","clk":4,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Right Wing","wing":"-","ttp":3.3,"spd":"Avg"},
    {"id":25,"p":"#5","tech":"Slice","dir":"Left","clk":9,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Left Wing","wing":"#23","ttp":2.1,"spd":"Fast"},
    {"id":26,"p":"#5","tech":"Directed Push","dir":"Left","clk":9,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Left Wing","wing":"#23","ttp":2.5,"spd":"Fast"},
    {"id":27,"p":"#4","tech":"Behind Rake","dir":"Backward","clk":6,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Right Wing","wing":"-","ttp":3.7,"spd":"Avg"},
    {"id":28,"p":"#4","tech":"Slice + Box","dir":"Right","clk":3,"dist":"Short","ht":"Ground","out":"Win","poss":"Scramble","who":"Ground Ball","wing":"-","ttp":4.8,"spd":"Slow"},
    {"id":29,"p":"#4","tech":"Forward + DL","dir":"Fwd-Right","clk":2,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Right Wing","wing":"#5","ttp":2.2,"spd":"Fast"},
    {"id":30,"p":"#23","tech":"Forward Launch","dir":"Fwd-Left","clk":10,"dist":"Long","ht":"Air","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
    {"id":31,"p":"#23","tech":"Forward + DL","dir":"Fwd-Right","clk":2,"dist":"Long","ht":"Air","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
    {"id":32,"p":"#23","tech":"Forward Power","dir":"Forward","clk":12,"dist":"Long","ht":"Air","out":"Win","poss":"Clean","who":"Left Wing","wing":"-","ttp":2.6,"spd":"Fast"},
]


def render(all_data):
    """Draw Control Center - UVA analysis + UVA scouting report from film study."""
    st.markdown("## Draw Control Center")
    st.markdown(f'<p style="color:{TEXT_GRAY};">Draw controls are the single highest-leverage stat in women\'s lacrosse. Teams winning 60%+ of draws gain multiple extra possessions per game.</p>', unsafe_allow_html=True)

    total_dc = sum(d["player"]["dc"] for d in all_data.values())
    _max_gp = max((d["player"]["gp"] for d in all_data.values()), default=1)
    dc_per_game = total_dc / max(_max_gp, 1)

    # two sub-tabs
    # sub-tab tracking
    dc_sub1, dc_sub2 = st.tabs(["🏠 UVA Draw Analysis", "🔍 UVA Draw Control Scouting Report"])

    # sub-tab 1: team draw analysis
    with dc_sub1:
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Total Draw Controls", total_dc)
        mc2.metric("DC / Game", f"{dc_per_game:.1f}")
        mc3.metric("Primary Draw Specialist", "Kate Galica (35)")

        st.markdown("")
        st.markdown("### Draw Control Distribution")
        dc_fig = make_draw_control_chart(all_data)
        if dc_fig:
            st.plotly_chart(dc_fig, use_container_width=True)

        st.markdown("### Kate Galica — Draw Control Deep Dive")
        galica = all_data.get("Kate Galica")
        if galica:
            p = galica["player"]
            g1, g2 = st.columns(2)
            with g1:
                st.markdown(f"""<div class="coaching-notes">
                <strong>Draw Control Dominance:</strong> {p['dc']} draws won across {p['gp']} games = {p['dc']/p['gp']:.0f} DC/game<br>
                She accounts for <strong>{p['dc']/max(total_dc,1)*100:.0f}%</strong> of all team draw controls.<br><br>
                <strong>Recommendation:</strong> Galica must take every draw in competitive games. Build a secondary option
                (Dinardo with {all_data.get('Jenna Dinardo', {}).get('player', {}).get('dc', 0)} DCs or Reilly with {all_data.get('Alex Reilly', {}).get('player', {}).get('dc', 0)} DCs)
                for rest in blowouts.
                </div>""", unsafe_allow_html=True)
            with g2:
                fig = make_rolling_avg_chart(p)
                if fig:
                    st.markdown("**Goals Rolling Average (3-game)**")
                    st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Draw Circle → Goal Conversion Pipeline")
        st.markdown(f"""<div class="rec-box">
        <strong>Draw-to-Goal Flow:</strong><br>
        Draw Controls Won: <strong>{total_dc}</strong> → Ground Balls Recovered: <strong>{sum(d['player']['gb'] for d in all_data.values())}</strong> →
        Team Goals: <strong>56</strong><br><br>
        With {total_dc} draws and 56 goals, the team converts roughly 1 goal per {total_dc/56:.1f} draws won.
        Improving draw circle ground ball recovery is a high-leverage practice area.
        </div>""", unsafe_allow_html=True)

    # sub-tab 2: scouting report
    with dc_sub2:
        uva_df = pd.DataFrame(UVA_DRAW_CLIPS)

        st.subheader("UVA Draw Control Scouting Report")
        st.caption("32 Draw Controls Analyzed · Multi-Game Film Study · Internal Scouting")

        # KPI row
        uva_wins = len(uva_df[uva_df["out"] == "Win"])
        uva_losses = len(uva_df[uva_df["out"] == "Loss"])
        uva_fifty = len(uva_df[uva_df["out"] == "50-50"])
        uva_win_pct = uva_wins / len(uva_df) * 100

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.markdown(f'<div class="stat-box"><div class="stat-val">{len(uva_df)}</div><div class="stat-label">Total Draws</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN}">{uva_win_pct:.0f}%</div><div class="stat-label">UVA Win Rate</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN}">{uva_wins}</div><div class="stat-label">Wins</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_MAGENTA}">{uva_losses}</div><div class="stat-label">Losses</div></div>', unsafe_allow_html=True)
        k5.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_YELLOW}">{uva_fifty}</div><div class="stat-label">50-50</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # player profiles
        st.markdown("### Player Profiles")
        player_stats = {}
        for p_id in ["#5", "#4", "#23"]:
            pdata = uva_df[uva_df["p"] == p_id]
            pw = len(pdata[pdata["out"] == "Win"])
            pl = len(pdata[pdata["out"] == "Loss"])
            pf = len(pdata[pdata["out"] == "50-50"])
            win_ttps = pdata[(pdata["out"] == "Win") & (pdata["ttp"] > 0)]["ttp"]
            avg_ttp = win_ttps.mean() if len(win_ttps) > 0 else 0
            top_tech = pdata["tech"].str.replace(r" \(COUNTERED\)", "", regex=True).value_counts().index[0] if len(pdata) > 0 else "—"
            top_dir = pdata["dir"].value_counts().index[0] if len(pdata) > 0 else "—"
            player_stats[p_id] = {"total": len(pdata), "wins": pw, "losses": pl, "fifty": pf,
                                  "win_pct": pw / max(len(pdata), 1) * 100, "avg_ttp": avg_ttp,
                                  "top_tech": top_tech, "top_dir": top_dir}

        pp1, pp2, pp3 = st.columns(3)
        player_cols = {
            "#5": (UVA_ORANGE, pp1, "Kate Galica", "Primary Draw Taker",
                   "Forward Clamp dominant — goes Fwd-Right ~55% of the time. Right Wing #4 (Dinardo) is the primary recovery target. Extremely repeatable pattern with fast TTP."),
            "#4": (UVA_CYAN, pp2, "Jenna Dinardo", "Backup Draw Taker",
                   "Behind Rake technique — fundamentally different style from Galica. More physical in the circle. Versatile enough to play wing recovery when Galica draws."),
            "#23": (UVA_YELLOW, pp3, "Alex Reilly", "Tertiary Draw Taker",
                    "Forward Launch with power — still developing consistency (1W-2L). Strong athleticism but over-powers draws beyond wing recovery range at times.")
        }
        for p_id, (color, col, name, role, scout_note) in player_cols.items():
            ps = player_stats[p_id]
            with col:
                st.markdown(f"""<div class="player-card" style="border-top:4px solid {color};">
                <h3 style="color:{color} !important;margin:0 0 4px 0;font-size:1.5rem;">{name} ({p_id})</h3>
                <p style="color:{TEXT_GRAY};font-size:0.8rem;margin:0 0 12px 0;">{role}</p>
                <div style="display:flex;gap:8px;margin-bottom:12px;">
                    <span style="background:rgba(46,125,50,0.12);color:{UVA_GREEN};padding:3px 10px;border-radius:12px;font-size:0.8rem;font-weight:600;">{ps['wins']}W</span>
                    <span style="background:rgba(198,40,40,0.12);color:{UVA_MAGENTA};padding:3px 10px;border-radius:12px;font-size:0.8rem;font-weight:600;">{ps['losses']}L</span>
                    <span style="background:rgba(253,218,36,0.12);color:{UVA_YELLOW};padding:3px 10px;border-radius:12px;font-size:0.8rem;font-weight:600;">{ps['fifty']}T</span>
                </div>
                <div style="font-size:0.85rem;margin-bottom:6px;"><strong>Win Rate:</strong> {ps['win_pct']:.0f}% ({ps['total']} draws)</div>
                <div style="font-size:0.85rem;margin-bottom:6px;"><strong>#1 Technique:</strong> {ps['top_tech']}</div>
                <div style="font-size:0.85rem;margin-bottom:6px;"><strong>#1 Direction:</strong> {ps['top_dir']}</div>
                <div style="font-size:0.85rem;margin-bottom:10px;"><strong>Avg TTP (wins):</strong> {ps['avg_ttp']:.1f}s</div>
                <div class="coaching-notes" style="font-size:0.8rem;">{scout_note}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # technique analysis
        st.markdown("### Technique Breakdown")
        tc1, tc2 = st.columns(2)

        with tc1:
            tech_clean = uva_df["tech"].str.replace(r" \(COUNTERED\)", "", regex=True)
            tech_counts = tech_clean.value_counts()
            tech_wins = uva_df.copy()
            tech_wins["tech_clean"] = tech_clean
            tech_wr = tech_wins.groupby("tech_clean").apply(
                lambda g: pd.Series({"wins": (g["out"] == "Win").sum(), "total": len(g)}),
                include_groups=False
            )
            tech_wr["win_rate"] = (tech_wr["wins"] / tech_wr["total"] * 100).round(0)
            tech_wr = tech_wr.sort_values("total", ascending=True)

            fig_tech = go.Figure()
            fig_tech.add_trace(go.Bar(
                y=tech_wr.index, x=tech_wr["total"],
                orientation="h", name="Total",
                marker_color=UVA_BLUE_25,
                text=[f'{int(t)} draws · {int(w)}%' for t, w in zip(tech_wr["total"], tech_wr["win_rate"])],
                textposition="outside", textfont=dict(size=10, color=UVA_BLUE)
            ))
            fig_tech.add_trace(go.Bar(
                y=tech_wr.index, x=tech_wr["wins"],
                orientation="h", name="Wins",
                marker_color=UVA_ORANGE
            ))
            _base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("margin", "xaxis", "yaxis")}
            fig_tech.update_layout(**_base, height=380, barmode="overlay",
                xaxis=dict(title="Count"), yaxis=dict(tickfont=dict(size=10)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=140, r=30, t=40, b=30))
            st.plotly_chart(fig_tech, use_container_width=True)

        with tc2:
            # win rate by ball height
            ht_stats = uva_df.groupby("ht").apply(
                lambda g: pd.Series({"wins": (g["out"] == "Win").sum(), "total": len(g)}),
                include_groups=False
            )
            ht_stats["win_rate"] = (ht_stats["wins"] / ht_stats["total"] * 100).round(1)

            fig_ht = go.Figure()
            ht_colors = {"Ground": UVA_GREEN, "Air": UVA_CYAN, "Bounce": UVA_YELLOW}
            for ht_type in ht_stats.index:
                fig_ht.add_trace(go.Bar(
                    x=[ht_type], y=[ht_stats.loc[ht_type, "win_rate"]],
                    name=ht_type, marker_color=ht_colors.get(ht_type, UVA_BLUE_25),
                    text=[f'{ht_stats.loc[ht_type, "win_rate"]:.0f}% ({int(ht_stats.loc[ht_type, "wins"])}/{int(ht_stats.loc[ht_type, "total"])})'],
                    textposition="outside", textfont=dict(size=11, color=UVA_BLUE)
                ))
            _ht_base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("margin", "yaxis")}
            fig_ht.update_layout(**_ht_base, height=380, showlegend=False,
                yaxis=dict(title="Win Rate %", range=[0, 110]),
                title=dict(text="Win Rate by Ball Height", font=dict(size=14)))
            st.plotly_chart(fig_ht, use_container_width=True)

        st.markdown("---")

        # directional tendencies
        st.markdown("### Directional Tendencies")
        dr1, dr2 = st.columns(2)

        with dr1:
            # polar chart by clock position
            clock_bins = {"12 (Forward)": [11, 12, 1], "3 (Right)": [2, 3, 4],
                          "6 (Backward)": [5, 6, 7], "9 (Left)": [8, 9, 10]}
            zone_counts = []
            zone_wins = []
            zone_labels = list(clock_bins.keys())
            for label, clks in clock_bins.items():
                zone_data = uva_df[uva_df["clk"].isin(clks)]
                zone_counts.append(len(zone_data))
                zone_wins.append(len(zone_data[zone_data["out"] == "Win"]))

            fig_polar = go.Figure()
            fig_polar.add_trace(go.Scatterpolar(
                r=zone_counts + [zone_counts[0]],
                theta=zone_labels + [zone_labels[0]],
                fill="toself", name="All Draws",
                fillcolor="rgba(35,45,75,0.2)", line=dict(color=UVA_BLUE, width=2),
                marker=dict(size=8)
            ))
            fig_polar.add_trace(go.Scatterpolar(
                r=zone_wins + [zone_wins[0]],
                theta=zone_labels + [zone_labels[0]],
                fill="toself", name="Wins",
                fillcolor="rgba(229,114,0,0.2)", line=dict(color=UVA_ORANGE, width=2),
                marker=dict(size=8)
            ))
            fig_polar.update_layout(
                polar=dict(
                    bgcolor=WHITE,
                    radialaxis=dict(visible=True, gridcolor=MED_GRAY, tickfont=dict(size=9)),
                    angularaxis=dict(tickfont=dict(size=11, color=UVA_BLUE))
                ),
                height=380, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                paper_bgcolor=WHITE, plot_bgcolor=WHITE,
                margin=dict(t=60, b=40)
            )
            st.plotly_chart(fig_polar, use_container_width=True)

        with dr2:
            # direction detail breakdown
            dir_wr = uva_df.groupby("dir").apply(
                lambda g: pd.Series({"wins": (g["out"] == "Win").sum(), "total": len(g)}),
                include_groups=False
            )
            dir_wr["win_rate"] = (dir_wr["wins"] / dir_wr["total"] * 100).round(0)
            dir_wr = dir_wr.sort_values("total", ascending=False)

            def dir_color(d):
                d_low = d.lower()
                if "left" in d_low and "back" not in d_low:
                    return UVA_CYAN
                elif "right" in d_low and "back" not in d_low:
                    return UVA_ORANGE
                elif "back" in d_low:
                    return UVA_MAGENTA
                else:
                    return UVA_GREEN

            fig_dir = go.Figure()
            fig_dir.add_trace(go.Bar(
                x=dir_wr.index, y=dir_wr["total"],
                marker_color=[dir_color(d) for d in dir_wr.index],
                text=[f'{int(t)} ({int(w)}%)' for t, w in zip(dir_wr["total"], dir_wr["win_rate"])],
                textposition="outside", textfont=dict(size=10, color=UVA_BLUE)
            ))
            _dir_base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("margin", "xaxis", "yaxis")}
            fig_dir.update_layout(**_dir_base, height=380,
                yaxis=dict(title="Count"), xaxis=dict(tickfont=dict(size=10), tickangle=-30),
                title=dict(text="Direction Frequency & Win Rate", font=dict(size=14)),
                margin=dict(l=30, r=30, t=40, b=80))
            st.plotly_chart(fig_dir, use_container_width=True)

        # directional insight
        fwd_right_count = len(uva_df[uva_df["dir"].str.contains("Right", na=False) & ~uva_df["dir"].str.contains("Back", na=False)])
        fwd_right_pct = fwd_right_count / len(uva_df) * 100
        st.markdown(f"""<div class="rec-box">
        <strong>Key Directional Insight:</strong> Galica goes <strong>Forward-Right {fwd_right_pct:.0f}%</strong> of the time
        ({fwd_right_count}/{len(uva_df)} draws). Right Wing #4 (Dinardo) positions at 3 o'clock pre-whistle and uses a body seal to box out.
        When the ball goes RIGHT, UVA's wing structure gives a significant recovery advantage.
        Opponents should expect us to overload the right-wing lane.
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # wing & possession analysis
        st.markdown("### Wing & Possession Analysis")
        wc1, wc2 = st.columns(2)

        with wc1:
            # who secures possession on wins?
            who_counts = uva_df[uva_df["out"] == "Win"].groupby("who").size().sort_values(ascending=True)
            fig_who = go.Figure()
            fig_who.add_trace(go.Bar(
                y=who_counts.index, x=who_counts.values,
                orientation="h", marker_color=UVA_ORANGE,
                text=[str(v) for v in who_counts.values],
                textposition="outside", textfont=dict(size=11, color=UVA_BLUE)
            ))
            _who_base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("margin", "xaxis")}
            fig_who.update_layout(**_who_base, height=300,
                title=dict(text="Win Contribution (Who Secures Ball?)", font=dict(size=14)),
                xaxis=dict(title="Wins Secured"), margin=dict(l=120, r=30, t=40, b=30))
            st.plotly_chart(fig_who, use_container_width=True)

        with wc2:
            # possession type distribution
            poss_counts = uva_df.groupby("poss").apply(
                lambda g: pd.Series({"wins": (g["out"] == "Win").sum(), "total": len(g)}),
                include_groups=False
            )
            poss_counts["win_rate"] = (poss_counts["wins"] / poss_counts["total"] * 100).round(0)

            poss_colors = {"Wing": UVA_ORANGE, "Clean": UVA_GREEN, "Scramble": UVA_YELLOW, "Opponent": UVA_MAGENTA}
            fig_poss = go.Figure()
            fig_poss.add_trace(go.Pie(
                labels=poss_counts.index, values=poss_counts["total"],
                marker=dict(colors=[poss_colors.get(p, UVA_BLUE_25) for p in poss_counts.index]),
                textinfo="label+percent", textfont=dict(size=11),
                hole=0.4
            ))
            fig_poss.update_layout(height=300, font=dict(),
                paper_bgcolor=WHITE, plot_bgcolor=WHITE,
                title=dict(text="Possession Type Distribution", font=dict(size=14, color=UVA_BLUE)),
                showlegend=False, margin=dict(t=60, b=20))
            st.plotly_chart(fig_poss, use_container_width=True)

        # wing player callout
        wing_4_count = len(uva_df[uva_df["wing"] == "#4"])
        wing_23_count = len(uva_df[uva_df["wing"] == "#23"])
        st.markdown(f"""<div class="coaching-notes">
        <strong>Wing Targets:</strong><br>
        <strong>Right Wing #4 (Dinardo)</strong> — Primary recovery target ({wing_4_count} clips). Positions at 3 o'clock, uses body seal to box out. Our most reliable wing recovery option.<br><br>
        <strong>#23 (Reilly)</strong> — Secondary wing target ({wing_23_count} clips). Used on left-side directed draws where Galica opens up to the left. Developing wing recovery consistency.<br><br>
        <strong>#5 (Galica self-recovery)</strong> — On Go-With Grab and scramble situations, Galica secures her own draw. Happens mostly on air-ball outcomes.
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # time to possession
        st.markdown("### Time to Possession (TTP)")
        ttp_df = uva_df[(uva_df["out"] == "Win") & (uva_df["ttp"] > 0)].copy()

        tp1, tp2 = st.columns(2)
        with tp1:
            fig_ttp = go.Figure()
            fig_ttp.add_trace(go.Histogram(
                x=ttp_df["ttp"], nbinsx=10,
                marker_color=UVA_ORANGE,
                name="TTP (seconds)"
            ))
            fig_ttp.add_vline(x=ttp_df["ttp"].mean(), line_dash="dash", line_color=UVA_BLUE,
                annotation_text=f"Avg: {ttp_df['ttp'].mean():.1f}s", annotation_font_size=11)
            _ttp_base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")}
            fig_ttp.update_layout(**_ttp_base, height=300,
                xaxis=dict(title="Time to Possession (seconds)"),
                yaxis=dict(title="Count"),
                title=dict(text="TTP Distribution (UVA Wins)", font=dict(size=14)))
            st.plotly_chart(fig_ttp, use_container_width=True)

        with tp2:
            # TTP by speed category
            spd_data = ttp_df.groupby("spd")["ttp"].agg(["mean", "count"]).reset_index()
            spd_colors = {"Fast": UVA_GREEN, "Avg": UVA_YELLOW, "Slow": UVA_MAGENTA}

            fig_spd = go.Figure()
            for _, row in spd_data.iterrows():
                fig_spd.add_trace(go.Bar(
                    x=[row["spd"]], y=[row["mean"]],
                    marker_color=spd_colors.get(row["spd"], UVA_BLUE_25),
                    text=[f'{row["mean"]:.1f}s (n={int(row["count"])})'],
                    textposition="outside", textfont=dict(size=11, color=UVA_BLUE),
                    showlegend=False
                ))
            _spd_base = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("yaxis",)}
            fig_spd.update_layout(**_spd_base, height=300,
                yaxis=dict(title="Avg TTP (seconds)"),
                title=dict(text="Avg TTP by Reaction Speed", font=dict(size=14)))
            st.plotly_chart(fig_spd, use_container_width=True)

        fast_wins = len(ttp_df[ttp_df["spd"] == "Fast"])
        slow_wins = len(ttp_df[ttp_df["spd"] == "Slow"])
        fast_avg = ttp_df[ttp_df["spd"] == "Fast"]["ttp"].mean() if fast_wins > 0 else 0
        slow_avg = ttp_df[ttp_df["spd"] == "Slow"]["ttp"].mean() if slow_wins > 0 else 0
        st.markdown(f"""<div class="rec-box">
        <strong>TTP Insight:</strong> UVA secures possession in an average of <strong>{ttp_df['ttp'].mean():.1f}s</strong> on wins.
        Fast wins ({fast_wins} clips, avg {fast_avg:.1f}s) come from clean wing delivery to Dinardo or Reilly.
        Slow wins ({slow_wins} clips, avg {slow_avg:.1f}s) involve scrambles and ground balls — practice focus area for improving transition speed.
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # all clips table
        with st.expander("📋 View All 32 Scouting Clips", expanded=False, key="dc_clips_expander"):
            display_df = uva_df[["id", "p", "tech", "dir", "clk", "ht", "out", "poss", "who", "wing", "ttp", "spd"]].copy()
            display_df.columns = ["Clip", "Player", "Technique", "Direction", "Clock", "Height", "Outcome", "Possession", "Secured By", "Wing", "TTP (s)", "Speed"]
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
