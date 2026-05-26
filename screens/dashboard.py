"""
IG Manager Pro - Dashboard Screen
"""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from models.database import Database
from assets.theme import *

Builder.load_string("""
<StatCard>:
    orientation: "vertical"
    padding: "16dp"
    spacing: "8dp"
    radius: [16,]
    md_bg_color: app.hex_to_rgba("#12121a")
    size_hint_y: None
    height: "110dp"
    elevation: 4

<DashboardScreen>:
    name: "dashboard"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: app.hex_to_rgba("#0a0a0f")

        # ── Header ──────────────────────────────────────────────────────
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "64dp"
            padding: ["20dp", "8dp"]
            spacing: "12dp"
            md_bg_color: app.hex_to_rgba("#12121a")

            MDLabel:
                text: "IG Manager Pro"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: app.hex_to_rgba("#a855f7")
                bold: True
                size_hint_x: 1

            MDIconButton:
                icon: "refresh"
                theme_icon_color: "Custom"
                icon_color: app.hex_to_rgba("#06b6d4")
                on_release: root.refresh()

        # ── Scrollable body ─────────────────────────────────────────────
        ScrollView:
            do_scroll_x: False

            MDBoxLayout:
                id: body
                orientation: "vertical"
                padding: "16dp"
                spacing: "16dp"
                size_hint_y: None
                height: self.minimum_height

                # Stat cards row
                MDGridLayout:
                    id: stats_grid
                    cols: 2
                    spacing: "12dp"
                    size_hint_y: None
                    height: self.minimum_height

                # Charts placeholder
                MDCard:
                    id: chart_card
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [16,]
                    md_bg_color: app.hex_to_rgba("#12121a")
                    size_hint_y: None
                    height: "240dp"
                    elevation: 4

                    MDLabel:
                        text: "Account Status Distribution"
                        font_style: "Subtitle1"
                        theme_text_color: "Custom"
                        text_color: app.hex_to_rgba("#94a3b8")
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDBoxLayout:
                        id: chart_box
                        size_hint_y: 1

                # Recent scans
                MDCard:
                    id: recent_card
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "10dp"
                    radius: [16,]
                    md_bg_color: app.hex_to_rgba("#12121a")
                    size_hint_y: None
                    height: self.minimum_height
                    elevation: 4

                    MDLabel:
                        text: "Recent Scans"
                        font_style: "Subtitle1"
                        theme_text_color: "Custom"
                        text_color: app.hex_to_rgba("#94a3b8")
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDBoxLayout:
                        id: recent_box
                        orientation: "vertical"
                        spacing: "8dp"
                        size_hint_y: None
                        height: self.minimum_height
""")


class StatCard(MDCard):
    def __init__(self, label, value, color, icon, **kwargs):
        super().__init__(**kwargs)
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout

        top_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(28),
        )
        ico = MDLabel(
            text=icon,
            font_style="H5",
            theme_text_color="Custom",
            text_color=self._hex(color),
            size_hint_x=None,
            width=dp(32),
        )
        lbl = MDLabel(
            text=label,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=self._hex("#94a3b8"),
        )
        top_row.add_widget(ico)
        top_row.add_widget(lbl)

        val_lbl = MDLabel(
            text=str(value),
            font_style="H4",
            theme_text_color="Custom",
            text_color=self._hex(color),
            bold=True,
        )
        self.add_widget(top_row)
        self.add_widget(val_lbl)

    @staticmethod
    def _hex(hex_color):
        from kivy.utils import get_color_from_hex
        return get_color_from_hex(hex_color)


class RecentScanRow(MDBoxLayout):
    STATUS_ICONS = {
        "active":    "✅",
        "disabled":  "🚫",
        "shadowban": "⚠️",
        "private":   "🔒",
        "unknown":   "❓",
    }
    STATUS_COLORS = {
        "active":    "#22c55e",
        "disabled":  "#ef4444",
        "shadowban": "#f97316",
        "private":   "#a855f7",
        "unknown":   "#94a3b8",
    }

    def __init__(self, scan: dict, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
            **kwargs,
        )
        from kivy.utils import get_color_from_hex
        status = scan.get("status", "unknown")
        color  = get_color_from_hex(self.STATUS_COLORS.get(status, "#94a3b8"))

        icon = MDLabel(
            text=self.STATUS_ICONS.get(status, "❓"),
            size_hint_x=None,
            width=dp(28),
            font_style="Body1",
        )
        name = MDLabel(
            text=f"@{scan.get('username', '')}",
            theme_text_color="Custom",
            text_color=color,
            font_style="Body1",
            bold=True,
        )
        meta = MDLabel(
            text=f"{scan.get('followers', 0):,} followers",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#475569"),
            font_style="Caption",
            halign="right",
        )
        self.add_widget(icon)
        self.add_widget(name)
        self.add_widget(meta)


class DashboardScreen(MDScreen):
    def on_enter(self):
        self.refresh()

    def refresh(self):
        db    = Database()
        stats = db.get_stats()
        recents = db.get_recent_scans(10)
        self._update_stats(stats)
        self._update_chart(stats)
        self._update_recent(recents)

    def _update_stats(self, stats):
        grid = self.ids.stats_grid
        grid.clear_widgets()
        cards = [
            ("Active",    stats["active"],    "#22c55e", "✅"),
            ("Disabled",  stats["disabled"],  "#ef4444", "🚫"),
            ("Shadowban", stats["shadowban"], "#f97316", "⚠️"),
            ("Private",   stats["private"],   "#a855f7", "🔒"),
        ]
        for label, value, color, icon in cards:
            grid.add_widget(StatCard(label, value, color, icon))

    def _update_chart(self, stats):
        from kivy.graphics import Color, RoundedRectangle
        from kivy.utils import get_color_from_hex
        box = self.ids.chart_box
        box.clear_widgets()

        total = max(stats["total"], 1)
        bars = [
            ("Active",    stats["active"],    "#22c55e"),
            ("Disabled",  stats["disabled"],  "#ef4444"),
            ("Shadowban", stats["shadowban"], "#f97316"),
            ("Private",   stats["private"],   "#a855f7"),
        ]

        bar_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            padding=[dp(8), 0],
        )
        for label, count, color in bars:
            col = MDBoxLayout(orientation="vertical", spacing=dp(4))
            pct = count / total

            bar_outer = MDBoxLayout(
                size_hint_y=1,
                size_hint_x=None,
                width=dp(36),
            )
            bar_inner = MDCard(
                size_hint_x=1,
                size_hint_y=pct if pct > 0 else 0.02,
                md_bg_color=get_color_from_hex(color),
                radius=[8, 8, 0, 0],
            )
            bar_outer.add_widget(bar_inner)

            lbl_count = MDLabel(
                text=str(count),
                theme_text_color="Custom",
                text_color=get_color_from_hex(color),
                halign="center",
                font_style="Caption",
                bold=True,
                size_hint_y=None,
                height=dp(18),
            )
            lbl_name = MDLabel(
                text=label,
                theme_text_color="Custom",
                text_color=get_color_from_hex("#475569"),
                halign="center",
                font_style="Caption",
                size_hint_y=None,
                height=dp(16),
            )
            col.add_widget(bar_outer)
            col.add_widget(lbl_count)
            col.add_widget(lbl_name)
            bar_box.add_widget(col)

        box.add_widget(bar_box)

    def _update_recent(self, scans):
        box = self.ids.recent_box
        box.clear_widgets()
        if not scans:
            box.add_widget(MDLabel(
                text="No scans yet. Go to Scanner to start.",
                theme_text_color="Custom",
                text_color=[0.4, 0.4, 0.5, 1],
                font_style="Body2",
                size_hint_y=None,
                height=dp(40),
            ))
            return
        for scan in scans:
            box.add_widget(RecentScanRow(scan))
