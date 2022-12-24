import requests
import fitz
import os
from time import sleep
from utils import getCaptchaToken
from datetime import timedelta, datetime

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


def savePdfs(initialDate, finalDate):
    dif = finalDate - initialDate

    lista_datas = []
    for i in range(dif.days + 1):
        day = initialDate + timedelta(days=i)
        lista_datas.append(day)

    lista_datas = [datetime.strftime(dt, format="%Y-%m-%d")
                   for dt in lista_datas]

    print(lista_datas)
    orgaos = requests.get(urlOrgaos, headers=headers)
    orgaos = orgaos.json()

    for data in lista_datas:
        for orgao in orgaos:
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

                            captchaToken = getCaptchaToken(idProcesso)

                            file = requests.get(
                                'https://pje.trt2.jus.br/pje-consulta-api/api/processos/' + str(idProcesso) + '/documentos/283356716?tokenCaptcha=' + captchaToken, allow_redirects=True, headers=headers)

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
                                os.remove(item["numeroProcesso"] + '.pdf')
