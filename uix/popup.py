import calendar
from kivy.app import App
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarIconListItem, ILeftBody
from kivymd.uix.selectioncontrol.selectioncontrol import MDCheckbox

from config import Configure 


class WeeklyListMainBody(OneLineAvatarIconListItem):
	pass

class WeeklyListLeftBody(ILeftBody, MDCheckbox):
	day = StringProperty(None)

class WeeklyOffPopup:
	def __init__(self):
		try:
			submit_button_text = 'Update' if Configure().get("User", 'weekly off') else 'Set'
		except KeyError:
			submit_button_text = 'Set'
		self.submit_button = MDFlatButton(
		text= submit_button_text,
		on_release= self.submit)
		
		days = list(calendar.day_name)
		days_list = []
		for i in days:
			list_item = WeeklyListMainBody(text=i)
			checkbox = WeeklyListLeftBody(day=i, on_active = self.on_checkbox_check)
			checkbox.bind(active=self.on_checkbox_check)
			list_item.add_widget(checkbox)
			days_list.append(list_item)
			
		self._dialog = MDDialog(
		title = 'Select days',
		text = 'You can select only two days.',
		type = 'simple',
		auto_dismiss = False,
		items = days_list,
		buttons = [
		MDFlatButton(
			text= 'Cancel',
			on_release= lambda x: self.dismiss(),
		),
		self.submit_button,
		])
		
	def submit(self, ins):
		configure = Configure()
		if hasattr(self, 'temp_selected_days'):
			if len(self.temp_selected_days):
				configure.update(
					section = 'User',
					key = 'weekly off',
					value = ',' .join(self.temp_selected_days)
				)
				root = App.get_running_app().root
				root.ids.weekly_offs_label.text = configure.get('User', 'weekly off')
				
		self.dismiss()
				
		
	def open(self):
		self._dialog.open()
		
	def dismiss(self):
		self._dialog.dismiss()
		
	def on_checkbox_check(self, ins, value):
		if value:
			if hasattr(self, 'temp_selected_days'):
				if len(self.temp_selected_days) > 1:
					ins.active = False
					return 
				else:
					self.temp_selected_days.append(ins.day)
			else:
				self.temp_selected_days = []
				self.temp_selected_days.append(ins.day)
		else:
			if hasattr(self, 'temp_selected_days'):
				try:
					self.temp_selected_days.remove(ins.day)
				except ValueError:
					pass
					

class InfoPopup(MDDialog):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.title = 'Info'
		self.text = 'imoptant information'
		
		cancel_button = MDFlatButton(
			text= 'Cancel',
			on_release= lambda x: self.dismiss(),
		)
		ok_button = MDFlatButton(
			text= 'Ok',
			on_release= lambda x: self.on_ok(),
		)
		self.buttons = [cancel_button, ok_button]
		self.ids.root_button_box.height = "52dp"
		self.create_buttons()
		
	def on_ok(self):
		'''overwrite this function for ok button event
		this function get fired when ok button release '''
		self.dismiss()
		
		
