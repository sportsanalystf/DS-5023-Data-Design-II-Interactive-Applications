# game comparison tab
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from style import *
from analytics import *


def render(sheets, game, info, home_team, opp, hs, aws):
    """Render the game comparison analysis tab."""
    try:
        all_games = list_games()
        if len(all_games) < 2:
            st.info("Need at least 2 games for comparison.")
        else:
            st.markdown('<h4 style="color:#232D4B;">Game Comparison</h4>', unsafe_allow_html=True)
            # lets you compare any two games side by side
            st.caption("Compare Virginia's performance across two games side-by-side.")

            gc1, gc2 = st.columns(2)
            # lets you compare any two games
            with gc1:
                game_a_idx = st.selectbox("Game A", range(len(all_games)),
                                          format_func=lambda i: all_games[i]["label"], key="cmp_a")
            with gc2:
                default_b = min(1, len(all_games) - 1)
                game_b_idx = st.selectbox("Game B", range(len(all_games)),
                                          format_func=lambda i: all_games[i]["label"],
                                          index=default_b, key="cmp_b")

            # Milestone 3: Input Validation — Scenario 4: same game selected
            if game_a_idx == game_b_idx:
                st.warning("⚠️ You've selected the **same game** in both slots. Choose two different games for a meaningful comparison.")

            # Milestone 3: User Feedback — spinner during comparison load
            with st.spinner("Comparing game data..."):
                sheets_a = load_game(all_games[game_a_idx]["file"])
                sheets_b = load_game(all_games[game_b_idx]["file"])
                comparison = compare_games(sheets_a, sheets_b)

            if not comparison.empty:
                # game result headers
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

                # statistical comparison bar chart — consistent metrics
                # define ordered metric columns matching team stats
                metric_order = [
                    ("UVA_Goals", "Goals"), ("UVA_Shots", "Shots"), ("UVA_SOG", "SOG"),
                    ("UVA_Draw Controls", "Draw Controls"), ("UVA_Ground Balls", "Ground Balls"),
                    ("UVA_Turnovers", "Turnovers"), ("UVA_Caused TOs", "Caused TOs"),
                    ("UVA_Saves", "Saves"), ("UVA_Assists", "Assists"),
                    ("UVA_Clears", "Clears"), ("UVA_Cards", "Cards"),
                ]
                chart_cats = []
                vals_a = []
                vals_b = []
                for col_name, display_name in metric_order:
                    if col_name not in comparison.columns:
                        continue
                    v1 = comparison.iloc[0].get(col_name, 0)
                    v2 = comparison.iloc[1].get(col_name, 0)
                    # convert NaN to 0
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

                    # delta cards — show first row of key stats
                    st.markdown('<h4 style="color:#232D4B;">Stat Deltas</h4>', unsafe_allow_html=True)
                    n_cards = min(len(chart_cats), 6)
                    delta_cols = st.columns(n_cards)
                    for idx in range(n_cards):
                        delta = vals_b[idx] - vals_a[idx]
                        # turnovers, cards: lower is better
                        is_inverse = chart_cats[idx] in ("Turnovers", "Cards")
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

                # full comparison table
                st.markdown('<h4 style="color:#232D4B;">Full Comparison Data</h4>', unsafe_allow_html=True)
                # clean NaN values for display
                display_cmp = comparison.fillna(0)
                st.dataframe(display_cmp, use_container_width=True, hide_index=True)

                # ── quarter by quarter analysis ──
                st.markdown("---")
                st.markdown('<h4 style="color:#232D4B;">Quarter by Quarter Analysis</h4>', unsafe_allow_html=True)
                st.caption("Compare UVA's performance by quarter across the two selected games.")

                # pull Team_Stats_QoQ for each game
                stats_a = sheets_a.get("Team_Stats_QoQ", pd.DataFrame())
                stats_b = sheets_b.get("Team_Stats_QoQ", pd.DataFrame())
                score_a = sheets_a.get("Score_By_Quarter", pd.DataFrame())
                score_b = sheets_b.get("Score_By_Quarter", pd.DataFrame())

                # categories available in the data
                qoq_cats = ["Shots", "Saves", "Ground Balls", "Draw Controls", "Turnovers", "Clears"]
                quarters = ["Q1", "Q2", "Q3", "Q4"]

                def _get_uva_qoq(stats_df, category):
                    """Get UVA's quarter values for a stat category."""
                    if stats_df.empty:
                        return [0, 0, 0, 0]
                    row = stats_df[(stats_df["Category"] == category)
                                   & (stats_df["Team"].str.contains("Virginia", case=False, na=False))]
                    if row.empty:
                        return [0, 0, 0, 0]
                    vals = []
                    for q in quarters:
                        raw = str(row.iloc[0].get(q, 0))
                        if "-" in raw:
                            try:
                                vals.append(int(raw.split("-")[0]))
                            except ValueError:
                                vals.append(0)
                        else:
                            try:
                                vals.append(int(raw))
                            except (ValueError, TypeError):
                                vals.append(0)
                    return vals

                def _get_uva_score_qoq(score_df):
                    """Get UVA's scoring by quarter."""
                    if score_df.empty:
                        return [0, 0, 0, 0]
                    uva_row = score_df[score_df["Team"].str.contains("Virginia", case=False, na=False)]
                    if uva_row.empty:
                        return [0, 0, 0, 0]
                    return [int(uva_row.iloc[0].get(q, 0)) for q in quarters]

                # scoring by quarter comparison
                score_qa = _get_uva_score_qoq(score_a)
                score_qb = _get_uva_score_qoq(score_b)

                fig_score_q = go.Figure()
                fig_score_q.add_trace(go.Bar(
                    x=quarters, y=score_qa, name=f"vs {opp_a}",
                    marker=dict(color=UVA_ORANGE),
                    text=[str(v) for v in score_qa], textposition="outside",
                ))
                fig_score_q.add_trace(go.Bar(
                    x=quarters, y=score_qb, name=f"vs {opp_b}",
                    marker=dict(color=UVA_BLUE),
                    text=[str(v) for v in score_qb], textposition="outside",
                ))
                fig_score_q.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
                    font=dict(family="DM Sans, sans-serif", color=UVA_BLUE, size=12),
                    margin=dict(l=40, r=20, t=50, b=40), height=320, barmode="group",
                    title=dict(text="Goals by Quarter", font=dict(size=14, color=UVA_BLUE)),
                    xaxis=dict(gridcolor="#ECECEC"), yaxis=dict(gridcolor="#ECECEC"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                )
                st.plotly_chart(fig_score_q, use_container_width=True)

                # stat-by-stat quarter comparison (2 columns of charts)
                for row_cats in [qoq_cats[:3], qoq_cats[3:]]:
                    q_cols = st.columns(len(row_cats))
                    for col_obj, cat in zip(q_cols, row_cats):
                        qa_vals = _get_uva_qoq(stats_a, cat)
                        qb_vals = _get_uva_qoq(stats_b, cat)

                        fig_cat = go.Figure()
                        fig_cat.add_trace(go.Bar(
                            x=quarters, y=qa_vals, name=f"vs {opp_a}",
                            marker=dict(color=UVA_ORANGE),
                            text=[str(v) for v in qa_vals], textposition="outside",
                        ))
                        fig_cat.add_trace(go.Bar(
                            x=quarters, y=qb_vals, name=f"vs {opp_b}",
                            marker=dict(color=UVA_BLUE),
                            text=[str(v) for v in qb_vals], textposition="outside",
                        ))
                        fig_cat.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
                            font=dict(family="DM Sans, sans-serif", color=UVA_BLUE, size=11),
                            margin=dict(l=30, r=10, t=40, b=30), height=260, barmode="group",
                            title=dict(text=cat, font=dict(size=13, color=UVA_BLUE)),
                            xaxis=dict(gridcolor="#ECECEC"), yaxis=dict(gridcolor="#ECECEC"),
                            showlegend=False,
                        )
                        with col_obj:
                            st.plotly_chart(fig_cat, use_container_width=True)

                # quarter summary table
                st.markdown('<h4 style="color:#232D4B;">Quarter Summary Table</h4>', unsafe_allow_html=True)
                q_table_data = []
                for q_idx, q in enumerate(quarters):
                    row_data = {"Quarter": q}
                    row_data[f"Goals (vs {opp_a})"] = score_qa[q_idx]
                    row_data[f"Goals (vs {opp_b})"] = score_qb[q_idx]
                    for cat in qoq_cats:
                        qa = _get_uva_qoq(stats_a, cat)
                        qb = _get_uva_qoq(stats_b, cat)
                        row_data[f"{cat} (vs {opp_a})"] = qa[q_idx]
                        row_data[f"{cat} (vs {opp_b})"] = qb[q_idx]
                    q_table_data.append(row_data)
                q_table_df = pd.DataFrame(q_table_data)
                st.dataframe(q_table_df, use_container_width=True, hide_index=True)

            else:
                st.info("Could not generate comparison.")

    except Exception as e:
        st.error(f"Error in Game Comparison tab: {e}")
        import traceback
        st.code(traceback.format_exc())
