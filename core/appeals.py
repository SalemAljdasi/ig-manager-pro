from datetime import datetime

ISSUE_TYPES = [
    "معطل",
    "شادوبان",
    "مخترق",
    "انتحال هوية",
    "حقوق نشر",
    "أخرى",
]

ISSUE_TYPES_EN = {
    "معطل": "Disabled Account",
    "شادوبان": "Shadowban",
    "مخترق": "Hacked Account",
    "انتحال هوية": "Identity Impersonation",
    "حقوق نشر": "Copyright Violation",
    "أخرى": "Other Issue",
}

BAN_REASONS = [
    "انتحال هوية",
    "اختراق الحساب",
    "مخالفة شروط الخدمة",
    "محتوى مخالف",
    "نشاط مشبوه",
    "غير ذلك",
]

BAN_REASONS_EN = {
    "انتحال هوية": "Identity Impersonation",
    "اختراق الحساب": "Account Hacking",
    "مخالفة شروط الخدمة": "Terms of Service Violation",
    "محتوى مخالف": "Violating Content",
    "نشاط مشبوه": "Suspicious Activity",
    "غير ذلك": "Other",
}


def generate_appeal(username, full_name, email, country, phone,
                    year_created, issue_type, description) -> tuple:
    date_ar = datetime.now().strftime("%Y/%m/%d")
    date_en = datetime.now().strftime("%B %d, %Y")
    issue_en = ISSUE_TYPES_EN.get(issue_type, issue_type)
    phone_line_ar = f"- رقم الهاتف: {phone}" if phone else ""
    phone_line_en = f"- Phone: {phone}" if phone else ""

    appeal_ar = f"""بسم الله الرحمن الرحيم

إلى فريق دعم إنستغرام المحترم،

التاريخ: {date_ar}
الموضوع: طلب استئناف — مشكلة: {issue_type}

أتقدم إليكم بكل احترام وأطلب منكم إعادة النظر في وضع حسابي على منصة إنستغرام.

معلوماتي الشخصية:
- اسم المستخدم: @{username}
- الاسم الكامل: {full_name}
- البريد الإلكتروني: {email}
- الدولة: {country}
{phone_line_ar}
- سنة إنشاء الحساب: {year_created}

نوع المشكلة: {issue_type}

وصف المشكلة:
{description}

أؤكد لكم أنني لم أخالف أي من سياسات وشروط استخدام منصة إنستغرام، وأن حسابي يمثل هويتي الحقيقية وأعمالي المشروعة. أرجو منكم التكرم بمراجعة حالة حسابي واتخاذ الإجراء المناسب لإعادة تفعيله.

أنا مستعد لتقديم أي وثائق إضافية أو معلومات تساعدكم في عملية المراجعة.

مع خالص الاحترام والتقدير،
{full_name}
{email}
{date_ar}
"""

    appeal_en = f"""To the Instagram Support Team,

Date: {date_en}
Subject: Account Appeal — Issue: {issue_en}

I am writing to respectfully request a reconsideration of my Instagram account status.

Account Information:
- Username: @{username}
- Full Name: {full_name}
- Email Address: {email}
- Country: {country}
{phone_line_en}
- Account Created: {year_created}

Issue Type: {issue_en}

Issue Description:
{description}

I sincerely assure you that I have not violated any of Instagram's Community Guidelines or Terms of Service. My account represents my true identity and legitimate activities. I kindly request that you review my account status and take the appropriate action to restore access.

I am fully prepared to provide any additional documentation or information that may assist in the review process.

Thank you for your time and consideration.

Respectfully,
{full_name}
{email}
{date_en}
"""
    return appeal_ar.strip(), appeal_en.strip()


def generate_recovery_appeal(username, ban_reason, extra_info="") -> str:
    date_en = datetime.now().strftime("%B %d, %Y")
    reason_en = BAN_REASONS_EN.get(ban_reason, ban_reason)
    extra = f"\nAdditional context: {extra_info}" if extra_info else ""

    appeal = f"""To the Instagram Trust & Safety Team,

Date: {date_en}
Subject: Urgent Account Recovery Request

Dear Instagram Support,

I am writing to urgently request the recovery of my Instagram account (@{username}), which has been disabled.

Reason for Disabling (as I understand it): {reason_en}
{extra}

I want to clarify the following:

1. I am the original and sole owner of this account.
2. I have never intentionally violated Instagram's Terms of Service or Community Guidelines.
3. The content I have posted is original, respectful, and compliant with your policies.
4. I understand and respect Instagram's rules and will ensure full compliance going forward.

I am prepared to verify my identity through any method required, including:
- Government-issued ID submission
- Video selfie verification
- Email or phone confirmation

This account is extremely important to my personal/professional life, and losing access has significantly impacted me. I sincerely request your team to reconsider this decision and restore my account.

Please let me know if you need any additional information to process this request.

Thank you for your understanding and prompt attention to this matter.

Sincerely,
@{username}
{date_en}
"""
    return appeal.strip()


def generate_verification_request(username, full_name, email, account_type,
                                   social_links, activities, followers_count,
                                   media_coverage) -> str:
    date_en = datetime.now().strftime("%B %d, %Y")
    account_type_en = "Personal Account" if account_type == "شخصي" else "Business / Brand Account"

    request = f"""To the Instagram Verification Team,

Date: {date_en}
Subject: Verification Badge Request — @{username}

Dear Instagram Team,

I am writing to formally request the verification badge (blue checkmark) for my Instagram account.

Account Details:
- Username: @{username}
- Full Name: {full_name}
- Email Address: {email}
- Account Type: {account_type_en}
- Approximate Followers: {followers_count}

Online Presence & Social Profiles:
{social_links}

Description of Activities & Public Interest:
{activities}

Media Coverage & References:
{media_coverage}

I am a recognized public figure / notable entity with a significant online presence. My account is authentic, unique, complete, and notable — meeting all four of Instagram's criteria for verification. My identity and prominence can be verified through the links and references provided above.

I understand that verification is intended for accounts at risk of impersonation, and I sincerely believe my account qualifies based on the above information.

I would greatly appreciate your team's consideration of this request.

Thank you for your time and consideration.

Respectfully,
{full_name}
@{username}
{date_en}
"""
    return request.strip()
