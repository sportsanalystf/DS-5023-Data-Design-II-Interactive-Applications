# style constants and helpers for laxiq

# --- colors ---
# colors from https://brand.virginia.edu

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
LIGHT_BG = "#F1F1EF"
WHITE = "#FFFFFF"
BORDER = "#DADADA"
TEXT_PRIMARY = UVA_BLUE
TEXT_MUTED = "#666666"

# --- plotly theme ---

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=WHITE,
    font=dict(family="DM Sans, sans-serif", color=UVA_BLUE, size=12),
    margin=dict(l=50, r=20, t=50, b=40),
    xaxis=dict(gridcolor="#ECECEC", zerolinecolor=BORDER, linecolor=BORDER),
    yaxis=dict(gridcolor="#ECECEC", zerolinecolor=BORDER, linecolor=BORDER),
)

# --- css ---
# most of this CSS is for overriding streamlit defaults

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Bebas+Neue&display=swap');

/* Light background */
.stApp { background: #F1F1EF; }
section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #DADADA; }

/* Hide Streamlit's auto-generated page navigation in the sidebar */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] nav { display: none !important; }
section[data-testid="stSidebar"] ul[data-testid="stSidebarNavItems"] { display: none !important; }
section[data-testid="stSidebar"] * { color: #232D4B !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label { color: #666666 !important; font-size: 0.8rem; }
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
    background: #F1F1EF !important;
    border: 1px solid #DADADA !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div > div,
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] .stSelectbox div[role="combobox"],
section[data-testid="stSidebar"] .stSelectbox div[role="combobox"] * {
    color: #232D4B !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    -webkit-text-fill-color: #232D4B !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg {
    fill: #232D4B !important;
}
/* Make dropdown menu items readable (dark text on white bg) */
section[data-testid="stSidebar"] [data-baseweb="popover"] li,
section[data-testid="stSidebar"] [data-baseweb="popover"] li * {
    color: #232D4B !important;
    -webkit-text-fill-color: #232D4B !important;
    font-weight: 500 !important;
}

/* Ensure main content text is dark on light background */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    color: #232D4B !important;
}
.stApp .stMarkdown p, .stApp .stMarkdown li {
    color: #333 !important;
}
.stApp .stTabs [data-baseweb="tab-list"] button {
    color: #232D4B !important;
}
.stApp .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #E57200 !important;
}

/* Metric card */
.metric-card {
    background: white; border: 1px solid #DADADA; border-radius: 12px;
    padding: 16px; text-align: center; box-shadow: 0 2px 8px rgba(35,45,75,0.06);
}
.metric-value { font-size: 1.6rem; font-weight: 700; color: #232D4B; }
.metric-label { font-size: 0.7rem; color: #666; text-transform: uppercase; letter-spacing: 1.2px; margin-top: 4px; font-weight: 600; }
.val-pos { color: #2E7D32; }
.val-neg { color: #C62828; }
.val-orange { color: #E57200; }

/* Game header */
.game-header {
    background: linear-gradient(135deg, #232D4B 0%, #3A4F7A 50%, #E57200 100%);
    border-radius: 14px; padding: 24px 32px; text-align: center; color: white;
    margin-bottom: 16px;
}
.game-header .teams { display: flex; align-items: center; justify-content: center; gap: 32px; margin-top: 10px; }
.game-header .team-name { font-size: 0.9rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; }
.game-header .score { font-size: 3rem; font-weight: 700; line-height: 1; }
.game-header .badge { padding: 3px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; letter-spacing: 1.5px; }

/* Insight box */
.insight-box {
    background: white; border-left: 4px solid #E57200;
    border-radius: 0 10px 10px 0; padding: 14px 18px;
    margin: 8px 0; font-size: 0.88rem; line-height: 1.6;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.insight-green { border-left-color: #2E7D32; background: #F1F8E9; }
.insight-red { border-left-color: #C62828; background: #FDE8E8; }
.insight-blue { border-left-color: #232D4B; }

/* Moment card */
.moment-card {
    background: white; border: 1px solid #DADADA; border-radius: 12px;
    padding: 18px 22px; margin-bottom: 12px; border-left: 5px solid #E57200;
    box-shadow: 0 2px 8px rgba(35,45,75,0.06);
}
.moment-card.pos { border-left-color: #2E7D32; }
.moment-card.neg { border-left-color: #C62828; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: white; border: 1px solid #DADADA; color: #666;
    border-radius: 8px 8px 0 0; font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #232D4B; border-color: #232D4B; color: white;
}

/* Enhanced game header with records and quarter scores */
.game-header-v2 {
    background: linear-gradient(135deg, #232D4B 0%, #3A4F7A 50%, #E57200 100%);
    border-radius: 14px 14px 0 0; padding: 28px 32px 20px; text-align: center; color: white;
}
.game-header-v2 .meta-line {
    font-size: 0.7rem; opacity: 0.6; letter-spacing: 1.5px;
    text-transform: uppercase; font-weight: 600; margin-bottom: 12px;
}
.game-header-v2 .teams-row {
    display: flex; align-items: center; justify-content: center; gap: 40px;
}
.game-header-v2 .team-block { text-align: center; }
.game-header-v2 .team-name {
    font-size: 0.9rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
}
.game-header-v2 .team-record {
    font-size: 0.7rem; opacity: 0.5; margin-top: 2px;
}
.game-header-v2 .score {
    font-size: 3.2rem; font-weight: 700; line-height: 1; margin-top: 4px;
}
.game-header-v2 .score.loser { opacity: 0.35; }
.game-header-v2 .final-label {
    font-size: 0.75rem; opacity: 0.35; letter-spacing: 2px; font-weight: 600;
}
.game-header-v2 .badge {
    padding: 3px 14px; border-radius: 20px; font-size: 0.68rem;
    font-weight: 700; letter-spacing: 1.5px; position: absolute; right: 32px; top: 28px;
}
.game-header-v2 { position: relative; }

/* Quarter score pills */
.quarter-pills {
    display: flex; justify-content: center; gap: 6px; margin-top: 14px;
}
.quarter-pills .qp {
    background: rgba(255,255,255,0.12); border-radius: 8px;
    padding: 4px 12px; font-size: 0.72rem; text-align: center;
}
.quarter-pills .qp .qlabel {
    font-size: 0.6rem; opacity: 0.5; letter-spacing: 1px; text-transform: uppercase;
}
.quarter-pills .qp .qscore { font-weight: 700; font-size: 0.8rem; }

/* Letter grade cards row */
.grade-strip {
    display: flex; background: #1a2238; border-radius: 0 0 14px 14px;
    overflow: hidden; margin-bottom: 18px;
}
.grade-card {
    flex: 1; text-align: center; padding: 14px 8px;
    border-right: 1px solid rgba(255,255,255,0.08);
}
.grade-card:last-child { border-right: none; }
.grade-card .grade-label {
    font-size: 0.62rem; color: rgba(255,255,255,0.5);
    text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;
}
.grade-card .grade-value {
    font-size: 1.5rem; font-weight: 700; margin-top: 4px;
}

/* Dark stat comparison card */
.stat-comparison-dark {
    background: #232D4B; border-radius: 12px; padding: 20px; color: white;
}
</style>
"""


# --- html helpers ---

def metric_card(value, label, color_class=""):
    # generates the metric card html
    vc = f' {color_class}' if color_class else ''
    return f'<div class="metric-card"><div class="metric-value{vc}">{value}</div><div class="metric-label">{label}</div></div>'


def game_header(home_team, away_team, home_score, away_score, result, date, location=""):
    badge_bg = "#2E7D32" if result == "W" else "#C62828"
    badge_text = "WIN" if result == "W" else "LOSS"
    loser_style = 'opacity:0.4'
    return f'''<div class="game-header">
        <div style="font-size:0.72rem;opacity:0.6;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">
            Women's Lacrosse &middot; {date} &middot; {location}
            <span class="badge" style="background:{badge_bg};margin-left:10px;">{badge_text}</span>
        </div>
        <div class="teams">
            <div>
                <div class="team-name" style="color:#F9DCBF;">{home_team}</div>
                <div class="score">{home_score}</div>
            </div>
            <div style="font-size:0.8rem;opacity:0.35;letter-spacing:2px;font-weight:600;">FINAL</div>
            <div>
                <div class="team-name" style="color:#C8CBD2;">{away_team}</div>
                <div class="score" style="{loser_style if result == 'W' else ''}">{away_score}</div>
            </div>
        </div>
    </div>'''


def insight_box(text, variant=""):
    # generates insight box html with optional variant
    cls = f"insight-box {variant}" if variant else "insight-box"
    return f'<div class="{cls}">{text}</div>'


def game_header_v2(home_team, away_team, home_score, away_score, result, date,
                    location="", home_record="", away_record="", quarter_scores=None):
    # enhanced game header with quarter pills and records
    badge_bg = "#2E7D32" if result == "W" else "#C62828"
    badge_text = "WIN" if result == "W" else "LOSS"
    loser_cls = ' loser' if result == "W" else ''
    winner_cls = ' loser' if result == "L" else ''

    # Quarter pills HTML
    qp_html = ""
    if quarter_scores:
        pills = []
        for i, (h, a) in enumerate(quarter_scores):
            pills.append(f'<div class="qp"><div class="qlabel">Q{i+1}</div><div class="qscore">{h}-{a}</div></div>')
        qp_html = f'<div class="quarter-pills">{"".join(pills)}</div>'

    rec_home = f'<div class="team-record">{home_record}</div>' if home_record else ''
    rec_away = f'<div class="team-record">{away_record}</div>' if away_record else ''

    return f'''<div class="game-header-v2">
        <div class="meta-line">Women's Lacrosse &middot; {date} &middot; {location}</div>
        <span class="badge" style="background:{badge_bg};">{badge_text}</span>
        <div class="teams-row">
            <div class="team-block">
                <div class="team-name" style="color:#F9DCBF;">{home_team}</div>
                {rec_home}
                <div class="score{winner_cls}">{home_score}</div>
            </div>
            <div class="final-label">FINAL</div>
            <div class="team-block">
                <div class="team-name" style="color:#C8CBD2;">{away_team}</div>
                {rec_away}
                <div class="score{loser_cls}">{away_score}</div>
            </div>
        </div>
        {qp_html}
    </div>'''


def grade_strip(grades):
    # probably could simplify this but it works
    from analytics import grade_color
    categories = ["Offense", "Defense", "Transition", "Draw Unit", "Goalkeeping", "Discipline"]
    cards = []
    for cat in categories:
        g = grades.get(cat, "N/A")
        color = grade_color(g)
        cards.append(f'''<div class="grade-card">
            <div class="grade-label">{cat.upper()}</div>
            <div class="grade-value" style="color:{color};">{g}</div>
        </div>''')
    return f'<div class="grade-strip">{"".join(cards)}</div>'


def moment_card(title, description, wpa=None, variant=""):
    # creates a moment card with optional wpa indicator
    cls = f"moment-card {variant}"
    wpa_html = ""
    if wpa is not None:
        color = POSITIVE if wpa > 0 else NEGATIVE
        bg = "rgba(46,125,50,0.1)" if wpa > 0 else "rgba(200,40,40,0.1)"
        wpa_html = f'<span style="font-family:monospace;font-size:0.85rem;font-weight:600;padding:2px 8px;border-radius:5px;background:{bg};color:{color};">{wpa:+.1f}%</span>'
    return f'''<div class="{cls}">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <div style="font-weight:700;font-size:0.95rem;color:{UVA_BLUE};">{title}</div>{wpa_html}
        </div>
        <div style="font-size:0.85rem;color:#666;line-height:1.7;">{description}</div>
    </div>'''
