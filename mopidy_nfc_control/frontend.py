import logging
import time
from threading import Thread
import traceback

from mopidy import core
import pykka

import nxppy
import ndef

logger = logging.getLogger(__name__)
mifare = nxppy.Mifare()

__logprefix__ = 'NfcControl: '


class NfcControl(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(NfcControl, self).__init__()
        self.core = core
        self.taghold = config['nfc-control']['taghold']
        self.running = False

        self.lastTag = None
        self.tagRemoved = True

        logger.info(__logprefix__ +
                    'Successfully initialized NfcControl frontend plugin.')

    def start_thread(self):
        while self.running:
            # try:
            logger.info(__logprefix__ + 'Cycle')
            try:
                uid = mifare.select()
                logger.info(__logprefix__ + uid)
            except nxppy.SelectError:
                # SelectError is raised if no card is in the field.
                logger.info(__logprefix__ + "empty")

            time.sleep(1)
            #     # uid = self.mifare.select()
            #     uid = 1
            #     logger.info(__logprefix__ + 'Cycle #2')
            #     if uid != self.lastTag:
            #         logger.debug("Selected the following id: {}".format(uid))
            #         self.lastTag = uid
            #         nfc_content = list(
            #             ndef.message_decoder(self.mifare.read_ndef()))
            #         for record in nfc_content:
            #             logger.debug("Record type: {}".format(record.type))
            #             if record.type == 'urn:nfc:wkt:U':
            #                 logger.debug("detected URI type")
            #                 logger.debug('URI: {}'.format(record.uri))
            #                 self.PlaybackonUri(record.uri)
            #             else:
            #                 logger.debug("detected unknown type")
            #                 logger.debug('TYPE: {}'.format(record.type))
            #                 self.Control()
            #     else:
            #         logger.info(__logprefix__ + 'Cycle #3')
            #         if self.nfcTagHold and self.tagRemoved:
            #             self.Control('RESUME')
            #     logger.info(__logprefix__ + 'Cycle #4')
            #     self.tagRemoved = False
            # except nxppy.SelectError as se:
            #     # SelectError is raised if no card is in the field.
            #     logger.debug(
            #         "Had an issue selecting the id. Probably the NFC tag has been removed: {}"
            #         .format(se))
            #     if self.nfcTagHold:
            #         self.TagRemoved()
            #         self.tagRemoved = True
            time.sleep(0.5)

    def on_start(self):
        try:
            self.running = True
            thread = Thread(target=self.start_thread)
            thread.start()
        except:
            traceback.print_exc()

    def on_stop(self):
        logger.info(__logprefix__ + 'NfcTagMonitor thread stopped.')
        self.running = False

    def TagRemoved(self):
        logger.debug(__logprefix__ + 'Tag has been removed')

    def Control(self, control_string=None):
        logger.info(__logprefix__ +
                    'Received {} control.'.format(control_string))

    def PlaybackonUri(self, uri):
        '''
        Play the given uri on mopidy.

        :param uri: the URI to run in mopidy.
        :type uri: string
        '''
        logger.info('Received {} URI.'.format(uri))
