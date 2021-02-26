#!/usr/bin/python3
#-*- coding: utf-8 -*-
import random

from PyQt5.QtWidgets import QPushButton


class FormateButton:
	def __init__(self,parent):
		self.name = None
		self.parent = parent
		self.rect = None

	def __init__(self, formate_rect, parent, color=None):
		self.name = formate_rect.text
		self.parent = parent
		self.rect = formate_rect
		self.qt_button = QPushButton(self.name, parent)
		if color is None:
			r = lambda: random.randint(0, 255)
			self.qt_button.setStyleSheet("background-color: rgb(" + (str(r()) + "," + str(r()) + "," + str(r())) + ");opacity:0.2;")
		else:
			self.qt_button.setStyleSheet("background-color: rgb(" + color[0] + "," + color[1] + "," + color[2] + ");opacity:0.2;")
		self.qt_button.move(formate_rect.x, formate_rect.y)
		self.qt_button.resize((int(formate_rect.w) - int(formate_rect.x)),(int(formate_rect.h) - int(formate_rect.y) ))
		self.qt_button.clicked.connect(self.clickButtonMethod)
		self.qt_button.show()

	def clickButtonMethod(self):
		print("clicked button")

	def highlight(self, ):
		pass

