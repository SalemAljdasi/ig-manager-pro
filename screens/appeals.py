import os
import webbrowser
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from core.appeals import ISSUE_TYPES, generate_appeal
from models.database import save_appeal
from assets.theme import INSTAGRAM_SUPPORT_URL


class AppealsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "appeals"
        self.dialog = None
        self.selected_issue = ISSUE_TYPES[0]
        self.menu = None
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
            text="📝 الاستئنافات",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            bold=True,
        ))
        root.add_widget(header)

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(16),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(MDLabel(
            text="نموذج طلب الاستئناف الاحترافي",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            size_hint_y=None,
            height=dp(36),
        ))

        fields = [
            ("username_f", "اسم المستخدم (بدون @) *"),
            ("fullname_f", "الاسم الكامل *"),
            ("email_f", "البريد الإلكتروني *"),
            ("year_f", "سنة إنشاء الحساب (مثال: 2018) *"),
            ("country_f", "البلد *"),
            ("phone_f", "رقم الهاتف (اختياري)"),
        ]
        for attr, hint in fields:
            field = MDTextField(
                hint_text=hint,
                mode="rectangle",
                size_hint_y=None,
                height=dp(52),
            )
            setattr(self, attr, field)
            content.add_widget(field)

        # Issue type dropdown
        content.add_widget(MDLabel(
            text="نوع المشكلة:",
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24),
        ))
        self.issue_btn = MDRaisedButton(
            text=f"نوع المشكلة: {self.selected_issue}",
            md_bg_color=(0.1, 0.07, 0.2, 1),
            size_hint_y=None,
            height=dp(44),
            on_release=self.open_issue_menu,
        )
        content.add_widget(self.issue_btn)

        # Description
        self.desc_field = MDTextField(
            hint_text="وصف تفصيلي للمشكلة *",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(120),
        )
        content.add_widget(self.desc_field)

        # Generate button
        gen_btn = MDRaisedButton(
            text="✨ توليد رسالة الاستئناف",
            md_bg_color=(0.486, 0.227, 0.918, 1),
            size_hint_y=None,
            height=dp(50),
            on_release=self.generate,
        )
        content.add_widget(gen_btn)

        # Result area
        content.add_widget(MDLabel(
            text="النتيجة:",
            font_style="Subtitle2",
            bold=True,
            size_hint_y=None,
            height=dp(30),
        ))

        self.result_ar = MDTextField(
            hint_text="رسالة الاستئناف بالعربية",
            mode="rectangle",
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height=dp(200),
        )
        content.add_widget(self.result_ar)

        self.result_en = MDTextField(
            hint_text="رسالة الاستئناف بالإنجليزية",
            mode="rectangle",
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height=dp(200),
        )
        content.add_widget(self.result_en)

        # Action buttons
        action_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48),
        )
        for label, action in [
            ("📋 نسخ AR", self.copy_ar),
            ("📋 نسخ EN", self.copy_en),
            ("💾 حفظ TXT", self.save_txt),
            ("🌐 دعم رسمي", self.open_support),
        ]:
            btn = MDRaisedButton(text=label, on_release=action)
            action_row.add_widget(btn)
        content.add_widget(action_row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def open_issue_menu(self, button):
        menu_items = [
            {
                "text": issue,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=issue: self.select_issue(x),
            }
            for issue in ISSUE_TYPES
        ]
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def select_issue(self, issue):
        self.selected_issue = issue
        self.issue_btn.text = f"نوع المشكلة: {issue}"
        if self.menu:
            self.menu.dismiss()

    def generate(self, *args):
        username = self.username_f.text.strip().lstrip("@")
        full_name = self.fullname_f.text.strip()
        email = self.email_f.text.strip()
        year = self.year_f.text.strip()
        country = self.country_f.text.strip()
        phone = self.phone_f.text.strip()
        desc = self.desc_field.text.strip()

        if not all([username, full_name, email, year, country, desc]):
            self._show_msg("تنبيه", "يرجى ملء جميع الحقول الإلزامية (*)")
            return

        appeal_ar, appeal_en = generate_appeal(
            username, full_name, email, country, phone, year,
            self.selected_issue, desc
        )
        self.result_ar.text = appeal_ar
        self.result_en.text = appeal_en

        save_appeal(username, full_name, email, country, phone,
                    self.selected_issue, desc, appeal_ar, appeal_en)
        self._show_msg("✅ تم", "تم توليد رسالة الاستئناف وحفظها بنجاح!")

    def copy_ar(self, *args):
        from kivy.core.clipboard import Clipboard
        if self.result_ar.text:
            Clipboard.copy(self.result_ar.text)
            self._show_msg("تم", "تم نسخ الرسالة العربية إلى الحافظة.")

    def copy_en(self, *args):
        from kivy.core.clipboard import Clipboard
        if self.result_en.text:
            Clipboard.copy(self.result_en.text)
            self._show_msg("تم", "تم نسخ الرسالة الإنجليزية إلى الحافظة.")

    def save_txt(self, *args):
        if not self.result_ar.text:
            self._show_msg("تنبيه", "لا يوجد نص لحفظه. يرجى توليد الرسالة أولاً.")
            return
        path = os.path.join(os.path.expanduser("~"), "ig_appeal.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("=== رسالة الاستئناف بالعربية ===\n\n")
            f.write(self.result_ar.text)
            f.write("\n\n=== Appeal Letter in English ===\n\n")
            f.write(self.result_en.text)
        self._show_msg("✅ تم الحفظ", f"تم حفظ الملف في:\n{path}")

    def open_support(self, *args):
        webbrowser.open(INSTAGRAM_SUPPORT_URL)

    def _show_msg(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="حسناً", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()
