# coding: utf-8
from PySide6.QtCore import QObject, QEvent, QSize, Qt, Signal, SignalInstance
from PySide6.QtWidgets import QPushButton, QWidget, QStackedWidget, QFrame, QLabel, QHBoxLayout, QSizePolicy, QSpacerItem
from typing import Callable
from ...style import Styles
from ..dockWidget import StackedWidgetDock
from typing import Union, Type, TypeVar
from ...threadPool import Processing
from functools import partial

ViewT = TypeVar('ViewT', bound=object)
ControllerT = TypeVar('ControllerT', bound=object)

def create_mvc_instance(
    class_name: str,
    view: Type[ViewT],
    controller: Type[ControllerT],
    *args, **kwargs
) -> Union[ViewT, ControllerT]: 
    def __init__(self, *args, **kwargs):
        view.__init__(self)
        controller.__init__(self, self, *args, **kwargs)
    
    bases = (view, controller)
    DynamicClass = type(class_name, bases, {'__init__': __init__})
    return DynamicClass(*args, **kwargs)

class ClickFilter(QObject):
    action : object = None
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if self.action:
                self.action()
            return True
        return super().eventFilter(obj, event)
    
class FrameStyleSheet(Styles.WidgetStyleSheet):
    def __init__(self, *, selected=False, prefix=""):
        super().__init__(f"{prefix} QFrame")
        self.frame = self.Frame(selected=selected, prefix=prefix)
        self.widget = self.Widget(selected=selected, prefix=prefix)
        self.hoverWidget = self.HoverWidget(selected=selected,prefix=prefix)
        self.hoverLabel = self.HoverLabel(selected=selected,prefix=prefix)

    class Frame(Styles.StyleSheet):
        def __init__(self, *, selected=False, prefix=""):
            super().__init__('QFrame', prefix)
            self.text_align = Styles.Property.TextAlign('left')
            self.font = Styles.Property.FontSegoeUI(12)
            if selected:
                self.color = Styles.Property.Color("#4c94f4")
                self.background_color = Styles.Property.BackgroundColor(Styles.Color.Menu.Button.hover_background.rgba)
                self.border = Styles.Property.Border(radius=6, color=Styles.Color.Menu.Button.hover_border.rgba)
            else:
                self.background_color = Styles.Property.BackgroundColor('transparent')
                self.color = Styles.Property.Color(Styles.Color.Reverse.primary)
                self.border = Styles.Property.Border(radius=6, color='transparent')

    class Widget(Styles.StyleSheet):
        def __init__(self, *, selected=False, prefix=""):
            super().__init__('QFrame QWidget', prefix)
            self.border = Styles.Property.Border(width=0)
            if selected:
                self.color = Styles.Property.Color("#4c94f4")
                self.background_color = Styles.Property.BackgroundColor(Styles.Color.Menu.Button.hover_background.rgba)
            else:
                self.background_color = Styles.Property.BackgroundColor('transparent')
                self.color = Styles.Property.Color(Styles.Color.Reverse.primary)
           
    class HoverWidget(Styles.StyleSheet):
         def __init__(self, *, selected=False, prefix=""):
            super().__init__('QWidget:hover', prefix)
            if selected:
                self.background_color = Styles.Property.BackgroundColor(Styles.Color.Menu.Button.hover_background.rgba)
            else:
                self.background_color = Styles.Property.BackgroundColor(Styles.Color.Menu.Button.pressed_background.rgba)

    class HoverLabel(Styles.StyleSheet):
         def __init__(self, *, selected=False, prefix=""):
            super().__init__('QLabel:hover', prefix)
            if selected:
                self.background_color = Styles.Property.BackgroundColor(Styles.Color.Menu.Button.hover_background.rgba)
            else:
                self.background_color = Styles.Property.BackgroundColor(Styles.Color.Menu.Button.pressed_background.rgba)

class Page(QFrame):
    clicked = Signal()
    initialized = Signal()

    def __init__(self, widget_callable: Callable[[], QWidget] | QWidget, stackedWidget: QStackedWidget, text: str, callable_icon: Callable, selcted_callable_icon: Callable, icon_size=18, expandable : bool = False):
        super().__init__(None)
        self.showing : SignalInstance = None
        self.selected = False
        self.expandable = expandable
        self.loaded = not isinstance(widget_callable, Callable)
        self.widget_callable = widget_callable
        self.stackedWidget = stackedWidget
        self.dynamic_page: QWidget = None
        self.callable_icon = callable_icon
        self.selcted_callable_icon = selcted_callable_icon
        self.icon_size = icon_size
        self._initial_args = ()
        self._initial_kwargs = {}
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5) 

        self.label_icon = QLabel()
        self.label_icon.setFixedSize(38, 36)  
        self.label_icon.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_text = QLabel(text)
        self.label_text.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.label_text.setVisible(False)  

        if self.expandable:
            self.btn_maximize = QPushButton()
            self.btn_maximize.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.btn_maximize.setIconSize(QSize(14, 14))
            self.btn_maximize.setCursor(Qt.CursorShape.PointingHandCursor)
            Styles.set_icon(self.btn_maximize, Styles.Resources.maximize.gray, Styles.Resources.maximize.theme)
            self.btn_maximize.hide()

        self.spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout.addWidget(self.label_icon, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.label_text, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addItem(self.spacer)
        if self.expandable:
            layout.addWidget(self.btn_maximize)

        self.setFixedHeight(36)

        if self.loaded:
            self.dynamic_page = widget_callable
            self._load_page()

    def toggle_icon(self, selcted : bool):
        self.selected = selcted
        if selcted:
            self.label_icon.setPixmap(self.selcted_callable_icon().toPixmap(self.icon_size))
        else:
            self.label_icon.setPixmap(self.callable_icon().toPixmap(self.icon_size))

    def detached(self):
        if self.selected:
            self.stackedWidget.setCurrentIndex(0)
      
    def reattached(self):
        if self.selected:
            self.stackedWidget.setCurrentWidget(self.stackedWidgetDock.page)
        self.btn_maximize.close()

    def _load_page(self):
        if not self.dynamic_page:
            view, controller = self.widget_callable()
            self.dynamic_page = create_mvc_instance('DynamicPage', view, controller, *self._initial_args, **self._initial_kwargs)
        if hasattr(self.dynamic_page, 'showing'):
            if isinstance(self.dynamic_page.showing, SignalInstance):
                self.showing = self.dynamic_page.showing
        if self.expandable:
            self.stackedWidgetDock = StackedWidgetDock(stackedWidget=self.stackedWidget, widget=self.dynamic_page, icon=self.selcted_callable_icon(), doc_title=self.label_text.text(),
                                                                btn_maximize=self.btn_maximize)
            self.stackedWidgetDock.detached.connect(self.detached)
            self.stackedWidgetDock.reattached.connect(self.reattached)
        else:
            self.stackedWidget.addWidget(self.dynamic_page)
        if self.selected:
            if self.expandable:
                self.stackedWidgetDock.activate()
            else:
                self.stackedWidget.setCurrentWidget(self.dynamic_page)
        if self.dynamic_page:
            if self.showing:
                self.showing.emit()
        self.initialized.emit()
      
    def _create_page(self, *args, **kwargs):
        self._initial_args = args
        self._initial_kwargs = kwargs
        Processing(self.widget_callable, callback=self._load_page)
      
    def _show_page(self, *args, **kwargs):
        if not self.loaded:
            self.loaded = True
            self._create_page(*args, **kwargs)
        if self.dynamic_page:
            if self.showing:
                self.showing.emit()
            if self.expandable:
                if self.stackedWidgetDock.isDock():
                    self.stackedWidget.setCurrentIndex(0)
                self.stackedWidgetDock.activate()
            else:
                self.stackedWidget.setCurrentWidget(self.dynamic_page)
        else:
            self.stackedWidget.setCurrentIndex(1)

    def mousePressEvent(self, a0):
        self.clicked.emit()
        return super().mousePressEvent(a0)

    def enterEvent(self, event):
        if self.expandable:
            if self.label_text.isVisible() and self.loaded and not self.stackedWidgetDock.isDock():
                self.btn_maximize.show()
        return super().enterEvent(event)
    
    def leaveEvent(self, a0):
        if self.expandable:
            self.btn_maximize.close()
        return super().leaveEvent(a0)