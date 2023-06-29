import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from ..messages.message import Message
from ..postgresql import Postgresql
import textwrap

class ExpandCell(QtWidgets.QDialog):
    
    def __init__(self, 
            text,
            parent=None,
            message=Message()
        ):
        super(ExpandCell, self).__init__(parent=parent)
        uic.loadUi(self.getUIPath(), self)
        self.setWindowTitle('Erro')
        self.text = text
        
    def getUIPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'expandCell.ui'
        )

    def showEvent(self, event):
        self.textLb.setText(self.text)