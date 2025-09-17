### DPGTheminator

*ALPHA* This project is in it's infancy.

Currently, and possibly forever, only supports _colors_.  No other DPG theme
settings are supported.

```python
import dpgtheminator

dpgtheminator.load('light').bind()
```

To customize a theme visually:

```python
dpgtheminator.load('light').bind().show_gui()
```

From the gui, you can *save* your customized theme.  Then, once satisfied,
instead of loading 'light' load your saved path, and omit the .show_gui() call.
