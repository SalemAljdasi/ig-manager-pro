"""
IG Manager Pro - Appeal Generator
Generates official bilingual (Arabic/English) appeal letters for Instagram support
"""

from datetime import datetime


ISSUE_TYPES = {
    "disabled":    ("حساب معطّل", "Disabled Account"),
    "shadowban":   ("شادوبان / قيود مخفية", "Shadowban / Hidden Restrictions"),
    "hacked":      ("حساب مخترق", "Hacked Account"),
    "impersonation": ("انتحال هوية", "Identity Impersonation"),
    "copyright":   ("حقوق نشر", "Copyright Violation"),
    "other":       ("مشكلة أخرى", "Other Issue"),
}

INSTAGRAM_SUPPORT_URL = "https://help.instagram.com/contact/1652567094844914"


def generate_appeal(data: dict) -> dict:
    """
    Generate bilingual appeal text.

    Args:
        data: dict with keys:
            username, full_name, email, year_created,
            country, issue_type, issue_detail
    Returns:
        dict with keys: appeal_ar, appeal_en
    """
    username     = data.get("username", "").strip().lstrip("@")
    full_name    = data.get("full_name", "").strip()
    email        = data.get("email", "").strip()
    year_created = data.get("year_created", "").strip()
    country      = data.get("country", "").strip()
    issue_type   = data.get("issue_type", "other")
    issue_detail = data.get("issue_detail", "").strip()

    issue_ar, issue_en = ISSUE_TYPES.get(issue_type, ISSUE_TYPES["other"])
    now = datetime.now().strftime("%Y-%m-%d")

    # ─── Arabic Appeal ────────────────────────────────────────────────────────
    appeal_ar = f"""════════════════════════════════════
طلب استئناف رسمي – إنستغرام
التاريخ: {now}
════════════════════════════════════

إلى فريق دعم وسلامة مجتمع إنستغرام،
إلى Meta Platforms Inc.،

الموضوع: {issue_ar} – @{username}

تحية طيبة وبعد،

أنا {full_name}، صاحب الحساب الشخصي على منصة إنستغرام:
• اسم المستخدم : @{username}
• البريد الإلكتروني المرتبط: {email}
• سنة إنشاء الحساب: {year_created}
• البلد: {country}

أتقدم إليكم بهذا الطلب الرسمي بخصوص المشكلة التالية:
المشكلة: {issue_ar}

─────────────────────────────────────
تفاصيل المشكلة:
{issue_detail}
─────────────────────────────────────

أؤكد بشكل قاطع أن حسابي يلتزم تمامًا بشروط خدمة إنستغرام وإرشادات
مجتمع Meta، ولم أقم بأي نشاط يخالف هذه الشروط.

طلباتي:
1. مراجعة الإجراء المتخذ بحق حسابي بشكل عاجل
2. إعادة الحساب إلى وضعه الطبيعي الكامل فور التحقق
3. إبلاغي بنتيجة المراجعة عبر البريد الإلكتروني المذكور أعلاه

أنا على استعداد تام لتقديم أي وثائق أو تحقق إضافي تحتاجه مراجعتكم.

مع التقدير،
{full_name}
@{username}
{email}
التاريخ: {now}
════════════════════════════════════
"""

    # ─── English Appeal ───────────────────────────────────────────────────────
    appeal_en = f"""════════════════════════════════════
Official Appeal Request – Instagram
Date: {now}
════════════════════════════════════

To: Instagram Community Safety & Support Team
To: Meta Platforms Inc.

Subject: {issue_en} – @{username}

Dear Instagram Support Team,

My name is {full_name}, and I am writing to formally appeal regarding
my personal Instagram account:
• Username    : @{username}
• Linked Email: {email}
• Account Year: {year_created}
• Country     : {country}

I am submitting this official request regarding the following issue:
Issue Type: {issue_en}

─────────────────────────────────────
Issue Details:
{issue_detail}
─────────────────────────────────────

I firmly confirm that my account has always been operated in strict
compliance with Instagram's Terms of Service and Meta's Community
Guidelines. I have not engaged in any activity that violates these
policies.

My Requests:
1. Urgently review the action taken against my account
2. Fully restore my account upon verification of the above
3. Notify me of the review outcome via the email provided above

I am fully prepared to provide any additional documentation or
verification needed for your review.

Respectfully,
{full_name}
@{username}
{email}
Date: {now}
════════════════════════════════════
"""

    return {
        "appeal_ar": appeal_ar.strip(),
        "appeal_en": appeal_en.strip(),
    }
