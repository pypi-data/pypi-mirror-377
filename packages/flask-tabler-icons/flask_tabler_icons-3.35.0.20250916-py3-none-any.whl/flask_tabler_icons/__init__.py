#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from typing import Any

from flask import Flask
from flask_topassets import TopAssets

# version is same as tabler-icons
__version__ = "3.35.0.20250916"
CLASS_NAME = "TablerIcons"


class TablerIcons(TopAssets):
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        app.config.setdefault("TABLER_ICON_SIZE", 24)
        self.prepare(app, "tabler_icons")
        filled = "tabler-sprite-filled.svg"
        normal = "tabler-sprite-nostroke.svg"
        self.bundle_files("filled", files=filled, output=filled)
        self.bundle_files("normal", files=normal, output=normal)
        self.get_url("filled")
        self.get_url("normal")
