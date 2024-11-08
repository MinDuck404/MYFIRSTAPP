import time
import pyautogui as pt
from tkinter import *
import tkinter as tk
from threading import Thread
import functools
import pyperclip
import keyboard
from tkinter import ttk
import random

active_counter=0

def follow(thefile):
  thefile.seek(0,2)
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
        sta = Thread(target = run)
        sta.start()
        button.config(text="Stop")
    else:
        active_counter = 1
        button.config(text="Start")

def do_not_run_twice(func):
    prev_call = None

    @functools.wraps(func) # It is good practice to use this decorator for decorators
    def wrapper(*args, **kwargs):
        nonlocal prev_call
        if (args, kwargs) == prev_call:
            return None
        prev_call = args, kwargs
        return func(*args, **kwargs)
    return wrapper

@do_not_run_twice    
def auto(pkm,t):
    lAnswer.configure(text=pkm.lower())
    pyperclip.copy(pkm)
    pt.press('t')
    time.sleep(t)
    with pt.hold('ctrl'):
      pt.press('a')
      pt.press('v')
    if t<2.5:
      time.sleep(1)
      pt.press('Enter')
    else:
      pt.press('Enter')
    time.sleep(3)

def chayngaydi():
    chay=Thread(target=click)
    chay.start()

def click():
    global active_counter
    tam=active_counter
    time.sleep(4)
    mon=float(tClick.get())
    if boss.get()==1:
        active_counter=1
    if check.get()==1:
        if cb1.get()=='Righ Click':
            while (not keyboard.is_pressed('`')) and check.get()==1:
                pt.rightClick(interval=mon)
        else:
            while (not keyboard.is_pressed('`')) and check.get()==1:
                pt.leftClick(interval=mon)
        check.set(0)
        active_counter=tam
    if active_counter ==0:
      sta = Thread(target = run)
      sta.start()

def clickAFK():
    time.sleep(4)
    if vAFK.get()==1:
        while (not keyboard.is_pressed('`')) and vAFK.get()==1:
            a=random.randint(60, 300)
            pt.leftClick(interval=a)
        vAFK.set(0)

def afk():
    AFK=Thread(target=clickAFK)
    AFK.start()


def run():
    dex=float(tdex.get())
    unr=float(tUnscramble.get())
    q5=float(tQuest5.get())
    q6=float(tQuest.get())
    f = open("Pokedex.txt",'r')
    a = f.read().splitlines()
    q=open('h-tl.txt','r')
    quest=q.read().splitlines()
    logfile = open(r'C:\Users\duccj\AppData\Roaming\.technic\modpacks\ultimate-reallife-roleplay\logs\latest.log', 'r')

    loglines = follow(logfile)
    for line in loglines:
      if active_counter==1:
        break
      if "Professor Oak" in line:
        print('ok')

        if " dex number" in line:
          i=-3
          m=1
          pkm=0
          while line[i] != ' ':
            if line[i] in {'0','1','2','3','4','5','6','7','8','9'}:
              pkm = pkm + int((line[i]))*m
              i-=1
              m=m*10
          auto((a[pkm-1]),len(a[pkm-1])*dex+1.2145)
          
        if "Unscramble the word" in line:
          i=-2
          pkm=''
          while line[i] != ' ':
            pkm = pkm + (line[i])
            i-=1
          for p in a:
            if len(pkm) == len(p):
              x=p.lower()
              cc= len( set(x) & set(pkm) )
              if cc == len(set(x)):
                l1=sorted(pkm)
                l2=sorted(x)
                if l1==l2:
                  if len(x)<5:
                    auto(x,len(x)*unr)
                  elif len(x)<=9:
                    auto(x,len(x)*(unr+0.111))
                  else:
                    auto(x,len(x)*(unr+0.211))

        # if 'Click the' in line:
        #     pt.press('t')
        #     pt.click(784,565)
        #     time.sleep(0.5)
        #     pt.press('Enter')

        else:
          d=0
          for i in quest:
            if d%2 == 0:
              if i !='':
                traloi=i.lower()
                cauhoi=line.lower()
                if traloi in cauhoi:
                  if (d+1)%2 !=0:
                    if len(quest[d+1])<6:
                      auto(quest[d+1].lower(),q5)
                    else:
                        auto(quest[d+1].lower(),len(quest[d+1])*q6+0.456)
            d+=1
      if 'It got away!' in line:
        time.sleep(0.3254)
        pt.rightClick()


window=Tk()
window.title("Yanoo's Program")
window.iconbitmap("yano.ico")

#label
ldex=Label(window,text='Dex Number: ',font=('Arial',15))
ldex.grid(column=0,row=1)
lUnscramble=Label(window,text='Unscramble: ',font=('Arial',15))
lUnscramble.grid(column=0,row=2)

lQuest5=Label(window,text='Quest < 5: ',font=('Arial',15))
lQuest5.grid(column=0,row=3)

lQuest=Label(window,text='Quest > 5: ',font=('Arial',15))
lQuest.grid(column=0,row=4)

lAnswer=Label(window,text='Answer',font=('Arial',20))
lAnswer.grid(column=0,row=5)

lClick=Label(window,text='time: ',font=('Arial',15))
lClick.grid(column=0,row=7)

#text box
tdex=Entry(window,width=20)
tdex.insert(END,0.324)
tdex.grid(row=1,column=1,ipady=1,ipadx=1)

tUnscramble=Entry(window,width=20)
tUnscramble.insert(END,0.244)
tUnscramble.grid(column=1,row=2)

tQuest5=Entry(window,width=20)
tQuest5.insert(END,1.657)
tQuest5.grid(column=1,row=3)

tQuest=Entry(window,width=20)
tQuest.insert(END,0.234)
tQuest.grid(column=1,row=4)

tClick=Entry(window,width=20)
tClick.insert(END,0.1)
tClick.grid(column=1,row=7)

#button
button=Button(window,text='Start',command=start_stop)
button.grid(row = 0, column = 0, sticky = EW,columnspan=4)

#check box
check = tk.IntVar()
boss=tk.IntVar()
vAFK=tk.IntVar()
c1 = tk.Checkbutton(window, text='AutoClick',variable=check, onvalue=1, offvalue=0, command=chayngaydi)
c1.grid(column=0,row=6)

c2=tk.Checkbutton(window, text='Boss?',variable=boss, onvalue=1, offvalue=0)
c2.grid(column=1,row=6)

Cafk=Checkbutton(window,text='AFK Mode',variable=vAFK, onvalue=1, offvalue=0,command=afk)
Cafk.grid(column=0,row=8, sticky = EW,columnspan=4)


#combo box
idk = tk.StringVar()
cb1=ttk.Combobox(window,width=10,textvariable = idk)
cb1['values'] = ('Righ Click','Left Click')
cb1.grid(column=3,row =6)
cb1.current(0)

window.mainloop()
