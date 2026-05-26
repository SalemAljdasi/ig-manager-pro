"""
IG Manager Pro - Instagram Account Checker
Uses public HTTP requests only (no login, no API key required)
"""

import requests
import json
import time
import re
from typing import Optional

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 11; Samsung Galaxy S21 Ultra) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT":             "1",
    "Connection":      "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

TIMEOUT = 15
SESSION = None


def _get_session() -> requests.Session:
    global SESSION
    if SESSION is None:
        SESSION = requests.Session()
        SESSION.headers.update(HEADERS)
    return SESSION


def check_account(username: str) -> dict:
    """
    Fetch public data for an Instagram username.
    Returns a structured result dict.
    """
    username = username.strip().lstrip("@").lower()
    result = {
        "username":   username,
        "status":     "unknown",
        "followers":  0,
        "following":  0,
        "posts":      0,
        "is_private": False,
        "is_verified":False,
        "shadowban":  False,
        "full_name":  "",
        "bio":        "",
        "profile_pic":"",
        "error":      None,
        "raw":        {},
    }

    if not username or len(username) < 1:
        result["error"] = "Invalid username"
        return result

    # ── Strategy 1: JSON endpoint ────────────────────────────────────────────
    try:
        session = _get_session()
        url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
        resp = session.get(url, timeout=TIMEOUT, allow_redirects=True)

        if resp.status_code == 200:
            try:
                data = resp.json()
                user = (
                    data.get("graphql", {}).get("user")
                    or data.get("data", {}).get("user")
                    or {}
                )
                if user:
                    return _parse_user(user, username, result)
            except (json.JSONDecodeError, ValueError):
                pass

        elif resp.status_code == 404:
            result["status"] = "disabled"
            result["error"]  = "Account not found (404)"
            return result

        elif resp.status_code == 429:
            result["status"] = "unknown"
            result["error"]  = "Rate limited – try again later"
            return result

    except requests.RequestException as e:
        result["error"] = str(e)

    # ── Strategy 2: Scrape HTML page ─────────────────────────────────────────
    try:
        session = _get_session()
        url  = f"https://www.instagram.com/{username}/"
        resp = session.get(url, timeout=TIMEOUT)

        if resp.status_code == 404:
            result["status"] = "disabled"
            result["error"]  = "Account not found"
            return result

        html = resp.text

        # Extract shared_data JSON from HTML
        match = re.search(
            r'window\._sharedData\s*=\s*(\{.+?\});</script>', html, re.DOTALL
        )
        if match:
            try:
                shared = json.loads(match.group(1))
                user   = (
                    shared.get("entry_data", {})
                          .get("ProfilePage", [{}])[0]
                          .get("graphql", {})
                          .get("user", {})
                )
                if user:
                    return _parse_user(user, username, result)
            except (json.JSONDecodeError, IndexError, KeyError):
                pass

        # Minimal HTML signals
        if "Sorry, this page" in html or "Page Not Found" in html:
            result["status"] = "disabled"
            return result

        if "This account is private" in html:
            result["status"]     = "private"
            result["is_private"] = True
            return result

        if f"@{username}" in html or username in html:
            result["status"] = "active"
            return result

    except requests.RequestException as e:
        result["error"] = str(e)

    return result


def _parse_user(user: dict, username: str, base: dict) -> dict:
    """Parse a user JSON object into a normalised result dict."""
    followers  = user.get("edge_followed_by", {}).get("count", 0)
    following  = user.get("edge_follow",      {}).get("count", 0)
    posts      = user.get("edge_owner_to_timeline_media", {}).get("count", 0)
    is_private = user.get("is_private", False)
    is_verified= user.get("is_verified", False)

    if is_private:
        status = "private"
    elif followers == 0 and posts == 0 and not is_private:
        status = "shadowban"
    else:
        status = "active"

    base.update({
        "username":    username,
        "status":      status,
        "followers":   followers,
        "following":   following,
        "posts":       posts,
        "is_private":  is_private,
        "is_verified": is_verified,
        "shadowban":   status == "shadowban",
        "full_name":   user.get("full_name", ""),
        "bio":         user.get("biography", ""),
        "profile_pic": user.get("profile_pic_url_hd", "") or user.get("profile_pic_url", ""),
        "raw":         user,
        "error":       None,
    })
    return base


def check_accounts_bulk(usernames: list, progress_cb=None, stop_flag=None) -> list:
    """
    Check multiple usernames with optional progress callback.

    Args:
        usernames:   list of username strings
        progress_cb: callable(current, total, result_dict) for UI updates
        stop_flag:   callable() → bool, returns True to abort
    """
    results = []
    total   = len(usernames)

    for idx, username in enumerate(usernames):
        if stop_flag and stop_flag():
            break

        result = check_account(username)
        results.append(result)

        if progress_cb:
            progress_cb(idx + 1, total, result)

        # Polite delay to avoid rate limiting
        time.sleep(1.2)

    return results
