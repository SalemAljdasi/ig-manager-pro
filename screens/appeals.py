"""
IG Manager Pro - Appeals (Support Hub) Screen
Generate bilingual official appeal letters
"""

import os
from datetime import datetime
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from models.database import Database
from core.appeals import generate_appeal, ISSUE_TYPES, INSTAGRAM_SUPPORT_URL
from assets.theme import *

Builder.load_string("""
<AppealsScreen>:
    name: "appeals"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: app.hex_to_rgba("#0a0a0f")

        # Header
        MDBoxLayout:
            size_hint_y: None
            height: "64dp"
            padding: ["20dp", "8dp"]
            md_bg_color: app.hex_to_rgba("#12121a")
            MDLabel:
                text: "Support Hub"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: app.hex_to_rgba("#ec4899")
                bold: True

        ScrollView:
            do_scroll_x: False
            MDBoxLayout:
                orientation: "vertical"
                padding: "16dp"
                spacing: "16dp"
                size_hint_y: None
                height: self.minimum_height

                # Form Card
                MDCard:
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [16,]
                    md_bg_color: app.hex_to_rgba("#12121a")
                    size_hint_y: None
                    height: self.minimum_height
                    elevation: 4

                    MDLabel:
                        text: "Account Information"
                        font_style: "Subtitle1"
                        theme_text_color: "Custom"
                        text_color: app.hex_to_rgba("#ec4899")
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDTextField:
                        id: username_f
                        hint_text: "Instagram Username (without @)"
                        mode: "rectangle"
                        line_color_focus: app.hex_to_rgba("#ec4899")
                        size_hint_y: None
                        height: "48dp"

                    MDTextField:
                        id: fullname_f
                        hint_text: "Full Legal Name"
                        mode: "rectangle"
                        line_color_focus: app.hex_to_rgba("#a855f7")
                        size_hint_y: None
                        height: "48dp"

                    MDTextField:
                        id: email_f
                        hint_text: "Email linked to account"
                        mode: "rectangle"
                        line_color_focus: app.hex_to_rgba("#06b6d4")
                        size_hint_y: None
                        height: "48dp"

                    MDBoxLayout:
                        spacing: "12dp"
                        size_hint_y: None
                        height: "48dp"

                        MDTextField:
                            id: year_f
                            hint_text: "Account Year (e.g. 2019)"
                            mode: "rectangle"
                            line_color_focus: app.hex_to_rgba("#a855f7")
                            size_hint_x: 0.5

                        MDTextField:
                            id: country_f
                            hint_text: "Country"
                            mode: "rectangle"
                            line_color_focus: app.hex_to_rgba("#a855f7")
                            size_hint_x: 0.5

                    # Issue type dropdown
                    MDRaisedButton:
                        id: issue_btn
                        text: "▼  Select Issue Type"
                        md_bg_color: app.hex_to_rgba("#1a1a2e")
                        size_hint_x: 1
                        on_release: root.open_issue_menu()

                    MDTextField:
                        id: detail_f
                        hint_text: "Describe the issue in detail..."
                        mode: "rectangle"
                        multiline: True
                        line_color_focus: app.hex_to_rgba("#ec4899")
                        size_hint_y: None
                        height: "120dp"

                    MDRaisedButton:
                        text: "⚡ GENERATE APPEAL"
                        md_bg_color: app.hex_to_rgba("#ec4899")
                        size_hint_x: 1
                        on_release: root.generate()

                # Output Card
                MDCard:
                    id: output_card
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [16,]
                    md_bg_color: app.hex_to_rgba("#12121a")
                    size_hint_y: None
                    height: self.minimum_height
                    elevation: 4

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "36dp"
                        spacing: "8dp"

                        MDLabel:
                            text: "Generated Appeal"
                            font_style: "Subtitle1"
                            theme_text_color: "Custom"
                            text_color: app.hex_to_rgba("#94a3b8")
                            bold: True

                        MDRaisedButton:
                            id: tab_ar_btn
                            text: "🇸🇦 Arabic"
                            md_bg_color: app.hex_to_rgba("#a855f7")
                            font_size: "12sp"
                            size_hint_x: None
                            width: "90dp"
                            on_release: root.show_tab("ar")

                        MDRaisedButton:
                            id: tab_en_btn
                            text: "🇺🇸 English"
                            md_bg_color: app.hex_to_rgba("#1a1a2e")
                            font_size: "12sp"
                            size_hint_x: None
                            width: "90dp"
                            on_release: root.show_tab("en")

                    ScrollView:
                        size_hint_y: None
                        height: "260dp"
                        do_scroll_x: False

                        MDLabel:
                            id: output_text
                            text: "Fill in the form above and tap Generate."
                            theme_text_color: "Custom"
                            text_color: app.hex_to_rgba("#94a3b8")
                            font_style: "Body2"
                            size_hint_y: None
                            height: self.texture_size[1]
                            text_size: self.width, None

                    # Action buttons
                    MDBoxLayout:
                        spacing: "8dp"
                        size_hint_y: None
                        height: "44dp"

                        MDRaisedButton:
                            text: "📋 Copy"
                            md_bg_color: app.hex_to_rgba("#1a1a2e")
                            font_size: "12sp"
                            on_release: root.copy_text()

                        MDRaisedButton:
                            text: "💾 Save TXT"
                            md_bg_color: app.hex_to_rgba("#a855f7")
                            font_size: "12sp"
                            on_release: root.save_txt()

                        MDRaisedButton:
                            text: "🌐 IG Support"
                            md_bg_color: app.hex_to_rgba("#06b6d4")
                            font_size: "12sp"
                            on_release: root.open_support_link()
""")

ISSUE_LABELS = {k: f"{v[0]} / {v[1]}" for k, v in ISSUE_TYPES.items()}


class AppealsScreen(MDScreen):
    _appeal_ar = ""
    _appeal_en = ""
    _current_tab = "ar"
    _issue_key = "disabled"
    _menu = None

    def open_issue_menu(self):
        items = [
            {
                "viewclass": "OneLineListItem",
                "text": label,
                "on_release": lambda x=key: self._set_issue(x),
            }
            for key, label in ISSUE_LABELS.items()
        ]
        self._menu = MDDropdownMenu(
            caller=self.ids.issue_btn,
            items=items,
            width_mult=4,
        )
        self._menu.open()

    def _set_issue(self, key: str):
        self._issue_key = key
        self.ids.issue_btn.text = f"▼  {ISSUE_LABELS.get(key, key)}"
        if self._menu:
            self._menu.dismiss()

    def generate(self):
        data = {
            "username":     self.ids.username_f.text.strip().lstrip("@"),
            "full_name":    self.ids.fullname_f.text.strip(),
            "email":        self.ids.email_f.text.strip(),
            "year_created": self.ids.year_f.text.strip(),
            "country":      self.ids.country_f.text.strip(),
            "issue_type":   self._issue_key,
            "issue_detail": self.ids.detail_f.text.strip(),
        }

        if not data["username"]:
            self._toast("Please enter a username.")
            return

        result = generate_appeal(data)
        self._appeal_ar = result["appeal_ar"]
        self._appeal_en = result["appeal_en"]

        # Save to DB
        data.update(result)
        Database().save_appeal(data)

        self.show_tab(self._current_tab)

    def show_tab(self, tab: str):
        self._current_tab = tab
        if tab == "ar":
            self.ids.output_text.text      = self._appeal_ar or "No Arabic appeal generated yet."
            self.ids.tab_ar_btn.md_bg_color = self._hex("#a855f7")
            self.ids.tab_en_btn.md_bg_color = self._hex("#1a1a2e")
        else:
            self.ids.output_text.text      = self._appeal_en or "No English appeal generated yet."
            self.ids.tab_ar_btn.md_bg_color = self._hex("#1a1a2e")
            self.ids.tab_en_btn.md_bg_color = self._hex("#06b6d4")

    def copy_text(self):
        text = self.ids.output_text.text
        if not text:
            return
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            self._toast("Copied to clipboard!")
        except Exception:
            self._toast("Copy not supported on this device.")

    def save_txt(self):
        text = self.ids.output_text.text
        if not text or "Fill in" in text:
            self._toast("Generate an appeal first.")
            return
        try:
            from android.storage import primary_external_storage_path  # type: ignore
            base = os.path.join(primary_external_storage_path(), "Download")
        except ImportError:
            base = os.path.expanduser("~")
        os.makedirs(base, exist_ok=True)
        tab  = "AR" if self._current_tab == "ar" else "EN"
        path = os.path.join(
            base,
            f"appeal_{tab}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        self._toast(f"Saved: {path}")

    def open_support_link(self):
        try:
            from android.permissions import request_permissions, Permission  # type: ignore
        except ImportError:
            pass
        try:
            import webbrowser
            webbrowser.open(INSTAGRAM_SUPPORT_URL)
        except Exception:
            self._toast("Could not open browser.")

    @staticmethod
    def _hex(h: str):
        return get_color_from_hex(h)

    def _toast(self, msg: str):
        from kivymd.toast import toast
        toast(msg)
