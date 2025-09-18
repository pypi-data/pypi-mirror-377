# footsbviz

Zero-friction helpers to visualize **StatsBomb Open Data** — without manual data engineering.

> Not affiliated with StatsBomb. Please respect the StatsBomb Open Data license and terms.

## Install

```bash
pip install footsbviz
# or with optional viz extras:
pip install "footsbviz[viz]"
```

## Quickstart
```bash
import footsbviz as fz

# events_df = (your StatsBomb events DataFrame with standard columns)
fig, ax = fz.create_shot_map_team(
    events_df, team_name="Belgium", team_colour="#d00",
    pitch_length_x=120, pitch_length_y=80,
    orientation="horizontal", aspect="full",
    x_dimensions=10, y_dimensions=7,
    subtitle="Example Match", save_path=None, show=True
)
```
## Credits

This library draws inspiration from community work on StatsBomb visuals. Certain function ideas and column expectations originated in publicly shared scripts; we re-implemented them in a package-friendly way and added a stable API. See CREDITS.md for attribution.
