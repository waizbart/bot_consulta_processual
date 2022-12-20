import requests
import fitz
import os
from time import sleep

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

tokenCaptcha = "a72ddd0094ad56fd16f6d625feb4562ab703907a8a071daaf7892283950d4d0a"

idOj = "2"
data = "2022-12-19"

urlOrgaos = "https://pje.trt2.jus.br/pje-consulta-api/api/orgaosjulgadores?somenteOJCs=true"


orgaos = requests.get(urlOrgaos, headers=headers)
orgaos = orgaos.json()

for orgao in orgaos:
    if orgao.get("id"):
        id = orgao["id"]

        url = "https://pje.trt2.jus.br/pje-consulta-api/api/audiencias?pagina=1&tamanhoPagina=100&idOj=" + \
            str(id) + "&data=" + data
        req = requests.get(url, headers=headers)
        req = req.json()

        if req.get("resultado"):
            for item in req["resultado"]:
                file = requests.get(
                    'https://pje.trt2.jus.br/pje-consulta-api/api/processos/'+ item["idProcesso"] +'/documentos/283356716?tokenCaptcha=' + tokenCaptcha, allow_redirects=True, headers=headers)

                download = open(item["numeroProcesso"] + '.pdf', 'wb')
                download.write(file.content)
                download.close()

                savePdf = False

                with fitz.open(item["numeroProcesso"] + '.pdf') as pdf:
                    for pagina in pdf:
                        if 'perícia' in pagina.get_text():
                            savePdf = True
                            break

                if not savePdf:
                    os.remove(item["numeroProcesso"] + '.pdf')


    print("--------------------------------------------------")
