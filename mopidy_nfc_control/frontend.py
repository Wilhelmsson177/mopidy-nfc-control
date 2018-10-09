import logging

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

        logger.info(__logprefix__ +
                    'Successfully initialized NfcControl frontend plugin.')

    def on_start(self):
        self.nfcTagMonitor = NfcTagMonitor()

        self.nfcTagMonitor.RegisterNewUriCallback(self.PlaybackonUri)
        self.nfcTagMonitor.RegisterNewTextCallback(self.Control)
        self.nfcTagMonitor.RegisterTagLostCallback(self.TagRemoved)

        logger.info(__logprefix__ + 'Start nfcTagMonitor in new thread')
        self.nfcTagMonitor.daemon = True
        try:
            self.nfcTagMonitor.start()
            logger.info(__logprefix__ + 'Should have been started')
        except:
            traceback.print_exc()

    def on_stop(self):
        logger.info(__logprefix__ + 'NfcTagMonitor thread stopped.')
        self.nfcTagMonitor.cancel()

    def TagRemoved(self):
        logger.debug(__logprefix__ + 'Tag has been removed')
        self.core.PlaybackController.stop()

    def Control(self, input=None):
        logger.info(__logprefix__ + 'Received {} control.'.format(input))

    def PlaybackonUri(self, uri):
        '''
        Play the given uri on mopidy.

        :param uri: the URI to run in mopidy.
        :type uri: string
        '''
        logger.info('Received {} URI.'.format(uri))
        self.core.TracklistController.clear()
	    self.core.TracklistController.add(None, None, uri, None)
        self.core.PlaybackController.play()
