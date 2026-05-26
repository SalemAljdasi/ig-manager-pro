import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout

from models.database import init_db
from screens.dashboard import DashboardScreen
from screens.scanner import ScannerScreen
from screens.reports import ReportsScreen
from screens.appeals import AppealsScreen
from screens.recovery import RecoveryScreen
from screens.verification import VerificationScreen
from screens.settings import SettingsScreen
from screens.ai_chat import AIChatScreen

KV = """
<RootLayout>:
    orientation: "vertical"

MDBottomNavigationItem:
    name: "dashboard"
    text: "لوحة التحكم"
    icon: "view-dashboard"

MDBottomNavigationItem:
    name: "scanner"
    text: "الفاحص"
    icon: "magnify"
"""


class IGManagerApp(MDApp):
    def build(self):
        # Initialize DB
        init_db()

        # Theme setup
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Cyan"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_hue = "500"

        # Window settings
        Window.softinput_mode = "below_target"

        # Build navigation
        nav = MDBottomNavigation(
            panel_color=(0.07, 0.07, 0.18, 1),
            text_color_normal=(0.58, 0.58, 0.70, 1),
            text_color_active=(0.655, 0.231, 0.929, 1),
        )

        # Screen definitions: (tab_name, icon, arabic_label, ScreenClass)
        screens_config = [
            ("dashboard", "view-dashboard", "لوحة التحكم", DashboardScreen),
            ("scanner", "magnify-scan", "الفاحص", ScannerScreen),
            ("reports", "file-chart", "التقارير", ReportsScreen),
            ("appeals", "file-document-edit", "الاستئنافات", AppealsScreen),
            ("recovery", "lock-reset", "الاسترداد", RecoveryScreen),
            ("verification", "check-decagram", "التوثيق", VerificationScreen),
            ("settings", "cog", "الإعدادات", SettingsScreen),
            ("ai_chat", "robot", "المساعد", AIChatScreen),
        ]

        for tab_name, icon, label, ScreenClass in screens_config:
            item = MDBottomNavigationItem(
                name=tab_name,
                text=label,
                icon=icon,
            )
            screen = ScreenClass()
            item.add_widget(screen)
            nav.add_widget(item)

        return nav

    def on_start(self):
        Window.clearcolor = (0.04, 0.04, 0.10, 1)


if __name__ == "__main__":
    IGManagerApp().run()
