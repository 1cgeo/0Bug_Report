from .erroHandler import ErroHandler
from qgis import utils
from qgis.utils import iface
import os
from PyQt5 import QtWidgets, QtGui
from .widgets.errorTable import ErrorTable


class Main(object):
    def __init__(self, iface):
        self.plugin_dir = os.path.dirname(__file__)
        self.bkp_show_exception = None
        self.custom_show_exception = ErroHandler.showException
        self.errorTableAction = None

    def initGui(self):
        self.bkp_show_exception = utils.showException
        utils.showException = self.custom_show_exception
        self.errorTableAction = self.createAction(
            'Bug Report',
            os.path.join(
                os.path.abspath(os.path.join(
                    os.path.dirname(__file__)
                )),
                'icons',
                'bug.png'
            ),
            self.showErrorTable
        )
        self.addActionDigitizeToolBar(self.errorTableAction)

    def createAction(self, name, iconPath, callback):
        a = QtWidgets.QAction(
            QtGui.QIcon(iconPath),
            name,
            iface.mainWindow()
        )
        a.triggered.connect(callback)
        return a

    def showErrorTable(self):
        self.errorTableDlg = ErrorTable()
        self.errorTableDlg.show()
        
    def addActionDigitizeToolBar(self, action):
        iface.digitizeToolBar().addAction(action)

    def removeActionDigitizeToolBar(self, action):
        iface.digitizeToolBar().removeAction(action)

    def unload(self):
        utils.showException = self.bkp_show_exception
        self.removeActionDigitizeToolBar(self.errorTableAction)