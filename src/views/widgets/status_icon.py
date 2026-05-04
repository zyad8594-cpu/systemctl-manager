from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

class StatusIcon(QWidget):
    def __init__(self, status="inactive", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel()
        self.set_status(status)
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def set_status(self, status):
        # رموز ملونة بدوائر حديثة
        if status == "active":
            self.label.setText("●")
            self.label.setStyleSheet("color: #2ecc71; font-size: 18px; margin-right: 5px;")
        elif status == "failed" or status == "error":
            self.label.setText("●")
            self.label.setStyleSheet("color: #e74c3c; font-size: 18px; margin-right: 5px;")
        else:
            self.label.setText("○")
            self.label.setStyleSheet("color: #95a5a6; font-size: 18px; margin-right: 5px;")
