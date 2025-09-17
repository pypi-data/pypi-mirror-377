import enum
import pathlib
import types
import typing

import cyclopts
import msgspec

from dpgtheminator.models import Palette
from dpgtheminator.util import blank_theme

class CatppuccinFlavour(enum.StrEnum):
    FRAPPE = enum.auto()
    LATTE = enum.auto()
    MACCHIATO = enum.auto()
    MOCHA = enum.auto()


def generate(flavour: CatppuccinFlavour):
    palette_path = pathlib.Path(__file__).parent.parent / f'src/dpgtheminator/default_palettes/catppuccin_{flavour}.json'
    content = palette_path.read_bytes()
    palette = msgspec.json.decode(content, type=Palette)
    palette_ns = types.SimpleNamespace(zip(palette.names, palette.colors))

    theme = blank_theme()
    core_colors = theme.components[0].core_colors
    plot_colors = theme.components[0].plot_colors
    node_colors = theme.components[0].node_colors

    core_colors.border = palette_ns.Crust
    core_colors.border_shadow = palette_ns.Mantle
    core_colors.button = palette_ns.Surface_0
    core_colors.button_active = palette_ns.Surface_2
    core_colors.button_hovered = palette_ns.Surface_1
    core_colors.check_mark = palette_ns.Subtext_0
    core_colors.child_bg = palette_ns.Overlay_0
    core_colors.docking_empty_bg = palette_ns.Crust
    core_colors.docking_preview = palette_ns.Rosewater
    core_colors.drag_drop_target = palette_ns.Yellow
    core_colors.frame_bg = palette_ns.Surface_0
    core_colors.frame_bg_active = palette_ns.Surface_2
    core_colors.frame_bg_hovered = palette_ns.Surface_1
    core_colors.header = palette_ns.Surface_0
    core_colors.header_active = palette_ns.Surface_2
    core_colors.header_hovered = palette_ns.Surface_1
    core_colors.menu_bar_bg = palette_ns.Overlay_1
    core_colors.modal_window_dim_bg = palette_ns.Surface_0
    core_colors.nav_highlight = palette_ns.Sky
    core_colors.nav_windowing_dim_bg = palette_ns.Surface_2
    core_colors.nav_windowing_highlight = palette_ns.Sky
    core_colors.plot_histogram = palette_ns.Crust
    core_colors.plot_histogram_hovered = palette_ns.Crust
    core_colors.plot_lines = palette_ns.Peach
    core_colors.plot_lines_hovered = palette_ns.Mauve
    core_colors.popup_bg = palette_ns.Overlay_0
    core_colors.resize_grip = palette_ns.Lavender
    core_colors.resize_grip_active = palette_ns.Sapphire
    core_colors.resize_grip_hovered = palette_ns.Sapphire
    core_colors.scrollbar_bg = palette_ns.Overlay_0
    core_colors.scrollbar_grab = palette_ns.Lavender
    core_colors.scrollbar_grab_active = palette_ns.Blue
    core_colors.scrollbar_grab_hovered = palette_ns.Blue
    core_colors.separator = palette_ns.Subtext_0
    core_colors.separator_active = palette_ns.Subtext_1
    core_colors.separator_hovered = palette_ns.Subtext_1
    core_colors.slider_grab = palette_ns.Overlay_0
    core_colors.slider_grab_active = palette_ns.Overlay_1
    core_colors.tab = palette_ns.Surface_0
    core_colors.tab_active = palette_ns.Surface_2
    core_colors.tab_hovered = palette_ns.Overlay_0
    core_colors.tab_unfocused = palette_ns.Surface_0
    core_colors.tab_unfocused_active = palette_ns.Surface_2
    core_colors.table_border_light = palette_ns.Overlay_0
    core_colors.table_border_strong = palette_ns.Text
    core_colors.table_header_bg = palette_ns.Mantle
    core_colors.table_row_bg = palette_ns.Surface_0
    core_colors.table_row_bg_alt = palette_ns.Surface_1
    core_colors.text = palette_ns.Text
    core_colors.text_disabled = palette_ns.Subtext_0
    core_colors.text_selected_bg = palette_ns.Crust
    core_colors.title_bg = palette_ns.Surface_0
    core_colors.title_bg_active = palette_ns.Surface_2
    core_colors.title_bg_collapsed = palette_ns.Surface_1
    core_colors.window_bg = palette_ns.Base

    plot_colors.axis_bg = palette_ns.Surface_0
    plot_colors.axis_bg_active = palette_ns.Surface_1
    plot_colors.axis_bg_hovered = palette_ns.Surface_2
    plot_colors.axis_grid = palette_ns.Overlay_0
    plot_colors.axis_text = palette_ns.Subtext_1
    plot_colors.crosshairs = palette_ns.Rosewater
    plot_colors.error_bar = palette_ns.Flamingo
    plot_colors.fill = None
    plot_colors.frame_bg = palette_ns.Surface_0
    plot_colors.inlay_text = palette_ns.Rosewater
    plot_colors.legend_bg = palette_ns.Crust
    plot_colors.legend_border = palette_ns.Crust
    plot_colors.legend_text = palette_ns.Text
    plot_colors.line = None
    plot_colors.marker_fill = palette_ns.Crust
    plot_colors.marker_outline = palette_ns.Crust
    plot_colors.plot_bg = palette_ns.Crust
    plot_colors.plot_border = palette_ns.Crust
    plot_colors.selection = palette_ns.Rosewater
    plot_colors.title_text = palette_ns.Text

    node_colors.box_selector = palette_ns.Crust
    node_colors.box_selector_outline = palette_ns.Crust
    node_colors.grid_background = palette_ns.Crust
    node_colors.grid_line = palette_ns.Crust
    node_colors.link = palette_ns.Crust
    node_colors.link_hovered = palette_ns.Crust
    node_colors.link_selected = palette_ns.Crust
    node_colors.node_background = palette_ns.Crust
    node_colors.node_background_hovered = palette_ns.Crust
    node_colors.node_background_selected = palette_ns.Crust
    node_colors.node_outline = palette_ns.Crust
    node_colors.pin = palette_ns.Crust
    node_colors.pin_hovered = palette_ns.Crust
    node_colors.title_bar = palette_ns.Crust
    node_colors.title_bar_hovered = palette_ns.Crust
    node_colors.title_bar_selected = palette_ns.Crust

    # Colormap for plots et al
    theme.colormaps.append(
        (
            palette_ns.Mauve,
            palette_ns.Red,
            palette_ns.Maroon,
            palette_ns.Peach,
            palette_ns.Yellow,
            palette_ns.Green,
            palette_ns.Teal,
            palette_ns.Sky,
            palette_ns.Sapphire,
            palette_ns.Blue,
        ),
    )


    output_path = pathlib.Path(__file__).parent.parent / f'src/dpgtheminator/default_themes/catppuccin_{flavour}.json'
    output_path.write_bytes(
        msgspec.json.encode(theme),
    )


def main(flavours: tuple[CatppuccinFlavour | typing.Literal['*'], ...]):
    # print(flavours)
    # exit()
    if '*' in flavours:
        for flavour in CatppuccinFlavour:
            generate(flavour)
    # else:
    #     for flavour in flavours:
    #         generate(flavour)


if __name__ == '__main__':
    cyclopts.run(main)
