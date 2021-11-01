#!/usr/bin/env /usr/bin/python3

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QProgressBar, QDesktopWidget
from PyQt5 import uic

from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation
from PyQt5.QtGui import QPixmap, QFont

import datetime
import signal
import sys
import os
import time
import logging
import subprocess
import select
import threading



class myThread(threading.Thread):
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.log = logging.getLogger("MiTangBox-theading")
        self.format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S")
        self.handler = logging.StreamHandler(stream=sys.stdout)
        self.handler.setFormatter(self.format)
        self.handler.setLevel(logging.DEBUG)
        self.log.addHandler(self.handler)
        self.log.setLevel(logging.DEBUG)
        self.func = func


    def run(self):
        self.log.debug("Watching starts")
        # Reading from file
        f = subprocess.Popen(['cat','',"/home/pi/metadata/now_playing"],\
            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)

        while True:
            if p.poll(1):
                l = f.stdout.readline()
                # self.log.debug(l)
                self.func(l.decode('utf8'))
            time.sleep(0.5)



class MiTangBox(QApplication):
  def __init__(self, argv):
    super().__init__(argv)
    self.log = logging.getLogger("MiTangBox-display")
    self.format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S")
    self.handler = logging.StreamHandler(stream=sys.stdout)
    self.handler.setFormatter(self.format)
    self.handler.setLevel(logging.DEBUG)
    self.log.addHandler(self.handler)
    self.log.setLevel(logging.DEBUG)
    self.log.info("Starting application")

    #self.length = 0
    self.window = uic.loadUi("./MiTangBox.ui")
    self.window.setStyleSheet("background-color : black; color : white;");

    self.window.show()
    self.mainArea = self.window.findChild(QLabel, 'main')

    self._initialize_display()

    # theading starts
    thread1 = myThread(self._set_metadata)
    thread1.start()
    # theading ends
    self.window.destroyed.connect(self.quit)


  def _initialize_display(self):
     self._set_metadata("artwork=default.jpg")


  def _set_metadata(self, line):
    line = line.rstrip("\n")
    if line is None:
        return

    # What's the incoming message?
    try:
        key, value = line.split("=")
    except Exception as e:
        return

    # self.log.debug("["+key+"]:" + value)

    # Post to UI
    if key == "artwork": # doing artwork
        if value is not None:
            artwork_path = "/home/pi/metadata/"+value
            self.log.debug("Artwork:" + artwork_path)
            pixmap = QPixmap(artwork_path)
            if pixmap.width() >= pixmap.height():
                self.mainArea.setPixmap(pixmap.scaledToWidth(200))
            else:
                self.mainArea.setPixmap(pixmap.scaledToHeight(200))


  def _clear_display(self):
    self.mainArea.clear()


if (__name__ == "__main__"):
  client = MiTangBox(sys.argv)
  signal.signal(signal.SIGINT, lambda *args: client.quit())
  client.startTimer(500)
  client.exec_()
