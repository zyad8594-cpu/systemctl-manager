"""
تشغيل المهام الطويلة في خيط منفصل لمنع تجميد الواجهة مع ضمان تحديث الواجهة بأمان
"""
from PySide6.QtCore import QThread, Signal, QObject, Qt
from typing import Callable, Any

class Worker(QObject):
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class AsyncRunner(QObject):
    # إشارات وسيطة لضمان التنفيذ في الخيط الرئيسي
    task_finished = Signal(object, object)  # (result, callback_func)
    task_error = Signal(str, object)        # (error_msg, callback_func)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._threads = []
        # ربط الإشارات الوسيطة بالتوابع التي ستنفذ الـ callbacks
        self.task_finished.connect(self._handle_finished)
        self.task_error.connect(self._handle_error)

    def run(self, func: Callable, on_finished: Callable[[Any], None] = None, on_error: Callable[[str], None] = None):
        thread = QThread()
        worker = Worker(func)
        worker.moveToThread(thread)
        
        thread.started.connect(worker.run)
        
        # عند انتهاء العامل، نرسل النتيجة للإشارة الوسيطة في الخيط الرئيسي
        worker.finished.connect(lambda res: self.task_finished.emit(res, on_finished))
        worker.error.connect(lambda err: self.task_error.emit(err, on_error))
            
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        
        thread.finished.connect(thread.deleteLater)
        worker.deleteLater()
        
        self._threads.append(thread)
        thread.finished.connect(lambda: self._threads.remove(thread) if thread in self._threads else None)
        
        thread.start()

    def _handle_finished(self, result, callback):
        if callback:
            callback(result)

    def _handle_error(self, error_msg, callback):
        if callback:
            callback(error_msg)
