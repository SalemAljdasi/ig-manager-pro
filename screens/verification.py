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
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from core.appeals import generate_verification_request
from core.verification import (
    VERIFICATION_CONDITIONS_AR, ACCOUNT_TYPES, VERIFICATION_URL
)
from models.database import save_verification_request


class VerificationScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "verification"
        self.dialog = None
        self.selected_type = ACCOUNT_TYPES[0]
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
            text="✔️ طلب التوثيق",
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

        # Conditions card
        content.add_widget(MDLabel(
            text="📋 شروط الحصول على التوثيق",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            size_hint_y=None,
            height=dp(36),
        ))

        cond_card = MDCard(
            md_bg_color=(0.07, 0.07, 0.16, 1),
            radius=[dp(12)],
            padding=dp(14),
            size_hint_y=None,
            elevation=3,
        )
        cond_label = MDLabel(
            text=VERIFICATION_CONDITIONS_AR,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
        )
        cond_label.bind(texture_size=lambda inst, ts: setattr(inst, "height", ts[1] + dp(12)))
        cond_card.bind(minimum_height=cond_card.setter("height"))
        cond_card.add_widget(cond_label)
        content.add_widget(cond_card)

        # Form
        content.add_widget(MDLabel(
            text="📨 نموذج طلب التوثيق",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            size_hint_y=None,
            height=dp(36),
        ))

        fields = [
            ("username_f", "اسم المستخدم *"),
            ("fullname_f", "الاسم الكامل *"),
            ("email_f", "البريد الإلكتروني *"),
            ("followers_f", "عدد المتابعين التقريبي *"),
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

        self.type_btn = MDRaisedButton(
            text=f"نوع الحساب: {self.selected_type}",
            md_bg_color=(0.1, 0.07, 0.2, 1),
            size_hint_y=None,
            height=dp(44),
            on_release=self.open_type_menu,
        )
        content.add_widget(self.type_btn)

        self.social_field = MDTextField(
            hint_text="روابط الحسابات الأخرى (تويتر، فيسبوك، ويكيبيديا...) *",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
        )
        content.add_widget(self.social_field)

        self.activities_field = MDTextField(
            hint_text="وصف النشاط والأسباب التي تجعلك جديراً بالتوثيق *",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(100),
        )
        content.add_widget(self.activities_field)

        self.media_field = MDTextField(
            hint_text="تغطيات إعلامية أو مراجع (اختياري)",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
        )
        content.add_widget(self.media_field)

        gen_btn = MDRaisedButton(
            text="✨ توليد طلب التوثيق الرسمي",
            md_bg_color=(0.486, 0.227, 0.918, 1),
            size_hint_y=None,
            height=dp(50),
            on_release=self.generate,
        )
        content.add_widget(gen_btn)

        self.result_field = MDTextField(
            hint_text="طلب التوثيق بالإنجليزية",
            mode="rectangle",
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height=dp(300),
        )
        content.add_widget(self.result_field)

        action_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48),
        )
        for label, action in [
            ("📋 نسخ", self.copy_result),
            ("💾 حفظ TXT", self.save_txt),
            ("🌐 نموذج رسمي", self.open_official),
        ]:
            btn = MDRaisedButton(text=label, on_release=action)
            action_row.add_widget(btn)
        content.add_widget(action_row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def open_type_menu(self, button):
        menu_items = [
            {
                "text": t,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=t: self.select_type(x),
            }
            for t in ACCOUNT_TYPES
        ]
        self.menu = MDDropdownMenu(caller=button, items=menu_items, width_mult=4)
        self.menu.open()

    def select_type(self, t):
        self.selected_type = t
        self.type_btn.text = f"نوع الحساب: {t}"
        if self.menu:
            self.menu.dismiss()

    def generate(self, *args):
        username = self.username_f.text.strip().lstrip("@")
        full_name = self.fullname_f.text.strip()
        email = self.email_f.text.strip()
        followers = self.followers_f.text.strip()
        social_links = self.social_field.text.strip()
        activities = self.activities_field.text.strip()
        media = self.media_field.text.strip()

        if not all([username, full_name, email, followers, activities]):
            self._show_msg("تنبيه", "يرجى ملء الحقول الإلزامية (*)")
            return

        text = generate_verification_request(
            username, full_name, email, self.selected_type,
            social_links, activities, followers, media
        )
        self.result_field.text = text
        save_verification_request(
            username, full_name, email, self.selected_type,
            social_links, activities, followers, media, text
        )
        self._show_msg("✅ تم", "تم توليد طلب التوثيق وحفظه بنجاح!")

    def copy_result(self, *args):
        from kivy.core.clipboard import Clipboard
        if self.result_field.text:
            Clipboard.copy(self.result_field.text)
            self._show_msg("تم", "تم نسخ الطلب إلى الحافظة.")

    def save_txt(self, *args):
        if not self.result_field.text:
            self._show_msg("تنبيه", "لا يوجد نص لحفظه.")
            return
        path = os.path.join(os.path.expanduser("~"), "ig_verification.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.result_field.text)
        self._show_msg("✅ تم", f"تم حفظ الملف في:\n{path}")

    def open_official(self, *args):
        webbrowser.open(VERIFICATION_URL)

    def _show_msg(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="حسناً", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()
