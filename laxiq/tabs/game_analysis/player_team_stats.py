# player and team stats tab
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from style import *
from analytics import *


def render(sheets, game, info, home_team, opp, hs, aws):
    """Render the player and team stats analysis tab."""
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

        # overall statistical comparison

        if stats_qoq is not None and not stats_qoq.empty:
            # build comprehensive stat list (matching mockup)
            stat_categories = [
                "Goals", "Shots", "Shots On Goal", "Draw Controls",
                "Ground Balls", "Turnovers", "Saves", "Clears",
                "Free-Position Shots", "Fouls",
            ]
            # add player-derived stats: Assists, Caused TOs
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
                    # handle Clears format "15-17" → extract made/failed
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

            # insert player-derived stats
            # goals first from scoring
            # add Assists and Caused TOs (from player sheets)
            stats_data.append({"category": "Assists", "uva": uva_assists, "opponent": opp_assists})
            stats_data.append({"category": "Caused TOs", "uva": uva_ct, "opponent": opp_ct})

            # also add Cards from Penalty_Summary if available
            penalties = sheets.get("Penalty_Summary")
            if penalties is not None and not penalties.empty:
                uva_cards = len(penalties[penalties["Team"].str.contains("Virginia", case=False, na=False)])
                opp_cards = len(penalties[~penalties["Team"].str.contains("Virginia", case=False, na=False)])
                stats_data.append({"category": "Cards", "uva": uva_cards, "opponent": opp_cards})

            if stats_data:
                stats_df = pd.DataFrame(stats_data)
                # reverse order so first category is at top
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

            # quarter by quarter breakdown

            st.markdown(f'<h4 style="color:{UVA_BLUE};">Quarter-by-Quarter Breakdown</h4>',
                        unsafe_allow_html=True)

            # build QoQ data for both teams
            qoq_categories = [
                "Goals", "Shots", "Draw Controls",
                "Ground Balls", "Turnovers", "Saves",
            ]

            # collect per-quarter stats
            qoq_data = {}  # {quarter: {cat: (uva, opp)}}
            for q_i in range(1, 5):
                q_label = f"Q{q_i}"
                qoq_data[q_label] = {}

            # goals from Score_By_Quarter
            score_qoq = sheets.get("Score_By_Quarter")
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

            # render as 4 dark quarter cards side by side
            q_cols = st.columns(4)
            short_labels = {"Goals": "G", "Shots": "SH", "Draw Controls": "DC",
                            "Ground Balls": "GB", "Turnovers": "TO", "Saves": "SV"}
            for col, q_label in zip(q_cols, ["Q1", "Q2", "Q3", "Q4"]):
                q_stats_map = qoq_data.get(q_label, {})
                # score line
                g_uva, g_opp = q_stats_map.get("Goals", (0, 0))
                score_color = "#4CAF50" if g_uva > g_opp else "#EF5350" if g_opp > g_uva else "white"

                stat_rows_html = ""
                for cat in qoq_categories:
                    uv, ov = q_stats_map.get(cat, (0, 0))
                    sl = short_labels.get(cat, cat[:2])
                    # highlight advantage
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

        # virginia player influence using WPA

        st.markdown("---")

        uva_players_df = sheets["UVA_Players"].copy()
        uva_players_df = compute_player_efficiency(uva_players_df)

        # trying to compute WPA from play by play data
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

        # attaching WPA to player rows with fallback
        wpa_col = []
        for _, row in uva_players_df.iterrows():
            name = row["Player"]
            if name in player_wpa:
                wpa_col.append(round(player_wpa[name], 1))
            else:
                wpa_col.append(round(row["Impact"] * 0.5, 1))  # scaled fallback
        uva_players_df["WPA"] = wpa_col

        # filter to players with any activity
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

        # player statistics cards

        st.markdown("---")
        st.markdown('<h4 style="color:#232D4B;">Player Statistics</h4>', unsafe_allow_html=True)

        # sort by WPA descending for card layout
        card_players = uva_players_df[
            (uva_players_df["G"] + uva_players_df["A"] + uva_players_df["GB"]
             + uva_players_df["DC"] + uva_players_df["TO"] + uva_players_df["CT"]
             + uva_players_df["SH"] > 0)
            | (uva_players_df["WPA"].abs() > 0.05)
        ].copy().sort_values("WPA", ascending=False)

        if not card_players.empty:
            # render 4-column grid of player cards
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

                    # figure out which stat to highlight for each player
                    stats_list = [("G", g_val), ("A", a_val), ("DC", dc_val), ("TO", to_val), ("CT", ct_val)]
                    highlight_stat = None
                    if wpa_val >= 0:
                        # positive: pick the highest-value positive stat (G > DC > CT > A)
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
                        # negative: turnovers are usually the culprit
                        if to_val > 0:
                            highlight_stat = ("TO", "#EF5350")  # red
                        else:
                            # no TOs — check if low production is the issue
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

        # goalkeeper section
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

        # ── Milestone 3: Dependent Dropdowns — Position → Player spotlight ──
        st.markdown("---")
        st.markdown('<h4 style="color:#232D4B;">Player Spotlight</h4>', unsafe_allow_html=True)
        st.caption("Select a position to filter available players, then pick a player for a detailed game snapshot.")

        uva_pl = sheets.get("UVA_Players")
        if uva_pl is not None and not uva_pl.empty and "Player" in uva_pl.columns:
            # build position map from player intelligence data if available
            # fallback: infer from stats (GK has saves-related cols)
            _all_positions = sorted(set(
                ["A", "M", "D", "GK"] if "Position" not in uva_pl.columns
                else uva_pl["Position"].dropna().unique()
            ))
            dep1, dep2 = st.columns(2)
            with dep1:
                spot_pos = st.selectbox("Position Filter", _all_positions, key="spotlight_pos",
                                        help="Selecting a position filters the Player dropdown")
            # build dependent player list based on position
            # without explicit Position column, use heuristics: GK if row has very low SH
            if "Position" in uva_pl.columns:
                pos_players = uva_pl[uva_pl["Position"] == spot_pos]["Player"].tolist()
            else:
                # heuristic: GK = low shots & high saves; everyone else = field
                if spot_pos == "GK":
                    pos_players = uva_pl[uva_pl["SH"] == 0]["Player"].tolist() if "SH" in uva_pl.columns else []
                else:
                    pos_players = uva_pl[uva_pl["SH"] > 0]["Player"].tolist() if "SH" in uva_pl.columns else uva_pl["Player"].tolist()
            if not pos_players:
                pos_players = uva_pl["Player"].tolist()  # fallback

            with dep2:
                spot_player = st.selectbox("Player", pos_players, key="spotlight_player",
                                           help="Players available depend on Position Filter selection")

            # show that player's stats for this game
            p_row = uva_pl[uva_pl["Player"] == spot_player]
            if not p_row.empty:
                p = p_row.iloc[0]
                sp_cols = st.columns(6)
                stat_map = [("Goals", "G"), ("Assists", "A"), ("Shots", "SH"),
                            ("GB", "GB"), ("DC", "DC"), ("TO", "TO")]
                for col_obj, (label, col_key) in zip(sp_cols, stat_map):
                    val = int(p.get(col_key, 0)) if pd.notna(p.get(col_key)) else 0
                    with col_obj:
                        st.metric(label, val)

    except Exception as e:
        st.error(f"Error in Players & Team Stats tab: {e}")
        import traceback
        st.code(traceback.format_exc())
