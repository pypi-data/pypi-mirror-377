# coding: utf-8
from functools import partial
from PySide6.QtWidgets import QFrame, QPushButton, QWidget, QWidgetAction, QTreeWidget, QHBoxLayout, QSizePolicy, QVBoxLayout, QLabel, QHeaderView, QAbstractItemView, QTreeWidgetItem, QMainWindow, QApplication
from ...style import Styles
from ...menu import Menu
from PySide6.QtCore import QSize, Qt,  QCoreApplication,  SignalInstance, QPoint, QTimer
from ...notification import Notification
from ..textEditor import TextEditor
import locale
from datetime import datetime
from ...treeWidget import TreeWidget
from .utils import ClickFilter

CLICK_FILTER = ClickFilter()

class CustomMenuNotification(Menu):

    class CustomWidgetAction(Menu.CustomWidgetAction):
         
        class CustomTreeWidget(TreeWidget):

            class NotificationItem(QFrame):

                class StyleSheet(Styles.Standard.StyleSheet):
                    def __init__(self):
                        super().__init__()

                    def style(self):

                        textBrowser = Styles.textBrowser()
                        textBrowser.textBrowser.background_color.value = Styles.Color.primary
                        textBrowser.scrollBarHorizontal.background_color.value = Styles.Color.primary
                        textBrowser.scrollBarVertical.background_color.value = Styles.Color.primary

                        style = f'''
                            #NotificationItem, #NotificationItem QFrame {{background-color: {Styles.Color.primary}}}
                            {textBrowser}
                        '''

                        return style
                
                def __init__(self, data : Notification.NotificationData,*, parent : QWidget = None):
                    super().__init__(parent=parent)
                    self.setObjectName("NotificationItem")
                    self.data = data
                    layout_header = QHBoxLayout()
                    layout_header.setContentsMargins(5,0,0,0)
                    self.btn_delete = QPushButton()
                    self.btn_delete.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
                    self.btn_delete.setIconSize(QSize(12,12))
                    self.btn_delete.setFixedHeight(20)
                    self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
                    
                    Styles.set_icon(self.btn_delete, Styles.Resources.close.gray, Styles.Resources.close.theme)
                    layout_header.addWidget(self.format_date_label(data.date))
                    layout_header.addWidget(self.btn_delete)

                    layout_main = QVBoxLayout()
                    layout_main.setContentsMargins(5,0,0,0)
                    layout_main.setSpacing(0)
                    label_title = QLabel(data.title)
                    label_title.setStyleSheet('font: 63 12pt "Segoe UI Semibold"')

                    viewer = TextEditor(adjust_height=True, content=data.message, readOnly=True)
                    layout_main.addWidget(label_title)
                    layout_main.addWidget(viewer)

                    layout = QVBoxLayout()
                    layout.setContentsMargins(5,5,5,5)
                    layout.setSpacing(0)
                    layout.addLayout(layout_header)
                    layout.addLayout(layout_main)
                    self.setLayout(layout)
                    self.btn_delete.setVisible(False)

                    Styles.set_widget_style_theme(self.StyleSheet(), self)

            
                def format_date_label(self, date: datetime):

                    locale.setlocale(locale.LC_TIME)

                    today = datetime.now()

                    # Obter a data de hoje sem o componente de tempo
                    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

                    # Truncar a hora da data para garantir que o delta seja apenas em dias
                    formatted_date = date.replace(hour=0, minute=0, second=0, microsecond=0)

                    # Calcular a diferença em dias
                    delta = (today - formatted_date).days

                    if delta == 0:
                        # Data de hoje - exibir apenas as horas
                        self.label_date = QLabel(date.strftime("%H:%M"))
                    elif delta == 1:
                        # Ontem em inglês
                        self.label_date = QLabel("Yesterday")
                    elif 1 < delta <= 7:
                        # No máximo uma semana - nome do dia da semana em inglês
                        self.label_date = QLabel(date.strftime("%A"))
                    else:
                        # Mais de uma semana - apenas a data sem horas
                        self.label_date = QLabel(date.strftime("%Y-%m-%d"))

                    # Definir o estilo
                    self.label_date.setStyleSheet('font: 10pt "Segoe UI"')
                    self.label_date.setFixedHeight(20)
                    return self.label_date
                
                def update_date_label(self):
                    locale.setlocale(locale.LC_TIME)

                    today = datetime.now()

                    # Obter a data de hoje sem o componente de tempo
                    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

                    # Truncar a hora da data para garantir que o delta seja apenas em dias
                    formatted_date = self.data.date.replace(hour=0, minute=0, second=0, microsecond=0)

                    # Calcular a diferença em dias
                    delta = (today - formatted_date).days

                    if delta == 0:
                        # Data de hoje - exibir apenas as horas
                        self.label_date.setText(self.data.date.strftime("%H:%M"))
                    elif delta == 1:
                        # Ontem em inglês
                        self.label_date.setText("Yesterday")
                    elif 1 < delta <= 7:
                        # No máximo uma semana - nome do dia da semana em inglês
                        self.label_date.setText(self.data.date.strftime("%A"))
                    else:
                        # Mais de uma semana - apenas a data sem horas
                        self.label_date.setText(self.data.date.strftime("%Y-%m-%d"))

                def enterEvent(self, event):
                    self.btn_delete.setVisible(True)
                    super().enterEvent(event)

                def leaveEvent(self, event):
                    self.btn_delete.setVisible(False)
                    super().leaveEvent(event)

            def __init__(self,  signal_notification : SignalInstance, signal_delete_notification : SignalInstance, *, parent : QWidget = None):
                super().__init__(scroll_amount=40,parent=parent)
                self.itemClicked.connect(self.toggle_expand)
                Notification.signal_notification = signal_notification
                Notification.signal_notification.connect(self.new_notification)
                self.signal_delete_notification = signal_delete_notification
                self.signal_delete_notification.connect(self.delete_notification)
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_dates)
                thirty_minutes_ms = 30 * 60 * 1000
                self.timer.start(thirty_minutes_ms)
                self.icon_category = Styles.Resources.category.gray()
                self.setColumnCount(1)
                header = self.header()
                header.setVisible(False)
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
                self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
                self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
                self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
                self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

            def update_dates(self):
                notification_items = self.get_all_notification_items()
                for notification in notification_items:
                    notification.update_date_label()

            def get_all_notification_items(self):
                notification_items : list[CustomMenuNotification.CustomWidgetAction.CustomTreeWidget.NotificationItem] = []

                # Itera por todos os itens top-level
                for i in range(self.topLevelItemCount()):
                    top_item = self.topLevelItem(i)

                    # Itera por todos os filhos do top-level
                    for j in range(top_item.childCount()):
                        child_item = top_item.child(j)

                        # Obtém o widget associado à coluna 0
                        widget = self.itemWidget(child_item, 0)
                        if widget:
                            # Procura o NotificationItem dentro do QFrame
                            for k in range(widget.layout().count()):
                                child_widget = widget.layout().itemAt(k).widget()
                                if isinstance(child_widget, self.NotificationItem):
                                    notification_items.append(child_widget)

                return notification_items

            def new_notification(self, data : Notification.NotificationData):
                
                item_local : QTreeWidgetItem = None
                for i in range(self.topLevelItemCount()):
                    top_level_item = self.topLevelItem(i)
                    if top_level_item:
                        if top_level_item.text(0) == data.local:
                            item_local = top_level_item
                if not item_local:
                    item_local = self.add_item_local(data.local)

                self.add_item_widget(item_local, data)
                item_local.setExpanded(True)

            def delete_notification(self, item: QTreeWidgetItem, guid : str):
                parent = item.parent()
                widget = self.itemWidget(item, 0)
                
                if widget:
                    self.removeItemWidget(item, 0)
                    widget.deleteLater()

                if parent:
                    parent.removeChild(item)
                    if parent.childCount() == 0:
                        top_index = self.indexOfTopLevelItem(parent)
                        if top_index != -1:
                            self.takeTopLevelItem(top_index)

            def clear(self):
                for i in range(self.topLevelItemCount() - 1, -1, -1): 
                    top_item = self.topLevelItem(i)
                    self._remove_item_recursive(top_item)
                return super().clear()
            
            def _remove_item_recursive(self, item: QTreeWidgetItem):
                for i in range(item.childCount() - 1, -1, -1):  
                    child = item.child(i)
                    self._remove_item_recursive(child)
                
                widget = self.itemWidget(item, 0)
                if widget:
                    self.removeItemWidget(item, 0)
                    widget.deleteLater()
                
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    top_index = self.indexOfTopLevelItem(item)
                    if top_index != -1:
                        self.takeTopLevelItem(top_index)

            def load(self, notifications : list[Notification.NotificationData]):

                dict_model : dict[str, list[Notification.NotificationData]] = {}
                for model in notifications:
                    lista : list[Notification.NotificationData] = dict_model.get(model.local, [])
                    lista.append(model)
                    dict_model[model.local] = lista

                for local, models in dict_model.items():
                    local_item = self.add_item_local(local)
                    for model in models:
                        self.add_item_widget(local_item, model)
                    local_item.setExpanded(True)

            def add_item_widget(self, item_local : QTreeWidget, data : Notification.NotificationData):
                item = QTreeWidgetItem(item_local)
                widget = QFrame()
                widget.setObjectName('FrameItem')
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(0,5,5,5)
                notificationItem = self.NotificationItem(data)
                layout.addWidget(notificationItem)
                notificationItem.btn_delete.clicked.connect(partial(self.signal_delete_notification.emit, item, data.guid))
                self.setItemWidget(item, 0, widget)

            def toggle_expand(self, item : QTreeWidgetItem):
                local : bool = item.data(0, 1000)
                if local:
                        item.setExpanded(not item.isExpanded())

            def add_item_local(self, local : str):
                category_item = QTreeWidgetItem([local])
                self.addTopLevelItem(category_item)
                category_item.setData(0, 1000, True)
                category_item.setIcon(0, self.icon_category)
                category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                return category_item

        class StyleSheet(Styles.Standard.StyleSheet):
                def __init__(self):
                    super().__init__()


                def style(self):

                    style = f'''
                        {Styles.standard()}
                        #LabelTitle {{font: 63 15pt "Segoe UI Semibold"; background-color: {Styles.Color.table}}}
                        #CustomActionNotification, #FrameItem {{background-color: {Styles.Color.table}}}
                        {Styles.treeView(single_background_color=Styles.Color.table)}
                    '''

                    return style
               
        def __init__(self, signal_notification : SignalInstance, signal_delete_notification : SignalInstance, signal_clear_notification : SignalInstance, *, parent : QWidget = None):
            super().__init__(parent=parent)
            widget = QFrame()
            widget.installEventFilter(CLICK_FILTER)
            widget.setObjectName("CustomActionNotification")
            label = QLabel()
            label.setText("Notifications")
            label.setObjectName("LabelTitle")
            btn_clean = QPushButton()
            btn_clean.setToolTip('Clear all notifications')
            btn_clean.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
            btn_clean.clicked.connect(signal_clear_notification.emit)
            Styles.set_icon(btn_clean, Styles.Resources.limpar.gray, Styles.Resources.limpar.blue)
            layout_header = QHBoxLayout()
            layout_header.addWidget(label)
            layout_header.addWidget(btn_clean)
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(5,5,5,5)
            layout.setSpacing(5)
            layout.addLayout(layout_header)
            self.treeWidget = self.CustomTreeWidget(signal_notification, signal_delete_notification)
            signal_clear_notification.connect(self.treeWidget.clear)
            layout.addWidget(self.treeWidget)
            Styles.set_widget_style_theme(self.StyleSheet(), widget)
            self.setDefaultWidget(widget)

        def load(self, notifications : list[Notification.NotificationData]):
            self.treeWidget.load(notifications)

    def __init__(self, widget : QPushButton, signal_notification : SignalInstance, signal_delete_notification : SignalInstance, signal_clear_notification : SignalInstance, *, parent : QWidget = None):
        super().__init__(widget, parent)
        self.customWidgetAction = self.CustomWidgetAction(signal_notification, signal_delete_notification, signal_clear_notification)
        self.addAction(self.customWidgetAction)

        widget.clicked.connect(self.show_right)
        Styles.set_widget_style_theme(Styles.menu(), self)

    def set_show_right(self):
        self.widget.clicked.disconnect()
        self.widget.clicked.connect(self.show_right)

    def set_show_over_widget(self, target_widget: QWidget, right : bool = False):
        self.widget.clicked.disconnect()
        self.widget.clicked.connect(partial(self.show_over_widget, target_widget, right))
    
    def load(self, notifications : list[Notification.NotificationData]):
        self.customWidgetAction.load(notifications)

    def _exec(self, point : QPoint, width : int, height : int):
        self.setFixedSize(0, 0)
        self.move(QPoint(-1, -1))
        self.show()
        QCoreApplication.processEvents()
        self.close()
        self.setFixedSize(width, height)
        self.exec(point)

    def show_right(self):
        QCoreApplication.processEvents()
        # Get the geometry of the target widget
        margin = 10
        widget_geometry = self.widget.parentWidget().geometry()
        widget_pos = self.widget.parentWidget().mapToGlobal(widget_geometry.topLeft())  # Convert to global coordinates
        widget_x = widget_pos.x() + self.widget.geometry().right() + 12
        widget_y = widget_pos.y()

        widget_height = widget_geometry.height()

        # Calculate new size and position with margin
        width = 600
        height = max(0, widget_height - 2 * margin)
        pos_x = widget_x + margin
        pos_y = widget_y + margin

        # Adjust size of the default widget if the menu has a single QWidgetAction
        actions = self.actions()
        if len(actions) == 1:
            action = actions[0]
            if isinstance(action, QWidgetAction):
                action.defaultWidget().setFixedSize(width - 2, height - 2)

        # Show the menu
        self._exec(QPoint(pos_x, pos_y), width, height)

    def mainWindow(self) -> QMainWindow:
        app = QApplication.instance()
    
        if not app:
            return None
        
        if isinstance(app, QMainWindow):
            return widget
        
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget
   
    def show_over_widget(self, target_widget: QWidget, right : bool = False):
        QCoreApplication.processEvents()
    
        widget_geometry = target_widget.geometry()
        widget_pos = target_widget.mapToGlobal(widget_geometry.topLeft()) 
        widget_x = widget_pos.x()
        widget_y = widget_pos.y()
        widget_height = widget_geometry.height()
        widget_width = widget_geometry.width()

        mainWindow = self.mainWindow()
        current_screen = QApplication.screenAt(mainWindow.geometry().center())
        
        if current_screen is None:
            current_screen = QApplication.primaryScreen()

        screen_geometry = current_screen.geometry()

        screen_width = screen_geometry.width()
        width = max(600, screen_width // 2)
        width = min(width, target_widget.width() - 20)
        height = max(0, widget_height - (2 * 10))
        
        pos_y = widget_y + 10
        if right:
            pos_x = widget_x + widget_width - width - 10
        else:
            pos_x = widget_x + 10
      
        actions = self.actions()
        if len(actions) == 1:
            action = actions[0]
            if isinstance(action, QWidgetAction):
                action.defaultWidget().setFixedSize(width - 2, height - 2)

        self._exec(QPoint(pos_x, pos_y), width, height)
