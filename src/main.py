#!/usr/bin/env python3
"""
نقطة الدخول الرئيسية للتطبيق
"""

import sys
import os

# إضافة المسار الأب للـ Python path (لتشغيل الملف مباشرة)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from src.controllers.app_controller import AppController
from src.views.main_window import MainWindow

def main():
    if os.geteuid() != 0:
        print("Warning: It is recommended to run this application as root for full systemctl capabilities.")
        
    app = QApplication(sys.argv)
    
    # MVC Initialization
    controller = AppController()
    view = MainWindow(controller)
    
    # Internationalization (i18n)
    from PySide6.QtCore import QTranslator, QLocale
    translator = QTranslator()
    # جلب مسار ملفات الترجمة
    translations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "translations")
    locale = QLocale.system().name() # e.g. 'ar_SA' or 'en_US'
    
    if translator.load(f"app_{locale}", translations_path):
        app.installTranslator(translator)
    elif translator.load(f"app_{locale.split('_')[0]}", translations_path): # Try 'ar' if 'ar_SA' fails
        app.installTranslator(translator)

    # Connecting controller signals to view
    controller.loading_state_changed.connect(view.set_loading_state)
    controller.error_occurred.connect(view.show_error)
    controller.message_occurred.connect(view.show_message)
    controller.show_environment_dialog.connect(view.open_environment_dialog)
    controller.show_advanced_builder_dialog.connect(view.open_advanced_builder_dialog)
    controller.show_service_details_dialog.connect(view.open_service_details_dialog)
    
    is_dark = QGuiApplication.palette().window().color().lightness() < 128
    view.apply_theme(is_dark)
    view.show()
    
    controller.refresh_services()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()