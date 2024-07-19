from com_formate_render.FormateScreenshot import FormateScreenshot
from PyQt5 import QtCore

class ScreenShotWrapper(QtCore.QObject):
    def __init__(self, screenshot, parent_screenshot=None):
        super().__init__()
        self.screenshot = screenshot
        self.formate_screenshot = FormateScreenshot(parent_screenshot)  # Initialize with parent_screenshot

    def __getattr__(self, item):
        if hasattr(self.screenshot, item):
            return getattr(self.screenshot, item)
        elif hasattr(self.formate_screenshot, item):
            return getattr(self.formate_screenshot, item)
        else:
            raise AttributeError(f"'ScreenShot' object has no attribute '{item}'")

    def insert_screenshot(self, screenshot):
        self.formate_screenshot.insert_screenshot(screenshot)  # Delegate to FormateScreenshot
