from tkinter import *
from tkinter import Tk, messagebox
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk


gui = ThemedTk(theme="winxpblue")
gui.title("LanO-Lan Configuration")
gui.geometry("300x412")
gui.resizable(False, False)
gui.config(highlightbackground="black", highlightthickness=2)

style = ttk.Style()
style.theme_use('alt')
style.configure('serveroff.TButton', background='red', foreground='white', font=('Comic Sans MS', 10, 'bold'))
style.configure('serveron.TButton', background='green', foreground='white', relief='sunken', font=('Comic Sans MS', 10, 'bold'))

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








possible_ports = ['port1', 'port2', 'port3']
registered_users_list = ['user1', 'user2']

selected_port = tk.StringVar(value='port1')
selected_user = tk.StringVar(value='user1')



tk.messagebox.showinfo("Welcome to LanO'Lan!", "Here you can configure, turn on, and close the LanO'Lan server as the admin and server hoster.")
tk.messagebox.showinfo("Server Status & Controls","The button below shows the current server status. Click it to turn the server on/off. Use the other buttons, widgets and dropdown menus to register, view, inspect or delete registered users.")
tk.messagebox.showwarning("Certificates", "Certificates are automatically configured when the server is turned on. Incase you want to override them and use your own, uncheck the 'Configure Certificates' checkbox.")
user = tk.StringVar()
password = tk.StringVar()
registered_users = {}
link = tk.StringVar(value="https://192.168.1.4:8000")
certify= tk.BooleanVar()
status_button = ttk.Button(gui, text="Server: OFF", command=lambda: status_trigger())
username_label = ttk.Label(gui, text="Username", font=('Comic Sans MS', 10, 'bold'))
password_label = ttk.Label(gui, text="Password", font=('Comic Sans MS', 10, 'bold'))
username_entry = ttk.Entry(gui, textvariable=user)
password_entry = ttk.Entry(gui, textvariable=password)
register_button = ttk.Button(gui, text="Register", command=lambda: register_all(user.get(), password.get()))
add_button = ttk.Button(gui, text="Add", command=lambda: add_user(user.get(), password.get()))
inspect_button = ttk.Button(gui, text="Inspect", command=lambda: inspect_user(selected_user.get()))
delete_button = ttk.Button(gui, text="Delete", command=lambda: delete_user(selected_user.get()))
selected_user_menu = ttk.OptionMenu(gui, selected_user, *registered_users_list)
selected_port_menu = ttk.OptionMenu(gui, selected_port, *possible_ports)
link_label =ttk.Entry(gui, state='readonly', textvariable=link, justify='center', font=('Comic Sans MS', 8, 'bold'))
certify_button = ttk.Checkbutton(gui, text="Certificates", variable=certify)
user_list_label = ttk.Label(gui, text="User List", font=('Comic Sans MS', 10, 'bold'))
port_list_label = ttk.Label(gui, text="Port Selection", font=('Comic Sans MS', 10, 'bold'))

link_label.grid(column=1, row=1, padx=5, pady=5, columnspan=2)
username_label.grid(column=1, row=2, padx=5, pady=5, columnspan=2)
password_label.grid(column=1, row=4, padx=5, pady=5, columnspan=2)
username_entry.grid(column=1, row=3, padx=5, pady=5, columnspan=2, sticky='ew')
password_entry.grid(column=1, row=5, padx=5, pady=5, columnspan=2, sticky='ew')
selected_port_menu.grid(column=1, row=7, padx=5, pady=5, columnspan=2, sticky='ew')
selected_user_menu.grid(column=1, row=9, padx=5, pady=5, columnspan=2, sticky='ew')
inspect_button.grid(column=0, row=10, padx=5, pady=5, sticky='ew')
add_button.grid(column=1, row=10, padx=5, pady=5, sticky='ew')
register_button.grid(column=2, row=10, padx=5, pady=5, sticky='ew')
delete_button.grid(column=3, row=10, padx=5, pady=5, sticky='ew')
certify_button.grid(column=1, row=11, padx=5, pady=5, columnspan=2, sticky='ew')
status_button.grid(column=1, row=0, pady=5, padx=5, columnspan=2 ,sticky='ew')
user_list_label.grid(column=1, row=8, padx=5, pady=5, columnspan=2)
port_list_label.grid(column=1, row=6, padx=5, pady=5, columnspan=2)


status_button.config(style='serveroff.TButton')

gui.columnconfigure(0, weight=1)
gui.columnconfigure(1, weight=1)
gui.columnconfigure(2, weight=1)
gui.columnconfigure(3, weight=1)

gui.mainloop()