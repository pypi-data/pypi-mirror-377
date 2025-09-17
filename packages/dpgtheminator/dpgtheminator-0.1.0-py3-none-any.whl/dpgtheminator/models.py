import msgspec
import typing

import dearpygui.dearpygui as dpg  # type: ignore
import dpgcontainers.base
import dpgcontainers.containers as dpgc


def _snake_to_camel(name: str) -> str:
    camel_parts = [name[0].upper(), ]
    next_upper = False
    for char in name[1:]:
        if char == '_':
            next_upper = True
            continue
        if next_upper:
            camel_parts.append(char.upper())
            next_upper = False
            continue
        camel_parts.append(char)
    return ''.join(camel_parts)


def _camel_to_snake(name: str) -> str:
    snake_parts = [name[0].lower(), ]
    for char in name[1:]:
        if char.isupper():
            snake_parts.append('_')
        snake_parts.append(char.lower())
    return ''.join(snake_parts)


class Color(msgspec.Struct):
    red: float
    green: float
    blue: float
    alpha: float = 1.0

    def get_dpg_color(self) -> tuple[int, int, int, int]:
        r = round(self.red * 255)
        g = round(self.green * 255)
        b = round(self.blue * 255)
        a = round(self.alpha * 255)
        return (r, g, b, a)


class ColorsMixin:
    def get_dpg_colors(self) -> dict[str, dpgc.ThemeColor]:
        colors = {}
        for name in self.__struct_fields__:  # type: ignore
            color = getattr(self, name)
            if color is None:
                continue
            camel_name = _snake_to_camel(name)
            const_name = f'{self._dpg_prefix}{camel_name}'  # type: ignore
            const_value = getattr(dpg, const_name)
            colors[name] = dpgc.ThemeColor(const_value, color.get_dpg_color(), category=self._dpg_category)  # type: ignore
        return colors

class CoreColors(msgspec.Struct, ColorsMixin):
    '''CoreColors colors'''
    _dpg_prefix: typing.ClassVar[str] = 'mvThemeCol_'
    _dpg_category: typing.ClassVar[int] = dpg.mvThemeCat_Core

    border: Color|None = None
    border_shadow: Color|None = None
    button: Color|None = None
    button_active: Color|None = None
    button_hovered: Color|None = None
    check_mark: Color|None = None
    child_bg: Color|None = None
    docking_empty_bg: Color|None = None
    docking_preview: Color|None = None
    drag_drop_target: Color|None = None
    frame_bg: Color|None = None
    frame_bg_active: Color|None = None
    frame_bg_hovered: Color|None = None
    header: Color|None = None
    header_active: Color|None = None
    header_hovered: Color|None = None
    menu_bar_bg: Color|None = None
    modal_window_dim_bg: Color|None = None
    nav_highlight: Color|None = None
    nav_windowing_dim_bg: Color|None = None
    nav_windowing_highlight: Color|None = None
    plot_histogram: Color|None = None
    plot_histogram_hovered: Color|None = None
    plot_lines: Color|None = None
    plot_lines_hovered: Color|None = None
    popup_bg: Color|None = None
    resize_grip: Color|None = None
    resize_grip_active: Color|None = None
    resize_grip_hovered: Color|None = None
    scrollbar_bg: Color|None = None
    scrollbar_grab: Color|None = None
    scrollbar_grab_active: Color|None = None
    scrollbar_grab_hovered: Color|None = None
    separator: Color|None = None
    separator_active: Color|None = None
    separator_hovered: Color|None = None
    slider_grab: Color|None = None
    slider_grab_active: Color|None = None
    tab: Color|None = None
    tab_active: Color|None = None
    tab_hovered: Color|None = None
    tab_unfocused: Color|None = None
    tab_unfocused_active: Color|None = None
    table_border_light: Color|None = None
    table_border_strong: Color|None = None
    table_header_bg: Color|None = None
    table_row_bg: Color|None = None
    table_row_bg_alt: Color|None = None
    text: Color|None = None
    text_disabled: Color|None = None
    text_selected_bg: Color|None = None
    title_bg: Color|None = None
    title_bg_active: Color|None = None
    title_bg_collapsed: Color|None = None
    window_bg: Color|None = None


class PlotColors(msgspec.Struct, ColorsMixin):
    '''PlotColors colors'''
    _dpg_prefix: typing.ClassVar[str] = 'mvPlotCol_'
    _dpg_category: typing.ClassVar[int] = dpg.mvThemeCat_Plots

    axis_bg: Color|None = None
    axis_bg_active: Color|None = None
    axis_bg_hovered: Color|None = None
    axis_grid: Color|None = None
    axis_text: Color|None = None
    crosshairs: Color|None = None
    error_bar: Color|None = None
    fill: Color|None = None
    frame_bg: Color|None = None
    inlay_text: Color|None = None
    legend_bg: Color|None = None
    legend_border: Color|None = None
    legend_text: Color|None = None
    line: Color|None = None
    marker_fill: Color|None = None
    marker_outline: Color|None = None
    plot_bg: Color|None = None
    plot_border: Color|None = None
    selection: Color|None = None
    title_text: Color|None = None


class NodeColors(msgspec.Struct, ColorsMixin):
    '''NodeColors colors'''
    _dpg_prefix: typing.ClassVar[str] = 'mvNodeCol_'
    _dpg_category: typing.ClassVar[int] = dpg.mvThemeCat_Nodes

    box_selector: Color|None = None
    box_selector_outline: Color|None = None
    grid_background: Color|None = None
    grid_line: Color|None = None
    link: Color|None = None
    link_hovered: Color|None = None
    link_selected: Color|None = None
    node_background: Color|None = None
    node_background_hovered: Color|None = None
    node_background_selected: Color|None = None
    node_outline: Color|None = None
    pin: Color|None = None
    pin_hovered: Color|None = None
    title_bar: Color|None = None
    title_bar_hovered: Color|None = None
    title_bar_selected: Color|None = None


class ThemeComponent(msgspec.Struct):
    core_colors: CoreColors | None = None
    plot_colors: PlotColors | None = None
    node_colors: NodeColors | None = None
    component: int = dpg.mvAll


class Theme(msgspec.Struct):
    components: list[ThemeComponent] = list()
    colormaps: list[tuple[Color, ...]] = list()


class Palette(msgspec.Struct):
    colors: list[Color]
    names: list[str]

