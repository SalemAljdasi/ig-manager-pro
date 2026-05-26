[app]
  title = IG Manager Pro
  package.name = igmanagerpro
  package.domain = com.igmanager.pro
  source.dir = .
  source.include_exts = py,png,jpg,kv,atlas,json
  source.exclude_dirs = tests,bin,.git,__pycache__,.github,igapp
  version = 4.0

  requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,pillow,certifi,urllib3,charset-normalizer,idna

  orientation = portrait
  fullscreen = 0

  android.api = 33
  android.minapi = 21
  android.ndk = 25b
  android.ndk_api = 21
  android.archs = arm64-v8a
  android.private_storage = True
  android.accept_sdk_license = True
  android.allow_backup = True
  android.skip_update = False
  android.enable_androidx = True
  android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

  android.presplash_color = #0A0A1A

  [buildozer]
  log_level = 2
  warn_on_root = 1
  