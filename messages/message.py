from .htmlMessageDialog  import HtmlMessageDialog
from .infoMessageBox  import InfoMessageBox
from .errorMessageBox  import ErrorMessageBox
from .questionMessageBox  import QuestionMessageBox

class Message:

    def createMessage(self, messageType):
        messageTypes = {
            'HtmlMessageDialog': HtmlMessageDialog,
            'InfoMessageBox': InfoMessageBox,
            'ErrorMessageBox': ErrorMessageBox,
            'QuestionMessageBox': QuestionMessageBox

        }
        return messageTypes[messageType]()