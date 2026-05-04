from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QPushButton, QMessageBox, QStatusBar,
    QLineEdit, QApplication, QMenuBar, QMenu, QLabel, QCheckBox,
    QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction
import os
from src.views.widgets.filter_bar import FilterBar
from src.views.widgets.service_card import ServiceCard
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.controllers.app_controller import AppController

class MainWindow(QMainWindow):
    
    def __init__(self, controller: 'AppController'):
        super().__init__()
        self.controller = controller
        self.model = controller.model
        self.is_dark_mode = False
        self.setWindowTitle(self.tr("مدير خدمات Systemd"))
        self.resize(1000, 800)
        
        # ضبط أيقونة النافذة
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setup_menu_bar()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        
        # العنصر المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        main_layout.addWidget(self.progress_bar)
        
        # شريط العلوي (فلتر + ثيم)
        top_bar = QHBoxLayout()
        self.filter_bar = FilterBar()
        self.filter_bar.filter_changed.connect(self.model.set_filter)
        self.filter_bar.category_changed.connect(self.model.set_category)
        self.filter_bar.type_changed.connect(self.model.set_unit_type)
        top_bar.addWidget(self.filter_bar, 1)
        
        self.btn_theme_toggle = QPushButton()
        self.btn_theme_toggle.setFixedSize(40, 40)
        self.btn_theme_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_theme_toggle.setToolTip(self.tr("تبديل وضع الألوان (فاتح/داكن)"))
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.btn_theme_toggle, 0, Qt.AlignTop)
        
        main_layout.addLayout(top_bar)
        
        # وصف نوع الوحدة وأدوات التحديد الجماعي
        bulk_layout = QHBoxLayout()
        self.unit_desc_label = QLabel(self.tr("الوحدات: جميع الأنواع"))
        self.unit_desc_label.setStyleSheet("color: #3498db; font-weight: bold; font-size: 14px;")
        
        self.btn_cancel_multi = QPushButton()
        self.btn_cancel_multi.setIcon(QIcon.fromTheme("go-previous"))
        self.btn_cancel_multi.setFixedSize(30, 30)
        self.btn_cancel_multi.setToolTip(self.tr("إلغاء وضع التحديد"))
        self.btn_cancel_multi.clicked.connect(lambda: self.set_multi_select_mode(False))
        self.btn_cancel_multi.hide()
        
        self.check_select_all = QCheckBox("تحديد الكل")
        self.check_select_all.stateChanged.connect(self.toggle_select_all)
        self.check_select_all.hide()
        
        self.lbl_selection_count = QLabel(self.tr("محدد: 0"))
        self.lbl_selection_count.setStyleSheet("color: #e67e22; font-weight: bold; margin: 0 10px;")
        
        self.btn_bulk_options = QPushButton("⋮")
        self.btn_bulk_options.setFixedSize(30, 30)
        self.btn_bulk_options.setToolTip(self.tr("الأوامر الجماعية"))
        
        def handle_bulk_action(action_key, display_name):
            if not self.btn_cancel_multi.isVisible():
                self.set_multi_select_mode(True)
            else:
                self.execute_bulk(action_key, display_name)

        bulk_menu = QMenu(self.btn_bulk_options)
        bulk_menu.addAction(QIcon.fromTheme("media-playback-start"), "تشغيل المحدد", lambda: handle_bulk_action("start", "تشغيل"))
        bulk_menu.addAction(QIcon.fromTheme("media-playback-stop"), "إيقاف المحدد", lambda: handle_bulk_action("stop", "إيقاف"))
        bulk_menu.addAction(QIcon.fromTheme("system-reboot"), "إعادة تشغيل المحدد", lambda: handle_bulk_action("restart", "إعادة تشغيل"))
        self.btn_bulk_options.setMenu(bulk_menu)
        
        bulk_layout.addWidget(self.btn_cancel_multi)
        bulk_layout.addWidget(self.unit_desc_label)
        bulk_layout.addStretch()
        bulk_layout.addWidget(self.lbl_selection_count)
        bulk_layout.addWidget(self.check_select_all)
        bulk_layout.addWidget(self.btn_bulk_options)
        main_layout.addLayout(bulk_layout)
        
        # ربط الوصف بتغييرات الفلتر
        self.filter_bar.type_changed.connect(self.update_unit_description)
        
        # منطقة التمرير
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setObjectName("MainScrollArea")
        
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area)
        
        # أزرار سفلية سريعة
        bottom_layout = QHBoxLayout()
        self.btn_refresh = QPushButton(self.tr(" تحديث القائمة"))
        self.btn_refresh.setIcon(QIcon.fromTheme("view-refresh"))
        self.btn_refresh.clicked.connect(self.controller.refresh_services)
        
        self.btn_daemon_reload = QPushButton(self.tr(" تحديث مدير النظام (Reload)"))
        self.btn_daemon_reload.setToolTip(self.tr("systemctl daemon-reload"))
        self.btn_daemon_reload.setIcon(QIcon.fromTheme("system-reboot")) # استعارة آيقونة تقريبية
        self.btn_daemon_reload.clicked.connect(self.controller.daemon_reload)
        
        bottom_layout.addWidget(self.btn_refresh)
        bottom_layout.addWidget(self.btn_daemon_reload)
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.model.modelReset.connect(self.update_cards)
        self.update_system_status()
        
        # Refresh system status every 30 seconds
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_system_status)
        self.status_timer.start(30000)
        # self.update_selection_count()

    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        
        view_menu = menu_bar.addMenu(self.tr("عرض"))
        
        env_action = QAction(QIcon.fromTheme("preferences-system"), self.tr("بيئة النظام (Environment)"), self)
        env_action.triggered.connect(self.controller.show_environment)
        view_menu.addAction(env_action)
        
        advanced_action = QAction(QIcon.fromTheme("utilities-terminal"), self.tr("منشئ الأوامر المتقدم"), self)
        advanced_action.triggered.connect(self.controller.open_advanced_command_builder)
        view_menu.addAction(advanced_action)
        
        system_menu = menu_bar.addMenu(self.tr("النظام"))
        power_actions = [
            (self.tr("إعادة التشغيل"), "reboot", "system-reboot"),
            (self.tr("إيقاف التشغيل"), "poweroff", "system-shutdown"),
            (self.tr("تعليق (Suspend)"), "suspend", "system-suspend"),
            (self.tr("سبات (Hibernate)"), "hibernate", "system-suspend-hibernate"),
        ]
        
        for text, action_key, icon in power_actions:
            action = QAction(QIcon.fromTheme(icon), text, self)
            action.triggered.connect(lambda checked, a=action_key, t=text: self.confirm_and_execute_power(a, t))
            system_menu.addAction(action)

    def show_loading(self, show: bool):
        if show:
            self.progress_bar.show()
        else:
            self.progress_bar.hide()

    def update_system_status(self):
        status = self.controller.backend.is_system_running()
        self.statusBar.clearMessage()
        self.statusBar.showMessage(self.tr("حالة النظام: {status} | إجمالي الوحدات: {count}").format(status=status.upper(), count=len(self.model._filtered_services)))

    def toggle_theme(self):
        self.apply_theme(not self.is_dark_mode)

    def apply_theme(self, is_dark: bool):
        self.is_dark_mode = is_dark
        self.btn_theme_toggle.setText("🌙" if not is_dark else "☀️")
        self.load_styles()

    def load_styles(self):
        style_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                qss = f.read()
                if self.is_dark_mode:
                    qss += self.get_dark_overrides()
                # تطبيق الستايل على كامل التطبيق لتوحيد الثيم
                QApplication.instance().setStyleSheet(qss)

    def get_dark_overrides(self) -> str:
        return """
        /* Premium Dark Mode Overrides */
        QMainWindow, QDialog { background-color: #121212; }
        QWidget { color: #e0e0e0; }
        
        #MainScrollArea, #MainScrollArea > QWidget > QWidget { background-color: transparent; }
        
        #ServiceCard { background-color: #1e1e1e; border-color: #333333; }
        #ServiceCard:hover { background-color: #282828; border-color: #3498db; }
        
        #ServiceName { color: #ffffff; }
        #ServiceDesc { color: #a0a0a0; }
        
        QPushButton { background-color: #1e1e1e; color: #e0e0e0; border-color: #333333; }
        QPushButton:hover { background-color: #2d2d2d; border-color: #555555; }
        QPushButton:pressed { background-color: #121212; }
        
        QPushButton#MenuButton { color: #a0a0a0; }
        QPushButton#MenuButton:hover { color: #3498db; background-color: rgba(52, 152, 219, 0.15); }
        
        QPushButton#FilterChip { background-color: #1e1e1e; border-color: #333333; color: #a0a0a0; }
        QPushButton#FilterChip:hover { background-color: #2d2d2d; border-color: #555555; color: #e0e0e0; }
        QPushButton#FilterChip:checked { background-color: #3498db; color: #ffffff; border-color: #3498db; }
        
        QLineEdit { background-color: #121212; color: #ffffff; border-color: #333333; }
        QLineEdit:focus { border-color: #3498db; background-color: #1e1e1e; }
        
        QGroupBox { border-color: #333333; color: #e0e0e0; }
        QGroupBox::title { color: #b0b0b0; }
        
        QTextEdit { background-color: #000000; color: #00ff00; border-color: #333333; } /* Retro terminal look for logs */
        
        QTabWidget::pane { background-color: #1e1e1e; border-color: #333333; }
        QTabBar::tab { background-color: #121212; color: #a0a0a0; border-color: #333333; }
        QTabBar::tab:selected { background-color: #1e1e1e; color: #3498db; }
        QTabBar::tab:hover:!selected { background-color: #2d2d2d; color: #e0e0e0; }
        
        QStatusBar { background-color: #121212; color: #888888; border-top-color: #333333; }
        
        QMenu { background-color: #1e1e1e; color: #e0e0e0; border-color: #333333; }
        QMenu::item { color: #e0e0e0; }
        QMenu::item:selected { background-color: #2d2d2d; color: #3498db; }
        """

    def update_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        services = self.model._filtered_services
        for service in services:
            card = ServiceCard(service)
            card.action_triggered.connect(self.on_card_action)
            card.details_requested.connect(self.controller.show_service_details)
            card.check_target.stateChanged.connect(self.update_selection_count)
            self.cards_layout.addWidget(card)
        self.update_system_status()
        self.check_select_all.setChecked(False)

    def set_multi_select_mode(self, enabled: bool):
        self.btn_cancel_multi.setVisible(enabled)
        self.check_select_all.setVisible(enabled)
        self.unit_desc_label.setVisible(not enabled)

        for i in range(self.cards_layout.count()):
            w = self.cards_layout.itemAt(i).widget()
            if w:
                w.check_target.setVisible(enabled)
                if not enabled:
                    w.check_target.blockSignals(True)
                    w.check_target.setChecked(False)
                    w.check_target.blockSignals(False)
        
        if not enabled:
            self.check_select_all.blockSignals(True)
            self.check_select_all.setChecked(False)
            self.check_select_all.blockSignals(False)
            
        self.update_selection_count()

    def update_selection_count(self):
        count = sum(1 for i in range(self.cards_layout.count()) if self.cards_layout.itemAt(i).widget() and self.cards_layout.itemAt(i).widget().check_target.isChecked())
        total = self.cards_layout.count()
        self.lbl_selection_count.setText(f"محدد: {count} / {total}")

    def toggle_select_all(self, state):
        for i in range(self.cards_layout.count()):
            w = self.cards_layout.itemAt(i).widget()
            if w:
                w.check_target.setChecked(state != 0)

    def execute_bulk(self, action: str, display_name: str):
        selected_units = []
        for i in range(self.cards_layout.count()):
            widget = self.cards_layout.itemAt(i).widget()
            if widget and widget.check_target.isChecked():
                selected_units.append(widget.service.name)
        
        if not selected_units:
            self.show_error("لم يتم تحديد أي وحدة!")
            return
            
        reply = QMessageBox.question(
            self, "تأكيد جماعي", 
            f"هل أنت متأكد من تنفيذ أمر '{display_name}' على {len(selected_units)} وحدة؟",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.controller.execute_bulk_action(action, selected_units)

    def update_unit_description(self, unit_type: str):
        descriptions = {
            "all": "جميع الوحدات: يعرض كافة أنواع النظام المكتشفة.",
            "service": "الخدمات (Services): برامج وعمليات تعمل في الخلفية بشكل دائم.",
            "socket": "المقابس (Sockets): نقاط اتصال لتفعيل الخدمات عند الطلب عبر الشبكة أو الجذور.",
            "timer": "المؤقتات (Timers): مسؤولة عن تشغيل مهام أخرى في أوقات مجدولة (بديل لـ Cron).",
            "target": "الأهداف (Targets): تمثل مجموعات منطقية لا تقوم بشيء بنفسها، لكنها تربط وحدات أخرى لتشكيل حالة نظام.",
            "path": "المسارات (Paths): وحدات تقوم بمراقبة ملفات أو مجلدات وتفعل خدمة عند حدوث تغيير.",
            "mount": "نقاط التركيب (Mounts): تدير تركيب وفصل أنظمة الملفات (أقراص/مسارات خارجية)."
        }
        self.unit_desc_label.setText(descriptions.get(unit_type, "وحدات نظام systemd."))

    def on_card_action(self, action_id: str, service_name: str):
        action_map = {
            "start_service": self.controller.start_service,
            "stop_service": self.controller.stop_service,
            "restart_service": self.controller.restart_service,
            "reload_service": self.controller.reload_service,
            "enable_service": self.controller.enable_service,
            "disable_service": self.controller.disable_service,
            "mask_service": self.controller.mask_service,
            "unmask_service": self.controller.unmask_service,
            "kill_service": self.controller.kill_service,
        }
        if action_id == "reset_failed_service": self.controller.reset_failed_service(service_name)
        elif action_id == "clean_unit": self.controller.clean_unit(service_name)
        elif action_id == "freeze_unit": self.controller.freeze_unit(service_name)
        elif action_id == "thaw_unit": self.controller.thaw_unit(service_name)
        elif action_id == "isolate_unit": self.controller.isolate_unit(service_name)
        elif action_id == "multi_select":
            self.set_multi_select_mode(True)
            for i in range(self.cards_layout.count()):
                w = self.cards_layout.itemAt(i).widget()
                if w and w.service.name == service_name:
                    w.check_target.setChecked(True)
                    break
        elif action_id in action_map:
            action_map[action_id](service_name)

    def show_error(self, message: str):
        QMessageBox.critical(self, "خطأ", message)
        
    def show_message(self, message: str):
        self.statusBar.showMessage(message)

    def set_loading_state(self, is_loading: bool, message: str):
        self.show_loading(is_loading)
        if message:
            self.statusBar.showMessage(message)

    def confirm_and_execute_power(self, action: str, display_name: str):
        reply = QMessageBox.warning(
            self,
            "تأكيد الإجراء",
            f"هل أنت متأكد أنك تريد تنفيذ أمر '{display_name}' للنظام بأكمله؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.controller.execute_power_action(action)

    def open_environment_dialog(self, env_text: str):
        from src.views.environment_dialog import EnvironmentDialog
        dialog = EnvironmentDialog(env_text, self.controller.backend, self)
        dialog.exec()

    def open_advanced_builder_dialog(self, backend: object):
        from src.views.advanced_command_dialog import AdvancedCommandDialog
        dialog = AdvancedCommandDialog(backend, self)
        dialog.exec()

    def open_service_details_dialog(self, service: object, backend: object):
        from src.views.service_dialog import ServiceDialog
        dialog = ServiceDialog(service, backend, self)
        dialog.action_requested.connect(self.on_card_action)
        dialog.exec()
    #