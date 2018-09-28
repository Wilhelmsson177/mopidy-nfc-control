import logging
import traceback

import time

from mopidy import core
import nxppy

import pykka

logger = logging.getLogger(__name__)
mifare = nxppy.Mifare()


class NfcControl(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(NfcControl, self).__init__()
        self.core = core
        self.lastId = None

    def _getIds():
        while True:
            # reading the card id
            try:
                uid = mifare.select()
                logging.info("Received the following data: {}".format(uid))
                if uid != self.lastId:
                    self.lastId = uid

            except nxppy.SelectError as se:
                # SelectError is raised if no card is in the field.
                logging.debug("Had an issue selecting the id: {}".format(se))

            time.sleep(0.5)
