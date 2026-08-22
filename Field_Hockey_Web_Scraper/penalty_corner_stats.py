"""
penalty_corner_stats.py
-----------------------
Parses scraped field hockey play-by-play strings and computes penalty corner
statistics for a scouted team and their opponents.

Expected play string formats (case-insensitive):
    "57:00 penalty corner by american sarah steinman [57:00]."
    "48:09 shot by american alyssa freeman, save (by goalie) emma clements."
    "8:30 GOAL by VCU Lina Behrmann (FIRST GOAL)"

All plays must be in a list called `plays`, sorted chronologically.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Play:
    """Represents a single parsed play from the play-by-play log."""
    raw: str                        # Original scraped string
    time_seconds: int               # Play time converted to total seconds
    play_type: str                  # "penalty_corner" | "shot" | "goal" | "unknown"
    team: str                       # Team name as it appears in the string (lowercased)
    player: str                     # Player name extracted from the string


@dataclass
class PlayerStats:
    """Shot and goal totals for a single player on penalty corners."""
    shots: int = 0
    goals: int = 0


@dataclass
class TeamPCStats:
    """
    Penalty corner statistics for one side (scouted team OR their opponents).

    Offensive stats  – corners won, shots taken, goals scored from corners.
    Defensive stats  – corners conceded, shots faced, goals conceded from corners.

    recorners_taken / recorners_conceded count how many times a corner
    sequence was extended by a re-corner (i.e. each extra corner after the
    first in a sequence).
    """
    # --- Offensive (this team attacking) ---
    corners_taken: int = 0
    recorners_taken: int = 0
    shots_from_corners: int = 0
    goals_from_corners: int = 0
    player_stats: dict[str, PlayerStats] = field(default_factory=dict)

    # --- Defensive (this team defending) ---
    corners_conceded: int = 0
    recorners_conceded: int = 0
    shots_conceded_from_corners: int = 0
    goals_conceded_from_corners: int = 0


# ---------------------------------------------------------------------------
# Timing helpers
# ---------------------------------------------------------------------------

def parse_time(time_str: str) -> int:
    """
    Convert a "MM:SS" or "M:SS" timestamp string to total seconds (int).

    The scraped time may be any width (e.g. "8:30" or "57:00"), so we split
    on ":" rather than using fixed character positions.

    Args:
        time_str: A string like "8:30" or "57:00".

    Returns:
        Total seconds as an integer.

    Raises:
        ValueError: If the string cannot be parsed as MM:SS.
    """
    parts = time_str.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Unexpected time format: '{time_str}'")
    minutes, seconds = int(parts[0]), int(parts[1])
    return minutes * 60 + seconds


def extract_time_from_play(raw: str) -> tuple[int, str]:
    """
    Pull the leading timestamp out of a raw play string.

    The timestamp is always the first token and matches M:SS or MM:SS.
    Returns both the numeric value (seconds) and the original token so the
    caller can strip it from the remainder of the string.

    The pattern r"^(\\d{1,3}:\\d{2})" means:
        ^          → start of the string
        \\d{1,3}   → 1 to 3 digit number (minutes: 0-999)
        :          → a literal colon
        \\d{2}     → exactly 2 digits (seconds: 00-59)


    Args:
        raw: Full raw play string, e.g. "57:00 penalty corner by ...".

    Returns:
        (time_seconds, time_token)  e.g. (3420, "57:00")

    Raises:
        ValueError: If no valid timestamp is found at the start.
    """
    # Match an optional leading timestamp like "57:00" or "8:30"
    match = re.match(r"^(\d{1,3}:\d{2})", raw.strip())
    if not match:
        raise ValueError(f"No timestamp found at start of play: '{raw}'")
    token = match.group(1)
    return parse_time(token), token

def time_diff(earlier_seconds: int, later_seconds: int) -> int:
    """
    Compute how many seconds apart two play times are.
 
    We always subtract the earlier from the later so the result is positive.
    Both times are already in seconds (converted by parse_time), so this is
    just simple subtraction.
 
    Args:
        earlier_seconds: The earlier play's time in total seconds.
        later_seconds:   The later play's time in total seconds.
 
    Returns:
        Non-negative integer number of seconds between the two plays.
    """
    return later_seconds - earlier_seconds



# ---------------------------------------------------------------------------
# Play parsing
# ---------------------------------------------------------------------------

def classify_play(raw: str) -> str:
    """
    Determine the play type from the raw string content.

    Detection order matters – "penalty corner" must be checked before a
    generic "corner kick" if your scraper mixes both sports; here we check
    penalty corner first.

    Args:
        raw: Raw play string (any case).

    Returns:
        One of: "penalty_corner", "shot", "goal", "unknown".
    """
    lowered = raw.lower()
    if "penalty corner by" in lowered:
        return "penalty_corner"
    if "goal by" in lowered:
        return "goal"
    if "shot by" in lowered:
        return "shot"
    if "corner kick by" in lowered:
        
        return "penalty_corner"   # treat corner kicks the same way
    return "unknown"


def extract_team_and_player(raw: str, time_token: str) -> tuple[str, str]:
    """
    Extract the team name and player name from the body of a play string.

    Strategy:
        1. Strip the leading timestamp and any bracketed duplicate timestamp
           (e.g. "[57:00]") as well as trailing punctuation.
        2. Find the keyword phrase ("penalty corner by", "shot by", "goal by")
           and take everything after "by " as "<TEAM> <PLAYER ...>".
        3. The *first word* after "by" is treated as the team name; the rest
           of the words (up to a comma or parenthesis) are the player name.
        
        4. Search for the word "by" followed by the team name and player name.
           The pattern expects: "by TEAMNAME FIRSTNAME LASTNAME"
           Everything before a comma or opening parenthesis is the player name.
 

    This is intentionally lenient – team names in scraped data often vary in
    casing and abbreviation.

    Args:
        raw:        Original play string.
        time_token: The timestamp token to strip (e.g. "57:00").

    Returns:
        (team_lowercase, player_fullname)
    """
    # Remove leading timestamp
    body = raw.strip()
    body = body[len(time_token):].strip()

    # Remove any bracketed duplicate timestamp like [57:00]
    body = re.sub(r"\[\d{1,3}:\d{2}\]", "", body).strip()

    # Normalise whitespace
    body = re.sub(r"\s+", " ", body)

    # Find "by <TEAM> <PLAYER>" pattern (case-insensitive)
    by_match = re.search(r"\bby\s+(\S+)\s+(.+?)(?:[,.(]|$)", body, re.IGNORECASE)
    if not by_match:
        # Fallback: return empty strings; caller can handle gracefully
        return "", ""

    team = by_match.group(1).lower()
    # Player name: strip trailing punctuation/spaces
    player = by_match.group(2).strip().rstrip(".,;:()")
    def extract_player(player):
        match player:
            case _ if("blocked" in player):
                index=player.find("blocked")
                player=player[0:index-1]
                return player
            case _ if("wide" in player):
                index=player.find("wide")
                player=player[0:index-1]
                return player
            case _ if("defensive" in player):
                index=player.find("defensive")
                player=player[0:index-1]
                return player
            case _ if ("high" in player):
                index=player.find("high")
                player=player[0:index-1]
                return player
            case _:
                return player
            
    player_name=extract_player(player)

    
        
    return team, player_name


def parse_play(raw: str) -> Optional[Play]:
    """
    Parse a single raw play string into a Play dataclass.

    Returns None if the string cannot be parsed (e.g. empty or malformed).

    Args:
        raw: Raw scraped play string.

    Returns:
        Populated Play instance, or None on failure.
    """
    raw = raw.strip()
    if not raw:
        return None

    try:
        time_seconds, time_token = extract_time_from_play(raw)
    except ValueError:
        # Can't determine timing – skip this play
        print(f"this is a wrong play type {raw}")
        
        
        return None

    play_type = classify_play(raw)
    team, player = extract_team_and_player(raw, time_token)

    return Play(
        raw=raw,
        time_seconds=time_seconds,
        play_type=play_type,
        team=team,
        player=player,
    )


def parse_all_plays(plays: list[str]) -> list[Play]:
    """
    Parse every string in the scraped plays list.

    Unknown/unparseable plays are silently dropped.

    Args:
        plays: List of raw play strings, sorted chronologically.

    Returns:
        List of Play objects in chronological order.
    """
    parsed = []
    
    for raw in plays:

        play = parse_play(raw)
        
        
        if play is not None and play.play_type != "unknown":
            parsed.append(play)
    return parsed


# ---------------------------------------------------------------------------
# Team identification
# ---------------------------------------------------------------------------

def normalize_team_name(name: str) -> str:
    """
    Lowercase and strip a team name for comparison.

    Args:
        name: Raw team name string.

    Returns:
        Normalised string.
    """
    return name.strip().lower()


def belongs_to_scouted_team(play: Play, scouted_team: str) -> bool:
    """
    Decide whether a play belongs to the scouted team.

    Matching is flexible: the scouted team identifier can be a full name
    (e.g. "american") or an acronym / abbreviation (e.g. "vcu").  We check
    whether the scraped team token *starts with* or *contains* the identifier,
    so "american" matches "american" and "vcu" matches "vcu".

    Args:
        play:         Parsed Play object.
        scouted_team: Name or acronym entered by the user (any case).

    Returns:
        True if the play is attributed to the scouted team.
    """
    norm_scraped = normalize_team_name(play.team)
    norm_scouted = normalize_team_name(scouted_team)
    
    
    return norm_scouted in norm_scraped or norm_scraped.startswith(norm_scouted) or norm_scraped in norm_scouted


# ---------------------------------------------------------------------------
# Penalty corner linking
# ---------------------------------------------------------------------------

PC_WINDOW_SECONDS = 12  # A shot/goal within this window counts as a PC result

def within_pc_window(earlier_time: int, later_time: int) -> bool:
    """
    Return True if later_time falls within PC_WINDOW_SECONDS of earlier_time.
 
    This is used both to detect PC results (shot/goal) AND re-corners.
    Any play within 12 seconds of the most recent corner in a sequence is
    part of that penalty corner sequence.
 
    Args:
        earlier_time: Time of the penalty corner (seconds).
        later_time:   Time of the next play to test (seconds).
 
    Returns:
        True if the gap is 0–12 seconds inclusive.
    """
    diff = time_diff(earlier_time, later_time)
    return 0 <= diff <= PC_WINDOW_SECONDS
 

def is_pc_result(corner: Play, next_play: Play) -> bool:
    """
    Determine whether a shot or goal directly results from a penalty corner.

    Rules:
        - next_play must be a "shot" or "goal".
        - next_play must occur within PC_WINDOW_SECONDS after the corner.
        - The corner must come *before* (or exactly at) the next play's time
          (the plays list is chronological, so this is always true in practice).

    Args:
        corner:    A penalty_corner Play.
        next_play: The candidate shot/goal Play immediately following the corner.

    Returns:
        True if next_play counts as a result of this penalty corner.
    """
    if next_play.play_type not in ("shot", "goal"):
        return False
    time_diff = next_play.time_seconds - corner.time_seconds
    return 0 <= time_diff <= PC_WINDOW_SECONDS


# ---------------------------------------------------------------------------
# Main stats computation
# ---------------------------------------------------------------------------

def compute_penalty_corner_stats(
    plays: list,
    scouted_team: str,
) -> tuple:
    """
    Compute penalty corner statistics for the scouted team and their opponents.
 
    HOW THE LOOP WORKS
    ──────────────────
    We walk through the plays list one by one using an index `i`.
    When we land on a penalty_corner, we enter a "PC sequence" and keep
    looking ahead (i + 1, i + 2, …) until we either:
        (a) find a shot or goal within 12 seconds → record it, end sequence
        (b) find a re-corner within 12 seconds    → update the "last corner
            time" and keep looking (the sequence continues)
        (c) find a play outside 12 seconds or end of list → end sequence
 
    This means a re-corner resets the 12-second clock. A shot after the
    re-corner (within 12 seconds of the re-corner) still counts.
 
    TEAM ATTRIBUTION FIX
    ─────────────────────
    We decide which team is attacking based on the CORNER play's team, NOT the
    shot play's team. This prevents the bug where a goal was mistakenly credited
    to the wrong team because the shot string was mis-matched.
 
    Args:
        plays:        Raw scraped play strings (chronological order).
        scouted_team: Team name / acronym entered by the user.
 
    Returns:
        (scouted_stats, opponent_stats) — both are TeamPCStats objects.
    """
    parsed = parse_all_plays(plays)
    scouted_stats = TeamPCStats()
    opponent_stats = TeamPCStats()
 
    i = 0
    last_corner_time=0
    while i < len(parsed):
        play = parsed[i]
        
 
        # Only start processing when we hit a penalty corner
        if play.play_type != "penalty_corner":
            i += 1
            continue
 
        # ── We found the start of a penalty corner sequence ──────────────────
 
        # Figure out which team took this corner (attacker vs defender)
        corner_is_scouted = belongs_to_scouted_team(play, scouted_team)
        
        # Credit the first corner of this sequence
        if corner_is_scouted:
            scouted_stats.corners_taken += 1
            opponent_stats.corners_conceded += 1
            if (within_pc_window(last_corner_time, play.time_seconds)):
                scouted_stats.recorners_taken += 1
                opponent_stats.recorners_conceded += 1

            
        else:
            opponent_stats.corners_taken += 1
            scouted_stats.corners_conceded += 1
            if (within_pc_window(last_corner_time, play.time_seconds)):
                opponent_stats.recorners_taken += 1
                scouted_stats.recorners_conceded += 1
        

 
        # Remember the time of the most recent corner in this sequence.
        # If a re-corner happens, we update this to the re-corner's time.
        last_corner_time = play.time_seconds
        
       
        # Look ahead through the next plays while still inside the sequence
        j = i + 1
        sequence_active = True

        while sequence_active and j < len(parsed):
            next_play = parsed[j]
 
            if not within_pc_window(last_corner_time, next_play.time_seconds):
                # This play is too far away — the PC sequence is over
                sequence_active = False
 
                j += 1  # keep looking forward
 
            elif next_play.play_type in ("shot", "goal"):
                # ── SHOT or GOAL from a PC ────────────────────────────────────
                # Use the corner's team (corner_is_scouted) for team attribution,
                # but the shot play for the player name.
                player_name = next_play.player
 
                if corner_is_scouted:
                    scouted_stats.shots_from_corners += 1
                    opponent_stats.shots_conceded_from_corners += 1
                    _update_player_shots(scouted_stats, player_name)
 
                    if next_play.play_type == "goal":
                        scouted_stats.goals_from_corners += 1
                        opponent_stats.goals_conceded_from_corners += 1
                        _update_player_goals(scouted_stats, player_name)
                else:
                    opponent_stats.shots_from_corners += 1
                    scouted_stats.shots_conceded_from_corners += 1
                    _update_player_shots(opponent_stats, player_name)
 
                    if next_play.play_type == "goal":
                        opponent_stats.goals_from_corners += 1
                        scouted_stats.goals_conceded_from_corners += 1
                        _update_player_goals(opponent_stats, player_name)
 
                # After a shot/goal the sequence ends regardless
                j += 1
                sequence_active = False
 
            else:
                # Unknown play type within the window — skip it and keep looking
                j += 1
 
        # Jump the main loop past everything we already processed
        i = j
 
    return scouted_stats, opponent_stats


# ---------------------------------------------------------------------------
# Private helpers for player tracking
# ---------------------------------------------------------------------------

def _update_player_shots(stats: TeamPCStats, player: str) -> None:
    """Increment the shot count for `player` inside `stats`."""
    if player not in stats.player_stats:
        stats.player_stats[player] = PlayerStats()
    stats.player_stats[player].shots += 1


def _update_player_goals(stats: TeamPCStats, player: str) -> None:
    """
    Add one goal to a player's tally inside the given TeamPCStats.
 
    Args:
        stats:  The TeamPCStats object to update.
        player: Player's full name string.
    """

    if player not in stats.player_stats:
        stats.player_stats[player] = PlayerStats()
    stats.player_stats[player].goals += 1


#---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
 
# ...existing code...
def print_stats_report(
    scouted_team: str,
    scouted_stats: TeamPCStats,
    opponent_stats: TeamPCStats,
    corners_taken: int,
    corners_conceded: int
) -> None:
    """
    Write a human-readable penalty corner scouting report to a text file in
    the user's "Scout_Documents" folder. The filename is:
        {scouted_team} scout report.txt
    """
    sep = "-" * 55

    lines: list[str] = []
    lines.append(sep)
    lines.append(f"  PENALTY CORNER SCOUTING REPORT — {scouted_team.upper()}")
    lines.append(sep)

    lines.append("") 
    lines.append("[OFFENSIVE — corners taken by scouted team]")
    lines.append(f"  Corners taken          : {corners_taken}")
    lines.append(f"  Re-corners taken       : {scouted_stats.recorners_taken}")
    lines.append(f"  Shots from corners     : {scouted_stats.shots_from_corners}")
    lines.append(f"  Goals from corners     : {scouted_stats.goals_from_corners}")
    if corners_taken > 0:
        shot_pct = scouted_stats.shots_from_corners / corners_taken * 100
        goal_pct = scouted_stats.goals_from_corners / corners_taken * 100
        lines.append(f"  Shot conversion        : {shot_pct:.1f}%")
        lines.append(f"  Goal conversion        : {goal_pct:.1f}%")
    else: 
        shot_pct=0
        goal_pct=0
        lines.append(f"  Shot conversion        : {shot_pct:.1f}%")
        lines.append(f"  Goal conversion        : {goal_pct:.1f}%")

    if scouted_stats.player_stats:
        lines.append("")
        lines.append("  Player breakdown (offensive):")
        for name, ps in sorted(scouted_stats.player_stats.items()):
            lines.append(f"    {name:<28} shots: {ps.shots}  goals: {ps.goals}")

    lines.append("")
    lines.append("[DEFENSIVE — corners conceded by scouted team]")
    lines.append(f"  Corners conceded             : {corners_conceded}")
    lines.append(f"  Re-corners conceded          : {scouted_stats.recorners_conceded}")
    lines.append(f"  Opponent shots from corners  : {scouted_stats.shots_conceded_from_corners}")
    lines.append(f"  Opponent goals from corners  : {scouted_stats.goals_conceded_from_corners}")
    if corners_conceded > 0:
        shot_pct = scouted_stats.shots_conceded_from_corners / corners_conceded * 100
        goal_pct = scouted_stats.goals_conceded_from_corners / corners_conceded * 100
        lines.append(f"  Opp. shot conversion         : {shot_pct:.1f}%")
        lines.append(f"  Opp. goal conversion         : {goal_pct:.1f}%")

    lines.append(sep)

    print("making the file...")

    # Build and sanitize filename, ensure folder exists, then write file
    safe_team = re.sub(r'[<>:"/\\|?*]', "_", scouted_team).strip() or "scouted_team"
    filename = f"{safe_team} scout report.txt"
    

    report_text = "\n".join(lines)

    with open(filename, "w", encoding="utf-8") as fh:
        fh.write(report_text)

    print(f"saved report to '{filename}'")

    return report_text
