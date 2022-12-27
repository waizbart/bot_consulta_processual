import base64
import requests
import os
from twocaptcha import TwoCaptcha


def saveImageBase64(filename, imageBase64):
    decoded_data = base64.b64decode((imageBase64))
    img_file = open(filename, 'wb')
    img_file.write(decoded_data)
    img_file.close()


def getCaptchaToken(processId):
    try:
        req1 = requests.get(
            "https://pje.trt2.jus.br/pje-consulta-api/api/processos/" + str(processId))
        req1 = req1.json()
        tokenDesafio = req1["tokenDesafio"]
        imageBase64 = req1["imagem"]

        saveImageBase64('captcha.png', imageBase64)

        captchaCode = getCaptchaCode('captcha.png')

        req2 = requests.get("https://pje.trt2.jus.br/pje-consulta-api/api/processos/" + str(processId) + "?tokenDesafio=" +
                            tokenDesafio + "&resposta=" + captchaCode)

        req2headers = req2.headers
        req2 = req2.json()

        if req2.get("tokenDesafio"):
            print("Erro captcha")
            return getCaptchaToken(processId)
        else:
            print("Acertou captcha")
            tokenCaptcha = req2headers['captchatoken']
            return tokenCaptcha

    except Exception as e:
        print("Error", e)
        return getCaptchaToken(processId)


def getCaptchaCode(filename):
    solver = TwoCaptcha('ee753880fba88538ae2972eaeb7b4aba')

    config = {
        'server':           '2captcha.com',
        'apiKey':           'ee753880fba88538ae2972eaeb7b4aba',
        'softId':            123,
        'defaultTimeout':    120,
        'recaptchaTimeout':  600,
        'pollingInterval':   10,
    }

    solver = TwoCaptcha(**config)

    print("Getting captcha code...")

    result = solver.normal(filename)

    os.remove(filename)

    return result['code']
