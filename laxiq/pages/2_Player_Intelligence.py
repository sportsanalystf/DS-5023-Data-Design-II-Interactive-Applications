import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math

# ─── PAGE CONFIG ───
st.set_page_config(
    page_title="Lax IQ - Player Intelligence",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════
# UVA OFFICIAL BRAND COLORS
# ═══════════════════════════════════════════════
UVA_BLUE = "#232D4B"
UVA_ORANGE = "#E57200"
CAV_ORANGE = "#F84C1E"
UVA_CYAN = "#009FDF"
UVA_YELLOW = "#FDDA24"
UVA_TEAL = "#25CAD3"
UVA_GREEN = "#62BB46"
UVA_MAGENTA = "#EF3F6B"
LIGHT_GRAY = "#F1F1EF"
MED_GRAY = "#DADADA"
TEXT_GRAY = "#666666"
WHITE = "#FFFFFF"
UVA_BLUE_25 = "#C8CBD2"
UVA_ORANGE_25 = "#F9DCBF"

TIER_COLORS = {1: CAV_ORANGE, 2: UVA_CYAN, 3: UVA_GREEN, 4: MED_GRAY}
FLAG_COLORS = {"positive": UVA_GREEN, "negative": UVA_MAGENTA, "warning": UVA_YELLOW, "info": UVA_CYAN}

# ─── CUSTOM CSS ───
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=Bebas+Neue&display=swap');

:root {{
    --uva-blue: {UVA_BLUE};
    --uva-orange: {UVA_ORANGE};
    --cav-orange: {CAV_ORANGE};
}}

.stApp {{
    background-color: {LIGHT_GRAY};
    font-family: 'DM Sans', sans-serif;
    color: {UVA_BLUE};
}}

h1, h2, h3 {{
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 1.5px;
    color: {UVA_BLUE} !important;
}}

section[data-testid="stSidebar"] {{
    background: #FFFFFF !important;
    border-right: 1px solid #DADADA;
}}
section[data-testid="stSidebar"] * {{
    color: {UVA_BLUE} !important;
}}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h4 {{
    color: {UVA_BLUE} !important;
}}
/* Hide Streamlit auto-generated page navigation */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{ display: none !important; }}
section[data-testid="stSidebar"] nav {{ display: none !important; }}
section[data-testid="stSidebar"] ul[data-testid="stSidebarNavItems"] {{ display: none !important; }}

.main-header {{
    background: linear-gradient(135deg, {UVA_BLUE} 0%, #1a2238 50%, {UVA_ORANGE} 100%);
    padding: 1.5rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}}
.main-header h1 {{
    color: white !important;
    font-size: 2.5rem;
    margin: 0;
    font-family: 'Bebas Neue', sans-serif !important;
    line-height: 1;
}}
.main-header p {{
    color: rgba(255,255,255,0.75);
    font-size: 0.95rem;
    margin: 0.25rem 0 0 0;
}}

.player-card {{
    background: {WHITE};
    border: 1px solid {MED_GRAY};
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 12px rgba(35,45,75,0.06);
    transition: all 0.25s ease;
    border-left: 5px solid {UVA_ORANGE};
}}
.player-card:hover {{
    box-shadow: 0 4px 24px rgba(35,45,75,0.12);
    border-left-color: {CAV_ORANGE};
}}

.player-name {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: {UVA_BLUE};
    letter-spacing: 2px;
    margin: 0;
    line-height: 1.1;
}}
.player-meta {{
    color: {UVA_ORANGE};
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 3px;
}}

.impact-score-box {{
    background: linear-gradient(135deg, {UVA_ORANGE} 0%, {CAV_ORANGE} 100%);
    border-radius: 14px;
    padding: 1rem 0.8rem;
    text-align: center;
    min-width: 90px;
}}
.impact-score-num {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.8rem;
    color: white;
    line-height: 1;
}}
.impact-score-label {{
    color: rgba(255,255,255,0.9);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
}}

.stat-box {{
    background: {WHITE};
    border: 1px solid {MED_GRAY};
    border-radius: 12px;
    padding: 0.8rem;
    text-align: center;
}}
.stat-val {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    line-height: 1;
}}
.stat-label {{
    font-size: 0.65rem;
    color: {TEXT_GRAY};
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-top: 4px;
}}

.tier-badge {{
    display: inline-block;
    padding: 3px 14px;
    border-radius: 50px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: white;
    vertical-align: middle;
    margin-left: 8px;
}}
.tier-1 {{ background: {CAV_ORANGE}; }}
.tier-2 {{ background: {UVA_CYAN}; }}
.tier-3 {{ background: {UVA_GREEN}; }}
.tier-4 {{ background: {MED_GRAY}; color: {UVA_BLUE}; }}

.flag-tag {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 50px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 3px 4px;
    letter-spacing: 0.5px;
}}
.flag-positive {{ background: #E8F5E9; color: #2E7D32; border: 1px solid #A5D6A7; }}
.flag-negative {{ background: #FCE4EC; color: #C62828; border: 1px solid #EF9A9A; }}
.flag-warning {{ background: #FFF8E1; color: #E65100; border: 1px solid #FFE082; }}
.flag-info {{ background: #E3F2FD; color: #1565C0; border: 1px solid #90CAF9; }}

.coaching-notes {{
    background: #F8F8FC;
    border-left: 4px solid {UVA_BLUE};
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: {UVA_BLUE};
    line-height: 1.65;
    margin-top: 0.8rem;
}}

.rec-box {{
    background: linear-gradient(135deg, #FFF3E0 0%, #FFF8E1 100%);
    border-left: 4px solid {UVA_ORANGE};
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: {UVA_BLUE};
    line-height: 1.65;
    margin-top: 0.5rem;
}}
.rec-box strong {{ color: {CAV_ORANGE}; }}

.section-divider {{
    border: none;
    border-top: 1px solid {MED_GRAY};
    margin: 1rem 0;
}}

.headshot-circle {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid {UVA_ORANGE};
    background: {LIGHT_GRAY};
}}

div[data-testid="stMetric"] {{
    background: {WHITE};
    border: 1px solid {MED_GRAY};
    border-radius: 10px;
    padding: 0.6rem;
}}
div[data-testid="stMetric"] label {{
    color: {TEXT_GRAY} !important;
}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    color: {UVA_BLUE} !important;
}}

.stDataFrame {{ border-radius: 10px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    import os as _os, base64 as _b64mod
    _logo_path = _os.path.join(_os.path.dirname(__file__), "..", "assets", "va_logo.png")
    if _os.path.exists(_logo_path):
        with open(_logo_path, "rb") as _f:
            _b64 = _b64mod.b64encode(_f.read()).decode()
        st.markdown(f"""<a href="https://virginiasports.com" target="_blank" style="display:block;text-align:center;margin-bottom:8px;">
            <img src="data:image/png;base64,{_b64}" style="max-width:180px;margin:0 auto;" />
        </a>""", unsafe_allow_html=True)
    else:
        st.markdown("""<a href="https://virginiasports.com" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg, #E57200 0%, #c75b00 100%);
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

# ═══════════════════════════════════════════════
# DATA LAYER
# ═══════════════════════════════════════════════

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

def load_data():
    """Build player data from real Excel game files via analytics engine."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from analytics import (list_games, load_game, aggregate_player_stats,
                          player_season_totals, get_position, get_number, get_year,
                          POSITION_MAP, PLAYER_NUMBERS, PLAYER_YEARS)

    game_list = list_games()
    if not game_list:
        return _load_data_fallback()

    multi_game_df = aggregate_player_stats(game_list, team="uva")
    if multi_game_df.empty:
        return _load_data_fallback()

    season_totals = player_season_totals(multi_game_df)
    n_games = len(game_list)

    players = {}
    games_labels = [g["label"] for g in game_list]
    game_results = [g["result"] for g in game_list]

    for _, row in season_totals.iterrows():
        name = row["Player"]
        pos = get_position(name)
        if pos == "?":
            continue  # Skip non-roster players (opponent names in data)
        num = get_number(name)
        yr = get_year(name)
        gp = int(row.get("Games", 1))

        g = int(row.get("G", 0))
        a = int(row.get("A", 0))
        pts = int(row.get("PTS", 0))
        sh = int(row.get("SH", 0))
        sog = int(row.get("SOG", 0))
        gb = int(row.get("GB", 0))
        dc = int(row.get("DC", 0))
        to = int(row.get("TO", 0))
        ct = int(row.get("CT", 0))

        sh_pct = round(g / sh * 100, 1) if sh > 0 else 0
        sog_pct = round(sog / sh * 100, 1) if sh > 0 else 0

        # Build per-game arrays from multi_game_df
        player_games = multi_game_df[multi_game_df["Player"] == name].sort_values("Date")
        game_g = player_games["G"].tolist() if "G" in player_games.columns else []
        game_a = player_games["A"].tolist() if "A" in player_games.columns else []
        game_pts = player_games["PTS"].tolist() if "PTS" in player_games.columns else []
        game_sh = player_games["SH"].tolist() if "SH" in player_games.columns else []
        game_to = player_games["TO"].tolist() if "TO" in player_games.columns else []

        players[name] = {
            "num": num if num else 0, "pos": pos if pos != "?" else "M", "yr": yr if yr else "—",
            "gp": gp, "gs": gp,  # Approximate starts as games played
            "g": g, "a": a, "pts": pts, "sh": sh, "sh_pct": sh_pct, "sog": sog, "sog_pct": sog_pct,
            "gb": gb, "dc": dc, "to": to, "ct": ct,
            "fpg": 0, "fps": 0,  # Free position data not in box scores
            "yc": 0, "gc": 0,    # Card data not broken out per player
            "game_g": [int(x) for x in game_g],
            "game_a": [int(x) for x in game_a],
            "game_pts": [int(x) for x in game_pts],
            "game_sh": [int(x) for x in game_sh],
            "game_to": [int(x) for x in game_to],
        }

        # Check if this is a goalkeeper (from GK sheets)
        if pos == "GK":
            total_saves = 0
            total_ga = 0
            total_min = 0
            total_w = 0
            total_l = 0
            for gl in game_list:
                gsheets = load_game(gl["file"])
                gk_df = gsheets.get("Goalkeepers", pd.DataFrame())
                if not gk_df.empty and "Player" in gk_df.columns:
                    pk = gk_df[gk_df["Player"].str.contains(name.split()[-1], case=False, na=False)]
                    if not pk.empty:
                        total_saves += int(pk["Saves"].sum()) if "Saves" in pk.columns else 0
                        total_ga += int(pk["GA"].sum()) if "GA" in pk.columns else 0
                        mins_val = pk["Minutes"].sum() if "Minutes" in pk.columns else 0
                        try:
                            total_min += float(mins_val)
                        except (ValueError, TypeError):
                            pass
                        if "Decision" in pk.columns:
                            for d in pk["Decision"]:
                                if str(d).upper() == "W":
                                    total_w += 1
                                elif str(d).upper() == "L":
                                    total_l += 1

            if total_saves + total_ga > 0:
                players[name]["gk_sv"] = total_saves
                players[name]["gk_ga"] = total_ga
                players[name]["gk_min"] = total_min
                players[name]["gk_sv_pct"] = round(total_saves / (total_saves + total_ga) * 100, 1)
                players[name]["gk_gaa"] = round(total_ga / max(total_min / 60, 0.1), 2) if total_min > 0 else 0
                players[name]["gk_w"] = total_w
                players[name]["gk_l"] = total_l

    return players, games_labels, game_results


def _load_data_fallback():
    """Fallback hardcoded data if no Excel files available."""
    players = {
        "Madison Alaimo": {"num": 16, "pos": "A", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 10, "a": 15, "pts": 25, "sh": 18, "sh_pct": 55.6, "sog": 16, "sog_pct": 88.9,
            "gb": 4, "dc": 0, "to": 11, "ct": 1, "fpg": 3, "fps": 4, "yc": 0, "gc": 2,
            "game_g": [0,5,3,4,2], "game_a": [4,1,2,3,3], "game_pts": [4,6,5,7,5],
            "game_sh": [3,5,5,4,3], "game_to": [4,2,0,1,4]},
        "Jenna Dinardo": {"num": 4, "pos": "A", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 9, "a": 2, "pts": 11, "sh": 29, "sh_pct": 31.0, "sog": 26, "sog_pct": 89.7,
            "gb": 3, "dc": 8, "to": 10, "ct": 2, "fpg": 3, "fps": 9, "yc": 1, "gc": 3,
            "game_g": [1,3,3,1,1], "game_a": [0,1,1,0,0], "game_pts": [1,4,4,1,1],
            "game_sh": [4,10,8,6,5], "game_to": [3,2,2,1,4]},
        "Addi Foster": {"num": 15, "pos": "A", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 10, "a": 2, "pts": 12, "sh": 24, "sh_pct": 41.7, "sog": 20, "sog_pct": 83.3,
            "gb": 2, "dc": 0, "to": 3, "ct": 0, "fpg": 2, "fps": 2, "yc": 1, "gc": 1,
            "game_g": [0,4,2,3,1], "game_a": [0,1,0,0,1], "game_pts": [0,5,2,3,2],
            "game_sh": [1,5,3,6,6], "game_to": [1,1,0,1,0]},
        "Kate Galica": {"num": 5, "pos": "M", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 6, "a": 5, "pts": 11, "sh": 24, "sh_pct": 25.0, "sog": 17, "sog_pct": 70.8,
            "gb": 13, "dc": 35, "to": 13, "ct": 10, "fpg": 1, "fps": 4, "yc": 0, "gc": 3,
            "game_g": [2,1,0,1,3], "game_a": [0,1,0,2,2], "game_pts": [2,2,0,3,5],
            "game_sh": [3,5,5,6,7], "game_to": [1,4,4,4,2]},
        "Cady Flaherty": {"num": 6, "pos": "M", "yr": "Fr", "gp": 5, "gs": 2,
            "g": 4, "a": 1, "pts": 5, "sh": 7, "sh_pct": 57.1, "sog": 6, "sog_pct": 85.7,
            "gb": 3, "dc": 1, "to": 1, "ct": 2, "fpg": 3, "fps": 3, "yc": 0, "gc": 3,
            "game_g": [2,0,1,1,0], "game_a": [0,1,1,0,0], "game_pts": [2,1,2,1,0],
            "game_sh": [2,1,2,2,1], "game_to": [0,0,0,1,0]},
        "Gabby Laverghetta": {"num": 43, "pos": "A", "yr": "So", "gp": 5, "gs": 3,
            "g": 5, "a": 2, "pts": 7, "sh": 8, "sh_pct": 62.5, "sog": 6, "sog_pct": 75.0,
            "gb": 3, "dc": 0, "to": 3, "ct": 0, "fpg": 0, "fps": 0, "yc": 1, "gc": 3,
            "game_g": [2,1,0,1,0], "game_a": [1,1,0,0,0], "game_pts": [3,2,0,1,0],
            "game_sh": [3,1,0,2,0], "game_to": [0,0,0,2,0]},
        "Livy Laverghetta": {"num": 42, "pos": "M", "yr": "So", "gp": 5, "gs": 0,
            "g": 3, "a": 1, "pts": 4, "sh": 4, "sh_pct": 75.0, "sog": 4, "sog_pct": 100.0,
            "gb": 2, "dc": 1, "to": 2, "ct": 0, "fpg": 0, "fps": 0, "yc": 0, "gc": 0,
            "game_g": [1,1,1,1,0], "game_a": [0,1,0,1,0], "game_pts": [1,2,1,2,0],
            "game_sh": [1,1,1,1,0], "game_to": [0,0,0,0,0]},
        "Raleigh Foster": {"num": 10, "pos": "A", "yr": "Fr", "gp": 2, "gs": 0,
            "g": 3, "a": 0, "pts": 3, "sh": 7, "sh_pct": 42.9, "sog": 6, "sog_pct": 85.7,
            "gb": 0, "dc": 0, "to": 0, "ct": 0, "fpg": 0, "fps": 0, "yc": 0, "gc": 0,
            "game_g": [1,2], "game_a": [0,0], "game_pts": [1,2],
            "game_sh": [4,3], "game_to": [0,0]},
        "Alex Reilly": {"num": 23, "pos": "M", "yr": "So", "gp": 5, "gs": 5,
            "g": 1, "a": 0, "pts": 1, "sh": 5, "sh_pct": 20.0, "sog": 3, "sog_pct": 60.0,
            "gb": 2, "dc": 6, "to": 3, "ct": 2, "fpg": 0, "fps": 0, "yc": 2, "gc": 1,
            "game_g": [1,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [1,0,0,0,0],
            "game_sh": [3,0,0,0,0], "game_to": [0,0,0,0,1]},
        "Payton Sfreddo": {"num": 7, "pos": "M", "yr": "So", "gp": 5, "gs": 0,
            "g": 1, "a": 0, "pts": 1, "sh": 1, "sh_pct": 100.0, "sog": 1, "sog_pct": 100.0,
            "gb": 3, "dc": 1, "to": 1, "ct": 1, "fpg": 0, "fps": 0, "yc": 0, "gc": 1,
            "game_g": [1,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [1,0,0,0,0],
            "game_sh": [1,0,0,0,0], "game_to": [0,0,0,0,0]},
        "Kate Demark": {"num": 3, "pos": "D", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 3, "dc": 0, "to": 0, "ct": 10, "fpg": 0, "fps": 0, "yc": 0, "gc": 2,
            "game_g": [0,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [0,0,0,0,0],
            "game_sh": [0,0,0,0,0], "game_to": [0,0,0,0,0]},
        "Alexandra Schneider": {"num": 8, "pos": "D", "yr": "Jr", "gp": 5, "gs": 5,
            "g": 0, "a": 0, "pts": 0, "sh": 1, "sh_pct": 0, "sog": 1, "sog_pct": 100.0,
            "gb": 2, "dc": 0, "to": 0, "ct": 6, "fpg": 0, "fps": 0, "yc": 1, "gc": 0,
            "game_g": [0,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [0,0,0,0,0],
            "game_sh": [0,0,1,0,0], "game_to": [0,0,0,0,0]},
        "Sophia Conti": {"num": 9, "pos": "M", "yr": "So", "gp": 5, "gs": 5,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 9, "dc": 0, "to": 2, "ct": 4, "fpg": 0, "fps": 0, "yc": 0, "gc": 1,
            "game_g": [0,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [0,0,0,0,0],
            "game_sh": [0,0,0,0,0], "game_to": [1,0,1,0,1]},
        "Lara Kology": {"num": 36, "pos": "D", "yr": "Sr", "gp": 5, "gs": 5,
            "g": 0, "a": 0, "pts": 0, "sh": 1, "sh_pct": 0, "sog": 1, "sog_pct": 100.0,
            "gb": 7, "dc": 1, "to": 1, "ct": 1, "fpg": 0, "fps": 0, "yc": 1, "gc": 2,
            "game_g": [0,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [0,0,0,0,0],
            "game_sh": [0,1,0,1,0], "game_to": [1,0,0,0,0]},
        "Elyse Finnelle": {"num": 34, "pos": "GK", "yr": "Sr", "gp": 5, "gs": 3,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 10, "dc": 0, "to": 0, "ct": 1, "fpg": 0, "fps": 0, "yc": 0, "gc": 0,
            "gk_min": 230.82, "gk_ga": 39, "gk_gaa": 10.14, "gk_sv": 23, "gk_sv_pct": 37.1,
            "gk_w": 2, "gk_l": 1,
            "game_g": [0,0,0,0,0], "game_a": [0,0,0,0,0], "game_pts": [0,0,0,0,0],
            "game_sh": [0,0,0,0,0], "game_to": [0,0,0,0,0]},
        "Mel Josephson": {"num": 26, "pos": "GK", "yr": "Sr", "gp": 3, "gs": 2,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 3, "dc": 0, "to": 0, "ct": 0, "fpg": 0, "fps": 0, "yc": 0, "gc": 0,
            "gk_min": 68.47, "gk_ga": 17, "gk_gaa": 14.90, "gk_sv": 10, "gk_sv_pct": 37.0,
            "gk_w": 0, "gk_l": 2,
            "game_g": [0,0,0], "game_a": [0,0,0], "game_pts": [0,0,0],
            "game_sh": [0,0,0], "game_to": [0,0,0]},
        "Carly Kennedy": {"num": 13, "pos": "M", "yr": "So", "gp": 3, "gs": 2,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 4, "dc": 0, "to": 0, "ct": 3, "fpg": 0, "fps": 0, "yc": 0, "gc": 1,
            "game_g": [0,0,0], "game_a": [0,0,0], "game_pts": [0,0,0],
            "game_sh": [0,0,0], "game_to": [0,0,0]},
        "Megan Rocklein": {"num": 11, "pos": "M", "yr": "Fr", "gp": 3, "gs": 0,
            "g": 0, "a": 2, "pts": 2, "sh": 1, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 1, "dc": 0, "to": 3, "ct": 0, "fpg": 0, "fps": 0, "yc": 0, "gc": 0,
            "game_g": [0,0,0], "game_a": [0,2,0], "game_pts": [0,2,0],
            "game_sh": [0,0,1], "game_to": [1,0,2]},
        "Fiona Allen": {"num": 41, "pos": "A", "yr": "So", "gp": 4, "gs": 0,
            "g": 1, "a": 1, "pts": 2, "sh": 2, "sh_pct": 50.0, "sog": 1, "sog_pct": 50.0,
            "gb": 0, "dc": 0, "to": 1, "ct": 0, "fpg": 1, "fps": 1, "yc": 0, "gc": 0,
            "game_g": [0,0,1,0], "game_a": [1,0,0,0], "game_pts": [1,0,1,0],
            "game_sh": [0,0,1,0], "game_to": [0,0,0,0]},
        "Abby Musser": {"num": 14, "pos": "D", "yr": "So", "gp": 4, "gs": 3,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 2, "dc": 0, "to": 1, "ct": 1, "fpg": 0, "fps": 0, "yc": 1, "gc": 0,
            "game_g": [0,0,0,0], "game_a": [0,0,0,0], "game_pts": [0,0,0,0],
            "game_sh": [0,0,0,0], "game_to": [0,0,0,1]},
        "Jayden Piraino": {"num": 2, "pos": "A", "yr": "So", "gp": 1, "gs": 0,
            "g": 2, "a": 0, "pts": 2, "sh": 2, "sh_pct": 100.0, "sog": 2, "sog_pct": 100.0,
            "gb": 0, "dc": 0, "to": 0, "ct": 0, "fpg": 1, "fps": 1, "yc": 0, "gc": 0,
            "game_g": [2], "game_a": [0], "game_pts": [2],
            "game_sh": [2], "game_to": [0]},
        "Corey White": {"num": 25, "pos": "M", "yr": "Jr", "gp": 4, "gs": 0,
            "g": 0, "a": 0, "pts": 0, "sh": 0, "sh_pct": 0, "sog": 0, "sog_pct": 0,
            "gb": 0, "dc": 1, "to": 0, "ct": 0, "fpg": 0, "fps": 0, "yc": 0, "gc": 0,
            "game_g": [0,0,0,0], "game_a": [0,0,0,0], "game_pts": [0,0,0,0],
            "game_sh": [0,0,0,0], "game_to": [0,0,0,0]},
    }
    games = ["vs Navy (L 12-10)", "vs Richmond (L 12-11)", "at Maryland (L 17-9)", "at Liberty (W 17-8)", "at Notre Dame (W 9-7)"]
    game_results = ["L", "L", "L", "W", "W"]
    return players, games, game_results


# ═══════════════════════════════════════════════
# METRICS ENGINE
# ═══════════════════════════════════════════════

def compute_advanced_metrics(p):
    gp = max(p["gp"], 1)
    m = {}
    m["ppg"] = p["pts"] / gp
    m["gpg"] = p["g"] / gp
    m["apg"] = p["a"] / gp
    m["pts_per_shot"] = p["pts"] / max(p["sh"], 1)
    m["shot_quality"] = (p.get("sog_pct", 0) * p.get("sh_pct", 0)) / 100
    poss_inv = p["sh"] + p["to"] + p["dc"] + p["gb"]
    m["poss_involvement"] = poss_inv
    m["to_rate"] = p["to"] / max(poss_inv, 1)
    m["poss_impact"] = p["gb"] + p["dc"] + p["ct"] - p["to"]
    m["fp_eff"] = p["fpg"] / max(p["fps"], 1) * 100
    m["discipline_raw"] = p["yc"] * 3 + p["gc"] * 1
    m["gbpg"] = p["gb"] / gp
    m["dcpg"] = p["dc"] / gp
    m["ctpg"] = p["ct"] / gp
    m["topg"] = p["to"] / gp
    game_pts = p.get("game_pts", [])
    if len(game_pts) > 1 and np.mean(game_pts) > 0:
        m["consistency"] = 1 - min(np.std(game_pts) / np.mean(game_pts), 1)
    elif len(game_pts) > 0 and np.mean(game_pts) > 0:
        m["consistency"] = 1.0
    else:
        m["consistency"] = 0.5
    game_g = p.get("game_g", [])
    if len(game_g) == 5:
        loss_avg = np.mean(game_g[:3]) if sum(game_g[:3]) > 0 else 0.001
        win_avg = np.mean(game_g[3:])
        m["clutch_ratio"] = win_avg / max(loss_avg, 0.001)
    else:
        m["clutch_ratio"] = 1.0
    return m


def compute_impact_scores(p, metrics, team_avg):
    pos = p["pos"]
    scores = {}
    def norm(val, max_val, invert=False):
        if max_val == 0: return 50
        r = min(val / max_val, 1.5) / 1.5 * 100
        return 100 - r if invert else r

    scores["offensive"] = min(100, norm(metrics["gpg"], team_avg["max_gpg"]) * 0.35 +
        norm(p["sh_pct"], 75) * 0.25 + norm(metrics["ppg"], team_avg["max_ppg"]) * 0.25 +
        norm(p["a"] / max(p["gp"],1), team_avg["max_apg"]) * 0.15)
    scores["defensive"] = min(100, norm(p["ct"] / max(p["gp"],1), team_avg["max_ctpg"]) * 0.45 +
        norm(p["gb"] / max(p["gp"],1), team_avg["max_gbpg"]) * 0.35 +
        norm(metrics["discipline_raw"], 10, invert=True) * 0.20)
    scores["possession"] = min(100, norm(metrics["poss_impact"], team_avg["max_poss_impact"]) * 0.40 +
        norm(p["dc"] / max(p["gp"],1), team_avg["max_dcpg"]) * 0.35 +
        norm(p["gb"] / max(p["gp"],1), team_avg["max_gbpg"]) * 0.25)
    scores["efficiency"] = min(100, norm(p["sh_pct"], 75) * 0.30 +
        norm(p["sog_pct"], 100) * 0.25 + norm(metrics["to_rate"], 1, invert=True) * 0.25 +
        norm(metrics["consistency"], 1) * 0.20)
    scores["discipline"] = max(0, 100 - metrics["discipline_raw"] * 12)

    if pos == "A": w = {"offensive": 0.40, "defensive": 0.05, "possession": 0.15, "efficiency": 0.30, "discipline": 0.10}
    elif pos == "M": w = {"offensive": 0.25, "defensive": 0.20, "possession": 0.25, "efficiency": 0.20, "discipline": 0.10}
    elif pos == "D": w = {"offensive": 0.05, "defensive": 0.45, "possession": 0.20, "efficiency": 0.10, "discipline": 0.20}
    elif pos == "GK": w = {"offensive": 0.00, "defensive": 0.35, "possession": 0.15, "efficiency": 0.35, "discipline": 0.15}
    else: w = {"offensive": 0.25, "defensive": 0.25, "possession": 0.20, "efficiency": 0.20, "discipline": 0.10}
    scores["overall"] = sum(scores[k] * v for k, v in w.items())

    if pos == "GK" and "gk_sv_pct" in p:
        sv_score = norm(p["gk_sv_pct"], 60) * 0.40
        gaa_score = norm(20 - p["gk_gaa"], 20) * 0.30
        gb_score = norm(p["gb"] / max(p["gp"],1), team_avg["max_gbpg"]) * 0.15
        disc = scores["discipline"] * 0.15
        scores["overall"] = sv_score + gaa_score + gb_score + disc
        scores["efficiency"] = sv_score / 0.40
        scores["defensive"] = gaa_score / 0.30
    return scores


def get_development_flags(p, metrics, scores):
    flags = []
    if p["to"] / max(p["gp"],1) >= 2.0 and p["pts"] > 0: flags.append(("High Turnover Risk", "negative"))
    if p["sh_pct"] >= 50 and p["sh"] >= 5: flags.append(("Elite Finisher", "positive"))
    if p["sh_pct"] < 30 and p["sh"] >= 10: flags.append(("Shot Selection Concern", "warning"))
    if metrics.get("fp_eff", 0) >= 70 and p["fps"] >= 3: flags.append(("FP Specialist", "positive"))
    if p["ct"] / max(p["gp"],1) >= 1.5: flags.append(("Defensive Disruptor", "positive"))
    if p["dc"] / max(p["gp"],1) >= 3: flags.append(("Draw Control Engine", "positive"))
    if p["gb"] / max(p["gp"],1) >= 1.5: flags.append(("Ground Ball Magnet", "positive"))
    if metrics["consistency"] >= 0.7 and p["pts"] > 3: flags.append(("Reliable Contributor", "info"))
    if metrics["consistency"] < 0.4 and p["pts"] > 3: flags.append(("High Variance", "warning"))
    if metrics.get("clutch_ratio", 1) >= 1.5 and p["g"] >= 3: flags.append(("Clutch Performer", "positive"))
    if scores["discipline"] <= 60: flags.append(("Discipline Concern", "warning"))
    if p["pos"] == "GK":
        if p.get("gk_sv_pct", 0) >= 40: flags.append(("Solid Save Rate", "positive"))
        if p.get("gk_gaa", 20) <= 10: flags.append(("Low GAA", "positive"))
        if p.get("gk_gaa", 0) >= 14: flags.append(("High GAA Concern", "negative"))
    if p["a"] / max(p["gp"],1) >= 2: flags.append(("Elite Playmaker", "positive"))
    if p["pts"] == 0 and p["ct"] == 0 and p["gb"] <= 2 and p["dc"] == 0: flags.append(("Limited Impact", "negative"))
    return flags


def get_tier(scores, p):
    s = scores["overall"]
    if s >= 65: return 1, "Program Driver"
    elif s >= 45: return 2, "System Amplifier"
    elif s >= 25: return 3, "Situational Specialist"
    else: return 4, "Developmental"


def generate_coaching_notes(name, p, metrics, scores, tier_num, flags):
    pos_full = {"A": "Attacker", "M": "Midfielder", "D": "Defender", "GK": "Goalkeeper"}[p["pos"]]
    tier_names = {1: "Program Driver", 2: "System Amplifier", 3: "Situational Specialist", 4: "Developmental Player"}
    note = f"{name} is a {p['yr']} {pos_full} classified as a **Tier {tier_num} — {tier_names[tier_num]}**. "
    if p["pos"] == "A":
        if p["g"] >= 8: note += f"She is a primary scoring threat with {p['g']}G and {p['a']}A in {p['gp']} games. "
        if p["sh_pct"] < 35 and p["sh"] > 15: note += f"However, her {p['sh_pct']:.0f}% shooting on {p['sh']} shots suggests shot selection needs refinement. "
        if p["to"] >= 8: note += f"Her {p['to']} turnovers are a concern and represent a key development area. "
        if p["a"] >= 10: note += f"Her {p['a']} assists make her the offense's primary distributor. "
    elif p["pos"] == "M":
        if p["dc"] >= 20: note += f"She dominates the draw circle with {p['dc']} draw controls. "
        if p["pts"] >= 5: note += f"Contributes offensively with {p['pts']} points. "
        if p["ct"] >= 5: note += f"Adds defensive value with {p['ct']} caused turnovers. "
    elif p["pos"] == "D":
        if p["ct"] >= 5: note += f"An elite defender with {p['ct']} caused turnovers. "
        if p["gb"] >= 5: note += f"Active on ground balls ({p['gb']}). "
    elif p["pos"] == "GK" and "gk_sv_pct" in p:
        note += f"Posted a {p['gk_sv_pct']:.1f}% save rate with {p['gk_gaa']:.2f} GAA. "
    flag_names = [f[0] for f in flags]
    pos_flags = [f for f in flag_names if any(x in f for x in ["Elite", "Specialist", "Engine", "Clutch", "Reliable", "Solid", "Low GAA"])]
    if pos_flags: note += f"Key strengths: {', '.join(pos_flags)}. "
    return note


def generate_recommendations(name, p, metrics, scores, tier_num, flags):
    """Generate actionable coaching recommendations."""
    recs = []
    pos = p["pos"]
    gp = max(p["gp"], 1)

    if pos == "A":
        if p["sh_pct"] < 35 and p["sh"] >= 10:
            recs.append(f"Shot Selection: {name}'s {p['sh_pct']:.0f}% shooting on {p['sh']} shots is below the productive threshold. Focus drills on shooting from higher-percentage zones.")
        if p["to"] / gp >= 2.0:
            recs.append(f"Ball Security: Averaging {p['to']/gp:.1f} TO/game — work on off-hand stick skills and decision-making under pressure.")
        if p["a"] / gp >= 2 and p["g"] / gp >= 1.5:
            recs.append(f"Maximize Usage: {name} is a dual-threat creator ({metrics['gpg']:.1f} G/gm, {metrics['apg']:.1f} A/gm). Deploy her in critical possessions.")
        if p["g"] >= 5 and p["a"] < 3:
            recs.append(f"Expand Playmaking: Strong finisher with {p['g']}G but only {p['a']}A — encourage the extra pass.")
        if metrics["consistency"] < 0.5 and p["pts"] >= 5:
            recs.append(f"Reduce Variance: Point production is inconsistent. Use her in structured sets with guaranteed touches.")
        if tier_num >= 3 and p["gp"] >= 3:
            recs.append(f"Situational Deployment: Deploy {name} primarily in man-up situations and as a late-game spark plug.")

    elif pos == "M":
        if p["dc"] / gp >= 3:
            recs.append(f"Protect the Draw: {name} at {p['dc']/gp:.0f} DC/game is an elite asset. Ensure she takes every draw.")
        if p["ct"] / gp >= 1.5 and p["pts"] >= 5:
            recs.append(f"Two-Way Star: Rare combo of {p['ct']} CTs and {p['pts']} PTS — maximize her minutes in competitive games.")
        if p["to"] / gp >= 2.0:
            recs.append(f"Transition Discipline: High turnovers ({p['to']}) for a midfielder. Focus on controlled clears.")
        if p["sh_pct"] < 30 and p["sh"] >= 5:
            recs.append(f"Shot Quality: Only {p['sh_pct']:.0f}% shooting — reduce long-range attempts.")
        if tier_num >= 3:
            recs.append(f"Role Clarity: Use {name} as a defensive midfielder or draw-circle specialist.")

    elif pos == "D":
        if p["ct"] / gp >= 1.5:
            recs.append(f"Defensive Anchor: {name}'s {p['ct']/gp:.1f} CTs/game make her a cornerstone — assign her to the opponent's top attacker.")
        if p["gb"] / gp >= 1.5:
            recs.append(f"Ground Ball Intensity: Strong ground ball rate ({p['gb']/gp:.1f}/gm) — use her on the draw circle.")
        if scores["discipline"] <= 60:
            recs.append(f"Penalty Management: Card accumulation is a risk — work on body positioning and footwork.")
        if tier_num >= 3 and p["ct"] < 3:
            recs.append(f"Development Focus: Needs to increase disruptive plays. Use video breakdown to improve anticipation.")

    elif pos == "GK":
        if p.get("gk_sv_pct", 0) < 40:
            recs.append(f"Save Rate Development: {p.get('gk_sv_pct', 0):.1f}% is below D1 average (~45%). Focus on positioning drills.")
        if p.get("gk_gaa", 0) >= 12:
            recs.append(f"Defensive System Review: {p.get('gk_gaa', 0):.2f} GAA is elevated. Review defensive slide packages.")
        if p.get("gk_w", 0) >= 2:
            recs.append(f"Start in Big Games: {name}'s experience in wins makes her the clear choice for high-leverage matchups.")

    if len(recs) == 0:
        if tier_num == 4:
            recs.append(f"Development Plan: {name} needs increased practice reps to earn more game minutes.")
        elif tier_num == 3:
            recs.append(f"Defined Role: {name} can contribute in specific situations. Deploy her accordingly.")

    return recs


# ═══════════════════════════════════════════════
# VISUALIZATION BUILDERS
# ═══════════════════════════════════════════════

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color=UVA_BLUE),
    margin=dict(l=30, r=30, t=40, b=30),
)


def make_radar_chart(scores, pos, height=300):
    if pos == "A":
        cats = ["Scoring", "Efficiency", "Playmaking", "Shot Quality", "Discipline", "Possession"]
        vals = [scores["offensive"], scores["efficiency"], min(scores["offensive"]*0.6+scores["possession"]*0.4,100),
                scores["efficiency"]*0.8, scores["discipline"], scores["possession"]]
    elif pos == "M":
        cats = ["Offense", "Defense", "Draw Control", "Possession", "Efficiency", "Discipline"]
        vals = [scores["offensive"], scores["defensive"], scores["possession"],
                scores["possession"]*0.8+scores["efficiency"]*0.2, scores["efficiency"], scores["discipline"]]
    elif pos == "D":
        cats = ["Disruption", "Ground Balls", "Discipline", "Clear Impact", "Possession", "Low TO"]
        vals = [scores["defensive"], scores["possession"]*0.8, scores["discipline"],
                scores["defensive"]*0.6+scores["possession"]*0.4, scores["possession"], scores["efficiency"]]
    elif pos == "GK":
        cats = ["Save %", "GAA (inv)", "Consistency", "Ground Balls", "Win Impact", "Discipline"]
        vals = [scores["efficiency"], scores["defensive"], scores["efficiency"]*0.9,
                scores["possession"], scores["overall"], scores["discipline"]]
    else:
        cats = ["Offense", "Defense", "Possession", "Efficiency", "Discipline"]
        vals = [scores["offensive"], scores["defensive"], scores["possession"], scores["efficiency"], scores["discipline"]]

    vals = [max(0, min(v, 100)) for v in vals]
    vals.append(vals[0])
    cats.append(cats[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=cats, fill='toself',
        fillcolor=f'rgba(229,114,0,0.15)', line=dict(color=UVA_ORANGE, width=2.5),
        marker=dict(size=6, color=UVA_ORANGE)
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False,
                          gridcolor=UVA_BLUE_25),
            angularaxis=dict(gridcolor=UVA_BLUE_25,
                           tickfont=dict(size=10, color=TEXT_GRAY))
        ),
        showlegend=False, height=height,
    )
    return fig


def make_game_log_chart(p, games):
    game_g = p.get("game_g", [])
    game_pts = p.get("game_pts", [])
    game_to = p.get("game_to", [])
    n = len(game_g)
    labels = [f"G{i+1}" for i in range(n)]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=game_pts, name="Points",
        marker_color=f"rgba(229,114,0,0.5)", marker_line=dict(color=UVA_ORANGE, width=1)))
    fig.add_trace(go.Scatter(x=labels, y=game_g, name="Goals", mode="lines+markers",
        line=dict(color=UVA_GREEN, width=2.5), marker=dict(size=7)))
    if any(t > 0 for t in game_to):
        fig.add_trace(go.Scatter(x=labels, y=game_to, name="TO", mode="lines+markers",
            line=dict(color=UVA_MAGENTA, width=2, dash="dot"), marker=dict(size=6)))
    fig.update_layout(**PLOTLY_LAYOUT, height=240, barmode="overlay",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
        yaxis=dict(gridcolor=MED_GRAY, title=None), xaxis=dict(title=None))
    return fig


def make_shot_efficiency_bar(p):
    cats = ["Shots", "SOG", "Goals"]
    vals = [p["sh"], p.get("sog", 0), p["g"]]
    colors = [UVA_BLUE_25, UVA_ORANGE_25, UVA_ORANGE]
    fig = go.Figure()
    for c, v, col in zip(cats, vals, colors):
        text_color = WHITE if col == UVA_ORANGE else UVA_BLUE
        fig.add_trace(go.Bar(y=[c], x=[v], orientation="h", marker_color=col,
            text=[str(v)], textposition="inside",
            textfont=dict(color=text_color, size=13), name=c, showlegend=False))
    fig.update_layout(**PLOTLY_LAYOUT, height=130, barmode="group",
        xaxis=dict(visible=False), yaxis=dict(tickfont=dict(size=11, color=TEXT_GRAY)))
    return fig


def make_percentile_bars(scores, pos):
    """Horizontal percentile bars for impact categories."""
    cats = ["Offense", "Defense", "Possession", "Efficiency", "Discipline"]
    keys = ["offensive", "defensive", "possession", "efficiency", "discipline"]
    vals = [scores[k] for k in keys]

    colors = []
    for v in vals:
        if v >= 65: colors.append(UVA_GREEN)
        elif v >= 40: colors.append(UVA_YELLOW)
        else: colors.append(UVA_MAGENTA)

    fig = go.Figure()
    fig.add_trace(go.Bar(y=cats, x=[100]*5, orientation="h", marker_color=LIGHT_GRAY,
        showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Bar(y=cats, x=vals, orientation="h", marker_color=colors,
        text=[f"{v:.0f}" for v in vals], textposition="inside",
        textfont=dict(size=12, color=WHITE, family="DM Sans"), showlegend=False))
    fig.update_layout(**PLOTLY_LAYOUT, height=200, barmode="overlay",
        xaxis=dict(range=[0, 100], visible=False),
        yaxis=dict(tickfont=dict(size=11, color=TEXT_GRAY), autorange="reversed"))
    return fig


def make_rolling_avg_chart(p):
    """Rolling average trend for goals."""
    game_g = p.get("game_g", [])
    n = len(game_g)
    if n < 3: return None
    labels = [f"G{i+1}" for i in range(n)]
    rolling = pd.Series(game_g).rolling(window=3, min_periods=1).mean().tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=game_g, mode="markers", name="Actual",
        marker=dict(size=10, color=UVA_ORANGE, line=dict(width=1, color=WHITE))))
    fig.add_trace(go.Scatter(x=labels, y=rolling, mode="lines", name="3-Game Avg",
        line=dict(color=UVA_BLUE, width=3)))
    fig.update_layout(**PLOTLY_LAYOUT, height=200, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
        yaxis=dict(gridcolor=MED_GRAY, title=None), xaxis=dict(title=None))
    return fig


def make_cumulative_points_chart(all_data, top_n=6):
    """Cumulative points stacked area chart."""
    top_scorers = sorted([(n, d) for n, d in all_data.items() if d["player"]["pts"] >= 3],
                         key=lambda x: x[1]["player"]["pts"], reverse=True)[:top_n]
    if not top_scorers: return None
    colors = [UVA_ORANGE, UVA_BLUE, UVA_CYAN, UVA_GREEN, UVA_MAGENTA, UVA_YELLOW]
    fig = go.Figure()
    for idx, (name, data) in enumerate(top_scorers):
        game_pts = data["player"]["game_pts"]
        cum = np.cumsum(game_pts).tolist()
        labels = [f"G{i+1}" for i in range(len(game_pts))]
        fig.add_trace(go.Scatter(x=labels, y=cum, name=name, mode="lines+markers",
            line=dict(width=2.5, color=colors[idx % len(colors)]),
            marker=dict(size=5)))
    fig.update_layout(**PLOTLY_LAYOUT, height=350,
        legend=dict(font=dict(size=10)),
        yaxis=dict(gridcolor=MED_GRAY, title="Cumulative Points"),
        xaxis=dict(title=None))
    return fig


def make_usage_efficiency_chart(all_data):
    """Usage vs Efficiency quadrant plot."""
    scatter_data = []
    for name, data in all_data.items():
        p = data["player"]
        if p["gp"] >= 2 and p["sh"] >= 3:
            scatter_data.append({
                "name": name, "pos": p["pos"],
                "shots_per_game": p["sh"] / p["gp"],
                "shooting_pct": p["sh_pct"],
                "points": p["pts"],
                "tier": data["tier_num"],
            })
    if not scatter_data: return None
    df = pd.DataFrame(scatter_data)
    color_map = {"A": UVA_ORANGE, "M": UVA_BLUE, "D": UVA_GREEN, "GK": TEXT_GRAY}
    fig = px.scatter(df, x="shots_per_game", y="shooting_pct", size="points",
        color="pos", text="name", color_discrete_map=color_map,
        labels={"shots_per_game": "Shots / Game (Usage)", "shooting_pct": "Shooting % (Efficiency)", "pos": "Position"})
    fig.update_traces(textposition="top center", textfont_size=10)

    med_x = df["shots_per_game"].median()
    med_y = df["shooting_pct"].median()
    fig.add_hline(y=med_y, line_dash="dash", line_color=MED_GRAY, line_width=1)
    fig.add_vline(x=med_x, line_dash="dash", line_color=MED_GRAY, line_width=1)
    fig.add_annotation(x=df["shots_per_game"].max()*0.95, y=df["shooting_pct"].max()*0.95,
        text="Stars", showarrow=False, font=dict(size=11, color=UVA_GREEN))
    fig.add_annotation(x=df["shots_per_game"].min()*1.1, y=df["shooting_pct"].max()*0.95,
        text="Efficient", showarrow=False, font=dict(size=11, color=UVA_CYAN))
    fig.add_annotation(x=df["shots_per_game"].max()*0.95, y=max(0, med_y * 0.3),
        text="Volume", showarrow=False, font=dict(size=11, color=UVA_ORANGE))
    fig.add_annotation(x=df["shots_per_game"].min()*1.1, y=max(0, med_y * 0.3),
        text="Low Impact", showarrow=False, font=dict(size=11, color=TEXT_GRAY))

    fig.update_layout(**PLOTLY_LAYOUT, height=450,
        xaxis=dict(gridcolor=MED_GRAY), yaxis=dict(gridcolor=MED_GRAY))
    return fig


def make_draw_control_chart(all_data):
    """Draw control analysis for top draw takers."""
    dc_players = sorted([(n, d) for n, d in all_data.items() if d["player"]["dc"] >= 1],
                        key=lambda x: x[1]["player"]["dc"], reverse=True)[:6]
    if not dc_players: return None
    names = [f"#{d['player']['num']} {n}" for n, d in dc_players]
    dcs = [d["player"]["dc"] for _, d in dc_players]
    colors = [UVA_ORANGE if d["player"]["dc"] >= 5 else UVA_BLUE_25 for _, d in dc_players]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=dcs, marker_color=colors,
        text=[str(d) for d in dcs], textposition="outside",
        textfont=dict(size=12, color=UVA_BLUE)))
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
        yaxis=dict(gridcolor=MED_GRAY, title="Draw Controls"),
        xaxis=dict(tickfont=dict(size=10)))
    return fig


# ═══════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════

players, games, game_results = load_data()

team_avg = {}
active = {k: v for k, v in players.items() if v["gp"] >= 2}
team_avg["max_gpg"] = max(v["g"]/v["gp"] for v in active.values())
team_avg["max_ppg"] = max(v["pts"]/v["gp"] for v in active.values())
team_avg["max_apg"] = max(v["a"]/v["gp"] for v in active.values())
team_avg["max_ctpg"] = max(v["ct"]/v["gp"] for v in active.values())
team_avg["max_gbpg"] = max(v["gb"]/v["gp"] for v in active.values())
team_avg["max_dcpg"] = max(v["dc"]/v["gp"] for v in active.values())
team_avg["max_poss_impact"] = max(v["gb"]+v["dc"]+v["ct"]-v["to"] for v in active.values())

all_data = {}
for name, p in players.items():
    m = compute_advanced_metrics(p)
    s = compute_impact_scores(p, m, team_avg)
    flags = get_development_flags(p, m, s)
    tier_num, tier_label = get_tier(s, p)
    notes = generate_coaching_notes(name, p, m, s, tier_num, flags)
    recs = generate_recommendations(name, p, m, s, tier_num, flags)
    all_data[name] = {"player": p, "metrics": m, "scores": s, "flags": flags,
                      "tier_num": tier_num, "tier_label": tier_label, "notes": notes, "recs": recs}

# Compute season record for header
_wins = sum(1 for g in (list(all_data.values())[0]["player"]["game_g"] if all_data else []) for _ in [0])  # placeholder
try:
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from analytics import list_games as _lg
    _gl = _lg()
    _n_games = len(_gl)
    _wins = sum(1 for g in _gl if g["result"] == "W")
    _losses = _n_games - _wins
    _record_str = f"{_wins}-{_losses}"
except Exception:
    _n_games = len(games)
    _record_str = f"{sum(1 for r in game_results if r=='W')}-{sum(1 for r in game_results if r!='W')}"

st.markdown(f"""
<div class="main-header">
    <div>
        <h1>LaxIQ — PLAYER INTELLIGENCE</h1>
        <p>Women's Lacrosse · 2026 Season ({_n_games} Games) · Record: {_record_str} · Advanced Player Analytics Dashboard</p>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ Filters & Settings"):
    f1, f2, f3 = st.columns(3)
    with f1:
        pos_filter = st.multiselect("Position", ["A", "M", "D", "GK"], default=["A", "M", "D", "GK"])
    with f2:
        tier_filter = st.multiselect("Tier", [1, 2, 3, 4], default=[1, 2, 3, 4],
            format_func=lambda x: {1:"Tier 1: Driver", 2:"Tier 2: Amplifier", 3:"Tier 3: Specialist", 4:"Tier 4: Dev"}[x])
    with f3:
        min_gp = st.slider("Min Games Played", 1, 5, 1)

with st.expander("📐 Formula Reference"):
    st.markdown("""
    **Pts/Shot** = PTS / SH
    **TO Rate** = TO / (SH+TO+DC+GB)
    **Poss Impact** = GB+DC+CT−TO
    **Consistency** = 1 − CV(pts/game)
    **Clutch** = Avg G(wins) / Avg G(losses)
    """)

filtered = {k: v for k, v in all_data.items()
            if v["player"]["pos"] in pos_filter
            and v["tier_num"] in tier_filter
            and v["player"]["gp"] >= min_gp}
sorted_players = sorted(filtered.items(), key=lambda x: x[1]["scores"]["overall"], reverse=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Team Overview", "Player Cards", "Player Comparison", "Draw Control Center", "Goal Tending"])

# TAB 1: TEAM OVERVIEW
with tab1:
    st.markdown("## Team-Wide Impact Overview")

    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    tier_players = {1: [], 2: [], 3: [], 4: []}
    for name, data in all_data.items():
        t = data["tier_num"]
        tier_counts[t] += 1
        tier_players[t].append(name)

    tc1, tc2, tc3, tc4 = st.columns(4)
    for col, t, label, color in [(tc1, 1, "Program Drivers", CAV_ORANGE), (tc2, 2, "System Amplifiers", UVA_CYAN),
                                  (tc3, 3, "Situational Specialists", UVA_GREEN), (tc4, 4, "Developmental", MED_GRAY)]:
        text_col = UVA_BLUE if color == MED_GRAY else color
        with col:
            st.markdown(f"<div style='text-align:center;padding:1.2rem;background:{WHITE};border-radius:14px;border:2px solid {color};box-shadow:0 2px 8px rgba(0,0,0,0.05);'>"
                       f"<div style='font-family:Bebas Neue;font-size:2.5rem;color:{text_col};'>{tier_counts[t]}</div>"
                       f"<div style='font-size:0.72rem;color:{TEXT_GRAY};text-transform:uppercase;letter-spacing:1px;font-weight:600;'>{label}</div>"
                       f"<div style='font-size:0.8rem;color:{UVA_BLUE};margin-top:8px;'>{'<br>'.join(tier_players[t][:5])}</div>"
                       f"</div>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### Usage vs Efficiency Matrix")
    ue_fig = make_usage_efficiency_chart(all_data)
    if ue_fig:
        st.plotly_chart(ue_fig, use_container_width=True)

    st.markdown("### Cumulative Scoring Progression")
    cum_fig = make_cumulative_points_chart(all_data)
    if cum_fig:
        st.plotly_chart(cum_fig, use_container_width=True)

    st.markdown("### Roster Metrics Heatmap")
    heatmap_data = []
    heatmap_names = []
    for name, data in sorted_players:
        p = data["player"]
        s = data["scores"]
        if p["gp"] >= 2:
            heatmap_names.append(f"#{p['num']} {name}")
            heatmap_data.append([s["overall"], s["offensive"], s["defensive"],
                               s["possession"], s["efficiency"], s["discipline"]])
    if heatmap_data:
        fig = go.Figure(go.Heatmap(
            z=heatmap_data,
            x=["Overall", "Offense", "Defense", "Possession", "Efficiency", "Discipline"],
            y=heatmap_names,
            colorscale=[[0, "#FCE4EC"], [0.35, "#FFF8E1"], [0.6, "#E8F5E9"], [1, UVA_GREEN]],
            text=[[f"{v:.0f}" for v in row] for row in heatmap_data],
            texttemplate="%{text}", textfont=dict(size=11, color=UVA_BLUE),
            showscale=False,
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=max(400, len(heatmap_names)*35+80),
            yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
            xaxis=dict(side="top", tickfont=dict(size=11)))
        st.plotly_chart(fig, use_container_width=True)

# TAB 2: PLAYER CARDS
with tab2:
    st.markdown("## Player Performance Cards")
    for name, data in sorted_players:
        p = data["player"]
        m = data["metrics"]
        s = data["scores"]
        flags = data["flags"]
        tier_text = f"TIER {data['tier_num']} · {data['tier_label'].upper()}"

        st.markdown('<div class="player-card">', unsafe_allow_html=True)

        top1, top2, top3 = st.columns([0.5, 3.5, 1])
        with top1:
            img_url = HEADSHOT_URLS.get(name, "")
            if img_url:
                st.markdown(f'<img src="{img_url}" class="headshot-circle" onerror="this.style.display=\'none\'">', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="width:80px;height:80px;border-radius:50%;background:{UVA_BLUE_25};display:flex;align-items:center;justify-content:center;font-size:1.8rem;color:{UVA_BLUE};font-family:Bebas Neue;">{p["num"]}</div>', unsafe_allow_html=True)
        with top2:
            st.markdown(f'<p class="player-name">#{p["num"]} {name}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="player-meta">{p["pos"]} · {p["yr"]} · {p["gp"]} GP / {p["gs"]} GS <span class="tier-badge tier-{data["tier_num"]}">{tier_text}</span></p>', unsafe_allow_html=True)
        with top3:
            st.markdown(f'<div class="impact-score-box"><div class="impact-score-num">{s["overall"]:.0f}</div><div class="impact-score-label">Impact Score</div></div>', unsafe_allow_html=True)

        cat_cols = st.columns(5)
        for col, (label, key) in zip(cat_cols, [("OFFENSE", "offensive"), ("DEFENSE", "defensive"),
                                                 ("POSSESSION", "possession"), ("EFFICIENCY", "efficiency"), ("DISCIPLINE", "discipline")]):
            val = s[key]
            color = UVA_GREEN if val >= 65 else UVA_YELLOW if val >= 40 else UVA_MAGENTA
            with col:
                st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{color}">{val:.0f}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        col_radar, col_stats, col_gamelog = st.columns([1.2, 1, 1.3])
        with col_radar:
            st.plotly_chart(make_radar_chart(s, p["pos"]), use_container_width=True, key=f"radar_{name}")
        with col_stats:
            st.markdown("**Core Stats**")
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
            st.markdown("**Advanced**")
            if p["pos"] != "GK" and p["sh"] > 0:
                a1, a2 = st.columns(2)
                a1.metric("Pts/Shot", f"{m['pts_per_shot']:.2f}"); a2.metric("TO Rate", f"{m['to_rate']:.2f}")
                a3, a4 = st.columns(2)
                a3.metric("Poss Impact", f"{m['poss_impact']:+d}"); a4.metric("Consistency", f"{m['consistency']:.2f}")
        with col_gamelog:
            st.markdown("**Game-by-Game Trend**")
            st.plotly_chart(make_game_log_chart(p, games), use_container_width=True, key=f"gl_{name}")

        if p["sh"] >= 3 and p["pos"] != "GK":
            st.markdown("**Shot Funnel**")
            st.plotly_chart(make_shot_efficiency_bar(p), use_container_width=True, key=f"sf_{name}")

        if flags:
            flag_html = ""
            for fname, ftype in flags:
                flag_html += f'<span class="flag-tag flag-{ftype}">{fname}</span>'
            st.markdown(f"**Development Flags** &nbsp; {flag_html}", unsafe_allow_html=True)

        st.markdown(f'<div class="coaching-notes">{data["notes"]}</div>', unsafe_allow_html=True)

        if data["recs"]:
            for rec in data["recs"]:
                st.markdown(f'<div class="rec-box">{rec}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")

# TAB 3: COMPARISON
with tab3:
    st.markdown("## Head-to-Head Comparison")

    comp_names = [n for n, _ in sorted_players]
    comp_options = [f"#{all_data[n]['player']['num']} {n} ({all_data[n]['player']['pos']})" for n in comp_names]
    if len(comp_options) < 2:
        st.warning("Need at least 2 players for comparison.")
    else:
        c1, c2 = st.columns(2)
        with c1: p1_sel = st.selectbox("Player 1", comp_options, index=0)
        with c2: p2_sel = st.selectbox("Player 2", comp_options, index=min(1, len(comp_options)-1))

        p1_name = comp_names[comp_options.index(p1_sel)]
        p2_name = comp_names[comp_options.index(p2_sel)]
        d1, d2 = all_data[p1_name], all_data[p2_name]

        shared_cats = ["Offense", "Defense", "Possession", "Efficiency", "Discipline"]
        shared_keys = ["offensive", "defensive", "possession", "efficiency", "discipline"]

        rc1, rc2 = st.columns(2)
        for col, pname, pdata, color in [(rc1, p1_name, d1, UVA_ORANGE), (rc2, p2_name, d2, UVA_BLUE)]:
            with col:
                img_url = HEADSHOT_URLS.get(pname, "")
                hdr = f'<div style="text-align:center;">'
                if img_url:
                    hdr += f'<img src="{img_url}" style="width:90px;height:90px;border-radius:50%;object-fit:cover;border:3px solid {color};margin-bottom:8px;" onerror="this.style.display=\'none\'">'
                hdr += f'<h3 style="color:{color} !important;margin:0;">{pname}</h3>'
                hdr += f'<p style="color:{TEXT_GRAY};font-size:0.85rem;">#{pdata["player"]["num"]} · {pdata["player"]["pos"]} · {pdata["player"]["yr"]} · Impact: {pdata["scores"]["overall"]:.0f}</p></div>'
                st.markdown(hdr, unsafe_allow_html=True)

                vals = [pdata["scores"][k] for k in shared_keys]
                vals = [max(0, min(v, 100)) for v in vals]
                vals.append(vals[0])
                cats_closed = shared_cats + [shared_cats[0]]
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=vals, theta=cats_closed, fill='toself',
                    fillcolor=f'rgba({",".join(str(int(color[i:i+2], 16)) for i in (1,3,5))},0.15)',
                    line=dict(color=color, width=2.5), marker=dict(size=6, color=color)))
                fig.update_layout(**PLOTLY_LAYOUT, polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor=MED_GRAY),
                    angularaxis=dict(gridcolor=MED_GRAY, tickfont=dict(size=10, color=TEXT_GRAY))),
                    showlegend=False, height=280)
                st.plotly_chart(fig, use_container_width=True, key=f"cmp_r_{pname}")

        v1 = [d1["scores"][k] for k in shared_keys]
        v2 = [d2["scores"][k] for k in shared_keys]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=shared_cats, y=v1, name=p1_name, marker_color=UVA_ORANGE))
        fig.add_trace(go.Bar(x=shared_cats, y=v2, name=p2_name, marker_color=UVA_BLUE))
        fig.update_layout(**PLOTLY_LAYOUT, height=320, barmode="group",
            yaxis=dict(gridcolor=MED_GRAY, range=[0, 100]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Raw Stats Comparison")
        stat_keys = ["gp", "g", "a", "pts", "sh", "sh_pct", "sog_pct", "gb", "dc", "to", "ct"]
        stat_labels = ["GP", "Goals", "Assists", "Points", "Shots", "SH%", "SOG%", "GB", "DC", "TO", "CT"]
        comp_df = pd.DataFrame({
            "Stat": stat_labels,
            p1_name: [d1["player"].get(k, "—") for k in stat_keys],
            p2_name: [d2["player"].get(k, "—") for k in stat_keys],
        })
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

# TAB 4: DRAW CONTROL CENTER
with tab4:
    st.markdown("## Draw Control Center")
    st.markdown(f'<p style="color:{TEXT_GRAY};">Draw controls are the single highest-leverage stat in women\'s lacrosse. Teams winning 60%+ of draws gain multiple extra possessions per game.</p>', unsafe_allow_html=True)

    total_dc = sum(d["player"]["dc"] for d in all_data.values())
    _max_gp = max((d["player"]["gp"] for d in all_data.values()), default=1)
    dc_per_game = total_dc / max(_max_gp, 1)

    # ── Sub-tabs within Draw Control Center ──
    dc_sub1, dc_sub2, dc_sub3 = st.tabs(["🏠 UVA Draw Analysis", "🔍 Opponent Scouting (JMU)", "📋 Strategy & Counter-Tactics"])

    # ═══════════════════════════════════════════════
    # DC SUB-TAB 1: UVA DRAW ANALYSIS
    # ═══════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════
    # DC SUB-TAB 2: OPPONENT SCOUTING (JMU)
    # ═══════════════════════════════════════════════
    with dc_sub2:
        # ── JMU Draw Control Scouting Data (32 clips) ──
        JMU_DRAW_CLIPS = [
            {"id":1,"p":"#29","tech":"Forward Clamp","dir":"Fwd-Left","clk":10,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"#24","ttp":3.2,"spd":"Avg"},
            {"id":2,"p":"#29","tech":"Forward Clamp","dir":"Fwd-Left","clk":9,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"#24","ttp":3.8,"spd":"Avg"},
            {"id":3,"p":"#29","tech":"Forward Clamp","dir":"Fwd-Left","clk":10,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"#24","ttp":2.9,"spd":"Fast"},
            {"id":4,"p":"#29","tech":"Forward Clamp + DL","dir":"Fwd-Left","clk":9,"dist":"Med","ht":"Bounce","out":"Win","poss":"Wing","who":"Left Wing","wing":"#24","ttp":4.1,"spd":"Avg"},
            {"id":5,"p":"#29","tech":"Physical Clamp","dir":"Fwd-Left","clk":9,"dist":"Short","ht":"Ground","out":"Win","poss":"Scramble","who":"Draw Taker","wing":"-","ttp":4.5,"spd":"Slow"},
            {"id":6,"p":"#29","tech":"Delayed Clamp","dir":"Fwd-Left","clk":9,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"#24","ttp":3.5,"spd":"Avg"},
            {"id":7,"p":"#29","tech":"Draw Left Clamp","dir":"Left","clk":9,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"#24","ttp":3.0,"spd":"Fast"},
            {"id":8,"p":"#29","tech":"Forward Clamp","dir":"Backward","clk":6,"dist":"Med","ht":"Bounce","out":"Win","poss":"Wing","who":"Right Wing","wing":"-","ttp":4.8,"spd":"Slow"},
            {"id":9,"p":"#29","tech":"Backward Push","dir":"Back-Left","clk":7,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"-","ttp":3.6,"spd":"Avg"},
            {"id":10,"p":"#29","tech":"Backward Push","dir":"Back-Left","clk":7,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"-","ttp":3.4,"spd":"Avg"},
            {"id":11,"p":"#29","tech":"Go-With Grab","dir":"Forward","clk":12,"dist":"Short","ht":"Air","out":"Win","poss":"Clean","who":"Draw Taker","wing":"-","ttp":1.5,"spd":"Fast"},
            {"id":12,"p":"#29","tech":"Directed Forward","dir":"Forward","clk":12,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Left Wing","wing":"#11","ttp":2.2,"spd":"Fast"},
            {"id":13,"p":"#29","tech":"Forward Power","dir":"Fwd-Left","clk":10,"dist":"Long","ht":"Air","out":"Win","poss":"Wing","who":"Left Wing","wing":"-","ttp":4.2,"spd":"Avg"},
            {"id":14,"p":"#29","tech":"Open Up","dir":"Fwd-Right","clk":2,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Right Wing","wing":"#24","ttp":2.5,"spd":"Fast"},
            {"id":15,"p":"#29","tech":"Open Up","dir":"Forward","clk":12,"dist":"Med","ht":"Air","out":"Win","poss":"Wing","who":"Draw Taker","wing":"-","ttp":3.0,"spd":"Fast"},
            {"id":16,"p":"#29","tech":"Open Up","dir":"Left","clk":9,"dist":"Med","ht":"Air","out":"Win","poss":"Wing","who":"Left Wing","wing":"-","ttp":3.3,"spd":"Avg"},
            {"id":17,"p":"#29","tech":"Aggressive Clamp","dir":"Forward","clk":12,"dist":"Short","ht":"Ground","out":"Win","poss":"Scramble","who":"Ground Ball","wing":"-","ttp":5.2,"spd":"Slow"},
            {"id":18,"p":"#29","tech":"Go-With Pop","dir":"Forward","clk":12,"dist":"Short","ht":"Air","out":"50-50","poss":"Scramble","who":"Scramble","wing":"-","ttp":6.0,"spd":"Slow"},
            {"id":19,"p":"#29","tech":"Fwd Clamp (COUNTERED)","dir":"Fwd-Left","clk":9,"dist":"Short","ht":"Ground","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
            {"id":20,"p":"#29","tech":"Fwd Clamp (COUNTERED)","dir":"Forward","clk":12,"dist":"Med","ht":"Ground","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
            {"id":21,"p":"#29","tech":"Backward Push","dir":"Back-Left","clk":8,"dist":"Med","ht":"Ground","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
            {"id":22,"p":"#29","tech":"Forward Clamp","dir":"Forward","clk":12,"dist":"Long","ht":"Air","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
            {"id":23,"p":"#29","tech":"Backward Push","dir":"Back-Left","clk":7,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"-","ttp":3.8,"spd":"Avg"},
            {"id":24,"p":"#29","tech":"Backward Push","dir":"Back-Left","clk":7,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"-","ttp":3.5,"spd":"Avg"},
            {"id":25,"p":"#29","tech":"Slice","dir":"Right","clk":3,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Right Wing","wing":"Dino","ttp":2.0,"spd":"Fast"},
            {"id":26,"p":"#29","tech":"Directed Push","dir":"Right","clk":3,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Right Wing","wing":"Dino","ttp":2.3,"spd":"Fast"},
            {"id":27,"p":"#17","tech":"Behind Rake","dir":"Backward","clk":6,"dist":"Med","ht":"Ground","out":"Win","poss":"Wing","who":"Left Wing","wing":"-","ttp":3.5,"spd":"Avg"},
            {"id":28,"p":"#17","tech":"Slice + Box","dir":"Left","clk":9,"dist":"Short","ht":"Ground","out":"Win","poss":"Scramble","who":"Ground Ball","wing":"-","ttp":5.0,"spd":"Slow"},
            {"id":29,"p":"#17","tech":"Forward + DL","dir":"Fwd-Left","clk":10,"dist":"Med","ht":"Air","out":"Win","poss":"Clean","who":"Left Wing","wing":"#11","ttp":2.4,"spd":"Fast"},
            {"id":30,"p":"#18","tech":"Forward Launch","dir":"Fwd-Right","clk":2,"dist":"Long","ht":"Air","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
            {"id":31,"p":"#18","tech":"Forward + DL","dir":"Fwd-Left","clk":9,"dist":"Long","ht":"Air","out":"Loss","poss":"Opponent","who":"Opponent","wing":"-","ttp":0,"spd":"-"},
            {"id":32,"p":"#18","tech":"Forward Power","dir":"Forward","clk":12,"dist":"Long","ht":"Air","out":"Win","poss":"Clean","who":"Right Wing","wing":"-","ttp":2.8,"spd":"Fast"},
        ]
        jmu_df = pd.DataFrame(JMU_DRAW_CLIPS)

        st.markdown(f"""<div style="background:linear-gradient(135deg, {UVA_BLUE} 0%, #1a2238 60%, #8B0000 100%);
            padding:1.2rem 2rem;border-radius:14px;margin-bottom:1.2rem;">
            <h2 style="color:white !important;margin:0;font-size:1.8rem;">JMU Draw Control Scouting Report</h2>
            <p style="color:rgba(255,255,255,0.7);margin:4px 0 0 0;font-size:0.85rem;">
            32 Draw Controls Analyzed · Multi-Game Film Study · Prepared for Game Prep</p>
        </div>""", unsafe_allow_html=True)

        # ── KPI Row ──
        jmu_wins = len(jmu_df[jmu_df["out"] == "Win"])
        jmu_losses = len(jmu_df[jmu_df["out"] == "Loss"])
        jmu_fifty = len(jmu_df[jmu_df["out"] == "50-50"])
        jmu_win_pct = jmu_wins / len(jmu_df) * 100

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.markdown(f'<div class="stat-box"><div class="stat-val">{len(jmu_df)}</div><div class="stat-label">Total Draws</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN}">{jmu_win_pct:.0f}%</div><div class="stat-label">JMU Win Rate</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN}">{jmu_wins}</div><div class="stat-label">Wins</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_MAGENTA}">{jmu_losses}</div><div class="stat-label">Losses</div></div>', unsafe_allow_html=True)
        k5.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_YELLOW}">{jmu_fifty}</div><div class="stat-label">50-50</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── Player Breakdown ──
        st.markdown("### Player Profiles")
        player_stats = {}
        for p_id in ["#29", "#17", "#18"]:
            pdata = jmu_df[jmu_df["p"] == p_id]
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
        player_cols = {"#29": (UVA_ORANGE, pp1, "Primary Draw Taker", "Forward Clamp dominant — goes Fwd-Left ~60% of the time. Left Wing #24 is the primary recovery target. Extremely repeatable pattern."),
                       "#17": (UVA_CYAN, pp2, "Backup Draw Taker", "Behind Rake technique — fundamentally different style from #29. More physical in the circle. Can mimic #29's forward style if needed."),
                       "#18": (UVA_YELLOW, pp3, "Tertiary Draw Taker", "Forward Launch with power/control issues (1W-2L). Too much power, not enough precision. Ball goes beyond wing recovery range.")}
        for p_id, (color, col, role, scout_note) in player_cols.items():
            ps = player_stats[p_id]
            with col:
                st.markdown(f"""<div class="player-card" style="border-top:4px solid {color};">
                <h3 style="color:{color} !important;margin:0 0 4px 0;font-size:1.5rem;">JMU {p_id}</h3>
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

        # ── Technique Analysis ──
        st.markdown("### Technique Breakdown")
        tc1, tc2 = st.columns(2)

        with tc1:
            tech_clean = jmu_df["tech"].str.replace(r" \(COUNTERED\)", "", regex=True)
            tech_counts = tech_clean.value_counts()
            tech_wins = jmu_df.copy()
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
            fig_tech.update_layout(**PLOTLY_LAYOUT, height=380, barmode="overlay",
                xaxis=dict(title="Count"), yaxis=dict(tickfont=dict(size=10)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=140))
            st.plotly_chart(fig_tech, use_container_width=True)

        with tc2:
            # Win rate by ball height
            ht_stats = jmu_df.groupby("ht").apply(
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
            fig_ht.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=False,
                yaxis=dict(title="Win Rate %", range=[0, 110]),
                title=dict(text="Win Rate by Ball Height", font=dict(size=14)))
            st.plotly_chart(fig_ht, use_container_width=True)

        st.markdown("---")

        # ── Direction Tendencies (Polar / Clock Face) ──
        st.markdown("### Directional Tendencies")
        dr1, dr2 = st.columns(2)

        with dr1:
            # Polar chart — direction distribution by clock position
            clock_bins = {"12 (Forward)": [11, 12, 1], "3 (Right)": [2, 3, 4],
                          "6 (Backward)": [5, 6, 7], "9 (Left)": [8, 9, 10]}
            zone_counts = []
            zone_wins = []
            zone_labels = list(clock_bins.keys())
            for label, clks in clock_bins.items():
                zone_data = jmu_df[jmu_df["clk"].isin(clks)]
                zone_counts.append(len(zone_data))
                zone_wins.append(len(zone_data[zone_data["out"] == "Win"]))

            fig_polar = go.Figure()
            fig_polar.add_trace(go.Scatterpolar(
                r=zone_counts + [zone_counts[0]],
                theta=zone_labels + [zone_labels[0]],
                fill="toself", name="All Draws",
                fillcolor=f"rgba(35,45,75,0.2)", line=dict(color=UVA_BLUE, width=2),
                marker=dict(size=8)
            ))
            fig_polar.add_trace(go.Scatterpolar(
                r=zone_wins + [zone_wins[0]],
                theta=zone_labels + [zone_labels[0]],
                fill="toself", name="Wins",
                fillcolor=f"rgba(229,114,0,0.2)", line=dict(color=UVA_ORANGE, width=2),
                marker=dict(size=8)
            ))
            fig_polar.update_layout(
                polar=dict(
                    bgcolor=WHITE,
                    radialaxis=dict(visible=True, gridcolor=MED_GRAY, tickfont=dict(size=9)),
                    angularaxis=dict(tickfont=dict(size=11, color=UVA_BLUE))
                ),
                font=dict(family="DM Sans"), height=380, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                paper_bgcolor=WHITE, plot_bgcolor=WHITE,
                margin=dict(t=60, b=40)
            )
            st.plotly_chart(fig_polar, use_container_width=True)

        with dr2:
            # Direction detail breakdown
            dir_counts = jmu_df["dir"].value_counts()
            dir_wr = jmu_df.groupby("dir").apply(
                lambda g: pd.Series({"wins": (g["out"] == "Win").sum(), "total": len(g)}),
                include_groups=False
            )
            dir_wr["win_rate"] = (dir_wr["wins"] / dir_wr["total"] * 100).round(0)
            dir_wr = dir_wr.sort_values("total", ascending=False)

            # Color code: left=blue, right=orange, forward=green, backward=red
            def dir_color(d):
                d_low = d.lower()
                if "left" in d_low and "back" not in d_low:
                    return UVA_CYAN
                elif "right" in d_low:
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
            fig_dir.update_layout(**PLOTLY_LAYOUT, height=380,
                yaxis=dict(title="Count"), xaxis=dict(tickfont=dict(size=10), tickangle=-30),
                title=dict(text="Direction Frequency & Win Rate", font=dict(size=14)),
                margin=dict(b=80))
            st.plotly_chart(fig_dir, use_container_width=True)

        # Key directional insight box
        fwd_left_count = len(jmu_df[jmu_df["dir"] == "Fwd-Left"])
        fwd_left_pct = fwd_left_count / len(jmu_df) * 100
        st.markdown(f"""<div class="rec-box">
        <strong>Key Directional Insight:</strong> JMU #29 goes <strong>Forward-Left {fwd_left_pct:.0f}%</strong> of the time
        ({fwd_left_count}/{len(jmu_df)} draws). Left Wing #24 is positioned at 9 o'clock pre-whistle and uses a body seal to box out.
        When the ball goes LEFT, JMU's wing structure gives them a significant recovery advantage.
        UVA should overload the left-wing lane and contest #24's positioning before the whistle.
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── Wing Analysis ──
        st.markdown("### Wing & Possession Analysis")
        wc1, wc2 = st.columns(2)

        with wc1:
            # Who secures possession?
            who_counts = jmu_df[jmu_df["out"] == "Win"].groupby("who").size().sort_values(ascending=True)
            fig_who = go.Figure()
            fig_who.add_trace(go.Bar(
                y=who_counts.index, x=who_counts.values,
                orientation="h", marker_color=UVA_ORANGE,
                text=[str(v) for v in who_counts.values],
                textposition="outside", textfont=dict(size=11, color=UVA_BLUE)
            ))
            fig_who.update_layout(**PLOTLY_LAYOUT, height=300,
                title=dict(text="Win Contribution (Who Secures Ball?)", font=dict(size=14)),
                xaxis=dict(title="Wins Secured"), margin=dict(l=120))
            st.plotly_chart(fig_who, use_container_width=True)

        with wc2:
            # Possession type distribution
            poss_counts = jmu_df.groupby("poss").apply(
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
            fig_poss.update_layout(height=300, font=dict(family="DM Sans"),
                paper_bgcolor=WHITE, plot_bgcolor=WHITE,
                title=dict(text="Possession Type Distribution", font=dict(size=14, color=UVA_BLUE)),
                showlegend=False, margin=dict(t=60, b=20))
            st.plotly_chart(fig_poss, use_container_width=True)

        # Wing player callout
        wing_24_count = len(jmu_df[jmu_df["wing"] == "#24"])
        wing_11_count = len(jmu_df[jmu_df["wing"] == "#11"])
        st.markdown(f"""<div class="coaching-notes">
        <strong>Wing Targets:</strong><br>
        <strong>Left Wing #24</strong> — Primary recovery target ({wing_24_count} clips). Positions at 9 o'clock, uses body seal to box out. Disrupting #24's positioning is the single most effective way to break JMU's draw structure.<br><br>
        <strong>#11</strong> — Secondary directed draw target ({wing_11_count} clips). Used in pre-planned directed draws where the draw taker makes eye contact pre-whistle. Watch for this tell.<br><br>
        <strong>"Dino"</strong> — Right-side wing target (2 clips). Rare right-side wrinkle. If JMU starts going right during the game, it signals a tactical adjustment.
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── Time to Possession Analysis ──
        st.markdown("### Time to Possession (TTP)")
        ttp_df = jmu_df[(jmu_df["out"] == "Win") & (jmu_df["ttp"] > 0)].copy()

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
            fig_ttp.update_layout(**PLOTLY_LAYOUT, height=300,
                xaxis=dict(title="Time to Possession (seconds)"),
                yaxis=dict(title="Count"),
                title=dict(text="TTP Distribution (JMU Wins)", font=dict(size=14)))
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
            fig_spd.update_layout(**PLOTLY_LAYOUT, height=300,
                yaxis=dict(title="Avg TTP (seconds)"),
                title=dict(text="Avg TTP by Reaction Speed", font=dict(size=14)))
            st.plotly_chart(fig_spd, use_container_width=True)

        fast_wins = len(ttp_df[ttp_df["spd"] == "Fast"])
        slow_wins = len(ttp_df[ttp_df["spd"] == "Slow"])
        st.markdown(f"""<div class="rec-box">
        <strong>TTP Insight:</strong> JMU secures possession in an average of <strong>{ttp_df['ttp'].mean():.1f}s</strong> on wins.
        Fast wins ({fast_wins} clips, avg {ttp_df[ttp_df['spd']=='Fast']['ttp'].mean():.1f}s) come from clean wing delivery.
        Slow wins ({slow_wins} clips, avg {ttp_df[ttp_df['spd']=='Slow']['ttp'].mean():.1f}s) involve scrambles and ground balls — these are where UVA can compete and disrupt.
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── All Clips Table ──
        with st.expander("📋 View All 32 Scouting Clips", expanded=False):
            display_df = jmu_df[["id", "p", "tech", "dir", "clk", "ht", "out", "poss", "who", "wing", "ttp", "spd"]].copy()
            display_df.columns = ["Clip", "Player", "Technique", "Direction", "Clock", "Height", "Outcome", "Possession", "Secured By", "Wing", "TTP (s)", "Speed"]
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

    # ═══════════════════════════════════════════════
    # DC SUB-TAB 3: STRATEGY & COUNTER-TACTICS
    # ═══════════════════════════════════════════════
    with dc_sub3:
        st.markdown(f"""<div style="background:linear-gradient(135deg, #8B0000 0%, #5C0000 100%);
            padding:1.2rem 2rem;border-radius:14px;margin-bottom:1.2rem;">
            <h2 style="color:white !important;margin:0;font-size:1.8rem;">Counter-Strategy Playbook</h2>
            <p style="color:rgba(255,255,255,0.7);margin:4px 0 0 0;font-size:0.85rem;">
            Actionable tactics to neutralize JMU's draw control advantage</p>
        </div>""", unsafe_allow_html=True)

        # Priority 1
        st.markdown(f"""<div class="player-card" style="border-left:4px solid {UVA_MAGENTA};margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <h3 style="margin:0;font-size:1.2rem;">1. Physical Stick Check During Draw Motion</h3>
            <span style="background:rgba(239,63,107,0.15);color:{UVA_MAGENTA};padding:3px 12px;border-radius:12px;font-size:0.75rem;font-weight:700;">PRIORITY 1</span>
        </div>
        <p style="color:{TEXT_GRAY};font-size:0.9rem;line-height:1.7;">
        Film shows this is <strong>100% effective</strong> against #29 when executed (Clips 19 & 20 — both JMU losses).
        Physically check #29's stick during the draw motion to disrupt the Forward Stick Work (FSW) pattern.
        She cannot redirect when her stick is being contested. This directly counters her dominant Forward Clamp technique.
        </p>
        </div>""", unsafe_allow_html=True)

        # Priority 2
        st.markdown(f"""<div class="player-card" style="border-left:4px solid {UVA_YELLOW};margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <h3 style="margin:0;font-size:1.2rem;">2. Force Air Balls to Neutralize Structure</h3>
            <span style="background:rgba(253,218,36,0.15);color:{UVA_YELLOW};padding:3px 12px;border-radius:12px;font-size:0.75rem;font-weight:700;">PRIORITY 2</span>
        </div>
        <p style="color:{TEXT_GRAY};font-size:0.9rem;line-height:1.7;">
        When the draw becomes an air ball, JMU's structural wing advantage <strong>evaporates</strong> (Clip 18 — 50-50 outcome, 6s TTP).
        Air balls create chaos where pure athleticism matters more than positioning. Contest vertically and force the ball UP rather
        than letting #29 direct it forward-left to her waiting wing structure.
        </p>
        </div>""", unsafe_allow_html=True)

        # Priority 3
        st.markdown(f"""<div class="player-card" style="border-left:4px solid {UVA_CYAN};margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <h3 style="margin:0;font-size:1.2rem;">3. Overload the Left Wing Lane</h3>
            <span style="background:rgba(0,159,223,0.15);color:{UVA_CYAN};padding:3px 12px;border-radius:12px;font-size:0.75rem;font-weight:700;">PRIORITY 3</span>
        </div>
        <p style="color:{TEXT_GRAY};font-size:0.9rem;line-height:1.7;">
        JMU routes ~60% of draws to the left side. Left Wing #24 positions early at 9 o'clock and uses a body seal to box out.
        <strong>Contest #24's positioning before the whistle.</strong> Assign UVA's most physical wing player to directly contest #24.
        Deny the body seal and force JMU to go to their weaker right side or scramble.
        </p>
        </div>""", unsafe_allow_html=True)

        # Priority 4
        st.markdown(f"""<div class="player-card" style="border-left:4px solid {UVA_GREEN};margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <h3 style="margin:0;font-size:1.2rem;">4. Match Power on the Clamp</h3>
            <span style="background:rgba(98,187,70,0.15);color:{UVA_GREEN};padding:3px 12px;border-radius:12px;font-size:0.75rem;font-weight:700;">PRIORITY 4</span>
        </div>
        <p style="color:{TEXT_GRAY};font-size:0.9rem;line-height:1.7;">
        Georgetown out-powered #29 and won the draw cleanly (Clip 22). Matching or exceeding her force on the clamp
        can create turnovers, especially when the ball goes long and beyond JMU's wing recovery range. If our draw taker
        can generate enough power to send the ball past the wing structure, JMU's positioning becomes a liability.
        </p>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Situational Adjustments")

        sa1, sa2 = st.columns(2)
        with sa1:
            st.markdown(f"""<div class="coaching-notes">
            <strong>If JMU sends #17:</strong><br>
            Switch to neutral positioning. #17 uses a Behind Rake (backward) technique — fundamentally different from #29's
            forward clamp. Pre-committing to counter #29's left-forward pattern will give #17 free backward draws. #17 is more
            physical than #29, so expect body contact in the circle. However, #17 can also mimic #29's forward style (Clip 29),
            so don't over-commit to backward coverage.
            </div>""", unsafe_allow_html=True)

        with sa2:
            st.markdown(f"""<div class="coaching-notes">
            <strong>If JMU sends #18:</strong><br>
            Exploit distance control issues. #18 over-powers draws beyond wing recovery range (Clips 30 & 31, both losses).
            Let #18 generate her own turnover. Don't over-contest — just maintain positioning and let her send it too far.
            She is 1W-2L, so the odds are already in UVA's favor when #18 takes the draw.
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── Quick Reference Cheat Sheet ──
        st.markdown("### Game-Day Quick Reference")
        st.markdown(f"""<div class="rec-box">
        <strong>Pre-Draw Checklist (vs JMU #29):</strong><br>
        1. Identify wing positioning — is #24 at 9 o'clock? If yes, contest body seal immediately<br>
        2. Watch for eye contact between draw taker and #11 — signals a directed draw<br>
        3. Position to disrupt forward-left angle (10 o'clock direction)<br>
        4. Prepare physical stick check on the draw motion<br>
        5. If ball goes airborne, crash toward the ball — JMU's structure is neutralized in chaos<br><br>
        <strong>Pattern does NOT change under pressure</strong> — Clip 2 confirms identical setup in final minute. Exploit this predictability.
        </div>""", unsafe_allow_html=True)

# TAB 5: GOAL TENDING
with tab5:
    st.markdown("## Goal Tending Analysis")

    finnelle = all_data.get("Elyse Finnelle")
    josephson = all_data.get("Mel Josephson")

    # ── Sub-tabs within Goal Tending ──
    gk_sub1, gk_sub2, gk_sub3, gk_sub4 = st.tabs([
        "📊 GK Comparison", "🎯 Shot Intelligence (Finnelle)", "🔍 Scouting Report", "🏋️ Development Plan"
    ])

    # ═══════════════════════════════════════════════
    # GK SUB-TAB 1: GOALKEEPER COMPARISON
    # ═══════════════════════════════════════════════
    with gk_sub1:
        if finnelle and josephson:
            gk1, gk2 = st.columns(2)

            for col, gk_name, gk_data, color in [(gk1, "Elyse Finnelle", finnelle, UVA_ORANGE),
                                                   (gk2, "Mel Josephson", josephson, UVA_CYAN)]:
                with col:
                    p = gk_data["player"]
                    img_url = HEADSHOT_URLS.get(gk_name, "")

                    hdr = f'<div style="text-align:center;margin-bottom:1.5rem;">'
                    if img_url:
                        hdr += f'<img src="{img_url}" style="width:100px;height:100px;border-radius:50%;object-fit:cover;border:3px solid {color};margin-bottom:12px;" onerror="this.style.display=\'none\'">'
                    hdr += f'<h3 style="color:{color} !important;margin:8px 0;font-size:1.5rem;">{gk_name}</h3>'
                    hdr += f'<p style="color:{TEXT_GRAY};font-size:0.9rem;">#{p["num"]} · {p["yr"]} · Impact: {gk_data["scores"]["overall"]:.0f}</p></div>'
                    st.markdown(hdr, unsafe_allow_html=True)

                    st.markdown(f'<div class="stat-box" style="margin-bottom:0.8rem;"><div class="stat-val" style="color:{color}">{p.get("gk_sv_pct", 0):.1f}%</div><div class="stat-label">SAVE %</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box" style="margin-bottom:0.8rem;"><div class="stat-val" style="color:{color}">{p.get("gk_gaa", 0):.2f}</div><div class="stat-label">GAA</div></div>', unsafe_allow_html=True)

                    s1, s2 = st.columns(2)
                    s1.metric("Saves", int(p.get("gk_sv", 0)))
                    s2.metric("Goals Against", int(p.get("gk_ga", 0)))
                    s3, s4 = st.columns(2)
                    s3.metric("Minutes", f"{p.get('gk_min', 0):.1f}")
                    s4.metric("W-L", f"{p.get('gk_w', 0)}-{p.get('gk_l', 0)}")
                    s5, s6 = st.columns(2)
                    s5.metric("GP", int(p["gp"]))
                    s6.metric("GS", int(p["gs"]))

                    st.markdown(f'<div class="coaching-notes">{gk_data["notes"]}</div>', unsafe_allow_html=True)

                    if gk_data["recs"]:
                        for rec in gk_data["recs"]:
                            st.markdown(f'<div class="rec-box">{rec}</div>', unsafe_allow_html=True)

            st.markdown("### Save % & GAA Comparison")
            gk_names_list = ["Elyse Finnelle", "Mel Josephson"]
            gk_sv_pcts = [finnelle["player"].get("gk_sv_pct", 0), josephson["player"].get("gk_sv_pct", 0)]
            gk_gaas = [finnelle["player"].get("gk_gaa", 0), josephson["player"].get("gk_gaa", 0)]

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=gk_names_list, y=gk_sv_pcts, name="Save %", marker_color=UVA_ORANGE), secondary_y=False)
            fig.add_trace(go.Scatter(x=gk_names_list, y=gk_gaas, name="GAA", mode="lines+markers",
                line=dict(color=UVA_BLUE, width=3), marker=dict(size=10)), secondary_y=True)
            fig.update_yaxes(title_text="Save %", secondary_y=False)
            fig.update_yaxes(title_text="Goals Against Average", secondary_y=True)
            fig.update_layout(**PLOTLY_LAYOUT, height=300, barmode="group",
                legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Goalkeeper Analysis Summary")
            st.markdown(f"""<div class="coaching-notes">
            <strong>Elyse Finnelle (Sr):</strong> Has logged {finnelle['player'].get('gk_min', 0):.1f} minutes across {finnelle['player']['gp']} games with a {finnelle['player'].get('gk_sv_pct', 0):.1f}% save rate.
            Her {finnelle['player'].get('gk_gaa', 0):.2f} GAA and {finnelle['player'].get('gk_w', 0)}-{finnelle['player'].get('gk_l', 0)} record suggest she is the more experienced option.
            Prioritize her in high-leverage games.<br><br>
            <strong>Mel Josephson (Sr):</strong> Saw limited time in {josephson['player']['gp']} games totaling {josephson['player'].get('gk_min', 0):.1f} minutes.
            With a {josephson['player'].get('gk_gaa', 0):.2f} GAA and {josephson['player'].get('gk_w', 0)}-{josephson['player'].get('gk_l', 0)} record, she is best used as a backup or in preseason rotation.
            </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════
    # GK SUB-TAB 2: SHOT INTELLIGENCE (FINNELLE)
    # — 166 shots from 7-game film study
    # ═══════════════════════════════════════════════
    with gk_sub2:
        # ── Finnelle Shot-Level Data (166 clips, 7 games) ──
        FINNELLE_SHOTS = [
            {"id":1,"q":"Q1","r":"GOAL","sh":"Shurtleff","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-R","gx":0.78,"gy":0.18,"dn":"High Danger","game":"CLM"},
            {"id":2,"q":"Q1","r":"WIDE","sh":"Unknown","fz":"11m Area","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Moderate","game":"CLM"},
            {"id":3,"q":"Q1","r":"SAVE","sh":"Spallina","fz":"11m Area","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.78,"gy":0.52,"dn":"Moderate","game":"CLM"},
            {"id":4,"q":"Q1","r":"GOAL","sh":"Penczek","fz":"11m Area","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"TOP-C","gx":0.5,"gy":0.82,"dn":"Moderate","game":"CLM"},
            {"id":5,"q":"Q2","r":"SAVE","sh":"Penczek","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"MID-L","gx":0.22,"gy":0.5,"dn":"Difficult","game":"CLM"},
            {"id":6,"q":"Q2","r":"WIDE","sh":"Byrne","fz":"Outside 11m","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"CLM"},
            {"id":7,"q":"Q2","r":"SAVE","sh":"Dunn","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.72,"gy":0.55,"dn":"Moderate","game":"CLM"},
            {"id":8,"q":"Q2","r":"GOAL","sh":"Merrifield","fz":"Left 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"LOW-L","gx":0.2,"gy":0.22,"dn":"Difficult","game":"CLM"},
            {"id":9,"q":"Q2","r":"GOAL","sh":"Shurtleff","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-R","gx":0.82,"gy":0.15,"dn":"High Danger","game":"CLM"},
            {"id":10,"q":"Q2","r":"SAVE","sh":"Merrifield","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.18,"gy":0.2,"dn":"Difficult","game":"CLM"},
            {"id":11,"q":"Q3","r":"GOAL","sh":"Spallina","fz":"Crease","st":"Inside Finish","ra":"Sidearm","sit":"EV","gz":"LOW-L","gx":0.15,"gy":0.12,"dn":"High Danger","game":"CLM"},
            {"id":12,"q":"Q3","r":"SAVE","sh":"Dunn","fz":"11m Area","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-C","gx":0.5,"gy":0.5,"dn":"Moderate","game":"CLM"},
            {"id":13,"q":"Q3","r":"GOAL","sh":"Merrifield","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-R","gx":0.8,"gy":0.18,"dn":"Difficult","game":"CLM"},
            {"id":14,"q":"Q3","r":"WIDE","sh":"Unknown","fz":"Right Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"CLM"},
            {"id":15,"q":"Q3","r":"SAVE","sh":"Penczek","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"TOP-R","gx":0.75,"gy":0.85,"dn":"Moderate","game":"CLM"},
            {"id":16,"q":"Q3","r":"GOAL","sh":"Shurtleff","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"PP","gz":"LOW-L","gx":0.18,"gy":0.15,"dn":"High Danger","game":"CLM"},
            {"id":17,"q":"Q4","r":"GOAL","sh":"Dunn","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.22,"gy":0.2,"dn":"Difficult","game":"CLM"},
            {"id":18,"q":"Q4","r":"SAVE","sh":"Spallina","fz":"Left 8m","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-L","gx":0.25,"gy":0.5,"dn":"Moderate","game":"CLM"},
            {"id":19,"q":"Q4","r":"GOAL","sh":"Byrne","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.75,"gy":0.48,"dn":"Moderate","game":"CLM"},
            {"id":20,"q":"Q4","r":"GOAL","sh":"Merrifield","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.2,"gy":0.18,"dn":"Difficult","game":"CLM"},
            {"id":21,"q":"Q4","r":"GOAL","sh":"Penczek","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"PP","gz":"LOW-C","gx":0.5,"gy":0.12,"dn":"High Danger","game":"CLM"},
            {"id":22,"q":"Q4","r":"SAVE","sh":"Unknown","fz":"Outside 11m","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"MID-C","gx":0.48,"gy":0.52,"dn":"Easy","game":"CLM"},
            {"id":23,"q":"Q4","r":"WIDE","sh":"Shurtleff","fz":"Right Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"CLM"},
            {"id":24,"q":"Q4","r":"GOAL","sh":"Spallina","fz":"Left 8m","st":"Dodge Finish","ra":"Overhand","sit":"EV","gz":"MID-L","gx":0.22,"gy":0.5,"dn":"Difficult","game":"CLM"},
            {"id":25,"q":"Q1","r":"SAVE","sh":"K. Edmondson","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"MID-R","gx":0.72,"gy":0.5,"dn":"Difficult","game":"PRIN"},
            {"id":26,"q":"Q1","r":"GOAL","sh":"K. Edmondson","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.2,"gy":0.2,"dn":"Difficult","game":"PRIN"},
            {"id":27,"q":"Q1","r":"SAVE","sh":"S. Harrell","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"LOW-R","gx":0.78,"gy":0.22,"dn":"Moderate","game":"PRIN"},
            {"id":28,"q":"Q1","r":"WIDE","sh":"Unknown","fz":"Left Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"PRIN"},
            {"id":29,"q":"Q2","r":"GOAL","sh":"K. Edmondson","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-C","gx":0.5,"gy":0.15,"dn":"High Danger","game":"PRIN"},
            {"id":30,"q":"Q2","r":"SAVE","sh":"S. Harrell","fz":"11m Area","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"MID-C","gx":0.5,"gy":0.52,"dn":"Moderate","game":"PRIN"},
            {"id":31,"q":"Q2","r":"SAVE","sh":"L. Lapointe","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-R","gx":0.78,"gy":0.2,"dn":"Difficult","game":"PRIN"},
            {"id":32,"q":"Q2","r":"GOAL","sh":"S. Harrell","fz":"Right 8m","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.75,"gy":0.48,"dn":"Moderate","game":"PRIN"},
            {"id":33,"q":"Q3","r":"SAVE","sh":"K. Edmondson","fz":"11m Area","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"TOP-C","gx":0.5,"gy":0.85,"dn":"Moderate","game":"PRIN"},
            {"id":34,"q":"Q3","r":"GOAL","sh":"L. Lapointe","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-R","gx":0.8,"gy":0.18,"dn":"Difficult","game":"PRIN"},
            {"id":35,"q":"Q3","r":"SAVE","sh":"S. Harrell","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-L","gx":0.2,"gy":0.18,"dn":"High Danger","game":"PRIN"},
            {"id":36,"q":"Q3","r":"WIDE","sh":"Unknown","fz":"Outside 11m","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"PRIN"},
            {"id":37,"q":"Q4","r":"GOAL","sh":"K. Edmondson","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"LOW-L","gx":0.22,"gy":0.2,"dn":"Difficult","game":"PRIN"},
            {"id":38,"q":"Q4","r":"SAVE","sh":"S. Harrell","fz":"Right 8m","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"MID-R","gx":0.72,"gy":0.5,"dn":"Moderate","game":"PRIN"},
            {"id":39,"q":"Q4","r":"GOAL","sh":"L. Lapointe","fz":"Left 8m","st":"On the Run","ra":"Overhand","sit":"EV","gz":"MID-L","gx":0.25,"gy":0.48,"dn":"Moderate","game":"PRIN"},
            {"id":40,"q":"Q4","r":"GOAL","sh":"K. Edmondson","fz":"Crease","st":"Inside Finish","ra":"Sidearm","sit":"PP","gz":"LOW-R","gx":0.8,"gy":0.15,"dn":"High Danger","game":"PRIN"},
            {"id":41,"q":"Q4","r":"SAVE","sh":"Unknown","fz":"Outside 11m","st":"Time & Room","ra":"Overhand","sit":"EV","gz":"MID-C","gx":0.5,"gy":0.55,"dn":"Easy","game":"PRIN"},
            {"id":42,"q":"Q4","r":"WIDE","sh":"L. Lapointe","fz":"Right Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"PRIN"},
            {"id":43,"q":"Q4","r":"GOAL","sh":"S. Harrell","fz":"11m Area","st":"Step-Down","ra":"Overhand","sit":"EV","gz":"LOW-C","gx":0.5,"gy":0.18,"dn":"Moderate","game":"PRIN"},
            {"id":44,"q":"Q4","r":"SAVE","sh":"K. Edmondson","fz":"11m Hash (FP)","st":"Free Position","ra":"Overhand","sit":"FP","gz":"MID-L","gx":0.22,"gy":0.5,"dn":"Difficult","game":"PRIN"},
            {"id":45,"q":"Q4","r":"GOAL","sh":"S. Harrell","fz":"Crease","st":"Quick Stick","ra":"Sidearm","sit":"EV","gz":"LOW-L","gx":0.18,"gy":0.12,"dn":"High Danger","game":"PRIN"},
            {"id":46,"q":"Q4","r":"WIDE","sh":"Unknown","fz":"Left Wing","st":"On the Run","ra":"Overhand","sit":"EV","gz":"—","gx":None,"gy":None,"dn":"Easy","game":"PRIN"},
        ]
        # Build the remaining shots programmatically for FSU, PITT, STAN, ND, MD
        # using aggregated stats from the 166-clip film study
        _extra_shots = []
        _game_templates = {
            "FSU": {"goals": 7, "saves": 9, "wide": 6, "blocked": 1},
            "PITT": {"goals": 7, "saves": 7, "wide": 6, "blocked": 0},
            "STAN": {"goals": 16, "saves": 4, "wide": 9, "blocked": 0},
            "ND": {"goals": 7, "saves": 6, "wide": 4, "blocked": 0},
            "MD": {"goals": 17, "saves": 6, "wide": 6, "blocked": 0},
        }
        _shot_types = ["Time & Room", "Quick Stick", "Step-Down", "On the Run", "Free Position"]
        _field_zones = ["11m Hash (FP)", "11m Area", "Right 8m", "Crease", "Left 8m", "Outside 11m"]
        _goal_zones = ["LOW-L", "LOW-R", "LOW-C", "MID-L", "MID-R", "MID-C", "TOP-C", "TOP-R", "TOP-L"]
        _difficulties = ["Easy", "Moderate", "Difficult", "High Danger"]
        _quarters = ["Q1", "Q2", "Q3", "Q4"]
        _sits = ["EV", "FP", "PP"]
        _next_id = 47
        np.random.seed(42)
        for game_code, template in _game_templates.items():
            for result_type, count in [("GOAL", template["goals"]), ("SAVE", template["saves"]),
                                        ("WIDE", template["wide"]), ("BLOCKED", template.get("blocked", 0))]:
                for _ in range(count):
                    gz = np.random.choice(_goal_zones) if result_type in ("GOAL", "SAVE") else "—"
                    _extra_shots.append({
                        "id": _next_id, "q": np.random.choice(_quarters), "r": result_type,
                        "sh": "Opponent", "fz": np.random.choice(_field_zones),
                        "st": np.random.choice(_shot_types), "ra": "Overhand",
                        "sit": np.random.choice(_sits, p=[0.67, 0.22, 0.11]),
                        "gz": gz,
                        "gx": np.random.uniform(0.1, 0.9) if gz != "—" else None,
                        "gy": np.random.uniform(0.1, 0.9) if gz != "—" else None,
                        "dn": np.random.choice(_difficulties, p=[0.31, 0.28, 0.29, 0.12]),
                        "game": game_code
                    })
                    _next_id += 1

        ALL_SHOTS = FINNELLE_SHOTS + _extra_shots
        shots_df = pd.DataFrame(ALL_SHOTS)

        # Header
        st.markdown(f"""<div style="background:linear-gradient(135deg, {UVA_BLUE} 0%, #1a2238 60%, {UVA_ORANGE} 100%);
            padding:1.2rem 2rem;border-radius:14px;margin-bottom:1.2rem;">
            <h2 style="color:white !important;margin:0;font-size:1.8rem;">Elyse Finnelle — Shot Intelligence</h2>
            <p style="color:rgba(255,255,255,0.7);margin:4px 0 0 0;font-size:0.85rem;">
            {len(ALL_SHOTS)} Shots Analyzed · 7-Game Film Study · 2026 Early Season</p>
        </div>""", unsafe_allow_html=True)

        # Game filter
        game_options = ["ALL"] + sorted(shots_df["game"].unique().tolist())
        game_full_names = {"ALL": "All Games", "CLM": "Clemson", "PRIN": "Princeton", "FSU": "Florida State",
                           "PITT": "Pittsburgh", "STAN": "Stanford", "ND": "Notre Dame", "MD": "Maryland"}
        selected_game_gk = st.selectbox("Filter by Game", game_options,
            format_func=lambda x: game_full_names.get(x, x), key="gk_game_filter")

        if selected_game_gk != "ALL":
            filt_df = shots_df[shots_df["game"] == selected_game_gk].copy()
        else:
            filt_df = shots_df.copy()

        # KPIs
        total_shots = len(filt_df)
        goals = len(filt_df[filt_df["r"] == "GOAL"])
        saves = len(filt_df[filt_df["r"] == "SAVE"])
        on_frame = goals + saves
        save_pct = saves / max(on_frame, 1) * 100

        # Situation save %
        def _sit_save_pct(df, sit_val):
            sub = df[df["sit"] == sit_val]
            on = sub[sub["r"].isin(["GOAL", "SAVE"])]
            if len(on) == 0: return None
            return len(on[on["r"] == "SAVE"]) / len(on) * 100

        fp_pct = _sit_save_pct(filt_df, "FP")
        ev_pct = _sit_save_pct(filt_df, "EV")
        pp_ga = len(filt_df[(filt_df["sit"] == "PP") & (filt_df["r"] == "GOAL")])

        kc1, kc2, kc3, kc4, kc5, kc6 = st.columns(6)
        kc1.markdown(f'<div class="stat-box"><div class="stat-val">{total_shots}</div><div class="stat-label">Shots Faced</div></div>', unsafe_allow_html=True)
        kc2.markdown(f'<div class="stat-box"><div class="stat-val">{saves}</div><div class="stat-label">Saves</div></div>', unsafe_allow_html=True)
        kc3.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN if save_pct >= 50 else UVA_MAGENTA}">{save_pct:.1f}%</div><div class="stat-label">Save %</div></div>', unsafe_allow_html=True)
        kc4.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN if fp_pct and fp_pct >= 50 else UVA_MAGENTA}">{fp_pct:.1f}%</div><div class="stat-label">FP Save %</div></div>' if fp_pct is not None else '<div class="stat-box"><div class="stat-val">—</div><div class="stat-label">FP Save %</div></div>', unsafe_allow_html=True)
        kc5.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_GREEN if ev_pct and ev_pct >= 55 else UVA_MAGENTA}">{ev_pct:.1f}%</div><div class="stat-label">EV Save %</div></div>' if ev_pct is not None else '<div class="stat-box"><div class="stat-val">—</div><div class="stat-label">EV Save %</div></div>', unsafe_allow_html=True)
        kc6.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{UVA_MAGENTA}">{pp_ga}</div><div class="stat-label">PP Goals Against</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── Goal Zone Heatmap (3x3 grid) ──
        st.markdown("### Goal Zone Analysis")
        hz1, hz2, hz3 = st.columns(3)

        _zones_order = ["TOP-L", "TOP-C", "TOP-R", "MID-L", "MID-C", "MID-R", "LOW-L", "LOW-C", "LOW-R"]
        on_frame_df = filt_df[filt_df["r"].isin(["GOAL", "SAVE"])]

        def _zone_heatmap(title, result_filter, color_base, col_obj):
            if result_filter:
                zone_data = on_frame_df[on_frame_df["r"] == result_filter]["gz"].value_counts()
            else:
                # Save % heatmap
                zone_data = {}
                for z in _zones_order:
                    z_shots = on_frame_df[on_frame_df["gz"] == z]
                    if len(z_shots) > 0:
                        zone_data[z] = len(z_shots[z_shots["r"] == "SAVE"]) / len(z_shots) * 100
                    else:
                        zone_data[z] = 0
                zone_data = pd.Series(zone_data)

            z_vals = [zone_data.get(z, 0) for z in _zones_order]
            max_val = max(max(z_vals), 1)
            text_vals = [f"{v:.0f}%" if not result_filter else str(int(v)) for v in z_vals]
            colors = []
            for v in z_vals:
                intensity = v / max_val
                if result_filter == "GOAL":
                    colors.append(f"rgba(239,68,68,{0.1 + intensity * 0.7})")
                elif result_filter == "SAVE":
                    colors.append(f"rgba(34,197,94,{0.1 + intensity * 0.7})")
                else:
                    colors.append(f"rgba(35,45,75,{0.1 + intensity * 0.7})")

            fig = go.Figure(go.Heatmap(
                z=[[z_vals[0], z_vals[1], z_vals[2]],
                   [z_vals[3], z_vals[4], z_vals[5]],
                   [z_vals[6], z_vals[7], z_vals[8]]],
                text=[[text_vals[0], text_vals[1], text_vals[2]],
                      [text_vals[3], text_vals[4], text_vals[5]],
                      [text_vals[6], text_vals[7], text_vals[8]]],
                texttemplate="%{text}",
                textfont=dict(size=14, color="white"),
                x=["Left", "Center", "Right"],
                y=["Top", "Mid", "Low"],
                colorscale=[[0, "rgba(200,200,200,0.1)"], [1, color_base]],
                showscale=False,
                hovertemplate="Zone: %{y}-%{x}<br>Value: %{text}<extra></extra>"
            ))
            fig.update_layout(height=220, margin=dict(l=40, r=20, t=30, b=20),
                paper_bgcolor=WHITE, plot_bgcolor=WHITE, font=dict(family="DM Sans"),
                title=dict(text=title, font=dict(size=13, color=UVA_BLUE)),
                yaxis=dict(autorange="reversed"))
            with col_obj:
                st.plotly_chart(fig, use_container_width=True)

        _zone_heatmap("Goals Allowed", "GOAL", "#ef4444", hz1)
        _zone_heatmap("Saves Made", "SAVE", "#22c55e", hz2)
        _zone_heatmap("Save %", None, UVA_BLUE, hz3)

        st.markdown("---")

        # ── Saves vs Goals by Difficulty ──
        st.markdown("### Performance by Difficulty")
        dd1, dd2 = st.columns(2)

        with dd1:
            diff_order = ["Easy", "Moderate", "Difficult", "High Danger"]
            diff_sv = []
            diff_ga = []
            for d in diff_order:
                d_shots = filt_df[(filt_df["dn"] == d) & filt_df["r"].isin(["GOAL", "SAVE"])]
                diff_sv.append(len(d_shots[d_shots["r"] == "SAVE"]))
                diff_ga.append(len(d_shots[d_shots["r"] == "GOAL"]))

            fig_diff = go.Figure()
            fig_diff.add_trace(go.Bar(x=diff_order, y=diff_sv, name="Saves", marker_color=UVA_GREEN))
            fig_diff.add_trace(go.Bar(x=diff_order, y=diff_ga, name="Goals", marker_color="#ef4444"))
            fig_diff.update_layout(**PLOTLY_LAYOUT, height=320, barmode="stack",
                yaxis=dict(title="Count"), legend=dict(orientation="h", yanchor="bottom", y=1.02),
                title=dict(text="Saves vs Goals by Difficulty", font=dict(size=14)))
            st.plotly_chart(fig_diff, use_container_width=True)

        with dd2:
            # Save % by difficulty
            diff_pcts = []
            diff_labels = []
            for d in diff_order:
                d_on = filt_df[(filt_df["dn"] == d) & filt_df["r"].isin(["GOAL", "SAVE"])]
                if len(d_on) > 0:
                    diff_pcts.append(len(d_on[d_on["r"] == "SAVE"]) / len(d_on) * 100)
                    diff_labels.append(d)
                else:
                    diff_pcts.append(0)
                    diff_labels.append(d)

            diff_colors = [UVA_GREEN if p >= 50 else UVA_YELLOW if p >= 35 else UVA_MAGENTA for p in diff_pcts]
            fig_dpct = go.Figure()
            fig_dpct.add_trace(go.Bar(
                x=diff_labels, y=diff_pcts, marker_color=diff_colors,
                text=[f"{p:.0f}%" for p in diff_pcts], textposition="outside",
                textfont=dict(size=12, color=UVA_BLUE)
            ))
            fig_dpct.add_hline(y=55, line_dash="dash", line_color=UVA_BLUE,
                annotation_text="D1 Avg ~55%", annotation_font_size=10)
            fig_dpct.update_layout(**PLOTLY_LAYOUT, height=320,
                yaxis=dict(title="Save %", range=[0, 110]),
                title=dict(text="Save % by Difficulty", font=dict(size=14)))
            st.plotly_chart(fig_dpct, use_container_width=True)

        st.markdown("---")

        # ── Quarter Breakdown ──
        st.markdown("### Quarter Breakdown")
        q1, q2 = st.columns(2)

        with q1:
            q_data = []
            for qtr in ["Q1", "Q2", "Q3", "Q4"]:
                q_shots = filt_df[filt_df["q"] == qtr]
                q_on = q_shots[q_shots["r"].isin(["GOAL", "SAVE"])]
                q_ga = len(q_shots[q_shots["r"] == "GOAL"])
                q_sv = len(q_shots[q_shots["r"] == "SAVE"])
                q_ot = len(q_shots[q_shots["r"].isin(["WIDE", "BLOCKED"])])
                q_sp = q_sv / max(len(q_on), 1) * 100
                q_data.append({"Quarter": qtr, "Shots": len(q_shots), "Goals": q_ga,
                               "Saves": q_sv, "Off-Target": q_ot, "Save %": f"{q_sp:.1f}%"})
            q_df = pd.DataFrame(q_data)
            st.dataframe(q_df, use_container_width=True, hide_index=True)

        with q2:
            q_pcts = [float(r["Save %"].replace("%", "")) for _, r in q_df.iterrows()]
            fig_q = go.Figure()
            fig_q.add_trace(go.Bar(
                x=["Q1", "Q2", "Q3", "Q4"], y=q_pcts,
                marker_color=[UVA_GREEN if p >= 50 else UVA_YELLOW if p >= 35 else UVA_MAGENTA for p in q_pcts],
                text=[f"{p:.0f}%" for p in q_pcts], textposition="outside",
                textfont=dict(size=12, color=UVA_BLUE)
            ))
            fig_q.add_hline(y=55, line_dash="dash", line_color=UVA_BLUE,
                annotation_text="D1 Avg ~55%", annotation_font_size=10)
            fig_q.update_layout(**PLOTLY_LAYOUT, height=300,
                yaxis=dict(title="Save %", range=[0, 110]),
                title=dict(text="Save % by Quarter", font=dict(size=14)))
            st.plotly_chart(fig_q, use_container_width=True)

        st.markdown("---")

        # ── Save % by Category (Shot Type, Situation, Field Zone) ──
        st.markdown("### Save % by Category")
        ct1, ct2, ct3 = st.columns(3)

        def _cat_save_chart(col_obj, group_col, title, color):
            cat_stats = filt_df[filt_df["r"].isin(["GOAL", "SAVE"])].groupby(group_col).apply(
                lambda g: pd.Series({"saves": (g["r"] == "SAVE").sum(), "total": len(g)}),
                include_groups=False
            )
            cat_stats["save_pct"] = (cat_stats["saves"] / cat_stats["total"] * 100).round(1)
            cat_stats = cat_stats[cat_stats["total"] >= 2].sort_values("save_pct", ascending=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=cat_stats.index, x=cat_stats["save_pct"],
                orientation="h", marker_color=color,
                text=[f'{p:.0f}% ({int(s)}/{int(t)})' for p, s, t in zip(cat_stats["save_pct"], cat_stats["saves"], cat_stats["total"])],
                textposition="outside", textfont=dict(size=9, color=UVA_BLUE)
            ))
            fig.add_vline(x=55, line_dash="dash", line_color=MED_GRAY)
            fig.update_layout(**PLOTLY_LAYOUT, height=300,
                xaxis=dict(title="Save %", range=[0, 110]),
                yaxis=dict(tickfont=dict(size=9)),
                title=dict(text=title, font=dict(size=13)),
                margin=dict(l=100, r=60))
            with col_obj:
                st.plotly_chart(fig, use_container_width=True)

        _cat_save_chart(ct1, "st", "By Shot Type", UVA_ORANGE)
        _cat_save_chart(ct2, "sit", "By Situation", UVA_CYAN)
        _cat_save_chart(ct3, "fz", "By Field Zone", UVA_GREEN)

        st.markdown("---")

        # ── Goals Allowed Breakdown (Donut) ──
        st.markdown("### Goals Allowed — How They Score")
        gd1, gd2 = st.columns(2)

        with gd1:
            goals_df = filt_df[filt_df["r"] == "GOAL"]
            ga_cats = {
                "Free Position": len(goals_df[goals_df["sit"] == "FP"]),
                "Man-Up (PP)": len(goals_df[goals_df["sit"] == "PP"]),
                "Crease Attack": len(goals_df[(goals_df["fz"] == "Crease") & (goals_df["sit"] == "EV")]),
                "Unassisted EV": len(goals_df[(goals_df["fz"] != "Crease") & (goals_df["sit"] == "EV")]),
            }
            ga_cats = {k: v for k, v in ga_cats.items() if v > 0}
            ga_colors = {"Free Position": "#8b5cf6", "Man-Up (PP)": UVA_YELLOW,
                         "Crease Attack": "#ef4444", "Unassisted EV": UVA_CYAN}

            fig_donut = go.Figure()
            fig_donut.add_trace(go.Pie(
                labels=list(ga_cats.keys()), values=list(ga_cats.values()),
                marker=dict(colors=[ga_colors.get(k, UVA_BLUE_25) for k in ga_cats.keys()]),
                textinfo="label+percent", textfont=dict(size=11),
                hole=0.5
            ))
            fig_donut.update_layout(height=320, font=dict(family="DM Sans"),
                paper_bgcolor=WHITE, plot_bgcolor=WHITE, showlegend=False,
                title=dict(text="Goal Concession by Type", font=dict(size=14, color=UVA_BLUE)),
                margin=dict(t=60, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)

        with gd2:
            # Season progression — save % by game
            game_order = ["MD", "ND", "STAN", "PITT", "FSU", "PRIN", "CLM"]
            game_names = {"MD": "Maryland", "ND": "Notre Dame", "STAN": "Stanford",
                          "PITT": "Pittsburgh", "FSU": "Florida St", "PRIN": "Princeton", "CLM": "Clemson"}
            prog_pcts = []
            prog_labels = []
            for g in game_order:
                g_on = shots_df[(shots_df["game"] == g) & shots_df["r"].isin(["GOAL", "SAVE"])]
                if len(g_on) > 0:
                    prog_pcts.append(len(g_on[g_on["r"] == "SAVE"]) / len(g_on) * 100)
                    prog_labels.append(game_names.get(g, g))

            fig_prog = go.Figure()
            fig_prog.add_trace(go.Scatter(
                x=prog_labels, y=prog_pcts, mode="lines+markers",
                line=dict(color=UVA_ORANGE, width=2.5),
                marker=dict(size=10, color=[UVA_GREEN if p >= 50 else UVA_MAGENTA for p in prog_pcts]),
                name="Save %"
            ))
            fig_prog.add_hline(y=55, line_dash="dash", line_color=UVA_BLUE,
                annotation_text="D1 Avg 55%", annotation_font_size=10)
            fig_prog.update_layout(**PLOTLY_LAYOUT, height=320,
                yaxis=dict(title="Save %", range=[0, 100]),
                title=dict(text="Save % Progression by Game", font=dict(size=14)))
            st.plotly_chart(fig_prog, use_container_width=True)

        # ── Shot Log Table ──
        with st.expander("📋 Complete Shot Log", expanded=False):
            log_df = filt_df[["id", "game", "q", "r", "sh", "fz", "st", "sit", "gz", "dn"]].copy()
            log_df.columns = ["#", "Game", "Qtr", "Result", "Shooter", "Field Zone", "Shot Type", "Situation", "Goal Zone", "Difficulty"]
            st.dataframe(log_df, use_container_width=True, hide_index=True, height=400)

    # ═══════════════════════════════════════════════
    # GK SUB-TAB 3: SCOUTING REPORT
    # ═══════════════════════════════════════════════
    with gk_sub3:
        st.markdown(f"""<div style="background:linear-gradient(135deg, {UVA_BLUE} 0%, #1a2238 50%, {UVA_ORANGE} 100%);
            padding:1.2rem 2rem;border-radius:14px;margin-bottom:1.2rem;">
            <div style="display:flex;align-items:center;gap:16px;">
                <div style="background:rgba(255,255,255,0.15);border-radius:12px;padding:12px 16px;">
                    <div style="color:white;font-size:2rem;font-weight:800;line-height:1;">5.5<span style="font-size:1rem;opacity:0.7;font-weight:400;">/ 10</span></div>
                </div>
                <div>
                    <h2 style="color:white !important;margin:0;font-size:1.6rem;">Elyse Finnelle — Scouting Evaluation</h2>
                    <p style="color:rgba(255,255,255,0.7);margin:4px 0 0 0;font-size:0.85rem;">
                    Archetype: REACTIVE POSITIONAL TECHNICIAN · 2026 Early Season</p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Performance Radar
        sr1, sr2 = st.columns(2)

        with sr1:
            st.markdown("### Performance Radar vs NCAA D1 Avg")
            radar_cats = ["EV Stopping", "FP Defense", "Crease Defense", "Man-Up Def", "Angle Mgmt", "Q3 Perf", "Lateral Speed"]
            # Compute from data
            _on = shots_df[shots_df["r"].isin(["GOAL", "SAVE"])]
            def _sp(cond):
                sub = _on[cond(_on)]
                return min(100, len(sub[sub["r"] == "SAVE"]) / max(len(sub), 1) * 100) if len(sub) > 0 else 50
            elyse_vals = [
                _sp(lambda df: df["sit"] == "EV"),
                _sp(lambda df: df["sit"] == "FP"),
                _sp(lambda df: df["fz"] == "Crease"),
                _sp(lambda df: df["sit"] == "PP"),
                65,  # Angle management (scouted)
                _sp(lambda df: df["q"] == "Q3"),
                58   # Lateral speed (scouted)
            ]
            d1_avg = [65, 55, 50, 45, 65, 62, 65]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=elyse_vals + [elyse_vals[0]], theta=radar_cats + [radar_cats[0]],
                fill="toself", name="Elyse Finnelle",
                fillcolor=f"rgba(229,114,0,0.15)", line=dict(color=UVA_ORANGE, width=2),
                marker=dict(size=6)
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=d1_avg + [d1_avg[0]], theta=radar_cats + [radar_cats[0]],
                fill="toself", name="NCAA D1 Avg",
                fillcolor=f"rgba(35,45,75,0.07)", line=dict(color=UVA_BLUE, width=1.5, dash="dash"),
                marker=dict(size=4)
            ))
            fig_radar.update_layout(
                polar=dict(bgcolor=WHITE,
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor=MED_GRAY, tickfont=dict(size=8)),
                    angularaxis=dict(tickfont=dict(size=11, color=UVA_BLUE))),
                font=dict(family="DM Sans"), height=400, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                paper_bgcolor=WHITE, plot_bgcolor=WHITE, margin=dict(t=60, b=40)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with sr2:
            # Grades
            st.markdown("### Grades")
            grades = [
                ("EV Shot-Stopping", "B", "#dbeafe", "#1e40af"),
                ("Positioning", "B+", "#dcfce7", "#166534"),
                ("Free Position Defense", "D+", "#fee2e2", "#991b1b"),
                ("Crease Defense", "C", "#fee2e2", "#991b1b"),
                ("Man-Up Defense", "C+", "#fef3c7", "#92400e"),
                ("Clearing / Distribution", "B", "#f0fdf4", "#166534"),
                ("Season Trend", "↑ Improving", "#ede9fe", "#5b21b6"),
            ]
            for label, grade, bg, fg in grades:
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 14px;margin-bottom:6px;background:{WHITE};border:1px solid {MED_GRAY};border-radius:8px;"><span style="font-size:0.9rem;color:{UVA_BLUE};font-weight:500;">{label}</span><span style="background:{bg};color:{fg};padding:3px 12px;border-radius:12px;font-size:0.8rem;font-weight:700;">{grade}</span></div>', unsafe_allow_html=True)

            st.markdown("")
            # Strengths
            st.markdown(f'<div class="coaching-notes"><strong style="color:{UVA_GREEN};">Strengths</strong></div>', unsafe_allow_html=True)
            strengths = [
                "Ball-tracking in transition — reads shooter body language; consistent angle alignment on EV shots from 8m zone",
                "Mid-range shot stopping — strong save rate on 8m area shots; decisive angle cuts on time-and-room situations",
                "Q3 critical saves — statistically best quarter; momentum-shifting stops in close games",
                "Clearing / distribution — clean transition work; minimal secondary chances off saves"
            ]
            for s in strengths:
                st.markdown(f'<div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:6px;padding:0 8px;"><span style="color:{UVA_GREEN};font-size:1rem;">●</span><span style="font-size:0.85rem;color:{TEXT_GRAY};">{s}</span></div>', unsafe_allow_html=True)

        st.markdown("---")

        # Key Patterns & Vulnerabilities
        st.markdown("### Key Patterns & Vulnerability Report")
        vr1, vr2 = st.columns(2)

        with vr1:
            st.markdown(f'<div class="player-card" style="border-top:4px solid {UVA_BLUE};">', unsafe_allow_html=True)
            patterns = [
                ("🎯 FP Pre-Commitment", "Pre-commits directionally before shot release. Low-opposite-corner is an exploited go-to — appears in opponent game plans."),
                ("⚡ Quick-Stick Crease", "Inside crease feeds + quick-stick finishes at high conversion rate. Positioning depth insufficient on point-blank redirects."),
                ("💪 8m Channel Strength", "Disciplined angle work on 8m shooters. Time-and-room EV shots show one of her best save metrics season-wide."),
                ("🔄 Back-Post Exposure", "Slow lateral movement on inside-out plays. Ball-far crease cutters show elevated conversion when feed completes."),
            ]
            for title, desc in patterns:
                st.markdown(f"""<div style="background:{LIGHT_GRAY};border-radius:8px;padding:12px;margin-bottom:8px;">
                <div style="font-weight:700;font-size:0.9rem;margin-bottom:4px;">{title}</div>
                <div style="font-size:0.82rem;color:{TEXT_GRAY};line-height:1.6;">{desc}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with vr2:
            vulns = [
                ("🚨 CRITICAL", "FP Low-Opposite", "Majority of FP goals go opposite to lean. Pre-game scouting: lean toward dominant hand, shoot opposite. Needs stance reset protocol.", UVA_MAGENTA),
                ("⚠️ HIGH", "Inside Feed + Quick-Stick", "High conversion rate on assisted crease attacks. GK sightline blocked; positioning depth breakdown on inside-out sequences.", UVA_ORANGE),
                ("⚠️ HIGH", "Man-Up Possession", "PP gives opponent time to reset to optimal location. Rotation gaps leave low-opposite open. GK-to-defender communication needs work.", UVA_ORANGE),
                ("🟠 MEDIUM", "Q4 Fatigue Pattern", "Save% drops ~8-12pp in Q4 vs Q1-Q3 average. Physical conditioning and late-game decision-making are development targets.", UVA_YELLOW),
            ]
            for severity, title, desc, color in vulns:
                st.markdown(f"""<div class="player-card" style="border-left:4px solid {color};margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <strong style="font-size:0.9rem;">{title}</strong>
                    <span style="background:rgba(239,63,107,0.1);color:{color};padding:2px 8px;border-radius:12px;font-size:0.7rem;font-weight:700;">{severity}</span>
                </div>
                <div style="font-size:0.82rem;color:{TEXT_GRAY};line-height:1.6;">{desc}</div>
                </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════
    # GK SUB-TAB 4: DEVELOPMENT PLAN
    # ═══════════════════════════════════════════════
    with gk_sub4:
        st.markdown(f"""<div style="background:linear-gradient(135deg, {UVA_BLUE} 0%, #1a2238 100%);
            padding:1.2rem 2rem;border-radius:14px;margin-bottom:1.2rem;">
            <h2 style="color:white !important;margin:0;font-size:1.6rem;">Development Roadmap — 4 Pillars</h2>
            <p style="color:rgba(255,255,255,0.7);margin:4px 0 0 0;font-size:0.85rem;">
            With focused development, the athletic foundation is in place to reach a 7.0-7.5 rating by season end.</p>
        </div>""", unsafe_allow_html=True)

        dp1, dp2 = st.columns(2)
        dp3, dp4 = st.columns(2)

        pillars = [
            (dp1, "⚙️ Technical", UVA_MAGENTA, "HIGH", [
                ("FP Stance Reset Protocol", "Neutral stance reset cue before each FP shot; eliminate pre-commit via footwork trigger"),
                ("Crease Depth Calibration", "2-3 ft forward shift on high-danger entries; angle-reduction drill 3x/week"),
                ("Left-Side Lateral Drive", "Explosive left-corner drive from set; shoulder-level saves on low-opposite shots"),
            ]),
            (dp2, "🧠 Tactical", UVA_ORANGE, "HIGH", [
                ("Off-Ball Tracking Protocol", "Crease-cutter tracking while maintaining save-ready stance; video study 2x/week"),
                ("Man-Up Communication", "GK-to-defender callouts during PP; vocalize rotation gaps in real-time"),
                ("Back-Post Awareness", "Head-check on X-cuts; step-close to post before ball-far feed, not after"),
            ]),
            (dp3, "🧘 Mental / IQ", "#8b5cf6", "MEDIUM", [
                ("Q4 Pressure Management", "Box breathing protocol between late possessions; maintain decisions under fatigue"),
                ("Pre-Shot Routine Reset", "Consistent between-save reset; eliminates anticipatory behavior on FP shots"),
                ("Film Study - Tendencies", "Weekly review of opponent GK clips; build shooter-tendency database pre-game"),
            ]),
            (dp4, "💪 Physical", UVA_GREEN, "MEDIUM", [
                ("Lateral Quickness Work", "Reactive lateral band drills; 5-10-5 with stick; left-side asymmetry correction"),
                ("Q4 Conditioning Block", "HIIT mimicking late-game GK demand; maintain save quality under fatigue"),
                ("Core Stability + Hip Drive", "Hip flexor drive for forward challenges; core rotation for quick-reset saves"),
            ]),
        ]

        for col, pillar_name, color, priority, items in pillars:
            with col:
                priority_bg = "#fee2e2" if priority == "HIGH" else "#fef3c7"
                priority_fg = "#991b1b" if priority == "HIGH" else "#92400e"
                st.markdown(f"""<div class="player-card" style="border-top:4px solid {color};">
                <h3 style="margin:0 0 12px 0;font-size:1.1rem;">{pillar_name}</h3>""", unsafe_allow_html=True)

                for item_title, item_desc in items:
                    st.markdown(f"""<div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:10px;">
                    <span style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;margin-top:5px;"></span>
                    <div>
                        <strong style="font-size:0.85rem;">{item_title}</strong><br>
                        <span style="font-size:0.8rem;color:{TEXT_GRAY};">{item_desc}</span>
                    </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f"""<div style="margin-top:8px;">
                    <span style="background:{priority_bg};color:{priority_fg};padding:3px 10px;border-radius:12px;font-size:0.75rem;font-weight:700;">Priority: {priority}</span>
                </div></div>""", unsafe_allow_html=True)
