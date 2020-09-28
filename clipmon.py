#!/usr/bin/env python2

from __future__ import print_function
import time
import sys
import os
import clipboard
from notify import notify
from make_colors import make_colors
from datetime import datetime
import cmdw
from pydebugger.debug import debug
import re
from configset import configset

class clipmon(object):
	def __init__(self):
		super(clipmon, self)
		self.notify = notify()
		self.width = cmdw.getWidth()
		self.configname = os.path.join(os.path.dirname(__file__), 'clipmon.ini')
		self.config = configset(self.configname)
		
	def get_now(self):
		return datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S.%f') 
		
	def save_to_text(self, clip):
		file_clip = os.path.join(os.path.dirname(__file__), 'clips.txt')
		with open(file_clip, 'wb') as f:
			f.write(unicode(clip).encode('utf-8'))
			f.write("\n")
		return file_clip
	
	
	def save_to_db(self, clip):
		import sqlite3
		file_db = os.path.join(os.path.dirname(__file__), 'clips.db3')
		conn = sqlite3.connect(file_db)
		curs = conn.cursor()
		CREATE_TABLE = "CREATE TABLE IF NOT EXISTS clips ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'date' DATETIME NOT NULL, 'clip' TEXT)"
		INSERT_TABLE = "INSERT INTO clips ('date', 'clip') values('{0}', '{1}')"
		curs.execute(CREATE_TABLE)
		curs.commit()
		data_insert = INSERT_TABLE.format(self.get_now(), unicode(clip).encode('utf-8'))
		curs.execute(INSERT_TABLE)
		curs.commit()
		
	def monitor(self, sleep=1, to_db = True, to_text = True):
		if self.config.get_config('sleep', 'time'):
			if self.config.get_config('sleep', 'time').isdigit():
				sleep = int(self.config.get_config('sleep', 'time'))
		if self.config.get_config('save', 'db') == '1':
			to_db = True
		elif self.config.get_config('save', 'db') == '0':
			to_db = False
		if self.config.get_config('save', 'text') == '1':
			to_text = True
		elif self.config.get_config('save', 'text') == '0':
			to_text = False
		clip = None
		while 1:
			if not clipboard.paste() == clip:
				clip = clipboard.paste()
				if to_db:
					self.save_to_db(clip)
				if to_text:
					self.save_to_text(clip)
				debug(self_width = self.width)
				if len(clip) > (self.width - 55):
					msg = [clip]
					msg = str(msg)[1:(self.width - 55)][:-1] + " " + make_colors("...", 'lr')
				print(make_colors(self.get_now(), 'lw', 'bl') + " - " + make_colors("Clipboard Changed !", 'lw', 'lr') + " --> " + make_colors(msg, 'ly'))
				self.notify.notify("Clipboard Monitor", "Clipboard Changed", "Clipboard Monitor", "changed", host = None, port = None, timeout = None, icon = None, pushbullet_api = None, nmd_api = None, growl = True, pushbullet = False, nmd = False)
			else:
				pass
			time.sleep(sleep)
			
if __name__ == '__main__':
	c = clipmon()
	c.monitor()