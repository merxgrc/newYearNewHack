import os
import json
import codecs
import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty
from datepicker import DatePicker

# SHA-256 hash of "newYearNewHack" - json only allows dict keys to be strings,
# so this serves as a workaround to create a name for the default list that no user will ever accidentally repeat.
# Probably.
# (Stupid Kivy doesn't allow me to easily set length limits on TextInputs so that the default list name
#  could simply be something longer and achieve a 100% chance of not getting found out)
default_list = "485A39CA22060964FE81DE1A570636C167A2560E5EB6786E9B3CCE2004E49CCA485A39CA22060964FE81DE1A570636C167A2560E5EB6786E9B3CCE2004E49CCA"
# Data format: dict with values of the last open list and a dict containing all tasklists with tasklist names as keys
# and dicts, consisting of a task list and a "complete" boolean, as corresponding values
# Comes with a default list that contains all tasks that are not part of any lists.
# Save file example can be found as "TasksData_example.json"
data = {"last_opened": default_list,
        "tasklists": {default_list: {"tasks": [],
                                     "completed": True}}}


# Load data from save file
def load():
    with open('TasksData.json') as f:
        return json.load(f)


# Save data to file to recover it on next launch
def save():
    with open('TasksData.json', 'wb') as f:
        json.dump(data, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=4)


# Task object description
class Task:
    def __init__(self, name, deadline, desc, parent_list):
        self.name = name
        self.deadline = deadline
        self.creation_time = datetime.datetime.now()
        self.desc = desc
        self.complete = False
        self.parent_list = parent_list

    def get_data(self):
        task_data = {"name": self.name,
                     "deadline": self.deadline,
                     # To reverse: datetime.datetime.strptime(TIME_STRING, "%Y-%m-%d %H:%M:%S.%f")
                     "creation_time": str(self.creation_time),
                     "desc": self.desc,
                     "complete": self.complete}
        return task_data


# TODO: Task list description
class TaskList:
    def __init__(self, name):
        self.name = name
        self.tasks = []
        self.complete = True

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        self.tasks.remove(task)

    def update(self):
        self.complete = True
        for task in self.tasks:
            if not task.complete:
                self.complete = False
                break

    def get_data(self):
        return {"name": self.name,
                "completed": self.complete,
                "tasks": self.tasks}


# Store task in the data variable and call save()
def save_new_task(name, deadline, desc, parent_list, popup_instance):
    if parent_list == "Choose a task list":
        parent_list = default_list
    new_task = Task(name, deadline, desc, None)
    data["tasklists"][parent_list]["tasks"].append(new_task.get_data())
    data["tasklists"][parent_list]["completed"] = data["tasklists"][parent_list]["completed"] & True
    save()
    popup_instance.dismiss()
    success_msg = SuccessPopup("Task created")
    success_msg.open()
    Clock.schedule_once(success_msg.dismiss, 0.8)


def save_new_tasklist(name, popup_instance):
    new_tasklist = TaskList(name)
    tasklist_data = new_tasklist.get_data()
    data["tasklists"][tasklist_data["name"]] = {"tasks": tasklist_data["tasks"],
                                                "completed": tasklist_data["completed"]}
    save()
    popup_instance.dismiss()
    success_msg = SuccessPopup("Tasklist created")
    success_msg.open()
    Clock.schedule_once(success_msg.dismiss, 0.8)


# Success message popup with configurable title
class SuccessPopup(Popup):
    def __init__(self, text, **kwargs):
        super(SuccessPopup, self).__init__(title=text, size_hint=(0.4, None), size=(-1, 100), **kwargs)
        self.add_widget(Button(text="Ok", on_press=self.dismiss))


# Popup to input new task parameters
def create_task_popup():
    popup = Popup(title="Create new task",
                  size_hint=(0.5, 0.9))
    popup.add_widget(NewTaskPopupContent(popup))
    popup.open()


class NewTaskPopupContent(BoxLayout):
    def __init__(self, popup_instance, **kwargs):
        super(NewTaskPopupContent, self).__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='Name'))
        name_input = TextInput(hint_text="Task name", multiline=False)
        self.add_widget(name_input)
        self.add_widget(Label(text='Deadline'))
        deadline_input = DatePicker()
        self.add_widget(deadline_input)
        taskset = set(data["tasklists"].keys()) - {default_list, }
        if len(taskset) > 0:
            self.add_widget(Label(text="Task list"))
            tasklist_dropdown = DropDown()
            for key in list(taskset):
                tasklist_dropdown.add_widget(Button(text=key, size_hint_y=None, height=20,
                                                    on_release=lambda x: tasklist_dropdown.select(x.text)))
            tasklist_dropdown_btn = Button(text="Choose a task list",
                                           on_release=tasklist_dropdown.open)
            self.add_widget(tasklist_dropdown_btn)
            tasklist_dropdown.bind(on_select=lambda instance, x: setattr(tasklist_dropdown_btn, 'text', x))
        self.add_widget(Label(text="Description"))
        desc_input = TextInput(hint_text="Short description of the task.")
        self.add_widget(desc_input)
        self.add_widget(Button(text="Save", on_press=lambda *args: save_new_task(name_input.text,
                                                                                 deadline_input.text,
                                                                                 desc_input.text,
                                                                                 # TODO: CHANGE THIS once task lists are implemented
                                                                                 tasklist_dropdown_btn.text,
                                                                                 popup_instance)))
        self.add_widget(Button(text="Cancel", on_press=lambda *args: popup_instance.dismiss()))


# TODO: Popup to input new tasklist parameters
def create_tasklist_popup():
    popup = Popup(title="Create new List",
                  size_hint=(0.5, 0.9))
    popup.add_widget(NewTaskListPopupContent(popup))
    popup.open()


class NewTaskListPopupContent(BoxLayout):
    def __init__(self, popup_instance, **kwargs):
        super(NewTaskListPopupContent, self).__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='List name'))
        name_input = TextInput(hint_text='List name', multiline=False)
        self.add_widget(name_input)
        self.add_widget(Button(text='Save', on_press=lambda *args: save_new_tasklist(name_input.text, popup_instance)))
        self.add_widget(Button(text="Cancel", on_press=lambda *args: popup_instance.dismiss()))


# Sublayout for "Add-new-X" buttons
class New(BoxLayout):
    def __init__(self, **kwargs):
        super(New, self).__init__(size_hint_y=0.1, **kwargs)
        self.add_widget(Button(text='New task', size_hint_x=0.15, on_press=lambda x: create_task_popup()))
        self.add_widget(DarkerLabel(text=""))
        self.add_widget(Button(text='New task list', size_hint_x=0.2, on_press=lambda x: create_tasklist_popup()))


class Old(GridLayout):
    def __init__(self, **kwargs):
        super(Old, self).__init__(**kwargs)
        self.cols = 2
        for task in data["tasklists"][data["last_opened"]]["tasks"]:
            self.add_widget(Button(text="check", size_hint=(0.1, 0.1)))
            print(task["name"])
            self.add_widget(Label(text=task["name"], size_hint_y=0.1))
        self.add_widget(DarkerLabel(size_hint_x=0.1))
        self.add_widget(DarkerLabel())


# Main layout
# TODO: Once tasklists are implemented, convert to kivy.uix.pagelayout.Pagelayout
#  to allow swiping left-right between tasklists
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(orientation='vertical', **kwargs)
        if data["last_opened"] != default_list:
            self.add_widget(DarkerLabel(text=data["last_opened"], size_hint_y=0.05))
        else:
            self.add_widget(DarkerLabel(text="All", size_hint_y=0.05))
        self.add_widget(DarkLabel(size_hint_y=None, size=(-1, 2)))
        self.add_widget(Old())
        self.add_widget(New())


# Kivy initiation
class DarkLabel(Label):
    def __init__(self, **kwargs):
        super(DarkLabel, self).__init__(**kwargs)


class DarkerLabel(Label):
    def __init__(self, **kwargs):
        super(DarkerLabel, self).__init__(**kwargs)


class TaskellApp(App):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    if os.path.isfile("TasksData.json"):
        data = load()
    TaskellApp().run()
