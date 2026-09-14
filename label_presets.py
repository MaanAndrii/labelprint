"""Common label sizes used by the label configuration dialog."""

CUSTOM_PRESET = "Власний розмір"
DEFAULT_PRESET = "80 × 53 мм"

LABEL_SIZE_PRESETS = {
    DEFAULT_PRESET: (80.0, 53.0),
    "30 × 20 мм": (30.0, 20.0),
    "40 × 30 мм": (40.0, 30.0),
    "50 × 30 мм": (50.0, 30.0),
    "50 × 40 мм": (50.0, 40.0),
    "60 × 40 мм": (60.0, 40.0),
    "70 × 50 мм": (70.0, 50.0),
    "100 × 50 мм": (100.0, 50.0),
}


def find_matching_preset(width_mm, height_mm):
    """Return the preset name matching the dimensions, or the custom option."""
    for name, (preset_width, preset_height) in LABEL_SIZE_PRESETS.items():
        if width_mm == preset_width and height_mm == preset_height:
            return name
    return CUSTOM_PRESET
