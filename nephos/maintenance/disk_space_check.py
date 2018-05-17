import shutil
import pydash
from logging import getLogger

log = getLogger(__name__)


class DiskSpaceCheck:

    def __init__(self, config):

        self.min_space = pydash.get(config.maintenance_config, "")
