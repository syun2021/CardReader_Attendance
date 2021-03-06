from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from smartcard.System import readers as get_readers

from time import sleep
from tkinter import messagebox as mbox
import datetime
import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
import json
import os

template = {"names":[],"rank":[],"time":[]}
members=["ゲスト","ゲスト2","ゲスト3"]
ranks=["B3","B4","M1","M2","D"]

if not os.path.exists("IDs.json"):
    temp = {"names":[],"ids":[],"rank":[]}
    with open("IDs.json", "w") as f:
        json.dump(temp, f)

if not os.path.exists("./ATTEND"):
    os.makedirs("./ATTEND")

def entry(c1,c2,root):
    flag = mbox.askyesno("確認","登録しますか？")
    if flag:
        global name
        global rank
        name=c1.get()
        rank=c2.get()
        root.destroy()

def open_widget():
    root =tk.Tk()
    root.title("初回登録をしてください")
    root.geometry("400x300")
    v = tk.StringVar()
    cb = ttk.Combobox(root,values=members,textvariable=v)
    cb.pack()
    v2=tk.StringVar()
    cb2 = ttk.Combobox(root,values=ranks,textvariable=v2)
    cb2.pack()

    btn = tk.Button(root,text="入力",command=lambda:entry(cb,cb2,root))
    btn.pack()

    root.mainloop()

def Save_account(id):
    with open("IDs.json") as f:
        Names_and_Ids = json.load(f)

    try:
        if not id in Names_and_Ids["ids"]:
            open_widget()
            Names_and_Ids["ids"].append(id)
            Names_and_Ids["names"].append(name)
            Names_and_Ids["rank"].append(rank)
            with open("IDs.json", "w") as f:
                json.dump(Names_and_Ids, f)
            return name,rank

        index = Names_and_Ids["ids"].index(id)
        return Names_and_Ids["names"][index],Names_and_Ids["rank"][index]
    except NameError:
        pass

class PrintObserver(CardObserver):
    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("+Inserted: ", toHexString(card.atr))
            readers = get_readers()
            conn = readers[0].createConnection()
            conn.connect()
            send_data = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            recv_data, sw1, sw2 = conn.transmit(send_data)
            id = toHexString(recv_data)
            print("ID:",id)
            
            name,rank = Save_account(id)

            try:
                df = pd.read_csv(f"./ATTEND/{datetime.date.today()}.csv")
                if not (df["names"]==name).any():
                    df["names"].append(name)
                    df["rank"].append(rank)
                    df["time"].append(datetime.datetime.now().strftime("%H:%M"))
                    df.to_csv(f"./ATTEND/{datetime.date.today()}.csv")
            except:
                template["names"].append(name)
                template["rank"].append(rank)
                template["time"].append(datetime.datetime.now().strftime("%H:%M"))
                df = pd.DataFrame.from_dict(template)
                df.to_csv(f"./ATTEND/{datetime.date.today()}.csv")


        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))

if __name__ == '__main__':
    print("Please put smartcard on reader.")
    try:
            cardmonitor = CardMonitor()
            cardobserver = PrintObserver()
            cardmonitor.addObserver(cardobserver)
            while True:
                sleep(10)

    except KeyboardInterrupt:
        cardmonitor.deleteObserver(cardobserver)
