#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from flask import Flask
from flask_topassets import TopAssets

# version is same as sweetalert2js, with revision appdended
__version__ = "11.23.0.20250916"

# used for plugins importing
CLASS_NAME = "Sweetalert2"

SWEETALERT_ICON_MAPS = dict(warn="warning", danger="error")


class Sweetalert2(TopAssets):
    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        app.config.setdefault("SWEETALERT2_AUTOCLOSE_POS", "top-end")
        app.config.setdefault("SWEETALERT2_AUTOCLOSE_DELAY", 1500)  # ms
        app.config.setdefault("SWEETALERT2_AUTOCLOSE_CATEGORY", ["info", "success"])

        self.prepare(app, register=False)
        self.setup_filters(app)
        app.register_blueprint(self.bp)

        self.bundle_js("sweetalert2.all.min.js")
        self.bundle_js("helpers.js", key="helpers", output="helpers.js")
        self.bundle_css("sweetalert2.min.css")
        [self.get_url(k) for k in ("js", "css", "helpers")]

    def setup_filters(self, app: Flask) -> None:
        def can_autoclose_flash(category: str) -> bool:
            return category in app.config["SWEETALERT2_AUTOCLOSE_CATEGORY"]

        def get_autoclose_delay(category: str) -> int:
            if can_autoclose_flash(category):
                return app.config["SWEETALERT2_AUTOCLOSE_DELAY"] or 0

            return 0

        @app.template_filter("get_sweet_icon")
        def get_sweet_icon(category: str) -> str:
            return SWEETALERT_ICON_MAPS.get(category, category)

        @app.template_filter("get_autoclose_pos")
        def get_alert_pos(category: str) -> str:
            if get_autoclose_delay(category):
                return app.config["SWEETALERT2_AUTOCLOSE_POS"]

            return "center"

        app.jinja_env.filters["can_autoclose_flash"] = can_autoclose_flash
        app.jinja_env.filters["get_autoclose_delay"] = get_autoclose_delay
