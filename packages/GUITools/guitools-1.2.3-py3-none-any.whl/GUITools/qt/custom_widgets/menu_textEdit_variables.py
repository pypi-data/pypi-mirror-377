from PySide6.QtWidgets import QPushButton, QTextEdit, QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import QObject, QEvent
from pydantic import BaseModel
from typing import Callable
from ..menu import Menu
from ..style import Styles

class ClickFilter(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def eventFilter(self, obj, event):
        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress or event_type == QEvent.Type.MouseButtonDblClick or event_type == QEvent.Type.MouseButtonRelease :
            if isinstance(obj, (QFrame, QLabel)):
                return True
        return super().eventFilter(obj, event)
    
CLICK_FILTER = ClickFilter()

class MenuTextEditVariables(Menu):

     class VariableModel(BaseModel):
          text: str
          variable: str

     class CustomAction(Menu.CustomWidgetAction):

          class StyleSheet(Styles.Standard.StyleSheet):
               def __init__(self):
                    super().__init__()

               def style(self):
                    btn_style = Styles.button()
                    btn_style.button.add_additional_style(f'text-align: left; {Styles.Property.FontSegoeUI(10)}')

                    return f'''
                         {Styles.standard()}
                         QFrame {{{Styles.Property.BackgroundColor(Styles.Color.table)}}}
                         {btn_style}
                         '''
          def __init__(self, callable_close : Callable, textEdit: QTextEdit, variables: list['MenuTextEditVariables.VariableModel'], title : str):
               super().__init__(None)
               self.callable_close = callable_close
               self.textEdit = textEdit
               self.variables = variables
               layout = QVBoxLayout()
               layout.setContentsMargins(5, 5, 5, 5)
               layout.setSpacing(5)

               layout_header = QHBoxLayout()
               layout_header.setContentsMargins(5, 0, 0, 0)
               layout_header.setSpacing(5)
               label_title = QLabel(title)
               label_title.setStyleSheet('font: 63 13pt "Segoe UI Semibold"')
              
               layout.addWidget(label_title)

               for variable in self.variables:
                    btn = QPushButton(variable.text)
                    btn.clicked.connect(lambda _, var=variable: self.insert_variable(var))
                    layout.addWidget(btn)

               widget = QFrame()
               widget.setLayout(layout)
               widget.installEventFilter(CLICK_FILTER)
               Styles.set_widget_style_theme(self.StyleSheet(), widget)
               self.setDefaultWidget(widget)

          def insert_variable(self, variable: 'MenuTextEditVariables.VariableModel'):
               cursor = self.textEdit.textCursor()
               
               if cursor.hasSelection():
                    cursor.insertText(f' {{{variable.variable}}} ')
               else:
                    text_before_cursor = cursor.document().toPlainText()[:cursor.position()]
                    text_after_cursor = cursor.document().toPlainText()[cursor.position():]

                    prefix = ''
                    suffix = ''
                    if text_before_cursor and text_before_cursor[-1] not in (' ', '\n'):
                         prefix = ' '
                    if text_after_cursor and text_after_cursor[0] not in (' ', '\n'):
                         suffix = ' '
                    cursor.insertText(f'{prefix}{{{variable.variable}}}{suffix}')
               
               self.textEdit.setTextCursor(cursor)
               self.callable_close()
             
     def __init__(self, widget: QPushButton, textEdit: QTextEdit, variables: list[VariableModel], title : str = 'Variables'):
          super().__init__(widget)
          widget.clicked.connect(self.show_bottom_right)
          self.customAction = self.CustomAction(self.close, textEdit, variables, title)
          self.addAction(self.customAction)
          Styles.set_widget_style_theme(Styles.menu(), self)