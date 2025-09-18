from PySide6.QtWidgets import QSizePolicy, QLabel, QPushButton, QHBoxLayout, QWidget, QCheckBox, QComboBox, QWidget, QWidgetAction, QVBoxLayout, QScrollArea, QFrame, QTextEdit
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QMimeData, Signal
from .chat_message import WidgetMessage
from ..style import Styles
from ..comboBox import ComboBox
from .webEngineView import CustomWebEngineView
from .sideBar import SideBar
from .dockWidget import TabWidgetDock, StackedWidgetDock, SplitterDock
from .resizeLabel import ResizeLabel
from .codeEditor import CodeEditor
from .textEditor import TextEditor
from .checkableComboBox import CheckableComboBox
from .menu_textEdit_variables import MenuTextEditVariables

class CustomWidgets(object):

    class Widget(QWidget):
        def __init__(self, *, children : QWidget = None, parent = None):
            super().__init__(parent)
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            if children is not None:
                layout.addWidget(children)
            self.setStyleSheet("background-color: 'transparent';")
            self.setLayout(layout)

    class MenuTextEditVariables(MenuTextEditVariables):
        ...

    class CheckableComboBox(CheckableComboBox):
        ...

    class CodeEditor(CodeEditor):
        ...

    class TextEditor(TextEditor):
        ...

    class StackedWidgetDock(StackedWidgetDock):
        ...

    class TabWidgetDock(TabWidgetDock):
        ...

    class SplitterDock(SplitterDock):
        ...
            
    class SideBar(SideBar):
        ...

    class WebEngineView(CustomWebEngineView):
        ...

    class WidgetMessage(WidgetMessage):
        ...

    class ResizeLabel(ResizeLabel):
        ...

    class ActionDelete(QWidgetAction):
        def __init__(self, parent : object, action_delete : object = None, text = "Delete"):
            super().__init__(parent)
            self.btn_delete = QPushButton(text)
            Styles.set_icon(self.btn_delete, Styles.Resources.lixo.gray, Styles.Resources.lixo.theme)
            Styles.set_widget_style_theme(Styles.button(transparent=True), self.btn_delete)
            self.action_delete = action_delete
            self.btn_delete.clicked.connect(self.delete)
            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.btn_delete)
            widget.setLayout(layout)
            self.setDefaultWidget(widget)

        def delete(self):
            if self.action_delete != None:
             self.action_delete()

    class LabelAndPushButton(QWidget):
        def __init__(self, label_text : str, pushButton_func : object, icon_data : Styles.Resources.Data = None,  parent = None):
            super().__init__(parent)

            self.label = QLabel()
            self.label.setText(label_text)
            self.label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
            self.pushButton = QPushButton()
            self.pushButton.clicked.connect(pushButton_func)

            if icon_data:
                Styles.set_icon(self.pushButton, icon_data.callable_icon, icon_data.hover_callable_icon, icon_data.pixmap_size)
            self.pushButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred))
            layout = QHBoxLayout()
            layout.addWidget(self.label)
            layout.addWidget(self.pushButton)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)

    class IconLabelPushButton(QWidget):
        def __init__(self, text, pushButton_func : object, pushButton_icon_data : Styles.Resources.Data = None, label_icon_data : Styles.Resources.Data = None, icon_size = 16, margins = (0, 0, 0, 0),  parent=None):
            super().__init__(parent)
            self.selected = False
            layout = QHBoxLayout()
            layout.setContentsMargins(*margins)
            self.icon_label = QLabel()
            self.label_text = QLabel()
            self.label_text.setText(text)
            self.label_text.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
            self.icon_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding))
            self.pushButton = QPushButton()
            self.pushButton.setMinimumWidth(40)
            self.pushButton.setSizePolicy( QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding))
            self.pushButton.clicked.connect(pushButton_func)
            self.label_icon_data = label_icon_data
            self.icon_size = icon_size

            if label_icon_data:
                Styles.set_icon(self.icon_label, label_icon_data.callable_icon, label_icon_data.callable_icon, icon_size)
                layout.addWidget(self.icon_label)
    
            if pushButton_icon_data:
                Styles.set_icon(self.pushButton, pushButton_icon_data.callable_icon, pushButton_icon_data.hover_callable_icon, pushButton_icon_data.pixmap_size)
 
            btn_style = Styles.button(transparent=True)
            btn_style.button.border.radius = 2
            Styles.set_widget_style_theme(btn_style, self.pushButton)


            layout.addWidget(self.label_text)
            layout.addWidget(self.pushButton)

            self.setStyleSheet('''
                        background-color: 'transparent';
            ''')

            self.setLayout(layout)

        def SelectionChanged(self, selected : bool):
            if self.label_icon_data:
                if selected != self.selected:
                    self.icon_label.setPixmap(self.label_icon_data.hover_callable_icon().toPixmap() if selected else self.label_icon_data.callable_icon.toPixmap())
            self.selected = selected


    class CheckBoxAndComboBox(QWidget):
        def __init__(self, checkBox_text : str, comboBox_data : ComboBox.DataUpdate, checked : bool = False, checkBox_func : object = None, comboBox_func : object = None, index_comboBox = 0,  parent = None):
            super().__init__(parent)

            self.comboBox = QComboBox()
            ComboBox.update_data(self.comboBox, comboBox_data)
            if comboBox_data.items:
                self.comboBox.setCurrentIndex(index_comboBox)
            self.checkBox = QCheckBox()
            self.checkBox.setText(checkBox_text)
            self.checkBox.setChecked(checked)
            self.checkBox.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
            self.comboBox.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
            
            ComboBox.ignoreWheelEvent(self.comboBox)
        
            if checkBox_func:
                self.checkBox.toggled.connect(checkBox_func)
            if comboBox_func:
                self.comboBox.activated.connect(comboBox_func)

            layout = QHBoxLayout()
            layout.addWidget(self.checkBox)
            layout.addWidget(self.comboBox)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.setLayout(layout)


    class IconLabel(QWidget):
        def __init__(self, text, icon :QIcon = None, icon_data : Styles.Resources.Data = None, icon_size = 16, margins = (0, 0, 0, 0), parent=None):
            super().__init__(parent)
            self.selected = False
            self.icon = icon
            self.icon_data = icon_data
            self.icon_size = icon_size
            layout = QHBoxLayout()
            layout.setContentsMargins(*margins)
            self.icon_label = QLabel()
            self.label_text = QLabel()
            self.label_text.setText(text)
            size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
            self.icon_label.setSizePolicy(size_policy)

            if icon_data:
                Styles.set_icon(self.icon_label, icon_data.callable_icon, icon_data.hover_callable_icon, icon_size)
            elif icon:
                self.update_icon(icon, icon_size)

            layout.addWidget(self.icon_label)
            layout.addWidget(self.label_text)
            self.setStyleSheet('''
                        background-color: 'transparent';
            ''')

            self.setLayout(layout)

        def update_icon(self, icon : QIcon, icon_size = 16):
            if icon:
                pixmap = icon.pixmap(icon_size, icon_size)  # Ajuste o tamanho do �cone conforme necess�rio
                self.icon_label.setPixmap(pixmap)

        def SelectionChanged(self, selected : bool):
            if self.icon_data:
                if selected != self.selected:
                    self.icon_label.setPixmap(self.icon_data.hover_callable_icon().toPixmap() if selected else self.icon_data.callable_icon.toPixmap())
            self.selected = selected


    class StateLabel(QWidget):
        def __init__(self, style = "", size : int = 10, parent=None):
            super().__init__(parent)
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            self.label = QLabel()
            size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.label.setSizePolicy(size_policy)
            layout.addWidget(self.label)
            self.label.setMaximumSize(size, size)
            self.label.setMinimumSize(size, size)
            self.label.setStyleSheet(style)
            self.setStyleSheet('''
                        background-color: 'transparent';
            ''')

            self.setLayout(layout)


    class Label(QLabel):
        def __init__(self, text='', func_double_click = None,  parent=None):
            super().__init__(text, parent)
            self.func_double_click = func_double_click

        def mouseDoubleClickEvent(self, event):
            if self.func_double_click:
                self.func_double_click()


    class IconCheckBox(QWidget):
        def __init__(self, text, icon : QIcon = None, icon_size = 16, margins = [0, 0, 0, 0], spacing : int = None, parent=None):
            super().__init__(parent)
        
            self.margins = margins
            layout = QHBoxLayout()

            self.icon_label = QLabel()
            self.checkbox = QCheckBox(text)
            size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
            self.icon_label.setSizePolicy(size_policy)
            if icon:
                pixmap = icon.pixmap(icon_size, icon_size)  # Ajuste o tamanho do �cone conforme necess�rio
                self.icon_label.setPixmap(pixmap)
                layout.addWidget(self.icon_label)

            if spacing != None:
                layout.setSpacing(0)
            layout.setContentsMargins(*margins)
            layout.addWidget(self.checkbox)
        
            self.setStyleSheet('''
                        background-color: 'transparent';
            ''')

            self.setLayout(layout)

        def setIcon(self, icon : QIcon, icon_size = 16):
            pixmap = icon.pixmap(icon_size, icon_size)  
            self.icon_label.setPixmap(pixmap)
            layout = QHBoxLayout()
            layout.setContentsMargins(*self.margins)
            layout.addWidget(self.icon_label)
            layout.addWidget(self.checkbox)
            self.setLayout(layout)

    class AutoResizingTextEdit(QTextEdit):
        image_pasted  = Signal(object)
        def __init__(self, min_lines=3, max_height : int = None):
            super().__init__()

            self.line_height = 21  # Altura de um QLineEdit
            self.min_height = self.line_height * min_lines  # Altura mínima ajustável
            self.max_height = max_height
            self.setMinimumHeight(self.min_height)
            if max_height:
                self.setMaximumHeight(max_height)  # Define altura máxima para não crescer indefinidamente
                
            
            self.textChanged.connect(self.adjust_height)  # Ajusta altura ao mudar texto
            self.adjust_height()  # Ajusta altura inicial

        def insertFromMimeData(self, source : QMimeData):
            # URLs
            if source.hasUrls():
                for qurl in source.urls():
                    local_path = qurl.toLocalFile()
                    if local_path:
                        self.image_pasted.emit(local_path)
                    else:
                        url_str = qurl.toString()
                        self.image_pasted.emit(url_str)
                           
            # Imagem
            elif source.hasImage():
                image = source.imageData()
                self.image_pasted.emit(image)
            else:
                super().insertFromMimeData(source)

        def showEvent(self, event):
            self.adjust_height()
            return super().showEvent(event)

        def adjust_height(self):
            """
            Ajusta a altura do QTextEdit conforme o conteúdo cresce ou diminui.
            Se estiver vazio, mantém a altura mínima definida.
            """
            doc_height = self.document().size().height() 
            new_height = max(self.min_height, int(doc_height))

            if self.max_height:
                new_height = min(self.max_height, new_height)

            # Desativa atualizações para evitar flickering ou "movimento" no layout
            parent = self.parentWidget()
            if parent:
                parent.setUpdatesEnabled(False)

            self.setFixedHeight(int(new_height))  # Ajusta a altura dinamicamente

            if parent:
                parent.setUpdatesEnabled(True)  # Reativa atualizações

    class VerticalScrollArea(QScrollArea):
        def __init__(self, *, margins = [0,0,0,0], content_margins = [10,10,10,10], spacing = 0, content_spacing = 20,  parent: QWidget = None):
            super().__init__(parent)
            
            # Main content widget
            content_widget = QWidget()
            content_widget_layout = QVBoxLayout(content_widget)
            content_widget_layout.setContentsMargins(*margins)
            content_widget_layout.setSpacing(spacing)
            
            self.setWidget(content_widget)
            self.setWidgetResizable(True)

            # Scroll layout for adding items
            self.scroll_layout = QVBoxLayout()
            self.scroll_layout.setContentsMargins(*content_margins)
            self.scroll_layout.setSpacing(content_spacing)
            self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            # Content frame that holds the layout
            content_frame = QFrame()
            content_frame.setLayout(self.scroll_layout)

            # Add the content frame to the main content widget
            content_widget_layout.addWidget(content_frame)

            # Set minimum height for content frame to prevent extra scroll space
            content_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
           
        def add_item(self, widget : QWidget):
            """
            Adds a new widget to the scroll area layout.
            """
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.scroll_layout.addWidget(widget)

    class HorizontalScrollArea(QScrollArea):
        def __init__(self, *, margins=[0, 0, 0, 0], content_margins=[10, 10, 10, 10],
                spacing=0, content_spacing=20, parent: QWidget = None):
            super().__init__(parent)

            # Main content widget
            content_widget = QWidget()
            content_widget_layout = QHBoxLayout(content_widget)
            content_widget_layout.setContentsMargins(*margins)
            content_widget_layout.setSpacing(spacing)

            self.setWidget(content_widget)
            self.setWidgetResizable(True)

            # Scroll layout for adding items (horizontal)
            self.scroll_layout = QHBoxLayout()
            self.scroll_layout.setContentsMargins(*content_margins)
            self.scroll_layout.setSpacing(content_spacing)
            self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            # Content frame that holds the layout
            content_frame = QFrame()
            content_frame.setLayout(self.scroll_layout)

            # Add the content frame to the main content widget
            content_widget_layout.addWidget(content_frame)

            # Set minimum width for content frame to prevent extra scroll space
            content_frame.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

            # Enable horizontal scroll only
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        def add_item(self, widget: QWidget):
            """
            Adds a new widget to the horizontal scroll area layout.
            """
            widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self.scroll_layout.addWidget(widget)
            


    


