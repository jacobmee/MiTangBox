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
from time import sleep
import logging
import subprocess
import select
import threading
from airplay.item import Item
from roonapi.roonapi import RoonApi
import requests
import stat
from airplay.util import write_data_to_image
from airplay.codetable import CORE, SSNC, CORE_CODE_DICT, SSNC_CODE_DICT

CORE_CODE_WHITELIST = {'mikd', 'minm', 'mper', 'miid', 'asal', 'asar', 'ascm', 'asco', 'asbr', 'ascp', 'asda', 'aspl',
                       'asdm', 'asdc', 'asdn', 'aseq', 'asgn', 'asdt', 'asrv', 'assr', 'assz', 'asst', 'assp', 'astm',
                       'astc', 'astn', 'asur', 'asyr', 'asfm', 'asdb', 'asdk', 'asbt', 'agrp', 'ascd', 'ascs', 'asct',
                       'ascn', 'ascr', 'asri', 'asai', 'askd', 'assn', 'assu', 'aeNV', 'aePC', 'aeHV', 'aeMK', 'aeSN',
                       'aeEN'}



class ShairportWatcher(threading.Thread):
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.log = logging.getLogger("MiTangBox-Shairport-theading")
        self.format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S")
        self.handler = logging.StreamHandler(stream=sys.stdout)
        self.handler.setFormatter(self.format)
        self.handler.setLevel(logging.DEBUG)
        self.log.addHandler(self.handler)
        self.log.setLevel(logging.DEBUG)
        self.func = func


    def run(self):
        # Reading from file
        self._reading()


    def _reading(self):
        # wait till the pipe file is found
        pipe_file =  "/tmp/shairport-sync-metadata"
        while not os.path.exists(pipe_file) or not stat.S_ISFIFO(os.stat(pipe_file).st_mode):
            self.log.warning("Could not find pipe: %s. Retrying in 5 seconds...", pipe_file)
            sleep(5)

        self.log.info("Pipe watcher %s", pipe_file)

        self._is_listening = True
        self._tmp_track_info = {}   # temporary storage for track metadata
        self.track_info = {}  # track info send by ssnc
        self.artwork = ""

        tmp = ""  # temporary string which stores one item
        while self._is_listening:
            with open(pipe_file) as pipe:
                for line in pipe:
                    # service was stopped
                    if not self._is_listening:
                        break

                    strip_line = line.strip()
                    if strip_line.endswith("</item>"):
                        item = Item.item_from_xml_string(tmp + strip_line)
                        if item:
                            self._process_item(item)
                        tmp = ""
                    elif strip_line.startswith("<item>"):
                        # if only a closing tag is missing we try to close the tag and try to parse the data
                        if tmp != "":
                            item = Item.item_from_xml_string(tmp + "</item>")
                            if item:
                                self._process_item(item)
                        tmp = strip_line
                    else:
                        tmp += strip_line


    # pylint: disable=R0912, R0915
    def _process_item(self, item):
        """
        Process a single item from the pipe.
        :param item: metadata item
        """

        if item.type == SSNC:
            # snua or snam are the 'ANNOUNCE' packet to reserve the player
            if item.code == "PICT":
                if item.data_base64:  # check if picture data is found
                    self.artwork = write_data_to_image(item.data())  # Path to artwork image
            elif item.code == "pcst":
                # reset artwork
                self.artwork = ""
            elif item.code == "pcen":
                # send artwork when all data is received
                self.func(self.artwork)
                #self.log.info("Artwork is done:" + self.artwork)
            elif item.code == "mden":
                # only send updates if required
                #if not (self._tmp_track_info.items() <= self.track_info.items()):
                self.track_info = self._tmp_track_info
                self._tmp_track_info = {}
            elif item.code == "pend":
                self.func("./default.jpg")
            # else:
            #     self.log.debug("Unknown (ssnc) code \"%s\", with base64 data %s.", item.code,
            #                    item.data_base64)

        elif item.type == CORE:
            if item.code in CORE_CODE_WHITELIST:
                # save metadata info
                dmap_key, data_type = CORE_CODE_DICT[item.code]
                self._tmp_track_info[dmap_key] = item.data(dtype=data_type)
            elif item.code in CORE_CODE_DICT:
                # just ignore these and don't add them to the track info
                # you can still listen to the item property to respond to these keys
                pass
            # else:
            #     self.log.debug("Unknown core code: %s, with data %s.", item.code, item.data_base64)

        self.item = item


class RoonWatcher(threading.Thread):

    def _watching(self, event, changed_ids):
        # get target zone output_id
        zones = self.roonapi.zones
        for output in zones.values():
            if output["display_name"] == self.target_zone:
                if output["state"] == "playing":
                    current_image_key = output["now_playing"]["image_key"]
                    if current_image_key != self.image_key:
                        self.log.info("New Playing:" + output["now_playing"]["one_line"]["line1"])
                        self.log.info("New image:" + current_image_key)
                        self.image_key = current_image_key
                        # http://192.168.0.21:9100/api/image/f1b0059ad5ef45caaed0417103ea0505
                        url = 'http://192.168.0.21:9100/api/image/'
                        r = requests.get(url+current_image_key, allow_redirects=True)
                        file = "/tmp/roon_"+current_image_key+".jpg"
                        open(file, 'wb').write(r.content)
                        self.func(file)
                else:
                    self.func("./default.jpg")



    def __init__(self, func):
        threading.Thread.__init__(self)
        self.log = logging.getLogger("MiTangBox-Roon-theading")
        self.format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S")
        self.handler = logging.StreamHandler(stream=sys.stdout)
        self.handler.setFormatter(self.format)
        self.handler.setLevel(logging.DEBUG)
        self.log.addHandler(self.handler)
        self.log.setLevel(logging.DEBUG)
        self.func = func

        self.server = "192.168.0.21"
        self.target_zone = "MiTang Go"
        self.image_key = None
        self.appinfo = {
            "extension_id": "python_roon_reader",
            "display_name": "Roon Reader",
            "display_version": "1.0.0",
            "publisher": "jacob",
            "email": "jacob@mitang.me",
        }

        # Can be None if you don't yet have a token
        try:
            self.token = open("mytokenfile").read()
        except Exception as e:
            self.token = None

        # Take a look at examples/discovery if you want to use discovery.
        self.roonapi = RoonApi(self.appinfo, self.token, self.server)
        # receive state updates in your callback
        self.roonapi.register_state_callback(self._watching)

    def run(self):
        sleep (10)
        with open("mytokenfile", "w") as f:
            f.write(self.roonapi.token)
        self.log.info("mytokenfile is updated")

        while True:
            sleep(600)
            self.log.info("Roon watcher timechecks")


class mitangbox(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.log = logging.getLogger("MiTangBox-display")
        self.format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S")
        self.handler = logging.StreamHandler(stream=sys.stdout)
        self.handler.setFormatter(self.format)
        self.handler.setLevel(logging.DEBUG)
        self.log.addHandler(self.handler)
        self.log.setLevel(logging.DEBUG)


        #self.length = 0
        self.window = uic.loadUi("./mitangbox.ui")
        self.window.setStyleSheet("background-color : black; color : white;");
        self.window.showFullScreen();

        self.mainArea = self.window.findChild(QLabel, 'main')

        self._set_metadata("./default.jpg")

        # theading starts
        thread1 = ShairportWatcher(self._set_metadata)
        thread1.start()
        # theading ends

        # theading starts
        thread2 = RoonWatcher(self._set_metadata)
        thread2.start()
        # theading ends


    def _set_metadata(self,artwork_path):
        if artwork_path is None:
            return

        pixmap = QPixmap(artwork_path)
        if pixmap is None:
            return

        if pixmap.width() > 100:
            self.log.info("Artwork:" + artwork_path)
            #self.log.info("width:" + str(pixmap.width()) +", height:"+str(pixmap.height()))
            if pixmap.width() > pixmap.height():
                self.mainArea.setPixmap(pixmap.scaledToWidth(240))
            else:
                self.mainArea.setPixmap(pixmap.scaledToHeight(240))


if (__name__ == "__main__"):
    client = mitangbox(sys.argv)
    signal.signal(signal.SIGINT, lambda *args: client.quit())
    client.startTimer(500)
    client.exec_()
