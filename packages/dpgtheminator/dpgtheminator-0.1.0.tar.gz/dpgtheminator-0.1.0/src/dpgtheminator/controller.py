import dataclasses
import functools
import importlib.resources
import pathlib

import dearpygui.dearpygui as dpg  # type: ignore
from dpgcontainers.base import DPGContainersBase
import dpgcontainers.containers as dpgc
import msgspec

import dpgtheminator
from dpgtheminator import exceptions
from dpgtheminator.models import Theme
from dpgtheminator.gui.theminator import Theminator

@dataclasses.dataclass
class Controller:
    name: str | None = None
    theme: Theme | None = None
    dpg_theme: dpgc.Theme | None = None
    loaded: bool = False
    dpg_colormaps: list[dpgc.Colormap] = dataclasses.field(default_factory=list)
    colormap_bindings: list[tuple[int, int|str|None]] = dataclasses.field(default_factory=list)
    theme_path: pathlib.Path | None = None
    is_default_theme: bool = True


    def reload(self):
        self.load(self.theme, self.name)
        return self

    @functools.singledispatchmethod
    def load(self, theme: Theme, name: str):
        self.name = name
        self.theme = theme
        self.dpg_theme = dpgc.Theme()
        for component in theme.components:
            dpg_component = dpgc.ThemeComponent(component.component)
            if component.core_colors is not None:
                dpg_component(*component.core_colors.get_dpg_colors().values())
            if component.plot_colors is not None:
                dpg_component(*component.plot_colors.get_dpg_colors().values())
            if component.node_colors is not None:
                dpg_component(*component.node_colors.get_dpg_colors().values())

            self.dpg_theme(dpg_component)
        self.dpg_theme.render()

        self.dpg_colormaps = []
        if theme.colormaps:
            registry = dpgc.ColormapRegistry()
            for colormap in theme.colormaps:
                dpg_colormap = dpgc.Colormap(
                    list(color.get_dpg_color() for color in colormap),
                    qualitative=True,
                )
                registry(dpg_colormap)
                self.dpg_colormaps.append(dpg_colormap)
            registry.render()

        self.loaded = True
        return self

    @load.register
    def _(self, theme: pathlib.Path):
        self.theme_path = theme
        self.is_default_theme = False
        name = theme.name
        content = theme.read_bytes()
        loaded = msgspec.json.decode(content, type=Theme)
        return self.load(loaded, name)

    @load.register
    def _(self, theme: str):
        try:
            content = importlib.resources.read_binary(dpgtheminator, f'default_themes/{theme}.json')
        except FileNotFoundError:
            return self.load(pathlib.Path(theme))
        else:
            self.is_default_theme = True
            loaded = msgspec.json.decode(content, type=Theme)
            return self.load(loaded, theme)

    def save_as(self, path: pathlib.Path):
        encoded = msgspec.json.encode(self.theme)
        path.write_bytes(encoded)

    def save(self):
        if self.is_default_theme:
            raise exceptions.CannotSaveOverDefaultTheme()
        encoded = msgspec.json.encode(self.theme)
        self.theme_path.write_bytes(encoded)

    def bind(self, target: str|int|DPGContainersBase|None = None):
        if self.dpg_theme is None:
            raise exceptions.ThemeNotLoaded()
        if target is None:
            dpg.bind_theme(self.dpg_theme.id_)  # type: ignore
            return self
        if isinstance(target, DPGContainersBase):
            target = target.id_
        dpg.bind_item_theme(target, self.dpg_theme.id_)  # type: ignore
        return self

    def bind_colormap(self, index: int, target: str|int|DPGContainersBase):
        self.dpg_colormaps[index].bind(target)
        if isinstance(target, DPGContainersBase):
            cache_target: int|str = target.id_
        else:
            cache_target = target

        self.colormap_bindings.append((index, cache_target))

    def rebind_colormaps(self):
        known_bindings = self.colormap_bindings
        self.colormap_bindings = []
        for index, target in known_bindings:
            self.bind_colormap(index, target)

    def show_gui(self):
        gui = Theminator(self)
        gui.render()
        return self
