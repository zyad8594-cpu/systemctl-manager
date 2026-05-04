# 🐧 Systemd Manager | مدير خدمات النظام الاحترافي

### [Arabic Below | العربية في الأسفل](#العربية)

**Systemd Manager** is a professional, comprehensive GUI tool for managing the **systemd** ecosystem on Linux. It is designed to provide a premium user experience with granular control over units, processes, and overall system state.

---

## ✨ Key Features (English)

- **🌍 Full Internationalization (i18n)**: 100% bilingual interface (Arabic & English). Automatically detects system locale.
- **🗃️ Premium UI**: Modern card-based layout with full Dark Mode support and responsive design.
- **🛠️ Granular Control**: Start, Stop, Restart, Enable, Disable, Mask, Unmask, Kill, and Reset-Failed at a touch.
- **🔗 Dependency Tree**: Foldable, interactive visualization of service hierarchies.
- **🌍 Environment Studio**: Advanced manager to view, set, and unset system-wide environment variables.
- **📝 Unit File Editor**: Direct editing of unit files with automatic safe overrides and daemon-reload.
- **📊 Smart Property Inspector**: Detailed Key-Value tables for unit properties (`systemctl show`) with dynamic modification.
- **📋 Live Journal Logs**: Real-time log streaming from `journalctl` with extended selection support.
- **⚡ Bulk Operations**: Intelligent multi-select mode for collective management of dozens of units.
- **🚀 High Performance**: 100% asynchronous execution engine prevents UI freezing during heavy system operations.

---

## 🚀 Installation

### 1. Developer Setup:
```bash
git clone https://github.com/zyad/systemctl-manager.git
cd systemctl-manager
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Quick CLI Setup (Bash):
```bash
chmod +x setup.sh
./setup.sh
```

---

<a name="العربية"></a>

# 🐧 مدير خدمات النظام الاحترافي | Systemd Manager

تطبيق **Systemd Manager** هو أداة رسومية احترافية وشاملة لإدارة نظام **systemd** على بيئات Linux. تم تصميمه ليوفر تجربة مستخدم فائقة السلاسة مع دعم كامل لأدق تفاصيل التحكم في الوحدات والعمليات والنظام بأكمله.

---

## ✨ المميزات الرئيسية (العربية)

- **🌍 دعم عالمي للغات (i18n)**: واجهة كاملة ثنائية اللغة (عربي وإنجليزي) مع التعرف التلقائي على لغة النظام.
- **🗃️ واجهة بطاقات حديثة (Premium UI)**: عرض الوحدات بتصميم عصري يعتمد على البطاقات التفاعلية مع دعم كامل للوضع الداكن.
- **🛠️ تحكم كامل ودقيق**: بدء، إيقاف، إعادة تشغيل، تمكين، تعطيل، حجب (Mask)، إلغاء حجب، وإنهاء قسري (Kill).
- **🔗 إدارة الاعتماديات (Dependency Tree)**: عرض شجري تفاعلي لجميع اعتماديات الخدمة مع إمكانية الطي والفتح.
- **🌍 مدير بيئة النظام (Environment Studio)**: واجهة متكاملة لعرض وتعديل وحذف متغيرات بيئة النظام بشكل تفاعلي.
- **📝 محرر ملفات الخدمة (Unit Editor)**: تعديل ملفات الوحدات مباشرة وحفظها عبر نسخ Override آمنة مع إجراء `Daemon-Reload` تلقائياً.
- **📊 عرض الخصائص الذكي (Smart Properties)**: عرض وتحرير خصائص الوحدات بجداول منظمة (Key-Value) مع دعم لعمليات `set-property`.
- **📋 سجلات لحظية (Live Logs)**: جلب السجلات من `journalctl` وعرضها في قائمة منظمة وسهلة التصفح.
- **⚡ عمليات جماعية (Bulk Operations)**: وضع تحديد ذكي لإدارة عشرات الوحدات وتنفيذ العمليات عليها دفعة واحدة.
- **🚀 أداء غير متزامن (Async Engine)**: تنفيذ جميع أوامر النظام في الخلفية لضمان استجابة الواجهة بنسبة 100%.

---

## 🚀 التثبيت

### 1. تثبيت مشروع المطور:
```bash
git clone https://github.com/zyad/systemctl-manager.git
cd systemctl-manager
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. التثبيت السريع (Quick Setup - Bash):
```bash
chmod +x setup.sh
./setup.sh
```

---

## 🏗️ التصميم الهندسي (Architecture)

تم بناء المشروع باستخدام نمط **MVC** (Model-View-Controller) لضمان فصل منطق النظام عن واجهة المستخدم.

## 📄 الترخيص (License)

هذا المشروع متاح تحت رخصة **MIT**. لمزيد من التفاصيل، راجع ملف [LICENSE](LICENSE).

---

### 👨‍💻 المساهمة والتطوير
تم التطوير بواسطة **Zyad**. نرحب بجميع المساهمات والاقتراحات لتطوير البرنامج!