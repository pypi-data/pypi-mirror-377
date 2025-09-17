import pathlib

from dpgtheminator.models import Color
from dpgtheminator.models import CoreColors
from dpgtheminator.models import NodeColors
from dpgtheminator.models import PlotColors
from dpgtheminator.models import Theme
from dpgtheminator.models import ThemeComponent


def project_root() -> pathlib.Path:
    path = pathlib.Path(__file__).parent.parent.parent
    return path


def blank_theme():
    colors = (
        CoreColors(),
        PlotColors(),
        NodeColors(),
    )
    for color_inst in colors:
        for field in color_inst.__struct_fields__:
            setattr(color_inst, field, Color(0.0, 0.0, 0.0, 0.0))
    component = ThemeComponent(*colors)
    theme = Theme([component])
    return theme


