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
        self.core.playback.stop()

    def Control(self, control=None):
        logger.info(__logprefix__ + 'Received {} control.'.format(control))

    def PlaybackonUri(self, uri):
        '''
        Play the given uri on mopidy.

        :param uri: the URI to run in mopidy.
        :type uri: string
        '''
        logger.info("{}Received URI: {}".format(__logprefix__, uri))
        self.core.tracklist.clear()
        tracks = self.core.tracklist.add(uris=uri)
        logger.debug("{}Received tracks: {}".format(__logprefix__, tracks.get()))
        tl_track = self.core.tracklist.get_tl_tracks().get()[0]
        logger.debug("{}Newest track: {}".format(__logprefix__, tl_track))
        self.core.playback.play(tl_track)
        logger.debug("{}State: {}".format(__logprefix__, self.core.playback.get_state().get()))
