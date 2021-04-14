import tkinter as tk  # Import the modules for interfaces.
from tkinter import messagebox  # Fucking pop-up windows. It works brilliantly though. Also super easy to use.
import json  # Standard json library. Using this for data storage. Unstable but works.
from tkinter import ttk  # For quick access to parts like the Button.
from tkcalendar import Calendar  # Used for the date picking.
from datetime import date, datetime  # Used for setting starting date.
import threading  # Threading for checking time.
import time
import os, win32com.client, getpass, sys, shutil

exited = False  # Used to check if the user has exited the program

with open('tasks.json') as json_file:
    try:
        tasks_loaded = json.load(json_file)  # Getting the saved info from the json file.
    except KeyError:
        print("Some random key error from start up or the json file was changed.")  # Problems with using .json as a db.
task = {"tasks": []}  # Using a dictionary to store data whilst the program is running. This also makes converting to json easy.
try:
    tasks_list = tasks_loaded["tasks"]  # Get the data.
    task["tasks"] = tasks_list  # Current data is set to saved data on start up. Basically how the save-load system works.
except KeyError:
    print("Some random key error from start up or the json file was changed.")  # Problems with using .json as a db.
task_object = {  # Keeps all the data in a neat dictionary.
    "task": "",
    "date": "",
    "time": ""
}


def On_StartUp():
    curr_wd = os.getcwd()
    user = getpass.getuser()
    start_up = r"C:\Users\{}\Appdata\Roaming\Microsoft\Windows\Start Menu\Programs\StartUp".format(user)
    try:
        target = curr_wd + r"\Better-Todo.lnk"
        dest = start_up + r"\Better-Todo.lnk"
        shutil.copyfile(target, dest)
    except ValueError:
        return


On_StartUp()


def PickDate():  # To pick a date for the task.
    def print_sel():
        global tasks_list, task, task_object
        AddTask()  # Adding the task from the input box. See the function for more info.
        if task_object["task"] == "":  # Solves a problem where the program would die if the user enters an empty string. Idk who'd do that, but yeah. Just in case.
            messagebox.showinfo("Something bad happened :(", "Please enter your task first!")  # Also to keep everything in order. (Task first, date second)
        else:
            this_date = cal.selection_get()  # Gets the date.
            task_object["date"] = str(this_date)
            task["tasks"].append(task_object)  # Combines the task & date into a single string so it is easier to display.
            task_object = {}
            top.destroy()  # Auto close.
            SaveToJson()  # Saves to the json file. Also updates the list displayed. See the function for more info.

    top = tk.Toplevel(root)  # Init the window.
    t_width = 350
    t_height = 350
    t_left = int(top.winfo_screenwidth() - t_width - 60)
    t_right = int(top.winfo_screenheight() - t_height - 100)
    top.geometry("{}x{}+{}+{}".format(t_width, t_height, t_left, t_right))  # Appear at the center.
    cal = Calendar(top, font="Arial 14", selectmode='day', cursor="hand1", year=date.today().year, month=date.today().month, day=date.today().day)  # The date-picker system.
    cal.pack(fill="both", expand=True)  # Packing it.
    button = ttk.Button(top, text="Choose", command=print_sel)  # The pick date button.
    button.pack()  # Packing it.


def SaveToJson():  # Saving to the local json database.
    global task
    with open('tasks.json', 'w') as tasks_dumped:
        json.dump(task, tasks_dumped, indent=3, sort_keys=True)  # This somehow fucking works.
    RefreshList()  # Refresh the list every time a change happens.
    # colorizeTasks()


def AddTask():  # Get the tasks name from the user.
    global task, task_entry, t_var
    if str(task_entry.get()) == "":  # If the input is empty string
        return  # Do nothing
    else:
        task_object["task"] = (str(task_entry.get()))  # This should have been the first function that I wrote but it wasn't so it's gonna stay here.
    t_var.set("")  # Reset the text box.


def RefreshList():  # Showing the list.
    global tree, task
    some_count = 0  # To keep track of the id.
    tree.delete(*tree.get_children())  # Deletes everything.
    due_t, past_t = CheckDates()  # Gets the due dates and the past dates.
    colorizeTasks()  # "Sorts" them by color. Light blue is due today, and pink is missed.
    for t_ in task["tasks"]:  # Puts everything back.
        if not due_t and not past_t:  # Some checks to see if there are any due and past tasks.
            tree.insert(parent="", index="end", iid=some_count, text="", values=(t_["task"], t_["time"], t_["date"]))
        elif past_t and due_t:
            if [t_["date"] == member["date"] for member in due_t][0]:
                print("got one due1 {}".format(t_["task"]))
                tree.insert(parent="", index="end", iid=some_count, text="", values=(t_["task"], t_["time"], t_["date"]), tags=("due",))
            elif [t_["date"] == member["date"] for member in past_t][0]:
                print("got one past1 {}".format(t_["task"]))
                tree.insert(parent="", index="end", iid=some_count, text="", values=(t_["task"], t_["time"], t_["date"]), tags=("missed",))
            else:
                tree.insert(parent="", index="end", iid=some_count, text="", values=(t_["task"], t_["time"], t_["date"]))
        elif due_t and not past_t:
            if [t_["date"] == member["date"] for member in due_t][0]:
                print("got one due2 {}".format(t_["task"]))
                tree.insert(parent="", index="end", iid=some_count, text="", values=(t_["task"], t_["time"], t_["date"]), tags=("due",))
            else:
                tree.insert(parent="", index="end", iid=some_count, text="", values=(t_["task"], t_["time"], t_["date"]))
        elif past_t and not due_t:
            if [t_["date"] == member["date"] for member in past_t]:
                print("got one past2 {}".format(t_["task"]))
                tree.insert(parent="", index="end", iid=some_count, text="", values=(t_["task"], t_["time"], t_["date"]), tags=("missed",))
        some_count += 1


def colorizeTasks():  # Colorize the tasks in the treeview
    tree.tag_configure('missed', background='pink')  # Pink. Red made the text unreadable.
    tree.tag_configure('due', background='lightblue')  # Light blue. Blue made the text unreadable.


def DeleteTask():  # Delete Tasks.
    global task, tree
    selected_item = tree.selection()[0]  # Gets which one is selected.
    tree.delete(selected_item)  # Deletes from treeview
    del task["tasks"][int(selected_item)]  # Deletes from task dictionary.
    SaveToJson()  # Saves to json.


def Clear():  # Deletes everything. Same logic with the DeleteTask function.
    global task, tree
    tree.delete(*tree.get_children())
    task["tasks"] = []
    SaveToJson()


def CheckDates():  # Checks if there are any due or past tasks. Returns them if there are any.
    global task
    present = date.today()
    count = 0
    past_ = []
    due_ = []
    for i in task["tasks"]:
        try:
            current = i["date"].split("-")
            current.insert(0, str(count + 1))
            if date(int(current[1]), int(current[2]), int(current[3])) < present:
                past_.append(i)
            if date(int(current[1]), int(current[2]), int(current[3])) == present:
                due_.append(i)
        except IndexError:  # Just in case.
            print("Index Error")
    return due_, past_


def ShowAtStart():
    due, past = CheckDates()  # Calls the function above which gives the due tasks and the passed tasks.
    total = ""
    if not past == []:
        total += "Tasks which you have missed: \n"  # Merge them together.
        for member in past:
            total += "{}\n".format(member["task"])
    if not due == []:
        total += "\n\nTasks for today: \n"
        for member in due:
            total += "{}\n".format(member["task"])
    if total == "":  # If there isn't anything worth mentioning, then don't show the message box.
        return
    else:
        return messagebox.showinfo("Attention", total)


def raiseBreak(): # When the program is closed, everything will close with it.
    global root, exited
    root.destroy()
    exited = True
    sys.exit()


def CheckTime():
    global minutes, task, root, exited
    time_up = []

    while True:
        print("Checking")
        if str(datetime.now().minute) in minutes:
            for _task in task["tasks"]:
                if _task["date"] != "{}".format(str(date.today())):
                    return
                date_item = _task["time"]
                date_item = date_item.split(":")
                if date_item[0] == str(datetime.now().hour) and date_item[1] == str(datetime.now().minute):
                    time_up.append(_task["task"])
            if time_up == []:
                time.sleep(60)
                pass
            else:
                latests_alarms = "\n".join(time_up)
                messagebox.showinfo("Time is up!", latests_alarms)
                time.sleep(60)
                return "Done!"

        root.protocol("WM_DELETE_WINDOW", raiseBreak)
        if exited:
            break
        time.sleep(60)


root = tk.Tk()  # The core of the tkinter interface system.
s = ttk.Style(root)  # Some styling.
s.theme_use('winnative')  # Some more styling.
tree = ttk.Treeview(root)  # A lot of treeview stuff. Styling etc...
style = ttk.Style(tree)
style.configure("Treeview", background="silver", foreground="black", rowheight=20, fieldbackground="silver")
style.map("Treeview", background=[("selected", "green")])
tree["column"] = ("Task", "Time", "Date")
tree.column('#0', width=0, stretch=tk.NO)
tree.column("Task", anchor=tk.CENTER, width=80)
tree.column("Time", anchor=tk.CENTER, width=80)
tree.column("Date", anchor=tk.CENTER, width=80)
tree.heading('#0', text="", anchor=tk.CENTER)
tree.heading("Task", anchor=tk.CENTER, text="Task")
tree.heading("Time", anchor=tk.CENTER, text="Time")
tree.heading("Date", anchor=tk.CENTER, text="Date")
tree.pack(padx=10, pady=10, fill="both", expand=1)
t_var = tk.StringVar()  # String variables to reset it back to "".
task_entry = ttk.Entry(root, textvariable=t_var)  # Getting the input from the user. This is the thing which adds the little input box.
task_entry.pack(padx=10, pady=10, fill="both", expand=1)  # Packing it separately because it wouldn't stop giving errors.
hours = ["01", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "00"]
hour_var = tk.StringVar()
hour_var.set("12")
minutes = ["00", "00", "10", "15", "20", "30", "40", "45", "50"]
minute_var = tk.StringVar()
minute_var.set("00")
hour_select = ttk.OptionMenu(root, hour_var, *hours)
hour_select.pack(padx=10, pady=10, side=tk.LEFT)
minute_label = ttk.Label(root, text="<---Hour // Minute--> ").pack(pady=10, padx=10, side=tk.LEFT)
minute_select = ttk.OptionMenu(root, minute_var, *minutes)
minute_select.pack(padx=10, pady=10, side=tk.LEFT)
ttk.Button(root, text="Set task", command=PickDate).pack(padx=10, pady=10)  # Button for setting task..
ttk.Button(root, text="Delete", command=DeleteTask).pack(padx=10, pady=10)  # Delete button that calls the delete function.
ttk.Button(root, text="Clear", command=Clear).pack(padx=10, pady=10)  # Delete button that calls the delete function.
strvar = tk.StringVar()  # Actual list part. The variable for the text.
w_width = 550  # Screen stuff...
w_height = 550  # Screen stuff...
s_left = int(root.winfo_screenwidth() - w_width - 10)  # Screen stuff...
s_right = int(root.winfo_screenheight() - w_height - 60)  # Screen stuff...
root.geometry("{}x{}+{}+{}".format(w_width, w_height, s_left, s_right))  # Center the window and set the size.
root.title("Todo List")  # Title
root.iconbitmap("icon.ico")  # Icon
RefreshList()
ShowAtStart()  # Call this function at start-up to see if there is anything relevant.
thread = threading.Thread(target=CheckTime)
thread.start()
root.protocol("WM_DELETE_WINDOW", raiseBreak)
root.mainloop()  # Finally initialize the program.
