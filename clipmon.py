#!c:/SDK/Anaconda2/python.exe

from __future__ import print_function
import time
import sys
import os
import clipboard
from notify import notify
from make_colors import make_colors
from datetime import datetime


class clipmon(object):
	def __init__(self):
		super(clipmon, self)
		self.notify = notify()
		
	def get_now(self):
		return datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S.%f') 
		
	def monitor(self, sleep=1):
		clip = None
		while 1:
			if not clipboard.paste() == clip:
				clip = clipboard.paste()
				print(make_colors(self.get_now(), 'lw', 'bl') + " - " + make_colors("Clipboard Changed !", 'lw', 'lr'))
				self.notify.notify("Clipboard Monitor", "Clipboard Changed", "Clipboard Monitor", "changed", host = None, port = None, timeout = None, icon = None, pushbullet_api = None, nmd_api = None, growl = True, pushbullet = True, nmd = True)
			else:
				pass
			time.sleep(sleep)
			
if __name__ == '__main__':
	c = clipmon()
	c.monitor()