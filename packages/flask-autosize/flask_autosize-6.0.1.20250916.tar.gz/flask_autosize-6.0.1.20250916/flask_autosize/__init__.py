#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from typing import Any

from flask import Flask
from flask_topassets import TopAssets

# version is same as autosize, with revision appdended
__version__ = "6.0.1.20250916"

# used for plugins importing
CLASS_NAME = "Autosize"


class Autosize(TopAssets):
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.prepare(app)
        self.bundle_js("autosize.min.js")
