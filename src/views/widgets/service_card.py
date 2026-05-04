from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMenu, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction, QPainter, QFontMetrics

class ElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._full_text = text
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(50)

    def setText(self, text: str):
        self._full_text = text
        self.update_elided_text()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_elided_text()

    def update_elided_text(self):
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self._full_text, Qt.ElideRight, self.width())
        super().setText(elided)

class ServiceCard(QFrame):
    action_triggered = Signal(str, str)  # (action_type, service_name)
    details_requested = Signal(str)      # (service_name)

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self.setObjectName("ServiceCard")
        self.setFrameShape(QFrame.StyledPanel)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)

        # Checkbox for bulk selection
        self.check_target = QCheckBox()
        self.check_target.setCursor(Qt.PointingHandCursor)
        self.check_target.setStyleSheet("margin-right: 5px;")
        self.check_target.hide()
        layout.addWidget(self.check_target)

        # Icon based on unit type
        icon_map = {
            'service': 'application-x-executable',
            'socket': 'network-wired',
            'timer': 'preferences-system-time',
            'mount': 'drive-harddisk',
            'target': 'system-run',
            'path': 'folder'
        }
        icon_name = icon_map.get(service.unit_type.lower(), 'application-x-executable')
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon.fromTheme(icon_name).pixmap(24, 24))
        layout.addWidget(self.icon_label)

        # Status indicator
        self.status_dot = QLabel("●")
        self.status_dot.setFixedWidth(20)
        self.status_dot.setStyleSheet(f"color: {service.status_color}; font-size: 20px;")
        layout.addWidget(self.status_dot)

        # Text info
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.name_label = ElidedLabel(service.name)
        self.name_label.setObjectName("ServiceName")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        
        self.desc_label = ElidedLabel(service.description)
        self.desc_label.setObjectName("ServiceDesc")
        self.desc_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        
        text_layout.addWidget(self.name_label)
        text_layout.addWidget(self.desc_label)
        layout.addLayout(text_layout, 1)

        # Status text badge
        self.status_badge = QLabel(service.status_text)
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setStyleSheet(f"background-color: {service.status_color}22; color: {service.status_color}; border-radius: 4px; padding: 4px 8px; font-weight: bold;")
        layout.addWidget(self.status_badge)
        
        # We removed the menu_btn, using ContextMenuEvent instead.
        
        self.setToolTip(self.tr("خدمة: {name}\nانقر بالزر الأيمن لعرض الخيارات، أو نقراً مزدوجاً للتفاصيل").format(name=service.name))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        # الأساسية
        menu.addAction(QIcon.fromTheme("edit-select-all"), self.tr("تحديد متعدد (Select)")).triggered.connect(
            lambda: self.action_triggered.emit("multi_select", self.service.name)
        )
        menu.addSeparator()

        if self.service.is_active:
            stop_action = menu.addAction(QIcon.fromTheme("media-playback-stop"), self.tr("إيقاف"))
            stop_action.triggered.connect(lambda: self.action_triggered.emit("stop_service", self.service.name))
        else:
            start_action = menu.addAction(QIcon.fromTheme("media-playback-start"), self.tr("بدء"))
            start_action.triggered.connect(lambda: self.action_triggered.emit("start_service", self.service.name))

        restart_action = menu.addAction(QIcon.fromTheme("system-reboot"), self.tr("إعادة تشغيل"))
        restart_action.triggered.connect(lambda: self.action_triggered.emit("restart_service", self.service.name))

        reload_action = menu.addAction(QIcon.fromTheme("view-refresh"), self.tr("إعادة تحميل"))
        reload_action.triggered.connect(lambda: self.action_triggered.emit("reload_service", self.service.name))

        menu.addSeparator()

        if self.service.is_enabled:
            disable_action = menu.addAction(QIcon.fromTheme("emblem-unreadable"), self.tr("تعطيل"))
            disable_action.triggered.connect(lambda: self.action_triggered.emit("disable_service", self.service.name))
        else:
            enable_action = menu.addAction(QIcon.fromTheme("emblem-ok"), self.tr("تمكين"))
            enable_action.triggered.connect(lambda: self.action_triggered.emit("enable_service", self.service.name))

        menu.addSeparator()

        # عمليات متقدمة
        advanced_menu = menu.addMenu(QIcon.fromTheme("preferences-system"), self.tr("عمليات متقدمة"))
        
        advanced_actions = [
            (self.tr("عزل (Isolate)"), "isolate_unit", "security-high"),
            (self.tr("تنظيف (Clean)"), "clean_unit", "edit-clear"),
            (self.tr("تجميد (Freeze)"), "freeze_unit", "media-playback-pause"),
            (self.tr("استئناف (Thaw)"), "thaw_unit", "media-playback-start"),
            (self.tr("حجب (Mask)"), "mask_service", "security-low"),
            (self.tr("إلغاء حجب"), "unmask_service", "security-high"),
            (self.tr("إعادة ضبط الفشل"), "reset_failed_service", "edit-clear-all"),
            (self.tr("إنهاء قسري (Kill)"), "kill_service", "process-stop"),
        ]

        for text, action_id, icon_name in advanced_actions:
            action = advanced_menu.addAction(QIcon.fromTheme(icon_name), text)
            action.triggered.connect(lambda checked=False, aid=action_id: self.action_triggered.emit(aid, self.service.name))

        menu.addSeparator()
        details_action = menu.addAction(QIcon.fromTheme("utilities-system-monitor"), self.tr("تفاصيل"))
        details_action.triggered.connect(lambda: self.details_requested.emit(self.service.name))

        menu.exec(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        self.details_requested.emit(self.service.name)
