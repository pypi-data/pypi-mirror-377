# coding: utf-8
from functools import partial
from ..Interface.SideBar import Ui_FrameSideBar
from PySide6.QtWidgets import QFrame, QWidget, QTreeWidgetItem, QLabel, QStackedWidget, QVBoxLayout
from ...style import Styles
from ...animation import Animation
from PySide6.QtCore import QSize, Qt, Signal, QTimer
from PySide6.QtGui import QCursor, QIcon
from typing import Callable
from ...notification import Notification
from .utils import ClickFilter, Page, FrameStyleSheet

CLICK_FILTER = ClickFilter()

from .menu_notifications import CustomMenuNotification
from .menu_user import CustomMenuUser

class SideBar(Ui_FrameSideBar, QFrame):
    
    class WidgetStyleSheet(Styles.WidgetStyleSheet):
        def __init__(self, action : object):
            super().__init__()
            self.action = action

        def style(self):
            self.action()
            style = f'''
                #frame_logo, #frame_separator {{ border-bottom: 1px solid {Styles.Color.division}; border-radius: 0px;}}
                {Styles.button(transparent=True, hover=False, prefix="#btn_notifications, #btn_user").styleSheet()}
            '''
            return f'{style}'

    signal_notification = Signal(Notification.NotificationData)
    signal_delete_notification = Signal(QTreeWidgetItem, str)
    signal_clear_notification = Signal()
    def __init__(self, parent : QWidget, stackedWidget : QStackedWidget, callable_icon_page_standard : Callable, display_notifications = True ):
        super().__init__(None)
        super().setupUi(self)
        self.opened = False
        self.user_name = "User"
        self.widge_parent = parent
        self.widge_parent.layout().addWidget(self)
        self.stackedWidget = stackedWidget
        self.whide_icon : QIcon = None
        self.whide_icon_size = QSize(40, 40)
        self.icon : QIcon = None
        self.icon_size = QSize(40, 40)
        self.pages : list[Page] = []
        
        self.label_logo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.label_logo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_text_logo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_toggle.setIcon(Styles.Resources.separador_left.gray())
        self.btn_toggle.clicked.connect(self.toggle)
        
        self.btn_user.close()
        self.btn_notifications.setVisible(display_notifications)
        if display_notifications:
            Styles.set_icon(self.btn_notifications, Styles.Resources.notification.gray, Styles.Resources.notification.blue)
            self.menuNotification = CustomMenuNotification(self.btn_notifications, self.signal_notification, self.signal_delete_notification, self.signal_clear_notification)

        self.widget_standard = QLabel()
        self.widget_standard.setPixmap(callable_icon_page_standard().toPixmap(300))
        self.widget_standard.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stackedWidget.addWidget(self.widget_standard)
        self.stackedWidget.setCurrentWidget(self.widget_standard)

        self.widget_loading = QLabel()
        self.widget_loading.setPixmap(Styles.Resources.loading.original().toPixmap(100))
        self.widget_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stackedWidget.addWidget(self.widget_loading)
   
        Styles.set_widget_style_theme(self.WidgetStyleSheet(self.update_btns_styles), self)

    def set_user_data(self, user_name: str, user_id: str):
        self.btn_user.show()
        Styles.set_icon(self.btn_user, Styles.Resources.user.gray, Styles.Resources.user.blue)
        self.menuUser = CustomMenuUser(self.btn_user)
        self.user_name = user_name
        self.menuUser.set_data_user(user_name, user_id)

    def set_icon(self, icon : QIcon, size_w = 40, size_h = 40):
        self.icon = icon
        self.icon_size = QSize(size_w, size_h)
        self.label_logo.setPixmap(icon.pixmap(self.icon_size))
      
    def set_whide_icon(self, icon : QIcon, size_w = 40, size_h = 40):
        self.whide_icon = icon
        self.whide_icon_size = QSize(size_w, size_h)
        
    def set_icon_action(self, action : object):
        click_filter = ClickFilter(self.label_logo)
        click_filter.action = action
        self.label_logo.installEventFilter(click_filter)
        click_filter = ClickFilter(self.label_text_logo)
        click_filter.action = action
        self.label_text_logo.installEventFilter(click_filter)

    def set_title(self, title : str):
        self.label_text_logo.setText(title)

    def add_page(self, callable_page : Callable, text : str, callable_icon : Callable, selcted_callable_icon : Callable, icon_size : int = 18, expandable : bool = False):
        style_normal = FrameStyleSheet()
        page = Page(callable_page, self.stackedWidget, text, callable_icon, selcted_callable_icon, icon_size, expandable)
        page.setStyleSheet(style_normal.styleSheet())
        page.clicked.connect(partial(self.select, page_select=page))
        self.frame_side_bar_btns.layout().addWidget(page)
        self.pages.append(page)
        return page
    
    def add_separator(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 5, 0, 5)
        separator = QFrame()
        separator.setObjectName('frame_separator')
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        self.frame_side_bar_btns.layout().addWidget(frame)
    
    def toggle(self):
        if self.opened:
            Animation.minimumWidth(self.widge_parent, 250, 60)
            if self.whide_icon:
                self.label_logo.setMinimumWidth(40)
                self.label_logo.setPixmap(self.icon.pixmap(self.icon_size))
        else:
            style_selected = FrameStyleSheet(selected=True)
            style_normal = FrameStyleSheet()
            Animation.minimumWidth(self.widge_parent, 60, 250)
            for page in self.pages:
                if page.selected:
                    page.setStyleSheet(style_selected.styleSheet())
                else:
                    page.setStyleSheet(style_normal.styleSheet())

            style_btn_toggle = Styles.button_menu()
            style_btn_toggle.button.font.size = 10
            style_btn_toggle.button.color.value = Styles.Color.Reverse.primary.fromRgba(200)

            self.btn_toggle.setStyleSheet(style_btn_toggle.styleSheet())
            self.btn_toggle.setText("  Hide side panel")
            self.btn_notifications.setStyleSheet(style_btn_toggle.styleSheet())
            self.btn_notifications.setText("  Notifications")
            self.btn_user.setStyleSheet(style_btn_toggle.styleSheet())
            self.btn_user.setText(f"  {self.user_name}")
            if self.whide_icon:
                self.label_logo.setMinimumWidth(230)
                self.label_logo.setPixmap(self.whide_icon.pixmap(self.whide_icon_size))

        self.opened = not self.opened 
        QTimer.singleShot(200, self.toggle_visible_texts)

    def toggle_visible_texts(self):
        for page in self.pages:
            page.label_text.setVisible(self.opened)

    def select(self, page_select : Page, *args):
        if not self.opened:
            self.btn_toggle.setText("")
            self.btn_notifications.setText("")
            self.btn_user.setText("")

        style_selected  = FrameStyleSheet(selected=True)
        style_normal = FrameStyleSheet()

        style_btn_toggle = Styles.button_menu(padding=self.opened)
        style_btn_toggle.button.font.size = 10
        style_btn_toggle.button.color.value = Styles.Color.Reverse.primary.fromRgba(200)

        self.btn_toggle.setStyleSheet(style_btn_toggle.styleSheet())
        self.btn_notifications.setStyleSheet(style_btn_toggle.styleSheet())
        self.btn_user.setStyleSheet(style_btn_toggle.styleSheet())
        for page in self.pages:
            if page_select == page:
                page.setStyleSheet(style_selected.styleSheet())
                page.toggle_icon(True)
            else:
                page.toggle_icon(False)
                page.setStyleSheet(style_normal.styleSheet())
        page_select._show_page(*args)
                
    def update_btns_styles(self):
        style_selected  = FrameStyleSheet(selected=True)
        style_normal = FrameStyleSheet()

        style_btn_toggle = Styles.button_menu(padding=self.opened)
        style_btn_toggle.button.font.size = 10
        style_btn_toggle.button.color.value = Styles.Color.Reverse.primary.fromRgba(200)

        self.btn_toggle.setStyleSheet(style_btn_toggle.styleSheet())
        self.btn_notifications.setStyleSheet(style_btn_toggle.styleSheet())
        self.btn_user.setStyleSheet(style_btn_toggle.styleSheet())
        for page in self.pages:
            if page.selected:
                page.toggle_icon(True)
                page.setStyleSheet(style_selected.styleSheet())
            else:
                page.toggle_icon(False)
                page.setStyleSheet(style_normal.styleSheet())

