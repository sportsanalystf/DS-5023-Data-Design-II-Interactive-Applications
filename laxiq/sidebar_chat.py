# sidebar chat panel

import streamlit as st
from gemini_chat import validate_api_key, send_message, clear_chat, check_prompt_injection
from style import UVA_BLUE, UVA_ORANGE


def render_sidebar_chat():
    """Render chat panel in sidebar."""
    with st.sidebar:
        st.markdown(
            f'<p style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;'
            f'letter-spacing:1px;color:{UVA_ORANGE};margin:12px 0 4px 0;">'
            f'🤖 Ask LaxIQ</p>',
            unsafe_allow_html=True,
        )

        if not validate_api_key():
            st.caption("⚠️ Add GEMINI_API_KEY to secrets.toml")
            return

        # initialize messages
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        # show recent messages
        recent = st.session_state["messages"][-6:]  # last 3 exchanges
        if recent:
            for msg in recent:
                role_icon = "🤖" if msg["role"] == "assistant" else "👤"
                # truncate long messages
                text = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
                st.markdown(
                    f'<div style="font-size:0.78rem;padding:4px 8px;margin:2px 0;'
                    f'background:{"#f0f2f6" if msg["role"] == "assistant" else "transparent"};'
                    f'border-radius:8px;">'
                    f'{role_icon} {text}</div>',
                    unsafe_allow_html=True,
                )

        # input field
        sidebar_input = st.text_input(
            "Quick question",
            key="sidebar_chat_input",
            placeholder="Ask about stats...",
            label_visibility="collapsed",
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            send_btn = st.button("Send", key="sidebar_send_btn", use_container_width=True)
        with col2:
            st.button("🗑️", on_click=clear_chat, key="sidebar_clear_btn",
                       help="Clear chat")

        if send_btn and sidebar_input and sidebar_input.strip():
            # validate input
            if len(sidebar_input) > 2000:
                st.warning("Message too long (max 2000 chars)")
                return

            if check_prompt_injection(sidebar_input):
                st.session_state["messages"].append({"role": "user", "content": sidebar_input})
                rsp = ("I'm LaxIQ — I stay in character and specialize in UVA lacrosse analytics. "
                       "How can I help with stats or game analysis?")
                st.session_state["messages"].append({"role": "assistant", "content": rsp})
                st.rerun()
                return

            st.session_state["messages"].append({"role": "user", "content": sidebar_input})
            with st.spinner("Thinking..."):
                rsp = send_message(sidebar_input)
            st.session_state["messages"].append({"role": "assistant", "content": rsp})
            st.rerun()

        # link to full chat
        st.page_link("pages/3_LaxIQ_Assistant.py", label="Open full chat →",
                      icon="💬")
