"""
التحكم الرئيسي بين الـ Model والـ View
إدارة جميع عمليات نظام systemd
"""
from PySide6.QtCore import QObject, Signal
from src.models.service_list_model import ServiceListModel
from src.services.systemd_backend import SystemdBackend
from src.utils.async_runner import AsyncRunner
from src.utils.logger import setup_logger

class AppController(QObject):
    loading_state_changed = Signal(bool, str)
    error_occurred = Signal(str)
    message_occurred = Signal(str)
    
    show_environment_dialog = Signal(str)
    show_advanced_builder_dialog = Signal(object)
    show_service_details_dialog = Signal(object, object)

    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.backend = SystemdBackend()
        self.model = ServiceListModel()
        self.async_runner = AsyncRunner()
        
    def refresh_services(self):
        self.loading_state_changed.emit(True, "يتم جلب الوحدات، يرجى الانتظار...")
                
        self.async_runner.run(
            func=self.backend.list_all_services, 
            on_finished=lambda s: (
                self.model.set_services(s), 
                self.loading_state_changed.emit(False, "")
            ), 
            on_error=lambda e: (
                self.loading_state_changed.emit(False, ""), 
                self.error_occurred.emit(f"خطأ في التحميل: {e}")
            )
        )
    
    # --- الأوامر الموجهة لخدمة معينة ---
    def _execute_service_action(self, action_func, service_name, success_msg, refresh_after=True):
        self.loading_state_changed.emit(True, f"جاري {success_msg}...")
        
        def task(): return action_func(service_name)
        def finished(success):
            self.loading_state_changed.emit(False, "")
            if success:
                self.logger.info(success_msg)
                if refresh_after:
                    self.refresh_services()
            else:
                self.error_occurred.emit(f"فشل تنفيذ العملية على {service_name}")
        self.async_runner.run(task, finished)

    def start_service(self, name): self._execute_service_action(self.backend.start_service, name, f"بدء {name}")
    def stop_service(self, name): self._execute_service_action(self.backend.stop_service, name, f"إيقاف {name}")
    def restart_service(self, name): self._execute_service_action(self.backend.restart_service, name, f"إعادة تشغيل {name}")
    def reload_service(self, name): self._execute_service_action(self.backend.reload_service, name, f"إعادة تحميل {name}")
    def enable_service(self, name): self._execute_service_action(self.backend.enable_service, name, f"تمكين {name}")
    def disable_service(self, name): self._execute_service_action(self.backend.disable_service, name, f"تعطيل {name}")
    def mask_service(self, name): self._execute_service_action(self.backend.mask_service, name, f"حجب {name}")
    def unmask_service(self, name): self._execute_service_action(self.backend.unmask_service, name, f"إلغاء حجب {name}")
    def kill_service(self, name): self._execute_service_action(self.backend.kill_service, name, f"إنهاء قسري {name}")
    def reset_failed_service(self, name): self._execute_service_action(self.backend.reset_failed_service, name, f"إعادة ضبط فشل {name}")
    def clean_unit(self, name): self._execute_service_action(self.backend.clean_unit, name, f"تنظيف موارد {name}")
    def freeze_unit(self, name): self._execute_service_action(self.backend.freeze_unit, name, f"تجميد {name}")
    def thaw_unit(self, name): self._execute_service_action(self.backend.thaw_unit, name, f"استئناف تجميد {name}")
    def isolate_unit(self, name): self._execute_service_action(self.backend.isolate_unit, name, f"عزل (Isolate) {name}")

    def execute_bulk_action(self, action: str, names: list):
        self.loading_state_changed.emit(True, f"جاري تنفيذ الأمر الجماعي '{action}'...")
        def task(): return self.backend.execute_bulk(action, names)
        def finished(success):
            self.loading_state_changed.emit(False, "")
            if success:
                self.logger.info(f"Bulk action '{action}' on {len(names)} units successful")
                self.refresh_services()
            else:
                self.error_occurred.emit(f"فشل تنفيذ '{action}' جماعي على بعض التحديدات")
                self.refresh_services() # Still refresh
        self.async_runner.run(task, finished)

    # --- أوامر النظام العامة ---
    def execute_power_action(self, action: str):
        def task(): return self.backend.power_action(action)
        def finished(success):
            if not success:
                self.error_occurred.emit(f"فشل تنفيذ الإجراء الخاص بالنظام")
        self.async_runner.run(task, finished)

    def show_environment(self):
        env_text = self.backend.show_environment()
        self.show_environment_dialog.emit(env_text)

    def open_advanced_command_builder(self):
        self.show_advanced_builder_dialog.emit(self.backend)

    def daemon_reload(self):
        self.loading_state_changed.emit(True, "جاري تحديث مدير النظام...")
        def finished(success):
            self.loading_state_changed.emit(False, "")
            if success:
                self.logger.info("Daemon Reload OK")
                self.message_occurred.emit("تم تحديث مدير النظام بنجاح")
                self.refresh_services()
            else:
                self.error_occurred.emit("فشل تحديث مدير النظام (Daemon-Reload)")
        self.async_runner.run(self.backend.daemon_reload, finished)

    def show_service_details(self, service_name):
        service = self.model.get_service_by_name(service_name)
        if service:
            self.show_service_details_dialog.emit(service, self.backend)
