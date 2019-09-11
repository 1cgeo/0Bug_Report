from .erroHandler import ErroHandler
from qgis import utils
import os

class Main(object):
    def __init__(self, iface):
        self.plugin_dir = os.path.dirname(__file__)
        self.bkp_show_exception = None
        self.custom_show_exception = ErroHandler.showException

    def initGui(self):
        self.bkp_show_exception = utils.showException
        utils.showException = self.custom_show_exception

    def unload(self):
        utils.showException = self.bkp_show_exception