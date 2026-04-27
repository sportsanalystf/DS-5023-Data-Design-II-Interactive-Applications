# shared sidebar for all pages
import streamlit as st
import os
import base64
from analytics import list_games, load_game
from style import UVA_ORANGE, UVA_BLUE


def render_sidebar(show_game_selector=False):
    """Render sidebar with logo, nav links, and optional game selector."""
    with st.sidebar:
        # logo
        _logo_dir = os.path.dirname(__file__)
        _logo_path = os.path.join(_logo_dir, "assets", "va_logo.png")
        if os.path.exists(_logo_path):
            with open(_logo_path, "rb") as _f:
                _b64 = base64.b64encode(_f.read()).decode()
            st.markdown(f"""<a href="https://virginiasports.com" target="_blank" style="display:block;text-align:center;margin-bottom:8px;">
                <img src="data:image/png;base64,{_b64}" style="max-width:180px;margin:0 auto;" />
            </a>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<a href="https://virginiasports.com" target="_blank" style="text-decoration:none;">
                <div style="background:linear-gradient(135deg, {UVA_ORANGE} 0%, #c75b00 100%);
                    border-radius:10px;padding:12px 16px;text-align:center;margin-bottom:8px;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;letter-spacing:2px;
                        color:white;line-height:1.1;">VIRGINIA ATHLETICS</div>
                </div>
            </a>""", unsafe_allow_html=True)

        st.markdown(f'<h2 style="margin:0;letter-spacing:1px;font-family:Bebas Neue,sans-serif;color:{UVA_BLUE} !important;">⚔️ LaxIQ</h2>', unsafe_allow_html=True)
        st.caption("Cavaliers Analytics Application")
        st.divider()
        st.page_link("Home.py", label="🏠 Season Overview")
        st.page_link("pages/1_Game_Analysis.py", label="📊 Game Analysis")
        st.page_link("pages/2_Player_Intelligence.py", label="⚔️ Player Intelligence")
        st.page_link("pages/3_LaxIQ_Assistant.py", label="🤖 LaxIQ Assistant")

        if show_game_selector:
            st.divider()

            games = list_games()
            if not games:
                st.error("No game data found in data/ folder.")
                st.stop()

            # preselect from home page navigation
            pre_selected_idx = 0
            if "selected_game" in st.session_state:
                for i, g in enumerate(games):
                    if g["file"] == st.session_state["selected_game"].get("file"):
                        pre_selected_idx = i
                        break

            # build game labels with W/L prefix
            game_labels = []
            for g in games:
                r = g.get("result", "")
                prefix = "W" if r == "W" else "L"
                game_labels.append(f"[{prefix}] {g['label']}")

            selected_idx = st.selectbox("Select Game", range(len(games)),
                                        index=pre_selected_idx,
                                        format_func=lambda i: game_labels[i],
                                        key="game_selector")
            st.session_state["selected_game"] = games[selected_idx]
            st.session_state["selected_sheets"] = load_game(games[selected_idx]["file"])

            # show selected game indicator
            sel_r = games[selected_idx].get("result", "")
            sel_badge_bg = "#2E7D32" if sel_r == "W" else "#C62828"
            sel_badge = "W" if sel_r == "W" else "L"
            st.markdown(f"""<div style="background:rgba(255,255,255,0.12);border-radius:8px;padding:8px 12px;
                margin-top:4px;text-align:center;">
                <span style="background:{sel_badge_bg};padding:2px 8px;border-radius:10px;
                    font-size:0.6rem;font-weight:700;letter-spacing:1px;color:white;">{sel_badge}</span>
                <span style="color:white;font-weight:600;font-size:0.8rem;margin-left:6px;">{games[selected_idx]['label']}</span>
            </div>""", unsafe_allow_html=True)
            st.divider()
