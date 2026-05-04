"""
نموذج QAbstractTableModel لعرض قائمة الخدمات مع دعم التصفية المتقدمة
"""
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from typing import List, Optional
from src.models.service_model import SystemdService

class ServiceListModel(QAbstractTableModel):
    COLUMNS = ["اسم الخدمة", "الوصف", "الحالة", "ممكن عند الإقلاع"]
    
    def __init__(self):
        super().__init__()
        self._services: List[SystemdService] = []
        self._filtered_services: List[SystemdService] = []
        self._filter_text = ""
        self._filter_category = "all"
        self._filter_type = "الكل (All)"
        
    def set_services(self, services: List[SystemdService]):
        self.beginResetModel()
        self._services = services
        self._apply_filter()
        self.endResetModel()
    
    def _apply_filter(self):
        """تطبيق فلتر النص والتصنيف معاً"""
        temp_list = self._services.copy()
        
        # فلتر التصنيف (Category)
        if self._filter_category != "all":
            if self._filter_category == "active":
                temp_list = [s for s in temp_list if s.is_active]
            elif self._filter_category == "inactive":
                temp_list = [s for s in temp_list if not s.is_active]
            elif self._filter_category == "failed":
                temp_list = [s for s in temp_list if s.active_state == "failed"]
            elif self._filter_category == "enabled":
                temp_list = [s for s in temp_list if s.is_enabled]
            elif self._filter_category == "disabled":
                temp_list = [s for s in temp_list if not s.is_enabled]
                
        # فلتر نوع الوحدة (Unit Type)
        if self._filter_type != "الكل (All)":
            target_type = self._filter_type.lower()
            temp_list = [s for s in temp_list if s.unit_type.lower() == target_type]
        
        # فلتر النص
        if self._filter_text:
            text = self._filter_text.lower()
            temp_list = [
                s for s in temp_list
                if text in s.name.lower() or text in s.description.lower()
            ]
            
        self._filtered_services = temp_list
    
    def set_filter(self, filter_text: str):
        self.beginResetModel()
        self._filter_text = filter_text
        self._apply_filter()
        self.endResetModel()

    def set_category(self, category: str):
        """تغيير التصنيف (نشط، متوقف، فاشل... إلخ)"""
        self.beginResetModel()
        self._filter_category = category
        self._apply_filter()
        self.endResetModel()

    def set_unit_type(self, unit_type: str):
        """تغيير نوع الوحدة (Service, Socket, Timer...)"""
        self.beginResetModel()
        self._filter_type = unit_type
        self._apply_filter()
        self.endResetModel()
    
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._filtered_services)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        
        service = self._filtered_services[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0: return service.name
            elif col == 1: return service.description
            elif col == 2: return service.status_text
            elif col == 3: return "ممكن" if service.is_enabled else "معطل"
        
        elif role == Qt.UserRole:
            return service
        
        return None
    
    def get_service_by_name(self, name: str) -> Optional[SystemdService]:
        for s in self._services:
            if s.name == name:
                return s
        return None
