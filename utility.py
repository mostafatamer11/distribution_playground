import json
import matplotlib as mpl


def gray_to_hex(gray_value: str):
    if gray_value.startswith("gray"):
        if len(gray_value) > 4:
            try:
                val = int(gray_value[4:]) * 255 / 100
                val = max(0, min(255, val))
                rgb = int(val), int(val), int(val)
                hex_color = '#%02x%02x%02x' % rgb
                return hex_color
            except ValueError:
                raise ValueError("Invalid gray value format after 'gray'")
        elif len(gray_value) == 4:
            return "#808080"
        else:
            raise ValueError("Invalid gray value format")
    elif gray_value.startswith("#"):
        return gray_value
    else:
        raise ValueError(f"Invalid input format. Expected grayN or a hex color (e.g. #RRGGBB) {gray_value}")



def load_theme(theme_path: str) -> dict:
    with open(theme_path, "r") as f:
        ctk_theme = json.load(f)

    bg_color = ctk_theme["CTk"]["fg_color"][1]
    text_color = ctk_theme["CTkButton"]["text_color"][1]
    axes_bg = ctk_theme["CTkFrame"]["fg_color"][1]
    line_color = ctk_theme["CTkButton"]["fg_color"][1]

    mpl.rcParams.update({
        'axes.edgecolor': gray_to_hex(text_color),
        'axes.facecolor': gray_to_hex(axes_bg),
        'axes.labelcolor': gray_to_hex(text_color),
        'figure.facecolor': gray_to_hex(bg_color),
        'xtick.color': gray_to_hex(text_color),
        'ytick.color': gray_to_hex(text_color),
        'grid.color': gray_to_hex('#444444'),
        'text.color': gray_to_hex(text_color),
        'lines.color': gray_to_hex(line_color),
        'font.family': 'Roboto',
        'font.size': 13,
        'legend.facecolor': gray_to_hex(axes_bg),
        'legend.edgecolor': gray_to_hex(text_color),
        'legend.labelcolor': gray_to_hex(text_color),
        'axes.titlecolor': gray_to_hex(text_color),
    })

    return mpl.rcParams

