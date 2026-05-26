from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.spinner import MDSpinner
from models.database import get_stats, get_recent_scans, init_db
from assets.theme import STATUS_LABELS_AR, STATUS_COLORS, COLORS


class StatCard(MDCard):
    def __init__(self, title, value, color, icon="", **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0.07, 0.07, 0.16, 1)
        self.radius = [dp(16)]
        self.padding = dp(16)
        self.size_hint_y = None
        self.height = dp(100)
        self.elevation = 4
        layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        icon_label = MDLabel(
            text=f"{icon}",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(36),
        )
        val_label = MDLabel(
            text=str(value),
            font_style="H4",
            halign="center",
            theme_text_color="Custom",
            text_color=self._hex_to_rgb(color),
            bold=True,
            size_hint_y=None,
            height=dp(36),
        )
        title_label = MDLabel(
            text=title,
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary",
        )
        layout.add_widget(icon_label)
        layout.add_widget(val_label)
        layout.add_widget(title_label)
        self.add_widget(layout)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
        return r, g, b, 1


class ScanRowItem(MDBoxLayout):
    def __init__(self, scan_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(48)
        self.padding = [dp(12), dp(4)]
        self.spacing = dp(8)
        with self.canvas.before:
            Color(0.07, 0.07, 0.16, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._update_rect, size=self._update_rect)

        username = scan_data.get("username", "")
        status = scan_data.get("status", "unknown")
        status_label = STATUS_LABELS_AR.get(status, "غير معروف")
        status_color = STATUS_COLORS.get(status, "#475569")
        r, g, b = [int(status_color.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4)]

        self.add_widget(MDLabel(
            text=f"@{username}",
            font_style="Body2",
            theme_text_color="Primary",
            size_hint_x=0.5,
        ))
        self.add_widget(MDLabel(
            text=status_label,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(r, g, b, 1),
            size_hint_x=0.3,
            halign="center",
        ))
        followers = scan_data.get("followers", 0)
        self.add_widget(MDLabel(
            text=f"{followers:,}",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_x=0.2,
            halign="center",
        ))

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "dashboard"
        self._build()

    def _build(self):
        root = MDBoxLayout(orientation="vertical", spacing=0)

        # Header
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(8)],
            md_bg_color=(0.07, 0.07, 0.18, 1),
        )
        header.add_widget(MDLabel(
            text="🌟 لوحة التحكم",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            bold=True,
        ))
        refresh_btn = MDIconButton(icon="refresh", on_release=lambda x: self.refresh())
        header.add_widget(refresh_btn)
        root.add_widget(header)

        scroll = ScrollView()
        self.content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(12),
            size_hint_y=None,
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.content.clear_widgets()
        init_db()
        stats = get_stats()
        recent = get_recent_scans(15)

        # Stats title
        self.content.add_widget(MDLabel(
            text="📊 إحصائيات الحسابات",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            size_hint_y=None,
            height=dp(36),
        ))

        # Stats grid
        grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(340),
        )
        stat_items = [
            ("حسابات نشطة", stats.get("active", 0), "#10B981", "✅"),
            ("معطلة", stats.get("disabled", 0), "#EF4444", "🔴"),
            ("شادوبان", stats.get("shadowban", 0), "#F59E0B", "⚠️"),
            ("خاصة", stats.get("private", 0), "#06B6D4", "🔒"),
            ("مخترقة", stats.get("hacked", 0), "#EC4899", "🚨"),
            ("موثقة", stats.get("verified", 0), "#7C3AED", "✔️"),
        ]
        for title, value, color, icon in stat_items:
            grid.add_widget(StatCard(title, value, color, icon))
        self.content.add_widget(grid)

        # Total
        total_card = MDCard(
            md_bg_color=(0.1, 0.07, 0.2, 1),
            radius=[dp(14)],
            padding=dp(12),
            size_hint_y=None,
            height=dp(60),
            elevation=3,
        )
        total_box = MDBoxLayout(orientation="horizontal")
        total_box.add_widget(MDLabel(
            text="إجمالي الفحوصات",
            font_style="Subtitle1",
            bold=True,
        ))
        total_box.add_widget(MDLabel(
            text=str(stats.get("total", 0)),
            font_style="H5",
            halign="right",
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            bold=True,
        ))
        total_card.add_widget(total_box)
        self.content.add_widget(total_card)

        # Recent scans title
        self.content.add_widget(MDLabel(
            text="🕐 آخر 15 عملية فحص",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            size_hint_y=None,
            height=dp(36),
        ))

        # Column headers
        header_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32),
            padding=[dp(12), 0],
        )
        for text, hint in [("المستخدم", 0.5), ("الحالة", 0.3), ("متابعون", 0.2)]:
            header_row.add_widget(MDLabel(
                text=text,
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_x=hint,
                halign="center",
            ))
        self.content.add_widget(header_row)

        if recent:
            for scan in recent:
                self.content.add_widget(ScanRowItem(scan))
        else:
            self.content.add_widget(MDLabel(
                text="لا توجد فحوصات بعد. ابدأ بفحص حسابات من شاشة الفاحص.",
                font_style="Body2",
                theme_text_color="Secondary",
                halign="center",
                size_hint_y=None,
                height=dp(80),
            ))
