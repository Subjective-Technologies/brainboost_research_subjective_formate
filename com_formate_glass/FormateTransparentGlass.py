from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from com_formate_computervision.FormateRenderScheduler import FormateRenderScheduler
from com_formate_computervision.FormateScreenReaderMss import FormateScreenReaderMss
from com_formate_render.FormateScreenshot import FormateScreenshot
from com_formate_glass.ScreenShotWrapper import ScreenShotWrapper
from com_formate_computervision.FormateTesseract import FormateTesseract
from com_formate_glass.FormateButton import FormateButton
from com_formate_glass.FormateRect import FormateRect
from com_formate_glass.FormateRendererOnGlass import FormateRendererOnGlass
from datetime import datetime
from com_formate_logs.FormateLogger import FormateLogger
from com_formate_logs.FormateLogEntry import FormateLogEntry
from com_formate_workerthreads.WorkerThreads import WorkerThreads

class FormateTransparentGlass(QMainWindow):

    def __init__(self):
        super().__init__()

        # setting the geometry of the window
        allScreens = QApplication.desktop().geometry()
        self.setGeometry(allScreens)
        self.buttons = []
        self.root_screenshot = None

        # Implement transparency
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )

        # Initialize screen reader that takes screenshots only in screen pixels changing areas
        self.input = FormateScreenReaderMss(glass=self)
        self.input.changedPixels.connect(self.new_image_detected_through_the_glass)
        WorkerThreads.add_thread(name="screenreader", my_thread=self.input)
        self.input.start()

        # Show the transparent glass
        self.show()

    def paintEvent(self, event):
        FormateLogger.log(FormateLogEntry(thread_name="FormateTransparentGlass.py", description="Refresh"))

    def settings_dialog(self):
        FormateLogger.log(FormateLogEntry(thread_name="FormateTransparentGlass.py", description="Settings clicked"))

    def has_root_screenshot(self):
        return self.root_screenshot is not None

    def has_not_a_root_screenshot(self):
        return self.root_screenshot is None

    @QtCore.pyqtSlot(object)
    def new_image_detected_through_the_glass(self, screenshot):
        wrapped_screenshot = ScreenShotWrapper(screenshot)
        if self.has_not_a_root_screenshot():
            self.root_screenshot = wrapped_screenshot
        else:
            self.root_screenshot.insert_screenshot(wrapped_screenshot)
        wrapped_screenshot.glass_render_this_newly_detected_element.connect(self.render_button_from_screenshot)
        wrapped_screenshot.glass_remove_elements_as_picture_from_this_screenshot_changed.connect(self.remove_elements_from_glass)
        FormateLogger.log(FormateLogEntry(thread_name="FormateTransparentGlass.py", description="new screenshot starting thread"))

    @QtCore.pyqtSlot(object)
    def remove_elements_from_glass(self, elements_to_remove):
        pass

    @QtCore.pyqtSlot(FormateRect)
    def render_button_from_screenshot(self, formate_rect):
        FormateLogger.log(FormateLogEntry(thread_name="FormateTransparentGlass.py", description="Render button from screenshot"))
        FormateButton(formate_rect, self)

    @QtCore.pyqtSlot(FormateRect)
    def render_formate_hook_from_screenshot(self, formate_rect):
        pass

    @QtCore.pyqtSlot(FormateScreenshot)
    def render_button(self):
        pass
