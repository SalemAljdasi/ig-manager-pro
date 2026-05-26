import re
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from models.database import save_chat, get_chat_history

# AI Knowledge Base - Comprehensive Q&A
KNOWLEDGE_BASE = [
    # Shadowban
    {
        "keywords": ["شادوبان", "shadowban", "shadow ban", "اختفاء المنشورات", "لا يظهر", "محتوى مخفي", "هاشتاق لا يعمل"],
        "response_ar": (
            "🌑 **ما هو الشادوبان؟**\n\n"
            "الشادوبان (Shadow Ban) هو قيد خفي تضعه إنستغرام على حسابك، بحيث:\n"
            "• لا يظهر محتواك في نتائج الهاشتاق\n"
            "• لا يراك أشخاص غير متابعيك\n"
            "• تنخفض معدلات التفاعل بشكل ملحوظ\n\n"
            "**🔧 كيفية الإزالة:**\n"
            "1. توقف عن النشر 48-72 ساعة\n"
            "2. احذف الهاشتاقات المحظورة من منشوراتك\n"
            "3. لا تستخدم تطبيقات التفاعل التلقائي\n"
            "4. امسح كاش التطبيق\n"
            "5. استخدم 5-10 هاشتاقات فقط في كل منشور\n"
            "6. انتظر 14-30 يوماً للتعافي الكامل\n\n"
            "💡 نصيحة: استخدم شاشة الفاحص للتحقق من حالة حسابك!"
        ),
        "response_en": (
            "🌑 **What is a Shadowban?**\n\n"
            "A shadowban is a hidden restriction Instagram places on your account:\n"
            "• Your content doesn't appear in hashtag results\n"
            "• Non-followers can't discover your posts\n"
            "• Engagement rates drop significantly\n\n"
            "**🔧 How to Remove It:**\n"
            "1. Stop posting for 48-72 hours\n"
            "2. Remove banned hashtags from your posts\n"
            "3. Stop using third-party automation apps\n"
            "4. Clear the app cache\n"
            "5. Use only 5-10 hashtags per post\n"
            "6. Wait 14-30 days for full recovery"
        ),
    },
    # Disabled account
    {
        "keywords": ["معطل", "disabled", "حساب معطل", "تم تعطيل", "لا استطيع الدخول", "محظور", "banned"],
        "response_ar": (
            "🔴 **كيفية استرداد حساب معطل؟**\n\n"
            "**الخطوات الأساسية:**\n"
            "1. اذهب إلى: instagram.com/disabled\n"
            "2. أدخل بريدك الإلكتروني أو هاتفك\n"
            "3. اتبع تعليمات التحقق من الهوية\n"
            "4. اكتب رسالة استرداد احترافية\n"
            "5. قدم هويتك الشخصية إن طُلب\n\n"
            "**⏱️ مدة الانتظار:** 3-30 يوماً\n\n"
            "**📧 تواصل مع الدعم:**\n"
            "help.instagram.com/contact\n\n"
            "💡 استخدم شاشة الاسترداد في التطبيق لتوليد رسالة احترافية!"
        ),
        "response_en": (
            "🔴 **How to recover a disabled account?**\n\n"
            "**Basic Steps:**\n"
            "1. Go to: instagram.com/disabled\n"
            "2. Enter your email or phone\n"
            "3. Follow the identity verification steps\n"
            "4. Write a professional recovery message\n"
            "5. Submit your ID if requested\n\n"
            "**⏱️ Response time:** 3-30 days\n\n"
            "Use the Recovery screen in this app to generate a professional letter!"
        ),
    },
    # Verification
    {
        "keywords": ["توثيق", "verification", "شارة", "شارة زرقاء", "verified", "blue badge", "blue check", "blue tick"],
        "response_ar": (
            "✔️ **كيف تحصل على الشارة الزرقاء؟**\n\n"
            "**الشروط الأربعة الرسمية:**\n"
            "1. ✅ الأصالة: حسابك يمثل شخصاً/علامة حقيقية\n"
            "2. ✅ التفرد: الحساب الوحيد لك على المنصة\n"
            "3. ✅ الاكتمال: حساب عام، صورة، سيرة، منشورات\n"
            "4. ✅ البروز: معروف ومُهتم به على نطاق واسع\n\n"
            "**📋 ما يساعد في القبول:**\n"
            "• تغطيات في مواقع إخبارية موثوقة\n"
            "• صفحة ويكيبيديا\n"
            "• حسابات موثقة على منصات أخرى\n"
            "• عدد متابعين حقيقيين كبير\n\n"
            "⚠️ لا تدفع لأحد مقابل التوثيق!\n"
            "يمكن إعادة التقديم بعد 30 يوماً من الرفض.\n\n"
            "💡 استخدم شاشة التوثيق لتوليد طلب احترافي!"
        ),
        "response_en": (
            "✔️ **How to get the blue verification badge?**\n\n"
            "**Four Official Requirements:**\n"
            "1. ✅ Authentic: Real person, business, or brand\n"
            "2. ✅ Unique: Only official account on the platform\n"
            "3. ✅ Complete: Public profile, photo, bio, and posts\n"
            "4. ✅ Notable: Well-known and widely searched\n\n"
            "**What helps:**\n"
            "• Media coverage on reputable news sites\n"
            "• Wikipedia page\n"
            "• Verified accounts on other platforms\n\n"
            "⚠️ Never pay for verification!"
        ),
    },
    # Hacked account
    {
        "keywords": ["مخترق", "hacked", "اختراق", "شخص دخل حسابي", "سُرق حسابي", "تغيير كلمة مرور", "تغيرت معلوماتي"],
        "response_ar": (
            "🚨 **حسابي مخترق — ماذا أفعل؟**\n\n"
            "**فوراً الآن:**\n"
            "1. اذهب إلى: help.instagram.com/149494825257596\n"
            "2. اضغط 'لا يمكنني الوصول لهذا البريد أو الهاتف'\n"
            "3. تحقق من هويتك عبر صورة سيلفي\n\n"
            "**بعد استعادة الوصول:**\n"
            "• غير كلمة مرورك فوراً\n"
            "• فعّل المصادقة الثنائية (2FA)\n"
            "• راجع التطبيقات المرتبطة وأزل المشبوهة\n"
            "• غير كلمة مرور بريدك الإلكتروني أيضاً\n"
            "• أخبر متابعيك بتجاهل أي رسائل صدرت من حسابك أثناء الاختراق\n\n"
            "⚠️ تصرف بسرعة — كل دقيقة مهمة!"
        ),
        "response_en": (
            "🚨 **My account is hacked — What to do?**\n\n"
            "**Immediately:**\n"
            "1. Go to: help.instagram.com/149494825257596\n"
            "2. Tap 'I can't access this email or phone number'\n"
            "3. Verify your identity with a selfie\n\n"
            "**After regaining access:**\n"
            "• Change your password immediately\n"
            "• Enable two-factor authentication (2FA)\n"
            "• Review and remove suspicious linked apps\n"
            "• Change your email password too\n\n"
            "⚠️ Act fast — every minute matters!"
        ),
    },
    # Account security
    {
        "keywords": ["حماية", "أمان", "security", "protect", "كلمة مرور", "password", "2fa", "مصادقة ثنائية", "two factor"],
        "response_ar": (
            "🛡️ **كيف تحمي حسابك من الاختراق؟**\n\n"
            "**الخطوات الأساسية:**\n"
            "1. 🔐 فعّل المصادقة الثنائية (2FA) فوراً\n"
            "   الإعدادات > الأمان > المصادقة الثنائية\n"
            "2. 🔑 استخدم كلمة مرور قوية (8+ حروف، أرقام، رموز)\n"
            "3. 📧 تأكد من أمان بريدك الإلكتروني المرتبط\n"
            "4. 📱 راجع الأجهزة المتصلة من الإعدادات\n"
            "5. 🚫 لا تستخدم تطبيقات طرف ثالث\n"
            "6. 🔗 لا تضغط على روابط مشبوهة\n"
            "7. 🔄 غير كلمة مرورك كل 3 أشهر\n"
            "8. 📶 لا تستخدم WiFi عامة عند الدخول\n\n"
            "💡 نصيحة ذهبية: المصادقة الثنائية تحمي 99% من حالات الاختراق!"
        ),
        "response_en": (
            "🛡️ **How to protect your account from hacking?**\n\n"
            "**Essential Steps:**\n"
            "1. 🔐 Enable Two-Factor Authentication (2FA) immediately\n"
            "2. 🔑 Use a strong password (8+ chars, numbers, symbols)\n"
            "3. 📧 Secure the email linked to your account\n"
            "4. 📱 Review connected devices in Settings\n"
            "5. 🚫 Don't use third-party apps\n"
            "6. 🔗 Don't click suspicious links\n"
            "7. 🔄 Change your password every 3 months\n\n"
            "💡 2FA protects 99% of hacking attempts!"
        ),
    },
    # Contact Instagram support
    {
        "keywords": ["دعم", "support", "تواصل", "مراسلة", "إنستغرام مباشرة", "فريق إنستغرام", "contact instagram", "help instagram"],
        "response_ar": (
            "📞 **كيف تتواصل مع دعم إنستغرام؟**\n\n"
            "**الروابط الرسمية:**\n"
            "1. مركز المساعدة:\n   help.instagram.com\n\n"
            "2. الإبلاغ عن مشكلة من داخل التطبيق:\n"
            "   الإعدادات > المساعدة > الإبلاغ عن مشكلة\n\n"
            "3. نموذج الاستئناف العام:\n   help.instagram.com/contact/1652567838289083\n\n"
            "4. حساب معطل:\n   instagram.com/disabled\n\n"
            "5. حساب مخترق:\n   help.instagram.com/149494825257596\n\n"
            "**💡 نصائح للحصول على رد أسرع:**\n"
            "• اكتب رسالة مفصلة وواضحة\n"
            "• قدم أكبر قدر من المعلومات\n"
            "• كن صبوراً (3-30 يوماً للرد)\n"
            "• لا ترسل طلبات متكررة في وقت قصير"
        ),
        "response_en": (
            "📞 **How to contact Instagram support?**\n\n"
            "**Official Links:**\n"
            "1. Help Center: help.instagram.com\n"
            "2. Report in-app: Settings > Help > Report a Problem\n"
            "3. Appeals: help.instagram.com/contact/1652567838289083\n"
            "4. Disabled account: instagram.com/disabled\n"
            "5. Hacked account: help.instagram.com/149494825257596\n\n"
            "**Tips for faster response:**\n"
            "• Write a detailed and clear message\n"
            "• Provide as much information as possible\n"
            "• Be patient (3-30 days for a reply)"
        ),
    },
    # Followers tips
    {
        "keywords": ["متابعين", "followers", "زيادة متابعين", "نمو", "grow", "reach"],
        "response_ar": (
            "📈 **نصائح لزيادة المتابعين بشكل طبيعي:**\n\n"
            "1. 📸 انشر محتوى عالي الجودة باستمرار\n"
            "2. ⏰ انشر في أوقات الذروة (7-9 صباحاً، 7-9 مساءً)\n"
            "3. #️⃣ استخدم هاشتاقات ذات صلة ومتخصصة\n"
            "4. 💬 تفاعل مع متابعيك ورد على التعليقات\n"
            "5. 📖 استخدم القصص (Stories) يومياً\n"
            "6. 🎥 ريلز (Reels) تصل لجمهور أوسع بكثير\n"
            "7. 🤝 تعاون مع حسابات أخرى في مجالك\n"
            "8. 📝 اكتب سيرة ذاتية جذابة وواضحة\n\n"
            "⚠️ تجنب شراء المتابعين — يضر بحسابك!"
        ),
        "response_en": (
            "📈 **Tips to grow followers organically:**\n\n"
            "1. 📸 Post high-quality content consistently\n"
            "2. ⏰ Post at peak times (7-9 AM, 7-9 PM)\n"
            "3. #️⃣ Use relevant niche hashtags\n"
            "4. 💬 Engage with your followers\n"
            "5. 📖 Use Stories daily\n"
            "6. 🎥 Reels reach a much wider audience\n"
            "7. 🤝 Collaborate with accounts in your niche\n\n"
            "⚠️ Never buy followers — it harms your account!"
        ),
    },
    # Default/greeting
    {
        "keywords": ["مرحبا", "hello", "hi", "أهلا", "السلام", "كيف", "ما هو", "help", "مساعدة", "ابدأ"],
        "response_ar": (
            "👋 **أهلاً بك في مساعد IG Manager Pro!**\n\n"
            "يمكنني مساعدتك في:\n\n"
            "🔴 الشادوبان وكيفية إزالته\n"
            "🔓 استرداد الحسابات المعطلة\n"
            "✔️ طلب التوثيق (الشارة الزرقاء)\n"
            "🛡️ حماية حسابك من الاختراق\n"
            "📞 التواصل مع دعم إنستغرام\n"
            "📈 نصائح لزيادة المتابعين\n\n"
            "اكتب سؤالك وسأجيبك فوراً! 🚀"
        ),
        "response_en": (
            "👋 **Welcome to IG Manager Pro Assistant!**\n\n"
            "I can help you with:\n\n"
            "🌑 Shadowban and how to remove it\n"
            "🔓 Recovering disabled accounts\n"
            "✔️ Getting the blue verification badge\n"
            "🛡️ Protecting your account from hacking\n"
            "📞 Contacting Instagram support\n"
            "📈 Tips to grow followers\n\n"
            "Ask me anything! 🚀"
        ),
    },
]

DEFAULT_AR = (
    "🤔 لم أفهم سؤالك تماماً. يمكنني مساعدتك في:\n"
    "• الشادوبان\n• الحسابات المعطلة\n• التوثيق\n• الأمان والحماية\n• دعم إنستغرام\n\n"
    "اكتب سؤالك بوضوح وسأساعدك!"
)

DEFAULT_EN = (
    "🤔 I didn't understand your question. I can help you with:\n"
    "• Shadowban\n• Disabled accounts\n• Verification\n• Security & protection\n• Instagram support\n\n"
    "Please rephrase your question!"
)


def detect_language(text: str) -> str:
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    return "ar" if arabic_chars > len(text) * 0.2 else "en"


def get_ai_response(user_input: str) -> str:
    lang = detect_language(user_input)
    lower_input = user_input.lower()

    for entry in KNOWLEDGE_BASE:
        for kw in entry["keywords"]:
            if kw.lower() in lower_input:
                return entry["response_ar"] if lang == "ar" else entry["response_en"]

    return DEFAULT_AR if lang == "ar" else DEFAULT_EN


class ChatBubble(MDCard):
    def __init__(self, text, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.radius = [dp(14), dp(14), dp(4) if is_user else dp(14), dp(14) if is_user else dp(4)]
        self.padding = [dp(12), dp(10)]
        self.size_hint_x = 0.85
        self.pos_hint = {"right": 1} if is_user else {"left": 0}
        self.md_bg_color = (0.486, 0.227, 0.918, 1) if is_user else (0.07, 0.07, 0.16, 1)
        self.elevation = 3

        label = MDLabel(
            text=text,
            font_style="Body2",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
        )
        label.bind(texture_size=lambda inst, ts: setattr(inst, "height", ts[1] + dp(4)))
        self.bind(minimum_height=self.setter("height"))
        self.add_widget(label)


class AIChatScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ai_chat"
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
            text="🤖 المساعد الذكي",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.655, 0.231, 0.929, 1),
            bold=True,
        ))
        clear_btn = MDIconButton(icon="delete-sweep", on_release=self.clear_chat)
        header.add_widget(clear_btn)
        root.add_widget(header)

        self.scroll = ScrollView()
        self.chat_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(12),
            size_hint_y=None,
        )
        self.chat_box.bind(minimum_height=self.chat_box.setter("height"))
        self.scroll.add_widget(self.chat_box)
        root.add_widget(self.scroll)

        # Input area
        input_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=[dp(8), dp(6)],
            spacing=dp(8),
            md_bg_color=(0.07, 0.07, 0.16, 1),
        )
        self.input_field = MDTextField(
            hint_text="اكتب سؤالك هنا...",
            mode="rectangle",
            size_hint_x=0.82,
        )
        self.input_field.bind(on_text_validate=self.send_message)
        send_btn = MDRaisedButton(
            text="➤",
            md_bg_color=(0.486, 0.227, 0.918, 1),
            size_hint_x=0.18,
            on_release=self.send_message,
        )
        input_row.add_widget(self.input_field)
        input_row.add_widget(send_btn)
        root.add_widget(input_row)

        self.add_widget(root)

    def on_enter(self):
        self.chat_box.clear_widgets()
        history = get_chat_history(50)
        if not history:
            self._add_bubble(
                "👋 أهلاً! أنا مساعد IG Manager Pro الذكي.\n"
                "يمكنني مساعدتك في أي سؤال حول إنستغرام.\n"
                "اكتب سؤالك وسأجيبك فوراً!",
                is_user=False
            )
        else:
            for msg in history:
                self._add_bubble(msg["message"], is_user=(msg["role"] == "user"))

    def send_message(self, *args):
        text = self.input_field.text.strip()
        if not text:
            return
        self.input_field.text = ""
        self._add_bubble(text, is_user=True)
        save_chat("user", text)
        Clock.schedule_once(lambda dt: self._process_response(text), 0.3)

    def _process_response(self, user_text):
        response = get_ai_response(user_text)
        self._add_bubble(response, is_user=False)
        save_chat("assistant", response)
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)

    def _add_bubble(self, text, is_user=False):
        bubble = ChatBubble(text=text, is_user=is_user)
        wrapper = MDBoxLayout(
            size_hint_y=None,
            padding=[0, dp(2)],
        )
        wrapper.bind(minimum_height=wrapper.setter("height"))
        if is_user:
            wrapper.add_widget(MDBoxLayout(size_hint_x=0.15))
            wrapper.add_widget(bubble)
        else:
            wrapper.add_widget(bubble)
            wrapper.add_widget(MDBoxLayout(size_hint_x=0.15))
        self.chat_box.add_widget(wrapper)
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)

    def _scroll_to_bottom(self):
        self.scroll.scroll_y = 0

    def clear_chat(self, *args):
        self.chat_box.clear_widgets()
        self._add_bubble(
            "تم مسح المحادثة. كيف يمكنني مساعدتك؟",
            is_user=False
        )
