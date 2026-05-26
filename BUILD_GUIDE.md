# IG Manager Pro — دليل بناء APK خطوة بخطوة

---

## المتطلبات الأساسية قبل البدء

| الأداة | الإصدار المطلوب | ملاحظة |
|--------|-----------------|--------|
| Python | 3.10 أو 3.11 (⚠️ ليس 3.12+) | Buildozer لا يدعم 3.12 بعد |
| Ubuntu | 20.04 أو 22.04 LTS | يُنصح باستخدام Linux أو WSL2 |
| Java JDK | 17 | android SDK يطلبه |
| Git | أي إصدار | لسحب python-for-android |
| RAM | 8 GB+ | البناء يستهلك ذاكرة كبيرة |
| مساحة Disk | 15 GB+ | NDK + SDK + cache |

---

## الخطوة 1: تجهيز بيئة Linux (Ubuntu/WSL2)

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات الأساسية
sudo apt install -y \
    python3 python3-pip python3-venv \
    git zip unzip curl wget \
    build-essential \
    libssl-dev libffi-dev \
    libsqlite3-dev \
    zlib1g-dev \
    openjdk-17-jdk \
    autoconf libtool pkg-config \
    libncurses5-dev libncursesw5-dev

# تحقق من Java
java -version   # يجب أن يظهر: openjdk 17
```

---

## الخطوة 2: تثبيت Buildozer

```bash
# أنشئ بيئة Python افتراضية (مُستحسن)
python3 -m venv ~/kivy_env
source ~/kivy_env/bin/activate

# تثبيت Buildozer + Kivy + KivyMD
pip install --upgrade pip
pip install buildozer
pip install kivy==2.3.0 kivymd==1.2.0
pip install cython==0.29.36   # مطلوب لبعض وصفات p4a
```

---

## الخطوة 3: نسخ مجلد المشروع

```bash
# انسخ مجلد ig-manager-pro إلى جهازك
# مثال إذا كنت تستخدم Git:
git clone <repo-url>
cd ig-manager-pro

# أو انسخ المجلد يدوياً ثم انتقل إليه
cd /path/to/ig-manager-pro
```

---

## الخطوة 4: إنشاء أصول الأيقونة (اختياري)

```bash
# أنشئ مجلد assets إذا لم يكن موجوداً
mkdir -p assets

# إنشاء أيقونة بسيطة (512×512) باستخدام Python
python3 - <<'EOF'
try:
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (512, 512), (168, 85, 247, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([80, 80, 432, 432], fill=(6, 182, 212, 255))
    draw.text((180, 200), "IG", fill=(255,255,255,255))
    img.save("assets/icon.png")
    img.save("assets/presplash.png")
    print("Icons created!")
except ImportError:
    print("PIL not installed — copy any 512x512 PNG as assets/icon.png")
EOF

# أو ثبّت pillow ثم أعد تشغيل الأمر
pip install pillow
```

---

## الخطوة 5: بناء APK (Debug)

```bash
# من داخل مجلد ig-manager-pro:
source ~/kivy_env/bin/activate

# البناء الأول — يستغرق 20-40 دقيقة لتحميل NDK/SDK
buildozer android debug

# عند اكتمال البناء ستجد APK في:
# bin/igmanagerpro-1.0.0-arm64-v8a-debug.apk
ls -lh bin/
```

> ⚠️ **مهم**: البناء الأول يُحمِّل Android NDK (~1.5 GB) و SDK (~500 MB)
> تأكد من اتصال إنترنت مستقر وقرص صلب كافٍ.

---

## الخطوة 6: تثبيت APK على الهاتف

### طريقة A — عبر USB (ADB)

```bash
# تثبيت ADB
sudo apt install android-tools-adb

# تفعيل "USB Debugging" على هاتف Samsung S21 Ultra:
# الإعدادات → حول الهاتف → رقم الإصدار (اضغط 7 مرات)
# الإعدادات → خيارات المطور → تصحيح USB = تشغيل

# توصيل الهاتف عبر USB ثم:
adb devices          # يجب أن يظهر رقم الجهاز
adb install bin/igmanagerpro-1.0.0-arm64-v8a-debug.apk
```

### طريقة B — نقل الملف

```bash
# انسخ APK إلى /sdcard/Download
adb push bin/igmanagerpro-1.0.0-arm64-v8a-debug.apk /sdcard/Download/

# ثم افتح APK من مدير الملفات على الهاتف
# (تأكد من تفعيل "تثبيت تطبيقات من مصادر غير معروفة")
```

---

## الخطوة 7: بناء APK للإصدار (Release) — اختياري

```bash
# أنشئ مفتاح توقيع (مرة واحدة فقط)
keytool -genkey -v \
  -keystore my-release-key.keystore \
  -alias igmanager \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# عدّل buildozer.spec وأضف:
# android.release_artifact = apk
# android.keystore = my-release-key.keystore
# android.keystore_alias = igmanager
# android.keystore_password = YOUR_PASSWORD

buildozer android release
# ينتج: bin/igmanagerpro-1.0.0-arm64-v8a-release.apk
```

---

## استكشاف الأخطاء الشائعة

| الخطأ | الحل |
|-------|------|
| `SDK not found` | `buildozer android update` أو احذف `~/.buildozer/` وأعد البناء |
| `NDK not found` | شغّل `buildozer android debug 2>&1 \| grep NDK` للتحقق من المسار |
| `cython error` | `pip install cython==0.29.36` (ليس أحدث) |
| `JAVA_HOME not set` | `export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64` |
| `Permission denied /sdcard` | تأكد من صلاحيات READ/WRITE_EXTERNAL_STORAGE في buildozer.spec |
| APK يُثبَّت لكن يتعطل | شغّل `adb logcat -s python` لرؤية أخطاء Python |
| بطء الفحص في Scanner | طبيعي — delay 1.2 ثانية بين كل حساب لتجنب Rate Limiting |

---

## هيكل الملفات النهائي

```
ig-manager-pro/
├── main.py                  ← نقطة الدخول الرئيسية
├── buildozer.spec           ← إعدادات البناء
├── requirements.txt         ← المكتبات المطلوبة
├── BUILD_GUIDE.md           ← هذا الدليل
│
├── assets/
│   ├── theme.py             ← ألوان ومتغيرات التصميم
│   ├── icon.png             ← أيقونة التطبيق (512×512)
│   └── presplash.png        ← شاشة البداية
│
├── models/
│   └── database.py          ← SQLite: حفظ وقراءة البيانات
│
├── core/
│   ├── checker.py           ← فحص حسابات Instagram عبر HTTP
│   └── appeals.py           ← توليد رسائل الاستئناف الرسمية
│
└── screens/
    ├── dashboard.py         ← الشاشة الرئيسية + إحصائيات + رسم بياني
    ├── scanner.py           ← فحص فردي وجماعي + شريط تقدم
    ├── reports.py           ← تقارير + تصدير HTML/JSON
    └── appeals.py           ← نموذج الاستئناف + توليد ثنائي اللغة
```

---

## ملاحظات أمان ✅

- التطبيق **لا يخزن** أي كلمات مرور أو بيانات دخول
- الفحص يعتمد على **HTTP requests للبيانات العامة فقط**
- البيانات تُحفظ محلياً على الجهاز فقط (SQLite)
- لا يوجد خادم خارجي أو إرسال بيانات للإنترنت
- **قانوني 100%**: يجلب فقط ما هو متاح علناً بدون تسجيل دخول

---

## للمساعدة

- [Buildozer Docs](https://buildozer.readthedocs.io/)
- [KivyMD Docs](https://kivymd.readthedocs.io/)
- [python-for-android](https://python-for-android.readthedocs.io/)
