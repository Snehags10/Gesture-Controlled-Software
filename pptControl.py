# This app will use your built-in webcam to control your slides presentation.
# For a one-handed presentation, use Gesture 1 (thumbs up) to go to the previous slide and Gesture 2 (whole hand pointing up) to go to the next slide.

import win32com.client
import cv2
import os
import numpy as np
import aspose.slides as slides
import aspose.pydrawing as drawing
import time

filename = "E:\\2023_2024\\LBS\\GestureControlledPC\\GCPC\\test.pptx"

'''
filename = "E:\\2023_2024\\LBS\\GestureControlledPC\\GCPC\\test.pptx"
Application = win32com.client.Dispatch("PowerPoint.Application")
Presentation = Application.Presentations.Open(filename)
#print(Presentation.Name)
Presentation.SlideShowSettings.Run()
'''

# Instantiates the Presentation class and passes the file path to its constructor
with slides.Presentation(filename) as pres:
    # Prints the total number of slides present in the presentation
    print(pres.slides.length)
    max_slide_len = pres.slides.length

'''
for index in range(pres.slides.length):
    Presentation.SlideShowWindow.View.Next()
    time.sleep(1)
'''


def openPPT():
    global Presentation
    global Application
    Application = win32com.client.Dispatch("PowerPoint.Application")
    Presentation = Application.Presentations.Open(filename)
    Presentation.SlideShowSettings.Run()
    time.sleep(2)

def runPPT():    # Finds all hands in a frame
    global Presentation
    Presentation.SlideShowSettings.Run()

def moveNextSlide():    # Finds all hands in a frame
    global Presentation
    Presentation.SlideShowWindow.View.Next()

def movePreviousSlide():    # Finds all hands in a frame
    global Presentation
    Presentation.SlideShowWindow.View.Previous()

def closePPT():
    global Presentation
    global Application
    if Application:
        Presentation.SlideShowWindow.View.Exit()
        time.sleep(1)
        Application.Quit()
        print("Application Quit")
        os.system("TASKKILL /F /IM powerpnt.exe")
        time.sleep(1)