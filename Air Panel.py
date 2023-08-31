import sys

import cv2
import numpy as np
import time
import os
import pyautogui
import HandTracking as htm

tipIds = [4, 8, 12, 16, 20]


def Draw():
    def fingerUps():
        if len(lmList) != 0:
            fingers = []

            # Thumb
            if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

            # 4 Fingers
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            return fingers

    ########
    brushThickness = 5
    #########

    folderPath = "Header"
    myList = os.listdir(folderPath)
    # print(myList)
    overlayList = []
    for imPath in myList:
        image = cv2.imread(f'{folderPath}/{imPath}')
        Image = cv2.resize(image, (640, 63))
        overlayList.append(Image)
    # print(len(overlayList))
    header = overlayList[0]
    drawcolor = (255, 0, 255)
    cap = cv2.VideoCapture(0)
    detector = htm.handDetector(detectionCon=0.85)
    xp, yp = 0, 0
    imgCanvas = np.zeros((480, 640, 3), np.uint8)

    while True:

        # 1. import image
        success, img = cap.read()
        img = cv2.flip(img, 1)

        # 2. Find Hand landmarks
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:
            # print(lmList)

            # tip of index and middle fingers
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]

            # 3.Check which finger are up
            fingers = fingerUps()
            # print(fingers)

            # 4. If selection mode - Two finger are up
            if fingers[1] and fingers[2]:
                xp, yp = 0, 0
                print('selection mode')
                if y1 < 125:
                    if 150 < x1 < 230:
                        header = overlayList[0]
                        drawcolor = (255, 0, 255)
                    elif 250 < x1 < 340:
                        header = overlayList[1]
                        drawcolor = (255, 0, 0)
                    elif 350 < x1 < 430:
                        header = overlayList[2]
                        drawcolor = (0, 255, 0)
                    elif 450 < x1 < 510:
                        header = overlayList[3]
                        drawcolor = (0, 0, 0)

                cv2.rectangle(img, (x1, y1 - 20), (x2, y2 + 20), drawcolor, cv2.FILLED)

            # 5. If Drawing Mode - Index finger is up
            if fingers[1] and fingers[2] == False:
                print('drawing mode')
                cv2.circle(img, (x1, y1), 5, drawcolor, cv2.FILLED)
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                if drawcolor == (0, 0, 0):
                    cv2.line(img, (xp, yp), (x1, y1), drawcolor, 100)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawcolor, 100)
                else:
                    cv2.line(img, (xp, yp), (x1, y1), drawcolor, brushThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawcolor, brushThickness)

                xp, yp = x1, y1

        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)

        img[0:63, 0:640] = header
        # img = cv2.addWeighted(img, 0.5, imgCanvas, 0.5, 0)
        cv2.imshow("Image", img)
        cv2.imshow("Canvas", imgCanvas)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def Mouse():
    def fingerUps():
        if len(lmList) != 0:
            fingers = []

            # Thumb
            if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

            # 4 Fingers
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            return fingers

    ############
    wCam, hCam = 640, 480
    frameR = 100
    smoothening = 5

    ############
    pTime = 0
    plocX, plocY = 0, 0
    clocX, clocy = 0, 0
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    detector = htm.handDetector(maxHands=1)
    wScr, hScr = pyautogui.size()
    # print(wScr,  hScr)

    while True:
        # 1. Find Hand Landmarks
        success, img = cap.read()
        # img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        # 2.Get the tip of the index and middle fingers
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            # print(x1, y1, x2, y2)

            # 3. Check which finger are up
            fingers = fingerUps()
            # print(fingers)
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
            # 4. only index finger : Moving Mode
            if fingers[1] == 1 and fingers[2] == 0:
                # 5.convert coordinate
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                # 6. Smoothen value
                clocX = plocX + (x3 - plocX) / smoothening
                clocy = plocY + (y3 - plocY) / smoothening

                # 7.Move Mouse
                pyautogui.moveTo(wScr - clocX, clocy)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocy

            # 8.Both index and middle finger are up: clicking Mode
            if fingers[1] == 1 and fingers[2] == 1:
                length, img, lineInfo = detector.findDistance(8, 12, img)
                # print(length)
                if length < 40:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()
            # 9.find distance between fingers
            # 10.Click mouse if disrance short
            # 11.Frame Rate

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def main():
    # print(sys.argv[1])
    # if sys.argv[1] == 'm':
    #     Mouse()
    # elif sys.argv[1] == 'd':
    #     Draw()
    while True:
        print("\nMAIN MENU")
        print("1. Mouse")
        print("2. Draw")
        print("3. Exit")
        choice = int(input("Enter the Choice:"))

        if choice == 1:
            Mouse()
        elif choice == 2:
            Draw()
        elif choice == 3:
            break
        else:
            print("Incorrect option")


if __name__ == '__main__':
    main()
