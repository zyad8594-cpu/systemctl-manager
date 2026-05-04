"""
نموذج بيانات الخدمة الواحدة
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class SystemdService:
    name: str
    description: str
    load_state: str       # loaded, not-found, error
    active_state: str     # active, inactive, activating, deactivating, failed
    sub_state: str        # running, exited, waiting, ...
    enabled: Optional[bool] = None  # enabled/disabled (قد يكون غير معروف)
    unit_type: str = ""
    
    def __post_init__(self):
        if '.' in self.name:
            self.unit_type = self.name.split('.')[-1]
        else:
            self.unit_type = "unknown"
    
    @property
    def is_active(self) -> bool:
        return self.active_state == "active"
    
    @property
    def is_enabled(self) -> bool:
        return self.enabled is True
    
    @property
    def status_text(self) -> str:
        if self.is_active:
            return "يعمل"
        elif self.active_state == "failed":
            return "فشل"
        else:
            return "متوقف"
    
    @property
    def status_color(self) -> str:
        if self.is_active:
            return "#4caf50"  # أخضر
        elif self.active_state == "failed":
            return "#f44336"  # أحمر
        else:
            return "#9e9e9e"  # رمادي
    # 
# 
