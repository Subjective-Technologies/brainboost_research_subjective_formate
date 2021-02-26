#!/usr/bin/python3
#-*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QPushButton

from com_formate_computervision.FormateTesseract import FormateTesseract
from com_formate_glass.FormateButton import FormateButton
from com_formate_glass.FormateRect import FormateRect


class FormateTransparentGlass(QMainWindow):

	def __init__(self, w, h):
		super().__init__()
		# set the title
		self.buttons = []
		self.resolution = FormateRect(0, 0, w, h, "ForMate")
		self.worker_thread_1 = FormateTesseract(self)
		self.worker_thread_1.shoot_text_to_glass_signal.connect(self.show_button)
		self.worker_thread_1.start()


		self.setWindowFlags(
			QtCore.Qt.WindowStaysOnTopHint |
			QtCore.Qt.FramelessWindowHint |
			QtCore.Qt.X11BypassWindowManagerHint
		)

		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		# self.setWindowFlags(QtCore.Qt.WindowTransparentForInput)

		# setting  the geometry of window
		self.setGeometry(
			QtWidgets.QStyle.alignedRect(
				QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter,
				QtCore.QSize(self.resolution.w, self.resolution.h),
				QtWidgets.qApp.desktop().availableGeometry()
			))


		self.show()

	@QtCore.pyqtSlot(FormateRect)
	def show_button(self, single_rect):
		FormateButton(single_rect, parent=self)
		#print("render buttons running: " + str(single_rect))


	def paintEvent(self, event):
		print("refresh")


	def settings_dialog(self):
		print("Settings clicked...")