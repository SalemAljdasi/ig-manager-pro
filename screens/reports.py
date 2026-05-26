"""
IG Manager Pro - Reports Screen
View, filter, export and manage saved scan results
"""

import os
import json
from datetime import datetime
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from models.database import Database
from assets.theme import *

Builder.load_string("""
<ReportsScreen>:
    name: "reports"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: app.hex_to_rgba("#0a0a0f")

        # Header
        MDBoxLayout:
            size_hint_y: None
            height: "64dp"
            padding: ["20dp", "8dp"]
            spacing: "8dp"
            md_bg_color: app.hex_to_rgba("#12121a")
            MDLabel:
                text: "Reports"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: app.hex_to_rgba("#22c55e")
                bold: True
                size_hint_x: 1

        # Filter bar
        MDBoxLayout:
            size_hint_y: None
            height: "52dp"
            padding: ["12dp", "6dp"]
            spacing: "8dp"
            md_bg_color: app.hex_to_rgba("#12121a")

            MDRaisedButton:
                text: "All"
                md_bg_color: app.hex_to_rgba("#1a1a2e")
                font_size: "12sp"
                size_hint_x: None
                width: "56dp"
                on_release: root.filter_scans("all")

            MDRaisedButton:
                text: "✅ Active"
                md_bg_color: app.hex_to_rgba("#1a1a2e")
                font_size: "12sp"
                size_hint_x: None
                width: "84dp"
                on_release: root.filter_scans("active")

            MDRaisedButton:
                text: "🚫 Off"
                md_bg_color: app.hex_to_rgba("#1a1a2e")
                font_size: "12sp"
                size_hint_x: None
                width: "72dp"
                on_release: root.filter_scans("disabled")

            MDRaisedButton:
                text: "⚠️ SB"
                md_bg_color: app.hex_to_rgba("#1a1a2e")
                font_size: "12sp"
                size_hint_x: None
                width: "64dp"
                on_release: root.filter_scans("shadowban")

            MDRaisedButton:
                text: "🔒 Prv"
                md_bg_color: app.hex_to_rgba("#1a1a2e")
                font_size: "12sp"
                size_hint_x: None
                width: "68dp"
                on_release: root.filter_scans("private")

        # Export buttons
        MDBoxLayout:
            size_hint_y: None
            height: "48dp"
            padding: ["12dp", "4dp"]
            spacing: "8dp"
            md_bg_color: app.hex_to_rgba("#0a0a0f")

            MDRaisedButton:
                text: "📄 Export HTML"
                md_bg_color: app.hex_to_rgba("#06b6d4")
                font_size: "12sp"
                on_release: root.export_html()

            MDRaisedButton:
                text: "📦 Export JSON"
                md_bg_color: app.hex_to_rgba("#a855f7")
                font_size: "12sp"
                on_release: root.export_json()

            MDRaisedButton:
                text: "🗑 Clear All"
                md_bg_color: app.hex_to_rgba("#ef4444")
                font_size: "12sp"
                on_release: root.confirm_clear()

        # Results count label
        MDLabel:
            id: count_label
            text: "Loading..."
            theme_text_color: "Custom"
            text_color: app.hex_to_rgba("#475569")
            font_style: "Caption"
            padding: ["16dp", "4dp"]
            size_hint_y: None
            height: "24dp"

        # Table header
        MDBoxLayout:
            size_hint_y: None
            height: "36dp"
            padding: ["12dp", "4dp"]
            md_bg_color: app.hex_to_rgba("#12121a")
            spacing: "4dp"

            MDLabel:
                text: "Status"
                theme_text_color: "Custom"
                text_color: app.hex_to_rgba("#94a3b8")
                font_style: "Caption"
                bold: True
                size_hint_x: 0.18

            MDLabel:
                text: "Username"
                theme_text_color: "Custom"
                text_color: app.hex_to_rgba("#94a3b8")
                font_style: "Caption"
                bold: True
                size_hint_x: 0.3

            MDLabel:
                text: "Followers"
                theme_text_color: "Custom"
                text_color: app.hex_to_rgba("#94a3b8")
                font_style: "Caption"
                bold: True
                size_hint_x: 0.22
                halign: "right"

            MDLabel:
                text: "Date"
                theme_text_color: "Custom"
                text_color: app.hex_to_rgba("#94a3b8")
                font_style: "Caption"
                bold: True
                size_hint_x: 0.3
                halign: "right"

        # Scrollable results list
        ScrollView:
            do_scroll_x: False
            MDBoxLayout:
                id: results_box
                orientation: "vertical"
                spacing: "2dp"
                size_hint_y: None
                height: self.minimum_height
""")

STATUS_META = {
    "active":    ("✅", "#22c55e"),
    "disabled":  ("🚫", "#ef4444"),
    "shadowban": ("⚠️", "#f97316"),
    "private":   ("🔒", "#a855f7"),
    "unknown":   ("❓", "#94a3b8"),
}


class ScanRow(MDBoxLayout):
    def __init__(self, scan: dict, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            padding=[dp(12), 0],
            spacing=dp(4),
            **kwargs,
        )
        status = scan.get("status", "unknown")
        icon, color = STATUS_META.get(status, ("❓", "#94a3b8"))
        date_str = scan.get("scanned_at", "")[:10]

        self.add_widget(MDLabel(
            text=icon,
            size_hint_x=0.18,
            font_style="Body2",
        ))
        self.add_widget(MDLabel(
            text=f"@{scan.get('username', '')}",
            theme_text_color="Custom",
            text_color=get_color_from_hex(color),
            font_style="Body2",
            bold=True,
            size_hint_x=0.3,
        ))
        self.add_widget(MDLabel(
            text=f"{scan.get('followers', 0):,}",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#94a3b8"),
            font_style="Caption",
            halign="right",
            size_hint_x=0.22,
        ))
        self.add_widget(MDLabel(
            text=date_str,
            theme_text_color="Custom",
            text_color=get_color_from_hex("#475569"),
            font_style="Caption",
            halign="right",
            size_hint_x=0.3,
        ))


def _export_dir():
    try:
        from android.storage import primary_external_storage_path  # type: ignore
        base = os.path.join(primary_external_storage_path(), "Download")
    except ImportError:
        base = os.path.expanduser("~")
    os.makedirs(base, exist_ok=True)
    return base


def _html_report(scans: list) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = ""
    for s in scans:
        status  = s.get("status", "unknown")
        _, color = STATUS_META.get(status, ("❓", "#94a3b8"))
        rows += f"""
        <tr>
          <td style="color:{color};">{status.upper()}</td>
          <td>@{s.get('username','')}</td>
          <td>{s.get('followers',0):,}</td>
          <td>{s.get('following',0):,}</td>
          <td>{s.get('posts',0):,}</td>
          <td>{'Yes' if s.get('is_private') else 'No'}</td>
          <td>{'Yes' if s.get('is_verified') else 'No'}</td>
          <td>{s.get('scanned_at','')[:16]}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>IG Manager Pro – Report</title>
<style>
  body{{background:#0a0a0f;color:#f1f5f9;font-family:Arial,sans-serif;padding:24px}}
  h1{{color:#a855f7}} h2{{color:#06b6d4}}
  table{{width:100%;border-collapse:collapse;margin-top:16px}}
  th{{background:#12121a;color:#94a3b8;padding:10px;text-align:left;border-bottom:2px solid #a855f7}}
  td{{padding:8px 10px;border-bottom:1px solid #1a1a2e}}
  tr:hover{{background:#12121a}}
  .badge{{padding:3px 10px;border-radius:12px;font-size:12px;font-weight:bold}}
</style>
</head>
<body>
<h1>IG Manager Pro</h1>
<h2>Scan Report – {now}</h2>
<p>Total accounts: <strong>{len(scans)}</strong></p>
<table>
  <thead>
    <tr>
      <th>Status</th><th>Username</th><th>Followers</th>
      <th>Following</th><th>Posts</th><th>Private</th>
      <th>Verified</th><th>Scanned At</th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>
<p style="margin-top:32px;color:#475569;font-size:12px">
  Generated by IG Manager Pro • {now}
</p>
</body>
</html>"""


class ReportsScreen(MDScreen):
    _current_filter = "all"
    _dialog = None

    def on_enter(self):
        self.filter_scans(self._current_filter)

    def filter_scans(self, status: str):
        self._current_filter = status
        db = Database()
        scans = db.get_all_scans(status)
        self._render(scans)

    def _render(self, scans):
        box = self.ids.results_box
        box.clear_widgets()
        self.ids.count_label.text = f"{len(scans)} result(s)"
        for scan in scans:
            box.add_widget(ScanRow(scan))
        if not scans:
            box.add_widget(MDLabel(
                text="No results found.",
                theme_text_color="Custom",
                text_color=get_color_from_hex("#475569"),
                font_style="Body2",
                size_hint_y=None,
                height=dp(48),
                halign="center",
            ))

    def export_html(self):
        db = Database()
        scans = db.get_all_scans()
        html = _html_report(scans)
        path = os.path.join(
            _export_dir(),
            f"igmanager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        self._toast(f"Exported: {path}")

    def export_json(self):
        db = Database()
        scans = db.get_all_scans()
        path = os.path.join(
            _export_dir(),
            f"igmanager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scans, f, ensure_ascii=False, indent=2)
        self._toast(f"Exported: {path}")

    def confirm_clear(self):
        self._dialog = MDDialog(
            title="Clear All Data",
            text="This will permanently delete ALL scan results. Are you sure?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self._dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=get_color_from_hex("#ef4444"),
                    on_release=self._do_clear,
                ),
            ],
        )
        self._dialog.open()

    def _do_clear(self, *_):
        if self._dialog:
            self._dialog.dismiss()
        Database().clear_all_scans()
        self.filter_scans("all")

    def _toast(self, msg: str):
        from kivymd.toast import toast
        toast(msg)
