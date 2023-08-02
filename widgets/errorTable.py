import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from ..messages.message import Message
from ..postgresql import Postgresql
import textwrap
import json
from .expandCell import ExpandCell

class ErrorTable(QtWidgets.QDialog):
    
    def __init__(self, 
            parent=None,
            message=Message()
        ):
        super(ErrorTable, self).__init__(parent=parent)
        uic.loadUi(self.getUIPath(), self)
        self.message = message
        self.tableWidget.horizontalHeader().sortIndicatorOrder()
        self.tableWidget.setSortingEnabled(True)
        self.loadDataBtn.clicked.connect(self.fetchDataByDate)
        self.setWindowTitle('Bug Report')
        self.hiddenColumns([0])
        self.postgresql = Postgresql()
        self.setup()
        self.fetchDataByDate()
        self.showFixedCbx.stateChanged.connect(lambda state: self.fetchDataByDate())
        
    def getUIPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'errorTable.ui'
        )

    def setup(self):
        self.startDe.setDate(QtCore.QDate.currentDate())
        self.endDe.setDate(QtCore.QDate.currentDate())

    def fetchDataByDate(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        data = self.postgresql.getErrorsByDate(
            self.startDe.dateTime().toTime_t(),
            self.endDe.dateTime().toTime_t()
        )
        if not self.showFixedCbx.isChecked():
            data = [ d for d in data if not d[9] ]
        self.addRows(data)
        QtWidgets.QApplication.restoreOverrideCursor()

    def addRows(self, data):
        self.clearAllItems()
        for row in data:
            self.addRow(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9]
            )
        self.adjustColumns()

    def addRow(
            self,
            rowId,
            mac,
            user,
            datatime,
            errorType,
            description,
            versionQgis,
            SO,
            pluginVersion,
            fixed
        ):
        idx = self.getRowIndex(rowId)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(rowId))
        self.tableWidget.setCellWidget(idx, 1, self.createFixLabel('Sim' if fixed else 'Não', idx, 1))
        self.tableWidget.setCellWidget(idx, 2, self.createExpandLabel(description, idx, 2))
        self.tableWidget.setCellWidget(idx, 3, self.createLabel(user, idx, 3))
        self.tableWidget.setCellWidget(idx, 4, self.createLabel(str(datatime), idx, 4))
        self.tableWidget.setCellWidget(idx, 5, self.createLabel(errorType, idx, 5))
        self.tableWidget.setCellWidget(idx, 6, self.createLabel(versionQgis, idx, 6))
        self.tableWidget.setCellWidget(idx, 7, self.createLabel(pluginVersion, idx, 7))
        self.tableWidget.setCellWidget(idx, 8, self.createLabel(SO, idx, 8))
        self.tableWidget.setCellWidget(idx, 9, self.createLabel(mac, idx, 9))

    def getRowIndex(self, rowId):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    rowId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        return self.tableWidget.model().index(rowIndex, 0).data()

    def hiddenColumns(self, columns):
        [ self.tableWidget.setColumnHidden(idx, True) for idx in columns ]

    def hiddenTableColumns(self, tableWidget, columns):
        [ tableWidget.setColumnHidden(idx, True) for idx in columns ]
    
    def getRowIndex(self, rowId):
        if not rowId:
            return -1
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    rowId == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def createToolButton(self, tableWidget, tooltip, iconPath ):
        button = QtWidgets.QPushButton('', tableWidget)
        button.setToolTip( tooltip )
        button.setIcon(QtGui.QIcon( iconPath ))
        button.setFixedSize(QtCore.QSize(25, 25))
        button.setIconSize(QtCore.QSize(20, 20))
        return button

    def getEditIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'edit.png'
        )

    def getDeleteIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'icons',
            'trash.png'
        )

    def createRowEditWidget(self, 
            tableWidget, 
            row, 
            col, 
            editCallback, 
            deleteCallback
        ):
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        index = QtCore.QPersistentModelIndex(tableWidget.model().index(row, col))

        editBtn = self.createToolButton( tableWidget, 'Editar', self.getEditIconPath() )
        editBtn.clicked.connect(
            lambda *args, index=index: editCallback(index)
        )
        layout.addWidget(editBtn)

        deleteBtn = self.createToolButton( tableWidget, 'Deletar', self.getDeleteIconPath() )
        deleteBtn.clicked.connect(
            lambda *args, index=index: deleteCallback(index)
        )
        layout.addWidget(deleteBtn)

        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def getSelectedRowData(self):
        rowsData = []
        for item in self.tableWidget.selectionModel().selectedRows():
            rowsData.append( self.getRowData(item.row()) )
        return rowsData

    def getAllTableData(self):
        rowsData = []
        for idx in range(self.tableWidget.rowCount()):
            rowsData.append( self.getRowData(idx) )
        return rowsData

    def validateValue(self, value):
        if value is None:
            return ''
        return str(value)

    def createNotEditableItem(self, value):
        item = QtWidgets.QTableWidgetItem(self.validateValue(value))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        return item

    def createNotEditableItemNumber(self, value):
        item = QtWidgets.QTableWidgetItem()
        item.setData(QtCore.Qt.DisplayRole, value)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        return item
    
    def createEditableItem(self, value):
        item = QtWidgets.QTableWidgetItem(self.validateValue(value))
        return item

    def createLabel(self, text, row, col):
        #self.tableWidget.setItem(row, col, SortLabelTableWidgetItem())
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        wrapper = textwrap.TextWrapper(width=40)
        te = QtWidgets.QLabel()
        te.setText('\n'.join(wrapper.wrap(text=text)))
        layout.addWidget(te)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def createExpandLabel(self, text, row, col):
        #self.tableWidget.setItem(row, col, SortLabelTableWidgetItem())
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        wrapper = textwrap.TextWrapper(width=40)
        te = QtWidgets.QLabel()
        te.setText('\n'.join(wrapper.wrap(text=text)))
        layout.addWidget(te)
        btn = self.createToolButton(
            self.tableWidget, 
            'Ver', 
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                '..',
                'icons',
                'glass.png'
            )
        )
        btn.clicked.connect(lambda b, text=text: self.expandText(text))
        layout.addWidget(btn)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def expandText(self, text):
        dlg = ExpandCell(text)
        dlg.exec_()

    def createFixLabel(self, text, row, col):
        #self.tableWidget.setItem(row, col, SortLabelTableWidgetItem())
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        wrapper = textwrap.TextWrapper(width=40)
        te = QtWidgets.QLabel()
        te.setText('\n'.join(wrapper.wrap(text=text)))
        layout.addWidget(te)
        btn = self.createToolButton(
            self.tableWidget, 
            'Ver', 
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                '..',
                'icons',
                'ok.png'
            )
        )
        btn.clicked.connect(lambda b, row=row: self.fixError(row))
        layout.addWidget(btn)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def fixError(self, row):
        errorId = self.getRowData(row)
        self.postgresql.setFixedError([errorId], True)
        self.showInfo('Aviso', 'Salvo com sucesso!')
        self.fetchDataByDate()

    @QtCore.pyqtSlot(bool)
    def on_deselectBtn_clicked(self, b):
        self.tableWidget.clearSelection()

    @QtCore.pyqtSlot(bool)
    def on_fixSelectionBtn_clicked(self, b):
        errorIds = []
        for item in self.tableWidget.selectionModel().selectedRows():
            errorIds.append( self.getRowData(item.row()) )
        self.postgresql.setFixedError(errorIds, True)
        self.fetchDataByDate()
        self.showInfo('Aviso', 'Salvo com sucesso!')

    @QtCore.pyqtSlot(str)
    def on_searchLe_textEdited(self, text):
        self.searchRows(text)

    def searchRows(self, text):
        for idx in range(self.tableWidget.rowCount()):
            if text and not self.hasTextOnRow(idx, text):
                self.tableWidget.setRowHidden(idx, True)
            else:
                self.tableWidget.setRowHidden(idx, False)                

    def showError(self, title, message):
        errorMessageBox = self.message.createMessage('ErrorMessageBox')
        errorMessageBox.show(self, title, message)

    def showInfo(self, title, message):
        infoMessageBox = self.message.createMessage('InfoMessageBox')
        infoMessageBox.show(self, title, message)

    def showQuestion(self, title, message):
        questionMessageBox = self.message.createMessage('QuestionMessageBox')
        return questionMessageBox.show(self, title, message)

    def clearAllTableItems(self, tableWidget):
        tableWidget.setRowCount(0)
    
    def adjustColumns(self):
        self.tableWidget.resizeColumnsToContents()

    def adjustRows(self):
        self.tableWidget.resizeRowsToContents()

    def adjustTable(self):
        self.adjustColumns()
        self.adjustRows()

    def removeSelected(self):
        while self.tableWidget.selectionModel().selectedRows() :
            self.tableWidget.removeRow(self.tableWidget.selectionModel().selectedRows()[0].row())

    def hasTextOnRow(self, rowIdx, text):
        for colIdx in self.getColumnsIndexToSearch():
            cellText = self.tableWidget.model().index(rowIdx, colIdx).data()
            if cellText and text.lower() in cellText.lower():
                return True
        return False

    def closeEvent(self, e):
        self.closeChildren(QtWidgets.QDialog)
        super().closeEvent(e)

    def closeChildren(self, typeWidget):
        [ d.close() for d in self.findChildren(typeWidget) ]

    def createCombobox(self, row, col, mapValues, currentValue, handle=None ):
        #self.tableWidget.setItem(row, col, SortComboTableWidgetItem())
        wd = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wd)
        combo = QtWidgets.QComboBox(self.tableWidget)
        combo.setFixedSize(QtCore.QSize(200, 30))
        if mapValues:
            for data in mapValues:
                combo.addItem(data['name'], data['value'])
            combo.setCurrentIndex(combo.findData(currentValue))
        if handle:
            index = QtCore.QPersistentModelIndex(self.tableWidget.model().index(row, col))
            combo.currentIndexChanged.connect(
                lambda *args, combo=combo, index=index: handle(combo, index)
            )
        layout.addWidget(combo)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        return wd

    def clearAllItems(self):
        self.tableWidget.setRowCount(0)