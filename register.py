from tkinter import Tk, messagebox
import tkinter as tk

gui = Tk()
gui.title("LanO-Lan Configuration")
gui.config(bg="PeachPuff")
gui.geometry("260x400")
gui.resizable(False, False)


def register_all(username, password):
    print("soon")
def add_user(username, password):
    print("soon")
def inspect_user(username):
    print("soon")
def delete_user(username):
    print("soon")
def status_trigger():
    print("soon")


possible_ports = ['dummy']
registered_users_list = ['dummy']

appframe = tk.Frame(gui)

selected_port = tk.StringVar(value='dummy')
selected_user = tk.StringVar(value='dummy')
tk.messagebox.showinfo("Welcome to LanO'Lan!", "Here you can configure, turn on, and close the LanO'Lan server as the admin and server hoster.")
tk.messagebox.showinfo("Server Status & Controls","The button below shows the current server status. Click it to turn the server on/off. Use the other buttons, widgets and dropdown menus to register, view, inspect or delete registered users.")
tk.messagebox.showwarning("Certificates", "Certificates are automatically configured when the server is turned on. Incase you want to override them and use your own, uncheck the 'Configure Certificates' checkbox.")
user = tk.StringVar()
password = tk.StringVar()
registered_users = {}
link = tk.StringVar()
certify= tk.BooleanVar()
status_button = tk.Button(gui, text="Server: OFF", command=lambda: status_trigger())
username_label = tk.Label(gui, text="Username")
password_label = tk.Label(gui, text="Password")
username_entry = tk.Entry(gui, textvariable=user)
password_entry = tk.Entry(gui, textvariable=password)
register_button = tk.Button(gui, text="Register", command=lambda: register_all(user.get(), password.get()))
add_button = tk.Button(gui, text="Add", command=lambda: add_user(user.get(), password.get()))
inspect_button = tk.Button(gui, text="Inspect", command=lambda: inspect_user(selected_user.get()))
delete_button = tk.Button(gui, text="Delete", command=lambda: delete_user(selected_user.get()))
selected_user_menu = tk.OptionMenu(gui, selected_user, *registered_users_list)
selected_port_menu = tk.OptionMenu(gui, selected_port, *possible_ports)
link_label =tk.Label(gui, textvariable=link)
certify_button = tk.Checkbutton(gui, text="Generate Certificates", variable=certify)

link_label.grid(column=1, row=1, padx=5, pady=5, columnspan=2)
username_label.grid(column=1, row=2, padx=5, pady=5, columnspan=2)
password_label.grid(column=1, row=3, padx=5, pady=5, columnspan=2)
username_entry.grid(column=1, row=4, padx=5, pady=5, columnspan=2, sticky='ew')
password_entry.grid(column=1, row=5, padx=5, pady=5, columnspan=2, sticky='ew')
selected_port_menu.grid(column=1, row=6, padx=5, pady=5, columnspan=2, sticky='ew')
selected_user_menu.grid(column=1, row=7, padx=5, pady=5, columnspan=2, sticky='ew')
inspect_button.grid(column=0, row=8, padx=5, pady=5, sticky='ew')
add_button.grid(column=1, row=8, padx=5, pady=5, sticky='ew')
register_button.grid(column=2, row=8, padx=5, pady=5, sticky='ew')
delete_button.grid(column=3, row=8, padx=5, pady=5, sticky='ew')
certify_button.grid(column=1, row=9, padx=5, pady=5, columnspan=2, sticky='ew')
status_button.grid(column=1, row=0, pady=5, padx=5, columnspan=2 ,sticky='ew')


gui.columnconfigure(0, weight=0)
gui.columnconfigure(1, weight=1)
gui.columnconfigure(2, weight=1)
gui.columnconfigure(3, weight=1)
gui.columnconfigure(4, weight=1)
gui.columnconfigure(5, weight=0)

gui.mainloop()