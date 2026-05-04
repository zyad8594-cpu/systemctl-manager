"""
إدارة الصلاحيات (استخدام pkexec للحصول على صلاحيات الجذر)
"""
import subprocess
import os

def run_as_root(command: list) -> subprocess.CompletedProcess:
    """
    تنفيذ أمر بصلاحيات root باستخدام pkexec.
    ستعمل نافذة رسومية لطلب كلمة المرور.
    """
    full_cmd = ["pkexec"] + command
    return subprocess.run(full_cmd, capture_output=True, text=True)

def has_root_privileges() -> bool:
    """التحقق مما إذا كان التطبيق يعمل كـ root (عادة لا)"""
    return os.geteuid() == 0
