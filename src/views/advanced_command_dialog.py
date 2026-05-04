from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QCheckBox, QPushButton, 
    QTextEdit, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.services.systemd_backend import SystemdBackend
from src.utils.async_runner import AsyncRunner

class AdvancedCommandDialog(QDialog):
    def __init__(self, backend: SystemdBackend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.async_runner = AsyncRunner()
        self.setWindowTitle(self.tr("باني الأوامر المتقدم (Advanced Command Builder)"))
        self.resize(700, 600)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 1. Target & Action
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel(self.tr("الوحدة الهدف (Target):")))
        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText(self.tr("مثال: apache2.service"))
        self.target_edit.textChanged.connect(self.update_command_preview)
        target_layout.addWidget(self.target_edit)
        
        target_layout.addWidget(QLabel(self.tr("الأمر (Command):")))
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "start", "stop", "restart", "reload", "status", 
            "enable", "disable", "mask", "unmask", "isolate", 
            "kill", "clean", "freeze", "thaw", "reset-failed"
        ])
        self.action_combo.currentTextChanged.connect(self.update_command_preview)
        target_layout.addWidget(self.action_combo)
        main_layout.addLayout(target_layout)
        
        # 2. Options Checkboxes
        options_group = QGroupBox(self.tr("خيارات متقدمة (Options)"))
        options_layout = QGridLayout(options_group)
        
        self.checkboxes = {
            "--now": QCheckBox("--now (Start/stop immediately)"),
            "--force": QCheckBox("--force (Override)"),
            "--dry-run": QCheckBox("--dry-run (Simulate)"),
            "--no-block": QCheckBox("--no-block (Don't wait)"),
            "--wait": QCheckBox("--wait (Wait for unit)"),
            "--user": QCheckBox("--user (User mode)"),
            "--system": QCheckBox("--system (System mode)"),
            "--global": QCheckBox("--global"),
            "--runtime": QCheckBox("--runtime (Temporarily)")
        }
        
        row, col = 0, 0
        for flag, chk in self.checkboxes.items():
            chk.stateChanged.connect(self.update_command_preview)
            options_layout.addWidget(chk, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        main_layout.addWidget(options_group)
        
        # 3. Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel(self.tr("الأمر الذي سيتم إنشاؤه:")))
        self.preview_text = QLineEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Monospace", 12))
        self.preview_text.setStyleSheet("background-color: #1e1e1e; color: #3498db; font-weight: bold;")
        preview_layout.addWidget(self.preview_text)
        main_layout.addLayout(preview_layout)
        
        # 4. Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_execute = QPushButton(self.tr("تنفيذ الأمر المخصص"))
        self.btn_execute.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.btn_execute.clicked.connect(self.execute_command)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_execute)
        main_layout.addLayout(btn_layout)
        
        # 5. Output Log
        main_layout.addWidget(QLabel(self.tr("سجل التنفيذ (Output):")))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Monospace", 10))
        main_layout.addWidget(self.output_text)

        self.update_command_preview()

    def update_command_preview(self):
        cmd = ["systemctl"]
        for flag, chk in self.checkboxes.items():
            if chk.isChecked():
                cmd.append(flag)
                
        cmd.append(self.action_combo.currentText())
        
        target = self.target_edit.text().strip()
        if target:
            cmd.append(target)
            
        self.preview_text.setText(" ".join(cmd))

    def execute_command(self):
        cmd_str = self.preview_text.text()
        self.output_text.append(f"\n> {cmd_str}")
        self.btn_execute.setEnabled(False)
        
        # We need to construct the list
        cmd_list = cmd_str.split()
        
        def run_task():
            # Run manually using backend's helper
            return self.backend._run_cmd(cmd_list, use_root=True)

        def on_finished(result):
            code, out, err = result
            if out:
                self.output_text.append(out)
            if err:
                self.output_text.append(self.tr("أخطاء: {err}").format(err=err))
            self.output_text.append(self.tr("رمز الخروج: {code}").format(code=code))
            
            # Scroll to bottom
            scrollbar = self.output_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            self.btn_execute.setEnabled(True)

        self.async_runner.run(run_task, on_finished)
