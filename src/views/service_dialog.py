from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QGroupBox, QFormLayout,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem, QMenu, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont
from src.utils.async_runner import AsyncRunner
from src.utils.logger import setup_logger

class ServiceDialog(QDialog):
    action_requested = Signal(str, str)
    
    
    def __init__(self, service, backend, parent=None):
        super().__init__(parent)
        self.service = service
        self.backend = backend
        self.async_runner = AsyncRunner()
        self.logger = setup_logger()
        self.setWindowTitle(self.tr("تفاصيل الوحدة: {name}").format(name=service.name))
        self.resize(800, 600)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Tab Widget
        self.tabs = QTabWidget()
        
        # 1. التبويب العام (Info & Logs)
        self.tab_general = QWidget()
        self.setup_general_tab()
        self.tabs.addTab(self.tab_general, self.tr("عام و السجلات"))
        
        # 2. تبويب الخصائص (Properties)
        self.tab_properties = QWidget()
        self.setup_properties_tab()
        self.tabs.addTab(self.tab_properties, self.tr("الخصائص (Properties)"))
        
        # 3. تبويب ملف الوحدة (Unit File)
        self.tab_unit_file = QWidget()
        self.setup_unit_file_tab()
        self.tabs.addTab(self.tab_unit_file, self.tr("ملف الخدمة (Unit File)"))
        
        # 4. تبويب الاعتماديات (Dependencies)
        self.tab_dependencies = QWidget()
        self.setup_dependencies_tab()
        self.tabs.addTab(self.tab_dependencies, self.tr("الاعتماديات (Dependencies)"))
        
        main_layout.addWidget(self.tabs)
        
        # Footer buttons
        footer_layout = QHBoxLayout()
        
        actions = []
        if self.service.is_active:
            actions.append((self.tr("إيقاف"), "media-playback-stop", "stop_service"))
        else:
            actions.append((self.tr("بدء"), "media-playback-start", "start_service"))
            
        actions.append((self.tr("إعادة تشغيل"), "system-reboot", "restart_service"))
        
        if self.service.is_enabled:
            actions.append((self.tr("تعطيل"), "process-stop", "disable_service"))
        else:
            actions.append((self.tr("تمكين"), "system-run", "enable_service"))
        
        for text, icon, action_id in actions:
            btn = QPushButton(f" {text}")
            btn.setIcon(QIcon.fromTheme(icon))
            btn.clicked.connect(lambda checked, a_id=action_id: self.action_requested.emit(a_id, self.service.name))
            footer_layout.addWidget(btn)
            
        footer_layout.addStretch()
        
        btn_close = QPushButton(self.tr("إغلاق"))
        btn_close.clicked.connect(self.accept)
        btn_close.setFixedWidth(100)
        footer_layout.addWidget(btn_close)
        
        main_layout.addLayout(footer_layout)
        
        self.setLayout(main_layout)
        
        # تحميل البيانات غير المتزامنة
        self.load_logs()
        self.load_properties()
        self.load_unit_file()
        self.load_dependencies()
        
    def setup_general_tab(self):
        layout = QVBoxLayout(self.tab_general)
        
        info_group = QGroupBox(self.tr("معلومات الخدمة"))
        form_layout = QFormLayout()
        
        labels = [
            (self.tr("الاسم:"), self.service.name),
            (self.tr("الوصف:"), self.service.description),
            (self.tr("الحالة:"), self.service.status_text),
            (self.tr("تمكين عند الإقلاع:"), self.tr("ممكن") if self.service.is_enabled else self.tr("معطل")),
            (self.tr("حالة التحميل:"), self.service.load_state),
            (self.tr("الحالة الفرعية:"), self.service.sub_state),
        ]
        
        for label_text, value in labels:
            val_label = QLabel(value)
            val_label.setStyleSheet("font-weight: normal;")
            if label_text == self.tr("الحالة:"):
                val_label.setStyleSheet(f"font-weight: bold; color: {self.service.status_color};")
            
            row_label = QLabel(label_text)
            row_label.setStyleSheet("font-weight: bold;")
            form_layout.addRow(row_label, val_label)
            
        info_group.setLayout(form_layout)
        layout.addWidget(info_group)
        
        logs_group = QGroupBox(self.tr("آخر السجلات (journalctl)"))
        logs_layout = QVBoxLayout()
        self.logs_list = QListWidget()
        self.logs_list.setFont(QFont("Monospace", 9))
        self.logs_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.logs_list.setWordWrap(False)
        self.logs_list.setStyleSheet(
            "QListWidget::item { padding: 4px; border-bottom: 1px solid #333333; }"
            "QListWidget::item:selected { background-color: #2d2d2d; color: #3498db; }"
        )
        logs_layout.addWidget(self.logs_list)
        
        btn_refresh_logs = QPushButton(self.tr(" تحديث السجلات"))
        btn_refresh_logs.setIcon(QIcon.fromTheme("view-refresh"))
        btn_refresh_logs.clicked.connect(self.load_logs)
        logs_layout.addWidget(btn_refresh_logs)
        
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)

    def setup_properties_tab(self):
        layout = QVBoxLayout(self.tab_properties)
        self.properties_table = QTableWidget()
        self.properties_table.setColumnCount(2)
        self.properties_table.setHorizontalHeaderLabels([self.tr("الخاصية (Key)"), self.tr("القيمة (Value)")])
        self.properties_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.properties_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.properties_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.properties_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.properties_table.verticalHeader().setVisible(False)
        self.properties_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.properties_table.customContextMenuRequested.connect(self.show_properties_context_menu)
        self.properties_table.setStyleSheet(
            "QTableWidget { background-color: transparent; border: none; }"
            "QTableWidget QLineEdit { padding: 0px; margin: 0px; background-color: #2d2d2d; color: #3498db; }"
        )
        layout.addWidget(self.properties_table)
        
        btn_layout = QHBoxLayout()
        btn_add_prop = QPushButton(self.tr(" إضافة خاصية جديدة"))
        btn_add_prop.setIcon(QIcon.fromTheme("list-add"))
        btn_add_prop.clicked.connect(self.add_new_property)
        btn_layout.addWidget(btn_add_prop)
        
        btn_save_props = QPushButton(self.tr(" حفظ التعديلات على الخصائص (Set-Property)"))
        btn_save_props.setIcon(QIcon.fromTheme("document-save"))
        btn_save_props.clicked.connect(self.save_properties)
        btn_layout.addWidget(btn_save_props)
        
        layout.addLayout(btn_layout)

    def setup_unit_file_tab(self):
        layout = QVBoxLayout(self.tab_unit_file)
        self.unit_file_text = QTextEdit()
        self.unit_file_text.setReadOnly(False)
        self.unit_file_text.setFont(QFont("Monospace", 10))
        layout.addWidget(self.unit_file_text)
        
        btn_save_unit = QPushButton(self.tr(" حفظ التعديلات على ملف الخدمة"))
        btn_save_unit.setIcon(QIcon.fromTheme("document-save"))
        btn_save_unit.clicked.connect(self.save_unit_file_content)
        layout.addWidget(btn_save_unit)

    def setup_dependencies_tab(self):
        layout = QVBoxLayout(self.tab_dependencies)
        self.dependencies_tree = QTreeWidget()
        self.dependencies_tree.setHeaderHidden(True)
        self.dependencies_tree.setAnimated(True)
        self.dependencies_tree.setFont(QFont("Monospace", 10))
        self.dependencies_tree.setStyleSheet("QTreeWidget { background-color: transparent; border: none; }")
        layout.addWidget(self.dependencies_tree)

    # --- Methods for Async Data Loading ---

    def load_logs(self):
        def fetch(): return self.backend.get_service_logs(self.service.name, lines=100)
        def on_finished(logs):
            self.logs_list.clear()
            for line in logs.strip().split('\n'):
                if line.strip():
                    self.logs_list.addItem(line)
            if self.logs_list.count() > 0:
                self.logs_list.scrollToBottom()
        def on_error(err): self.logs_list.addItem(self.tr("خطأ: {err}").format(err=err))
        self.async_runner.run(fetch, on_finished, on_error)

    def show_properties_context_menu(self, pos):
        item = self.properties_table.itemAt(pos)
        if not item: return
        
        menu = QMenu(self)
        action_edit = menu.addAction(QIcon.fromTheme("document-edit"), self.tr("تعديل (Edit)"))
        action_del = menu.addAction(QIcon.fromTheme("edit-delete"), self.tr("حذف (Delete)"))
        
        action = menu.exec(self.properties_table.viewport().mapToGlobal(pos))
        row = item.row()
        if action == action_edit:
            self.properties_table.editItem(self.properties_table.item(row, 1))
        elif action == action_del:
            # We flag this for deletion internally by making it empty on save, 
            # and physically removing the row.
            key = self.properties_table.item(row, 0).text()
            if self._original_properties.get(key) is not None:
                self._original_properties[key] = "" # track deletion if it was original
            self.properties_table.removeRow(row)

    def add_new_property(self):
        text, ok = QInputDialog.getText(self, self.tr("إضافة شخصية جديدة"), self.tr("أدخل اسم الخاصية (Property Key):"))
        if ok and text:
            row = self.properties_table.rowCount()
            self.properties_table.insertRow(row)
            key_item = QTableWidgetItem(text.strip())
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
            self.properties_table.setItem(row, 0, key_item)
            val_item = QTableWidgetItem("")
            self.properties_table.setItem(row, 1, val_item)
            self.properties_table.scrollToBottom()
            self.properties_table.editItem(val_item)

    def load_properties(self):
        def fetch(): return self.backend.get_service_properties(self.service.name)
        def on_finished(props): 
            self.properties_table.setRowCount(0)
            self._original_properties = {}
            lines = props.strip().split('\n')
            for line in lines:
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    self._original_properties[key] = val
                    row = self.properties_table.rowCount()
                    self.properties_table.insertRow(row)
                    key_item = QTableWidgetItem(key)
                    key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable) # Key non-editable
                    self.properties_table.setItem(row, 0, key_item)
                    self.properties_table.setItem(row, 1, QTableWidgetItem(val))
        def on_error(err): 
            self.properties_table.setRowCount(1)
            self.properties_table.setItem(0, 0, QTableWidgetItem("Error"))
            self.properties_table.setItem(0, 1, QTableWidgetItem(str(err)))
        self.async_runner.run(fetch, on_finished, on_error)

    def save_properties(self):
        changed = {}
        current_keys = set()
        for row in range(self.properties_table.rowCount()):
            key_item = self.properties_table.item(row, 0)
            val_item = self.properties_table.item(row, 1)
            if not key_item or not val_item: continue
            key, val = key_item.text().strip(), val_item.text().strip()
            current_keys.add(key)
            if self._original_properties.get(key) != val:
                changed[key] = val
                
        # Check for deleted properties
        for orig_k, orig_v in self._original_properties.items():
            if orig_k not in current_keys:
                # User deleted the row completely
                changed[orig_k] = "" 
        
        if not changed:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("معلومات"), self.tr("لم تقم بإجراء أي تعديلات على الخصائص."))
            return
            
        def process(): return self.backend.set_service_properties(self.service.name, changed)
        def on_finished(res):
            success, msg = res
            from PySide6.QtWidgets import QMessageBox
            if success:
                QMessageBox.information(self, self.tr("نجاح"), msg)
                self.load_properties()
            else:
                QMessageBox.critical(self, self.tr("خطأ (تأكد أن الخاصية تدعم التعديل الديناميكي)"), msg)
        self.async_runner.run(process, on_finished)

    def load_unit_file(self):
        def fetch(): return self.backend.get_service_file(self.service.name)
        def on_finished(content): self.unit_file_text.setPlainText(content)
        def on_error(err): self.unit_file_text.setPlainText(f"خطأ: {err}")
        self.async_runner.run(fetch, on_finished, on_error)
        
    def save_unit_file_content(self):
        new_content = self.unit_file_text.toPlainText()
        def process(): return self.backend.save_unit_file(self.service.name, new_content)
        def on_finished(res):
            success, msg = res
            from PySide6.QtWidgets import QMessageBox
            if success:
                QMessageBox.information(self, self.tr("نجاح"), msg)
            else:
                QMessageBox.critical(self, self.tr("خطأ"), msg)
                
        self.async_runner.run(process, on_finished)
        
    def load_dependencies(self):
        def fetch(): return self.backend.get_unit_dependencies(self.service.name)
        def on_finished(content):
            self.dependencies_tree.clear()
            lines = content.strip().split('\n')
            if not lines or not lines[0].strip(): return
            
            root_item = QTreeWidgetItem([lines[0].strip()])
            root_item.setIcon(0, QIcon.fromTheme("applications-system"))
            self.dependencies_tree.addTopLevelItem(root_item)
            
            stack = [(0, root_item)]
            for line in lines[1:]:
                stripped = line.lstrip(' ●├─└│ ')
                if not stripped: continue
                idx = line.find(stripped)
                
                while stack and stack[-1][0] >= idx:
                    stack.pop()
                    
                parent_item = stack[-1][1] if stack else root_item
                item = QTreeWidgetItem([stripped])
                item.setIcon(0, QIcon.fromTheme("system-run"))
                parent_item.addChild(item)
                stack.append((idx, item))
                
            self.dependencies_tree.expandAll()
        def on_error(err): 
            self.dependencies_tree.clear()
            QTreeWidgetItem(self.dependencies_tree, [self.tr("خطأ: {err}").format(err=err)])
            
        self.async_runner.run(fetch, on_finished, on_error)
