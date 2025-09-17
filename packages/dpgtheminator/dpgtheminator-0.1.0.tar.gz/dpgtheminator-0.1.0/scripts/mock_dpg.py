import msgspec

from dpgtheminator.models import Color
from dpgtheminator.models import CoreColors
from dpgtheminator.models import NodeColors
from dpgtheminator.models import PlotColors
from dpgtheminator.models import Theme
from dpgtheminator.models import ThemeComponent


def _camel_to_snake(name: str) -> str:
    snake_parts = [name[0].lower(), ]
    for char in name[1:]:
        if char.isupper():
            snake_parts.append('_')
        snake_parts.append(char.lower())
    return ''.join(snake_parts)


class MockDpg:
    def __init__(self) -> None:
        self.color_keys: list[str] = []
        self.color_values: list[tuple[int, int, int, int]] = []
        self.color_cats: list[str] = []

    def __getattr__(self, key: str) -> str:
        return key

    def add_theme_color(self, key, values, category='mvThemeCat_Core'):
        self.color_keys.append(key)
        self.color_values.append(values)
        self.color_cats.append(category)

    def to_theme(self) -> Theme:
        core_colors = CoreColors()
        plot_colors = PlotColors()
        node_colors = NodeColors()
        cat_to_colors = {
            'mvThemeCat_Core': core_colors,
            'mvThemeCat_Plots': plot_colors,
            'mvThemeCat_Nodes': node_colors,
        }

        for key, values, cat in zip(self.color_keys, self.color_values, self.color_cats):
            _, camel_key = key.split('_')
            snake_key = _camel_to_snake(camel_key)
            norm_values = tuple(v/255 for v in values)
            setattr(cat_to_colors[cat], snake_key, Color(*norm_values))

        component = ThemeComponent(
            core_colors,
            plot_colors,
            node_colors,
        )

        return Theme([component])

    def to_json(self) -> bytes:
        theme = self.to_theme()
        json = msgspec.json.encode(theme)
        return json
