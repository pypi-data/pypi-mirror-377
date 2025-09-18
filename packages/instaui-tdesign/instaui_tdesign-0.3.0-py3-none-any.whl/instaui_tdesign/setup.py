from pathlib import Path
from typing import Optional, Union, Literal
from instaui import ui
from instaui.dependencies.plugin_dependency import register_plugin
from instaui_tdesign.types import TLocale, TCustomizeLocale
from instaui_tdesign._settings import configure
from instaui_tdesign.consts import THEME_CSS_DIR

static_folder = Path(__file__).parent / "static"

tdesign_css = static_folder / "instaui-tdesign.css"
tdesign_esm_js = static_folder / "instaui-tdesign.js"


def _register_tdesign():
    register_plugin("InstauiTDesign", esm=tdesign_esm_js, css=[tdesign_css])


def use(
    *,
    locale: ui.TMaybeRef[Union[TLocale, TCustomizeLocale]] = "en-US",
    theme: Optional[Literal["default", "green", "violet"]] = None,
):
    """Use tdesign ui.

    Args:
        locale (ui.TMaybeRef[Union[TLocale, TCustomizeLocale]], optional): The locale of tdesign ui. Defaults to "en-US".

    Examples:
    .. code-block:: python
        from instaui import ui
        import instaui_tdesign as td

        td.use()

        @ui.page("/")
        def index_page():
            td.input(placeholder="input")
    """

    _register_tdesign()
    configure(locale=locale)
    if theme is not None:
        ui.add_css_link(THEME_CSS_DIR / f"theme-{theme}.css")
