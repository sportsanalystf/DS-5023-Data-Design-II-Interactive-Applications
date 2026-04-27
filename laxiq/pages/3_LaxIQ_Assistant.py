# LaxIQ Assistant - chat page powered by Gemini

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

st.set_page_config(
    page_title="LaxIQ Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(CSS, unsafe_allow_html=True)

# sidebar
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

    st.button("🗑️ Clear Chat", on_click=clear_chat, key="clear_chat_btn",
              use_container_width=True, help="Clear all messages and start a new conversation")

    st.markdown("---")
    st.caption("Powered by Google Gemini")
    st.caption("Ask me about UVA lacrosse stats, player performance, game breakdowns, and more.")

# chat page styles
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
</style>
""", unsafe_allow_html=True)

# header
st.markdown("""<div class="chat-header">
    <h1>🤖 LaxIQ Assistant</h1>
    <div class="sub">AI-powered analytics assistant for UVA Women's Lacrosse · Ask about stats, players, games, and strategy</div>
</div>""", unsafe_allow_html=True)

# check API key
if not validate_api_key():
    st.error(
        "⚠️ **Gemini API key not found.** "
        "Please add `GEMINI_API_KEY = \"your-key\"` to `laxiq/.streamlit/secrets.toml`. "
        "You can get a free key at [Google AI Studio](https://aistudio.google.com/apikey)."
    )
    st.stop()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# show example prompts when chat is empty
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
    cols = st.columns(4)
    for i, prompt in enumerate(example_prompts):
        with cols[i % 4]:
            if st.button(prompt, key=f"example_{i}", use_container_width=True):
                st.session_state["_example_prompt"] = prompt
                st.rerun()

    # handle clicked example prompt
    if "_example_prompt" in st.session_state:
        user_input = st.session_state.pop("_example_prompt")
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("LaxIQ is analyzing..."):
                response_text = send_message(user_input)
            st.markdown(response_text)
        st.session_state["messages"].append({"role": "assistant", "content": response_text})
        st.stop()

# show previous messages
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# chat input
user_input = st.chat_input("Ask LaxIQ about UVA lacrosse...", key="chat_input")

if user_input:
    # check for empty input
    if not user_input.strip():
        st.warning("⚠️ Please enter a question before sending.")
        st.stop()

    # check message length
    if len(user_input) > 2000:
        st.warning(
            f"⚠️ Your message is {len(user_input)} characters long (limit: 2000). "
            "Please shorten your question for best results."
        )
        st.stop()

    # block injection attempts
    if check_prompt_injection(user_input):
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        injection_response = (
            "I'm **LaxIQ**, and I specialize in UVA Women's Lacrosse analytics. "
            "I stay in character at all times and can't change my role or instructions. "
            "How can I help you with lacrosse stats, player analysis, or game breakdowns?"
        )
        st.session_state["messages"].append({"role": "assistant", "content": injection_response})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(injection_response)
        st.stop()

    # show user message
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # get response from Gemini
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("LaxIQ is analyzing..."):
            response_text = send_message(user_input)
        st.markdown(response_text)

    st.session_state["messages"].append({"role": "assistant", "content": response_text})
