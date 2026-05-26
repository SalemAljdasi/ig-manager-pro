import requests
import json
import random
import re
from assets.theme import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_API_URL

INSTAGRAM_BASE = "https://www.instagram.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/112.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "X-IG-App-ID": "936619743392459",
}


def send_telegram_notification(message: str) -> bool:
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
        }
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def check_account(username: str) -> dict:
    username = username.strip().lower().lstrip("@")
    result = {
        "username": username,
        "status": "unknown",
        "followers": 0,
        "following": 0,
        "posts": 0,
        "is_verified": False,
        "is_private": False,
        "guessed_email": "",
        "security_score": 0,
        "security_level": "unknown",
        "error": None,
    }
    try:
        url = f"{INSTAGRAM_BASE}/{username}/?__a=1&__d=dis"
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code == 404:
            result["status"] = "disabled"
            result["error"] = "الحساب غير موجود أو معطل"
            _notify_if_alert(username, "disabled")
            result["security_score"], result["security_level"] = calculate_security_score(result)
            return result
        if r.status_code == 429:
            result["error"] = "تم تجاوز حد الطلبات — حاول لاحقاً"
            return result
        if r.status_code != 200:
            result["error"] = f"خطأ في الاتصال: {r.status_code}"
            return result

        try:
            data = r.json()
            user = data.get("graphql", {}).get("user") or data.get("data", {}).get("user", {})
        except Exception:
            user = {}

        if not user:
            url2 = f"{INSTAGRAM_BASE}/api/v1/users/web_profile_info/?username={username}"
            try:
                r2 = requests.get(url2, headers=HEADERS, timeout=12)
                data2 = r2.json()
                user = data2.get("data", {}).get("user", {})
            except Exception:
                user = {}

        if user:
            result["followers"] = user.get("edge_followed_by", {}).get("count", 0) or user.get("follower_count", 0)
            result["following"] = user.get("edge_follow", {}).get("count", 0) or user.get("following_count", 0)
            result["posts"] = (user.get("edge_owner_to_timeline_media", {}).get("count", 0)
                               or user.get("media_count", 0))
            result["is_verified"] = bool(user.get("is_verified", False))
            result["is_private"] = bool(user.get("is_private", False))

            if result["is_private"]:
                result["status"] = "private"
            elif result["is_verified"]:
                result["status"] = "verified"
            else:
                result["status"] = "active"

            result["guessed_email"] = guess_email(username, user)
        else:
            result["status"] = _infer_status_from_response(r)

        if result["status"] in ("disabled", "shadowban", "hacked"):
            _notify_if_alert(username, result["status"])

        result["security_score"], result["security_level"] = calculate_security_score(result)
        return result

    except requests.exceptions.ConnectionError:
        result["error"] = "لا يوجد اتصال بالإنترنت"
        return result
    except requests.exceptions.Timeout:
        result["error"] = "انتهت مهلة الاتصال"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def _infer_status_from_response(response) -> str:
    text = response.text.lower()
    if "page not found" in text or "sorry, this page" in text:
        return "disabled"
    if "this account is private" in text:
        return "private"
    return "active"


def guess_email(username: str, user_data: dict = None) -> str:
    if user_data:
        email = user_data.get("email") or user_data.get("public_email", "")
        if email:
            return email
    email_suffixes = [
        f"{username}@gmail.com",
        f"{username}@yahoo.com",
        f"{username}@hotmail.com",
        f"{username}@outlook.com",
    ]
    return email_suffixes[0]


def calculate_security_score(account_data: dict) -> tuple:
    score = 50
    followers = account_data.get("followers", 0)
    following = account_data.get("following", 0)
    posts = account_data.get("posts", 0)
    is_verified = account_data.get("is_verified", False)
    status = account_data.get("status", "unknown")

    if status == "active":
        score += 15
    elif status in ("disabled", "hacked"):
        score -= 30
    elif status == "shadowban":
        score -= 20

    if is_verified:
        score += 20

    if followers > 1000:
        score += 10
    elif followers > 100:
        score += 5

    ratio = (following / max(followers, 1))
    if ratio > 10:
        score -= 15
    elif ratio > 3:
        score -= 5
    else:
        score += 5

    if posts > 50:
        score += 10
    elif posts > 10:
        score += 5
    elif posts == 0:
        score -= 10

    score = max(0, min(100, score))

    if score <= 40:
        level = "weak"
    elif score <= 70:
        level = "medium"
    else:
        level = "good"

    return score, level


def _notify_if_alert(username: str, status: str):
    status_messages = {
        "disabled": f"🔴 تنبيه: الحساب @{username} معطّل!",
        "shadowban": f"⚠️ تنبيه: الحساب @{username} في وضع الشادوبان!",
        "hacked": f"🚨 خطر: الحساب @{username} قد يكون مخترقاً!",
    }
    message = status_messages.get(status)
    if message:
        msg = (
            f"<b>🔔 IG Manager Pro v4.0</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{message}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<i>تم الفحص تلقائياً بواسطة IG Manager Pro</i>"
        )
        send_telegram_notification(msg)


def check_accounts_bulk(usernames: list, progress_callback=None) -> list:
    results = []
    total = len(usernames)
    for i, username in enumerate(usernames):
        if not username.strip():
            continue
        result = check_account(username.strip())
        results.append(result)
        if progress_callback:
            progress_callback(i + 1, total, result)
    return results


def send_test_notification() -> bool:
    message = (
        "<b>✅ IG Manager Pro v4.0</b>\n"
        "━━━━━━━━━━━━━━━\n"
        "🎉 إشعارات تلغرام تعمل بشكل صحيح!\n"
        "تم ربط التطبيق بنجاح مع بوت تلغرام.\n"
        "━━━━━━━━━━━━━━━\n"
        "<i>IG Manager Pro © 2025</i>"
    )
    return send_telegram_notification(message)
