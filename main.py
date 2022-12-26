import tkinter as tk
from tkcalendar import DateEntry
from datetime import date, datetime
import requests
import fitz
import os
from time import sleep
from utils import getCaptchaToken
from datetime import timedelta, datetime
import threading

root = tk.Tk(baseName="root")

root.geometry("400x350")
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
         "Una", "Una (rito sumaríssimo)"]


stop_thread = False


def savePdfs(initialDate, finalDate):

    global stop_thread

    stop_thread = False

    try:
        dif = finalDate - initialDate

        lista_datas = []
        for i in range(dif.days + 1):
            day = initialDate + timedelta(days=i)
            lista_datas.append(day)

        lista_datas = [datetime.strftime(dt, format="%Y-%m-%d")
                       for dt in lista_datas]

        log(str(lista_datas))
        orgaos = requests.get(urlOrgaos, headers=headers)
        orgaos = orgaos.json()

        for data in lista_datas:
            log("DATA: " + data)

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
                            if item["tipo"] in tipos:
                                idProcesso = item["idProcesso"]
                                log("Lendo processo id: " + str(idProcesso))

                                log("Obtendo código captcha...")
                                captchaToken = getCaptchaToken(idProcesso)
                                log("Código obtido.")

                                processo = requests.get(
                                    'https://pje.trt2.jus.br/pje-consulta-api/api/processos/' + str(idProcesso) + '?tokenCaptcha=' + captchaToken, allow_redirects=True, headers=headers)

                                processo = processo.json()

                                filesProcesso = processo["itensProcesso"]

                                idDocument = ''

                                for f in filesProcesso:
                                    if f["titulo"] == "Ata da Audiência":
                                        idDocument = f["id"]

                                if idDocument != '' and idDocument:
                                    file = requests.get(
                                        'https://pje.trt2.jus.br/pje-consulta-api/api/processos/' + str(idProcesso) + '/documentos/' + str(idDocument) + '?tokenCaptcha=' + captchaToken, allow_redirects=True, headers=headers)

                                    download = open(
                                        item["numeroProcesso"] + '.pdf', 'wb')
                                    download.write(file.content)
                                    download.close()

                                    keyWords = 0

                                    with fitz.open(item["numeroProcesso"] + '.pdf') as pdf:
                                        for pagina in pdf:
                                            if 'perícia' in pagina.get_text():
                                                keyWords += 1
                                                break

                                    if keyWords < 2:
                                        os.remove(
                                            item["numeroProcesso"] + '.pdf')
                                        log(
                                            "Documento não corresponde as exigências")

                                    log(
                                        "Documento " + item["numeroProcesso"] + ".pdf salvo!")

                    else:
                        log("Não há processos")

        stop_thread = True

    except Exception as e:
        log("Erro na execução: " + str(e))
        stop_thread = False


def stop_thread_fn():
    global stop_thread
    stop_thread = True


def init():
    log("Iniciando programa...")
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
    log("Encerando")

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
