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
    self.window.resize(320, 240)
    self.window.show()

    self.mainArea = self.window.findChild(QLabel, 'artwork')
    self.bottomArea = self.window.findChild(QLabel, 'title')

    self._initialize_display()
    #self._watching()
    #self.window.destroyed.connect(self.quit)

  def _initialize_display(self):
     self._set_metadata("artwork=default.jpg\n")
     self._set_metadata("title=MiTang Go\n")

  def _watching(self):

    # Reading from file
    f = subprocess.Popen(['cat','',"/home/pi/metadata/now_playing"],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)

    while True:
        if p.poll(1):
            l = f.stdout.readline()
            #self.log.info(l)
            self._set_metadata(l.decode('utf8'))
            #sys.stdout.write()
        time.sleep(1)

  def _set_metadata(self, line):
    line = line.rstrip("\n")

    size = self.window.size();
    artwork = None
    title = None

    # What's the incoming message?
    try:
        key, value = line.split("=")
        self.log.debug("["+key+"]:" + value)

        # Post to UI
        if key == "artwork": # doing artwork
            if value is not None:
                pixmap = QPixmap("/home/pi/metadata/"+value)
                if pixmap.width() >= pixmap.height():
                    self.mainArea.setPixmap(pixmap.scaledToWidth(200))
                else:
                    self.mainArea.setPixmap(pixmap.scaledToHeight(200))
        elif key == "title": # doing title
            if value is not None:
                self.bottomArea.setText(value)

    except Exception as e:
        self.log.info("ignore:" + line)


  def _clear_display(self):
    self.mainArea.clear()
    self.bottomArea.clear()

if (__name__ == "__main__"):
  client = MiTangBox(sys.argv)
  signal.signal(signal.SIGINT, lambda *args: client.quit())
  client.startTimer(500)
  client.exec_()
