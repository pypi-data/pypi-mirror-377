import math

import dearpygui.dearpygui as dpg  # type: ignore
import dpgcontainers as dpgc

import dpgtheminator as dpgt


dpg = dpgc.wrap_dpg(dpg)

dpg.create_context()
dpg.configure_app(docking=True, docking_space=True)

x_data = [x / 1000 for x in range(0, 5000, 300)]
y1_data = [math.cos(x) - .5 for x in x_data]
y2_data = [math.sin(x) for x in x_data]
y3_data = [d + .15 for d in y2_data]
y4_data = [d + .4 for d in y2_data]



def drop_callback(sender, app_data, user_data):
    text_id = dpg.get_item_children(sender, 1)[0]
    text = dpg.get_value(text_id)
    parts = text.split(' ')
    new_count = int(parts[-1]) + app_data
    parts[-1] = str(new_count)
    new_text = ' '.join(parts)
    dpg.set_value(text_id, new_text)

class DemoWindow(dpgc.Window):
    def __init__(self):
        super().__init__('Demo Window', pos=(600, 50), width=600, height=800)

        self(
            dpgc.MenuBar()(
                dpgc.Menu('Utils')(
                    dpgc.MenuItem('Toggle collapsed items', callback=self.toggle_collapsed_items),
                ),
            ),
            dpgc.Group(horizontal=False)(
                dpgc.Group(horizontal=True)(
                    dpgc.InputText(default_value='Text Input', width=150),
                    dpgc.InputInt('int input', default_value=0, width=100),
                    dpgc.InputFloat('float input', default_value=0.0, width=100),
                ),
                dpgc.Group(horizontal=True)(
                    dpgc.InputText(default_value='multi line\ntext input\nWITH TOOLTIP', multiline=True)(
                        dpgc.Tooltip()(
                            dpgc.Text('Tooltip'),
                        ),
                    ),
                    dpgc.Group()(
                        dpgc.Group(horizontal=True)(
                            dpgc.RadioButton(('radio', 'buttons')),
                            dpgc.Group()(
                                dpgc.Checkbox('Check'),
                                dpgc.Checkbox('Box', default_value=True),
                            ),
                        ),
                        dpgc.SliderInt('Slider', width=125),
                        dpgc.Combo(('choice 1', 'choice 2', 'choice 3', ), 'Combo', width=125),
                    ),
                ),
                dpgc.Separator(),
                dpgc.Group(horizontal=True)(
                    dpgc.Button('Button > Popup', )(
                        dpgc.Popup()(
                            dpgc.Text('Hello there, this is a popup'),
                        ),
                    ),
                    dpgc.Button('Button > Modal', )(
                        dpgc.Popup(modal=True)(
                            dpgc.Text('Hello there, this is a modal popup'),
                        ),
                    ),
                    dpgc.Button('Drag-Dropable Button', )(
                        dpgc.DragPayload(drag_data=1, payload_type='int'),
                    ),
                ),
                dpgc.ChildWindow(height=50, drop_callback=drop_callback, payload_type='int')(
                    dpgc.Text('Child Window / Drop Zone!  Drop Count: 0'),
                ),
            ),
            dpgc.Group(horizontal=True)(
                dpgc.Selectable('Selectable 1', width=100, indent=50, classes=('selectable1')),
                dpgc.Selectable('Selectable 2', width=100, indent=200, classes=('selectable2')),
                dpgc.Selectable('Selectable 3', width=100, indent=350, classes=('selectable3')),
            ),
            dpgc.Table(
                row_background=True,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
            )(
                dpgc.TableColumn('Table'),
                dpgc.TableColumn('Headers'),
                dpgc.TableRow()(
                    dpgc.Text('Table'),
                    dpgc.Text('Contents'),
                ),
                dpgc.TableRow()(
                    dpgc.Text('Row'),
                    dpgc.Text('Two'),
                ),
                dpgc.TableRow()(
                    dpgc.Text('Row'),
                    dpgc.Text('Three'),
                ),
            ),
            dpgc.CollapsingHeader('Collapsing Header > Tree', classes=['collapsed_item', ])(
                dpgc.TreeNode('Tree')(
                    dpgc.TreeNode('Node 1')(
                        dpgc.TreeNode('Node 1.1', leaf=True),
                        dpgc.TreeNode('Node 1.2', leaf=True),
                    ),
                    dpgc.TreeNode('Node 2', leaf=True),
                    dpgc.TreeNode('Node 3')(
                        dpgc.TreeNode('Node 3.1', leaf=True),
                        dpgc.TreeNode('Node 3.2')(
                            dpgc.TreeNode('Node 3.2.1', leaf=True),
                            dpgc.TreeNode('Node 3.2.2', leaf=True),
                        ),
                    ),
                ),
            ),
            dpgc.CollapsingHeader('Collapsing Header > Plots', classes=['collapsed_item'], )(
                dpgc.Group(horizontal=True)(
                    plot_1=dpgc.Plot(width=250, crosshairs=True)(
                        dpgc.PlotAxis(dpg.mvXAxis, label='x'),
                        dpgc.PlotAxis(dpg.mvYAxis, label='cos(x) - .5')(
                            dpgc.BarSeries(x_data, y1_data),
                        ),
                        dpgc.PlotAxis(dpg.mvYAxis, label='sin(x)')(
                            dpgc.LineSeries(x_data, y2_data, ),
                            dpgc.LineSeries(x_data, y3_data, ),
                            dpgc.ErrorSeries(x_data, y4_data, negative=x_data, positive=x_data),
                            # dpgc.PlotLegend('Plot Legend 1'),
                        ),
                        dpgc.PlotLegend('Plot Legend 2'),
                    ),
                    plot_2=dpgc.Plot(width=250)(
                        dpgc.PlotAxis(dpg.mvXAxis, label='x'),
                        dpgc.PlotAxis(dpg.mvYAxis, label='pie axis')(
                            dpgc.PieSeries(0.5, 0.5, 0.5, (.05, .1, .15, .2, .2, .3), (0, 1, 2, 3, 4, 5)),
                        ),
                    ),
                ),
            ),
            dpgc.CollapsingHeader('Collapsing Header > Nodes', classes=['collapsed_item'], )(
                node_editor = dpgc.NodeEditor(height=200, width=550)(
                    dpgc.Node('Node 1', pos=(50, 20))(
                        dpgc.NodeAttribute('Node Attribute 1.1')(
                            dpgc.InputFloat('Float', width=100),
                        ),
                        node_attribute_out=dpgc.NodeAttribute('Node Attribute 1.2', attribute_type=dpg.mvNode_Attr_Output)(
                            dpgc.InputInt('Int', width=100),
                        ),
                    ),
                    dpgc.Node('Node 2', pos=(250, 50))(
                        node_attribute_in=dpgc.NodeAttribute('Node Attribute 2.1')(
                            dpgc.InputFloat('Float', width=100),
                        ),
                    ),
                ),
            ),
        )
        self.render()

        self.find('node_editor')(
            dpgc.NodeLink(
                self.find('node_attribute_out'),
                self.find('node_attribute_in'),
            ),
        )

    def toggle_collapsed_items(self):
        items = self.find_by_class('collapsed_item')
        for item in items:
            item.value = not item.value


window = DemoWindow().render()

theme_controller = dpgt.load('catppuccin_frappe')
theme_controller.bind().show_gui()
theme_controller.bind_colormap(0, window.find('plot_1'))
theme_controller.bind_colormap(0, window.find('plot_2'))


dpg.create_viewport(title='DPGTheminator Demo', width=1400, height=900, )

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
