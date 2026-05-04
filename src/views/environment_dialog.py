from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHeaderView, QMenu, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont

class EnvironmentDialog(QDialog):
    def __init__(self, env_text: str, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.setWindowTitle(self.tr("بيئة النظام (System Environment)"))
        self.resize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([self.tr("المتغير (Variable)"), self.tr("القيمة (Value)")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.table.setStyleSheet(
            "QTableWidget { background-color: transparent; border: none; }"
            "QTableWidget QLineEdit { padding: 0px; margin: 0px; background-color: #2d2d2d; color: #3498db; }"
        )
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_add = QPushButton(self.tr(" إضافة متغير"))
        btn_add.setIcon(QIcon.fromTheme("list-add"))
        btn_add.clicked.connect(self.add_variable)
        btn_layout.addWidget(btn_add)
        
        btn_save = QPushButton(self.tr(" حفظ التغييرات"))
        btn_save.setIcon(QIcon.fromTheme("document-save"))
        btn_save.clicked.connect(self.save_environment)
        btn_layout.addWidget(btn_save)
        
        btn_layout.addStretch()
        
        btn_close = QPushButton(self.tr("إغلاق"))
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        self.load_data(env_text)

    def load_data(self, env_text: str):
        self.table.setRowCount(0)
        self._original_env = {}
        
        lines = env_text.strip().split('\n')
        for line in lines:
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip()
                self._original_env[key] = val
                
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                key_item = QTableWidgetItem(key)
                key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 0, key_item)
                self.table.setItem(row, 1, QTableWidgetItem(val))

    def show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item: return
        
        menu = QMenu(self)
        action_edit = menu.addAction(QIcon.fromTheme("document-edit"), self.tr("تعديل (Edit)"))
        action_del = menu.addAction(QIcon.fromTheme("edit-delete"), self.tr("حذف (Delete)"))
        
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        row = item.row()
        if action == action_edit:
            self.table.editItem(self.table.item(row, 1))
        elif action == action_del:
            self.table.removeRow(row)

    def add_variable(self):
        text, ok = QInputDialog.getText(self, self.tr("إضافة متغير بيئة"), self.tr("أدخل اسم المتغير (Variable Name):"))
        if ok and text:
            row = self.table.rowCount()
            self.table.insertRow(row)
            key_item = QTableWidgetItem(text.strip())
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, key_item)
            val_item = QTableWidgetItem("")
            self.table.setItem(row, 1, val_item)
            self.table.scrollToBottom()
            self.table.editItem(val_item)

    def save_environment(self):
        current_env = {}
        for row in range(self.table.rowCount()):
            key_item = self.table.item(row, 0)
            val_item = self.table.item(row, 1)
            if key_item and val_item:
                current_env[key_item.text().strip()] = val_item.text().strip()
                
        # Find changes
        to_set = {}
        to_unset = []
        
        # 1. New or modified
        for k, v in current_env.items():
            if self._original_env.get(k) != v:
                to_set[k] = v
                
        # 2. Deleted
        for k in self._original_env:
            if k not in current_env:
                to_unset.append(k)
                
        if not to_set and not to_unset:
            QMessageBox.information(self, self.tr("معلومات"), self.tr("لم تقم بإجراء أي تعديلات."))
            return
            
        success_all = True
        error_msg = ""
        
        # Set
        for k, v in to_set.items():
            if not self.backend.set_environment_variable(k, v):
                success_all = False
                error_msg += self.tr("فشل في ضبط {key}\n").format(key=k)
                
        # Unset
        for k in to_unset:
            if not self.backend.unset_environment_variable(k):
                success_all = False
                error_msg += self.tr("فشل في حذف {key}\n").format(key=k)
                
        if success_all:
            QMessageBox.information(self, self.tr("نجاح"), self.tr("تم تحديث بيئة النظام بنجاح."))
            # Reload to sync with actual system state
            new_env = self.backend.show_environment()
            self.load_data(new_env)
        else:
            QMessageBox.critical(self, self.tr("خطأ"), self.tr("حدثت أخطاء أثناء التحديث:\n{msg}").format(msg=error_msg))

