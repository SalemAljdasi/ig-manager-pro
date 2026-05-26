import threading
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from models.database import get_all_scans, clear_all, export_to_json, export_to_csv, export_to_html
from assets.theme import STATUS_LABELS_AR, STATUS_COLORS


class ReportsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "reports"
        self.dialog = None
        self.current_filter = "all"
        self.current_search = ""
        self._build()

    def _build(self):
        root = MDBoxLayout(orientation="vertical")

        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(8)],
            md_bg_color=(0.07, 0.07, 0.18, 1),
        )
        header.add_widget(MDLabel(
            text="📋 التقارير",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            bold=True,
        ))
        refresh_btn = MDIconButton(icon="refresh", on_release=lambda x: self.load_data())
        header.add_widget(refresh_btn)
        root.add_widget(header)

        # Search & Filter
        controls = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(110),
            padding=dp(12),
            spacing=dp(8),
            md_bg_color=(0.07, 0.07, 0.16, 1),
        )
        self.search_field = MDTextField(
            hint_text="🔎 بحث باسم المستخدم",
            mode="rectangle",
            size_hint_y=None,
            height=dp(46),
        )
        self.search_field.bind(text=self.on_search)
        controls.add_widget(self.search_field)

        filter_row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(40))
        filter_items = [
            ("الكل", "all"), ("نشط", "active"), ("معطل", "disabled"),
            ("شادوبان", "shadowban"), ("خاص", "private"), ("مخترق", "hacked"),
        ]
        for label, val in filter_items:
            btn = MDFlatButton(
                text=label,
                size_hint_x=None,
                width=dp(80),
                on_release=lambda x, v=val: self.set_filter(v),
            )
            filter_row.add_widget(btn)
        controls.add_widget(filter_row)
        root.add_widget(controls)

        # Export buttons
        export_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            padding=[dp(12), dp(4)],
            spacing=dp(8),
        )
        for label, action in [
            ("📄 HTML", self.export_html),
            ("📊 JSON", self.export_json),
            ("📑 CSV", self.export_csv),
            ("🗑️ مسح الكل", self.confirm_clear),
        ]:
            color = (0.937, 0.267, 0.267, 1) if "مسح" in label else (0.486, 0.227, 0.918, 1)
            btn = MDRaisedButton(text=label, md_bg_color=color, on_release=action)
            export_row.add_widget(btn)
        root.add_widget(export_row)

        scroll = ScrollView()
        self.table_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(8),
            size_hint_y=None,
        )
        self.table_box.bind(minimum_height=self.table_box.setter("height"))
        scroll.add_widget(self.table_box)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self.load_data()

    def on_search(self, instance, text):
        self.current_search = text
        self.load_data()

    def set_filter(self, val):
        self.current_filter = val
        self.load_data()

    def load_data(self):
        self.table_box.clear_widgets()
        scans = get_all_scans(
            limit=500,
            status_filter=self.current_filter if self.current_filter != "all" else None,
            search=self.current_search if self.current_search else None,
        )
        if not scans:
            self.table_box.add_widget(MDLabel(
                text="لا توجد نتائج.",
                font_style="Body2",
                theme_text_color="Secondary",
                halign="center",
                size_hint_y=None,
                height=dp(60),
            ))
            return

        # Header row
        header_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32),
            md_bg_color=(0.1, 0.07, 0.2, 1),
            padding=[dp(8), 0],
        )
        for text, hint in [("المستخدم", 0.35), ("الحالة", 0.25), ("متابعون", 0.2), ("التاريخ", 0.2)]:
            header_row.add_widget(MDLabel(
                text=text,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.655, 0.231, 0.929, 1),
                size_hint_x=hint,
                bold=True,
            ))
        self.table_box.add_widget(header_row)

        for s in scans:
            status = s.get("status", "unknown")
            status_label = STATUS_LABELS_AR.get(status, "غير معروف")
            color_hex = STATUS_COLORS.get(status, "#475569")
            r, g, b = [int(color_hex.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4)]
            date_str = s.get("scanned_at", "")[:10]

            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(40),
                padding=[dp(8), dp(4)],
            )
            row.add_widget(MDLabel(
                text=f"@{s.get('username', '')}",
                font_style="Body2",
                size_hint_x=0.35,
            ))
            row.add_widget(MDLabel(
                text=status_label,
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(r, g, b, 1),
                size_hint_x=0.25,
                halign="center",
            ))
            row.add_widget(MDLabel(
                text=f"{s.get('followers', 0):,}",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_x=0.2,
                halign="center",
            ))
            row.add_widget(MDLabel(
                text=date_str,
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_x=0.2,
                halign="center",
            ))
            self.table_box.add_widget(row)

    def export_html(self, *args):
        path = export_to_html()
        self._show_msg("تم التصدير", f"تم حفظ التقرير في:\n{path}")

    def export_json(self, *args):
        path = export_to_json()
        self._show_msg("تم التصدير", f"تم حفظ JSON في:\n{path}")

    def export_csv(self, *args):
        path = export_to_csv()
        if path:
            self._show_msg("تم التصدير", f"تم حفظ CSV في:\n{path}")
        else:
            self._show_msg("تنبيه", "لا توجد بيانات للتصدير.")

    def confirm_clear(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title="⚠️ تأكيد المسح",
            text="هل أنت متأكد من مسح جميع البيانات؟ لا يمكن التراجع عن هذا الإجراء.",
            buttons=[
                MDFlatButton(text="إلغاء", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(
                    text="مسح الكل",
                    md_bg_color=(0.937, 0.267, 0.267, 1),
                    on_release=self.do_clear,
                ),
            ],
        )
        self.dialog.open()

    def do_clear(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        clear_all()
        self.load_data()
        self._show_msg("تم", "تم مسح جميع البيانات بنجاح.")

    def _show_msg(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="حسناً", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()
