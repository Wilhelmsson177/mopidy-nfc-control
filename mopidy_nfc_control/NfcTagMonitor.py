# -*- coding: utf-8 -*-
'''
Created on 02.12.2016

@author: lukas
'''

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from threading import Thread
import time


class NfcTagMonitor(Thread):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self.lastTag = None
        self.newTagCallback = None
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
        while True:
            self.adapter.StartPollLoop("test")
            objects = self.objManager.GetManagedObjects()
            allInterfaces = {}
            for dictionary in objects.itervalues():
                allInterfaces.update(dictionary)
            props = allInterfaces.get("org.neard.Record", {})
            for (key, value) in props.items():
                if key == "URI":
                    uri = value.decode("UTF-8")
                    if uri != self.lastTag:
                        print("TAG_DETECTED: {}".format(uri))
                        self.newTagCallback(uri)
                        self.lastTag = uri
                    break
            else:
                if self.lastTag:
                    print("TAG_LOST")
                    self.tagLostCallback()
                    self.lastTag = None

            time.sleep(0.1)

    def RegisterNewTagCallback(self, callback):
        self.newTagCallback = callback

    def RegisterTagLostCallback(self, callback):
        self.tagLostCallback = callback
