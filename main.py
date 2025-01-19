import os
from datetime import datetime

from kivy.utils import platform
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty

from kivy.logger import Logger
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.list import (ILeftBody, IRightBody,
OneLineAvatarIconListItem)
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol.selectioncontrol import MDSwitch
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.filemanager import MDFileManager

from uix.popup import WeeklyOffPopup, InfoPopup

from plyer import storagepath 

from config import Configure
from punch import PunchManager

android = False
if platform == 'android':
	android = True
	from android.permissions import (
	Permission,
	request_permissions,
	request_permission,
	check_permission,
	)

def has_permission():
	if android:
		a, b = [
		check_permission(Permission.READ_EXTERNAL_STORAGE),
		check_permission(Permission.WRITE_EXTERNAL_STORAGE)
		]
		if a and b:
			return True
		return False
	return False



class ThemeSwitch(IRightBody, MDSwitch):
	pass
	
class ListMainBody(OneLineAvatarIconListItem):
	pass

class ListLeftBody(ILeftBody, MDLabel):
	text = StringProperty('--/--/--')
	
class ListRightBody(IRightBody, MDBoxLayout):
	in_time = StringProperty('--:--:--')
	out_time = StringProperty('--:--:--')
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.size_hint_x = .5
		self.in_time_label = MDLabel(text= self.in_time)
		self.out_time_label = MDLabel(text= self.out_time, halign= 'right')
		
		self.add_widget(self.in_time_label)
		self.add_widget(self.out_time_label)
		
	def on_in_time(self, ins, time):
		self.in_time_label.text = time
		
	def on_out_time(self, ins, time):
		self.out_time_label.text = time
		

class MainWindow(MDScreenManager):
	weekly_offs = StringProperty('')
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
	
	def punch(self):
		punch_mn = PunchManager()
		date = str(datetime.now().date())
		data = punch_mn.punch_data()
		
		if date in data:
			try:
				punch_mn.punch()
				self.reload()
				toast('punched successfully')
			except Exception as e:
				self.open_info_popup(text=str(e))
				
		self.ids.punch_popup.dismiss()
		
	def reload(self):
		data = PunchManager().punch_data()
		punch_data_container = self.ids.punch_data_container
		
		try:
			punch_data_container.clear_widgets()
		except ReferenceError:
			pass
			
		for j, i in enumerate(data):
			left_body = ListLeftBody(text=i)
			right_body = ListRightBody()
			
			if 'in time' in data[i]:
				right_body.in_time = data[i]['in time']
			if 'out time' in data[i]:
				right_body.out_time = data[i]['out time']
				
			main_body = ListMainBody()
			main_body.add_widget(left_body)
			main_body.add_widget(right_body)
			punch_data_container.add_widget(main_body, index=j)
	
	def open_punch_popup(self):
		self.ids.punch_popup.open()
		
	def open_weekly_off_popup(self):
		WeeklyOffPopup().open()
		
	def switch_screen(self, screen: str):
		self.current = screen
	
	def open_info_popup(self, text):
		InfoPopup(text=text).open()
		
	def export_data(self):
		def start_export(popup):
			popup.dismiss()
			toast('exporting data')
			p = PunchManager()
			directory = ''
			try:
				directory = storagepath.get_external_storage_dir()
				if os.path.exists(os.path.join(directory, 'punch')):
					if os.path.isdir(os.path.join(directory, 'punch')):
						pass
					else:
						os.makedirs(os.path.join(directory, 'punch'))
				else:
					os.makedirs(os.path.join(directory, 'punch'))
				directory = os.path.join(directory, 'punch')
			except Exception as e:
				toast('Failed to export')
				popup = InfoPopup()
				popup.title = 'Error'
				popup.text = str(e)
				popup.open()
				
				
			if directory:
				p.export(directory)
			else:
				p.export()
			toast('Exporting Done.')
			
		def confirm():
			popup = InfoPopup()
			directory = storagepath.get_external_storage_dir()
			directory = os.path.join(directory, 'punch')
			
			popup.title = 'Infornation'
			popup.text = ('Exporting as: \"' +
			str(os.path.join(directory, 'punch.pn')) +
			'\" please use this file to import your data')
			popup.on_ok = lambda: start_export(popup)
			popup.open()
			
		def permission_callback(permission, granted):
			if all(granted):
				confirm()
				return
			return
		if has_permission():
			confirm()
		else:
			request_permissions([
				Permission.READ_EXTERNAL_STORAGE,
				Permission.WRITE_EXTERNAL_STORAGE
			], callback= permission_callback)
		
	def import_data(self, file):
		def start_import():
			toast('Start importing')
			p = PunchManager()
			p.import_data(file)
			toast('Import complete.')
			self.reload()
		
		def permission_callback(permission, granted):
			if all(granted):
				start_import()
				return
			return
		if has_permission():
			start_import()
		else:
			request_permissions([
				Permission.READ_EXTERNAL_STORAGE,
				Permission.WRITE_EXTERNAL_STORAGE
			], callback= permission_callback)
		
	def open_url(self, url):
		if platform== 'android':
			from android import open_url
			open_url(url)
			
			
	def open_file_manager(self):
		def exit_manager(exit_code):
			if exit_code == 1:
				mn.close()
				
		def select_path(file):
			mn.close()
			self.import_data(file)
			
		def open_manager():
			external_dir = storagepath.get_external_storage_dir()
			mn.show(external_dir)
		
		def permission_callback(permission, granted):
			if all(granted):
				open_manager()
				return
			return 
			
		mn = MDFileManager(
		exit_manager = exit_manager,
		select_path = select_path,
		)
		if has_permission():
			open_manager()
		else:
			request_permissions([
				Permission.READ_EXTERNAL_STORAGE,
				Permission.WRITE_EXTERNAL_STORAGE
			], callback= permission_callback)
		
	
class MainApp(MDApp):
	def build(self):
		self.theme_cls.theme_style_switch_animation = True
		self.theme_cls.material_style = 'M2'
		return MainWindow()
		
	def on_start(self):
		def on_import_popup_ok(ins, file):
			# param: < ins > an instance of InfoPopup
			# for dismiss the popup
			ins.dismiss()
			self.root.import_data(file)
			if punch_mn.need_to_punch:
				self.root.open_punch_popup()
			
			
		def permission_callback(x, y):
			pass
			
		def ask_permission():
			try:
				pr = [
				Permission.READ_EXTERNAL_STORAGE,
				Permission.WRITE_EXTERNAL_STORAGE
				]
				request_permission(
				pr, callback = permission_callback)
			except:
				pass
				
		def need_to_import_data():
			if not has_permission():
				ask_permission()
				return
			external_dir = storagepath.get_external_storage_dir()
			file = os.path.join(
			external_dir, 'punch', punch_mn.BACKUP_FILE
			)
			if os.path.exists(file):
				popup = InfoPopup()
				popup.title = 'Info'
				popup.text = 'We found a backup file in your device do you want to import it?'
				popup.on_ok = lambda: on_import_popup_ok(popup, file)
				popup.open()
			
			
		super().on_start()
		self.config = Configure()
		punch_mn = PunchManager()
		
		new_device = self.config.get('Genral', 'new-device')
		if new_device:
			ask_permission()
			need_to_import_data()
			self.config.update('Genral', 'new-device', False)
		else:
			if punch_mn.need_to_punch:
				self.root.open_punch_popup()
				
			
		theme = self.config.get('Genral', 'theme')
		self.change_theme_style(theme)
		
		if theme == 'Dark':
			self.root.ids.theme_switch.active = True
		else:
			self.root.ids.theme_switch.active = False
		
		try:
			weekly_offs = self.config.get('User', 'weekly off')
			print(self.config.get('Genral', 'theme'))
			self.root.weekly_offs = weekly_offs
		except KeyError:
			pass
		
		self.config.update('User', 'recent-login', str(datetime.now()))
		self.root.reload()
		
		
					
				
		
	def change_theme_style(self, theme=None):
		if theme:
			if theme == 'Dark':
				self.theme_cls.theme_style = 'Dark'
				self.theme_cls.primary_palette = 'BlueGray'
				self.config.update("Genral", 'theme', 'Dark')
				
			else:
				self.theme_cls.theme_style = 'Light'
				self.theme_cls.primary_palette = 'Blue'
				self.config.update("Genral", 'theme', 'Light')
				
			super().on_start()
			return 
			
		if self.theme_cls.theme_style == 'Dark':
			self.theme_cls.theme_style = 'Light'
			self.theme_cls.primary_palette = 'Blue'
			self.config.update("Genral", 'theme', 'Light')
			
		else:
			self.theme_cls.theme_style = 'Dark'
			self.theme_cls.primary_palette = 'BlueGray'
			self.config.update("Genral", 'theme', 'Dark')
		super().on_start()
		
	def sactive(self, ins, value):
		if value:
			self.change_theme_style('Dark')
			print('Setting dark thems')
		else:
			self.change_theme_style('Light')
			print('Setting Light Theme')
		
		
		
if __name__=="__main__":
	app = MainApp()
	app.run()