import time
import re
from tkinter import *
import tkinter as tk
from threading import Thread, Event
import functools
import pyperclip
from tkinter import ttk
import random
import pygame
import pygetwindow as gw
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button as MouseButton
import gc

# Khởi tạo các controller
keyboard = KeyboardController()
mouse = MouseController()

# Biến toàn cục
active_counter = 0
boss_active = False
selected_window_title = ""
last_hook_time = 0
last_random_value = None
stop_event = Event()  # Thêm Event để kiểm soát thread

# Khởi tạo pygame mixer
pygame.mixer.init()

def play_notification_sound(sound_file, volume):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()

def follow(thefile):
    thefile.seek(0, 2)
    while not stop_event.is_set():
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line.strip()  # Loại bỏ ký tự xuống dòng để giảm bộ nhớ

def with_cooldown(cooldown_time):
    def decorator(func):
        last_run_time = 0
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_run_time
            current_time = time.time()
            if current_time - last_run_time > cooldown_time:
                last_run_time = current_time
                return func(*args, **kwargs)
        return wrapper
    return decorator

@with_cooldown(5)
def handle_fishing_competition(click_interval):
    play_notification_sound(notification_sound.get(), notification_volume.get())
    activate_selected_window()
    if boss_active and click_interval > 10000:
        time.sleep(1)
        send_command("/fishing forfeit")
    else:
        time.sleep(0.2)
        keyboard.press(Key.end)
        keyboard.release(Key.end)
        time.sleep(60 * 31)
        keyboard.press(Key.end)
        keyboard.release(Key.end)

@with_cooldown(2)
def handle_hook_action():
    activate_selected_window()
    time.sleep(0.3)
    mouse.click(MouseButton.right)

@with_cooldown(5)
def handle_vote_party(sound_file, volume):
    play_notification_sound(sound_file, volume)
    activate_selected_window()
    time.sleep(0.2)

def start_stop():
    global active_counter
    if button['text'] == 'Start':
        active_counter = 0
        stop_event.clear()
        sta = Thread(target=run, daemon=True)
        sta.start()
        button.config(text="Stop")
    else:
        active_counter = 1
        stop_event.set()
        button.config(text="Start")

def auto_restart():
    while not stop_event.is_set():
        time.sleep(180)  # 3 phút
        if button['text'] == 'Stop':
            button.invoke()
        time.sleep(0.5)
        if button['text'] == 'Start':
            button.invoke()

def send_command(command):
    keyboard.press('t')
    keyboard.release('t')
    time.sleep(0.1)
    keyboard.type(command)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

def auto(pkm, delay):
    if not boss_active:
        lAnswer.configure(text=pkm.lower())
        pyperclip.copy(pkm.lower())
        activate_selected_window()
        delay = max(2.5, delay)  # Đảm bảo delay tối thiểu
        time.sleep(delay)
        send_command(pkm.lower())
        time.sleep(3)

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
    combobox_window['values'] = [w for w in windows if w.strip()]

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
    click_interval = float(tClick.get())

    # Đọc file log
    with open(r'C:\Users\duccj\AppData\Roaming\.technic\modpacks\ultimate-reallife-roleplay\logs\latest.log', 'r') as logfile:
        loglines = follow(logfile)

        for line in loglines:
            if stop_event.is_set():
                break

            # Xử lý các sự kiện
            if "Professor Oak" in line:
                next_lines = [next(loglines, "") for _ in range(3)]
                for following_line in next_lines:
                    if " dex number" in following_line:
                        pkm = extract_dex_number(following_line)
                        if pkm:
                            with open("Pokedex.txt", 'r') as f:
                                a = f.read().splitlines()
                            auto(a[pkm-1], len(a[pkm-1]) * dex + 1.2145)
                    elif "Unscramble the word" in following_line:
                        scrambled_word = following_line.split(":")[-1].strip()
                        with open("Pokedex.txt", 'r') as f:
                            for word in f:
                                word = word.strip()
                                if len(word) == len(scrambled_word) and sorted(word.lower()) == sorted(scrambled_word.lower()):
                                    delay = unr + (0.111 if len(word) <= 9 else 0.211)
                                    auto(word, len(word) * delay)
                                    break
                    elif "Pixelmon will begin in 10 seconds!" in following_line:
                        pass
                    else:
                        with open('h-tl.txt', 'r') as q:
                            quest = q.read().splitlines()
                        for idx in range(0, len(quest), 2):
                            cleaned_quest = re.sub(r'[^\w\s]', '', quest[idx].lower()).replace('n', '')
                            cleaned_line = re.sub(r'[^\w\s]', '', following_line.lower()).replace('n', '')
                            if cleaned_quest in cleaned_line:
                                answer = quest[idx + 1].lower()
                                delay = q5 if len(answer) < 6 else len(answer) * q6 + 0.456
                                auto(answer, delay)
                                break

            elif any(event in line for event in ["spawned nearby!", "votes remaining until the next Vote Party!", "World Boss has spawned!", "Yanoo", "yano", "yanoo"]) or re.search(r'\[Pixelmon\].*has spawned in a', line):
                handle_vote_party(notification_sound.get(), notification_volume.get())
            elif any(pokemon in line for pokemon in ["Azelf", "Manaphy", "Nihilego", "Latios", "Latias", "Suicune"]) and "You reeled in" in line:
                handle_vote_party(notification_sound.get(), notification_volume.get())
            elif "Fishing Competition Started" in line:
                handle_fishing_competition(click_interval)
                send_command("/fishing forfeit")
            elif "hook was instantly bit" in line:
                if fishing(random.randint(1, 4444)):
                    handle_hook_action()
            elif "You can only use custom fishing rods at the Fishing Warp!" in line:
                handle_fishing_competition(click_interval)

            # Giải phóng bộ nhớ định kỳ
            gc.collect()

def extract_dex_number(line):
    match = re.search(r'(\d+)\s*$', line)
    return int(match.group(1)) if match else None

def toggle_boss_mode():
    global boss_active
    from pynput.keyboard import Listener

    def on_press(key):
        global boss_active
        if hasattr(key, 'char') and key.char == '`':
            boss_active = not boss_active
            boss.set(boss_active)
            print(f"Boss Mode {'Activated' if boss_active else 'Deactivated'}")
            if boss_active:
                Thread(target=boss_press_r, daemon=True).start()

    listener = Listener(on_press=on_press)
    listener.start()

def boss_press_r():
    while boss_active and not stop_event.is_set():
        interval = float(tClick.get())
        activate_selected_window()
        keyboard.press('r')
        keyboard.release('r')
        time.sleep(interval)

def on_closing():
    global active_counter, boss_active
    active_counter = 1
    boss_active = False
    stop_event.set()
    window.destroy()

# GUI setup
window = Tk()
window.title("Yanoo's Program")
window.protocol("WM_DELETE_WINDOW", on_closing)

# Các widget GUI (giữ nguyên như code gốc)
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
tdex.grid(row=1, column=1)
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

button = Button(window, text='Start', command=start_stop)
button.grid(row=0, column=0, sticky=EW, columnspan=4)

boss = tk.IntVar()
c2 = tk.Checkbutton(window, text='Boss?', variable=boss, onvalue=1, offvalue=0)
c2.grid(column=1, row=6)

combobox_window = ttk.Combobox(window, state="readonly", width=47)
combobox_window.grid(column=0, row=9, columnspan=3)
combobox_window.bind('<<ComboboxSelected>>', select_window)

refresh_button = Button(window, text='Refresh Windows', command=refresh_window_list)
refresh_button.grid(column=3, row=9, sticky=EW)

# Khởi động thread boss mode
Thread(target=toggle_boss_mode, daemon=True).start()

window.mainloop()