"""
شريط بحث وتصفية متقدم مع أزرار تصنيف
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QButtonGroup, QComboBox
from PySide6.QtCore import Signal, Qt

class FilterBar(QWidget):
    # إشارة ترسل النص والفلتر النوعي
    filter_changed = Signal(str)
    category_changed = Signal(str)
    type_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # الصف الأول: البحث
        search_layout = QHBoxLayout()
        search_label = QLabel(self.tr("بحث:"))
        search_label.setToolTip(self.tr("ابحث عن خدمة هنا"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self.tr("اكتب اسم الخدمة أو الوصف..."))
        self.search_edit.setToolTip(self.tr("قم بكتابة اسم الخدمة (مثل: apache2) لتصفية النتائج فوراً"))
        self.search_edit.textChanged.connect(self.filter_changed.emit)
        
        type_label = QLabel(self.tr("نوع الوحدة:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([self.tr("الكل (All)"), "Service", "Socket", "Timer", "Target", "Mount", "Path"])
        self.type_combo.currentTextChanged.connect(self.type_changed.emit)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(type_label)
        search_layout.addWidget(self.type_combo)
        main_layout.addLayout(search_layout)
        
        # الصف الثاني: الأزرار المصنفة (Chips)
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(8)
        
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        
        filters = [
            (self.tr("الكل"), "all"),
            (self.tr("نشط"), "active"),
            (self.tr("متوقف"), "inactive"),
            (self.tr("فاشل"), "failed"),
            (self.tr("ممكن"), "enabled"),
            (self.tr("معطل"), "disabled"),
        ]
        
        for text, cat_id in filters:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("cat_id", cat_id)
            btn.setObjectName("FilterChip")
            btn.setToolTip(self.tr("الفلترة بواسطة: {text}").format(text=text))
            if cat_id == "all":
                btn.setChecked(True)
            
            self.group.addButton(btn)
            chips_layout.addWidget(btn)
            btn.clicked.connect(lambda checked=False, id=cat_id: self.category_changed.emit(id))
            
        chips_layout.addStretch()
        main_layout.addLayout(chips_layout)

