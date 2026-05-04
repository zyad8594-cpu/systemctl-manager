"""
الخلفية التي تتفاعل مع systemd عبر subprocess (أو D-Bus)
"""
import subprocess
import re
from typing import List, Optional, Dict
from src.models.service_model import SystemdService
from src.utils.permissions import run_as_root

class SystemdBackend:
    def __init__(self):
        pass
    
    def _run_cmd(self, cmd: List[str], use_root=False) -> tuple[int, str, str]:
        """تنفيذ أمر وعودة (رمز، stdout، stderr)"""
        try:
            if use_root:
                cmd = ["pkexec"] + cmd
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return proc.returncode, proc.stdout, proc.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def list_all_services(self) -> List[SystemdService]:
        """جلب قائمة بجميع الوحدات (Units)"""
        # نستخدم --type=all أو نحذف --type لجلب الجميع
        cmd_units = ["systemctl", "list-units", "--all", "--no-legend", "--full"]
        code1, out1, _ = self._run_cmd(cmd_units)
        
        services_dict: Dict[str, SystemdService] = {}
        
        if code1 == 0:
            for line in out1.strip().split('\n'):
                if not line.strip(): continue
                parts = line.split(None, 4)
                if len(parts) >= 5:
                    unit_name = parts[0]
                    # ignore strange systemd strings or device mounts if too noisy, 
                    # but for now we accept all units having an extension.
                    if '.' in unit_name:
                        services_dict[unit_name] = SystemdService(
                            name=unit_name,
                            description=parts[4],
                            load_state=parts[1],
                            active_state=parts[2],
                            sub_state=parts[3],
                            enabled=False # سيتم تحديثه لاحقاً
                        )

        # 2. جلب جميع ملفات الوحدات
        cmd_files = ["systemctl", "list-unit-files", "--no-legend"]
        code2, out2, _ = self._run_cmd(cmd_files)
        
        if code2 == 0:
            for line in out2.strip().split('\n'):
                if not line.strip(): continue
                parts = line.split()
                if len(parts) >= 2:
                    unit_name = parts[0]
                    state = parts[1] # enabled, disabled, static, etc.
                    
                    if '.' not in unit_name: continue
                    
                    if unit_name not in services_dict:
                        # خدمة موجودة كملف ولكنها غير محملة في الذاكرة
                        services_dict[unit_name] = SystemdService(
                            name=unit_name,
                            description="(خدمة غير محملة)",
                            load_state="not-loaded",
                            active_state="inactive",
                            sub_state="dead",
                            enabled=(state == "enabled")
                        )
                    else:
                        # تحديث حالة التمكين للخدمة الموجودة مسبقاً
                        services_dict[unit_name].enabled = (state == "enabled")

        # 3. جلب أوصاف إضافية للخدمات التي تفتقر إليها (اختياري ولكن يحسن الجودة)
        # ملاحظة: تم تعطيله حالياً لتسريع الأداء، ولكن يمكن إضافته إذا لزم الأمر
        
        return list(services_dict.values())
    
    def start_service(self, name: str) -> bool:
        cmd = ["systemctl", "start", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0
    
    def stop_service(self, name: str) -> bool:
        cmd = ["systemctl", "stop", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0
    
    def restart_service(self, name: str) -> bool:
        cmd = ["systemctl", "restart", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0
    
    def enable_service(self, name: str) -> bool:
        cmd = ["systemctl", "enable", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0
    
    def disable_service(self, name: str) -> bool:
        cmd = ["systemctl", "disable", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0
    
    def reload_service(self, name: str) -> bool:
        cmd = ["systemctl", "reload", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def mask_service(self, name: str) -> bool:
        cmd = ["systemctl", "mask", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def unmask_service(self, name: str) -> bool:
        cmd = ["systemctl", "unmask", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def kill_service(self, name: str) -> bool:
        cmd = ["systemctl", "kill", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def reset_failed_service(self, name: str) -> bool:
        cmd = ["systemctl", "reset-failed", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def clean_unit(self, name: str) -> bool:
        cmd = ["systemctl", "clean", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def freeze_unit(self, name: str) -> bool:
        cmd = ["systemctl", "freeze", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def thaw_unit(self, name: str) -> bool:
        cmd = ["systemctl", "thaw", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def isolate_unit(self, name: str) -> bool:
        cmd = ["systemctl", "isolate", name]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    # --- System & Power Commands ---
    def power_action(self, action: str) -> bool:
        """ينفذ أوامر الطاقة مثل reboot, poweroff, suspend, hibernate, emergency"""
        # actions supported: reboot, poweroff, suspend, hibernate, halt, rescue, emergency
        cmd = ["systemctl", action]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def show_environment(self) -> str:
        """جلب بيئة النظام باستخدام systemctl show-environment"""
        cmd = ["systemctl", "show-environment", "--no-pager"]
        code, out, err = self._run_cmd(cmd)
        if code == 0:
            return out
        return f"خطأ: {err}"

    def set_environment_variable(self, key: str, value: str) -> bool:
        """ضبط متغير بيئة نظام باستخدام systemctl set-environment"""
        cmd = ["systemctl", "set-environment", f"{key}={value}"]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def unset_environment_variable(self, key: str) -> bool:
        """حذف متغير بيئة نظام باستخدام systemctl unset-environment"""
        cmd = ["systemctl", "unset-environment", key]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def is_system_running(self) -> str:
        """التحقق من حالة تشغيل النظام systemctl is-system-running"""
        cmd = ["systemctl", "is-system-running"]
        code, out, _ = self._run_cmd(cmd)
        return out.strip() if out else "unknown"

    def daemon_reload(self) -> bool:
        cmd = ["systemctl", "daemon-reload"]
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def execute_bulk(self, action: str, units: list[str]) -> bool:
        """ينفذ عملية كإعادة تشغيل أو إيقاف على عدة وحدات دفعة واحدة"""
        cmd = ["systemctl", action] + units
        code, _, _ = self._run_cmd(cmd, use_root=True)
        return code == 0

    def get_service_properties(self, name: str) -> str:
        cmd = ["systemctl", "show", name, "--no-pager"]
        code, out, err = self._run_cmd(cmd)
        if code == 0:
            return out
        return f"خطأ: {err}"

    def get_service_file(self, name: str) -> str:
        cmd = ["systemctl", "cat", name, "--no-pager"]
        code, out, err = self._run_cmd(cmd)
        if code == 0:
            return out
        return f"خطأ: {err}"
    
    def get_unit_dependencies(self, name: str) -> str:
        """جلب الاعتماديات (Dependencies) باستخدام systemctl list-dependencies"""
        cmd = ["systemctl", "list-dependencies", name, "--no-pager"]
        code, out, err = self._run_cmd(cmd)
        if code == 0:
            return out
        return f"خطأ: {err}"
    
    def get_service_logs(self, name: str, lines: int = 50) -> str:
        cmd = ["journalctl", "-u", name, "-n", str(lines), "--no-pager"]
        code, out, err = self._run_cmd(cmd)
        if code == 0:
            return out
        else:
            return f"خطأ: {err}"
