import requests
import base64

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

url = "https://pje.trt2.jus.br/pje-consulta-api/api/processos/4771470"


for i in range(300):
    r = requests.get(url, headers=headers)
    r= r.json()

    decoded_data = base64.b64decode((r["imagem"]))
    # write the decoded data back to original format in  file
    img_file = open('captchas/' + str(i) + ".png", 'wb')
    img_file.write(decoded_data)
    img_file.close()
