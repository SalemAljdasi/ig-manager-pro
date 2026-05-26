"""
IG Manager Pro - Main Application Entry Point
Dark-themed Instagram account management tool for Android
"""

import os
os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")

from kivy.config import Config
Config.set("graphics", "width",  "412")
Config.set("graphics", "height", "892")
Config.set("graphics", "resizable", "1")
Config.set("kivy",     "window_icon", "")

from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen

from screens.dashboard import DashboardScreen
from screens.scanner   import ScannerScreen
from screens.reports   import ReportsScreen
from screens.appeals   import AppealsScreen

KV = """
<RootLayout>:
    orientation: "vertical"

    MDScreenManager:
        id: screen_manager

    MDNavigationBar:
        id: nav_bar
        on_switch_tabs: root.switch_tab(*args)

        MDNavigationItem:
            icon: "view-dashboard"
            text: "Dashboard"
            badge_icon: ""

        MDNavigationItem:
            icon: "magnify"
            text: "Scanner"

        MDNavigationItem:
            icon: "chart-bar"
            text: "Reports"

        MDNavigationItem:
            icon: "shield-account"
            text: "Appeals"
"""

Builder.load_string(KV)

TAB_NAMES = ["dashboard", "scanner", "reports", "appeals"]


class RootLayout(MDScreen):
    def switch_tab(self, bar, item, item_icon, item_text):
        name = item_text.lower()
        if name in TAB_NAMES:
            self.ids.screen_manager.current = name


class IGManagerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette  = "DeepPurple"
        self.theme_cls.accent_palette   = "Cyan"
        self.theme_cls.theme_style      = "Dark"
        self.theme_cls.primary_hue      = "A200"

        root = RootLayout()

        sm = root.ids.screen_manager
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(ScannerScreen(name="scanner"))
        sm.add_widget(ReportsScreen(name="reports"))
        sm.add_widget(AppealsScreen(name="appeals"))
        sm.current = "dashboard"

        return root

    @staticmethod
    def hex_to_rgba(hex_color: str, alpha: float = 1.0):
        """Utility: convert hex to RGBA list usable by Kivy/KivyMD."""
        c = get_color_from_hex(hex_color)
        if len(c) == 3:
            c = (*c, alpha)
        return list(c)

    def on_start(self):
        """Request Android permissions on startup."""
        try:
            from android.permissions import (   # type: ignore
                request_permissions, Permission
            )
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.INTERNET,
            ])
        except ImportError:
            pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    IGManagerApp().run()
