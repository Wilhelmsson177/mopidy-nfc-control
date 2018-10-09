# -*- coding: utf-8 -*-
'''
Created on 09.10.2018

@author: Willi
'''
import logging
import time
from threading import Thread

import dbus
from dbus.mainloop.glib import DBusGMainLoop

logger = logging.getLogger(__name__)
__logprefix__ = 'NfcTagMonitor: '


class NfcTagMonitor(Thread):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self.started = True
        self.lastTag = None

        self.newTextCallback = None
        self.newUriCallback = None
        self.tagLostCallback = None

        dbus_loop = DBusGMainLoop()
        self.bus = dbus.SystemBus(mainloop=dbus_loop)
        self.objManager = dbus.Interface(
            self.bus.get_object("org.neard", "/"),
            "org.freedesktop.DBus.ObjectManager")
        self.adapter = dbus.Interface(
            self.bus.get_object("org.neard", "/org/neard/nfc0"),
            "org.neard.Adapter")

    def run(self):
        while self.started:
            self.adapter.StartPollLoop("test")
            objects = self.objManager.GetManagedObjects()
            allInterfaces = {}
            for dictionary in objects.itervalues():
                allInterfaces.update(dictionary)
            props = allInterfaces.get("org.neard.Record", {})

            logger.debug("{}{}".format(__logprefix__, props))

            for (key, value) in props.items():
                if key == "URI":
                    uri = value.decode("UTF-8")
                    if uri != self.lastTag:
                        logger.debug(__logprefix__ +
                                     "TAG_DETECTED: {}".format(uri))
                        self.newTagCallback(uri)
                        self.lastTag = uri
                    break
                elif key == "Representation":
                    text = value.decode("UTF-8")
                    if text != self.lastTag:
                        logger.debug(__logprefix__ +
                                     "TAG_DETECTED: {}".format(text))
                        self.newTagCallback(text)
                        self.lastTag = text
                    break
            else:
                if self.lastTag:
                    logger.debug(__logprefix__ + "TAG_LOST")
                    self.tagLostCallback()
                    self.lastTag = None

            time.sleep(0.1)

    def cancel(self):
        self.started = False

    def RegisterNewUriCallback(self, callback):
        self.newUriCallback = callback

    def RegisterNewTextCallback(self, callback):
        self.newTextCallback = callback

    def RegisterTagLostCallback(self, callback):
        self.tagLostCallback = callback
