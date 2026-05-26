"""
IG Manager Pro - Theme Configuration
Dark theme with purple and cyan neon colors + Glassmorphism
"""

# ─── Primary Colors ───────────────────────────────────────────────────────────
PRIMARY_PURPLE = "#a855f7"
PRIMARY_CYAN   = "#06b6d4"
ACCENT_PINK    = "#ec4899"
ACCENT_GREEN   = "#22c55e"
ACCENT_ORANGE  = "#f97316"
ACCENT_RED     = "#ef4444"
ACCENT_YELLOW  = "#eab308"

# ─── Background Colors ────────────────────────────────────────────────────────
BG_DARK       = "#0a0a0f"
BG_CARD       = "#12121a"
BG_CARD2      = "#1a1a2e"
BG_SURFACE    = "#16213e"
BG_GLASS      = "#ffffff14"

# ─── Text Colors ─────────────────────────────────────────────────────────────
TEXT_PRIMARY   = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED     = "#475569"
TEXT_NEON_P    = "#c084fc"
TEXT_NEON_C    = "#22d3ee"

# ─── Status Colors ────────────────────────────────────────────────────────────
STATUS_ACTIVE    = "#22c55e"
STATUS_DISABLED  = "#ef4444"
STATUS_SHADOW    = "#f97316"
STATUS_PRIVATE   = "#a855f7"
STATUS_VERIFIED  = "#06b6d4"
STATUS_UNKNOWN   = "#94a3b8"

STATUS_COLORS = {
    "active":    STATUS_ACTIVE,
    "disabled":  STATUS_DISABLED,
    "shadowban": STATUS_SHADOW,
    "private":   STATUS_PRIVATE,
    "verified":  STATUS_VERIFIED,
    "unknown":   STATUS_UNKNOWN,
}

# ─── Fonts ────────────────────────────────────────────────────────────────────
FONT_REGULAR = "Roboto"
FONT_BOLD    = "Roboto"
FONT_MONO    = "RobotoMono"

# ─── Sizes ────────────────────────────────────────────────────────────────────
RADIUS_SM  = "8dp"
RADIUS_MD  = "12dp"
RADIUS_LG  = "18dp"
RADIUS_XL  = "24dp"

SPACING_XS = "4dp"
SPACING_SM = "8dp"
SPACING_MD = "16dp"
SPACING_LG = "24dp"
SPACING_XL = "32dp"

# ─── KivyMD Theme ─────────────────────────────────────────────────────────────
MD_THEME = {
    "primary_palette": "DeepPurple",
    "accent_palette":  "Cyan",
    "theme_style":     "Dark",
}
