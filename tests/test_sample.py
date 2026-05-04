"""
اختبار بسيط للتحقق من عمل النموذج
"""
import unittest
from src.models.service_model import SystemdService
from src.models.service_list_model import ServiceListModel

class TestServiceModel(unittest.TestCase):
    def test_service_creation(self):
        s = SystemdService("test.service", "وصف تجريبي", "loaded", "active", "running", True)
        self.assertTrue(s.is_active)
        self.assertTrue(s.is_enabled)
        self.assertEqual(s.status_text, "يعمل")
    
    def test_list_model(self):
        model = ServiceListModel()
        services = [
            SystemdService("a.service", "A", "loaded", "active", "running", True),
            SystemdService("b.service", "B", "loaded", "inactive", "dead", False)
        ]
        model.set_services(services)
        self.assertEqual(model.rowCount(), 2)
        model.set_filter("a")
        self.assertEqual(model.rowCount(), 1)

if __name__ == "__main__":
    unittest.main()