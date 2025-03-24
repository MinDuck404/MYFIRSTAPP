import time
import random
import re  # Thêm import re để sử dụng re.search
from tkinter import *
import tkinter as tk
from tkinter import ttk
from threading import Thread
from pynput.keyboard import Key, Controller
from pynput.mouse import Button as MouseButton, Controller as MouseController
import pygetwindow as gw
import pygame

keyboard = Controller()
mouse = MouseController()

active_counter = 0
selected_window_title = ""
last_hook_time = 0
last_random_value = None

# Initialize pygame mixer for playing sounds
pygame.mixer.init()

# Function to play notification sound
def play_notification_sound():
    pygame.mixer.music.load(notification_sound.get())
    pygame.mixer.music.set_volume(notification_volume.get())
    pygame.mixer.music.play()

def follow(thefile):
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def with_cooldown(cooldown_time):
    def decorator(func):
        last_run_time = 0
        def wrapper(*args, **kwargs):
            nonlocal last_run_time
            current_time = time.time()
            if current_time - last_run_time > cooldown_time:
                last_run_time = current_time
                return func(*args, **kwargs)
        return wrapper
    return decorator

@with_cooldown(5)
def handle_fishing_competition():
    play_notification_sound()
    activate_selected_window()
    time.sleep(0.2)

@with_cooldown(2)
def handle_hook_action():
    activate_selected_window()
    time.sleep(0.3)
    mouse.click(MouseButton.right)

@with_cooldown(5)
def handle_vote_party():
    play_notification_sound()
    activate_selected_window()
    time.sleep(0.2)

def start_stop():
    global active_counter
    if button['text'] == 'Start':
        active_counter = 0
        sta = Thread(target=run)
        sta.start()
        button.config(text="Stop")
    else:
        active_counter = 1
        button.config(text="Start")

def fishing(random_variable):
    global last_hook_time, last_random_value
    current_time = time.time()
    if (current_time - last_hook_time > 5) or (random_variable != last_random_value):
        last_hook_time = current_time
        last_random_value = random_variable
        return True
    return False

def activate_selected_window():
    if selected_window_title:
        try:
            window = gw.getWindowsWithTitle(selected_window_title)[0]
            window.activate()
        except IndexError:
            print("Selected window not found")

def refresh_window_list():
    windows = gw.getAllTitles()
    combobox_window['values'] = [window for window in windows if window.strip()]

def select_window(event):
    global selected_window_title
    selected_window_title = combobox_window.get()
    print(f"Selected window: {selected_window_title}")

def run():
    logfile = open(r'C:\Users\duccj\AppData\Roaming\.technic\modpacks\ultimate-reallife-roleplay\logs\latest.log', 'r')
    loglines = follow(logfile)

    for line in loglines:
        if active_counter == 1:
            break
        
        if "spawned nearby!" in line or re.search(r'\[Pixelmon\].*has spawned in a', line) or "votes remaining until the next Vote Party!" in line or "World Boss has spawned!" in line:
            handle_vote_party()
        elif any(pokemon in line for pokemon in ["Azelf", "Manaphy", "Nihilego", "Latios", "Latias", "Suicune"]) and "You reeled in" in line:
            handle_vote_party()
        elif "Fishing Competition Started" in line:
            time.sleep(1)
            keyboard.press('t')
            keyboard.release('t')
            time.sleep(0.5)
            keyboard.type("/fishing forfeit")
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            handle_fishing_competition()
        elif "hook was instantly bit" in line:
            random_variable = random.randint(1, 4444)
            if fishing(random_variable):
                handle_hook_action()
        elif "You can only use custom fishing rods at the Fishing Warp!" in line:  
            time.sleep(0.2)
            keyboard.press(Key.end)
            keyboard.release(Key.end)
            time.sleep(0.2)
            handle_fishing_competition()

def on_closing():
    global active_counter
    active_counter = 1
    window.destroy()

# GUI setup
window = Tk()
window.title("Yanoo's Program")
window.iconbitmap("yano.ico")
window.protocol("WM_DELETE_WINDOW", on_closing)

# Labels and Entries
lNotification = Label(window, text='Notification Sound: ', font=('Arial', 15))
lNotification.grid(column=0, row=0)
notification_sound = Entry(window, width=20)
notification_sound.insert(END, "notification.mp3")
notification_sound.grid(column=1, row=0)
notification_volume = Scale(window, from_=0, to=1, resolution=0.1, orient=HORIZONTAL, label="Volume")
notification_volume.set(0.5)
notification_volume.grid(column=2, row=0, sticky=EW, columnspan=2)

# Buttons
button = Button(window, text='Start', command=start_stop)
button.grid(row=1, column=0, sticky=EW, columnspan=4)

# Combobox for window titles
combobox_window = ttk.Combobox(window, state="readonly", width=47)
combobox_window.grid(column=0, row=2, columnspan=3)
combobox_window.bind('<<ComboboxSelected>>', select_window)

# Refresh button
refresh_button = Button(window, text='Refresh Windows', command=refresh_window_list)
refresh_button.grid(column=3, row=2, sticky=EW)

window.mainloop()