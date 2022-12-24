import tkinter as tk
from tkcalendar import DateEntry
from datetime import date, datetime
from process import savePdfs

root = tk.Tk(baseName="root")

root.geometry("400x150")
root.title("Descarregador de processos")
root.configure(background='#262626')

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=2)

sel1 = tk.StringVar()
sel2 = tk.StringVar()

lbX1 = tk.Label(root, text="Data inicial: ",
                background='#262626', foreground="white")
lbX1.grid(column=0, row=1, pady=10)
cal1 = DateEntry(root, selectmode='day', textvariable=sel1)
cal1.grid(column=0, row=2, pady=5)
cal1.set_date(date.today())

lbY2 = tk.Label(root, text="Data final: ",
                background='#262626', foreground="white")
lbY2.grid(column=1, row=1, pady=10)
cal2 = DateEntry(root, selectmode='day', textvariable=sel2)
cal2.grid(column=1, row=2, pady=5)
cal2.set_date(date.today())

def init():
    initialDate = sel1.get()
    finalDate = sel2.get()

    initialDay, initialMonth, finalYear = initialDate.split('/')
    initialDate = datetime(int(finalYear), int(initialMonth), int(initialDay))

    finalDay, finalMonth, finalYear = finalDate.split('/')
    finalDate = datetime(int(finalYear), int(finalMonth), int(finalDay))

    print(initialDate, finalDate)
    savePdfs(initialDate, finalDate)

init_btn = tk.Button(root, text="INICIAR DOWNLOAD DE PROCESSOS", command=init, width=40,
                     height=2, bg="#2E4159", activebackground="#8F8EBF", disabledforeground="yellow", fg="white")
init_btn.grid(columnspan=4, sticky=tk.W+tk.E, pady=15, padx=10)

root.mainloop()
