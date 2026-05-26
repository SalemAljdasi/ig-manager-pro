[app]
# ── Identity ──────────────────────────────────────────────────────────────────
title           = IG Manager Pro
package.name    = igmanagerpro
package.domain  = com.igmanager
source.dir      = .
source.include_exts = py,kv,png,jpg,jpeg,ttf,db,json,txt

# ── Version ───────────────────────────────────────────────────────────────────
version         = 1.0.0

# ── Requirements ─────────────────────────────────────────────────────────────
# IMPORTANT: No Rust-compiled packages (no pydantic-core, cryptography, etc.)
requirements    = python3,\
                  kivy==2.3.0,\
                  kivymd==1.2.0,\
                  requests,\
                  certifi,\
                  urllib3,\
                  charset-normalizer,\
                  idna,\
                  sqlite3

# ── Orientation & UI ──────────────────────────────────────────────────────────
orientation     = portrait
fullscreen      = 0
icon.filename   = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png

# ── Android settings ──────────────────────────────────────────────────────────
[buildozer]
log_level       = 2
warn_on_root    = 1

[android]
android.api             = 33
android.minapi          = 30
android.ndk             = 25c
android.sdk             = 33
android.ndk_api         = 21
android.arch            = arm64-v8a
android.release_artifact = apk

android.permissions = \
    INTERNET,\
    READ_EXTERNAL_STORAGE,\
    WRITE_EXTERNAL_STORAGE,\
    ACCESS_NETWORK_STATE

# KivyMD requires Material icons font
android.add_aars = 

# Extra Java sources (not needed for pure Python/Kivy)
# android.add_src =

# p4a (python-for-android) options
p4a.branch       = develop
p4a.bootstrap    = sdl2
p4a.local_recipes = 

# Gradle
android.gradle_dependencies = 
android.enable_androidx    = True

# ── iOS (disabled) ────────────────────────────────────────────────────────────
[ios]
# Not targeted
ios.kivy_ios_url   = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# ── Debug signing ─────────────────────────────────────────────────────────────
# For release: set android.release_artifact and provide keystore details
# android.keystore   = /path/to/your.keystore
# android.keystore_alias = myalias
# android.keystore_password = mypassword
