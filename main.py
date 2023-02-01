import tkinter as tk
from tkcalendar import DateEntry
from datetime import date, datetime
import requests
import fitz
import os
from utils import getCaptchaToken, getFoundsSolver
from datetime import timedelta, datetime
import threading
import time
import re
import csv
import babel.numbers

epoch = 1545925769.9618232

init_time = 0

root = tk.Tk(baseName="root")

root.geometry("400x350")
root.title("Robo Consulta TRT2")
root.configure(background='#262626')

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=2)

sel1 = tk.StringVar()
sel2 = tk.StringVar()

lbX1 = tk.Label(root, text="Data inicial: ",
                background='#262626', foreground="white")
lbX1.grid(column=0, row=1, pady=10)
cal1 = DateEntry(root, selectmode='day', textvariable=sel1, locale='pt_BR')
cal1.grid(column=0, row=2, pady=5)
cal1.set_date(date.today())

lbY2 = tk.Label(root, text="Data final: ",
                background='#262626', foreground="white")
lbY2.grid(column=1, row=1, pady=10)
cal2 = DateEntry(root, selectmode='day', textvariable=sel2, locale='pt_BR')
cal2.grid(column=1, row=2, pady=5)
cal2.set_date(date.today())


class clipboardThread(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.args = args

        return

    def run(self):
        print("Iniciando monitoramento")
        initialDate, finalDate = self.args
        savePdfs(initialDate, finalDate)


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "pt-BR,pt;q=0.9",
    "content-type": "application/json",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "x-grau-instancia": "1",
    "Referer": "https://pje.trt2.jus.br/consultaprocessual/pautas",
    "Referrer-Policy": "no-referrer-when-downgrade",
}

urlOrgaos = "https://pje.trt2.jus.br/pje-consulta-api/api/orgaosjulgadores?somenteOJCs=true"

tipos = ["Inicial (rito sumaríssimo)", "Inicial por videoconferência",
         "Una", "Una (rito sumaríssimo)", "Una por videoconferência", "Una por videoconferência (rito sumaríssimo)"]


stop_thread = False


def savePdfs(initialDate, finalDate):

    global stop_thread

    stop_thread = False

    try:
        f = open('emails_processos.csv', 'w', newline='', encoding='utf-8')
        w = csv.writer(f)
        w.writerow(["Data de consulta do processo", "Número do processo", "1° email", "2° email", "3° email", "4° email", "5° email"])

        balance = getFoundsSolver()
        log("Os fundos do 2captcha são: $" + str(balance))

        dif = finalDate - initialDate

        lista_datas = []
        for i in range(dif.days + 1):
            day = initialDate + timedelta(days=i)
            lista_datas.append(day)

        lista_datas = [datetime.strftime(dt, format="%Y-%m-%d")
                       for dt in lista_datas]

        orgaos = requests.get(urlOrgaos, headers=headers)
        orgaos = orgaos.json()

        for data in lista_datas:

            splitedDate = data.split("-")
            datetimeDate = datetime(int(splitedDate[0]), int(splitedDate[1]), int(splitedDate[2]))
            formatedDate = datetimeDate.strftime("%d/%m/%Y")

            if stop_thread:
                break

            log("DATA: " + formatedDate)

            for orgao in orgaos:

                if stop_thread:
                    break

                log("ORGÃO: " + str(orgao.get("descricao")))
                if orgao.get("id"):
                    id = orgao["id"]

                    url = "https://pje.trt2.jus.br/pje-consulta-api/api/audiencias?pagina=1&tamanhoPagina=100&idOj=" + \
                        str(id) + "&data=" + data
                    req = requests.get(url, headers=headers)
                    req = req.json()

                    if req.get("resultado"):
                        for item in req["resultado"]:
                            if stop_thread:
                                break
                            if item["tipo"] in tipos:
                                idProcesso = item["idProcesso"]
                                log("Lendo processo id: " + str(idProcesso))

                                log("Obtendo código captcha...")
                                captchaToken = getCaptchaToken(idProcesso)

                                while not captchaToken:
                                    log("Erro no captcha")
                                    log("Tentando novo código...")
                                    captchaToken = getCaptchaToken(idProcesso)
                                    time.sleep(1)

                                log("Código obtido.")

                                processo = requests.get(
                                    'https://pje.trt2.jus.br/pje-consulta-api/api/processos/' + str(idProcesso) + '?tokenCaptcha=' + captchaToken, allow_redirects=True, headers=headers)

                                processo = processo.json()

                                filesProcesso = []

                                if processo.get("itensProcesso"):
                                    filesProcesso = processo.get(
                                        "itensProcesso")

                                idDocument = ''

                                for f in filesProcesso:
                                    if f["titulo"] == "Ata da Audiência" and f.get("documento") == True and f.get("tipoConteudo") == "PDF":
                                        idDocument = f["id"]

                                if idDocument != '' and idDocument:
                                    file = requests.get(
                                        'https://pje.trt2.jus.br/pje-consulta-api/api/processos/' + str(idProcesso) + '/documentos/' + str(idDocument) + '?tokenCaptcha=' + captchaToken, allow_redirects=True, headers=headers)

                                    download = open(
                                        item["numeroProcesso"] + '.pdf', 'wb')
                                    download.write(file.content)
                                    download.close()

                                    keyWords = 0
                                    emails = []

                                    with fitz.open(item["numeroProcesso"] + '.pdf') as pdf:
                                        for pagina in pdf:
                                            textPage = pagina.get_text()
                                            keyWords += textPage.count('perícia')

                                            if '@' in textPage:
                                                match = re.search(r'[\w\.-]+@[a-z0-9\.-]+', textPage)
                                                emails.append(match.group())
                                                print(emails)
                                            else:
                                                print("Não há emails")
                                        

                                    print("Numero palavras", keyWords)
                                    if keyWords < 2:
                                        os.remove(
                                            item["numeroProcesso"] + '.pdf')
                                        log(
                                            "Documento não corresponde às exigências")
                                    else:
                                        log(
                                            "Emails processo " + item["numeroProcesso"] + " salvos no arquivo .csv")

                                        
                                        newrow = [formatedDate, item["numeroProcesso"]]
                                        for i in emails: newrow.append(i)

                                        w.writerow(newrow)
                                        
                                        os.remove(
                                            item["numeroProcesso"] + '.pdf')

                    else:
                        log("Não há processos")


        end_time = time.time()
        log("Tempo de execução: " + str(end_time - init_time) + "s")
        stop_thread = True

    except Exception as e:
        log("Erro na execução: " + str(e))
        print(e)
        stop_thread = False
        init_btn["text"] = "INICIAR DOWNLOAD DE PROCESSOS"
        init_btn["state"] = "normal"


def stop_thread_fn():
    global stop_thread

    stop_thread = True


def init():
    global init_time
    log("Iniciando programa...")

    init_time = time.time()
    initialDate = sel1.get()
    finalDate = sel2.get()

    initialDay, initialMonth, finalYear = initialDate.split('/')
    initialDate = datetime(int(finalYear), int(initialMonth), int(initialDay))

    finalDay, finalMonth, finalYear = finalDate.split('/')
    finalDate = datetime(int(finalYear), int(finalMonth), int(finalDay))

    clipboardThread.daemon = True
    thread = clipboardThread(args=(initialDate, finalDate))
    thread.start()

    init_btn["text"] = "EXECUTANDO..."
    init_btn["state"] = "disabled"


def stop_inspect():
    log("Encerando...")

    stop_thread_fn()

    init_btn["text"] = "INICIAR DOWNLOAD DE PROCESSOS"
    init_btn["state"] = "normal"


def log(text):
    log_box.configure(state='normal')
    log_box.insert(tk.END, text + '\n')
    log_box.configure(state='disabled')
    # Autoscroll to the bottom
    log_box.yview(tk.END)


init_btn = tk.Button(root, text="INICIAR DOWNLOAD DE PROCESSOS", command=init, width=40,
                     height=2, bg="#2E4159", activebackground="#8F8EBF", disabledforeground="yellow", fg="white")
init_btn.grid(columnspan=4, sticky=tk.W+tk.E, pady=15, padx=10)

stop_btn = tk.Button(root, text="PARAR", command=stop_inspect, width=40,
                     height=2, bg="#6C0E23", activebackground="#ED6A5A", fg="white")
stop_btn.grid(columnspan=4, sticky=tk.W+tk.E, pady=15, padx=10)

log_box = tk.Text(root, height=5, state="disabled")
log_box.grid(columnspan=4, pady=15, padx=10)

root.mainloop()
