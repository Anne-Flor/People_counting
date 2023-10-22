import numpy as np
import cv2 

#x: a coordenada x do canto superior esquerdo do retângulo.
#y: a coordenada y do canto superior esquerdo do retângulo.
#w: a largura do retângulo.
#h: a altura do retângulo.
def center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy

cap = cv2.VideoCapture('caminando.mp4')

detects = []

fgbg = cv2.createBackgroundSubtractorMOG2()

# Define o início e o fim do vídeo
start_frame = 1000
end_frame = 2200

posL = 150
offset = 30

xy1 = (20, posL)
xy2 = (300, posL)

total = 0 
up    = 0
down  = 0

# Pular para o frame inicial
cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

# Laço principal
while True:
        
    frame_count = cap.get(cv2.CAP_PROP_POS_FRAMES)

    # Verifica se o vídeo chegou ao fim
    if frame_count >= end_frame:
        break

    # Captura o próximo frame
    ret, frame = cap.read()
    cv2.putText(frame, "Frame: "+str(frame_count), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255),2)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Aplica a subtração de fundo
    fgmask = fgbg.apply(gray)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    retval, th = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
    
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations = 2)

    dilation = cv2.dilate(opening,kernel,iterations = 8)

    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel, iterations = 8)

    # Detecta os contornos
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Desenha a linha horizontal
    cv2.line(frame, xy1, xy2, (255, 0, 0), 3)
    cv2.line(frame, (xy1[0], posL - offset), (xy2[0], posL - offset), (255, 255, 0), 2)
    cv2.line(frame, (xy1[0], posL + offset), (xy2[0], posL + offset), (255, 255, 0), 2)

    # Desenha os contornos

    i = 0
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        if int(area) > 3000:
            centro = center(x, y, w, h)
            cv2.putText(frame, "Pessoa", (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            cv2.circle(frame, centro, 4, (0, 0, 255), -1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if len(detects) <= i:
                detects.append([])
            if centro[1]> posL-offset and centro[1] < posL+offset:
                detects[i].append(centro)
            else:
                detects[i].clear()
            i += 1

    if i == 0:
        detects.clear()

    i = 0

    if len(contours) == 0:
        detects.clear()

    else:
    # Verifica se o objeto está cruzando a linha
        for detect in detects:
            for (c, l) in enumerate(detect):
                if detect[c - 1][1] < posL and l[1] > posL:
                    detect.clear()
                    up += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, (0, 255, 0), 5)
                    continue

                if detect[c - 1][1] > posL and l[1] < posL:
                    detect.clear()
                    down += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, (0, 0, 255), 5)
                    continue

                if c > 0:
                    cv2.line(frame, detect[c - 1], l, (0, 0, 255), 1)

        # total += up - down
    cv2.putText(frame, "Frame: "+str(frame_count), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255),2)
    frame_count += 1
    cv2.putText(frame, "TOTAL: "+str(total), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255),2)
    cv2.putText(frame, "SUBINDO: "+str(up), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),2)
    cv2.putText(frame, "DESCENDO: "+str(down), (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255),2)
    # Mostra o frame
    cv2.imshow("frame", frame)

    # Espera por uma tecla
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Fecha o vídeo
cap.release()
