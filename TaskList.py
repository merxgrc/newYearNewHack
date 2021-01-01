import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class MyGridLayout(GridLayout):
	#keyword args
	def __init__(self, **kwargs):
		super(MyGridLayout, self).__init__(**kwargs)

		self.cols = 2

		#widgets
		self.add_widget(Label(text="Task: "))

		self.task = TextInput(multiline=False)

		self.add_widget(self.task)


class MyApp(App):
	def build(self):
		return MyGridLayout()


if __name__ == '__main__':
	MyApp().run()