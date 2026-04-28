"""
Player Cards tab - Player stats table and individual player detail view.
"""
import streamlit as st
import pandas as pd
from style import (UVA_BLUE, UVA_BLUE_25, WHITE, section_header,
                   GREEN as UVA_GREEN, YELLOW as UVA_YELLOW, MAGENTA as UVA_MAGENTA)
from .charts import make_radar_chart, make_game_log_chart, make_shot_efficiency_bar

# headshot URLs — also imported by player_comparison
HEADSHOT_URLS = {
    "Madison Alaimo": "https://virginiasports.com/imgproxy/pYMb3-v9_Iw05OEJEvS-VLV-PkXLxFnbK2dnVLNGX2o/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvYm9JU25aRzgycFVLbFVqTjc3c3daUkRwV0JOWkdpVDQ2UG0zSUVCQy5qcGc.jpg",
    "Jenna Dinardo": "https://virginiasports.com/imgproxy/M-EqJX8pcAsMqHLqjB7zcRq0P-nR7bKVTQ8i_D86R_4/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvaUpmMjVsZWtZazlNZzRRYWxoTWlCZmhSNldUZjBxZnBTdW1kbENRYi5qcGc.jpg",
    "Addi Foster": "https://virginiasports.com/imgproxy/a-B08gK1VEOXrp9J_Bq82N_9xdFa-xpzxKphIiuuPcg/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvRGdrQ1czdnJKTnRJcGRvZjJuOWRjSHBZMGJnbjRTeWZ3amFWRlFOOS5qcGc.jpg",
    "Kate Galica": "https://virginiasports.com/imgproxy/Z4W8fnWOqaA8_rvVBt7EqYIeGP5hJuEhM3yBq62nGYU/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvdmFpYXp5MlVkMXBRMThGVFJxemZ3V2hyb3ZkUjl4MEIzbTN5UHdaYi5qcGc.jpg",
    "Cady Flaherty": "https://virginiasports.com/imgproxy/K-T-B3xpQl-aDjFqBq_Y80c5ZE8x4l5H8MbR7AqGnOE/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvN2xzcFN0THhFbnMwZFBPNk1mTUt2V1M5VUt3S01VVlZPdkVzNWltdi5qcGc.jpg",
    "Gabby Laverghetta": "https://virginiasports.com/imgproxy/F_sxh_p1KSKW5FxzFKp3vQ0A-0k4Y5uyhd-yVCTBm2Y/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvWFdGa3VmcGdIbk9OT3FZaUlnVDQ5Uld3UXBZdWFSWENDcTdIT0RMMS5qcGc.jpg",
    "Livy Laverghetta": "https://virginiasports.com/imgproxy/b9RWFgqGBkgGFIjgOK2CzY-VKfyX8o_0dNxA-KbFVIE/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvbGRYSUxQeTRLN2dGN2dXbFlhcUtIaXExbzFLcDlGWFNMamdaMTVOeS5qcGc.jpg",
    "Elyse Finnelle": "https://virginiasports.com/imgproxy/0R3SdJ2qx08ccevzYjFN9e1z3SJEdN1jJ8kAMuBbZrQ/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcveDVla1RCZnluRnJIUWRjQzdGbWNLZGdFVXhGa25jWkh4amVJcG5Ybi5qcGc.jpg",
    "Kate Demark": "https://virginiasports.com/imgproxy/hqJLp2fJTW5ZPt0Zp8_GV7yOlAIOcBrwCOOJKBt5YZU/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvN3dWb0xoWXV3a0htamdHYjFJb2tVcXdEYnV0c0NZcHRkNWZJWWdYdi5qcGc.jpg",
    "Alexandra Schneider": "https://virginiasports.com/imgproxy/s9CLFpBGzTNyXL3r9hC6sSeLTsHXYSiNNGxkdDR7EoE/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvMk5uMGVGOXpSS3F2aHlSU0hHU1hGNmVPcjEweTYyNWxQQVZIVDhWWi5qcGc.jpg",
    "Sophia Conti": "https://virginiasports.com/imgproxy/5z2L5PGXqj8_YJRy8H8-tXxjj3pIH3CjRXzE97dG-eA/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvQmRzQU1yNkZjME1MSjd5OVFqOXVmRHdLdndlcUh5WjBvaTdYSWVRSi5qcGc.jpg",
    "Lara Kology": "https://virginiasports.com/imgproxy/gk2T0i4LG_ik2E-fL7oaS8nlJPhBl9aPWS-NHB2XpNM/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvZkdZYlhiZFdHT1d2bXRuUXFndUxyWW5ERWh3R3lqR2lLYjgzbm1JMC5qcGc.jpg",
    "Alex Reilly": "https://virginiasports.com/imgproxy/v5qLaFiVpJJ6AQBdz1V2PEiNWxJnS1vVPKN3Nde4wDk/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvUXRYTDUyOFJyODlUWm5wek1hOHRscXZXd2pjQnExNWdjY0VmQXZVbS5qcGc.jpg",
    "Payton Sfreddo": "https://virginiasports.com/imgproxy/TXIbMgQ6cnYINW5h0zcOSjHGNcNbptNMhT4HwIFi7FI/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvQjI3eG1zcXZVd3BmVENpNjRkMjZ2NXJ3SjNIR0xCOFdVT09tTkFnUy5qcGc.jpg",
    "Mel Josephson": "https://virginiasports.com/imgproxy/0l2LW0rXiVmhIAi7dFFqPjC_8iNmCIoNXHPj80L64io/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvZXRKSk55RXF5Nnl3YUV2Y3FUVDRHR1RVclNYazlXdGJGTGd3ekVQYy5qcGc.jpg",
    "Raleigh Foster": "https://virginiasports.com/imgproxy/Ke-zN1_Bc0bQF5BRmfL_y8JtajBT9e0Z3Y7WjMIyg6o/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvQjB4aWI5MlRFTXpPeFBzaW1Gc0VZc2drUEt5c0MyQ2JUZzVwM0Jqdy5qcGc.jpg",
    "Carly Kennedy": "https://virginiasports.com/imgproxy/jP9nvB-_HjIFZ23hA5A_eMpRn7gU5XBmNXhxW1AKK5A/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvSE5SSHBxZWF4Mk5jQXQ0ZXRWVEFYTHhiUnJ2VTlMbUZPU3BYUDdiOC5qcGc.jpg",
    "Megan Rocklein": "https://virginiasports.com/imgproxy/k7wIW43g42bHERYl-kL_FVPJ3-JqPxfjz4fwdZJBfbo/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvSk5yRDlpNldlSTBHbGpPUVFaYUVtNTBFWFhyVzFoRnBZcno0VmU1Yi5qcGc.jpg",
    "Fiona Allen": "https://virginiasports.com/imgproxy/Z_e6g3SVzfXz9VffJLWQWJP0KdKdGH7BKxj1xEm3eiU/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvTEV5d0daUEE5RTczTlQ3TGdJUjh0S2RMeTFjRlJiTjB4dHlwQ0p3Sy5qcGc.jpg",
    "Abby Musser": "https://virginiasports.com/imgproxy/2ZI8pSVJOr2J7oWmHI1Q-OWVeVj-6JFIm0fQRx8l5kM/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvU21NckJ6SEF3clZMZjdDNHlFMHQ0VjhxRmxVSmtLNWN4bVdwclRIVi5qcGc.jpg",
    "Jayden Piraino": "https://virginiasports.com/imgproxy/5i_Fqg7Lxf8Wge2MfLXp5LYdKJgSqS6K8l3iqGS77RY/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvZk5pZDFYYnhGR1UxTmkxSWdtSlI3aUQxZjM1MnBKSjN2VTlVUUoyYy5qcGc.jpg",
    "Corey White": "https://virginiasports.com/imgproxy/P7CbNjrQg_YxRiGiPMeMLxIJMC9FW4OPqyuKw-3cpyw/rs:fit:400:0:0:0/g:ce:0:0/q:85/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3Zpcmdpbmlhc3BvcnRzLWNvbS1wcm9kLzIwMjUvMDEvMDcvZTFTQUVHRE5mWWRLYkNOc21QQk12VlRONXI3Ymo5bkI2MHdGOEptOS5qcGc.jpg",
}


def render(filtered, sorted_players, games):
    """Render the Player Cards tab showing a stats table and individual player details."""
    st.markdown(section_header("Player Cards"), unsafe_allow_html=True)

    if not sorted_players:
        st.info("No players match the current filters.")
        return

    player_names = [name for name, _ in sorted_players]
    selected_player = st.selectbox("Select Player", player_names,
        format_func=lambda n: f"#{filtered[n]['player']['num']} {n} ({filtered[n]['player']['pos']}) — Impact: {filtered[n]['scores']['overall']:.0f}",
        key="player_card_selector")

    data = filtered[selected_player]
    p = data["player"]
    m = data["metrics"]
    s = data["scores"]
    tier_text = f"Tier {data['tier_num']} — {data['tier_label']}"

    # player header
    st.write(f"**#{p['num']} {selected_player}** — {p['pos']} · {p['yr']} · {p['gp']} GP · {tier_text}")

    # category scores
    cat_cols = st.columns(6)
    for col, (label, key) in zip(cat_cols, [("Overall", "overall"), ("Offense", "offensive"), ("Defense", "defensive"),
                                             ("Possession", "possession"), ("Efficiency", "efficiency"), ("Discipline", "discipline")]):
        val = s[key]
        with col:
            st.metric(label, f"{val:.0f}")

    # layout: radar on left, core+advanced stats and game trend on right
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.plotly_chart(make_radar_chart(s, p["pos"]), use_container_width=True, key=f"radar_{selected_player}")

    with col_right:
        # core stats and advanced side by side
        cs_col, adv_col = st.columns(2)
        with cs_col:
            st.write("**Core Stats**")
            if p["pos"] != "GK":
                r1a, r1b, r1c, r1d = st.columns(4)
                r1a.metric("G", p["g"]); r1b.metric("A", p["a"])
                r1c.metric("PTS", p["pts"]); r1d.metric("SH%", f"{p['sh_pct']:.0f}%" if p["sh"] > 0 else "—")
                r2a, r2b, r2c, r2d = st.columns(4)
                r2a.metric("GB", p["gb"]); r2b.metric("DC", p["dc"])
                r2c.metric("TO", p["to"]); r2d.metric("CT", p["ct"])
            else:
                if "gk_sv_pct" in p:
                    r1a, r1b = st.columns(2)
                    r1a.metric("SV%", f"{p['gk_sv_pct']:.1f}%"); r1b.metric("GAA", f"{p['gk_gaa']:.2f}")
                    r2a, r2b = st.columns(2)
                    r2a.metric("Saves", p["gk_sv"]); r2b.metric("GA", p["gk_ga"])
                    r3a, r3b = st.columns(2)
                    r3a.metric("W-L", f"{p.get('gk_w',0)}-{p.get('gk_l',0)}"); r3b.metric("GB", p["gb"])
        with adv_col:
            st.write("**Advanced**")
            if p["pos"] != "GK" and p["sh"] > 0:
                a1, a2 = st.columns(2)
                a1.metric("Pts/Shot", f"{m['pts_per_shot']:.2f}"); a2.metric("TO Rate", f"{m['to_rate']:.2f}")
                a3, a4 = st.columns(2)
                a3.metric("Poss Impact", f"{m['poss_impact']:+d}"); a4.metric("Consistency", f"{m['consistency']:.2f}")

        # game-by-game trend below stats, still inside right column
        st.write("**Game-by-Game Trend**")
        st.plotly_chart(make_game_log_chart(p, games), use_container_width=True, key=f"gl_{selected_player}")

    # shot funnel for shooters
    if p["sh"] >= 3 and p["pos"] != "GK":
        st.write("**Shot Funnel**")
        st.plotly_chart(make_shot_efficiency_bar(p), use_container_width=True, key=f"sf_{selected_player}")

    # coaching notes
    st.info(data["notes"])

    if data["recs"]:
        for rec in data["recs"]:
            st.caption(rec)
