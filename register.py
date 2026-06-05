## libraries & Dependencies
from tkinter import *
from tkinter import Tk, messagebox
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import subprocess
import psutil
import os
import json
import socket
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import ipaddress
import bcrypt
from os import path
## GUI Configuration & Styles
gui = ThemedTk(theme="winxpblue")
gui.title("LanO-Lan Configuration")
gui.geometry("300x438")
gui.resizable(False, False)
gui.config(highlightbackground="black", highlightthickness=2)
style = ttk.Style()
style.theme_use('alt')
style.configure('serveroff.TButton', background='red', foreground='white', font=('Comic Sans MS', 10, 'bold'))
style.configure('serveron.TButton', background='green', foreground='white', relief='sunken', font=('Comic Sans MS', 10, 'bold'))
## Global Variables
BASE_DIR = os.path.dirname(__file__)
TEMP_DIR = os.path.join(os.getcwd(), "temp")
SETTING_DIR = os.path.join(os.getcwd(), "Settings")
iconpath = path.abspath(path.join(path.dirname(__file__), '2fixed32px.png'))
icon = tk.PhotoImage(file=iconpath)
service = None
user = tk.StringVar()
password = tk.StringVar()
registered_users = {}
registered_users_unhashed = {}
link = tk.StringVar(value="https://192.168.1.4:8000")
certify= tk.BooleanVar(value=True)
registered_users_list = ['user1', 'user2']
selected_user = tk.StringVar(value='user1')
session_hashed_users = {}
ipv4 = ''
max_wait_time = tk.StringVar(value="420")
max_time_seconds = 0
ipv4_entry = tk.StringVar(value="Empty4AutoIPV4")
## Functions
def start_service():
    global service
    if os.path.exists(os.path.join(SETTING_DIR,"Certificates", "cert.pem")) and os.path.exists(os.path.join(SETTING_DIR,"Certificates", "key.pem")):
        service = subprocess.Popen('server.exe')
    else:
        messagebox.showwarning("Certificates Not Found", "Kindly provide ceritficates cert.pem and key.pem in /Settings/Certificates or enable automatic certificate generation and click register at least once.")
def close_service():
    global service
    parentservice = psutil.Process(service.pid)
    for child in parentservice.children(recursive=True):
        child.terminate()
    parentservice.terminate()
def check_service():
    if service is None or service.poll() is not None:
        status_button.config(text="Server: OFF", style='serveroff.TButton')
    else:
        status_button.config(text="Server: ON", style='serveron.TButton')
    gui.after(2000, check_service)

def max_time():
    global max_wait_time
    global max_time_seconds
    try:
        max_time = int(max_wait_time.get()) * 60
        max_time_seconds = max_time
        with open (os.path.join(SETTING_DIR, "settings.json"), "r") as file:
            settings = json.load(file)
            settings["max_wait_time"] = max_time
        with open (os.path.join(SETTING_DIR, "settings.json"), "w") as file:
            json.dump(settings, file, indent=4)
    except:
        messagebox.showerror("Invalid Input", "Please enter a valid number for max wait time.")
def get_ipv4():
    global ipv4
    if str(ipv4_entry.get()) == "" or str(ipv4_entry.get()) == "Empty4AutoIPV4":
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipv4 = s.getsockname()[0]
        s.close()
    else:
        ipv4 = str(ipv4_entry.get())
def certificate():
    os.makedirs(os.path.join(SETTING_DIR, "Certificates"), exist_ok=True)
    key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,)
    with open(os.path.join(SETTING_DIR, "Certificates", "key.pem"), "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),))
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
        x509.NameAttribute(NameOID.COMMON_NAME, "mysite.com"),])
    cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(key.public_key()).serial_number(
        x509.random_serial_number()).not_valid_before(datetime.datetime.now(datetime.timezone.utc)).not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=100)).add_extension(
        x509.SubjectAlternativeName([x509.IPAddress(ipaddress.IPv4Address(ipv4))]), critical=False,).sign(key, hashes.SHA256())
    with open(os.path.join(SETTING_DIR,"Certificates", "cert.pem"), "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
def hash_pass(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
def ammend(username, hashed_password):
    with open(os.path.join(SETTING_DIR, "users_db.json"), "r") as file:
        users_db = json.load(file)
    if users_db == {
    "user": {
        "username": "user",
        "hashed_password": "$2b$12$JyHReOPNxOaIQqq5bATeneG71mkUEgpFW6ejQ6DAO/LZ6zZOtuyNa"
    },
    "user2": {
        "username": "user2",
        "hashed_password": "$2b$12$JyHReOPNxOaIQqq5bATeneG71mkUEgpFW6ejQ6DAO/LZ6zZOtuyNa"
    }}:
        users_db = {}
    users_db[username] = {"username": username, "hashed_password": hashed_password.decode('utf-8')}
    with open(os.path.join(SETTING_DIR, "users_db.json"), "w") as file:
        json.dump(users_db, file, indent=4)
def updateusermenu():
    global registered_users_list
    selected_user_menu['menu'].delete(0, 'end')
    for user in registered_users_list:
        selected_user_menu['menu'].add_command(label=user, command=tk._setit(selected_user, user))

def register_all():
    global registered_users, registered_users_unhashed, certify, session_hashed_users
    if certify.get() == True:
        certificate()
        for username, password in registered_users_unhashed.items():
            hashed_password = hash_pass(password)
            ammend(username, hashed_password)
        registered_users_unhashed = {}
        max_time()
        messagebox.showinfo("Registration Complete", "Access the server via the link provided")
    else:
        messagebox.showwarning("Automatic Certificate Generation Disabled", "Locally signed or CA signed certificates are required for the app to function. Either provide them on your own in /Settings/Certificates as cert.pem & key.pem or enable automatic certificate generation.")
        for username, password in registered_users_unhashed.items():
            hashed_password = hash_pass(password)
            ammend(username, hashed_password)
        registered_users_unhashed = {}
        max_time()
        messagebox.showinfo("Registration Complete", "Access the server via the link provided")
    updateusermenu()
        
    


def add_user(username, password):
    global registered_users_unhashed
    registered_users_unhashed[username] = password
    registered_users_list.append(username)
    updateusermenu()
def inspect_user(username):
    if username in registered_users_unhashed:
        messagebox.showinfo("Inspect User", f"Username: {username}\nPassword: {registered_users_unhashed[username]}")
    else: messagebox.showwarning("Inspect User", f"User '{username}' was registered prior to this session and his password has been encrypted.")
def delete_user(username):
    global registered_users_unhashed
    messagebox.showwarning("Info", "This action deletes users that are to be registered, not already registered ones, for that you'll need to manually remove usernames from Settings/users_db.json")
    if username in registered_users_unhashed:
        del registered_users_unhashed[username]
    if username in registered_users_list:
        registered_users_list.remove(username)
    if username in registered_users:
        del registered_users[username]
    updateusermenu()
def status_trigger():
    if os.path.exists(os.path.join(SETTING_DIR,"Certificates", "cert.pem")) and os.path.exists(os.path.join(SETTING_DIR,"Certificates", "key.pem")):
         if service is None or service.poll() is not None:
            start_service()
         else:
            close_service()
    else:
        messagebox.showwarning("Certificates Not Found", "Kindly provide ceritficates cert.pem and key.pem in /Settings/Certificates or enable automatic certificate generation and click register at least once.")
def chores():
    global registered_users
    if not os.path.exists(os.path.join(SETTING_DIR, "users_db.json")):
        with open(os.path.join(SETTING_DIR, "users_db.json"), "w") as file:
            json.dump({}, file, indent=4)
    registered_users = json.load(open(os.path.join(SETTING_DIR, "users_db.json"), "r"))
    get_ipv4()
    with open(os.path.join(SETTING_DIR, "settings.json"), "r") as file:
        settings = json.load(file)
    settings["ipv4"] = ipv4
    with open(os.path.join(SETTING_DIR, "settings.json"), "w") as file:
        json.dump(settings, file, indent=4)
    link.set(f"https://{ipv4}:8000")
    registered_users_list.clear()
    with open(os.path.join(SETTING_DIR, "users_db.json"), "r") as file:
        users_db = json.load(file)
    for user in users_db:
        registered_users_list.append(user)
    updateusermenu()
## Widgets
tk.messagebox.showinfo("Welcome to LanO'Lan!", "Lan to Lan text, voice and video chat system paired with file sharing. No internet bandwith needed. Made by Samy0_o (SamyIOoOI) on github with pleasure. Open-Source under MIT Licence, https://github.com/SamyIOoOI/LanO-Lan.")
tk.messagebox.showinfo("Server Status & Controls","Here you can configure, turn on, and close the LanO'Lan server as the admin and server hoster. The button below shows the current server status. Click it to turn the server on/off. Use the other buttons, widgets and dropdown menus to register, view, inspect or delete registered users.")
tk.messagebox.showwarning("Certificates & Ports", "Certificates are automatically configured when the server is turned on. Incase you want to override them and use your own, uncheck the 'Configure Certificates' checkbox. Port is set to 8000 by default, to edit it use settings.json located in /Settings. Automatic Port Recognition needs a one-time on startup very tiny bit of bandwith, for a truly zero bandwith experience, type your ipv4 address in its respective box. Warning: A wrong ip address will prevent the server from initiating.")
status_button = ttk.Button(gui, text="Server: OFF", command=lambda: status_trigger())
username_label = ttk.Label(gui, text="Username", font=('Comic Sans MS', 10, 'bold'))
password_label = ttk.Label(gui, text="Password", font=('Comic Sans MS', 10, 'bold'))
username_entry = ttk.Entry(gui, textvariable=user)
password_entry = ttk.Entry(gui, textvariable=password)
register_button = ttk.Button(gui, text="Register", command=lambda: register_all())
add_button = ttk.Button(gui, text="Add", command=lambda: add_user(user.get(), password.get()))
inspect_button = ttk.Button(gui, text="Inspect", command=lambda: inspect_user(selected_user.get()))
delete_button = ttk.Button(gui, text="Delete", command=lambda: delete_user(selected_user.get()))
selected_user_menu = ttk.OptionMenu(gui, selected_user, *registered_users_list)
max_time_entry = ttk.Entry(gui, textvariable=max_wait_time)
link_label =ttk.Entry(gui, state='readonly', textvariable=link, justify='center', font=('Comic Sans MS', 8, 'bold'))
certify_button = ttk.Checkbutton(gui, text="Certificates", variable=certify)
user_list_label = ttk.Label(gui, text="User List", font=('Comic Sans MS', 10, 'bold'))
max_time_label = ttk.Label(gui, text="MaxTime. MIN", font=('Comic Sans MS', 10, 'bold'))
ipv4_entry_widget = ttk.Entry(gui, textvariable=ipv4_entry)
## Widget Placement & Layout
link_label.grid(column=1, row=1, padx=5, pady=5, columnspan=2)
username_label.grid(column=1, row=2, padx=5, pady=5, columnspan=2)
password_label.grid(column=1, row=4, padx=5, pady=5, columnspan=2)
username_entry.grid(column=1, row=3, padx=5, pady=5, columnspan=2, sticky='ew')
password_entry.grid(column=1, row=5, padx=5, pady=5, columnspan=2, sticky='ew')
max_time_entry.grid(column=1, row=7, padx=5, pady=5, columnspan=2, sticky='ew')
max_time_label.grid(column=1, row=6, padx=5, pady=5, columnspan=2)
selected_user_menu.grid(column=1, row=9, padx=5, pady=5, columnspan=2, sticky='ew')
inspect_button.grid(column=0, row=10, padx=5, pady=5, sticky='ew')
add_button.grid(column=1, row=10, padx=5, pady=5, sticky='ew')
register_button.grid(column=2, row=10, padx=5, pady=5, sticky='ew')
delete_button.grid(column=3, row=10, padx=5, pady=5, sticky='ew')
certify_button.grid(column=1, row=11, padx=5, pady=5, columnspan=2, sticky='ew')
status_button.grid(column=1, row=0, pady=5, padx=5, columnspan=2 ,sticky='ew')
user_list_label.grid(column=1, row=8, padx=5, pady=5, columnspan=2)
ipv4_entry_widget.grid(column=1, row=12, padx=5, pady=5, columnspan=2, sticky='ew')
status_button.config(style='serveroff.TButton')
gui.columnconfigure(0, weight=1)
gui.columnconfigure(1, weight=1)
gui.columnconfigure(2, weight=1)
gui.columnconfigure(3, weight=1)
## Initial Functions
gui.after(2000, check_service)
gui.after(2000, chores)
gui.iconphoto(True, icon)
gui.mainloop()