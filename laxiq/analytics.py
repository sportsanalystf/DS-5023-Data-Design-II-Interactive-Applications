# analytics engine for laxiq - computes stats from box score data

import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import glob
import math

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# --- roster data ---
POSITION_MAP = {
    "Jayden Piraino": "A", "Jenna Dinardo": "A", "Addi Foster": "A",
    "Madison Alaimo": "A", "Gabby Laverghetta": "A", "Fiona Allen": "A",
    "Raleigh Foster": "A", "Payton Shroads": "A", "Bella Gutierrez": "A",
    "Kaitlyn Levy": "A",
    "Kate Galica": "M", "Cady Flaherty": "M", "Alex Reilly": "M",
    "Sophia Conti": "M", "Livy Laverghetta": "M", "Carly Kennedy": "M",
    "Megan Rocklein": "M", "Jamie Gates": "M", "Rachel Clark": "M",
    "Sammy Kincaid": "M", "Ashlyn McGovern": "M", "Mackenzie Samson": "M",
    "Lauren DiGiovanni": "M", "Abigail Mignone": "M", "Elizabeth Kelly": "M",
    "Kate Demark": "D", "Alexandra Schneider": "D", "Lara Kology": "D",
    "Corey White": "D", "Maggie Boyd": "D", "Halle Brunner": "D",
    "Abby Curran": "D", "Anna Stieg": "D", "Sarah Keeney": "D",
    "Elyse Finnelle": "GK", "Mel Josephson": "GK", "Serena Reiter": "GK",
}

PLAYER_NUMBERS = {
    "Jayden Piraino": 2, "Kate Demark": 3, "Jenna Dinardo": 4,
    "Kate Galica": 5, "Cady Flaherty": 6, "Payton Shroads": 7,
    "Alexandra Schneider": 8, "Sophia Conti": 9, "Carly Kennedy": 13,
    "Addi Foster": 15, "Madison Alaimo": 16, "Alex Reilly": 23,
    "Mel Josephson": 26, "Elyse Finnelle": 34, "Lara Kology": 36,
    "Fiona Allen": 41, "Livy Laverghetta": 42, "Gabby Laverghetta": 43,
}

PLAYER_YEARS = {
    "Jayden Piraino": "So", "Jenna Dinardo": "Jr", "Kate Galica": "Jr",
    "Kate Demark": "Jr", "Alexandra Schneider": "Jr", "Addi Foster": "Jr",
    "Madison Alaimo": "Jr", "Cady Flaherty": "Fr", "Alex Reilly": "So",
    "Sophia Conti": "So", "Livy Laverghetta": "So", "Carly Kennedy": "So",
    "Gabby Laverghetta": "So", "Fiona Allen": "So", "Lara Kology": "Sr",
    "Elyse Finnelle": "Gr", "Mel Josephson": "Sr", "Corey White": "So",
    "Megan Rocklein": "Fr",
}


def get_position(name):
    return POSITION_MAP.get(name, "?")


def get_number(name):
    return PLAYER_NUMBERS.get(name, "")


def get_year(name):
    return PLAYER_YEARS.get(name, "")


# ==== data loading ====

@st.cache_data(ttl=300)
def list_games():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.xlsx")))
    games = []
    for f in files:
        try:
            info = pd.read_excel(f, sheet_name="Game_Info")
            row = info.iloc[0]
            opp = row.get("away_team", "Opponent")
            res = row.get("result", "")
            hs = int(row.get("home_score", 0))
            aws = int(row.get("away_score", 0))
            date_str = str(row.get("date", ""))
            games.append({
                "file": f,
                "date": date_str,
                "home_team": row.get("home_team", "Virginia"),
                "away_team": opp,
                "home_score": hs,
                "away_score": aws,
                "result": res,
                "location": row.get("location", ""),
                "label": f'{date_str} — {opp}',
            })
        except Exception as e:
            print(f"Error loading {f}: {e}")
    # Sort by date (chronological order) — parse M/D/YYYY for proper ordering
    def _date_sort_key(g):
        try:
            parts = g["date"].split("/")
            return (int(parts[2]), int(parts[0]), int(parts[1]))  # (year, month, day)
        except:
            return (9999, 99, 99)
    games.sort(key=_date_sort_key)
    return games


@st.cache_data(ttl=300)
def load_game(filepath):
    sheets = {}
    xl = pd.ExcelFile(filepath)
    for name in xl.sheet_names:
        sheets[name] = pd.read_excel(filepath, sheet_name=name)
    return sheets


# --- win probability model ---

def time_to_seconds(period, time_str):
    try:
        if pd.isna(time_str) or str(time_str).strip() in ("", "--:--"):
            return None
        parts = str(time_str).split(":")
        minutes = int(parts[0])
        seconds = int(parts[1]) if len(parts) > 1 else 0
        quarter_seconds = minutes * 60 + seconds
        remaining_quarters = 4 - int(period)
        return remaining_quarters * 15 * 60 + quarter_seconds
    except:
        return None


# logistic model - based on the approach from FiveThirtyEight articles
def win_probability(score_diff, seconds_remaining, total_seconds=3600):
    if seconds_remaining is None:
        return 0.5
    time_fraction = max(seconds_remaining / total_seconds, 0.001)
    leverage = score_diff / (np.sqrt(time_fraction) * 2.5 + 0.1)
    wp = 1 / (1 + np.exp(-leverage))
    return np.clip(wp, 0.001, 0.999)


def compute_wp_timeline(scoring_summary, home_team="Virginia"):
    # computes WP at each goal
    if scoring_summary.empty:
        return pd.DataFrame()

    events = []
    home_score, away_score = 0, 0

    events.append({
        "Goal_Num": 0, "Period": 1, "Time": "15:00",
        "Team": "", "Scorer": "Game Start", "Assist": "",
        "Home_Score": 0, "Away_Score": 0, "Score_Diff": 0,
        "Seconds_Remaining": 3600, "WP": 50.0,
        "Type": "", "Is_FPG": False, "Is_ManUp": False,
    })

    for _, row in scoring_summary.iterrows():
        team = str(row.get("Team", ""))
        is_home = home_team.lower() in team.lower()
        if is_home:
            home_score += 1
        else:
            away_score += 1

        score_diff = home_score - away_score
        secs = time_to_seconds(row["Period"], row["Time"])
        wp = win_probability(score_diff, secs)

        events.append({
            "Goal_Num": row.get("Goal_Num", 0),
            "Period": row["Period"], "Time": row["Time"],
            "Team": team, "Scorer": row.get("Scorer", ""),
            "Assist": row.get("Assist", ""),
            "Home_Score": home_score, "Away_Score": away_score,
            "Score_Diff": score_diff, "Seconds_Remaining": secs,
            "WP": round(wp * 100, 1),
            "Type": row.get("Type", ""),
            "Is_FPG": row.get("Is_FPG", False),
            "Is_ManUp": row.get("Is_ManUp", False),
        })

    return pd.DataFrame(events)


def compute_wpa(wp_timeline):
    # calculate WPA per goal
    if wp_timeline.empty or len(wp_timeline) < 2:
        return pd.DataFrame()

    wpa_list = []
    for i in range(1, len(wp_timeline)):
        curr = wp_timeline.iloc[i]
        prev = wp_timeline.iloc[i - 1]
        wpa = curr["WP"] - prev["WP"]
        wpa_list.append({
            "Goal_Num": curr["Goal_Num"],
            "Period": curr["Period"], "Time": curr["Time"],
            "Team": curr["Team"], "Scorer": curr["Scorer"],
            "Assist": curr["Assist"],
            "Score": f'{int(curr["Home_Score"])}-{int(curr["Away_Score"])}',
            "WP_Before": prev["WP"], "WP_After": curr["WP"],
            "WPA": round(wpa, 1),
            "Is_FPG": curr.get("Is_FPG", False),
            "Is_ManUp": curr.get("Is_ManUp", False),
            "Type": curr.get("Type", ""),
        })
    return pd.DataFrame(wpa_list)


# --- scoring runs ---

def detect_scoring_runs(scoring_summary, min_run=2):
    # find streaks of consecutive goals by same team
    if scoring_summary.empty:
        return []
    runs = []
    current_team = None
    current_run = []
    for _, row in scoring_summary.iterrows():
        team = row["Team"]
        if team == current_team:
            current_run.append(row)
        else:
            if len(current_run) >= min_run:
                runs.append({
                    "team": current_team, "length": len(current_run),
                    "start_period": current_run[0]["Period"],
                    "start_time": current_run[0]["Time"],
                    "end_period": current_run[-1]["Period"],
                    "end_time": current_run[-1]["Time"],
                    "scorers": [r["Scorer"] for r in current_run],
                })
            current_team = team
            current_run = [row]
    if len(current_run) >= min_run:
        runs.append({
            "team": current_team, "length": len(current_run),
            "start_period": current_run[0]["Period"],
            "start_time": current_run[0]["Time"],
            "end_period": current_run[-1]["Period"],
            "end_time": current_run[-1]["Time"],
            "scorers": [r["Scorer"] for r in current_run],
        })
    return runs


# ==== play-by-play analysis ====

def classify_pbp_events(pbp_df):
    # categorize PBP events
    if pbp_df.empty:
        return pbp_df
    df = pbp_df.copy()
    df["Play"] = df["Play"].fillna("").astype(str)

    conditions = [
        df["Play"].str.contains(r"\bGOAL\b", case=False, regex=True) & ~df["Play"].str.contains("goalie", case=False),
        df["Play"].str.contains("Shot by", case=False) & ~df["Play"].str.contains(r"\bGOAL\b", case=False, regex=True),
        df["Play"].str.contains("SAVE", case=False) & ~df["Play"].str.contains("goalie", case=False),
        df["Play"].str.contains("Turnover by", case=False),
        df["Play"].str.contains("Draw control", case=False),
        df["Play"].str.contains("Ground ball", case=False),
        df["Play"].str.contains("Clear attempt", case=False),
        df["Play"].str.contains("Clock violation|shot clock", case=False, regex=True),
        df["Play"].str.contains(r"(?:Green|Yellow|Red)\s+card", case=False, regex=True),
        df["Play"].str.contains("Foul on", case=False),
        df["Play"].str.contains("Timeout", case=False),
        (df["Play"].str.contains(r"Free position|free\-position|8.meter", case=False, regex=True)
         & ~df["Play"].str.contains(r"\bGOAL\b|Shot by", case=False, regex=True)),
        df["Play"].str.contains("Draw violation", case=False),
        df["Play"].str.contains("BLOCKED", case=False) & ~df["Play"].str.contains(r"\bGOAL\b", case=False, regex=True),
    ]
    choices = ["Goal", "Shot", "Save", "Turnover", "Draw Control",
               "Ground Ball", "Clear", "Shot Clock Violation", "Card", "Foul",
               "Timeout", "Free Position", "Draw Violation", "Blocked Shot"]

    # For turnovers with "(caused by Player)", we also extract Caused Turnover info
    # but the primary event type stays "Turnover"
    df["Event_Type"] = np.select(conditions, choices, default="Other")

    def extract_team(play):
        # this part is kind of messy but it works
        # Use the beginning of the play (before score lines) for team ID
        # Score lines look like "Virginia 5, Louisville 7"
        # Truncate at "goal number" or first score-like pattern
        trunc = play
        for cutoff in [" goal number", " for season", ". Virginia ", ". virginia "]:
            idx = trunc.lower().find(cutoff)
            if idx > 0:
                trunc = trunc[:idx]
                break
        play_upper = trunc.upper()

        # Check Virginia first (but not Virginia Tech)
        if "VIRGINIA TECH" in play_upper or " VT " in play_upper:
            return "Virginia Tech"
        if "VIRGINIA" in play_upper:
            return "Virginia"
        # Common opponent names/abbreviations in PBP text
        opp_patterns = [
            (r'\bLOU\b|LOUISVILLE', "Louisville"),
            (r'JAMES MA|JMU', "James Madison"),
            (r'\bUMD\b|MARYLAND', "Maryland"),
            (r'CLEMSON', "Clemson"),
            (r'NOTRE DAME', "Notre Dame"),
            (r'NORTH CAROLINA|\bUNC\b', "North Carolina"),
            (r'SYRACUSE', "Syracuse"),
            (r'BOSTON COLLEGE|\bBC\b', "Boston College"),
            (r'STANFORD', "Stanford"),
            (r'PRINCETON', "Princeton"),
            (r'\bNAVY\b', "Navy"),
            (r'RICHMOND', "Richmond"),
            (r'LIBERTY', "Liberty"),
            (r'PITTSBURGH|\bPITT\b', "Pittsburgh"),
            (r'FLORIDA ST|\bFSU\b', "Florida State"),
            (r'JOHNS HOPKINS', "Johns Hopkins"),
            (r'DUKE', "Duke"),
        ]
        for pattern, name in opp_patterns:
            if re.search(pattern, play_upper):
                return name
        return ""

    df["Event_Team"] = df["Play"].apply(extract_team)

    def extract_player(play):
        patterns = [
            r'GOAL by [\w\s]+?\s+([\w\s\'-]+?)(?:\s*\(|,|\s+goal)',
            r'Shot by [\w\s]+?\s+([\w\s\'-]+?)(?:\s*,|\s+WIDE|\s+HIGH|\s+BLOCKED|\s+HIT)',
            r'Turnover by [\w\s]+?\s+([\w\s\'-]+?)(?:\s*\(|\.)',
            r'Draw control by [\w\s]+?\s+([\w\s\'-]+?)(?:\.|$)',
            r'Ground ball pickup by [\w\s]+?\s+([\w\s\'-]+?)(?:\.|$)',
            r'(?:Green|Yellow|Red) card.*?on [\w\s]+?\s+([\w\s\'-]+?)(?:\.|$)',
            r'Foul on [\w\s]+?\s+([\w\s\'-]+?)(?:\.|$)',
            r'SAVE\s+([\w\s\'-]+?)(?:\.|$)',
        ]
        for pat in patterns:
            m = re.search(pat, play)
            if m:
                return m.group(1).strip()
        return ""

    df["Event_Player"] = df["Play"].apply(extract_player)
    return df


def compute_pbp_summary(pbp_classified, home_team="Virginia"):
    # summary stats from PBP
    if pbp_classified.empty:
        return {}
    df = pbp_classified
    summary = {}
    for team_label, team_name in [("home", home_team), ("away", "")]:
        if team_label == "away":
            team_df = df[(df["Event_Team"] != home_team) & (df["Event_Team"] != "")]
        else:
            team_df = df[df["Event_Team"] == home_team]
        actual_name = team_df["Event_Team"].mode().iloc[0] if not team_df.empty else team_name
        summary[team_label] = {
            "team": actual_name,
            "goals": len(team_df[team_df["Event_Type"] == "Goal"]),
            "shots": len(team_df[team_df["Event_Type"].isin(["Shot", "Goal"])]),
            "saves": len(df[df["Event_Type"] == "Save"]),
            "turnovers": len(team_df[team_df["Event_Type"] == "Turnover"]),
            "draw_controls": len(team_df[team_df["Event_Type"] == "Draw Control"]),
            "ground_balls": len(team_df[team_df["Event_Type"] == "Ground Ball"]),
            "cards": len(team_df[team_df["Event_Type"] == "Card"]),
            "fouls": len(team_df[team_df["Event_Type"] == "Foul"]),
        }
    return summary


# --- player analysis ---

def compute_player_efficiency(player_df):
    # compute efficiency metrics
    if player_df.empty:
        return player_df
    df = player_df.copy()
    df["Shot_Pct"] = np.where(df["SH"] > 0, (df["SOG"] / df["SH"] * 100).round(1), 0.0)
    df["Goal_Pct"] = np.where(df["SH"] > 0, (df["G"] / df["SH"] * 100).round(1), 0.0)
    df["TO_Ratio"] = np.where(df["TO"] > 0, (df["CT"] / df["TO"]).round(2),
                               np.where(df["CT"] > 0, 99.0, 0.0))
    df["Involvement"] = df["G"] + df["A"] + df["GB"] + df["DC"] + df["CT"]
    df["Impact"] = (df["G"] * 5 + df["A"] * 3 + df["CT"] * 2 + df["DC"] * 2 + df["GB"] * 1 - df["TO"] * 2).round(1)
    return df


def aggregate_player_stats(game_list, team="uva"):
    # combine player stats from multiple games
    all_players = []
    for game in game_list:
        sheets = load_game(game["file"])
        sheet_name = "UVA_Players" if team == "uva" else "OPP_Players"
        if sheet_name in sheets:
            df = sheets[sheet_name].copy()
            df["Game"] = game["label"]
            df["Date"] = game["date"]
            df["Opponent"] = game["away_team"]
            df["Result"] = game["result"]
            all_players.append(df)
    if not all_players:
        return pd.DataFrame()
    return pd.concat(all_players, ignore_index=True)


def player_season_totals(multi_game_df):
    # aggregate to season totals
    if multi_game_df.empty:
        return pd.DataFrame()
    numeric_cols = ["G", "A", "PTS", "SH", "SOG", "GB", "DC", "TO", "CT"]
    existing_cols = [c for c in numeric_cols if c in multi_game_df.columns]
    totals = multi_game_df.groupby("Player")[existing_cols].sum().reset_index()
    totals["Games"] = multi_game_df.groupby("Player")["Game"].nunique().values
    totals = compute_player_efficiency(totals)
    totals = totals.sort_values("Impact", ascending=False).reset_index(drop=True)
    return totals


# --- radar scores & tier system ---

def compute_radar_scores(season_totals, multi_game_df=None):
    # computes 5-dimension radar scores (offense, defense, possession, efficiency, discipline) and tier
    if season_totals.empty:
        return {}

    df = season_totals.copy()
    results = {}

    # Compute team-level maxes for normalization
    active = df[df["Games"] >= 1]
    if active.empty:
        return {}
    # TODO: would be nice to load these thresholds from a CSV instead of hardcoding

    max_gpg = max(0.001, float((active["G"] / active["Games"].clip(lower=1)).max()))
    max_ppg = max(0.001, float((active["PTS"] / active["Games"].clip(lower=1)).max()))
    max_apg = max(0.001, float((active["A"] / active["Games"].clip(lower=1)).max()))
    max_ctpg = max(0.001, float((active["CT"] / active["Games"].clip(lower=1)).max()))
    max_gbpg = max(0.001, float((active["GB"] / active["Games"].clip(lower=1)).max()))
    max_dcpg = max(0.001, float((active["DC"] / active["Games"].clip(lower=1)).max()))
    max_poss = max(0.001, float((active["GB"] + active["DC"] + active["CT"] - active["TO"]).max()))

    def norm(v, mx, inv=False):
        # simple 0-100 normalization
        if mx == 0:
            return 50
        r = min(v / mx, 1.5) / 1.5 * 100
        return 100 - r if inv else r

    # Per-game data for consistency calculation
    game_data = {}
    if multi_game_df is not None and not multi_game_df.empty:
        for name, group in multi_game_df.groupby("Player"):
            game_data[name] = {
                "game_g": group["G"].tolist(),
                "game_pts": group["PTS"].tolist(),
            }

    for _, row in df.iterrows():
        name = row["Player"]
        pos = get_position(name)
        gp = max(row["Games"], 1)

        gpg = row["G"] / gp
        apg = row["A"] / gp
        ppg = row["PTS"] / gp
        ctpg = row["CT"] / gp
        gbpg = row["GB"] / gp
        dcpg = row["DC"] / gp
        to_rate = row["TO"] / max(row["SH"] + row["TO"] + row["DC"] + row["GB"], 1)
        poss_impact = row["GB"] + row["DC"] + row["CT"] - row["TO"]
        sh_pct = row.get("Shot_Pct", 0) or 0

        # Discipline: cards penalty (estimate from TO patterns)
        # Without explicit card data in season totals, use TO as proxy
        discipline_penalty = 0  # Would add YC*3 + GC*1 if we had card data

        # Consistency from game-by-game data
        consistency = 0.5
        if name in game_data:
            gpts = game_data[name]["game_pts"]
            mean = sum(gpts) / len(gpts) if gpts else 0
            if len(gpts) > 1 and mean > 0:
                std = math.sqrt(sum((x - mean) ** 2 for x in gpts) / len(gpts))
                consistency = 1 - min(std / mean, 1)
            elif mean > 0:
                consistency = 1
            else:
                consistency = 0.5

        # 5 radar dimensions
        offensive = min(100, norm(gpg, max_gpg) * 0.35 + norm(sh_pct, 75) * 0.25 +
                        norm(ppg, max_ppg) * 0.25 + norm(apg, max_apg) * 0.15)
        defensive = min(100, norm(ctpg, max_ctpg) * 0.45 + norm(gbpg, max_gbpg) * 0.35 +
                        norm(discipline_penalty, 10, inv=True) * 0.20)
        possession = min(100, norm(poss_impact, max_poss) * 0.40 + norm(dcpg, max_dcpg) * 0.35 +
                         norm(gbpg, max_gbpg) * 0.25)
        efficiency = min(100, norm(sh_pct, 75) * 0.30 + norm(row.get("Goal_Pct", 0) or 0, 100) * 0.25 +
                         norm(to_rate, 1, inv=True) * 0.25 + norm(consistency, 1) * 0.20)
        discipline = max(0, 100 - discipline_penalty * 12)

        # Position-weighted overall
        weights = {
            "A": {"o": 0.40, "d": 0.05, "p": 0.15, "e": 0.30, "di": 0.10},
            "M": {"o": 0.25, "d": 0.20, "p": 0.25, "e": 0.20, "di": 0.10},
            "D": {"o": 0.05, "d": 0.45, "p": 0.20, "e": 0.10, "di": 0.20},
            "GK": {"o": 0.00, "d": 0.35, "p": 0.15, "e": 0.35, "di": 0.15},
        }.get(pos, {"o": 0.25, "d": 0.25, "p": 0.20, "e": 0.20, "di": 0.10})

        overall = (offensive * weights["o"] + defensive * weights["d"] +
                   possession * weights["p"] + efficiency * weights["e"] +
                   discipline * weights["di"])

        # Tier assignment
        # NOTE: thresholds (65, 45, 25) tuned by looking at D1 averages
        tier = 1 if overall >= 65 else (2 if overall >= 45 else (3 if overall >= 25 else 4))

        # Flags
        flags = []
        if row["TO"] / gp >= 2 and row["PTS"] > 0:
            flags.append(("High Turnover Risk", "negative"))
        if sh_pct >= 50 and row["SH"] >= 5:
            flags.append(("Elite Finisher", "positive"))
        if sh_pct < 30 and row["SH"] >= 10:
            flags.append(("Shot Selection Concern", "warning"))
        if ctpg >= 1.5:
            flags.append(("Defensive Disruptor", "positive"))
        if dcpg >= 3:
            flags.append(("Draw Control Engine", "positive"))
        if gbpg >= 1.5:
            flags.append(("Ground Ball Magnet", "positive"))
        if consistency >= 0.7 and row["PTS"] > 3:
            flags.append(("Reliable Contributor", "info"))
        if consistency < 0.4 and row["PTS"] > 3:
            flags.append(("High Variance", "warning"))
        if apg >= 2:
            flags.append(("Elite Playmaker", "positive"))

        # Coaching recommendations
        recs = generate_recommendations(name, pos, row, gp, sh_pct, ctpg, gbpg, dcpg, to_rate, tier)

        results[name] = {
            "scores": {
                "Offense": round(offensive, 1),
                "Defense": round(defensive, 1),
                "Possession": round(possession, 1),
                "Efficiency": round(efficiency, 1),
                "Discipline": round(discipline, 1),
            },
            "overall": round(overall, 1),
            "tier": tier,
            "flags": flags,
            "recs": recs,
            "impact": row["Impact"],
            "position": pos,
            "number": get_number(name),
            "year": get_year(name),
            "games": gp,
        }

    return results


def generate_recommendations(name, pos, row, gp, sh_pct, ctpg, gbpg, dcpg, to_rate, tier):
    # coaching recommendations based on stats and position
    recs = []
    if pos == "A":
        if sh_pct < 35 and row["SH"] >= 10:
            recs.append(f"🎯 **Shot Selection:** {sh_pct:.0f}% shooting on {int(row['SH'])} shots — focus on higher-percentage zones and reduce contested attempts.")
        if row["TO"] / gp >= 2:
            recs.append(f"🔄 **Ball Security:** Averaging {row['TO']/gp:.1f} TO/game — work on off-hand stick skills and decision-making under pressure. Use small-sided games with turnover penalties to build awareness.")
        if row["A"] / gp >= 2 and row["G"] / gp >= 1.5:
            recs.append(f"⭐ **Maximize Usage:** {name} is a dual-threat creator ({row['G']/gp:.1f} G/gm, {row['A']/gp:.1f} A/gm). She should be the primary option in critical possessions and settled offense.")
        if row["G"] >= 5 and row["A"] < 3:
            recs.append(f"👀 **Expand Playmaking:** Strong finisher ({int(row['G'])}G) but only {int(row['A'])}A — encourage extra pass when doubled.")
    elif pos == "M":
        if dcpg >= 3:
            recs.append(f"🏆 **Protect the Draw:** {name} at {dcpg:.0f} DC/game is an elite asset. Ensure she takes every draw and build secondary draw options to spell her in blowouts.")
        if row["CT"] >= 5 and row["PTS"] >= 5:
            recs.append(f"🔥 **Two-Way Star:** Rare combo of {int(row['CT'])} CTs and {int(row['PTS'])} PTS — maximize her minutes in competitive games.")
        if row["TO"] / gp >= 2:
            recs.append(f"🔄 **Transition Discipline:** High turnovers ({int(row['TO'])}) for a midfielder. Focus on controlled clears and limiting risky passes in the midfield.")
        if sh_pct < 30 and row["SH"] >= 5:
            recs.append(f"🎯 **Shot Quality:** Only {sh_pct:.0f}% shooting — reduce long-range attempts and focus on feeding attackers or driving to higher-percentage areas.")
    elif pos == "D":
        if ctpg >= 1.5:
            recs.append(f"🛡️ **Defensive Anchor:** {ctpg:.1f} CTs/game — assign to opponent's top attacker in big games.")
        if gbpg >= 1.5:
            recs.append(f"💪 **Ground Ball Intensity:** Use on draw circle for first-ground-ball recovery.")
    elif pos == "GK":
        if sh_pct < 40:
            recs.append(f"🧤 **Save Rate Development:** {sh_pct:.1f}% is below D1 average (~45%). Focus on positioning drills, especially on free-position shots. Track save % by shot location to find weaknesses.")
        recs.append(f"✅ **Start in Big Games:** {name}'s experience in wins makes her the clear choice for high-leverage matchups. Build confidence with clear communication from the coaching staff.")

    if not recs:
        if tier == 4:
            recs.append(f"🌱 **Development Plan:** Needs increased practice reps and game minutes. Focus on developing best positional skill.")
        elif tier == 3:
            recs.append(f"📋 **Defined Role:** Can contribute in specific situations. Identify top 1-2 skills and deploy accordingly.")
    return recs


# --- quarter momentum analysis ---

def compute_quarter_momentum(score_qoq, home_team="Virginia"):
    # quarter-by-quarter momentum
    if score_qoq.empty:
        return pd.DataFrame()
    home = score_qoq[score_qoq["Team"].str.contains(home_team, case=False)]
    away = score_qoq[~score_qoq["Team"].str.contains(home_team, case=False)]
    if home.empty or away.empty:
        return pd.DataFrame()
    quarters = []
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        h = int(home.iloc[0][q])
        a = int(away.iloc[0][q])
        diff = h - a
        quarters.append({
            "Quarter": q, "UVA_Goals": h, "OPP_Goals": a, "Diff": diff,
            "Momentum": "UVA" if diff > 0 else ("OPP" if diff < 0 else "Even"),
            "Emoji": "🟢" if diff > 0 else ("🔴" if diff < 0 else "🟡"),
        })
    return pd.DataFrame(quarters)


# --- play type impact analysis ---

def compute_play_type_impact(scoring_summary, wpa_df, penalties_df, home_team="Virginia"):
    # WPA impact by play type
    if wpa_df.empty:
        return pd.DataFrame()
    impacts = []
    team_goals = wpa_df[wpa_df["Team"].str.contains(home_team, case=False)]
    opp_goals = wpa_df[~wpa_df["Team"].str.contains(home_team, case=False)]

    for label, goals, prefix in [("UVA", team_goals, "UVA"), ("OPP", opp_goals, "OPP")]:
        ev = goals[(goals["Is_ManUp"] == False) & (goals["Is_FPG"] == False)]
        fp = goals[goals["Is_FPG"] == True]
        mu = goals[goals["Is_ManUp"] == True]
        if not ev.empty:
            impacts.append({"Category": f"{prefix} Even-Strength Goals", "WPA": round(ev["WPA"].sum(), 1), "Count": len(ev)})
        if not fp.empty:
            impacts.append({"Category": f"{prefix} Free Position Goals", "WPA": round(fp["WPA"].sum(), 1), "Count": len(fp)})
        if not mu.empty:
            impacts.append({"Category": f"{prefix} Man-Up Goals", "WPA": round(mu["WPA"].sum(), 1), "Count": len(mu)})

    return pd.DataFrame(impacts).sort_values("WPA") if impacts else pd.DataFrame()


# --- draw control analytics ---

def compute_draw_control_stats(season_totals, multi_game_df=None):
    # draw control stats
    if season_totals.empty:
        return {}

    dc_players = season_totals[season_totals["DC"] > 0].sort_values("DC", ascending=False)
    total_dc = dc_players["DC"].sum()
    total_games = season_totals["Games"].max() if not season_totals.empty else 1
    primary = dc_players.iloc[0]["Player"] if not dc_players.empty else "N/A"
    primary_dc = dc_players.iloc[0]["DC"] if not dc_players.empty else 0

    stats = {
        "total_dc": int(total_dc),
        "dc_per_game": round(total_dc / max(total_games, 1), 1),
        "primary_specialist": primary,
        "primary_dc": int(primary_dc),
        "primary_pct": round(primary_dc / max(total_dc, 1) * 100, 1),
        "dc_distribution": dc_players[["Player", "DC"]].to_dict("records"),
        "total_goals": int(season_totals["G"].sum()),
        "total_gb": int(season_totals["GB"].sum()),
    }

    # Per-game trend for primary specialist
    if multi_game_df is not None and not multi_game_df.empty:
        primary_games = multi_game_df[multi_game_df["Player"] == primary]
        if not primary_games.empty:
            stats["primary_trend"] = primary_games[["Opponent", "DC", "G"]].to_dict("records")

    return stats


# --- game comparison ---

def compare_games(game_a_sheets, game_b_sheets):
    # compare metrics between two games
    comparisons = []
    for label, sheets in [("Game A", game_a_sheets), ("Game B", game_b_sheets)]:
        info = sheets["Game_Info"].iloc[0]
        stats = sheets.get("Team_Stats_QoQ", pd.DataFrame())
        scoring = sheets.get("Scoring_Summary", pd.DataFrame())
        penalties = sheets.get("Penalty_Summary", pd.DataFrame())
        uva_players = sheets.get("UVA_Players", pd.DataFrame())

        def _safe_int(val, default=0):
            try:
                return int(val)
            except (ValueError, TypeError):
                return default

        def _stat_total(category):
            """Extract UVA total for a stat category, handling string formats like '15-17'."""
            if stats.empty:
                return 0
            uva_row = stats[(stats["Category"] == category)
                            & (stats["Team"].str.contains("Virginia", case=False, na=False))]
            if uva_row.empty:
                return 0
            raw = str(uva_row.iloc[0]["Total"])
            if "-" in raw and category == "Clears":
                try:
                    return int(raw.split("-")[0])  # clears made
                except ValueError:
                    return 0
            return _safe_int(raw)

        row = {
            "Game": label,
            "Opponent": info.get("away_team", ""),
            "Result": f'{"W" if info.get("result")=="W" else "L"} '
                      f'{_safe_int(info.get("home_score", 0))}-{_safe_int(info.get("away_score", 0))}',
            "Date": info.get("date", ""),
            "UVA_Goals": int(uva_players["G"].sum()) if not uva_players.empty and "G" in uva_players.columns else 0,
            "UVA_Assists": int(uva_players["A"].sum()) if not uva_players.empty and "A" in uva_players.columns else 0,
            "UVA_Shots": _stat_total("Shots"),
            "UVA_SOG": int(uva_players["SOG"].sum()) if not uva_players.empty and "SOG" in uva_players.columns else 0,
            "UVA_Draw Controls": _stat_total("Draw Controls"),
            "UVA_Ground Balls": _stat_total("Ground Balls"),
            "UVA_Turnovers": _stat_total("Turnovers"),
            "UVA_Caused TOs": int(uva_players["CT"].sum()) if not uva_players.empty and "CT" in uva_players.columns else 0,
            "UVA_Saves": _stat_total("Saves"),
            "UVA_Clears": _stat_total("Clears"),
            "UVA_Cards": 0,
        }

        if not penalties.empty and "Team" in penalties.columns:
            row["UVA_Cards"] = len(penalties[penalties["Team"].str.contains("Virginia", case=False, na=False)])

        comparisons.append(row)
    return pd.DataFrame(comparisons)


# --- turnover analysis ---

def compute_turnover_analysis(pbp_classified, home_team="Virginia"):
    # turnovers by player and quarter
    if pbp_classified.empty:
        return pd.DataFrame()

    tos = pbp_classified[
        (pbp_classified["Event_Type"] == "Turnover") &
        (pbp_classified["Event_Team"].str.contains(home_team, case=False))
    ].copy()

    if tos.empty:
        return pd.DataFrame()

    # Group by player and quarter
    tos["Quarter"] = "Q" + tos["Period"].astype(str)
    pivot = tos.pivot_table(index="Event_Player", columns="Quarter",
                            values="Play", aggfunc="count", fill_value=0)
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("Total", ascending=False).reset_index()
    pivot = pivot.rename(columns={"Event_Player": "Player"})
    return pivot


# --- full win probability timeline (all play types) ---

# WP momentum deltas by event type (positive = favors the event team)
# TODO: these deltas could be learned from actual game data instead of hardcoded
EVENT_WP_DELTAS = {
    "Goal":               0.0,   # handled by logistic model via score change
    "Draw Control":       1.4,
    "Turnover":          -1.8,   # negative for team committing it
    "Ground Ball":        0.7,
    "Save":               1.2,
    "Shot":               0.4,   # shot attempt = offensive pressure
    "Blocked Shot":       0.8,   # defensive play
    "Clear":              0.5,   # clear good; failed clears get negated
    "Card":              -1.2,   # card ON a team = bad for that team
    "Foul":              -0.6,   # foul ON a team = bad for that team
    "Shot Clock Violation": -1.5,  # loss of possession
    "Draw Violation":    -0.4,   # minor infraction
    "Timeout":            0.0,
    "Free Position":      0.5,
    "Other":              0.0,
}


def synthesize_pbp(scoring_summary, stats_qoq, uva_players, opp_players,
                   home_team="Virginia", away_team="Opponent"):
    # build play-by-play from box score data when full PBP unavailable
    rows = []

    # Parse quarter stats
    q_stats = {}  # {quarter: {category: {team: count}}}
    if stats_qoq is not None and not stats_qoq.empty:
        for q in [1, 2, 3, 4]:
            q_col = f"Q{q}"
            q_stats[q] = {}
            for _, r in stats_qoq.iterrows():
                cat = r.get("Category", "")
                team = str(r.get("Team", ""))
                try:
                    val = int(r.get(q_col, 0))
                except (ValueError, TypeError):
                    val = 0
                if cat not in q_stats[q]:
                    q_stats[q][cat] = {}
                is_home = home_team.lower() in team.lower()
                q_stats[q][cat]["home" if is_home else "away"] = val

    # Build goal events from scoring summary (these have real timestamps)
    goals_by_q = {1: [], 2: [], 3: [], 4: []}
    if scoring_summary is not None and not scoring_summary.empty:
        for _, r in scoring_summary.iterrows():
            period = int(r.get("Period", 1))
            team = str(r.get("Team", ""))
            scorer = r.get("Scorer", "")
            time_str = str(r.get("Time", ""))
            is_home = home_team.lower() in team.lower()
            team_name = home_team if is_home else away_team
            play = f"GOAL by {team_name.upper()} {scorer}."
            if period in goals_by_q:
                goals_by_q[period].append({"Period": period, "Time": time_str, "Play": play})

    # Map stat categories to event play text
    event_map = {
        "Shots": ("Shot by {TEAM} Player.", "Shot"),
        "Saves": ("SAVE by {TEAM} Goalkeeper.", "Save"),
        "Ground Balls": ("Ground ball pickup by {TEAM} Player.", "Ground Ball"),
        "Draw Controls": ("Draw control by {TEAM} Player.", "Draw Control"),
        "Turnovers": ("Turnover by {TEAM} Player.", "Turnover"),
        "Clears": ("Clear attempt by {TEAM} good.", "Clear"),
    }

    for q in [1, 2, 3, 4]:
        events_this_q = []

        # Add goal events
        for ge in goals_by_q.get(q, []):
            events_this_q.append(ge)

        # Add non-goal events from stats
        if q in q_stats:
            for cat, emap in event_map.items():
                template, _ = emap
                if cat in q_stats[q]:
                    for side in ["home", "away"]:
                        count = q_stats[q][cat].get(side, 0)
                        team_name = home_team if side == "home" else away_team
                        # Subtract goals from shots (goals are already counted)
                        if cat == "Shots":
                            n_goals = len([g for g in goals_by_q.get(q, [])
                                          if (home_team.upper() in g["Play"]) == (side == "home")])
                            count = max(0, count - n_goals)
                        for _ in range(count):
                            play = template.replace("{TEAM}", team_name.upper())
                            events_this_q.append({"Period": q, "Time": None, "Play": play})

        # Distribute events within the quarter
        # Goals have real times; other events get spread around them
        n_events = len(events_this_q)
        if n_events > 0:
            q_start_secs = (4 - q) * 900 + 900  # e.g. Q1 = 3600
            q_end_secs = (4 - q) * 900 + 10
            time_slots = np.linspace(q_start_secs, q_end_secs, n_events + 2)[1:-1]

            # Sort: goals with real times first (at their real positions), rest fill gaps
            goals_with_time = [e for e in events_this_q if e["Time"] and e["Time"] != "nan"]
            non_goals = [e for e in events_this_q if not e["Time"] or e["Time"] == "nan"]

            # Place goals at their real time positions
            for ge in goals_with_time:
                try:
                    parts = ge["Time"].split(":")
                    mm, ss = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
                    ge["_secs"] = (4 - q) * 900 + mm * 60 + ss
                except:
                    ge["_secs"] = q_start_secs - 450

            # Sort non-goals randomly and assign remaining time slots
            import random
            random.seed(q)  # deterministic
            random.shuffle(non_goals)

            # Merge: put all events together sorted by time
            all_events = []
            for ge in goals_with_time:
                secs = ge["_secs"]
                mm = secs % 900 // 60
                ss = secs % 60
                all_events.append({"Period": q, "Time": f"{mm:02d}:{ss:02d}", "Play": ge["Play"],
                                   "_secs": secs})

            # Assign times to non-goals in the remaining gaps
            used_secs = set(ge.get("_secs", 0) for ge in goals_with_time)
            available_slots = [s for s in time_slots if s not in used_secs]
            for i, ng in enumerate(non_goals):
                if i < len(available_slots):
                    secs = available_slots[i]
                else:
                    secs = q_start_secs - (i + 1) * (900 / (len(non_goals) + 1))
                mm = int(secs % 900) // 60
                ss = int(secs % 60)
                all_events.append({"Period": q, "Time": f"{mm:02d}:{ss:02d}", "Play": ng["Play"],
                                   "_secs": secs})

            all_events.sort(key=lambda e: -e["_secs"])  # descending (clock counts down)
            for e in all_events:
                rows.append({"Period": e["Period"], "Time": e["Time"], "Play": e["Play"]})

    return pd.DataFrame(rows, columns=["Period", "Time", "Play"])


def compute_full_wp_timeline(pbp_df, scoring_summary, home_team="Virginia"):
    # builds the full WP timeline including non-goal events
    if pbp_df.empty:
        return pd.DataFrame()

    classified = classify_pbp_events(pbp_df.copy())

    # ── 0. Fix period numbering if all events are in Period 1 ─────
    if classified["Period"].nunique() == 1:
        # Detect period boundaries from "End-of-period" markers or time resets
        current_period = 1
        periods = []
        for _, row in classified.iterrows():
            periods.append(current_period)
            play_text = str(row["Play"]).lower()
            if "end-of-period" in play_text or "end-of- period" in play_text or "end of period" in play_text:
                if current_period < 4:
                    current_period += 1
        classified["Period"] = periods
        # If we still only found 1 period, try time-based detection
        if classified["Period"].nunique() == 1:
            times = pd.to_numeric(classified["Time"].astype(str).str.split(":").str[0], errors="coerce")
            resets = (times.diff() > 5) & times.notna()
            current_period = 1
            periods = []
            for reset in resets:
                if reset and current_period < 4:
                    current_period += 1
                periods.append(current_period)
            classified["Period"] = periods

    # ── 1. Build goal lookup: Period+Time → cumulative score ──────
    goal_events = []
    h_score, a_score = 0, 0
    if scoring_summary is not None and not scoring_summary.empty:
        for _, row in scoring_summary.iterrows():
            team = str(row.get("Team", ""))
            is_home = home_team.lower() in team.lower()
            if is_home:
                h_score += 1
            else:
                a_score += 1
            goal_events.append({
                "Period": row["Period"], "Time": str(row["Time"]),
                "Home_Score": h_score, "Away_Score": a_score,
                "Scorer": row.get("Scorer", ""),
                "Assist": row.get("Assist", ""),
                "Is_FPG": row.get("Is_FPG", False),
                "Is_ManUp": row.get("Is_ManUp", False),
            })

    # ── 2. Interpolate missing times ─────────────────────────────
    df = classified.copy()
    df["Time_str"] = df["Time"].astype(str).str.strip()
    df.loc[df["Time_str"].isin(["", "nan", "None", "--:--"]), "Time_str"] = None

    def _clock_to_secs(period, time_str):
        """Convert period + clock to seconds remaining in the game."""
        try:
            parts = str(time_str).split(":")
            mins, secs = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            quarter_secs = mins * 60 + secs
            remaining_qs = 4 - int(period)
            return remaining_qs * 900 + quarter_secs
        except:
            return None

    def _secs_to_clock(secs_remaining):
        """Convert seconds remaining to clock string for the current period."""
        period_secs = secs_remaining % 900
        mm = period_secs // 60
        ss = period_secs % 60
        return f"{mm:02d}:{ss:02d}"

    # Compute seconds remaining where time is known
    df["Secs_Remaining"] = df.apply(
        lambda r: _clock_to_secs(r["Period"], r["Time_str"]) if r["Time_str"] else None,
        axis=1
    )
    # Ensure numeric dtype so interpolation works
    df["Secs_Remaining"] = pd.to_numeric(df["Secs_Remaining"], errors="coerce")

    # Forward/backward fill missing times within each period
    # Events are ordered chronologically, so interpolate linearly
    for period in df["Period"].unique():
        mask = df["Period"] == period
        period_df = df.loc[mask, "Secs_Remaining"].copy()
        n_known = period_df.notna().sum()

        if n_known >= 2:
            # Some timestamps known — interpolate between them
            df.loc[mask, "Secs_Remaining"] = (
                period_df.interpolate(method="linear")
                         .ffill().bfill()
            )
        elif n_known == 1:
            # Only one timestamp known — spread around it
            df.loc[mask, "Secs_Remaining"] = period_df.ffill().bfill()
        else:
            # NO timestamps at all — spread events evenly across the quarter
            # Quarter runs from 15:00 down to 0:01 (in secs_remaining terms)
            p = int(period)
            q_start = (4 - p) * 900 + 900  # top of quarter (e.g. Q1 = 3600)
            q_end = (4 - p) * 900 + 10     # near bottom (small buffer)
            n_events = mask.sum()
            if n_events > 1:
                spread = np.linspace(q_start, q_end, n_events)
            else:
                spread = np.array([q_start - 450])  # midpoint
            df.loc[mask, "Secs_Remaining"] = spread

    # Ensure numeric
    df["Secs_Remaining"] = pd.to_numeric(df["Secs_Remaining"], errors="coerce")

    # Final fallback: if somehow still NaN
    for period in df["Period"].unique():
        mask = (df["Period"] == period) & df["Secs_Remaining"].isna()
        if mask.any():
            mid = (4 - int(period)) * 900 + 450
            df.loc[mask, "Secs_Remaining"] = mid

    df["Secs_Remaining"] = df["Secs_Remaining"].astype(float)

    # ── 3. Build the full timeline ────────────────────────────────
    events = []
    home_score, away_score = 0, 0
    goal_idx = 0
    momentum = 0.0  # running momentum modifier
    DECAY = 0.82    # tuned these by trial and error

    # Game Start event
    events.append({
        "Event_Num": 0,
        "Period": 1, "Time": "15:00",
        "Secs_Remaining": 3600, "Minutes_Elapsed": 0.0,
        "Event_Type": "Game Start", "Event_Team": "",
        "Event_Player": "", "Play": "Game Start",
        "Home_Score": 0, "Away_Score": 0,
        "Score_Diff": 0, "WP": 50.0, "WP_Delta": 0.0,
        "Is_Home_Event": None,
        "Shot_Detail": "", "Clear_Detail": "", "TO_Detail": "",
    })

    for i, row in df.iterrows():
        etype = row["Event_Type"]
        eteam = row["Event_Team"]
        play_text = row["Play"]
        secs = row["Secs_Remaining"]

        if etype == "Other":
            continue  # skip end-of-period, etc.

        # Determine if this event belongs to the home team
        if eteam:
            is_home = home_team.lower() in str(eteam).lower()
        else:
            # If team extraction failed, try to infer from play text
            play_upper = play_text.upper()
            if "VIRGINIA TECH" in play_upper or " VT " in play_upper:
                is_home = False
            elif "VIRGINIA" in play_upper:
                is_home = True
            elif re.search(r'\bLOU\b|PITT|CLEMSON|NAVY|RICHMOND|MARYLAND|LIBERTY|'
                           r'NOTRE DAME|STANFORD|FLORIDA|PRINCETON|SYRACUSE|'
                           r'JAMES MA|JMU|LOUISVILLE|NORTH CAROLINA|UNC\b|'
                           r'BOSTON|DUKE|JOHNS HOPKINS', play_upper):
                is_home = False
            else:
                is_home = None

        # Handle goals: update score from scoring_summary and compute real WPA
        goal_delta = None
        if etype == "Goal" and goal_idx < len(goal_events):
            ge = goal_events[goal_idx]
            # WP before the goal (old score)
            old_diff = home_score - away_score
            wp_before = win_probability(old_diff, secs) * 100
            # Update score
            home_score = ge["Home_Score"]
            away_score = ge["Away_Score"]
            goal_idx += 1
            # WP after the goal (new score)
            new_diff = home_score - away_score
            wp_after = win_probability(new_diff, secs) * 100
            # Goal delta is the actual WP swing from the score change
            goal_delta = wp_after - wp_before
            momentum *= 0.5  # reset some momentum on goals

        score_diff = home_score - away_score

        # Base WP from logistic model
        base_wp = win_probability(score_diff, secs) * 100

        # Compute event delta
        if goal_delta is not None:
            # For goals, use the real WP shift from the score change
            delta = goal_delta
        elif is_home is not None:
            raw_delta = EVENT_WP_DELTAS.get(etype, 0.0)
            if raw_delta == 0:
                delta = 0.0
            else:
                # Adjust delta sign based on team and event semantics
                play_upper = play_text.upper()

                if etype == "Turnover":
                    # Turnover is BAD for the team that committed it
                    delta = raw_delta if is_home else -raw_delta

                elif etype == "Clear":
                    if "FAILED" in play_upper:
                        delta = -abs(raw_delta) * 1.5 if is_home else abs(raw_delta) * 1.5
                    else:
                        delta = abs(raw_delta) if is_home else -abs(raw_delta)

                elif etype == "Card" or etype == "Foul":
                    # Card/foul ON a team is bad for that team
                    delta = raw_delta if is_home else -raw_delta

                elif etype == "Shot":
                    # Shot attempt is slightly positive for the shooting team
                    if "SAVE" in play_upper:
                        delta = -abs(raw_delta) if is_home else abs(raw_delta)
                    else:
                        delta = abs(raw_delta) if is_home else -abs(raw_delta)

                else:
                    # Draw Control, Ground Ball, Save, Free Position = good for event team
                    delta = abs(raw_delta) if is_home else -abs(raw_delta)
        else:
            delta = 0.0

        # Update momentum
        momentum = momentum * DECAY + delta

        # Final WP = base + momentum, clamped
        wp = np.clip(base_wp + momentum, 0.5, 99.5)

        # Extract detail strings for hover
        shot_detail = ""
        if etype == "Shot":
            for tag in ["WIDE", "HIGH", "BLOCKED", "SAVE", "HIT POST"]:
                if tag in play_text.upper():
                    shot_detail = tag.title()
                    break

        clear_detail = ""
        if etype == "Clear":
            clear_detail = "Failed" if "FAILED" in play_text.upper() else "Good"

        to_detail = ""
        if etype == "Turnover":
            m = re.search(r'\(caused by (.+?)\)', play_text)
            to_detail = f"Caused by {m.group(1)}" if m else "Unforced"

        mins_elapsed = (3600 - secs) / 60.0

        events.append({
            "Event_Num": len(events),
            "Period": row["Period"],
            "Time": row["Time_str"] if row["Time_str"] else _secs_to_clock(int(secs)),
            "Secs_Remaining": secs,
            "Minutes_Elapsed": round(mins_elapsed, 2),
            "Event_Type": etype,
            "Event_Team": eteam,
            "Event_Player": row.get("Event_Player", ""),
            "Play": play_text,
            "Home_Score": home_score,
            "Away_Score": away_score,
            "Score_Diff": score_diff,
            "WP": round(wp, 1),
            "WP_Delta": round(delta, 2),
            "Is_Home_Event": is_home,
            "Shot_Detail": shot_detail,
            "Clear_Detail": clear_detail,
            "TO_Detail": to_detail,
        })

    # Game End event
    final_wp = events[-1]["WP"] if events else 50.0
    result_wp = 99.5 if home_score > away_score else (0.5 if home_score < away_score else 50.0)
    events.append({
        "Event_Num": len(events),
        "Period": 4, "Time": "00:00",
        "Secs_Remaining": 0, "Minutes_Elapsed": 60.0,
        "Event_Type": "Final", "Event_Team": "",
        "Event_Player": "", "Play": f"Final: {home_team} {home_score}-{away_score}",
        "Home_Score": home_score, "Away_Score": away_score,
        "Score_Diff": home_score - away_score,
        "WP": result_wp, "WP_Delta": 0.0,
        "Is_Home_Event": None,
        "Shot_Detail": "", "Clear_Detail": "", "TO_Detail": "",
    })

    return pd.DataFrame(events)


# --- game performance grading system ---

def grade_color(grade):
    # hex colors for letter grades
    if grade.startswith("A"):
        return "#2E7D32"  # green
    elif grade.startswith("B"):
        return "#E57200"  # orange
    elif grade.startswith("C"):
        return "#FDDA24"  # yellow
    elif grade.startswith("D"):
        return "#C62828"  # red
    else:
        return "#C62828"  # red for F


def _score_to_grade(score):
    """Convert numeric score (0-100) to letter grade."""
    try:
        s = float(score)
        if s >= 93:
            return "A+"
        elif s >= 90:
            return "A"
        elif s >= 87:
            return "A-"
        elif s >= 83:
            return "B+"
        elif s >= 80:
            return "B"
        elif s >= 77:
            return "B-"
        elif s >= 73:
            return "C+"
        elif s >= 70:
            return "C"
        elif s >= 67:
            return "C-"
        elif s >= 60:
            return "D"
        else:
            return "F"
    except (TypeError, ValueError):
        return "N/A"


def compute_game_grades(sheets, home_team="Virginia"):
    """Compute letter grades for 6 game performance categories.

    Calibrated for D1 women's lacrosse norms:
      - Avg goals/game ≈ 10-12, avg save rate ≈ 40-50%, avg DCs ≈ 10-12
    Uses Game_Info score as primary (more reliable than player stat sums).

    Returns dict like {"Offense": "A-", "Defense": "B", ...}
    """
    grades = {}

    def _safe(val, default=0):
        try:
            v = float(val)
            return v if not np.isnan(v) else default
        except (TypeError, ValueError):
            return default

    info = sheets.get("Game_Info", pd.DataFrame())
    uva_players = sheets.get("UVA_Players", pd.DataFrame())
    opp_players = sheets.get("OPP_Players", pd.DataFrame())

    # Use Game_Info score as authoritative source
    home_goals = _safe(info.iloc[0].get("home_score", 0)) if not info.empty else 0
    away_goals = _safe(info.iloc[0].get("away_score", 0)) if not info.empty else 0

    # ── OFFENSE ───────────────────────────────────────────────
    # 15+ goals = A+, 12-14 = A/A-, 10-11 = B+/B, 8-9 = C+/C, 6-7 = D, <6 = F
    try:
        goals = home_goals
        shots = _safe(uva_players["SH"].sum()) if not uva_players.empty else 0
        sog = _safe(uva_players["SOG"].sum()) if not uva_players.empty else 0

        # Goal volume (60%): piecewise — 5→40, 8→65, 10→78, 12→88, 15→98
        goal_score = min(100, 20 + goals * 5.2)
        # Shot efficiency (20%): SOG/SH typical 50-75%
        eff_score = min(100, (sog / shots * 120)) if shots > 0 else 60
        # Goal conversion (20%): G/SH typical 25-50%
        conv_score = min(100, (goals / shots * 220)) if shots > 0 else 50

        offense_score = goal_score * 0.60 + eff_score * 0.20 + conv_score * 0.20
        grades["Offense"] = _score_to_grade(min(100, offense_score))
    except Exception:
        grades["Offense"] = "N/A"

    # ── DEFENSE ───────────────────────────────────────────────
    # <7 opp goals = A, 8-9 = B, 10-11 = C, 12-13 = D, 14+ = F
    try:
        opp_g = away_goals
        ct = _safe(uva_players["CT"].sum()) if not uva_players.empty else 0
        gb = _safe(uva_players["GB"].sum()) if not uva_players.empty else 0

        # Goals allowed (55%): 6→96, 8→84, 10→72, 12→60, 15→42
        ga_score = max(0, min(100, 132 - opp_g * 6))
        # Caused turnovers (25%): 5→55, 8→75, 10→85, 12→95
        ct_score = min(100, 30 + ct * 6)
        # Ground balls (20%): 8→60, 12→78, 16→96
        gb_score = min(100, 25 + gb * 4.5)

        defense_score = ga_score * 0.55 + ct_score * 0.25 + gb_score * 0.20
        grades["Defense"] = _score_to_grade(min(100, defense_score))
    except Exception:
        grades["Defense"] = "N/A"

    # ── TRANSITION (turnovers + margin) ───────────────────────
    try:
        uva_tos = _safe(uva_players["TO"].sum()) if not uva_players.empty else 12
        opp_tos = _safe(opp_players["TO"].sum()) if not opp_players.empty else 12

        # Lower UVA turnovers = better: 6→96, 10→78, 14→60, 18→42
        to_score = max(0, min(100, 123 - uva_tos * 4.5))
        # TO differential: winning battle is bonus
        to_diff = opp_tos - uva_tos  # positive = good
        diff_bonus = min(15, max(-15, to_diff * 3))

        transition_score = min(100, max(0, to_score + diff_bonus))
        grades["Transition"] = _score_to_grade(transition_score)
    except Exception:
        grades["Transition"] = "N/A"

    # ── DRAW UNIT ─────────────────────────────────────────────
    # 18+ = A+, 14-17 = A/A-, 10-13 = B, 7-9 = C, <7 = D/F
    try:
        dc = _safe(uva_players["DC"].sum()) if not uva_players.empty else 0
        # Piecewise: 5→50, 8→66, 10→77, 13→93, 15→100
        draw_score = min(100, 25 + dc * 5.3)
        grades["Draw Unit"] = _score_to_grade(draw_score)
    except Exception:
        grades["Draw Unit"] = "N/A"

    # ── GOALKEEPING ───────────────────────────────────────────
    # Save% in WLAX: 55%+ elite, 45-50% good, 35-45% avg, <35% poor
    try:
        gk = sheets.get("Goalkeepers", pd.DataFrame())
        if not gk.empty and "Saves" in gk.columns and "GA" in gk.columns:
            saves = _safe(gk["Saves"].sum())
            ga = _safe(gk["GA"].sum())
            total = saves + ga
            if total > 0:
                save_pct = saves / total  # 0.30-0.55 typical
                # Scale so: 55%→95, 45%→78, 35%→60, 25%→42
                gk_score = max(0, min(100, save_pct * 175 - 1.5))
                grades["Goalkeeping"] = _score_to_grade(gk_score)
            else:
                grades["Goalkeeping"] = "N/A"
        else:
            grades["Goalkeeping"] = "N/A"
    except Exception:
        grades["Goalkeeping"] = "N/A"

    # ── DISCIPLINE ────────────────────────────────────────────
    try:
        pens = sheets.get("Penalty_Summary", pd.DataFrame())
        if pens is not None and not pens.empty and "Team" in pens.columns:
            uva_pens = int(pens["Team"].str.contains(home_team, case=False, na=False).sum())
            # 0=A+, 1=A-, 2=B+, 3=B-, 4=C, 5=D, 6+=F
            discipline_score = max(0, 97 - uva_pens * 14)
            grades["Discipline"] = _score_to_grade(discipline_score)
        else:
            grades["Discipline"] = _score_to_grade(97)  # no penalties = A+
    except Exception:
        grades["Discipline"] = "N/A"

    return grades
