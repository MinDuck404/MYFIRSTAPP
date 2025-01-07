import time
import re
from tkinter import *
import tkinter as tk
from threading import Thread
import functools
import pyperclip
import keyboard
from tkinter import ttk
import random
import pygame
import pygetwindow as gw

active_counter = 0
boss_active = False
selected_window_title = ""

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
        keyboard.press('t')
        keyboard.release('t')
        time.sleep(t)
        keyboard.press_and_release('ctrl+a')
        time.sleep(0.1)
        keyboard.press_and_release('ctrl+v')
        if t < 2.5:
            time.sleep(1)
            keyboard.press_and_release('enter')
        else:
            keyboard.press_and_release('enter')
        time.sleep(3)

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

def chayngaydi():
    chay = Thread(target=click)
    chay.start()

def click():
    global active_counter
    tam = active_counter
    time.sleep(4)
    mon = float(tClick.get())
    while not keyboard.is_pressed('`') and check.get() == 1:
        activate_selected_window()
        keyboard.press_and_release('left')
        time.sleep(mon)
    check.set(0)
    active_counter = tam
    if active_counter == 0:
        sta = Thread(target=run)
        sta.start()

def clickAFK():
    time.sleep(4)
    if vAFK.get() == 1:
        while not keyboard.is_pressed('`') and vAFK.get() == 1:
            a = random.randint(60, 300)
            activate_selected_window()
            keyboard.press_and_release('left')
            time.sleep(a)
        vAFK.set(0)

def afk():
    AFK = Thread(target=clickAFK)
    AFK.start()

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

    for line in loglines:
        if active_counter == 1:
            break

        if "Professor Oak" in line:
            next_lines = [next(loglines) for _ in range(3)]
            for following_line in next_lines:
                if " dex number" in following_line:
                    i = -3
                    m = 1
                    pkm = 0
                    while following_line[i] != ' ':
                        if following_line[i].isdigit():
                            pkm += int(following_line[i]) * m
                            i -= 1
                            m *= 10
                    auto(a[pkm-1], len(a[pkm-1]) * dex + 1.2145)
                    break
                elif "Unscramble the word" in following_line:
                    scrambled_word = following_line.split(":")[-1].strip()
                    print(f"Scrambled word detected: {scrambled_word}")
                    for word in a:
                        if len(word) == len(scrambled_word):
                            if sorted(word.lower()) == sorted(scrambled_word.lower()):
                                if len(word) < 5:
                                    auto(word, len(word) * unr)
                                elif len(word) <= 9:
                                    auto(word, len(word) * (unr + 0.111))
                                else:
                                    auto(word, len(word) * (unr + 0.211))
                                break
                else:
                    for idx, quest_item in enumerate(quest[::2]):
                        cleaned_quest_item = re.sub(r'[^\w\s]', '', quest_item.lower()).strip()
                        cleaned_following_line = re.sub(r'[^\w\s]', '', following_line.lower()).strip()

                        cleaned_quest_item = re.sub(r'n', '', cleaned_quest_item)
                        cleaned_following_line = re.sub(r'n', '', cleaned_following_line)

                        if cleaned_quest_item in cleaned_following_line:
                            answer = quest[idx * 2 + 1].lower()
                            time_delay = q5 if len(answer) < 6 else len(answer) * q6 + 0.456
                            auto(answer, time_delay)
                            break

        if "spawned nearby!" in line or re.search(r'\[Pixelmon\].*has spawned in a', line):
            play_notification_sound()

def toggle_boss_mode():
    global boss_active
    while True:
        if keyboard.is_pressed('`'):
            boss_active = not boss_active
            boss.set(boss_active)
            while keyboard.is_pressed('`'):
                time.sleep(0.1)
            if boss_active:
                boss_func = Thread(target=boss_press_r)
                boss_func.start()

def boss_press_r():
    while boss_active:
        interval = float(tClick.get())
        activate_selected_window()
        keyboard.press_and_release('r')
        time.sleep(interval)

def on_closing():
    global active_counter, boss_active
    active_counter = 1
    boss_active = False
    window.destroy()

window = Tk()
window.title("Yanoo's Program")
window.iconbitmap("yano.ico")

window.protocol("WM_DELETE_WINDOW", on_closing)

ldex = Label(window, text='Dex Number: ', font=('Arial', 15))
ldex.grid(column=0, row=1)
lUnscramble = Label(window, text='Unscramble: ', font=('Arial', 15))
lUnscramble.grid(column=0, row=2)
lQuest5 = Label(window, text='Quest < 5: ', font=('Arial', 15))
lQuest5.grid(column=0, row=3)
lQuest = Label(window, text='Quest > 5: ', font=('Arial', 15))
lQuest.grid(column=0, row=4)
lAnswer = Label(window, text='Answer', font=('Arial', 20))
lAnswer.grid(column=0, row=5)
lClick = Label(window, text='time: ', font=('Arial', 15))
lClick.grid(column=0, row=7)

tdex = Entry(window, width=20)
tdex.insert(END, 0.324)
tUnscramble = Entry(window, width=20)
tUnscramble.insert(END, 0.214)
tUnscramble.grid(column=1, row=2)

tQuest5 = Entry(window, width=20)
tQuest5.insert(END, 0.123)
tQuest5.grid(column=1, row=3)

tQuest = Entry(window, width=20)
tQuest.insert(END, 0.456)
tQuest.grid(column=1, row=4)

tClick = Entry(window, width=20)
tClick.insert(END, 2.5)
tClick.grid(column=1, row=7)

button = Button(window, text="Start", font=('Arial', 15), command=start_stop)
button.grid(column=0, row=6)

check = IntVar()
check_button = Checkbutton(window, text="Enable", variable=check, font=('Arial', 15), command=chayngaydi)
check_button.grid(column=1, row=6)

vAFK = IntVar()
afk_button = Checkbutton(window, text="AFK", variable=vAFK, font=('Arial', 15), command=afk)
afk_button.grid(column=2, row=6)

boss = BooleanVar()
boss_button = Checkbutton(window, text="Boss Mode", variable=boss, font=('Arial', 15))
boss_button.grid(column=2, row=7)

notification_sound = StringVar()
notification_sound.set("notification.mp3")
notification_label = Label(window, text="Notification Sound:", font=('Arial', 15))
notification_label.grid(column=0, row=8)
notification_entry = Entry(window, textvariable=notification_sound, width=20)
notification_entry.grid(column=1, row=8)

notification_volume = DoubleVar()
notification_volume.set(0.5)
volume_label = Label(window, text="Volume:", font=('Arial', 15))
volume_label.grid(column=0, row=9)
volume_slider = Scale(window, from_=0, to=1, resolution=0.1, orient=HORIZONTAL, variable=notification_volume)
volume_slider.grid(column=1, row=9)

combobox_window = ttk.Combobox(window, width=50)
combobox_window.grid(column=0, row=10, columnspan=2)
refresh_button = Button(window, text="Refresh Windows", command=refresh_window_list)
refresh_button.grid(column=2, row=10)
combobox_window.bind("<<ComboboxSelected>>", select_window)

refresh_window_list()
window.mainloop()

