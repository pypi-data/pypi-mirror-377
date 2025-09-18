# coding: utf-8
from PySide6.QtWidgets import QFrame, QStackedWidget, QPushButton, QVBoxLayout, QHBoxLayout, QSplitter, QTextBrowser, QTextEdit, QLineEdit
from PySide6.QtCore import Qt, SignalInstance
from .style import Styles

class Frame(object):

    class Expandable:
        def __init__(self, frame: QFrame, stackedWidget: QStackedWidget, btn_toggle: QPushButton, contentsMargins = [0, 0, 0, 0], maximizing : SignalInstance = None, minimizing :  SignalInstance = None):
            self.frame = frame
            self.stackedWidget = stackedWidget
            self.btn_toggle = btn_toggle
            self.originalContentsMargins = frame.layout().contentsMargins()
            self.contentsMargins = contentsMargins
            self.maximizing = maximizing
            self.minimizing = minimizing

            self.page_expand = QFrame()
            self.page_expand.setObjectName('PageToggleExpand')
            layout = QVBoxLayout(self.page_expand)
            layout.setContentsMargins(*self.contentsMargins)
            
            # Detecta o layout ou o splitter do pai
            parent = frame.parentWidget()
            self.parent_widget : QSplitter | QVBoxLayout | QHBoxLayout = parent
            if not isinstance(parent, QSplitter):
                self.parent_widget = parent.layout()
            self.index = self.parent_widget.indexOf(self.frame)
        
            # Conecta o botão ao método toggle
            btn_toggle.clicked.connect(lambda: self.toggle())
            Styles.set_icon(self.btn_toggle, Styles.Resources.full_screen.gray, Styles.Resources.full_screen.blue)
            self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)

        def toggle(self):
            self.btn_toggle.leaveEvent(None)

            if self.page_expand == self.stackedWidget.currentWidget():
                if self.minimizing:
                    self.minimizing.emit()
                Styles.set_icon(self.btn_toggle, Styles.Resources.full_screen.gray, Styles.Resources.full_screen.blue)

                self.page_expand.layout().removeWidget(self.frame)
                self.frame.setParent(None)

                self.parent_widget.insertWidget(self.index, self.frame)

                self.frame.layout().setContentsMargins(self.originalContentsMargins)
                self.stackedWidget.removeWidget(self.page_expand)
                self.page_expand.setParent(None)
            else:
                if self.maximizing:
                    self.maximizing.emit()
                Styles.set_icon(self.btn_toggle, Styles.Resources.exit_full_screen.gray, Styles.Resources.exit_full_screen.blue)

                self.parent_widget.removeWidget(self.frame)
                self.frame.setParent(None)

                self.page_expand.layout().addWidget(self.frame)
                self.frame.layout().setContentsMargins(0,0,0,0)

                self.stackedWidget.addWidget(self.page_expand)
                self.stackedWidget.setCurrentWidget(self.page_expand)

                self.focus_first_input()

        def focus_first_input(self):
            for widget_class in [QTextEdit, QLineEdit, QTextBrowser]:
                widget = self.frame.findChild(widget_class)
                if widget:
                    widget.setFocus()
                    break