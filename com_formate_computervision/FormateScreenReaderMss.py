from PyQt5.QtCore import QThread, pyqtSignal
import mss
import time

class FormateScreenReaderMss(QThread):
    changedPixels = pyqtSignal(object)

    def __init__(self, glass=None):
        super().__init__()
        self.glass = glass

    def run(self):
        with mss.mss() as sct:
            while True:
                screenshot = sct.grab(sct.monitors[1])
                self.changedPixels.emit(screenshot)
                time.sleep(1)
                if self.glass and hasattr(self.glass, 'has_root_screenshot'):
                    if self.glass.has_root_screenshot() is None:
                        continue
                    # More processing logic...
                else:
                    print("Error: glass does not have has_root_screenshot method")
                    break
