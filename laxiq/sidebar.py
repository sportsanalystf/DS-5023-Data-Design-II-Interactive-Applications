# shared sidebar for all pages
import streamlit as st
import os
from analytics import list_games, load_game
from style import UVA_ORANGE, UVA_BLUE


def render_sidebar(show_game_selector=False):
    """Render sidebar with logo, nav links, and optional game selector."""
    with st.sidebar:
        # logo
        _logo_dir = os.path.dirname(__file__)
        _logo_path = os.path.join(_logo_dir, "assets", "va_logo.png")
        if os.path.exists(_logo_path):
            st.image(_logo_path, width=180)
        else:
            st.write("Virginia Athletics")

        st.title("⚔️ LaxIQ")
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
            sel_badge = "W" if sel_r == "W" else "L"
            st.caption(f"**[{sel_badge}]** {games[selected_idx]['label']}")
            st.divider()
