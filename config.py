from datetime import datetime
import os
import sys
import json
from kivy.logger import Logger

class Configure:
	FILE_NAME = 'app_config.json'
	__data = dict()
	new_device = False
	def __init__(self):
		if not os.path.exists(self.FILE_NAME):
			self.new_device = True
			self._initialize()
			
	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(Configure, cls).__new__(cls)
		return cls.instance
			
	def _initialize(self):
		self.__data['Genral'] = {
		'theme': 'Light',
		'new-device': True,
		}
		
		self.__data['User'] = {
		'login-on': str(datetime.now()),
		'recent-login': str(datetime.now()),
		}
		try:
			with open(self.FILE_NAME, 'w') as f:
				f.write(json.dumps(self.__data))
			Logger.info('Punch Config: initialize successfully.')
		except Exception as e:
			err_type, error, tab = sys.exc_info()
			del tab
			Logger.exception('Config: {0}{1}'.format(err_type, err))
		
	def get(self, section, key=None):
		print(self.__data)
		if not self.__data:
			if os.path.exists(self.FILE_NAME):
				file = open(self.FILE_NAME)
				self.__data = json.load(file)
			else:
				return 
			
		if key:
			return self.__data[section][key]
			
		return self.__data[section]
		
	def update(self, section, key, value):
		if not self.__data:
			if os.path.exists(self.FILE_NAME):
				file = open(self.FILE_NAME)
				self.__data = json.load(file)
			else:
				return 
			
		self.__data[section][key] = value
		with open(self.FILE_NAME, 'w') as f:
			f.write(json.dumps(self.__data))