import configparser
from datetime import datetime
import os
import sys

class Configure:
	FILE_NAME = 'app_config.ini'
	__data = None
	def __init__(self):
		if not os.path.exists(self.FILE_NAME):
			self._initialize()
			
	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(Configure, cls).__new__(cls)
		return cls.instance
			
	def _initialize(self):
		config = configparser.ConfigParser()
		config['Genral'] = {
		'theme': 'Light',
		'new-device': str(True),
		}
		
		config['User'] = {
		'login-on': str(datetime.now()),
		'recent-login': str(datetime.now()),
		}
		try:
			with open('app_config.ini', 'w') as f:
				config.write(f)
			
		except Exception as e:
			err_type, error, tab = sys.exc_info()
			del tab
		
	def get(self, section, key=None):
		if not self.__data:
			self.__data = configparser.ConfigParser()
			self.__data.read('app_config.ini')
			
		if key:
			return self.__data[section][key]
			
		return self.__data[section]
		
	def get_boolean(self, section, key):
		if not self.__data:
			self.__data = configparser.ConfigParser()
			self.__data.read('app_config.ini')
			
		return self.__data[section].getboolean(key)
		
	def update(self, section, key, value):
		if not self.__data:
			self.__data = configparser.ConfigParser()
			self.__data.read('app_config.ini')
			
		self.__data[section][key] = value
		with open('app_config.ini', 'w') as f:
			self.__data.write(f)