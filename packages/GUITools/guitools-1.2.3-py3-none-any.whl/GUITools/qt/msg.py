# coding: utf-8

from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtGui import QIcon
from .style import Styles

def clearFocus():
    focused_widget = QApplication.focusWidget()
    if focused_widget:
        focused_widget.clearFocus()

class Msg(object):

    WindowIcon : QIcon = None

    @classmethod
    def get_icon(cls, window_icon : QIcon | None) -> QIcon:
        if not window_icon:
            if cls.WindowIcon:
                return cls.WindowIcon
            return Styles.Resources.mini_logo.original()
        return window_icon

    @staticmethod
    def p_nowrap(text):
        return f"<p style='white-space: nowrap;'> {text} </p>"
        
    @classmethod
    def information(cls, texto : str, texto_2 : str = None, window_icon : QIcon = None):
        clearFocus()
        msg = QMessageBox()
        msg.setWindowTitle('Information')
        msg.setWindowIcon(cls.get_icon(window_icon))
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(texto)
        msg.setInformativeText(texto_2)
        msg.exec()

    @classmethod
    def error(cls, texto : str, texto_2 : str =None, window_icon : QIcon = None):
        clearFocus()
        msg = QMessageBox()
        msg.setWindowTitle('Error')
        msg.setWindowIcon(cls.get_icon(window_icon))
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(texto)
        msg.setInformativeText(texto_2)
        msg.exec()

    @classmethod
    def confirmation(cls, texto_butao_s : str, texto : str, texto_2 : str = None, window_icon : QIcon = None):
        clearFocus()
        msg = QMessageBox()
        msg.setWindowTitle('Information')
        msg.setWindowIcon(cls.get_icon(window_icon))

        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(texto)
        msg.setInformativeText(texto_2)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | 
                         QMessageBox.StandardButton.No)

        buttonN = msg.button(QMessageBox.StandardButton.No)
        buttonS = msg.button(QMessageBox.StandardButton.Yes)
        buttonS.setText(texto_butao_s)
   
        buttonN.setText("Ok")

        resposta = msg.exec()

        if resposta == QMessageBox.StandardButton.Yes:
            return True

    @classmethod
    def choice(cls, texto_butao_s : str, texto : str, texto_2 : str = None, window_icon : QIcon = None):
        clearFocus()
        msg = QMessageBox()
        msg.setWindowTitle('Choice')
        msg.setWindowIcon(cls.get_icon(window_icon))
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(texto)
        msg.setInformativeText(texto_2)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | 
                         QMessageBox.StandardButton.No)

        buttonN = msg.button(QMessageBox.StandardButton.No)
        buttonS = msg.button(QMessageBox.StandardButton.Yes)
        buttonS.setText(texto_butao_s)
        buttonN.setText("Cancel")

        resposta = msg.exec()

        if resposta == QMessageBox.StandardButton.Yes:
            return True


