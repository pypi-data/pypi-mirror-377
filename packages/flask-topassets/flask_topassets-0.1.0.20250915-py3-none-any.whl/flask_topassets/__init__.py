#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from typing import Any

from flask import Blueprint, Flask
from flask_assets import Bundle, Environment
from markupsafe import Markup

__version__ = "0.1.0.20250915"


class TopAssets:
    def prepare(self, app: Flask, plugin: str = "", register: bool = True) -> None:
        if not plugin:
            plugin = self.__class__.__name__.lower()

        self.plugin = plugin
        self.app = app
        if not hasattr(app, "extensions"):
            app.extensions = {}

        if not hasattr(app, "assets"):
            app.assets = Environment(app)

        app.extensions[plugin] = self
        self.bp = bp = Blueprint(
            plugin,
            f"flask_{plugin}",
            static_folder=f"static/{plugin}",
            static_url_path=f"/{plugin}{app.static_url_path}",
            template_folder="templates",
        )
        app.jinja_env.globals[plugin] = self
        if register:
            app.register_blueprint(bp)

        # use webassets for hosting
        # self.assets = Environment(app)
        self.bundled = {}
        self.bundled_js = []
        self.bundled_css = []
        self.assets = app.assets

    def bundle_js(self, files: list | str, output: str = "", **kwargs: Any) -> None:
        self.bundle_files("js", files, output, **kwargs)

    def bundle_css(self, files: list | str, output: str = "", **kwargs: Any) -> None:
        self.bundle_files("css", files, output, **kwargs)

    def bundle_files(
        self,
        kind: str,
        files: list | str,
        output: str = "",
        filters: str = "",
        key: str = "",
        collect: bool = True,
    ) -> None:
        if (key or kind) in self.bundled:
            return

        out = output or f"packed.{kind}"
        kw = dict(filters=filters) if filters else {}
        bun = Bundle(
            *self.unpack_files([files] if isinstance(files, str) else files),
            output=f"gen/{self.plugin}/{out}",
            **kw,
        )
        self.assets.register(f"{self.plugin}_{key or kind}", bun)
        self.bundled[key or kind] = bun
        if collect:
            if kind == "js":
                self.bundled_js.append(key or kind)
            else:
                self.bundled_css.append(key or kind)

    def unpack_files(self, files: list) -> list:
        return [f"{self.plugin}/{f}" for f in files]

    def get_url(self, name: str) -> str:
        if name in self.bundled:
            bun = self.bundled[name]
        else:
            bun = self.assets[f"{self.plugin}_{name}"]

        return bun.urls()[0]

    def get_assets_path(self, name: str, kind: str = "") -> Markup:
        url = self.get_url(name)
        if (kind or name) == "css":
            return Markup(f'<link rel="stylesheet" href="{url}" />')

        return Markup(f'<script type="text/javascript" src="{url}"></script>')

    def get_path(self, *args: Any, **kwargs: Any) -> Markup:
        return self.get_assets_path(*args, **kwargs)
