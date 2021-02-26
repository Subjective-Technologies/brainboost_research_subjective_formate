#!/usr/bin/python3
#-*- coding: utf-8 -*-
from PyQt5.QtCore import QThread


class FormateComputerVision(QThread):
	def __init__(self):
		self.input = None

	def shoot(self, image=None):
		pass

