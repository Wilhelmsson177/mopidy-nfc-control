import logging
import traceback

import time

from mopidy import core
import nxppy
import ndef

import pykka

logger = logging.getLogger(__name__)
mifare = nxppy.Mifare()


class NfcControl(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(NfcControl, self).__init__()
        self.core = core
        self.lastId = None
        logger.info('Successfully initialized NfcControl frontend plugin.')
        self._getIds()

    def _getIds(self):
        while True:
            # reading the card id
            try:
                uid = mifare.select()
                logger.info("Selected the following id: {}".format(uid))
                if uid != self.lastId:
                    self.lastId = uid
                    nfc_content = list(ndef.message_decoder(mifare.read_ndef()))
                    for record in nfc_content:
                        logger.info("Record type: {}".format(record.type))
                        if record.type == 'urn:nfc:wkt:U':
                            logger.info("detected URI type")
                            logger.info('URI: {}'.format(record.uri))

            except nxppy.SelectError as se:
                # SelectError is raised if no card is in the field.
                logger.debug("Had an issue selecting the id: {}".format(se))

            time.sleep(0.5)
