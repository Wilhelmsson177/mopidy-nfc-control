import logging
import traceback

from mopidy import core

import pykka

logger = logging.getLogger(__name__)


class NfcControl(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(NfcControl, self).__init__()
        self.core = core