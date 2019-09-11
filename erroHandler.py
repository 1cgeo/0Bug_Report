from qgis.PyQt.QtWidgets import qApp
from qgis.PyQt.QtCore import QMetaObject, QObject, QSettings, QThread, Qt, pyqtSlot
import traceback, platform, os, uuid
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QThread
from qgis.PyQt.QtWidgets import QPushButton, QApplication
from qgis.core import Qgis, QgsMessageLog, qgsfunction, QgsMessageOutput
from qgis.gui import QgsMessageBar
from qgis.utils import iface, plugins
from configparser import ConfigParser
import datetime
import os
import sys
import traceback
import glob
import os.path
import warnings
import codecs
import time
import functools

from .postgresql import Postgresql

class ErroHandler(object):

    @staticmethod
    def show_message_log(pop_error=True):
        if pop_error:
            iface.messageBar().popWidget()

        iface.openMessageLog()

    @staticmethod
    def open_stack_dialog(etype, value, tb, msg, pop_error=True):
        if pop_error and iface is not None:
            iface.messageBar().popWidget()

        if msg is None:
            msg = QCoreApplication.translate('Python', 'An error has occurred while executing Python code:')

        # TODO Move this to a template HTML file
        txt = u'''<font color="red"><b>{msg}</b></font>
        <br>
        <h3>{main_error}</h3>
        <pre>
        {error}
        </pre>
        <br>
        <b>{version_label}</b> {num}
        <br>
        <b>{qgis_label}</b> {qversion} {qgisrelease}, {devversion}
        <br>
        <h4>{pypath_label}</h4>
        <ul>
        {pypath}
        </ul>'''

        error = ''
        lst = traceback.format_exception(etype, value, tb)
        for s in lst:
            error += s.decode('utf-8', 'replace') if hasattr(s, 'decode') else s
        error = error.replace('\n', '<br>')

        main_error = lst[-1].decode('utf-8', 'replace') if hasattr(lst[-1], 'decode') else lst[-1]

        version_label = QCoreApplication.translate('Python', 'Python version:')
        qgis_label = QCoreApplication.translate('Python', 'QGIS version:')
        pypath_label = QCoreApplication.translate('Python', 'Python Path:')
        txt = txt.format(msg=msg,
                        main_error=main_error,
                        error=error,
                        version_label=version_label,
                        num=sys.version,
                        qgis_label=qgis_label,
                        qversion=Qgis.QGIS_VERSION,
                        qgisrelease=Qgis.QGIS_RELEASE_NAME,
                        devversion=Qgis.QGIS_DEV_VERSION,
                        pypath_label=pypath_label,
                        pypath=u"".join(u"<li>{}</li>".format(path) for path in sys.path))

        txt = txt.replace('  ', '&nbsp; ')  # preserve whitespaces for nicer output

        dlg = QgsMessageOutput.createMessageOutput()
        dlg.setTitle(msg)
        dlg.setMessage(txt, QgsMessageOutput.MessageHtml)
        dlg.showMessage()

    @staticmethod
    def _showException(etype, value, tb, msg, messagebar=False):
        if msg is None:
            msg = 'An error has occurred while executing Python code:'

        logmessage = ''
        for s in traceback.format_exception(etype, value, tb):
            logmessage += s.decode('utf-8', 'replace') if hasattr(s, 'decode') else s

        title = 'Python error'
        QgsMessageLog.logMessage(logmessage, title)

        try:
            blockingdialog = QApplication.instance().activeModalWidget()
            window = QApplication.instance().activeWindow()
        except:
            blockingdialog = QApplication.activeModalWidget()
            window = QApplication.activeWindow()

        # Still show the normal blocking dialog in this case for now.
        if blockingdialog or not window or not messagebar or not iface:
            ErroHandler.open_stack_dialog(etype, value, tb, msg)
            return

        bar = iface.messageBar() if iface else None

        # If it's not the main window see if we can find a message bar to report the error in
        if not window.objectName() == "QgisApp":
            widgets = window.findChildren(QgsMessageBar)
            if widgets:
                # Grab the first message bar for now
                bar = widgets[0]

        item = bar.currentItem()
        if item and item.property("Error") == msg:
            # Return of we already have a message with the same error message
            return

        widget = bar.createMessage(title, msg + " " + "See message log (Python Error) for more details.")
        widget.setProperty("Error", msg)
        stackbutton = QPushButton("Stack trace", pressed=functools.partial(ErroHandler.open_stack_dialog, etype, value, tb, msg))
        button = QPushButton("View message log", pressed=ErroHandler.show_message_log)
        widget.layout().addWidget(stackbutton)
        widget.layout().addWidget(button)
        bar.pushWidget(widget, Qgis.Warning)

    @staticmethod
    def get_plugins_versions():
        plugins_versions = ''
        for name, plugin in plugins.items():
            try:
                metadata_path = os.path.join(
                    plugin.plugin_dir,
                    'metadata.txt'
                )
                with open(metadata_path) as mf:
                    cp = ConfigParser()
                    cp.readfp(mf)
                    plugins_versions += "{0} : {1}\n".format(name, cp.get('general', 'version'))
            except:
                pass
        return plugins_versions

    @staticmethod
    def showException(etype, value, tb, msg, *args, **kwargs):
        erro_type = etype.__name__
        description = ''
        for s in traceback.format_exception(etype, value, tb):
            description += s
        description += "{}\n".format(value)
        if platform.system() == 'Linux':
            user = os.environ['USER'] 
        else:
            user = os.environ['USERNAME'] 
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> d) & 0xff) for d in range(0,8*6,8)][::-1]).upper()
        qgis_version = Qgis.QGIS_VERSION
        operational_system = platform.platform()
        current_timestamp = datetime.datetime.now()
        plugins_versions = ErroHandler.get_plugins_versions()
        Postgresql().save_erro(
            mac, 
            user, 
            current_timestamp, 
            erro_type, 
            description, 
            qgis_version, 
            operational_system, 
            plugins_versions
        )
        ErroHandler._showException(etype, value, tb, msg, True)

    
            
    