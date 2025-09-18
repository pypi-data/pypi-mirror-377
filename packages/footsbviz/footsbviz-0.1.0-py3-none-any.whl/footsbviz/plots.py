# footsbviz/plots.py
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Arc

# Optional dependency for pretty highlighted titles
try:
    from highlight_text import htext
    _HAS_HIGHLIGHT = True
except Exception:
    _HAS_HIGHLIGHT = False


# ---------- small helpers ----------

def _save_and_show(fig, save_path: str | None, dpi: int, show: bool) -> None:
    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=dpi)
    if show:
        plt.show()


# ---------- pitch ----------

def draw_pitch(
    x_min: float = 0, x_max: float = 106, y_min: float = 0, y_max: float = 68,
    pitch_color: str = "w", line_color: str = "grey", line_thickness: float = 1.5, point_size: float = 20,
    orientation: str = "horizontal", aspect: str = "full", ax=None
):
    """
    Draw a football pitch on an existing Matplotlib Axes.

    Parameters
    ----------
    orientation : {"horizontal","vertical"}
    aspect      : {"full","half"}
    ax          : matplotlib.axes.Axes (required)
    """
    if ax is None:
        raise TypeError("Provide an existing Matplotlib Axes via ax=...")

    if orientation.lower().startswith("h"):
        first = 0; second = 1; arc_angle = 0
        if aspect == "half":
            ax.set_xlim(x_max / 2, x_max + 5)
    elif orientation.lower().startswith("v"):
        first = 1; second = 0; arc_angle = 90
        if aspect == "half":
            ax.set_ylim(x_max / 2, x_max + 5)
    else:
        raise NameError("orientation must be 'horizontal' or 'vertical'")

    ax.axis("off")

    # background
    rect = plt.Rectangle((x_min, y_min), x_max, y_max, facecolor=pitch_color, edgecolor="none", zorder=-2)
    ax.add_artist(rect)

    # coordinates
    x_conversion = x_max / 100
    y_conversion = y_max / 100
    pitch_x = [x * x_conversion for x in [0, 5.8, 11.5, 17, 50, 83, 88.5, 94.2, 100]]
    pitch_y = [x * y_conversion for x in [0, 21.1, 36.6, 50, 63.2, 78.9, 100]]
    goal_y  = [x * y_conversion for x in [45.2, 54.8]]

    # lines
    lx1 = [x_min, x_max, x_max, x_min, x_min]; ly1 = [y_min, y_min, y_max, y_max, y_min]              # border
    lx2 = [x_max, pitch_x[5], pitch_x[5], x_max]; ly2 = [pitch_y[1], pitch_y[1], pitch_y[5], pitch_y[5]]  # right 6-yard
    lx3 = [0, pitch_x[3], pitch_x[3], 0]; ly3 = [pitch_y[1], pitch_y[1], pitch_y[5], pitch_y[5]]         # left 6-yard
    lx4 = [x_max, x_max+2, x_max+2, x_max]; ly4 = [goal_y[0], goal_y[0], goal_y[1], goal_y[1]]           # right goal
    lx5 = [0, -2, -2, 0]; ly5 = [goal_y[0], goal_y[0], goal_y[1], goal_y[1]]                             # left goal
    lx6 = [x_max, pitch_x[7], pitch_x[7], x_max]; ly6 = [pitch_y[2], pitch_y[2], pitch_y[4], pitch_y[4]] # right box
    lx7 = [0, pitch_x[1], pitch_x[1], 0]; ly7 = [pitch_y[2], pitch_y[2], pitch_y[4], pitch_y[4]]         # left box
    lx8 = [pitch_x[4], pitch_x[4]]; ly8 = [0, y_max]                                                     # halfway

    lines = [[lx1, ly1],[lx2, ly2],[lx3, ly3],[lx4, ly4],[lx5, ly5],[lx6, ly6],[lx7, ly7],[lx8, ly8]]
    points = [[pitch_x[6], pitch_y[3]],[pitch_x[2], pitch_y[3]],[pitch_x[4], pitch_y[3]]]
    circle_points = [pitch_x[4], pitch_y[3]]
    arc_points1   = [pitch_x[6], pitch_y[3]]
    arc_points2   = [pitch_x[2], pitch_y[3]]

    for line in lines:
        ax.plot(line[first], line[second], color=line_color, lw=line_thickness, zorder=-1)
    for point in points:
        ax.scatter(point[first], point[second], color=line_color, s=point_size, zorder=-1)

    # centre circle and arcs
    circle = plt.Circle((circle_points[first], circle_points[second]), x_max * 0.088, lw=line_thickness,
                        color=line_color, fill=False, zorder=-1)
    ax.add_artist(circle)
    arc1 = Arc((arc_points1[first], arc_points1[second]), height=x_max * 0.088 * 2, width=x_max * 0.088 * 2,
               angle=arc_angle, theta1=128.75, theta2=231.25, color=line_color, lw=line_thickness, zorder=-1)
    ax.add_artist(arc1)
    arc2 = Arc((arc_points2[first], arc_points2[second]), height=x_max * 0.088 * 2, width=x_max * 0.088 * 2,
               angle=arc_angle, theta1=308.75, theta2=51.25, color=line_color, lw=line_thickness, zorder=-1)
    ax.add_artist(arc2)

    ax.set_aspect("equal")
    return ax


# ---------- plots: team shot map ----------

def create_shot_map_team(
    df: pd.DataFrame,
    team_name: str,
    team_colour: str,
    pitch_length_x: int,
    pitch_length_y: int,
    orientation: str,
    aspect: str,
    x_dimensions: int,
    y_dimensions: int,
    subtitle: str | None = None,
    save_path: str | None = None,
    dpi: int = 300,
    show: bool = True,
):
    """
    Team shot map (penalties excluded). Returns (fig, ax).

    Expected columns (StatsBomb-style):
    - 'type_name', 'shot_outcome_name', 'shot_statsbomb_xg'
    - 'location_x', 'location_y'
    - 'team_name'
    """
    df = df[df.get("shot_type_name", "Shot") != "Penalty"]
    df_shots = df[(df["type_name"] == "Shot") & (df["shot_outcome_name"] != "Goal") & (df["team_name"] == team_name)]
    df_goals = df[(df["type_name"] == "Shot") & (df["shot_outcome_name"] == "Goal") & (df["team_name"] == team_name)]
    df_shots_and_goals = df[(df["type_name"] == "Shot") & (df["team_name"] == team_name)]

    total_shots = int(len(df_shots))
    total_goals = int(len(df_goals))
    total_xg = float(df_shots_and_goals["shot_statsbomb_xg"].sum().round(2))

    y_shots = df_shots["location_x"].tolist()
    x_shots = df_shots["location_y"].tolist()
    y_goals = df_goals["location_x"].tolist()
    x_goals = df_goals["location_y"].tolist()

    # style
    background = "#F7F7F7"; text_colour = "black"
    mpl.rcParams.update(mpl.rcParamsDefault)
    mpl.rcParams["xtick.color"] = text_colour
    mpl.rcParams["ytick.color"] = text_colour

    fig, ax = plt.subplots(figsize=(x_dimensions, y_dimensions))
    fig.set_facecolor(background); ax.patch.set_facecolor(background)

    draw_pitch(0, pitch_length_x, 0, pitch_length_y, orientation=orientation, aspect=aspect,
               pitch_color=background, line_color="#3B3B3B", ax=ax)

    # markers sized by xG
    z1 = [1000 * float(i) for i in df_shots["shot_statsbomb_xg"].tolist()]
    z2 = [1000 * float(i) for i in df_goals["shot_statsbomb_xg"].tolist()]
    zo = 12

    # legend row for xG
    mSize = [0.05, 0.10, 0.2, 0.4, 0.6, 1.0]
    mSizeS = [1000 * i for i in mSize]
    mx = [1.5, 3.0, 5.0, 7.5, 10.625, 14.25]
    my = [pitch_length_x - 5] * 6  # place near top
    ax.text((mx[0]+mx[-1])/2, pitch_length_x - 9, "xG", color="#3B3B3B", ha="center", va="center",
            zorder=zo, fontsize=12)

    ax.scatter(x_shots, y_shots, marker="o", color="red", edgecolors="black", s=z1, alpha=0.7, zorder=zo, label="Shots")
    ax.scatter(x_goals, y_goals, marker="*", color="green", edgecolors="black", s=z2, alpha=0.7, zorder=zo, label="Goals")

    ax.scatter(mx, my, s=mSizeS, facecolors="#3B3B3B", edgecolor="#3B3B3B", zorder=zo)
    for i in range(len(mx)):
        ax.text(mx[i], my[i], mSize[i], fontsize=8, color="white", zorder=zo, ha="center", va="center")

    # title
    title_str = f"{team_name} — {total_shots} shots, {total_goals} goals ({total_xg:.2f} xG)"
    if _HAS_HIGHLIGHT:
        htext.fig_htext(title_str.replace(team_name, f"<{team_name}>"),
                        0.10, 0.98, highlight_colors=[team_colour],
                        highlight_weights=["bold"], string_weight="bold",
                        fontsize=16, color=text_colour)
    else:
        fig.text(0.10, 0.98, title_str, fontsize=16, fontweight="bold", color=text_colour)

    if subtitle:
        fig.text(0.10, 0.955, subtitle, fontsize=11, color=text_colour)

    ax.legend(loc="lower right")
    plt.tight_layout()
    _save_and_show(fig, save_path, dpi, show)
    return fig, ax


# ---------- plots: player shot map ----------

def create_shot_map_player(
    df: pd.DataFrame,
    player_name: str,
    team_of_interest: str,
    team_colour: str,
    pitch_length_x: int,
    pitch_length_y: int,
    orientation: str,
    aspect: str,
    x_dimensions: int,
    y_dimensions: int,
    subtitle: str | None = None,
    save_path: str | None = None,
    dpi: int = 300,
    show: bool = True,
):
    """
    Player shot map (penalties excluded). Returns (fig, ax).

    Expected columns: as in team shot map, plus 'player_name'.
    """
    df = df[df.get("shot_type_name", "Shot") != "Penalty"]
    df_shots = df[(df["type_name"] == "Shot") & (df["shot_outcome_name"] != "Goal") & (df["player_name"] == player_name)]
    df_goals = df[(df["type_name"] == "Shot") & (df["shot_outcome_name"] == "Goal") & (df["player_name"] == player_name)]
    df_shots_and_goals = df[(df["type_name"] == "Shot") & (df["player_name"] == player_name)]

    total_shots = int(len(df_shots))
    total_goals = int(len(df_goals))
    total_xg = float(df_shots_and_goals["shot_statsbomb_xg"].sum().round(2))

    y_shots = df_shots["location_x"].tolist()
    x_shots = df_shots["location_y"].tolist()
    y_goals = df_goals["location_x"].tolist()
    x_goals = df_goals["location_y"].tolist()

    background = "#F7F7F7"; text_colour = "black"
    mpl.rcParams.update(mpl.rcParamsDefault)
    mpl.rcParams["xtick.color"] = text_colour
    mpl.rcParams["ytick.color"] = text_colour

    fig, ax = plt.subplots(figsize=(x_dimensions, y_dimensions))
    fig.set_facecolor(background); ax.patch.set_facecolor(background)

    draw_pitch(0, pitch_length_x, 0, pitch_length_y, orientation=orientation, aspect=aspect,
               pitch_color=background, line_color="#3B3B3B", ax=ax)

    z1 = [1000 * float(i) for i in df_shots["shot_statsbomb_xg"].tolist()]
    z2 = [1000 * float(i) for i in df_goals["shot_statsbomb_xg"].tolist()]
    zo = 12

    ax.scatter(x_shots, y_shots, marker="o", color="red", edgecolors="black", s=z1, alpha=0.7, zorder=zo, label="Shots")
    ax.scatter(x_goals, y_goals, marker="*", color="green", edgecolors="black", s=z2, alpha=0.7, zorder=zo, label="Goals")

    title_str = f"{player_name} — {total_shots} shots, {total_goals} goals ({total_xg:.2f} xG) for {team_of_interest}"
    if _HAS_HIGHLIGHT:
        t_fmt = title_str.replace(team_of_interest, f"<{team_of_interest}>")
        htext.fig_htext(t_fmt, 0.10, 0.98, highlight_colors=[team_colour],
                        highlight_weights=["bold"], string_weight="bold", fontsize=16, color=text_colour)
    else:
        fig.text(0.10, 0.98, title_str, fontsize=16, fontweight="bold", color=text_colour)

    if subtitle:
        fig.text(0.10, 0.955, subtitle, fontsize=11, color=text_colour)

    ax.legend(loc="lower right")
    plt.tight_layout()
    _save_and_show(fig, save_path, dpi, show)
    return fig, ax


# ---------- plots: xG race chart ----------

def create_xg_race_chart(
    df: pd.DataFrame,
    home_team: str,
    away_team: str,
    home_colour: str,
    away_colour: str,
    mins_limit: int,
    x_dimensions: int,
    y_dimensions: int,
    subtitle: str | None = None,
    save_path: str | None = None,
    dpi: int = 300,
    show: bool = True,
):
    """
    xG race chart for a single match (minutes < mins_limit). Returns (fig, ax).

    Expected columns:
    - 'match_id', 'index', 'minute'
    - 'type_name', 'team_name', 'shot_outcome_name', 'shot_statsbomb_xg'
    - 'home_team_name', 'away_team_name'
    """
    df = df.sort_values(["match_id", "index"], ascending=[True, True])
    df = df[df["minute"] < mins_limit]
    df = df[(df["home_team_name"] == home_team) & (df["away_team_name"] == away_team)].reset_index(drop=True)
    df_shots = df[df["type_name"] == "Shot"].reset_index(drop=True)

    h_xG, a_xG = [0.0], [0.0]
    h_min, a_min = [0], [0]
    h_min_goals, a_min_goals = [], []

    for i in range(len(df_shots)):
        is_goal = df_shots.at[i, "shot_outcome_name"] == "Goal"
        minute  = int(df_shots.at[i, "minute"])
        xg_val  = float(df_shots.at[i, "shot_statsbomb_xg"])
        if df_shots.at[i, "team_name"] == home_team:
            h_xG.append(xg_val); h_min.append(minute)
            if is_goal: h_min_goals.append(minute)
        elif df_shots.at[i, "team_name"] == away_team:
            a_xG.append(xg_val); a_min.append(minute)
            if is_goal: a_min_goals.append(minute)

    def _cumsum(nums): return [sum(nums[:i+1]) for i in range(len(nums))]
    h_cum, a_cum = _cumsum(h_xG), _cumsum(a_xG)
    hlast, alast = h_cum[-1], a_cum[-1]
    last_min = int(df["minute"].max()) if len(df) else 0
    h_min.append(last_min); a_min.append(last_min)
    h_cum.append(hlast); a_cum.append(alast)
    xg_max = max(hlast, alast) if len(df) else 1.0

    # index of goal markers along step series
    a_goals_idx = [i for i, m in enumerate(a_min) if m in a_min_goals]
    a_cum_goals = [a_cum[i] for i in a_goals_idx]
    h_goals_idx = [i for i, m in enumerate(h_min) if m in h_min_goals]
    h_cum_goals = [h_cum[i] for i in h_goals_idx]

    # style
    background = "#F7F7F7"; text_colour = "black"
    mpl.rcParams.update(mpl.rcParamsDefault)
    mpl.rcParams["xtick.color"] = text_colour
    mpl.rcParams["ytick.color"] = text_colour
    mpl.rcParams.update({"font.size": 12})

    fig, ax = plt.subplots(figsize=(x_dimensions, y_dimensions))
    fig.set_facecolor(background); ax.patch.set_facecolor(background)
    ax.grid(linestyle="dotted", linewidth=0.25, color="#3B3B3B", axis="y", zorder=1)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]:
        ax.spines[s].set_color(text_colour)

    ax.step(x=h_min, y=h_cum, color=home_colour, label=home_team, linewidth=4, where="post")
    ax.step(x=a_min, y=a_cum, color=away_colour, label=away_team, linewidth=4, where="post")
    ax.scatter(x=h_min_goals, y=h_cum_goals, s=400, color=home_colour, edgecolors=background,
               marker="*", alpha=1, linewidth=0.5, zorder=2)
    ax.scatter(x=a_min_goals, y=a_cum_goals, s=400, color=away_colour, edgecolors=background,
               marker="*", alpha=1, linewidth=0.5, zorder=2)

    title = f"xG Race — {home_team} ({hlast:.2f}) vs {away_team} ({alast:.2f})"
    if _HAS_HIGHLIGHT:
        t_fmt = title.replace(home_team, f"<{home_team}>").replace(away_team, f"<{away_team}>")
        htext.fig_htext(t_fmt, 0.04, 1.02, highlight_colors=[home_colour, away_colour],
                        highlight_weights=["bold"], string_weight="bold", fontsize=16, color=text_colour)
    else:
        fig.text(0.04, 1.02, title, fontsize=16, fontweight="bold", color=text_colour)

    if subtitle:
        fig.text(0.04, 1.00, subtitle, fontsize=11, color=text_colour)

    ax.set_xlabel("Minute", color=text_colour, fontsize=12)
    ax.set_ylabel("xG", color=text_colour, fontsize=12)
    ax.set_xticks([0, 15, 30, 45, 60, 75, 90])
    ax.set_xlim([0, max(last_min + 2, 92)])
    ax.set_ylim([0, xg_max * 1.1 if xg_max > 0 else 1])

    ax.tick_params(axis="both", length=0)
    ax.legend(loc="upper left")
    plt.tight_layout()
    _save_and_show(fig, save_path, dpi, show)
    return fig, ax
