"""
footsbviz — Zero-friction visuals for StatsBomb open data.

Public API (v0.1):
- draw_pitch
- create_shot_map_team
- create_shot_map_player
- create_xg_race_chart
"""

from .plots import (
    draw_pitch,
    create_shot_map_team,
    create_shot_map_player,
    create_xg_race_chart,
)

__all__ = [
    "draw_pitch",
    "create_shot_map_team",
    "create_shot_map_player",
    "create_xg_race_chart",
]

__version__ = "0.1.0"

