from __future__ import annotations
import itertools
from typing import TYPE_CHECKING
import pathlib
import uuid

import msgspec

import dearpygui.dearpygui as dpg
import dpgcontainers.containers as dpgc

if TYPE_CHECKING:
    from dpgtheminator.controller import Controller
from dpgtheminator.exceptions import ThemeNotLoaded
from dpgtheminator.models import Color
from dpgtheminator.models import CoreColors
from dpgtheminator.models import NodeColors
from dpgtheminator.models import PlotColors
from dpgtheminator.models import Palette
# from dpgtheminator.models import ThemeComponent


shared_state = {
    'mouse_position': [0, 0],
}

class ColorEditWindow(dpgc.Window):
    def __init__(self, name: str, color: Color, row: 'ColorRow'):
        super().__init__(name, show=False, width=310, height=400)
        self.row = row
        self(
            picker=dpgc.ColorPicker(
                default_value=color.get_dpg_color(),
                callback=row.set_color,
            )
        )
        self.palette_display: dpgc.DPGContainersBase|None = None

    def add_palette(self, palette: Palette):
        if self.palette_display is None:
            self(palette_display=dpgc.ChildWindow()).render()
            self.palette_display = self.find('palette_display')

        self.palette_display.clear()

        per_row = 10
        names = palette.names
        if names is None:
            names = itertools.repeat('')
        for batch in itertools.batched(zip(names, palette.colors), per_row):
            row = dpgc.Group(horizontal=True)
            for name, color in batch:
                row(
                    dpgc.ColorButton(width=20, height=20, default_value=color.get_dpg_color(), callback=self.set_color)(
                        dpgc.Tooltip('')(
                            dpgc.Text(name),
                        ),
                    ),
                )
            self.palette_display(row)
        self.palette_display.render()

    def set_color(self, sender: int):
        dpg_color = dpg.get_value(sender)
        norm_color = [value / 255 for value in dpg_color]
        self.row.set_color(-1, norm_color)
        self.find('picker').value = dpg_color



class ColorRow(dpgc.TableRow):
    def __init__(self, name: str, color: Color, controller: Controller):
        super().__init__()

        self.name = name
        self.color = color
        self.controller = controller

        self(
            dpgc.Text(name),
            color_button = dpgc.ColorButton(
                width=20,
                height=20,
                default_value=color.get_dpg_color(),
                callback=self.edit_color,
            ),
        )
        self.edit_window = ColorEditWindow(name, color, self).render()
        # self.edit_window = dpgc.Window(name, show=False, width=300, height=300)(
        #     picker=dpgc.ColorPicker(
        #         default_value=self.color.get_dpg_color(),
        #         callback=self.set_color,
        #     ),
        # )

    def edit_color(self):
        self.edit_window.render()
        self.edit_window.configure(pos=shared_state['mouse_position'])
        self.edit_window.show = True

    def set_color(self, sender: int, norm_color: list[float]):
        self.color.red, self.color.green, self.color.blue, self.color.alpha = norm_color
        self.search_named_children('color_button').value = self.color.get_dpg_color()
        self.controller.reload().bind()

    def reset_color(self, color: Color):
        self.color = color
        self.search_named_children('color_button').value = self.color.get_dpg_color()


class ColorsTable(dpgc.Table):
    def __init__(self, colors: CoreColors|NodeColors|PlotColors, controller: Controller):
        super().__init__(header_row=False)
        self(
            dpgc.TableColumn(),
            dpgc.TableColumn(),
        )
        for name in colors.__struct_fields__:
            color = getattr(colors, name)
            if color is not None:
                self(ColorRow(name, color, controller))


class Theminator(dpgc.Window):
    def __init__(self, controller: Controller):
        if not controller.loaded:
            raise ThemeNotLoaded()

        super().__init__('dpgTheminator', width=400, height=600)
        self.controller = controller
        self.handler_registry = dpgc.HandlerRegistry()(
            dpgc.MouseMoveHandler(callback=self.set_mouse_position),
        ).render()

        self.file_dialog = dpgc.FileDialog(show=False, width=600, height=450)(
            dpgc.FileExtension('.json'),
        ).render()

        # TODO: (202509) satisfies typechecker for now, but should be handling these cases instead
        assert controller.theme is not None
        assert controller.theme.components[0].core_colors is not None
        assert controller.theme.components[0].plot_colors is not None
        assert controller.theme.components[0].node_colors is not None

        self(
            dpgc.MenuBar()(
                dpgc.Menu('File')(
                    dpgc.MenuItem('Open', callback=self.menu_open),
                    dpgc.MenuItem('Save', callback=self.menu_save),
                    dpgc.MenuItem('Save As', callback=self.menu_save_as),
                    dpgc.Separator(),
                    # dpgc.MenuItem('Generate Palette', callback=self.menu_generate_palette),
                    dpgc.MenuItem('Load Palette', callback=self.menu_load_palette),
                ),
                dpgc.Menu('Defaults')(
                    dpgc.Menu('Themes')(
                        dpgc.MenuItem('Light', user_data='light', callback=self.menu_load_default_theme),
                        dpgc.MenuItem('Dark', user_data='dark', callback=self.menu_load_default_theme),
                        dpgc.MenuItem('Catpuccin Frappe', user_data='catppuccin_frappe', callback=self.menu_load_default_theme),
                        dpgc.MenuItem('Catpuccin Mocha', user_data='catppuccin_mocha', callback=self.menu_load_default_theme),
                        dpgc.MenuItem('Catpuccin Macchiato', user_data='catppuccin_macchiato', callback=self.menu_load_default_theme),
                        dpgc.MenuItem('Catpuccin Latte', user_data='catppuccin_latte', callback=self.menu_load_default_theme),
                    ),
                    dpgc.MenuItem('Load Dark Theme', callback=self.debug_menu_load_dark_theme),
                    dpgc.MenuItem('Load Frappe Palette', callback=self.debug_menu_load_frappe_palette),
                ),
            ),

            dpgc.Group(horizontal=True)(
                theme_name=dpgc.Text(f'Theme: {controller.name}'),  # type: ignore
            ),
            dpgc.CollapsingHeader('Core Colors', default_open=True)(
                core_colors_table=ColorsTable(controller.theme.components[0].core_colors, controller),
            ),
            dpgc.CollapsingHeader('Plot Colors')(
                plot_colors_table=ColorsTable(controller.theme.components[0].plot_colors, controller),
            ),
            dpgc.CollapsingHeader('Node Colors')(
                node_colors_table=ColorsTable(controller.theme.components[0].node_colors, controller),
            ),
        )

    def menu_open(self, sender, app_data, user_data):
        self.file_dialog.configure(
            label='Open',
            show=True,
            callback=self.open_file,
        )

    def menu_save(self, sender, app_data, user_data):
        if self.controller.is_default_theme:
            dpgc.Window(modal=True)(
                dpgc.Text('Cannot save over default themes.'),
            ).render()
        else:
            self.controller.save()


    def menu_save_as(self, sender, app_data, user_data):
        self.file_dialog.configure(
            label='Save As',
            show=True,
            callback=self.save_as,
        )

    def menu_generate_palette(self):
        pass

    def menu_load_palette(self):
        self.file_dialog.configure(
            label='Load Palette',
            show=True,
            callback=self.load_palette,
        )

    def menu_load_default_theme(self, sender, app_data, user_data):
        self.controller.load(user_data).bind()
        self.controller.rebind_colormaps()
        self.on_theme_load()

    def load_palette(self, sender: int, app_data: dict[str, str]):
        file_path = pathlib.Path(app_data['file_path_name'])
        content = file_path.read_bytes()
        palette = msgspec.json.decode(content, type=Palette)
        self.set_palette(palette)

    def set_palette(self, palette: Palette):
        tables = (
            'core_colors_table',
            'plot_colors_table',
            'node_colors_table',
        )
        for table in tables:
            for child in self.find(table).children:
                if isinstance(child, ColorRow):
                    child.edit_window.add_palette(palette)


    def open_file(self, sender, app_data, user_data):
        file_path = pathlib.Path(app_data['file_path_name'])
        self.controller.load(file_path).bind()
        self.controller.rebind_colormaps()
        self.on_theme_load()

    def on_theme_load(self):
        tables = (
            'core_colors_table',
            'plot_colors_table',
            'node_colors_table',
        )
        for table in tables:
            attr_name = '_'.join(table.split('_')[:-1])
            theme_colors = getattr(self.controller.theme.components[0], attr_name)
            for child in self.find(table).children:
                if isinstance(child, ColorRow):
                    theme_color = getattr(theme_colors, child.name)
                    if theme_color is not None:
                        child.reset_color(theme_color)
                        child.edit_window.find('picker').set_value(theme_color.get_dpg_color())

    def save_as(self, sender, app_data, user_data):
        file_path = pathlib.Path(app_data['file_path_name'])
        self.controller.save_as(file_path)

    def set_mouse_position(self, sender, position):
        shared_state['mouse_position'] = position

    def debug_menu_load_dark_theme(self):
        pass

    def debug_menu_load_frappe_palette(self):
        app_data = {
            'file_path_name': pathlib.Path(__file__).parent.parent / 'default_palettes/catppuccin_frappe.json',
        }
        self.load_palette(-1, app_data)

