# coding: utf-8
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout
from ...style import Styles
from ...menu import Menu
from .utils import ClickFilter
from ..resizeLabel import ResizeLabel

CLICK_FILTER = ClickFilter()

class CustomMenuUser(Menu):
    
     class CustomWidgetAction(Menu.CustomWidgetAction):

          class StyleSheet(Styles.Standard.StyleSheet):
               def __init__(self):
                         super().__init__()
                         
               def style(self):
                         style = f'''
                         {Styles.standard()}
                         #FrameFooter {{ border-top: 1px solid {Styles.Color.division.horizontal_gradient([0, 0.1, 0.9, 1])}; border-top-right-radius: 0px; border-top-left-radius: 0px;}}
                         {Styles.button(prefix="#BtnLogOut").styleSheet(use_class_name=False)}
                         '''
                         return style

          signal_log_out = Signal()
          def __init__(self):
               super().__init__(None)
               layout = QVBoxLayout()
               layout.setContentsMargins(5,5,5,5)
               layout.setSpacing(5)

               self.resizeLabel = ResizeLabel(use_markdown=True)

               frame_footer = QFrame()
               frame_footer.setObjectName("FrameFooter")
               layout_footer = QVBoxLayout(frame_footer)
               layout_footer.setContentsMargins(0, 5, 0, 0)

               btn_log_out = QPushButton(" Log-out")
               btn_log_out.setObjectName('BtnLogOut')
               btn_log_out.clicked.connect(self.signal_log_out.emit)
               #Styles.set_icon(btn_log_out, Styles.Resources.entrar_sair.gray, Styles.Resources.entrar_sair.theme)
               layout_footer.addWidget(btn_log_out)

               layout.addWidget(self.resizeLabel)
               layout.addWidget(frame_footer)
    
               widget = QFrame()
               widget.setLayout(layout)
               widget.installEventFilter(CLICK_FILTER)
               Styles.set_widget_style_theme(self.StyleSheet(), widget)
               self.setDefaultWidget(widget)

          def set_data_user(self, user_name : str, user_id : str):
               html_text = f"""
               <ul>
                    <li style='white-space: nowrap;'><span style="font-weight: 600;">Id:</span> {user_id}</li>
                    <li><span style="font-weight: 600;">User Name:</span> {user_name}</li>
               </ul>
               """
          
               self.resizeLabel.setText(html_text, True)

     def __init__(self, widget : QPushButton):
          super().__init__(widget)
          self.customWidgetAction = self.CustomWidgetAction()
          self.addAction(self.customWidgetAction)
          widget.clicked.connect(self.show_top_right)
          Styles.set_widget_style_theme(Styles.menu(), self)
          self.customWidgetAction.signal_log_out.connect(self.close)

     def set_data_user(self, user_name : str, user_id : str):
          self.customWidgetAction.set_data_user(user_name, user_id)