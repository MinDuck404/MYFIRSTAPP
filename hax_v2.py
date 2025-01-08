import time
import re
from tkinter import *
import tkinter as tk
from threading import Thread
import functools
import pyperclip
# import keyboard
from tkinter import ttk
import random
import pygame
import pygetwindow as gw
from pynput.keyboard import Key, Controller, Listener
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton

keyboard = Controller()
mouse = MouseController() 
# import torch
# import json
# from torchvision import transforms
# from PIL import Image
# import numpy as np
# import torch.nn as nn
# from torchvision import models

active_counter = 0
boss_active = False
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

def auto_restart():
    while True:
        time.sleep(180)  # 3 phút
        if button['text'] == 'Stop':
            button.invoke()  
        time.sleep(0.5)  
        if button['text'] == 'Start':
            button.invoke()  

def do_not_run_twice(func):
    prev_call = None

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal prev_call
        if (args, kwargs) == prev_call:
            return None
        prev_call = args, kwargs
        return func(*args, **kwargs)
    return wrapper

@do_not_run_twice
def auto(pkm, t):
    if not boss_active:
        lAnswer.configure(text=pkm.lower())
        pyperclip.copy(pkm.lower())
        activate_selected_window()
        if t < 2.5:
            t+=1
        time.sleep(t)
        keyboard.press('t')
        keyboard.release('t')
        keyboard.press(Key.ctrl)
        keyboard.press('a')
        keyboard.release('a')
        keyboard.release(Key.ctrl)
        time.sleep(0.1)
        keyboard.press(Key.ctrl)
        keyboard.press('v')
        keyboard.release('v')
        keyboard.release(Key.ctrl)
        time.sleep(0.1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(3)

def fishing(random_variable):
    global last_hook_time, last_random_value
    current_time = time.time()
    
    # If it's been more than 5 seconds since last hook or it's a new random value
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
    global boss_active
    dex = float(tdex.get())
    unr = float(tUnscramble.get())
    q5 = float(tQuest5.get())
    q6 = float(tQuest.get())
    with open("Pokedex.txt", 'r') as f:
        a = f.read().splitlines()
    with open('h-tl.txt', 'r') as q:
        quest = q.read().splitlines()
    
    logfile = open(r'C:\Users\duccj\AppData\Roaming\.technic\modpacks\ultimate-reallife-roleplay\logs\latest.log', 'r')
    loglines = follow(logfile)

    boss_thread = Thread(target=toggle_boss_mode)
    boss_thread.start()
    auto_restart_thread = Thread(target=auto_restart, daemon=True)
    auto_restart_thread.start()

    for line in loglines:
        if active_counter == 1:
            break
        
        # if "Professor Oak" in line:
        #     next_lines = [next(loglines) for _ in range(3)]
        #     for following_line in next_lines:
        #         if " dex number" in following_line:
        #             # Lấy dex number
        #             i = -3
        #             m = 1
        #             pkm = 0
        #             while following_line[i] != ' ':
        #                 if following_line[i].isdigit():
        #                     pkm += int(following_line[i]) * m
        #                     i -= 1
        #                     m *= 10
        #             auto(a[pkm-1], len(a[pkm-1]) * dex + 1.2145)
                
        #         elif "Unscramble the word" in following_line:
        #             # Xử lý giải mã từ
        #             scrambled_word = following_line.split(":")[-1].strip()
        #             print(f"Scrambled word detected: {scrambled_word}")
        #             for word in a:
        #                 if len(word) == len(scrambled_word):
        #                     if sorted(word.lower()) == sorted(scrambled_word.lower()):
        #                         if len(word)<5:
        #                             auto(word,len(word)*unr)
        #                         elif len(word)<=9:
        #                             auto(word,len(word)*(unr+0.111))
        #                         else:
        #                             auto(word,len(word)*(unr+0.211))
                                
        #         elif "Pixelmon will begin in 10 seconds!" in following_line:
        #             pass
                
        #         else:        
        #                 # Xử lý câu hỏi trong quest
        #                 for idx, quest_item in enumerate(quest[::2]):
        #                     # Loại bỏ các ký tự không phải chữ cái, số và khoảng trắng (bao gồm cả dấu câu, dấu hỏi, etc.)
        #                     cleaned_quest_item = re.sub(r'[^\w\s]', '', quest_item.lower()).strip() # Loại bỏ ký tự không phải chữ cái, số
        #                     cleaned_following_line = re.sub(r'[^\w\s]', '', following_line.lower()).strip() # Xử lý `following_line` sau khi đã làm sạch
                        
        #                     # Loại bỏ tất cả các chữ 'n' (viết hoa hoặc viết thường) trong cả cleaned_quest_item và cleaned_following_line
        #                     cleaned_quest_item = re.sub(r'n', '', cleaned_quest_item)  
        #                     cleaned_following_line = re.sub(r'n', '', cleaned_following_line)  # Loại bỏ 'n' trong cleaned_following_line


        #                     if cleaned_quest_item in cleaned_following_line:
        #                         answer = quest[idx * 2 + 1].lower()
        #                         time_delay = q5 if len(answer) < 6 else len(answer) * q6 + 0.456
        #                         auto(answer, time_delay)
                                
        # # Detect spawn messages and play notification sound
        # Azelf Manaphu Nihilego Latios Latias Suicune
        if "spawned nearby!" in line or re.search(r'\[Pixelmon\].*has spawned in a', line) or "Fishing Competition Started" in line or "votes remaining until the next Vote Party!" in line or "World Boss has spawned!" in line or any(pokemon in line for pokemon in ["Azelf", "Manaphy", "Nihilego", "Latios", "Latias", "Suicune"]) and "You reeled in" in line or "Yano" in line or "Yanoo" in line or "yano" in line or "yanoo" in line:
            play_notification_sound()
        if "hook was instantly bit" in line:
            random_variable = random.randint(1, 4444)
            fishing(random_variable)
            if fishing:
                activate_selected_window()
                time.sleep(0.6)
                mouse.click(MouseButton.right)
                time.sleep(1)
                keyboard.press('2')
                keyboard.release('2')
                time.sleep(0.5)
                keyboard.press('1')
                keyboard.release('1')
            
        if "You can only use custom fishing rods at the Fishing Warp!" in line:
            # random_variable = random.randint(1, 4444)
            # fishing(random_variable)
            # if fishing:
                activate_selected_window()
                time.sleep(0.2)
                keyboard.press(Key.end)
                keyboard.release(Key.end)

        # if "reeled in" in line:
        #     keyboard.type('/eb')
        #     keyboard.press(Key.enter)


def toggle_boss_mode():
    global boss_active

    def on_press(key):
        global boss_active
        try:
            # Kiểm tra nếu phím ` được nhấn
            if hasattr(key, 'char') and key.char == '`':  # Nhận diện phím bằng ký tự
                boss_active = not boss_active
                boss.set(boss_active)
                print(f"Boss Mode {'Activated' if boss_active else 'Deactivated'}")
                if boss_active:
                    boss_func = Thread(target=boss_press_r, daemon=True)
                    boss_func.start()
        except AttributeError:
            pass  # Bỏ qua nếu key không có thuộc tính `char`

    # Lắng nghe phím trong luồng riêng
    listener = Listener(on_press=on_press)
    listener.start()

def boss_press_r():
    while boss_active:
        interval = float(tClick.get())
        activate_selected_window()
        keyboard.press('r')
        keyboard.release('r')
        time.sleep(interval)

def on_closing():
    global active_counter, boss_active
    active_counter = 1
    boss_active = False
    window.destroy()

window = Tk()
window.title("Yanoo's Program")
window.iconbitmap("yano.ico")

# Bind the on_closing function to the window close event
window.protocol("WM_DELETE_WINDOW", on_closing)

# Labels
ldex = Label(window, text='Dex Number: ', font=('Arial', 15))
ldex.grid(column=0, row=1)
lUnscramble = Label(window, text='Unscramble: ', font=('Arial', 15))
lUnscramble.grid(column=0, row=2)
lQuest5 = Label(window, text='Quest < 5: ', font=('Arial', 15))
lQuest5.grid(column=0, row=3)
lQuest = Label(window, text='Quest > 5: ', font=('Arial', 15))
lQuest.grid(column=0, row=4)
lAnswer = Label(window, text='Answer', font=('Arial', 20))
lAnswer = Label(window, text='Answer', font=('Arial', 20))
lAnswer.grid(column=0, row=5)
lClick = Label(window, text='time: ', font=('Arial', 15))
lClick.grid(column=0, row=7)

# Text boxes
tdex = Entry(window, width=20)
tdex.insert(END, 0.324)
tdex.grid(row=1, column=1, ipady=1, ipadx=1)
tUnscramble = Entry(window, width=20)
tUnscramble.insert(END, 0.244)
tUnscramble.grid(column=1, row=2)
tQuest5 = Entry(window, width=20)
tQuest5.insert(END, 1.657)
tQuest5.grid(column=1, row=3)
tQuest = Entry(window, width=20)
tQuest.insert(END, 0.234)
tQuest.grid(column=1, row=4)
tClick = Entry(window, width=20)
tClick.insert(END, 0.1)
tClick.grid(column=1, row=7)
notification_sound = Entry(window, width=20)
notification_sound.insert(END, "notification.mp3")
notification_sound.grid(column=1, row=8)
notification_volume = Scale(window, from_=0, to=1, resolution=0.1, orient=HORIZONTAL, label="Volume")
notification_volume.set(0.5)
notification_volume.grid(column=2, row=8, sticky=EW, columnspan=4)

# Buttons
button = Button(window, text='Start', command=start_stop)
button.grid(row=0, column=0, sticky=EW, columnspan=4)

# Checkboxes
check = tk.IntVar()
boss = tk.IntVar()
vAFK = tk.IntVar()

c2 = tk.Checkbutton(window, text='Boss?', variable=boss, onvalue=1, offvalue=0)
c2.grid(column=1, row=6)


# Combobox for window titles
combobox_window = ttk.Combobox(window, state="readonly", width=47)
combobox_window.grid(column=0, row=9, columnspan=3)
combobox_window.bind('<<ComboboxSelected>>', select_window)

# Refresh button to update window list
refresh_button = Button(window, text='Refresh Windows', command=refresh_window_list)
refresh_button.grid(column=3, row=9, sticky=EW)

window.mainloop()
