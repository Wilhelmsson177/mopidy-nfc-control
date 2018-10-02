import logging
import traceback
from thread import start_new_thread

import time

from mopidy import core

import pykka

from NfcTagMonitor import NfcTagMonitor

logger = logging.getLogger(__name__)



class NfcControl(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(NfcControl, self).__init__()
        self.core = core
        logger.info('Successfully initialized NfcControl frontend plugin.')
        self.nfcTagMonitor = NfcTagMonitor()
        self.nfcTagMonitor.RegisterControlTagCallback(self.Control)
        self.nfcTagMonitor.RegisterUriTagCallback(self.PlaybackonUri)
        self.nfcTagMonitor.RegisterNfcTagRemovedCallback(self.TagRemoved)
        start_new_thread(self.nfcTagMonitor.Run,())

    def TagRemoved(self):
        logger.debug('Tag has been removed')
    
    def Control(self, input=None):
        logger.info('Received {} control.'.format(input))

    def PlaybackonUri(self, uri):
        '''
        Play the given uri on mopidy.

        :param uri: the URI to run in mopidy.
        :type uri: string
        '''
        logger.info('Received {} URI.'.format(uri))
        pass

