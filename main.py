import tkinter as tk
from tkcalendar import DateEntry
from  datetime import date

root = tk.Tk(baseName="root")

root.geometry("400x150")
root.title("Descarregador de processos")
root.configure(background='#262626')

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=2)

lbX1 = tk.Label(root, text="Data inicial: ",
                background='#262626', foreground="white")
lbX1.grid(column=0, row=1, pady=10)
cal1 = DateEntry(root,selectmode='day')
cal1.grid(column=0, row=2, pady=5)
cal1.set_date(date.today())

lbY2 = tk.Label(root, text="Data final: ",
                background='#262626', foreground="white")
lbY2.grid(column=1, row=1, pady=10)
cal2 = DateEntry(root,selectmode='day')
cal2.grid(column=1, row=2, pady=5)
cal2.set_date(date.today())

init_btn = tk.Button(root, text="INICIAR DOWNLOAD DE PROCESSOS", command="init_inspector", width=40,
                     height=2, bg="#2E4159", activebackground="#8F8EBF", disabledforeground="yellow", fg="white")
init_btn.grid(columnspan=4, sticky=tk.W+tk.E, pady=15, padx=10)

root.mainloop()
