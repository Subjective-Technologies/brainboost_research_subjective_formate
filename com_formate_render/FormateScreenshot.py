from PyQt5 import QtCore
from com_formate_logs.FormateLogger import FormateLogger
from com_formate_logs.FormateLogEntry import FormateLogEntry

class FormateScreenshot(QtCore.QObject):
    glass_render_this_newly_detected_element = QtCore.pyqtSignal(object)
    glass_remove_elements_as_picture_from_this_screenshot_changed = QtCore.pyqtSignal(object)

    def __init__(self, parent_screenshot=None):
        super().__init__()
        self.parent_screenshot = parent_screenshot  # Initialize parent_screenshot

    def insert_screenshot(self, screenshot):
        if self.parent_screenshot:
            self.parent_screenshot.insert_screenshot(screenshot)
        else:
            FormateLogger.log(FormateLogEntry(thread_name="FormateScreenshot.py", description="Inserted parent screenshot"))
