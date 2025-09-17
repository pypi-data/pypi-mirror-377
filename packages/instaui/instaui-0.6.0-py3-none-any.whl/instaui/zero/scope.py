from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Optional, Union
from contextvars import copy_context
from instaui.runtime import new_app_slot, reset_app_slot
from instaui.systems import file_path_system
from instaui.runtime.utils import init_base_scope
from .func import to_html, to_html_str, get_template_model
from instaui.template.zero_template import ZeroTemplateModel
from instaui.launch_collector import get_launch_collector


class ZeroCaller:
    def __init__(
        self,
        *,
        icons_svg_path: Optional[Union[str, Path]] = None,
    ):
        self._mate = {}

        if icons_svg_path is not None:
            icons_svg_path = file_path_system.get_caller_path(icons_svg_path)
            self._mate["icons_svg_code"] = icons_svg_path.read_text(encoding="utf-8")

    def to_html(self, render_fn: Callable[..., Any], *, file: Union[str, Path]):
        file = file_path_system.get_caller_path(file)

        with _run(self._mate):
            copy_context().run(render_fn)
            return to_html(file)

    def to_html_str(self, render_fn: Callable[..., Any]):
        with _run(self._mate):
            copy_context().run(render_fn)
            return to_html_str()

    def to_debug_report(self, render_fn: Callable[..., Any], *, file: Union[str, Path]):
        file = file_path_system.get_caller_path(file)

        # Custom component dependencies must be recorded only during actual execution
        with _run(self._mate):
            copy_context().run(render_fn)
            result_html_str = to_html_str()

        model = get_template_model()
        with _run({"merge_global_resources": False}):
            _create_debug_report(model, result_html_str)
            to_html(file.resolve().absolute())


@contextmanager
def _run(mate: dict):
    app, app_token = new_app_slot("zero", app_meta=mate)
    init_base_scope(app)

    _events = [iter(event()) for event in get_launch_collector().page_init_lifespans]
    for event in _events:
        next(event)

    yield

    for event in _events:
        try:
            next(event)
        except StopIteration:
            pass

    assert app_token is not None
    reset_app_slot(app_token)


def _create_debug_report(model: ZeroTemplateModel, result_html_str: str):
    from instaui import ui, html

    no_exists_path_class = "ex-no-exists-path"

    def _path_exists_class(path: Path):
        return "" if path.exists() else no_exists_path_class

    ui.use_tailwind()

    ui.add_style(rf".{no_exists_path_class} {{background-color: red;color: white;}}")

    html_size = len(result_html_str.encode("utf-8")) / 1024 / 1024

    box_style = "border-2 border-gray-200 p-4 place-center gap-x-2"

    with ui.column().classes("gap-2"):
        # base info
        with ui.grid(columns="auto 1fr").classes(box_style):
            html.span("file size:")
            html.span(f"{html_size:.2f} MB")

        # import maps
        html.paragraph("import maps")

        rows = [
            ["vue", str(model.vue_js_code)],
            ["instaui", str(model.instaui_js_code)],
        ]

        for name, url in model.extra_import_maps.items():
            if isinstance(url, Path) and url.is_file():
                rows.append([name, str(url)])

        html.table(["name", "path"], rows).scoped_style(
            r"""
    table {
    outline: 1px solid black;
    }
    td, th {
    outline: 1px solid black;
    padding: 5px;
    }
    """,
            with_self=True,
        )

        # css links
        html.paragraph("css links")
        with ui.column().classes(box_style):
            for link in model.css_links:
                if isinstance(link, Path) and link.is_file():
                    html.span(str(link)).classes(_path_exists_class(link))

        # js links
        html.paragraph("js links")
        with ui.column().classes(box_style):
            for info in model.js_links:
                if isinstance(info.link, Path) and info.link.is_file():
                    html.span(str(info.link)).classes(_path_exists_class(info.link))

        # custom components
        html.paragraph("custom components")
        with ui.grid(columns="auto 1fr").classes(box_style):
            html.span("name")
            html.span("js file path")

            for info in model.vue_app_component:
                html.span(info.name)

                if isinstance(info.url, Path) and info.url.is_file():
                    html.span(str(info.url)).classes(_path_exists_class(info.url))
                else:
                    html.span("not file")
