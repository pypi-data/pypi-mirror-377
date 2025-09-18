
# coding: utf-8
from PySide6.QtWidgets import QTabWidget, QWidget, QDockWidget, QApplication, QMainWindow, QPushButton, QTabBar, QVBoxLayout, QStackedWidget, QLabel, QSplitter
from PySide6.QtGui import QCloseEvent, QResizeEvent, QIcon, QAction
from PySide6.QtCore import QEvent, Qt, Signal, QSize, QCoreApplication, QTimer, SignalInstance, QObject
from ..style import Styles
from typing import Callable
from ..notification import Notification

class CustomDockWidget(QDockWidget):
    def resizeEvent(self, a0: QResizeEvent) -> None:   
        try:
            if Notification.currentWidget and Notification.currentWidget.isVisible() and Notification.currentWidget.parentWidget() == self:
                Notification.currentWidget.center_notification()
        except Exception as ex:
            print('QDockWidget resizeEvent', ex)
        return super().resizeEvent(a0)
        
    def moveEvent(self, event):
        super().moveEvent(event)
        if Notification.currentWidget and Notification.currentWidget.isVisible() and Notification.currentWidget.parentWidget() == self:
            Notification.currentWidget.center_notification()
        
    def changeEvent(self, event):
        if event.type() == event.Type.WindowStateChange:
            try:
                if self.isMinimized() and Notification.currentWidget and Notification.currentWidget.isVisible() and Notification.currentWidget.parentWidget() == self:
                    Notification.currentWidget.pause_timer()

                elif not self.isMinimized() and Notification.currentWidget and not Notification.currentWidget.is_hidden:
                    Notification.currentWidget.resume_timer()
            except Exception as ex:
                print(ex)

        return super().changeEvent(event)

    def closeEvent(self, event):
        if Notification.currentWidget and Notification.currentWidget.isVisible() and Notification.currentWidget.parentWidget() == self:
            Notification.currentWidget._close()
         
        return super().closeEvent(event)

class WidgetVisibilityWatcher(QObject):

    def __init__(self, widget: QWidget):
        super().__init__(widget)
        self.widget = widget
        self.widget.installEventFilter(self) 

    def eventFilter(self, obj, event : QEvent):
        if obj == self.widget and event.type() == QEvent.Type.Show:
            self.widget.showing.emit()  
        return super().eventFilter(obj, event)

class TabWidgetDock(CustomDockWidget):
    resized = Signal()
    detached = Signal()
    reattached = Signal()
    detaching = Signal()
    reattaching = Signal()
    
    initialized = Signal()

    class StyleSheet(Styles.Standard.StyleSheet):
        def __init__(self):
            super().__init__()
           
        def style(self):
            return Styles.standard()

    class TitleWidget(QWidget):
        def __init__(self, dock_widget : QDockWidget, parent=None):
            super().__init__(parent)
            self.dock = dock_widget

    def __init__(self, *, tabWidget : QTabWidget, widget_callable: Callable[[], QWidget] | QWidget,  tab_title : str, doc_title : str, icon_data : Styles.Resources.Data , insert_position : int | None = None, delete_enabled = False, show_loading = True):
        super().__init__(doc_title)
        tabWidget.setIconSize(QSize(20, 20))
        self.tab = QWidget()
        self._widget_callable = widget_callable
        self.loaded = not isinstance(widget_callable, Callable)

        self.tab_title = tab_title
        self.icon = icon_data.callable_icon() 
        self.setWindowIcon(icon_data.hover_callable_icon())
        self.icon_data = icon_data
        self.tabWidget = tabWidget
        self.delete_enabled = delete_enabled

        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint |  Qt.WindowType.Widget | Qt.WindowType.WindowMinimizeButtonHint |
        Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)

        tab_layout = QVBoxLayout(self.tab)

        tab_layout.addWidget(self)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        icon = icon_data.hover_callable_icon() if tabWidget.count() == 0 else self.icon
        if insert_position != None:
            self.tab_index = self.tabWidget.insertTab(insert_position, self.tab, icon, tab_title)
        else:
            self.tab_index = self.tabWidget.addTab(self.tab, icon, tab_title)

        
        self.setTitleBarWidget(self.TitleWidget(self))
        
        self.installEventFilter(self)

        self.connTabChanged = tabWidget.currentChanged.connect(self.toggle_tab)

        self.add_toggle_button()

        self._show_loading = show_loading and not self.loaded

        if self._show_loading:
            label = QLabel()
            label.setPixmap(Styles.Resources.loading.original().toPixmap(100))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setWidget(label)

        if self.loaded:
            if hasattr(widget_callable, 'detached'):
                self.detached.connect(widget_callable.detached)
            if hasattr(widget_callable, 'reattached'):
                self.reattached.connect(widget_callable.reattached)

            if hasattr(widget_callable, 'showing'):
                if isinstance(widget_callable.showing, SignalInstance):
                    WidgetVisibilityWatcher(widget_callable)
            
            styleSheet = self.StyleSheet()
            if hasattr(widget_callable, 'customStyleSheet'):
                setattr(styleSheet, 'widget_customStyleSheet', widget_callable.customStyleSheet)

            if self.delete_enabled:
                if hasattr(widget_callable, 'delete'):
                    self._btn_delete.clicked.connect(widget_callable.delete)
            Styles.set_widget_style_theme(styleSheet, self)
            self.setWidget(widget_callable)
            self.initialized.emit()
        else:
            Styles.set_widget_style_theme(self.StyleSheet(), self)
            if tabWidget.count() == 1:
                self._load()

    def _load(self):
        if not self.loaded:
            self.loaded = True
            if self._show_loading:
                QCoreApplication.processEvents()
            
            widget = self._widget_callable()

            if hasattr(widget, 'detached'):
                self.detached.connect(widget.detached)
            if hasattr(widget, 'reattached'):
                self.reattached.connect(widget.reattached)

            if hasattr(widget, 'detaching'):
                self.detaching.connect(widget.detaching)
            if hasattr(widget, 'reattaching'):
                self.reattaching.connect(widget.reattaching)

            if hasattr(widget, 'showing'):
                if isinstance(widget.showing, SignalInstance):
                    WidgetVisibilityWatcher(widget)

            styleSheet = self.StyleSheet()
            
            if hasattr(widget, 'customStyleSheet'):
                setattr(styleSheet, 'widget_customStyleSheet', widget.customStyleSheet)

            if self.delete_enabled:
                if hasattr(widget, 'delete'):
                    self._btn_delete.clicked.connect(widget.delete)
            
            Styles.set_widget_style_theme(styleSheet, self)
            self.setWidget(widget)
            self.initialized.emit()

    def activate(self):
        if self.parent() != None:
            self.tabWidget.setCurrentWidget(self.tab)
        else:
            if self.isHidden():
                self.show()
                self.setWindowState((self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
                self.activateWindow()
            else:
                self.setWindowState((self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
                self.activateWindow()
        QTimer.singleShot(2, self._load) if self._show_loading else self._load()

    def update_title(self, tab_title : str, doc_title : str):
        self.tab_title = tab_title
        self.setWindowTitle(doc_title)
        tab_index = self.tabWidget.indexOf(self.tab)
        if tab_index != -1:
            self.tabWidget.setTabText(tab_index, tab_title)
    
    def update_icon_data(self, icon_data : Styles.Resources.Data):
        self.icon_data = icon_data
        self.icon = icon_data.callable_icon()
        self.setWindowIcon(icon_data.hover_callable_icon())
        self.toggle_tab()

    def toggle_tab(self, *args):
        position = self.tabWidget.indexOf(self.tab)
        if position != -1:
            if self.tabWidget.currentWidget() == self.tab:
                self.tabWidget.setTabIcon(position, self.icon_data.hover_callable_icon())
                QTimer.singleShot(2, self._load) if self._show_loading else self._load()
            else:
                self.tabWidget.setTabIcon(position, self.icon_data.callable_icon())

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.resized.emit()
        return super().resizeEvent(a0)

    def resizeConnect(self, func : object):
          self.resized.connect(func)

    def set_enabled_delete(self, enebled : bool):
        index = self.tabWidget.indexOf(self.tab)
        self.delete_enabled = enebled
        if self.parent() != None:
            if enebled:
                self._btn_delete = QPushButton()
                if hasattr(self.widget(), 'delete') and self.loaded:
                    self._btn_delete.clicked.connect(self.widget().delete)
                self._btn_delete.setIconSize(QSize(14, 14))
                self._btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
                Styles.set_icon(self._btn_delete, Styles.Resources.lixo.gray, Styles.Resources.lixo.original)
                self.tabWidget.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, self._btn_delete)
            else:
                self._btn_delete = self.tabWidget.tabBar().tabButton(index, QTabBar.ButtonPosition.RightSide)
                if self._btn_delete:
                    self._btn_delete.setParent(None) 

    def add_toggle_button(self):
        index = self.tabWidget.indexOf(self.tab)
        if self.delete_enabled:
            self._btn_delete = QPushButton()
            if hasattr(self.widget(), 'delete') and self.loaded:
                self._btn_delete.clicked.connect(self.widget().delete)
            self._btn_delete.setIconSize(QSize(14, 14))
            self._btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
            Styles.set_icon(self._btn_delete, Styles.Resources.lixo.gray, Styles.Resources.lixo.original)
            self.tabWidget.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, self._btn_delete)
           
        btn_maximize = QPushButton()
        btn_maximize.setIconSize(QSize(14, 14))
        btn_maximize.setCursor(Qt.CursorShape.PointingHandCursor)

        Styles.set_icon(btn_maximize, Styles.Resources.maximize.gray, Styles.Resources.maximize.theme)
        btn_maximize.clicked.connect(self.toggle_dock)
        self.tabWidget.tabBar().setTabButton(index, QTabBar.ButtonPosition.LeftSide, btn_maximize)

    def mainWindow(self) -> QMainWindow:
        app = QApplication.instance()
    
        if not app:
            return None
        
        if isinstance(app, QMainWindow):
            return widget
        
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget

    def center(self):
        # Obtém a tela onde a janela atual está sendo exibida
        mainWindow = self.mainWindow()
        current_screen = QApplication.screenAt(mainWindow.geometry().center())
        
        if current_screen is None:
            # Se a tela não for encontrada, usa a tela primária como fallback
            current_screen = QApplication.primaryScreen()

        # Obtém a geometria da tela onde a janela está sendo exibida
        screen_geometry = current_screen.geometry()

        # Calcula as coordenadas X e Y para centralizar a janela
        x = (screen_geometry.width() - self.width()) // 2 + screen_geometry.x()
        y = (screen_geometry.height() - self.height()) // 2 + screen_geometry.y()

        # Move a janela para a posição central na tela correta
        self.move(x, y)

    def toggle_dock(self):
        if self.parent() != None:
            self.removeDock()
        else:
            self.restoreDock()
     
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.NonClientAreaMouseButtonDblClick:
            return True
        return super().eventFilter(obj, event)

    def removeDock(self):
        self.detaching.emit()
        self.setParent(None)
        index = self.tabWidget.indexOf(self.tab)
        if index != -1:  # Verifica se a tab foi encontrada
            self.tabWidget.removeTab(index) 
            self.show()
        self.detached.emit()
        QTimer.singleShot(2, self._load) if self._show_loading else self._load()

    def restoreDock(self):
        self.reattaching.emit()
        self.tab.layout().addWidget(self)
        self.tabWidget.insertTab(self.tab_index, self.tab, self.icon, self.tab_title)
        self.add_toggle_button()
        self.reattached.emit()
        self.show()

    def show(self):
        self.resize(1200, 700)
        self.center()
        return super().show()
        
    def closeEvent(self, event: QCloseEvent) -> None:
        self.restoreDock()
        event.ignore()

    def deleteLater(self) -> None:
        self.tab.setParent(None)
        self.tab.deleteLater()
        self.tabWidget.disconnect(self.connTabChanged)
        return super().deleteLater()
    
class StackedWidgetDock(CustomDockWidget):
    resized = Signal()
    detached = Signal()
    reattached = Signal()
    detaching = Signal()
    reattaching = Signal()

    class StyleSheet(Styles.Standard.StyleSheet):
        def __init__(self):
            super().__init__()

        def style(self):
            return Styles.standard()

    class TitleWidget(QWidget):
        def __init__(self, dock_widget : QDockWidget, parent=None):
            super().__init__(parent)
            self.dock = dock_widget

   
    def __init__(self, *, stackedWidget : QStackedWidget, widget : QWidget, btn_maximize : QPushButton, doc_title : str, icon : QIcon):
        super().__init__(doc_title)

        self.page = QWidget()
        self.btn_maximize = btn_maximize
        self.btn_maximize.setCursor(Qt.CursorShape.PointingHandCursor)
        Styles.set_icon(self.btn_maximize, Styles.Resources.maximize.gray, Styles.Resources.maximize.blue)
        self.btn_maximize.clicked.connect(self.toggle_dock)

        self.setWindowIcon(icon)
        self.stackedWidget = stackedWidget

        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint |  Qt.WindowType.Widget | Qt.WindowType.WindowMinimizeButtonHint |
        Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)

        self.setWidget(widget)

        page_layout = QVBoxLayout(self.page)

        page_layout.addWidget(self)
        page_layout.setContentsMargins(0, 0, 0, 0)

        self.stackedWidget.addWidget(self.page)

        self.setTitleBarWidget(self.TitleWidget(self))
        self.installEventFilter(self)
        styleSheet = self.StyleSheet()
        if hasattr(widget, 'customStyleSheet'):
            setattr(styleSheet, 'widget_customStyleSheet', widget.customStyleSheet)

        if hasattr(widget, 'detached'):
            self.detached.connect(widget.detached)
        if hasattr(widget, 'reattached'):
            self.reattached.connect(widget.reattached)

        if hasattr(widget, 'detaching'):
            self.detaching.connect(widget.detaching)
        if hasattr(widget, 'reattaching'):
            self.reattaching.connect(widget.reattaching)

        if hasattr(widget, 'showing'):
            if isinstance(widget.showing, SignalInstance):
                WidgetVisibilityWatcher(widget)

        Styles.set_widget_style_theme(styleSheet, self)

    def activate(self):
        if self.parent() != None:
            self.stackedWidget.setCurrentWidget(self.page)
        else:
            if self.isHidden():
                self.show()
                self.setWindowState((self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
                self.activateWindow()
            else:
                self.setWindowState((self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
                self.activateWindow()

    def update_title(self,  doc_title : str):
        self.setWindowTitle(doc_title)

    def update_icon_data(self, icon : QIcon):
        self.setWindowIcon(icon)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.resized.emit()
        return super().resizeEvent(a0)

    def resizeConnect(self, func : object):
          self.resized.connect(func)

    def mainWindow(self) -> QMainWindow:
        app = QApplication.instance()
    
        if not app:
            return None
        
        if isinstance(app, QMainWindow):
            return widget
        
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget

    def center(self):
        # Obtém a tela onde a janela atual está sendo exibida
        mainWindow = self.mainWindow()
        current_screen = QApplication.screenAt(mainWindow.geometry().center())
        
        if current_screen is None:
            # Se a tela não for encontrada, usa a tela primária como fallback
            current_screen = QApplication.primaryScreen()

        # Obtém a geometria da tela onde a janela está sendo exibida
        screen_geometry = current_screen.geometry()

        # Calcula as coordenadas X e Y para centralizar a janela
        x = (screen_geometry.width() - self.width()) // 2 + screen_geometry.x()
        y = (screen_geometry.height() - self.height()) // 2 + screen_geometry.y()

        # Move a janela para a posição central na tela correta
        self.move(x, y)

    def isDock(self):
       return self.parent() == None

    def toggle_dock(self):
        if self.isDock():
            self.restoreDock()
        else:
            self.removeDock()
            
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.NonClientAreaMouseButtonDblClick:
            return True
        return super().eventFilter(obj, event)

    def removeDock(self):
        self.detaching.emit()
        self.setParent(None)
        self.btn_maximize.close()
        index = self.stackedWidget.indexOf(self.page)
        if index != -1:  
            self.stackedWidget.removeWidget(self.page) 
            self.show()
        self.detached.emit()
            
    def restoreDock(self):
        self.reattaching.emit()
        self.page.layout().addWidget(self)
        self.btn_maximize.show()
        self.stackedWidget.addWidget(self.page)
        self.reattached.emit()
        self.show()
        QCoreApplication.processEvents()

    def show(self):
        self.resize(1200, 700)
        self.center()
        return super().show()
        
    def closeEvent(self, event: QCloseEvent) -> None:
        self.restoreDock()
        event.ignore()

    def deleteLater(self) -> None:
        self.page.setParent(None)
        self.page.deleteLater()
        return super().deleteLater()
    
class SplitterDock(CustomDockWidget):
    resized = Signal()
    detached = Signal()
    reattached = Signal()
    detaching = Signal()
    reattaching = Signal()

    class StyleSheet(Styles.Standard.StyleSheet):
        def __init__(self):
            super().__init__()

        def style(self):
            return Styles.standard()

    class TitleWidget(QWidget):
        def __init__(self, dock_widget : QDockWidget, parent=None):
            super().__init__(parent)
            self.dock = dock_widget

   
    def __init__(self, *, splitter : QSplitter, widget : QWidget, btn_maximize : QPushButton | QAction, doc_title : str, icon : QIcon, sizes : list = []):
        super().__init__(doc_title)

        self.page = QWidget()
        self.sizes = sizes
        self.btn_maximize = btn_maximize
        
        if isinstance(btn_maximize, QPushButton):
            self.btn_maximize.setCursor(Qt.CursorShape.PointingHandCursor)
            Styles.set_icon(self.btn_maximize, Styles.Resources.maximize.gray, Styles.Resources.maximize.blue)
            self.btn_maximize.clicked.connect(self.toggle_dock)
        elif isinstance(btn_maximize, QAction):
            self.btn_maximize.triggered.connect(self.toggle_dock)
            self.btn_maximize.setIcon(Styles.Resources.maximize.gray())

        self.setWindowIcon(icon)
        self.splitter = splitter
        self.dock_mode = False

        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint |  Qt.WindowType.Widget | Qt.WindowType.WindowMinimizeButtonHint |
        Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)

        self.setWidget(widget)

        page_layout = QVBoxLayout(self.page)

        page_layout.addWidget(self)
        page_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter.addWidget(self.page)

        self.setTitleBarWidget(self.TitleWidget(self))
        self.installEventFilter(self)
        styleSheet = self.StyleSheet()
        if hasattr(widget, 'customStyleSheet'):
            setattr(styleSheet, 'widget_customStyleSheet', widget.customStyleSheet)

        if hasattr(widget, 'detached'):
            self.detached.connect(widget.detached)
        if hasattr(widget, 'reattached'):
            self.reattached.connect(widget.reattached)

        if hasattr(widget, 'detaching'):
            self.detaching.connect(widget.detaching)
        if hasattr(widget, 'reattaching'):
            self.reattaching.connect(widget.reattaching)

        if hasattr(widget, 'showing'):
            if isinstance(widget.showing, SignalInstance):
                WidgetVisibilityWatcher(widget)

        Styles.set_widget_style_theme(styleSheet, self)

    def activate(self):
        if self.parent() == None:
            if self.isHidden():
                self.show()
                self.setWindowState((self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
                self.activateWindow()
            else:
                self.setWindowState((self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
                self.activateWindow()

    def update_title(self,  doc_title : str):
        self.setWindowTitle(doc_title)

    def update_icon_data(self, icon : QIcon):
        self.setWindowIcon(icon)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.resized.emit()
        return super().resizeEvent(a0)

    def resizeConnect(self, func : object):
          self.resized.connect(func)

    def mainWindow(self) -> QMainWindow:
        app = QApplication.instance()
    
        if not app:
            return None
        
        if isinstance(app, QMainWindow):
            return widget
        
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget

    def center(self):
        # Obtém a tela onde a janela atual está sendo exibida
        mainWindow = self.mainWindow()
        current_screen = QApplication.screenAt(mainWindow.geometry().center())
        
        if current_screen is None:
            # Se a tela não for encontrada, usa a tela primária como fallback
            current_screen = QApplication.primaryScreen()

        # Obtém a geometria da tela onde a janela está sendo exibida
        screen_geometry = current_screen.geometry()

        # Calcula as coordenadas X e Y para centralizar a janela
        x = (screen_geometry.width() - self.width()) // 2 + screen_geometry.x()
        y = (screen_geometry.height() - self.height()) // 2 + screen_geometry.y()

        # Move a janela para a posição central na tela correta
        self.move(x, y)

    def isDock(self):
       return self.parent() == None

    def toggle_dock(self):
        if self.isDock():
            self.restoreDock()
        else:
            self.removeDock()
            
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.NonClientAreaMouseButtonDblClick:
            return True
        return super().eventFilter(obj, event)
    
    def removeDock(self):
        self.dock_mode = True
        self.detaching.emit()
        self.setParent(None)
        if isinstance(self.btn_maximize, QPushButton):
            self.btn_maximize.close()
            
        self.page.setParent(None)
        self.show()
        self.detached.emit()
            
    def restoreDock(self):
        self.reattaching.emit()
        self.page.layout().addWidget(self)
        if isinstance(self.btn_maximize, QPushButton):
            self.btn_maximize.show()
        self.splitter.addWidget(self.page)
        if self.sizes:
            self.splitter.setSizes(self.sizes)
        self.reattached.emit()
        self.show()
        QCoreApplication.processEvents()
        self.dock_mode = False

    def show(self):
        self.resize(1200, 700)
        self.center()
        return super().show()
        
    def closeEvent(self, event: QCloseEvent) -> None:
        self.restoreDock()
        event.ignore()

    def deleteLater(self) -> None:
        self.page.setParent(None)
        self.page.deleteLater()
        return super().deleteLater()
