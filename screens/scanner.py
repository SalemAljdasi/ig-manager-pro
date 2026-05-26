"""
IG Manager Pro - Scanner Screen
Single and bulk account scanning
"""

import threading
import os
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from models.database import Database
from core.checker import check_account, check_accounts_bulk
from assets.theme import *

Builder.load_string("""
<ScannerScreen>:
    name: "scanner"
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
                text: "Scanner"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: app.hex_to_rgba("#06b6d4")
                bold: True

        ScrollView:
            do_scroll_x: False
            MDBoxLayout:
                orientation: "vertical"
                padding: "16dp"
                spacing: "16dp"
                size_hint_y: None
                height: self.minimum_height

                # ── Single scan ──────────────────────────────────────────────
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
                        text: "Single Account Check"
                        font_style: "Subtitle1"
                        theme_text_color: "Custom"
                        text_color: app.hex_to_rgba("#06b6d4")
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDTextField:
                        id: username_input
                        hint_text: "@username"
                        mode: "rectangle"
                        line_color_focus: app.hex_to_rgba("#a855f7")
                        text_color_focus: app.hex_to_rgba("#f1f5f9")
                        hint_text_color_normal: app.hex_to_rgba("#475569")
                        size_hint_y: None
                        height: "48dp"

                    MDRaisedButton:
                        text: "CHECK ACCOUNT"
                        md_bg_color: app.hex_to_rgba("#a855f7")
                        size_hint_x: 1
                        on_release: root.single_scan()

                    MDCard:
                        id: result_card
                        orientation: "vertical"
                        padding: "12dp"
                        radius: [12,]
                        md_bg_color: app.hex_to_rgba("#1a1a2e")
                        size_hint_y: None
                        height: self.minimum_height

                        MDBoxLayout:
                            id: result_box
                            orientation: "vertical"
                            spacing: "6dp"
                            size_hint_y: None
                            height: self.minimum_height

                # ── Bulk scan ────────────────────────────────────────────────
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
                        text: "Bulk Scan (from .txt file)"
                        font_style: "Subtitle1"
                        theme_text_color: "Custom"
                        text_color: app.hex_to_rgba("#a855f7")
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDTextField:
                        id: file_path_input
                        hint_text: "/sdcard/Download/accounts.txt"
                        mode: "rectangle"
                        line_color_focus: app.hex_to_rgba("#06b6d4")
                        hint_text_color_normal: app.hex_to_rgba("#475569")
                        size_hint_y: None
                        height: "48dp"

                    MDBoxLayout:
                        spacing: "12dp"
                        size_hint_y: None
                        height: "48dp"

                        MDRaisedButton:
                            text: "BROWSE FILE"
                            md_bg_color: app.hex_to_rgba("#1a1a2e")
                            size_hint_x: 0.4
                            on_release: root.browse_file()

                        MDRaisedButton:
                            id: bulk_btn
                            text: "START BULK SCAN"
                            md_bg_color: app.hex_to_rgba("#06b6d4")
                            size_hint_x: 0.6
                            on_release: root.bulk_scan()

                    MDLinearProgressIndicator:
                        id: progress_bar
                        value: 0
                        color: app.hex_to_rgba("#a855f7")
                        size_hint_y: None
                        height: "6dp"

                    MDLabel:
                        id: progress_label
                        text: "Idle"
                        theme_text_color: "Custom"
                        text_color: app.hex_to_rgba("#475569")
                        font_style: "Caption"
                        size_hint_y: None
                        height: "20dp"

                    ScrollView:
                        size_hint_y: None
                        height: "200dp"
                        do_scroll_x: False

                        MDLabel:
                            id: bulk_log
                            text: ""
                            theme_text_color: "Custom"
                            text_color: app.hex_to_rgba("#94a3b8")
                            font_style: "Body2"
                            size_hint_y: None
                            height: self.texture_size[1]
                            text_size: self.width, None
""")


STATUS_ICONS = {
    "active":    ("✅", "#22c55e"),
    "disabled":  ("🚫", "#ef4444"),
    "shadowban": ("⚠️", "#f97316"),
    "private":   ("🔒", "#a855f7"),
    "unknown":   ("❓", "#94a3b8"),
}


def _row(label, value, color="#94a3b8"):
    row = MDBoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(24),
        spacing=dp(8),
    )
    row.add_widget(MDLabel(
        text=label,
        theme_text_color="Custom",
        text_color=get_color_from_hex("#475569"),
        font_style="Caption",
        size_hint_x=0.45,
    ))
    row.add_widget(MDLabel(
        text=str(value),
        theme_text_color="Custom",
        text_color=get_color_from_hex(color),
        font_style="Caption",
        bold=True,
        size_hint_x=0.55,
    ))
    return row


class ScannerScreen(MDScreen):
    _stop_flag = False
    _scanning  = False

    def single_scan(self):
        username = self.ids.username_input.text.strip().lstrip("@")
        if not username:
            self._show_result({"error": "Please enter a username."})
            return
        self._show_result({"status": "checking", "username": username})
        threading.Thread(
            target=self._do_single,
            args=(username,),
            daemon=True,
        ).start()

    def _do_single(self, username):
        result = check_account(username)
        db = Database()
        if result.get("status") != "unknown" or not result.get("error"):
            db.save_scan(result)
        Clock.schedule_once(lambda dt: self._show_result(result), 0)

    def _show_result(self, result):
        box = self.ids.result_box
        box.clear_widgets()

        status = result.get("status", "unknown")
        icon, color = STATUS_ICONS.get(status, ("❓", "#94a3b8"))

        if result.get("error") and status == "unknown":
            box.add_widget(MDLabel(
                text=f"Error: {result['error']}",
                theme_text_color="Custom",
                text_color=get_color_from_hex("#ef4444"),
                font_style="Body2",
                size_hint_y=None,
                height=dp(32),
            ))
            return

        # Status row
        status_row = MDBoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        status_row.add_widget(MDLabel(
            text=icon,
            size_hint_x=None, width=dp(28),
            font_style="H6",
        ))
        status_row.add_widget(MDLabel(
            text=f"@{result.get('username', '')}  —  {status.upper()}",
            theme_text_color="Custom",
            text_color=get_color_from_hex(color),
            font_style="Subtitle1",
            bold=True,
        ))
        box.add_widget(status_row)

        # Details
        if result.get("full_name"):
            box.add_widget(_row("Full Name",  result["full_name"]))
        box.add_widget(_row("Followers",  f"{result.get('followers', 0):,}", "#22c55e"))
        box.add_widget(_row("Following",  f"{result.get('following', 0):,}"))
        box.add_widget(_row("Posts",      f"{result.get('posts', 0):,}"))
        box.add_widget(_row("Private",    "Yes" if result.get("is_private")  else "No",
                            "#a855f7" if result.get("is_private") else "#475569"))
        box.add_widget(_row("Verified",   "Yes" if result.get("is_verified") else "No",
                            "#06b6d4" if result.get("is_verified") else "#475569"))
        box.add_widget(_row("Shadowban",  "Detected" if result.get("shadowban") else "None",
                            "#f97316" if result.get("shadowban") else "#475569"))

    # ── Bulk ──────────────────────────────────────────────────────────────────

    def browse_file(self):
        try:
            from android.storage import primary_external_storage_path  # type: ignore
            base = primary_external_storage_path()
        except ImportError:
            base = os.path.expanduser("~")
        self.ids.file_path_input.text = os.path.join(base, "Download", "accounts.txt")

    def bulk_scan(self):
        if self._scanning:
            self._stop_flag = True
            self.ids.bulk_btn.text = "START BULK SCAN"
            self._scanning = False
            return

        file_path = self.ids.file_path_input.text.strip()
        if not file_path or not os.path.exists(file_path):
            self.ids.progress_label.text = "File not found."
            return

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [ln.strip().lstrip("@") for ln in f if ln.strip()]

        if not lines:
            self.ids.progress_label.text = "File is empty."
            return

        self._stop_flag = False
        self._scanning  = True
        self.ids.bulk_btn.text     = "⛔ STOP"
        self.ids.bulk_log.text     = ""
        self.ids.progress_bar.value= 0
        self.ids.progress_label.text = f"0 / {len(lines)}"

        threading.Thread(
            target=self._do_bulk,
            args=(lines,),
            daemon=True,
        ).start()

    def _do_bulk(self, usernames):
        db    = Database()
        total = len(usernames)

        def progress_cb(current, total, result):
            status = result.get("status", "unknown")
            icon, _= STATUS_ICONS.get(status, ("❓", "#94a3b8"))
            line   = f"{icon} @{result.get('username','')}: {status}"
            if result.get("followers"):
                line += f" | {result['followers']:,} followers"
            if result.get("error"):
                line += f" | ERR: {result['error']}"

            def update(dt):
                self.ids.progress_bar.value  = current / total
                self.ids.progress_label.text = f"{current} / {total}"
                self.ids.bulk_log.text       += line + "\n"

            Clock.schedule_once(update, 0)
            if result.get("status") not in ("unknown",) or not result.get("error"):
                db.save_scan(result)

        check_accounts_bulk(
            usernames,
            progress_cb=progress_cb,
            stop_flag=lambda: self._stop_flag,
        )

        def done(dt):
            self._scanning = False
            self.ids.bulk_btn.text = "START BULK SCAN"
            self.ids.progress_label.text = "Done!"

        Clock.schedule_once(done, 0)
