# key moments and film tags tab
import streamlit as st
from style import *
from analytics import *


def render(sheets, game, info, home_team, opp, hs, aws, result):
    """Render the key moments and film tags analysis tab."""
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
                # showing positive and negative swings in the game
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

                # scoring runs
                runs = detect_scoring_runs(scoring_summary, min_run=3)
                if runs:
                    st.markdown('<h4 style="color:#232D4B;">Scoring Runs (3+ consecutive)</h4>', unsafe_allow_html=True)
                    for run in runs:
                        is_uva = "Virginia" in run["team"]
                        variant = "pos" if is_uva else "neg"
                        title = f"{run['team']} {run['length']}-0 Run — Q{run['start_period']} {run['start_time']} to Q{run['end_period']} {run['end_time']}"
                        desc = f"Scorers: {', '.join(run['scorers'])}. Study execution, transition speed, and defensive breakdowns."
                        st.markdown(moment_card(title, desc, variant=variant), unsafe_allow_html=True)

                # film tags for the coaching staff
                st.markdown("---")
                st.markdown('<h4 style="color:#232D4B;">Film Tags</h4>', unsafe_allow_html=True)
                st.caption("Suggested film sequences for coaching staff review.")

                ftcol1, ftcol2 = st.columns(2)

                with ftcol1:
                    # go-ahead goals
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

                    # must-show highlights
                    st.markdown(f'<p style="color:{UVA_BLUE};font-weight:700;margin-bottom:8px;">Must-Show Highlights</p>', unsafe_allow_html=True)
                    for _, row in wpa_df.nlargest(3, "WPA").iterrows():
                        title = f"Must-Show: {row['Scorer']}'s Q{int(row['Period'])} goal ({row['WPA']:+.1f}% WPA)"
                        desc = f"Score: {row['Score']}. High-impact goal."
                        st.markdown(moment_card(title, desc, wpa=row["WPA"], variant="pos"),
                                    unsafe_allow_html=True)

                with ftcol2:
                    # defensive review
                    st.markdown(f'<p style="color:{UVA_BLUE};font-weight:700;margin-bottom:8px;">Defensive Review</p>', unsafe_allow_html=True)
                    opp_wpa_goals = wpa_df[~wpa_df["Team"].str.contains("Virginia", case=False)]
                    if not opp_wpa_goals.empty:
                        for _, row in opp_wpa_goals.nsmallest(2, "WPA").iterrows():
                            title = f"Defensive Review: {row['Scorer']}'s Q{int(row['Period'])} goal ({row['WPA']:+.1f}% WPA)"
                            desc = f"Score: {row['Score']}. Analyze defensive positioning."
                            st.markdown(moment_card(title, desc, wpa=row["WPA"], variant="neg"),
                                        unsafe_allow_html=True)

                    # discipline
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
