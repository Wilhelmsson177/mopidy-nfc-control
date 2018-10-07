# -*- coding: utf-8 -*-
'''
The NFC Tag monitor which returns the values as callbacks.

:author: Willi Meierhof
'''
import logging
from threading import Event, Thread
import time

import nxppy
import ndef

logger = logging.getLogger(__name__)


class NfcTagMonitor(Thread):
    '''The tag monitor class definition.
    '''

    def __init__(self, nfc_tag_hold=True):
        """
        Constructor.
        """
        Thread.__init__(self)
        self._stop_event = Event()

        self.lastTag = None
        self.uriTagCallback = None
        self.controlTagCallback = None
        self.nfcTagRemovedCallback = None
        self.nfcTagHold = nfc_tag_hold
        self.tagRemoved = True
        self.mifare = nxppy.Mifare()

    def run(self):
        """
        The method to run in an additional thread.
        """
        logger.info("NfcTagMonitor: Run the cycle ...")
        while True:
            # reading the card id
            try:
                uid = self.mifare.select()
                if uid != self.lastTag:
                    logger.debug("Selected the following id: {}".format(uid))
                    self.lastTag = uid
                    nfc_content = list(
                        ndef.message_decoder(self.mifare.read_ndef()))
                    for record in nfc_content:
                        logger.debug("Record type: {}".format(record.type))
                        if record.type == 'urn:nfc:wkt:U':
                            logger.debug("detected URI type")
                            logger.debug('URI: {}'.format(record.uri))
                            self.uriTagCallback(record.uri)
                        else:
                            logger.debug("detected unknown type")
                            logger.debug('TYPE: {}'.format(record.type))
                            self.controlTagCallback()
                else:
                    if self.nfcTagHold and self.tagRemoved:
                        self.controlTagCallback('RESUME')
                self.tagRemoved = False
            except nxppy.SelectError as se:
                # SelectError is raised if no card is in the field.
                logger.debug(
                    "Had an issue selecting the id. Probably the NFC tag has been removed: {}"
                    .format(se))
                if self.nfcTagHold:
                    self.nfcTagRemovedCallback()
                    self.tagRemoved = True
            time.sleep(0.5)
    
    def cancel(self):
        self._stop_event.set()

    def RegisterUriTagCallback(self, callback):
        self.uriTagCallback = callback

    def RegisterControlTagCallback(self, callback):
        self.controlTagCallback = callback

    def RegisterNfcTagRemovedCallback(self, callback):
        self.nfcTagRemovedCallback = callback
