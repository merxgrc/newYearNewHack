from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout


class Task:
    def __init__(self, name, deadline, creation, desc):
        self.name = name
        self.deadline = deadline
        self.creation = creation
        self.desc = desc
        self.complete = False


class TaskList:
    def __init__(self):
        self.tasks = []


def create_task_popup(instance):
    popup = Popup(title="Create new task",
                  content=Label(text='Ohh, you found me!'),
                  size_hint=(0.5, 0.5))
    popup.open()


def create_tasklist_popup(instance):
    popup = Popup(title="Create new tasklist",
                  content=Label(text='Ohh, you found me!'),
                  size_hint=(0.5, 0.5))
    popup.open()


class New(BoxLayout):

    def __init__(self, **kwargs):
        super(New, self).__init__(**kwargs)
        button_create_task = Button(text='New task')
        button_create_task.bind(on_press=create_task_popup)
        self.add_widget(button_create_task)
        btn1 = Button(text='New task list')
        btn1.bind(on_press=create_tasklist_popup)
        self.add_widget(btn1)


class MainLayout(BoxLayout):

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text="Hello world!"))
        new = New()
        self.add_widget(new)


class MyApp(App):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    MyApp().run()
