from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow
from PyQt5.QtGui import QIcon
from com_formate_glass.FormateTransparentGlass import FormateTransparentGlass
from com_formate_logs.FormateLogger import FormateLogger
from com_formate_logs.FormateLogEntry import FormateLogEntry
from com_formate_computervision.FormateScreenReaderMss import FormateScreenReaderMss
import pytesseract
from PyQt5.QtWidgets import QPushButton
from PIL import Image
import numpy as np
import time

class FormateApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.transparent_glass = None
        self.initUI()
        self.startMonitoring()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Formate New')
        self.tray = QSystemTrayIcon(QIcon("formate.png"), self)
        self.menu = QMenu()
        self.settings_menu_item = QAction("ForMate Settings...", self)
        self.settings_menu_item.triggered.connect(self.settings_dialog)
        self.menu.addAction(self.settings_menu_item)
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(QApplication.instance().quit)
        self.menu.addAction(self.quit_action)
        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def startMonitoring(self):
        self.transparent_glass = FormateTransparentGlass()
        self.screen_reader = FormateScreenReaderMss(glass=self.transparent_glass)
        self.screen_reader.changedPixels.connect(self.handle_screen_change)
        self.screen_reader.start()

    def settings_dialog(self):
        FormateLogger.log(FormateLogEntry(thread_name="FormateApp.py", description="Settings Dialog Selected"))

    def handle_screen_change(self, screenshot):
        start_time = time.time()
        # Convert the screenshot to a format compatible with pytesseract
        img_array = np.frombuffer(screenshot.rgb, dtype=np.uint8).reshape((screenshot.height, screenshot.width, 3))
        img = Image.fromarray(img_array)
        # Perform OCR
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 60:  # Confidence threshold
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                self.create_button(x, y, w, h, data['text'][i])
        elapsed_time = time.time() - start_time
        print(f"Time to process screenshot: {elapsed_time} seconds")

    def create_button(self, x, y, w, h, text):
        button = QPushButton(text, self.transparent_glass)
        button.setStyleSheet("background-color: rgb(0, 255, 0);")
        button.setGeometry(x, y, w, h)
        button.show()

class FormateButton(QPushButton):
    def __init__(self, text, parent):
        super().__init__(text, parent)
        self.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.resize(100, 50)
        self.move(10, 10)
        self.show()
