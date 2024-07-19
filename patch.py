import os

patch_number = 21

# Update com_formate_render/FormateScreenshot.py
file_path_screenshot = 'com_formate_render/FormateScreenshot.py'
lines_screenshot = [
    "from PyQt5 import QtCore\n",
    "from com_formate_logs.FormateLogger import FormateLogger\n",
    "from com_formate_logs.FormateLogEntry import FormateLogEntry\n",
    "\n",
    "class FormateScreenshot(QtCore.QObject):\n",
    "    glass_render_this_newly_detected_element = QtCore.pyqtSignal(object)\n",
    "    glass_remove_elements_as_picture_from_this_screenshot_changed = QtCore.pyqtSignal(object)\n",
    "\n",
    "    def __init__(self, parent_screenshot=None):\n",
    "        super().__init__()\n",
    "        self.parent_screenshot = parent_screenshot  # Initialize parent_screenshot\n",
    "\n",
    "    def insert_screenshot(self, screenshot):\n",
    "        if self.parent_screenshot:\n",
    "            self.parent_screenshot.insert_screenshot(screenshot)\n",
    "        else:\n",
    "            FormateLogger.log(FormateLogEntry(thread_name=\"FormateScreenshot.py\", description=\"Inserted parent screenshot\"))\n",
]

with open(file_path_screenshot, 'w') as file:
    file.writelines(lines_screenshot)

print(f'Patch {patch_number} applied successfully.')
