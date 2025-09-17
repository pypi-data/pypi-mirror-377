from collections.abc import Callable
# import pathlib
import re
from typing import Generator

import httpx

from dpgtheminator.models import Color
from dpgtheminator.models import CoreColors
from dpgtheminator.models import NodeColors
from dpgtheminator.models import PlotColors
from dpgtheminator.models import Theme
from dpgtheminator.models import ThemeComponent


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


def filtered_getter(
    url: str,
    filter_func: Callable[[list[str], ], Generator[str]]
) -> Callable[[],Generator[str]]:
    response = httpx.get(url)
    lines = response.text.strip().split('\n')
    def _inner():
        return filter_func(lines)
    return _inner


# Defines
mv_app_item_h_url = 'https://raw.githubusercontent.com/hoffstadt/DearPyGui/57d10ff98b7d60a4725df17f5c39b2205bf80ebd/src/mvAppItem.h'
def filter_mv_app_item_h(lines: list[str]) -> Generator[str]:
    for line in lines:
        if line.startswith('#define MV_BASE_COL_') or line.startswith('#define mvImGuiCol_'):
            yield line
get_defines = filtered_getter(mv_app_item_h_url, filter_mv_app_item_h)

# PlotColors from imPlot
implot_cpp_url = 'https://raw.githubusercontent.com/epezent/implot/3da8bd34299965d3b0ab124df743fe3e076fa222/implot.cpp'
def filter_implot_cpp(lines: list[str]) -> Generator[str]:
    style_first_lines = {
        'classic': 5795,
        'dark': 5824,
        'light': 5853,
    }

    first_line = style_first_lines['classic']
    last_line = first_line + 20

    # from first_line-1 because 0-indexed vs linenums which are 1-indexed
    for i in range(first_line - 1, last_line):
        yield lines[i]
get_implot_lines = filtered_getter(implot_cpp_url, filter_implot_cpp)

# Node colors
mv_context_cpp_url = 'https://raw.githubusercontent.com/hoffstadt/DearPyGui/57d10ff98b7d60a4725df17f5c39b2205bf80ebd/src/mvContext.cpp'
def filter_mv_context(lines: list[str]) -> Generator[str]:
    for line in lines:
        if line.startswith('    ImNodes::GetStyle().Colors[ImNodesCol_'):
            yield line
get_imnode_lines = filtered_getter(mv_context_cpp_url, filter_mv_context)

# ModuleConstants.push_back
# dearpygui_cpp_url = 'https://raw.githubusercontent.com/hoffstadt/DearPyGui/57d10ff98b7d60a4725df17f5c39b2205bf80ebd/src/dearpygui.cpp'


def parse_color(value: str) -> Color:
    assert value.startswith('mvColor(')
    nums = value[8:-1].split(', ')
    norm = tuple(int(c)/255 for c in nums)
    return Color(*norm)


IMPLOT_AUTO_COL = Color(0, 0, 0, 0)
def parse_implot_value(value: str) -> Color:
    if value == 'IMPLOT_AUTO_COL':
        return IMPLOT_AUTO_COL

    nums = [
        float(n[:-1])
        for n
        in value[7:-1].split(', ')
    ]
    return Color(*nums)

def main():
    # CORE COLORS
    palette = {}
    colors = {}

    for line in get_defines():
        if not line:
            continue
        parts = line.strip().split(' ')
        _, name, *rest = parts
        value = ' '.join(rest)
        if name.startswith('MV_BASE_COL_'):
            palette[name] = parse_color(value)
        else:
            if value in palette:
                colors[name] = palette[value]
            else:
                colors[name] = parse_color(value)

    core_colors = CoreColors()

    for name, value in colors.items():
        _, dpg_camel = name.split('_')
        dpg_snake = _camel_to_snake(dpg_camel)
        if hasattr(core_colors, dpg_snake):
            setattr(core_colors, dpg_snake, value)

    # Whatever - these are defined in non-standard ways in the source
    core_colors.text_disabled = palette['MV_BASE_COL_textDisabledColor']
    core_colors.resize_grip_active = core_colors.resize_grip_hovered

    # PLOT COLORS
    plot_colors = PlotColors()

    implot_regex = r' +colors\[ImPlotCol_([a-zA-Z]+)] += ([^;]+).*'
    implot_matcher = re.compile(implot_regex)
    for line in get_implot_lines():
        match = implot_matcher.match(line)
        name_camel, value_str = match.groups()
        name_snake = _camel_to_snake(name_camel)
        if hasattr(plot_colors, name_snake):
            value = parse_implot_value(value_str)
            setattr(plot_colors, name_snake, value)
        else:
            print(f'implot: {name_snake} defined but not found on plot_colors')


    # NODE COLORS
    node_colors = NodeColors()
    imnode_regex = r' +ImNodes::GetStyle\(\)\.Colors\[ImNodesCol_([a-zA-Z]+)\] = mvColor::ConvertToUnsignedInt\(mvColor\(([0-9]+), ([0-9]+), ([0-9]+), ([0-9]+)\)\);'
    imnode_matcher = re.compile(imnode_regex)
    imnode_alt_regex = r' +ImNodes::GetStyle\(\)\.Colors\[ImNodesCol_([a-zA-Z]+)\] = mvColor::ConvertToUnsignedInt\(mvImGuiCol_([a-zA-Z]+)\);'
    imnode_alt_matcher = re.compile(imnode_alt_regex)
    for line in get_imnode_lines():
        match = imnode_matcher.match(line)
        if match:
            name_camel, *value_strs = match.groups()
            name_snake = _camel_to_snake(name_camel)
            if hasattr(node_colors, name_snake):
                value = Color(*(int(value_str)/255 for value_str in value_strs))
                setattr(node_colors, name_snake, value)
            else:
                print(f'imnode: {name_snake} defined but not found on node_colors')
        else:
            # Alternate form - uses a defined color instead, steal values from core_colors
            alt_match = imnode_alt_matcher.match(line)
            name_camel, value_key_camel = alt_match.groups()
            name_snake = _camel_to_snake(name_camel)
            value_key_snake = _camel_to_snake(value_key_camel)
            color = getattr(core_colors, value_key_snake)
            setattr(node_colors, name_snake, color)

    for key in CoreColors.__struct_fields__:
        if getattr(core_colors, key) is None:
            print('none in core: ', key)

    for key in PlotColors.__struct_fields__:
        if getattr(plot_colors, key) is None:
            print('none in plot: ', key)

    for key in NodeColors.__struct_fields__:
        if getattr(node_colors, key) is None:
            print('none in node: ', key)

    component = ThemeComponent(
        core_colors,
        plot_colors,
        node_colors,
    )

    theme = Theme([component])

    print(theme)


if __name__ == '__main__':
    main()
