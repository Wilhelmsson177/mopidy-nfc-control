# -*- coding: utf-8 -*-
'''
The NFC Tag monitor which returns the values as callbacks.

:author: Willi Meierhof
'''
import logging
import time

import nxppy
import ndef

logger = logging.getLogger(__name__)

class NfcTagMonitor(object):
    '''The tag monitor class definition.
    '''
    
    def __init__(self, nfc_tag_hold=True):
        """
        Constructor.
        """
        self.lastTag = None
        self.uriTagCallback = None
        self.controlTagCallback = None
        self.nfcTagRemovedCallback = None
        self.nfcTagHold = nfc_tag_hold
        self.tagRemoved = True
        self.mifare = nxppy.Mifare()

    def Run(self):
        """
        The method to run in an additional thread.
        """
        while True:
            # reading the card id
            try:
                uid = mifare.select()
                if uid != self.lastId:
                    logger.info("Selected the following id: {}".format(uid))
                    self.lastId = uid
                    nfc_content = list(ndef.message_decoder(mifare.read_ndef()))
                    for record in nfc_content:
                        logger.info("Record type: {}".format(record.type))
                        if record.type == 'urn:nfc:wkt:U':
                            logger.info("detected URI type")
                            logger.info('URI: {}'.format(record.uri))
                            self.uriTagCallback(uri)
                        else:
                            logger.info("detected unknown type")
                            logger.info('TYPE: {}'.format(record.type))
                            self.controlTagCallback()
                else:
                    if self.nfcTagHold and self.tagRemoved:
                       self.controlTagCallback('RESUME')
                self.tagRemoved = False
            except nxppy.SelectError as se:
                # SelectError is raised if no card is in the field.
                logger.debug("Had an issue selecting the id. Probably the NFC Tag has been removed: {}".format(se))
                if self.nfcTagHold:
                    self.nfcTagRemovedCallback()
                    self.tagRemoved = True

            time.sleep(0.1)

    def RegisterUriTagCallback(self, callback):
        self.uriTagCallback = callback
    
    def RegisterControlTagCallback(self, callback):
        self.controlTagCallback = callback
        
    def RegisterNfcTagRemovedCallback(self, callback):
        self.nfcTagRemovedCallback = callback
