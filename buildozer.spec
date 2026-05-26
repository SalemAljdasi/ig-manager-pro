[app]
title = IG Manager Pro
package.name = igmanagerpro
package.domain = com.igmanager.pro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.exclude_dirs = tests, bin, .git, __pycache__, .github
version = 4.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,pillow,sqlite3,certifi,charset-normalizer,idna,urllib3

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.api = 33
android.minapi = 30
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.private_storage = True
android.accept_sdk_license = True
android.allow_backup = True
android.skip_update = False
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.gradle_dependencies =
android.enable_androidx = True

# App icon & presplash
#icon.filename = %(source.dir)s/assets/icon.png
#presplash.filename = %(source.dir)s/assets/presplash.png
presplash.color = #0A0A1A
android.presplash_color = #0A0A1A

# Buildozer bootstrap
p4a.branch = master

[app:ios]
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false
