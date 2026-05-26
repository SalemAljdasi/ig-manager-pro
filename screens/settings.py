import threading
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDSwitch
from core.checker import send_test_notification
from models.database import clear_all
from assets.theme import APP_NAME, APP_VERSION, APP_COPYRIGHT, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.dialog = None
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
            text="⚙️ الإعدادات",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            bold=True,
        ))
        root.add_widget(header)

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=dp(16),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # Telegram section
        self._add_section_header(content, "📱 إشعارات تلغرام")

        tg_card = MDCard(
            md_bg_color=(0.07, 0.07, 0.16, 1),
            radius=[dp(14)],
            padding=dp(16),
            size_hint_y=None,
            elevation=4,
        )
        tg_inner = MDBoxLayout(orientation="vertical", spacing=dp(10))

        tg_inner.add_widget(MDLabel(
            text=f"التوكن الحالي: {TELEGRAM_TOKEN[:20]}...",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24),
        ))
        tg_inner.add_widget(MDLabel(
            text=f"Chat ID: {TELEGRAM_CHAT_ID}",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24),
        ))

        test_btn = MDRaisedButton(
            text="🔔 إرسال إشعار تجريبي",
            md_bg_color=(0.063, 0.722, 0.506, 1),
            size_hint_y=None,
            height=dp(44),
            on_release=self.send_test,
        )
        tg_inner.add_widget(test_btn)
        tg_card.bind(minimum_height=tg_card.setter("height"))
        tg_card.add_widget(tg_inner)
        content.add_widget(tg_card)

        # Custom token section
        self._add_section_header(content, "🔑 تغيير بيانات تلغرام (اختياري)")

        token_card = MDCard(
            md_bg_color=(0.07, 0.07, 0.16, 1),
            radius=[dp(14)],
            padding=dp(16),
            size_hint_y=None,
            elevation=4,
        )
        token_inner = MDBoxLayout(orientation="vertical", spacing=dp(10))

        self.token_field = MDTextField(
            hint_text="توكن البوت الجديد (اختياري)",
            mode="rectangle",
            size_hint_y=None,
            height=dp(52),
        )
        self.chatid_field = MDTextField(
            hint_text="Chat ID الجديد (اختياري)",
            mode="rectangle",
            size_hint_y=None,
            height=dp(52),
        )
        save_tg_btn = MDRaisedButton(
            text="💾 حفظ الإعدادات",
            md_bg_color=(0.486, 0.227, 0.918, 1),
            size_hint_y=None,
            height=dp(44),
            on_release=self.save_telegram_settings,
        )
        token_inner.add_widget(self.token_field)
        token_inner.add_widget(self.chatid_field)
        token_inner.add_widget(save_tg_btn)
        token_card.bind(minimum_height=token_card.setter("height"))
        token_card.add_widget(token_inner)
        content.add_widget(token_card)

        # Theme section
        self._add_section_header(content, "🎨 المظهر")
        theme_card = MDCard(
            md_bg_color=(0.07, 0.07, 0.16, 1),
            radius=[dp(14)],
            padding=dp(16),
            size_hint_y=None,
            height=dp(70),
            elevation=4,
        )
        theme_row = MDBoxLayout(orientation="horizontal")
        theme_row.add_widget(MDLabel(
            text="الوضع الليلي (Dark Mode)",
            font_style="Body1",
        ))
        self.dark_switch = MDSwitch(active=True)
        self.dark_switch.bind(active=self.toggle_theme)
        theme_row.add_widget(self.dark_switch)
        theme_card.add_widget(theme_row)
        content.add_widget(theme_card)

        # Database section
        self._add_section_header(content, "🗄️ قاعدة البيانات")
        db_card = MDCard(
            md_bg_color=(0.07, 0.07, 0.16, 1),
            radius=[dp(14)],
            padding=dp(16),
            size_hint_y=None,
            elevation=4,
        )
        db_inner = MDBoxLayout(orientation="vertical", spacing=dp(10))
        db_inner.add_widget(MDLabel(
            text="مسح جميع البيانات المحفوظة (الفحوصات، الاستئنافات، المحادثات)",
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(36),
        ))
        clear_btn = MDRaisedButton(
            text="🗑️ مسح قاعدة البيانات",
            md_bg_color=(0.937, 0.267, 0.267, 1),
            size_hint_y=None,
            height=dp(44),
            on_release=self.confirm_clear,
        )
        db_inner.add_widget(clear_btn)
        db_card.bind(minimum_height=db_card.setter("height"))
        db_card.add_widget(db_inner)
        content.add_widget(db_card)

        # About section
        self._add_section_header(content, "ℹ️ عن التطبيق")
        about_card = MDCard(
            md_bg_color=(0.07, 0.07, 0.16, 1),
            radius=[dp(14)],
            padding=dp(16),
            size_hint_y=None,
            elevation=4,
        )
        about_inner = MDBoxLayout(orientation="vertical", spacing=dp(8))
        about_items = [
            ("اسم التطبيق:", APP_NAME),
            ("الإصدار:", f"v{APP_VERSION}"),
            ("المنصة:", "Android 11+ (API 30+)"),
            ("التقنية:", "Python + KivyMD"),
            ("حقوق النشر:", APP_COPYRIGHT),
        ]
        for label_text, value_text in about_items:
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
            row.add_widget(MDLabel(
                text=label_text,
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_x=0.45,
            ))
            row.add_widget(MDLabel(
                text=value_text,
                font_style="Body2",
                bold=True,
                size_hint_x=0.55,
            ))
            about_inner.add_widget(row)
        about_card.bind(minimum_height=about_card.setter("height"))
        about_card.add_widget(about_inner)
        content.add_widget(about_card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _add_section_header(self, parent, text):
        parent.add_widget(MDLabel(
            text=text,
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            size_hint_y=None,
            height=dp(36),
        ))

    def send_test(self, *args):
        def do_send():
            result = send_test_notification()
            def show(dt):
                if result:
                    self._show_msg("✅ نجح", "تم إرسال إشعار تجريبي إلى تلغرام بنجاح!")
                else:
                    self._show_msg("❌ فشل", "فشل إرسال الإشعار. تحقق من التوكن والاتصال بالإنترنت.")
            Clock.schedule_once(show, 0)
        threading.Thread(target=do_send, daemon=True).start()

    def save_telegram_settings(self, *args):
        token = self.token_field.text.strip()
        chat_id = self.chatid_field.text.strip()
        if token or chat_id:
            import assets.theme as theme
            if token:
                theme.TELEGRAM_TOKEN = token
            if chat_id:
                theme.TELEGRAM_CHAT_ID = chat_id
            self._show_msg("✅ تم", "تم حفظ إعدادات تلغرام (مؤقتاً لهذه الجلسة).")
        else:
            self._show_msg("تنبيه", "لم تُدخل أي بيانات للحفظ.")

    def toggle_theme(self, instance, value):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if value else "Light"

    def confirm_clear(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title="⚠️ تأكيد المسح",
            text="هل أنت متأكد من مسح جميع البيانات؟ لا يمكن التراجع.",
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
        self._show_msg("✅ تم", "تم مسح جميع البيانات بنجاح.")

    def _show_msg(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="حسناً", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()
