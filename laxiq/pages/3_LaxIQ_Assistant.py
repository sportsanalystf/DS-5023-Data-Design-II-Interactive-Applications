"""
LaxIQ Assistant — Gemini-powered analytics chatbot for UVA Women's Lacrosse.
Milestone 4: Full-page chat interface with persistent conversation,
input validation, prompt injection defense, and loading feedback.
"""

import streamlit as st
from style import CSS, UVA_BLUE, UVA_ORANGE

try:
    from gemini_chat import (
        validate_api_key, send_message, clear_chat,
        check_prompt_injection,
    )
    CHAT_AVAILABLE = True
except ImportError:
    CHAT_AVAILABLE = False

# ── Page config ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="LaxIQ Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(CSS, unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────

with st.sidebar:
    import os, base64
    _logo_dir = os.path.dirname(os.path.dirname(__file__))
    _logo_path = os.path.join(_logo_dir, "assets", "va_logo.png")
    if os.path.exists(_logo_path):
        with open(_logo_path, "rb") as _f:
            _b64 = base64.b64encode(_f.read()).decode()
        st.markdown(f"""<a href="https://virginiasports.com" target="_blank"
            style="display:block;text-align:center;margin-bottom:8px;">
            <img src="data:image/png;base64,{_b64}" style="max-width:180px;margin:0 auto;" />
        </a>""", unsafe_allow_html=True)

    st.markdown(
        f'<h2 style="margin:0;letter-spacing:1px;font-family:Bebas Neue,sans-serif;'
        f'color:{UVA_BLUE} !important;">⚔️ LaxIQ</h2>',
        unsafe_allow_html=True,
    )
    st.caption("Cavaliers Analytics Application")
    st.divider()
    st.page_link("Home.py", label="🏠 Season Overview")
    st.page_link("pages/1_Game_Analysis.py", label="📊 Game Analysis")
    st.page_link("pages/2_Player_Intelligence.py", label="⚔️ Player Intelligence")
    st.page_link("pages/3_LaxIQ_Assistant.py", label="🤖 LaxIQ Assistant")

    st.divider()

    if not CHAT_AVAILABLE:
        st.warning("Install google-generativeai to use chat")
        st.stop()

    # Clear chat button (on_click callback — no st.rerun needed)
    st.button("🗑️ Clear Chat", on_click=clear_chat, key="clear_chat_btn",
              use_container_width=True, help="Clear all messages and start a new conversation")

    st.markdown("---")
    st.caption("Powered by Google Gemini")
    st.caption("Ask me about UVA lacrosse stats, player performance, game breakdowns, and more.")

# ── Custom CSS for chat ──────────────────────────────────────────────

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;600;700&display=swap');

.chat-header {{
    background: linear-gradient(135deg, {UVA_BLUE} 0%, #1a2238 60%, {UVA_ORANGE} 100%);
    border-radius: 14px; padding: 1.5rem 2rem; margin-bottom: 1.2rem;
    color: white;
}}
.chat-header h1 {{
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 2.4rem; letter-spacing: 2px; margin: 0; line-height: 1;
    color: white !important;
}}
.chat-header .sub {{
    color: rgba(255,255,255,0.7); font-size: 0.85rem; margin-top: 4px;
}}
.example-chip {{
    display: inline-block; background: {UVA_BLUE}10;
    border: 1px solid {UVA_BLUE}30; border-radius: 20px;
    padding: 6px 14px; margin: 4px; font-size: 0.82rem;
    color: {UVA_BLUE}; cursor: default;
}}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────

st.markdown("""<div class="chat-header">
    <h1>🤖 LaxIQ Assistant</h1>
    <div class="sub">AI-powered analytics assistant for UVA Women's Lacrosse · Ask about stats, players, games, and strategy</div>
</div>""", unsafe_allow_html=True)

# ── API key validation ───────────────────────────────────────────────

if not validate_api_key():
    st.error(
        "⚠️ **Gemini API key not found.** "
        "Please add `GEMINI_API_KEY = \"your-key\"` to `laxiq/.streamlit/secrets.toml`. "
        "You can get a free key at [Google AI Studio](https://aistudio.google.com/apikey)."
    )
    st.stop()

# ── Initialize message history ───────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ── Example prompts (shown when chat is empty) ───────────────────────

if not st.session_state["messages"]:
    st.markdown("**Try asking:**")
    example_prompts = [
        "Who is our leading scorer this season?",
        "How did we perform against ranked opponents?",
        "Compare Jayden Piraino and Addi Foster",
        "Which games did we struggle offensively?",
        "What does the Impact score measure?",
        "How does the draw control analysis work?",
    ]
    st.markdown(
        " ".join(f'<span class="example-chip">{p}</span>' for p in example_prompts),
        unsafe_allow_html=True,
    )
    st.markdown("")

# ── Render conversation history ──────────────────────────────────────
# Messages persist across reruns; the full conversation re-renders every time.

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# ── Chat input ───────────────────────────────────────────────────────

user_input = st.chat_input("Ask LaxIQ about UVA lacrosse...", key="chat_input")

if user_input:
    # ── Input validation: empty / whitespace ─────────────────────
    if not user_input.strip():
        st.warning("⚠️ Please enter a question before sending.")
        st.stop()

    # ── Input validation: very long prompts (>2000 chars) ────────
    if len(user_input) > 2000:
        st.warning(
            f"⚠️ Your message is {len(user_input)} characters long (limit: 2000). "
            "Please shorten your question for best results."
        )
        st.stop()

    # ── Prompt injection defense ─────────────────────────────────
    if check_prompt_injection(user_input):
        # Display the user's message
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Respond with a firm but friendly redirect
        injection_response = (
            "I'm **LaxIQ**, and I specialize in UVA Women's Lacrosse analytics. "
            "I stay in character at all times and can't change my role or instructions. "
            "How can I help you with lacrosse stats, player analysis, or game breakdowns?"
        )
        st.session_state["messages"].append({"role": "assistant", "content": injection_response})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(injection_response)
        st.stop()

    # ── Display user message ─────────────────────────────────────
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ── Call Gemini with spinner ─────────────────────────────────
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("LaxIQ is analyzing..."):
            response_text = send_message(user_input)
        st.markdown(response_text)

    # ── Save assistant response ──────────────────────────────────
    st.session_state["messages"].append({"role": "assistant", "content": response_text})
