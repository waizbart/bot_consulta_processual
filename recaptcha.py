import cv2
import numpy as np
import pytesseract
import re
import requests
import base64

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'


while True:
    req1 = requests.get("https://pje.trt2.jus.br/pje-consulta-api/api/processos/4711135")
    req1 = req1.json()
    tokenDesafio = req1["tokenDesafio"]
    imageBase64 = req1["imagem"]

    decoded_data=base64.b64decode((imageBase64))
    img_file = open('image.png', 'wb')
    img_file.write(decoded_data)
    img_file.close()

    img = cv2.imread("image.png")

    grey = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR_EXACT)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(1,1))

    grey = cv2.threshold(grey, 242, 255, cv2.THRESH_TOZERO)[1]

    grey = cv2.morphologyEx(grey, cv2.MORPH_CLOSE, kernel)


    grey = cv2.dilate(grey , kernel2 ,iterations = 5)
    grey = cv2.erode(grey , kernel2, iterations = 1)

    cv2.imwrite('image.png',grey)

    resposta = pytesseract.image_to_string(grey)
    resposta = re.sub(r'\W+', '', resposta).lower()

    print("Resposta: ", resposta)

    req2 = requests.get("https://pje.trt2.jus.br/pje-consulta-api/api/processos/4711135?tokenCaptcha=" + tokenDesafio + "&resposta=" + resposta)
    req2 = req2.json()

    print("req2", req2)

    if req2.get("tokenDesafio"):
        print("Erooou")
    else: 
        print("Acertou")
        break