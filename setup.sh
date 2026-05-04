#!/bin/bash

# 🐧 Systemd Manager - Bash Setup Script
# نص برمجى لتثبيت وإعداد مدير خدمات النظام

set -e

echo "🚀 بدء عملية الإعداد لـ Systemd Manager..."

# تحديد المسار الحالي للمشروع
APP_DIR=$(pwd)

# 1. التحقق من وجود بايثون
if ! command -v python3 &> /dev/null; then
    echo "❌ خطأ: Python 3 غير مثبت على نظامك. يرجى تثبيته للمتابعة."
    exit 1
fi

# 2. تثبيت المتطلبات
echo "📦 تثبيت المكتبات المطلوبة (PySide6)..."
pip install -r requirements.txt --upgrade

# 3. إعداد الأيقونة
echo "🎨 تثبيت أيقونة التطبيق..."
mkdir -p ~/.local/share/icons/
cp "$APP_DIR/src/resources/app_icon.png" ~/.local/share/icons/systemctl-manager.png

# 4. إعداد اختصار سطح المكتب
echo "🖥️ إعداد اختصار سطح المكتب..."
mkdir -p ~/.local/share/applications/

# تحديد المسارات
EXEC_PATH="/usr/bin/python3 $APP_DIR/src/main.py"
ICON_PATH="systemctl-manager"

# تحديث ملف desktop لتعديل المسار
cat <<EOF > ~/.local/share/applications/systemctl-manager.desktop
[Desktop Entry]
Name=Systemd Manager
Comment=Professional systemd unit and service management suite
Exec=$EXEC_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=System;Settings;
Keywords=systemd;systemctl;service;manager;linux;
StartupNotify=true
EOF

chmod +x ~/.local/share/applications/systemctl-manager.desktop

# 4. تحديث قاعدة بيانات التطبيقات
echo "🔄 تحديث قاعدة بيانات التطبيقات..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications/
fi

echo "✅ تم التثبيت والإعداد بنجاح!"
echo "💡 يمكنك الآن تشغيل البرنامج من قائمة التطبيقات الخاصة بك."
