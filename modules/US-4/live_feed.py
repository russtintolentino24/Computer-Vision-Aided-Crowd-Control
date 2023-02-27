import tkinter
from tkinter import *
from PIL import Image,ImageTk
import os
import cv2
import imutils
import numpy as np
import argparse


def show_webcam():
   check, frame = cam.read()
      
   if check:
      cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
      img = ImageTk.PhotoImage(Image.fromarray(cv2_img))
      disp.imgtk = img
      disp.configure(image=img)
      disp.after(10,show_webcam)


root=Tk()

global disp 
disp = Label(root)
disp.pack()

global cam
cam = cv2.VideoCapture(0)
  


show_webcam()
root.mainloop()
