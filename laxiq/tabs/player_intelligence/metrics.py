"""
Metrics computation and scoring engine for Player Intelligence dashboard.
Handles advanced metrics calculation, impact scoring, tier assignment, and player evaluation.
"""
import numpy as np


def compute_advanced_metrics(p):
    """Calculate advanced metrics for a player based on raw stats."""
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
    """Calculate impact scores across six dimensions: offensive, defensive, possession, efficiency, discipline, overall."""
    pos = p["pos"]
    scores = {}

    def norm(val, max_val, invert=False):
        """Normalize a value to 0-100 scale."""
        if max_val == 0:
            return 50
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

    # weights based on what matters most for each position
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
    """Identify key development flags and player strengths based on performance data."""
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
    """Classify player into tier 1-4 based on overall impact score."""
    s = scores["overall"]
    if s >= 65: return 1, "Program Driver"
    elif s >= 45: return 2, "System Amplifier"
    elif s >= 25: return 3, "Situational Specialist"
    else: return 4, "Developmental"


def generate_coaching_notes(name, p, metrics, scores, tier_num, flags):
    """Generate personalized coaching notes for player evaluation."""
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
    """Generate position-specific coaching recommendations for player development."""
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
