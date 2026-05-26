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
from core.appeals import BAN_REASONS, generate_recovery_appeal
from core.recovery import RECOVERY_GUIDE_AR, AVOIDANCE_TIPS_AR, RECOVERY_LINKS
from models.database import save_recovery_request


class RecoveryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "recovery"
        self.dialog = None
        self.selected_reason = BAN_REASONS[0]
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
            text="🔓 استرداد الحسابات",
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

        # Guide title
        content.add_widget(MDLabel(
            text="📖 دليل الاسترداد خطوة بخطوة",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            size_hint_y=None,
            height=dp(36),
        ))

        for step in RECOVERY_GUIDE_AR:
            card = MDCard(
                md_bg_color=(0.07, 0.07, 0.16, 1),
                radius=[dp(12)],
                padding=dp(14),
                size_hint_y=None,
                elevation=3,
            )
            inner = MDBoxLayout(orientation="vertical", spacing=dp(6))
            title_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
            title_row.add_widget(MDLabel(
                text=f"{step['icon']} الخطوة {step['step']}: {step['title']}",
                font_style="Subtitle2",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.655, 0.231, 0.929, 1),
            ))
            inner.add_widget(title_row)
            desc_label = MDLabel(
                text=step["description"],
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_y=None,
            )
            desc_label.bind(texture_size=lambda inst, ts: setattr(inst, "height", ts[1] + dp(8)))
            inner.add_widget(desc_label)
            card.bind(minimum_height=card.setter("height"))
            card.add_widget(inner)
            content.add_widget(card)

        # Avoidance tips
        content.add_widget(MDLabel(
            text="💡 نصائح لتجنب الحظر مستقبلاً",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.063, 0.722, 0.506, 1),
            size_hint_y=None,
            height=dp(36),
        ))

        tips_card = MDCard(
            md_bg_color=(0.04, 0.16, 0.1, 1),
            radius=[dp(12)],
            padding=dp(14),
            size_hint_y=None,
            elevation=3,
        )
        tips_inner = MDBoxLayout(orientation="vertical", spacing=dp(4))
        for i, tip in enumerate(AVOIDANCE_TIPS_AR, 1):
            tip_label = MDLabel(
                text=f"{i}. {tip}",
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_y=None,
            )
            tip_label.bind(texture_size=lambda inst, ts: setattr(inst, "height", ts[1] + dp(4)))
            tips_inner.add_widget(tip_label)
        tips_card.bind(minimum_height=tips_card.setter("height"))
        tips_card.add_widget(tips_inner)
        content.add_widget(tips_card)

        # Recovery form
        content.add_widget(MDLabel(
            text="📨 توليد رسالة استرداد",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            size_hint_y=None,
            height=dp(36),
        ))

        self.username_f = MDTextField(
            hint_text="اسم المستخدم *",
            mode="rectangle",
            size_hint_y=None,
            height=dp(52),
        )
        content.add_widget(self.username_f)

        self.reason_btn = MDRaisedButton(
            text=f"سبب الحظر: {self.selected_reason}",
            md_bg_color=(0.1, 0.07, 0.2, 1),
            size_hint_y=None,
            height=dp(44),
            on_release=self.open_reason_menu,
        )
        content.add_widget(self.reason_btn)

        self.extra_field = MDTextField(
            hint_text="معلومات إضافية (اختياري)",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(100),
        )
        content.add_widget(self.extra_field)

        gen_btn = MDRaisedButton(
            text="✨ توليد رسالة الاسترداد",
            md_bg_color=(0.486, 0.227, 0.918, 1),
            size_hint_y=None,
            height=dp(50),
            on_release=self.generate,
        )
        content.add_widget(gen_btn)

        self.result_field = MDTextField(
            hint_text="رسالة الاسترداد",
            mode="rectangle",
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height=dp(260),
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

    def open_reason_menu(self, button):
        menu_items = [
            {
                "text": reason,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=reason: self.select_reason(x),
            }
            for reason in BAN_REASONS
        ]
        self.menu = MDDropdownMenu(caller=button, items=menu_items, width_mult=4)
        self.menu.open()

    def select_reason(self, reason):
        self.selected_reason = reason
        self.reason_btn.text = f"سبب الحظر: {reason}"
        if self.menu:
            self.menu.dismiss()

    def generate(self, *args):
        username = self.username_f.text.strip().lstrip("@")
        if not username:
            self._show_msg("تنبيه", "يرجى إدخال اسم المستخدم")
            return
        extra = self.extra_field.text.strip()
        text = generate_recovery_appeal(username, self.selected_reason, extra)
        self.result_field.text = text
        save_recovery_request(username, self.selected_reason, extra, text)
        self._show_msg("✅ تم", "تم توليد رسالة الاسترداد وحفظها!")

    def copy_result(self, *args):
        from kivy.core.clipboard import Clipboard
        if self.result_field.text:
            Clipboard.copy(self.result_field.text)
            self._show_msg("تم", "تم نسخ الرسالة إلى الحافظة.")

    def save_txt(self, *args):
        if not self.result_field.text:
            self._show_msg("تنبيه", "لا يوجد نص لحفظه.")
            return
        path = os.path.join(os.path.expanduser("~"), "ig_recovery.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.result_field.text)
        self._show_msg("✅ تم", f"تم حفظ الملف في:\n{path}")

    def open_official(self, *args):
        import webbrowser
        webbrowser.open(RECOVERY_LINKS["disabled"])

    def _show_msg(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="حسناً", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()
