import logging
from threading

from mopidy import core

import pykka

from NfcTagMonitor import NfcTagMonitor

logger = logging.getLogger(__name__)
__logprefix__ = 'NfcControl: '

class NfcControl(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(NfcControl, self).__init__()
        self.core = core
        self.taghold = config['nfc-control']['taghold']
        self.nfcTagMonitor = None
        self.nfcTagMonitorThread = None

        logger.info(__logprefix__ + 'Successfully initialized NfcControl frontend plugin.')

    def on_start(self):
        self.nfcTagMonitor = NfcTagMontor(self.taghold)

        self.nfcTagMonitor.RegisterControlTagCallback(self.Control)
        self.nfcTagMonitor.RegisterUriTagCallback(self.PlaybackonUri)
        self.nfcTagMonitor.RegisterNfcTagRemovedCallback(self.TagRemoved)
        
        self.nfcTagMonitorThread = threading.Thread(target=self.nfcTagMonitor.Run)
        self.nfcTagMonitor.daemon = True

        self.nfcTagMonitorThread.start()
        logger.info(__logprefix__ + 'Start nfcTagMonitor in new thread')

    def on_stop(self):
        logger.info(__logprefix__ + 'NfcTagMonitor thread stopped.')
        self.nfcTagMonitorThread.stop()

    def TagRemoved(self):
        logger.debug(__logprefix__ + 'Tag has been removed')

    def Control(self, input=None):
        logger.info(__logprefix__ + 'Received {} control.'.format(input))

    def PlaybackonUri(self, uri):
        '''
        Play the given uri on mopidy.

        :param uri: the URI to run in mopidy.
        :type uri: string
        '''
        logger.info('Received {} URI.'.format(uri))
        pass
