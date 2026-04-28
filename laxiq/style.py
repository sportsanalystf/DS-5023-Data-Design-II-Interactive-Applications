# style constants and helpers

# colors
UVA_BLUE = "#232D4B"
UVA_BLUE_25 = "#C8CBD2"
UVA_ORANGE = "#E57200"
UVA_ORANGE_25 = "#F9DCBF"
CYAN = "#009FDF"
YELLOW = "#FDDA24"
TEAL = "#25CAD3"
GREEN = "#62BB46"
MAGENTA = "#EF3F6B"

# semantic colors
POSITIVE = "#2E7D32"
NEGATIVE = "#C62828"
NEUTRAL_GRAY = "#666666"
LIGHT_BG = "#F7F8FA"
WHITE = "#FFFFFF"
BORDER = "#DADADA"
TEXT_PRIMARY = UVA_BLUE
TEXT_MUTED = "#666666"

# plotly theme
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=WHITE,
    font=dict(color=UVA_BLUE),
    margin=dict(l=50, r=20, t=50, b=40),
)

# CSS — hide auto-nav, metric cards, tab styling
CSS = """
<style>
/* hide streamlit auto page navigation */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] nav { display: none !important; }
section[data-testid="stSidebar"] ul[data-testid="stSidebarNavItems"] { display: none !important; }

/* metric cards — bordered, centered */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 14px 16px;
    text-align: center;
}
[data-testid="stMetric"] label { justify-content: center; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { justify-content: center; }
[data-testid="stMetric"] [data-testid="stMetricDelta"] { justify-content: center; }

/* tab styling */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    padding: 10px 24px;
    border-radius: 8px 8px 0 0;
    font-weight: 600;
}
</style>
"""


# simple helper to show a metric in a styled card
def metric_card(value, label, color_class=""):
    vc = f' {color_class}' if color_class else ''
    return (
        f'<div style="text-align:center;padding:14px;background:#FFFFFF;'
        f'border:1px solid #E0E0E0;border-radius:8px;">'
        f'<div style="font-size:1.4rem;font-weight:700;color:#232D4B;{vc}">{value}</div>'
        f'<div style="font-size:0.75rem;color:#666;margin-top:4px;">{label}</div></div>'
    )


def insight_box(text, variant=""):
    color = "#E57200"
    if "green" in variant:
        color = POSITIVE
    elif "red" in variant:
        color = NEGATIVE
    return (
        f'<div style="border-left:3px solid {color};padding:10px 14px;margin:6px 0;'
        f'font-size:0.85rem;background:#FFFFFF;border-radius:0 6px 6px 0;">{text}</div>'
    )


def moment_card(title, description, wpa=None, variant=""):
    wpa_html = ""
    if wpa is not None:
        color = POSITIVE if wpa > 0 else NEGATIVE
        wpa_html = f' <span style="color:{color};font-weight:600;">({wpa:+.1f}%)</span>'
    return (
        f'<div style="border-left:3px solid #E57200;padding:10px 14px;margin:8px 0;'
        f'background:#FFFFFF;border-radius:0 6px 6px 0;">'
        f'<div style="font-weight:600;color:#232D4B;">{title}{wpa_html}</div>'
        f'<div style="font-size:0.85rem;color:#666;margin-top:4px;">{description}</div></div>'
    )


def section_header(title, subtitle=None):
    """Render a section header with UVA orange accent bar."""
    html = (
        f'<div style="border-left:4px solid #E57200;padding:4px 12px;margin:20px 0 12px 0;">'
        f'<span style="font-size:1.1rem;font-weight:700;color:#232D4B;">{title}</span>'
    )
    if subtitle:
        html += f'<br><span style="font-size:0.8rem;color:#666;">{subtitle}</span>'
    html += '</div>'
    return html
