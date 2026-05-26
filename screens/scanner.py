import threading
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tabs import MDTabs
from core.checker import check_account, check_accounts_bulk
from models.database import save_scan, init_db
from assets.theme import STATUS_LABELS_AR, STATUS_COLORS, COLORS


class Tab(MDFloatLayout, MDTabsBase):
    pass


class ScannerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "scanner"
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
            text="🔍 فاحص الحسابات",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            bold=True,
        ))
        root.add_widget(header)

        self.tabs = MDTabs()
        self.tabs.bind(on_tab_switch=self.on_tab_switch)

        # Single scan tab
        single_tab = Tab(title="فحص واحد")
        single_scroll = ScrollView()
        self.single_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(16),
            size_hint_y=None,
        )
        self.single_content.bind(minimum_height=self.single_content.setter("height"))
        self._build_single_tab()
        single_scroll.add_widget(self.single_content)
        single_tab.add_widget(single_scroll)

        # Bulk scan tab
        bulk_tab = Tab(title="فحص جماعي")
        bulk_scroll = ScrollView()
        self.bulk_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(16),
            size_hint_y=None,
        )
        self.bulk_content.bind(minimum_height=self.bulk_content.setter("height"))
        self._build_bulk_tab()
        bulk_scroll.add_widget(self.bulk_content)
        bulk_tab.add_widget(bulk_scroll)

        self.tabs.add_widget(single_tab)
        self.tabs.add_widget(bulk_tab)
        root.add_widget(self.tabs)
        self.add_widget(root)

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        pass

    def _build_single_tab(self):
        c = self.single_content

        c.add_widget(MDLabel(
            text="أدخل اسم المستخدم للفحص",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(36),
        ))

        self.username_field = MDTextField(
            hint_text="اسم المستخدم (بدون @)",
            helper_text="مثال: instagram",
            helper_text_mode="on_focus",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56),
        )
        c.add_widget(self.username_field)

        scan_btn = MDRaisedButton(
            text="🔍 فحص الحساب",
            md_bg_color=(0.486, 0.227, 0.918, 1),
            size_hint_y=None,
            height=dp(48),
            on_release=self.start_single_scan,
        )
        c.add_widget(scan_btn)

        self.single_spinner = MDBoxLayout(size_hint_y=None, height=0)
        c.add_widget(self.single_spinner)

        self.result_card = MDCard(
            md_bg_color=(0.07, 0.07, 0.16, 1),
            radius=[dp(14)],
            padding=dp(16),
            size_hint_y=None,
            height=0,
            elevation=4,
        )
        self.result_content = MDBoxLayout(orientation="vertical", spacing=dp(8))
        self.result_card.add_widget(self.result_content)
        c.add_widget(self.result_card)

    def _build_bulk_tab(self):
        c = self.bulk_content

        c.add_widget(MDLabel(
            text="الفحص الجماعي للحسابات",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(36),
        ))

        c.add_widget(MDLabel(
            text="الصق أسماء المستخدمين (سطر لكل اسم):",
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(28),
        ))

        self.bulk_field = MDTextField(
            hint_text="username1\nusername2\nusername3",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(150),
        )
        c.add_widget(self.bulk_field)

        bulk_btn = MDRaisedButton(
            text="🚀 بدء الفحص الجماعي",
            md_bg_color=(0.486, 0.227, 0.918, 1),
            size_hint_y=None,
            height=dp(48),
            on_release=self.start_bulk_scan,
        )
        c.add_widget(bulk_btn)

        self.progress_bar = MDProgressBar(
            value=0,
            size_hint_y=None,
            height=dp(8),
            color=(0.486, 0.227, 0.918, 1),
        )
        c.add_widget(self.progress_bar)

        self.progress_label = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(24),
            halign="center",
        )
        c.add_widget(self.progress_label)

        self.bulk_log = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
        )
        self.bulk_log.bind(minimum_height=self.bulk_log.setter("height"))
        c.add_widget(self.bulk_log)

    def start_single_scan(self, *args):
        username = self.username_field.text.strip().lstrip("@")
        if not username:
            self._show_error("يرجى إدخال اسم مستخدم")
            return

        self.result_card.height = 0
        self.result_content.clear_widgets()
        self.result_content.add_widget(MDLabel(
            text="⏳ جارٍ الفحص...",
            font_style="Body1",
            halign="center",
            size_hint_y=None,
            height=dp(40),
        ))
        self.result_card.height = dp(60)

        def scan_thread():
            init_db()
            result = check_account(username)
            Clock.schedule_once(lambda dt: self._show_single_result(result), 0)

        threading.Thread(target=scan_thread, daemon=True).start()

    def _show_single_result(self, result):
        self.result_content.clear_widgets()
        status = result.get("status", "unknown")
        status_label = STATUS_LABELS_AR.get(status, "غير معروف")
        status_color_hex = STATUS_COLORS.get(status, "#475569")
        r, g, b = [int(status_color_hex.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4)]

        def add_row(label, value, color=None):
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
            row.add_widget(MDLabel(
                text=label,
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_x=0.45,
            ))
            lbl = MDLabel(
                text=str(value),
                font_style="Body1",
                bold=True,
                size_hint_x=0.55,
                halign="left",
            )
            if color:
                lbl.theme_text_color = "Custom"
                lbl.text_color = color
            self.result_content.add_widget(row)
            row.add_widget(lbl)

        self.result_content.add_widget(MDLabel(
            text=f"نتيجة فحص @{result.get('username', '')}",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            size_hint_y=None,
            height=dp(40),
        ))

        add_row("الحالة:", status_label, (r, g, b, 1))
        add_row("المتابعون:", f"{result.get('followers', 0):,}")
        add_row("يتابع:", f"{result.get('following', 0):,}")
        add_row("المنشورات:", f"{result.get('posts', 0):,}")
        add_row("موثق:", "✅ نعم" if result.get("is_verified") else "❌ لا")
        add_row("خاص:", "🔒 نعم" if result.get("is_private") else "🔓 لا")
        add_row("البريد المتوقع:", result.get("guessed_email", "-"))

        score = result.get("security_score", 0)
        level = result.get("security_level", "unknown")
        level_map = {"weak": ("ضعيف", "#EF4444"), "medium": ("متوسط", "#F59E0B"), "good": ("جيد", "#10B981")}
        level_label, level_color = level_map.get(level, ("غير معروف", "#475569"))
        lc_r, lc_g, lc_b = [int(level_color.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4)]
        add_row("تقييم الأمان:", f"{level_label} ({score}%)", (lc_r, lc_g, lc_b, 1))

        if result.get("error"):
            add_row("ملاحظة:", result["error"])

        self.result_card.height = dp(48 + len(self.result_content.children) * 36)

        if not result.get("error"):
            save_scan(
                username=result.get("username", ""),
                status=result.get("status", "unknown"),
                followers=result.get("followers", 0),
                following=result.get("following", 0),
                posts=result.get("posts", 0),
                is_verified=result.get("is_verified", False),
                is_private=result.get("is_private", False),
                guessed_email=result.get("guessed_email", ""),
                security_score=result.get("security_score", 0),
                security_level=result.get("security_level", "unknown"),
            )

    def start_bulk_scan(self, *args):
        text = self.bulk_field.text.strip()
        if not text:
            self._show_error("يرجى إدخال أسماء المستخدمين")
            return
        usernames = [u.strip() for u in text.splitlines() if u.strip()]
        if not usernames:
            self._show_error("لا توجد أسماء صحيحة")
            return

        self.bulk_log.clear_widgets()
        self.progress_bar.value = 0
        self.progress_label.text = f"0 / {len(usernames)}"

        def progress_cb(done, total, result):
            def update(dt):
                self.progress_bar.value = (done / total) * 100
                self.progress_label.text = f"{done} / {total}"
                status = result.get("status", "unknown")
                status_label = STATUS_LABELS_AR.get(status, "غير معروف")
                row_label = MDLabel(
                    text=f"@{result.get('username')} — {status_label}",
                    font_style="Caption",
                    size_hint_y=None,
                    height=dp(24),
                )
                self.bulk_log.add_widget(row_label)
                save_scan(
                    username=result.get("username", ""),
                    status=result.get("status", "unknown"),
                    followers=result.get("followers", 0),
                    following=result.get("following", 0),
                    posts=result.get("posts", 0),
                    is_verified=result.get("is_verified", False),
                    is_private=result.get("is_private", False),
                    guessed_email=result.get("guessed_email", ""),
                    security_score=result.get("security_score", 0),
                    security_level=result.get("security_level", "unknown"),
                )
            Clock.schedule_once(update, 0)

        def bulk_thread():
            init_db()
            check_accounts_bulk(usernames, progress_callback=progress_cb)
            Clock.schedule_once(lambda dt: self._show_bulk_done(), 0)

        threading.Thread(target=bulk_thread, daemon=True).start()

    def _show_bulk_done(self):
        self.bulk_log.add_widget(MDLabel(
            text="✅ تم الفحص الجماعي بنجاح!",
            font_style="Body1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.063, 0.722, 0.506, 1),
            size_hint_y=None,
            height=dp(36),
            halign="center",
        ))

    def _show_error(self, msg):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title="تنبيه",
            text=msg,
            buttons=[MDFlatButton(text="حسناً", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()
