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
import traceback
import argparse

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
		if os.path.isfile(file_clip):
			with open(file_clip, 'ab') as f:
				f.write(self.get_now() + " --- " + unicode(clip).encode('utf-8'))
				f.write("\n")
		else:
			with open(file_clip, 'wb') as f:
				f.write(self.get_now() + " --- " + unicode(clip).encode('utf-8'))
				f.write("\n")
		return file_clip
	
	
	def save_to_db(self, clip):
		import sqlite3
		file_db = os.path.join(os.path.dirname(__file__), 'clips.db3')
		conn = sqlite3.connect(file_db)
		curs = conn.cursor()
		CREATE_TABLE = "CREATE TABLE IF NOT EXISTS clips ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'date' DATETIME NOT NULL, 'clip' TEXT)"
		INSERT_TABLE = 'INSERT INTO clips ("date", "clip") values("{0}", "{1}")'
		curs.execute(CREATE_TABLE)
		conn.commit()
		data_insert = INSERT_TABLE.format(self.get_now(), unicode(re.sub('"', "'", clip)).encode('utf-8'))
		try:
			curs.execute(data_insert)
		except:
			debug(data_insert = data_insert, debug = True)
			print(traceback.format_exc())
		conn.commit()
		
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
				# if len(clip) > (self.width - 55):
				# 	msg = [clip]
				# 	msg = str(msg)[1:(self.width - 55)][:-1] + " " + make_colors("...", 'lr') + " LEN:" + make_colors(len(clip), 'lg')
				msg = make_colors("...", 'lr') + " PID:" + make_colors(str(os.getpid()), 'ly') + " LEN:" + make_colors(len(clip), 'lg')
				print(make_colors(self.get_now(), 'lw', 'bl') + " - " + make_colors("Clipboard Changed !", 'lw', 'lr') + " --> " + make_colors(msg, 'ly'))

				self.notify.notify("Clipboard Monitor", "Clipboard Changed", "Clipboard Monitor", "changed", host = None, port = None, timeout = None, iconpath = 'clips.png', pushbullet_api = None, nmd_api = None, growl = True, pushbullet = False, nmd = False)
			else:
				pass
			time.sleep(sleep)

	def show_last(self, n = 1):
		file_clip = os.path.join(os.path.dirname(__file__), 'clips.txt')
		data = ''
		if os.path.isfile(file_clip):
			with open(file_clip, 'rb') as f:
				clip = f.readlines()[-n:]
				debug(clip = clip)
				for i in clip:
					data = re.split('^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{0,8}|\n', i)
					dd = re.findall('^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{0,8}', i)
					dd = filter(None, dd)
					data = filter(None, data)
					# print("dd =", dd)
					# print("data =", data)
					print(make_colors(dd[0], 'lw', 'bl') + make_colors(data[0], 'ly'))

	def get_last(self, n = 1):
		file_clip = os.path.join(os.path.dirname(__file__), 'clips.txt')
		data = ''
		if os.path.isfile(file_clip):
			with open(file_clip, 'rb') as f:
				clip = f.readlines()[-n]
				debug(clip = clip)
				if clip:
					clip = re.split('^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{0,8} --- |\n', clip)
					debug(clip = clip)
					if len(clip) > 2:
						if clip[2] == '':
							data = clip[1]
						else:
							data = " - ".join(clip[1:])
					elif len(clip) == 2:
						data = clip[1]

		if data:
			print(make_colors("Copy clip to clipboard !", 'lw', 'bl', ['blink']))
			clipboard.copy(data)
		else:
			print(make_colors("Clip ERROR !", 'lw', 'lr', ['blink']))

	def usage(self):
		parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
		parser.add_argument('-g', '--get', action='store', help = 'Get Last clipboard of n from end', type=int)
		parser.add_argument('-s', '--show', action='store', help = 'Show Last clipboard of from n end', type=int)
		parser.add_argument('-nd', '--no-db', action = 'store_false', help = 'Dont save clip to Database')
		parser.add_argument('-nt', '--no-text', action = 'store_false', help = 'Dont save clip to text')
		parser.add_argument('-t', '--time', action='store', help='time to sleep second, default 1 second', type=int, default = 1)
		if len(sys.argv) == 1:
			parser.print_help()
		else:
			args = parser.parse_args()
			if args.get:
				self.get_last(args.get)
			elif args.show:
				self.show_last(args.show)
			else:
				self.monitor(args.time, args.no_db, args.no_text)
			
if __name__ == '__main__':
	c = clipmon()
	# c.monitor()
	c.usage()