# IG Manager Pro v4.0 - Theme Configuration
# Telegram Bot Credentials
TELEGRAM_TOKEN = "8840411126:AAGNL_bGcQA23n1IjY9r7aWDER_0jZubhNc"
TELEGRAM_CHAT_ID = "659334247"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# App Info
APP_NAME = "IG Manager Pro"
APP_VERSION = "4.0"
APP_AUTHOR = "IG Manager Pro Team"
APP_COPYRIGHT = "© 2025 IG Manager Pro. All rights reserved."

# Dark Glassmorphism Color Palette
COLORS = {
    "bg_dark": "#0A0A1A",
    "bg_card": "#12122A",
    "bg_glass": "#1A1A3A",
    "primary": "#7C3AED",       # Purple
    "primary_light": "#A78BFA",
    "secondary": "#06B6D4",     # Cyan
    "secondary_light": "#67E8F9",
    "accent": "#EC4899",        # Pink
    "success": "#10B981",       # Green
    "warning": "#F59E0B",       # Amber
    "danger": "#EF4444",        # Red
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#475569",
    "border": "#2D2D5E",
    "neon_purple": "#BF5AF2",
    "neon_cyan": "#00E5FF",
    "neon_pink": "#FF2D92",
    "gradient_start": "#7C3AED",
    "gradient_end": "#06B6D4",
}

# MDTheme Palette
PRIMARY_PALETTE = "DeepPurple"
ACCENT_PALETTE = "Cyan"
THEME_STYLE = "Dark"

# Status Colors
STATUS_COLORS = {
    "active": "#10B981",
    "disabled": "#EF4444",
    "shadowban": "#F59E0B",
    "private": "#06B6D4",
    "hacked": "#EC4899",
    "verified": "#7C3AED",
    "unknown": "#475569",
}

STATUS_LABELS_AR = {
    "active": "نشط",
    "disabled": "معطل",
    "shadowban": "شادوبان",
    "private": "خاص",
    "hacked": "مخترق",
    "verified": "موثق",
    "unknown": "غير معروف",
}

ISSUE_TYPES = [
    "معطل",
    "شادوبان",
    "مخترق",
    "انتحال هوية",
    "حقوق نشر",
    "أخرى",
]

SECURITY_LEVELS = {
    "weak": {"label": "ضعيف", "color": "#EF4444", "score_range": (0, 40)},
    "medium": {"label": "متوسط", "color": "#F59E0B", "score_range": (41, 70)},
    "good": {"label": "جيد", "color": "#10B981", "score_range": (71, 100)},
}

# Instagram URLs
INSTAGRAM_SUPPORT_URL = "https://help.instagram.com/contact"
INSTAGRAM_DISABLED_URL = "https://www.instagram.com/disabled/"
INSTAGRAM_REPORT_URL = "https://help.instagram.com/contact/1652567838289083"
INSTAGRAM_VERIFY_URL = "https://www.instagram.com/accounts/request-verification/"
INSTAGRAM_HACKED_URL = "https://help.instagram.com/149494825257596"
INSTAGRAM_SHADOWBAN_URL = "https://help.instagram.com/contact/1638932959624764"
