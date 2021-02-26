#!/usr/bin/python3
#-*- coding: utf-8 -*-

class FormateRect:
	def __init__(self):
		self.x = None
		self.y = None
		self.w = None
		self.h = None
		self.text = None
		self.im = None

	def __init__(self, x, y, w, h, t, im=None):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.text = t
		self.im = im


