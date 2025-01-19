from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
import json
import pickle
import os

import config
import version

WEEKLY_OFF_SYMBOL = 'W/O'
ABSCENT_SYMBOL = 'A'

class PunchManager:
	FILE_NAME = 'punch_data.json'
	BACKUP_FILE = 'punch.pn'
	__data = dict()
	def __init__(self):
		if not os.path.exists(self.FILE_NAME):
			print('creating punch data file')
			self.__data = {str(datetime.now().date()): {}}
			self._save()
			print('punch data file created successfully.')
			
	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(PunchManager, cls).__new__(cls)
		return cls.instance
			
	def punch(self):
		punch_records = self.punch_data()
		time = datetime.now().strftime('%H:%M:%S')
		configure = config.Configure()
		try:
			today_data = punch_records[str(datetime.now().date())]
			print('today data:',today_data)
			if 'in time' not in today_data:
				today_data['in time'] = time
				self._save()
				configure.update(
				section= 'User',
				key = 'last-punch',
				value = str(datetime.now())
				)
				configure.update('User', 'last-punch-type', 'IN')
				
			elif 'out time' not in today_data:
				today_data['out time'] = time
				self._save()
				configure.update(
				section= 'User',
				key = 'last-punch',
				value = str(datetime.now())
				)
				
				configure.update('User', 'last-punch-type', 'OUT')
			else:
				return
		except KeyError:
			raise
			
	def get(self, date='str'):
		quary_date = parse(date)
		for i in self.data.keys():
			date = parse(i)
			if i == quary_date:
				return i
			
	def _save(self): 
		with open(self.FILE_NAME, "w") as f:
			f.write(json.dumps(self.__data))
			
	def punch_data(self) -> dict:
		if not self.__data:
			data = json.load(open('punch_data.json'))
			self.__data = data
		return self.__data
	
	@property
	def need_to_punch(self) -> bool:
		records = self.punch_data()
		current_date = datetime.now().date()
		
		try:
			today_records = records[str(datetime.now().date())]
			
			if self.is_it_weekly_off(current_date):
				self.__data[str(current_date)] = dict()
				self.__data[str(current_date)]['in time'] = WEEKLY_OFF_SYMBOL
				self.__data[str(current_date)]['out time'] = WEEKLY_OFF_SYMBOL
				self._save()
				return False
				
			elif 'in time' not in today_records or \
			'out time' not in today_records:
				return True
			
			
			return False
			
		except KeyError:
			self._put_absence()
			return True
			
		return False
		
	def _put_absence(self):
		configure = config.Configure()
		current_date = datetime.now().date()
		try:
			last_punch_date = configure.get('User', 'last-punch')
		except Exception as e:
			self.__data[str(current_date)] = dict()
			self._save()
			return 
		last_punch_date = parse(last_punch_date)
		if last_punch_date == current_date-relativedelta(days=1):
			self.__data[str(current_date)] = dict()
			return
		
		missed_days = rrule(
		freq= DAILY,
		dtstart=last_punch_date+relativedelta(days=1),
		until=current_date
		)
		for day in missed_days:
			missed_date = str(day.date())
			self.__data[missed_date] = {}
			if self.is_it_weekly_off(day.date()):
				self.__data[missed_date]['in time'] = WEEKLY_OFF_SYMBOL
				self.__data[missed_date]['out time'] = WEEKLY_OFF_SYMBOL
				continue 
				
			self.__data[missed_date]['in time'] = ABSCENT_SYMBOL
			self.__data[missed_date]['out time'] = ABSCENT_SYMBOL
		
		self.__data[str(current_date)] = dict()
		self._save()
		
	def is_it_weekly_off(self, date) -> bool:
		""" check is today is weekly off of user """
		try:
			weekly_offs = config.Configure().get('User', 'weekly off').split(',')
			day_name = date.strftime('%A')
			
			if day_name in weekly_offs:
				return True
			return False
			
		except KeyError:
			return False
		except:
			return False
		
		
	def export(self, dir: str = ''):
		data = dict()
		data['application'] = 'punch'
		data['version'] = version.__version__
		data['punch-data'] = self.punch_data()
		file = os.path.join(dir, self.BACKUP_FILE)
		with open(file, 'wb') as f:
			print('Exporting Data')
			pickle.dump(data, f)
			
			
	def import_data(self, filename:str):
		if os.path.exists(filename):
			print('File exists')
			extension = os.path.splitext(filename)[1]
			req_extension = os.path.splitext(self.BACKUP_FILE)[1]
			if not extension == req_extension:
				return
				
			file = open(filename, 'rb')
			data_object = pickle.load(file)
			if 'application' in data_object:
				if data_object['application'] == 'punch':
					data_object = data_object['punch-data']
					if os.path.exists(self.FILE_NAME):
						data = json.load(open('punch_data.json'))
						for i in data_object:
							if i in data:
								if 'in time' not in data[i] or 'out time' not in data[i]:
									if 'in time' in data_object[i] and 'in time' not in data[i]:
										data[i]['in time'] = data_object[i]['in time']
									if 'out time' in data_object[i] and 'out time' not in data[i]:
										data[i]['out time'] = data_object[i]['out time']
							else:
								data[i] = data_object[i]
								
								
						self.__data = data
					else:
						self.__data = data_object
						
					print('Shorting data')
					self._sort()
					self._save()
					print('Shorting Done.')
						
					print('importing done')
					print('data imported sussfully.')
					return True
				return
			return 
		return
		
		
	def _is_missed(self, data):
		pass
		
		
	def _sort(self):
		sorted_list = sorted(self.__data, key= lambda x: parse(x))
		new_dict = dict()
		for i in sorted_list:
			new_dict[i] = self.__data[i]
			
		self.__data = new_dict
		
				
				