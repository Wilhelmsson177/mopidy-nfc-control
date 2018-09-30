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
    
    def __init__(self):
        """
        Constructor.
        """
        self.lastTag = None
        self.uriTagCallback = None
        self.controlTagCallback = None
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

            except nxppy.SelectError as se:
                # SelectError is raised if no card is in the field.
                logger.debug("Had an issue selecting the id: {}".format(se))

            time.sleep(0.5)

    def RegisterUriTagCallback(self, callback):
        self.uriTagCallback = callback
    
    def RegisterControlTagCallback(self, callback):
        self.controlTagCallback = callback


