
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys

from com_formate_glass.FormateTransparentGlass import FormateTransparentGlass


class FormateApp:

	def __init__(self):
		print("Formate App Constructor")

	def settings_dialog(self):
		print("Settings Dialog Selected")

	def run(self):
		button_references = []

		# create pyqt5 app
		App = QApplication(sys.argv)

		# Adding an icon
		icon = QIcon("formate.png")

		# Adding item on the menu bar
		tray = QSystemTrayIcon()
		tray.setIcon(icon)
		tray.setVisible(True)

		# Creating the options
		menu = QMenu()
		settings_menu_item = QAction("ForMate Settings...")
		settings_menu_item.triggered.connect(self.settings_dialog)
		menu.addAction(settings_menu_item)

		# To quit the app
		quit = QAction("Quit")
		quit.triggered.connect(App.quit)
		menu.addAction(quit)

		# Adding options to the System Tray
		tray.setContextMenu(menu)

		# Get current screen size
		screen = App.primaryScreen()
		print('Screen: %s' % screen.name())
		size = screen.size()
		print('Size: %d x %d' % (size.width(), size.height()))
		rect = screen.availableGeometry()
		print('Available: %d x %d' % (rect.width(), rect.height()))

		# create the instance of our Window
		window = FormateTransparentGlass(size.width(), size.height())

		# start the app
		sys.exit(App.exec())