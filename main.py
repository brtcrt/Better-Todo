import tkinter as tk  # Import the modules for interfaces.
from tkinter import messagebox  # Fucking pop-up windows. It works brilliantly though. Also super easy to use.
import json  # Standard json library. Using this for data storage. Unstable but works.
from tkinter import ttk  # For quick access to parts like the Button.
from tkcalendar import Calendar  # Used for the date picking.
from datetime import date, datetime  # Used for setting starting date.
import threading, time  # Threading for checking time.

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
addedTask = ""  # To put all the info received in to order.


def PickDate():  # To pick a date for the task.
    def print_sel():
        global addedTask, tasks_list, task
        AddTask()  # Adding the task from the input box. See the function for more info.
        this_time = GetTime()  # Get time. See the function for more info.
        tasks = "tasks"  # This is just stupid but it fixed some error so I had to do it.
        if addedTask == "":  # Solves a problem where the program would die if the user enters an empty string. Idk who'd do that, but yeah. Just in case.
            messagebox.showinfo("Something bad happened :(", "Please enter your task first!")  # Also to keep everything in order. (Task first, date second)
        else:
            this_date = cal.selection_get()  # Gets the date.
            task[tasks].append(str(addedTask) + " --- Task Date: " + str(this_date) + " --- " + str(this_time))  # Combines the task & date into a single string so it is easier to display.
            top.destroy()  # Auto close.
            SaveToJson()  # Saves to the json file. Also updates the list displayed. See the function for more info.

    top = tk.Toplevel(root)  # Init the window.
    t_width = 350
    t_height = 350
    t_left = int(top.winfo_screenwidth() / 2 - t_width / 2)
    t_right = int(top.winfo_screenheight() / 2 - t_height / 2)
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


def AddTask():  # Get the tasks name from the user.
    global task, addedTask, task_entry, t_var
    if str(task_entry.get()) == "":  # If the input is empty string
        return  # Do nothing
    else:
        addedTask = (str(task_entry.get()))  # This should have been the first function that I wrote but it wasn't so it's gonna stay here.
    t_var.set("")  # Reset the text box.


def GetList():  # Needed this because I didn't want to keep writing the same stuff.
    i, last_list = 0, ""
    global task
    for t_ in task["tasks"]:  # Putting all the tasks in the list/dictionary in to a neat little string.
        i += 1  # Counter. I know there is a simpler way of doing this but I can't be bothered.
        last_list = last_list + "{}) Task name: ".format(str(i)) + t_ + "\n"
    return last_list


def RefreshList():  # Showing the list.
    global strvar
    new_info = GetList()  # Get the current list.
    strvar.set(new_info)  # Display it on to the screen.


def DeleteTask():  # Delete Tasks.
    global task, delete_entry, d_var
    delete_return = str(delete_entry.get())  # Get the input.
    delete_return.replace(" ", "")  # Replace any spaces with "" so that it's easier to turn into a list.
    delete_return = delete_return.split(",")  # Split with , to make it into a list.
    if delete_return[0] == "all":  # If the first argument is all, then delete every task.
        task["tasks"] = []
        SaveToJson()  # Save to json and update the list.
        d_var.set("")  # Reset the input box.
        return
    else:  # If some list indices were supplied:
        delete_return.sort(reverse=True)  # idk why I did this. I don't think it is actually necessary.
        try:
            if not len(set(delete_return)) == len(delete_return): return messagebox.showinfo("Something bad happened :(", "You entered the same number twice!")  # Some necessary checks.
            if not len(task["tasks"]) > len(delete_return): return messagebox.showinfo("Something bad happened :(", "You entered too many arguments!")  # Some necessary checks.
            remove_list = []
            for index in delete_return:  # Get the name of the removed item and push it into a list.
                delete_index = int(index)
                to_remove = task["tasks"][delete_index - 1]
                remove_list.append(to_remove)
            for member in remove_list:  # Remove the tasks.
                task["tasks"].remove(member)
            SaveToJson()  # Save to json and update the list.
            d_var.set("")  # Reset the input box.
            return
        except ValueError:
            d_var.set("")  # Reset the input box.
            return messagebox.showinfo("Something bad happened :(", "Received bad characters!")  # If it isn't "all" or a number it would give an error so I'm just excepting that.


def CheckDates():  # I spent so much time on this useless thing. There might be a faster and shorter way of doing it but I wrote it like this and can't be bothered to change it. But hey, it at least works.
    global task  # And no, I'm not actually going to talk about this function in detail. Even I have trouble understanding what goes on.
    present = date.today()
    count = 0
    all_tasks = GetList()
    all_tasks = all_tasks.replace("\n", " --- ")
    all_tasks = all_tasks.split(" --- ")
    task_index = []
    past_index = []
    all_dates = []
    past_dates = []
    past_tasks = []
    due_dates = []
    due_tasks = []
    for i in range(1, len(all_tasks), 3):
        try:
            all_dates.append(all_tasks[i])
            print(all_tasks[i])
        except IndexError:
            print("Index Error")
    all_dates = "".join(all_dates).replace("Task Date: ", " ").split(" ")
    del all_dates[0]
    for dates in all_dates:
        current = dates.split("-")
        current.insert(0, str(count + 1))
        if date(int(current[1]), int(current[2]), int(current[3])) < present:
            past_dates.append(" ".join([str(elem) for elem in current]))
        if date(int(current[1]), int(current[2]), int(current[3])) == present:
            due_dates.append(" ".join([str(elem) for elem in current]))
        count += 3
    for elem in due_dates:
        cur = elem.split(" ")
        task_index.append(cur[0])
    for index in task_index:
        due_tasks.append(all_tasks[int(index) - 1])
    for elem in past_dates:
        cur = elem.split(" ")
        past_index.append(cur[0])
    for index in past_index:
        past_tasks.append(all_tasks[int(index) - 1])
    return due_tasks, past_tasks


def ShowAtStart():
    due, past = CheckDates()  # Calls the function above which gives the due tasks and the passed tasks.
    total = ""
    if not past == []:
        total += "Tasks which you have missed: \n"  # Merge them together.
        for member in past:
            total += "{}\n".format(member)
    if not due == []:
        total += "\n\nTasks for today: \n"
        for member in due:
            total += "{}\n".format(member)
    if total == "":  # If there isn't anything worth mentioning, then don't show the message box.
        return
    else:
        return messagebox.showinfo("Attention", total)


def GetTime():
    global minute_var, hour_var
    return hour_var.get() + ":" + minute_var.get()


def CheckTime():
    global minutes, task
    time_up = []
    while True:
        if str(datetime.now().minute) in minutes:
            current_items = GetList().split("\n")
            del current_items[len(current_items) - 1]
            for item in current_items:
                new_item = item.split(" --- ")
                print(new_item)
                print("Task Date: {}".format(str(date.today())))
                if new_item[1] != "Task Date: {}".format(str(date.today())):
                    return
                date_item = new_item[2].split(":")
                print(date_item)
                if date_item[0] == str(datetime.now().hour) and date_item[1] == str(datetime.now().minute):
                    time_up.append(new_item[0])
            if time_up == []:
                time.sleep(60)
                pass
            else:
                latests_alarms = "\n".join(time_up)
                messagebox.showinfo("Time is up!", latests_alarms)
                time.sleep(60)
                return "Done!"
        time.sleep(60)


root = tk.Tk()  # The core of the tkinter interface system.
s = ttk.Style(root)  # Some styling.
s.theme_use('clam')  # Some more styling.
t_var = tk.StringVar()  # String variables to reset it back to "".
d_var = tk.StringVar()  # ^^^^^^^^
task_entry = ttk.Entry(root, textvariable=t_var)  # Getting the input from the user. This is the thing which adds the little input box.
task_entry.pack(padx=10, pady=10, fill="both", expand=1)  # Packing it separately because it wouldn't stop giving errors.
hours = ["01", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "00"]
hour_var = tk.StringVar()
hour_var.set("12")
minutes = ["00", "00", "10", "15", "20", "30", "40", "45", "50"]
minute_var = tk.StringVar()
minute_var.set("00")
hour_label = ttk.Label(root, text="Hour: ").pack(padx=10, pady=10)
hour_select = ttk.OptionMenu(root, hour_var, *hours)
hour_select.pack(padx=10, pady=10)
minute_label = ttk.Label(root, text="Minute: ").pack(padx=10, pady=10)
minute_select = ttk.OptionMenu(root, minute_var, *minutes)
minute_select.pack(padx=10, pady=10)
ttk.Button(root, text="Set task", command=PickDate).pack(padx=10, pady=10)  # Button for setting task.
delete_entry = ttk.Entry(root, textvariable=d_var)  # Delete input box.
delete_entry.pack(padx=10, pady=10, fill="both")  # Pack.
ttk.Button(root, text="Delete", command=DeleteTask).pack(padx=10, pady=10)  # Delete button that calls the delete function.
strvar = tk.StringVar()  # Actual list part. The variable for the text.
info = GetList()  # Get the list.
strvar.set(info)  # Put the info into the variable.
label = ttk.Label(root, textvariable=strvar)  # Create the label with the variable.
label.pack(padx=10, pady=10, fill="both")  # Pack.
w_width = 550  # Screen stuff...
w_height = 550  # Screen stuff...
s_left = int(root.winfo_screenwidth() / 2 - w_width / 2)  # Screen stuff...
s_right = int(root.winfo_screenheight() / 2 - w_height / 2)  # Screen stuff...
root.geometry("{}x{}+{}+{}".format(w_width, w_height, s_left, s_right))  # Center the window and set the size.
root.title("Todo List")  # Title
root.iconbitmap("icon.ico")  # Icon
ShowAtStart()  # Call this function at start-up to see if there is anything relevant.
thread = threading.Thread(target=CheckTime)
thread.start()
root.mainloop()  # Finally initialize the program.
