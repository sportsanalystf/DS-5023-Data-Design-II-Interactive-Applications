"""
Chart builders for Player Intelligence dashboard.
Creates radar charts, game logs, efficiency plots, and team-wide visualizations.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from style import (UVA_BLUE, UVA_ORANGE, UVA_BLUE_25, UVA_ORANGE_25,
                   CYAN as UVA_CYAN, YELLOW as UVA_YELLOW, TEAL as UVA_TEAL,
                   GREEN as UVA_GREEN, MAGENTA as UVA_MAGENTA,
                   LIGHT_BG as LIGHT_GRAY, BORDER as MED_GRAY, TEXT_MUTED as TEXT_GRAY,
                   WHITE, PLOT_LAYOUT)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=WHITE,
    font=dict(color=UVA_BLUE),
    margin=dict(l=30, r=30, t=40, b=30),
)


def make_radar_chart(scores, pos, height=300):
    """Create a position-specific radar chart showing player strengths across key dimensions."""
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
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=WHITE,
        font=dict(color=UVA_BLUE),
        margin=dict(l=10, r=10, t=20, b=20),
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
    """Create a game-by-game performance line and bar chart showing points, goals, and turnovers."""
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
    """Create a shot funnel visualization showing total shots, shots on goal, and goals."""
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
    """Create a horizontal bar chart showing percentile rankings across impact categories."""
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
        textfont=dict(size=12, color=WHITE), showlegend=False))
    fig.update_layout(**PLOTLY_LAYOUT, height=200, barmode="overlay",
        xaxis=dict(range=[0, 100], visible=False),
        yaxis=dict(tickfont=dict(size=11, color=TEXT_GRAY), autorange="reversed"))
    return fig


def make_rolling_avg_chart(p):
    """Create a rolling 3-game average chart to smooth out performance trends."""
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
    """Create a cumulative points chart for top scorers across the season."""
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
    """Create a quadrant plot showing player usage vs efficiency (shots per game vs shooting %)."""
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
    fig.update_layout(**PLOTLY_LAYOUT, height=450)
    return fig


def make_draw_control_chart(all_data):
    """Create a bar chart of top draw control players (key possession stat)."""
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
