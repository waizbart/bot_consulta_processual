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
        print("Gerando código captcha")
        captchaCode = getCaptchaCode('captcha.png')

        if captchaCode:
            req2 = requests.get("https://pje.trt2.jus.br/pje-consulta-api/api/processos/" + str(processId) + "?tokenDesafio=" +
                                tokenDesafio + "&resposta=" + captchaCode)

            req2headers = req2.headers
            req2 = req2.json()

            if req2.get("tokenDesafio"):
                print("Erro captcha")
                return None
            else:
                print("Acertou captcha")
                tokenCaptcha = req2headers['captchatoken']
                return tokenCaptcha

    except Exception as e:
        print("Error", e)


def getCaptchaCode(filename):
    try:
        solver = TwoCaptcha('b405caa1b13eb319db4794df3db523de')

        print("Getting captcha code...")

        result = solver.normal(filename)

        os.remove(filename)

        return result['code']
    except Exception as e:
        # invalid parameters passed
        print("Exception", e)


def getFoundsSolver():
    try:
        solver = TwoCaptcha('b405caa1b13eb319db4794df3db523de')

        balance = solver.balance()

        return balance
    except Exception as e:
        # invalid parameters passed
        print("Exception", e)
