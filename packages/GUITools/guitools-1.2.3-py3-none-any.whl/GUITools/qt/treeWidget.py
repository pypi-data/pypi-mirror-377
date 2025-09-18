# coding: utf-8

from PySide6.QtWidgets import QTreeWidgetItem, QWidget, QVBoxLayout, QPushButton, QTreeWidget, QAbstractItemView
from PySide6.QtCore import QSize, QCoreApplication, Qt, QEvent, QTimer, SignalInstance, Signal, QObject
from .style import Styles
from .menu import Menu
from pydantic import BaseModel

class Data(BaseModel):
     column : int 
     role : int 
     values : list[object]

class WidgetVisibilityWatcher(QObject):

    def __init__(self, widget: QWidget, signal_update : SignalInstance):
        super().__init__(widget)
        self.widget = widget
        self.signal_update = signal_update
        self.load = False
        self.widget.installEventFilter(self) 

    def eventFilter(self, obj, event : QEvent):
        if obj == self.widget and event.type() == QEvent.Type.Show and not self.load:
            self.load = True
            self.signal_update.emit()  
        return super().eventFilter(obj, event)

class TreeWidget(QTreeWidget):
     signal_update = Signal()
     def __init__(self, *, scroll_amount : int = None, parent : QWidget = None):
          super().__init__(parent)
          self._selection_locked = False
          self.allowed_selectable_data : list[Data] = []
          self.scroll_amount : int = scroll_amount
          if scroll_amount:
               self.setAutoScroll(False)
               self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
               self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
          self.signal_update.connect(self.count_signals)

          self.signal_count = 0
          self.signal_timer = QTimer()
          self.signal_timer.setSingleShot(True)
          self.signal_timer.timeout.connect(self.process_signal_batch)

     def count_signals(self):
        self.signal_count += 1

        if not self.signal_timer.isActive():
            self.signal_timer.start(100)  

     def process_signal_batch(self):
        self.signal_count = 0
        self.update_tree_widgets()

     def setItemWidget(self, item, column, widget):
        WidgetVisibilityWatcher(widget, self.signal_update)
        return super().setItemWidget(item, column, widget)

     def clear(self):
          self.allowed_selectable_data.clear()
          return super().clear()

     def wheelEvent(self, event):
          """Controla o comportamento de rolagem ao usar a roda do mouse."""
          if self.scroll_amount:
               if event.angleDelta().y() > 0:
                    self.verticalScrollBar().setValue(self.verticalScrollBar().value() - self.scroll_amount)  # Subir mais rapidamente
               else:
                    self.verticalScrollBar().setValue(self.verticalScrollBar().value() + self.scroll_amount)  # Descer mais rapidamente
               event.accept()
          else:
               super().wheelEvent(event)

     def setSelectionLocked(self, locked: bool):
        self._selection_locked = locked

     def setAllowedSelectableData(self, column : int, role : int, value : object):
          for data in self.allowed_selectable_data:
               if data.column == column and data.role == role:
                    if value not in data.values:
                         data.values.append(value)
                    return
          self.allowed_selectable_data.append(Data(column=column, role=role, values=[value]))

     def isAllowedItem(self, item : QTreeWidgetItem):
          for data in self.allowed_selectable_data:
               value = item.data(data.column, data.role)
               if value in data.values:
                    return True
          return False

     def mousePressEvent(self, event):
          if self._selection_locked:
               item = self.itemAt(event.pos())
               if item is not None and (item.flags() & Qt.ItemFlag.ItemIsSelectable) and not self.isAllowedItem(item):
                    event.ignore()
                    return
          super().mousePressEvent(event)

     def mouseMoveEvent(self, event):
          if self._selection_locked:
               event.ignore()
               return
          super().mouseMoveEvent(event)

     def keyPressEvent(self, event):
          if self._selection_locked and event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
               event.ignore()
               return
          super().keyPressEvent(event)

     def get_expanded_items(self):
          """Obtém todos os itens expandidos no QTreeWidget."""
          expanded_items : list[QTreeWidgetItem] = []

          def find_expanded_items(item : QTreeWidgetItem):
               if item.isExpanded():
                    expanded_items.append(item)
               for i in range(item.childCount()):
                    find_expanded_items(item.child(i))

          for i in range(self.topLevelItemCount()):
               find_expanded_items(self.topLevelItem(i))

          return expanded_items
    
     def update_tree_widgets(self):
          items = self.get_all_items(self)
          for item in items:
               if item.data(0, 1001):
                    continue

               updated = False
               for col in range(self.columnCount()):
                    widget : QWidget = self.itemWidget(item, col)
                    if widget is not None:
                         if not widget.isVisible():
                              break
                         updated = True
                         widget.adjustSize()  
                         widget.updateGeometry() 
                         height = widget.height()
                         sizeHint = item.sizeHint(col)
                         if sizeHint.height() != height:
                              item.setSizeHint(col, QSize(sizeHint.width(), height))
               if updated:
                    item.setData(0, 1001, True)

          for col in range(self.columnCount()):
               self.resizeColumnToContents(col)
          self.viewport().update() 

     def clearSelection(self):
          try:
               self.setUpdatesEnabled(False)
               self.blockSignals(True)
               self.clearSelection()
               self.blockSignals(False)
               self.setUpdatesEnabled(True)
               QCoreApplication.processEvents()
          except:
            ...

     def get_topLevelItems(self):
        top_items = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]
        return top_items
     
     def remove_topLevelItem(self, item: QTreeWidgetItem):
          """Remove um item de nível superior e seus filhos corretamente."""
          if item:
               for i in reversed(range(item.childCount())):
                    child = item.child(i)
                    widget = self.itemWidget(child, 0)
                    if widget:
                         widget.deleteLater()
                    item.removeChild(child)
                    del child
               index = self.indexOfTopLevelItem(item)
               self.takeTopLevelItem(index)
               del item

     @staticmethod
     def toggle_expand(item : QTreeWidgetItem, column : int, *, fized_column : int = None, role = 1000):
          expand : bool = item.data(column if fized_column == None else fized_column, role)
          if expand:
               item.setExpanded(not item.isExpanded())

     @staticmethod
     def all_toggle_expand(item : QTreeWidgetItem):
          item.setExpanded(not item.isExpanded())

     @staticmethod
     def get_all_children(item : QTreeWidgetItem):
        """
        Retorna uma lista de todos os itens filhos de 'item', incluindo todos os descendentes.

        :param item: QTreeWidgetItem inicial.
        :return: Lista de QTreeWidgetItem.
        """
        children : list[QTreeWidgetItem] = []
        stack = [item]

        while stack:
               current_item = stack.pop()
               child_count = current_item.childCount()
               for i in range(child_count):
                    child = current_item.child(i)
                    children.append(child)
                    stack.append(child)
        return children
     
     @staticmethod
     def get_texts(items : list[QTreeWidgetItem], column : int):
          texts = [item.text(column) for item in items]
          return texts

     @classmethod
     def get_all_items(cls, tree: QTreeWidget, top_level = True) -> list[QTreeWidgetItem]:
          items = []
          for i in range(tree.topLevelItemCount()):
               item = tree.topLevelItem(i)
               if top_level:
                    items.append(item)
               items.extend(cls.get_all_children(item)) 
          return items
     
     @classmethod
     def get_all_data(cls, tree: QTreeWidget, column: int = 0, role : int = 0, top_level = True):
          items = cls.get_all_items(tree, top_level)
          data = [item.data(column, role) for item in items]
          return [d for d in data if d is not None]
        
     @classmethod
     def find_item_by_data(cls, tree: QTreeWidget, data_value, column: int = 0, role : int = 0,  top_level = True) -> QTreeWidgetItem | None:
          for i in range(tree.topLevelItemCount()):
               item = tree.topLevelItem(i)
               if top_level and item.data(column, role) == data_value:
                    return item
               items = cls.get_all_children(item)
               for sub_item in items:
                    if sub_item.data(column, role) == data_value:
                         return sub_item
          return None
     
     def find_topLevelItem_by_text(self, text: str) -> QTreeWidgetItem:
          for index in range(self.topLevelItemCount()):
               item = self.topLevelItem(index)
               if item.text(0) == text:
                    return item
          return None
     
     @staticmethod
     def set_item_not_selectable(item : QTreeWidgetItem):
          item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

     @staticmethod
     def set_item_spanned(item : QTreeWidgetItem):
          item.setFirstColumnSpanned(True)  
          item.setTextAlignment(0, Qt.AlignmentFlag.AlignCenter)

     @classmethod
     def disable_items(cls, tree_widget: QTreeWidget):
          for i in range(tree_widget.topLevelItemCount()):
               top_item = tree_widget.topLevelItem(i)
               cls.disable_item_and_widgets(tree_widget, top_item)
               for j in range(top_item.childCount()):
                    child_item = top_item.child(j)
                    cls.disable_item_and_widgets(tree_widget, child_item)
                    
     @classmethod
     def enable_items(cls, tree_widget: QTreeWidget):
          for i in range(tree_widget.topLevelItemCount()):
               top_item = tree_widget.topLevelItem(i)
               cls.enable_item_and_widgets(tree_widget, top_item)
               for j in range(top_item.childCount()):
                    child_item = top_item.child(j)
                    cls.enable_item_and_widgets(tree_widget, child_item)

     @classmethod
     def disable_item_and_widgets(cls, tree_widget: QTreeWidget, item: QTreeWidgetItem):
          item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
          for column in range(tree_widget.columnCount()):
               widget = tree_widget.itemWidget(item, column)
               if widget:
                    widget.setDisabled(True)

     @classmethod
     def enable_item_and_widgets(cls, tree_widget: QTreeWidget, item: QTreeWidgetItem):
          item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
          for column in range(tree_widget.columnCount()):
               widget = tree_widget.itemWidget(item, column)
               if widget:
                    widget.setDisabled(False)

     @staticmethod
     def disable_tree_item(tree_widget: QTreeWidget, item: QTreeWidgetItem):
          item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
          for column in range(tree_widget.columnCount()):
               widget = tree_widget.itemWidget(item, column)
               if widget:
                    widget.setDisabled(True)

     @staticmethod
     def enable_tree_item(tree_widget: QTreeWidget, item: QTreeWidgetItem):
          item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
          for column in range(tree_widget.columnCount()):
               widget = tree_widget.itemWidget(item, column)
               if widget:
                    widget.setDisabled(False)

     @staticmethod
     def select_item(tree_widget : QTreeWidget, item : QTreeWidgetItem, scrollToItem = True):
          if scrollToItem:
               parent = item.parent()
               while parent:
                    parent.setExpanded(True)
                    parent = parent.parent()
          
          item.setSelected(True)
          if scrollToItem:
               tree_widget.scrollToItem(item)

     def filter_items(self, search_text : str):
          search_text = search_text.lower().strip()

          top_level_items = TreeWidget.get_topLevelItems(self)

          def filter_recursive(item : QTreeWidgetItem, search_text):
               match = search_text in item.text(0).lower()

               children_matches = []
               for i in range(item.childCount()):
                    child = item.child(i)
                    if filter_recursive(child, search_text):
                         children_matches.append(child)

               # Se o item tiver widget → ignora filtro direto
               has_widget = self.itemWidget(item, 0) is not None

               if not has_widget:
                    if match and not children_matches:
                         # Caso especial: match apenas pelo texto do item
                         item.setHidden(False)
                         # Torna todos os filhos visíveis
                         for i in range(item.childCount()):
                              child = item.child(i)
                              if self.itemWidget(child, 0) is None:  # só altera se não tiver widget
                                   child.setHidden(False)
                    else:
                         # Normal: visível se ele ou algum filho corresponder
                         item.setHidden(not (match or bool(children_matches)))

               return match or bool(children_matches)

          for top_item in top_level_items:
               filter_recursive(top_item, search_text)

     class WidgetOptions(QWidget):

          def __init__(self, tree_item: QTreeWidgetItem, parent=None):
               super().__init__(parent)
               self.tree_item = tree_item
               self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
               self._menu : Menu = None
               layout = QVBoxLayout(self)
               layout.setContentsMargins(0,0,0,0)
               self.button = QPushButton()
               self.button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
               self.button.setIconSize(QSize(14, 14))
               self.button.setCursor(Qt.CursorShape.PointingHandCursor)
               Styles.set_icon(self.button, Styles.Resources.three_point.gray, Styles.Resources.three_point.theme)
               self.button.setVisible(False)  # Initially hidden
               layout.addWidget(self.button)
               self.setLayout(layout)

               # Connect selection change to update button visibility
               tree_widget = self.tree_item.treeWidget()
               if tree_widget:
                    tree_widget.itemSelectionChanged.connect(self.update_button_visibility)

          def setMenu(self, menu : Menu):
               if not self._menu:
                    self._menu = menu
                    self._menu.aboutToHide.connect(self.on_menu_about_to_hide)
               else:
                    self._menu = menu
                    self._menu.aboutToHide.disconnect(self.on_menu_about_to_hide)
                    self._menu.aboutToHide.connect(self.on_menu_about_to_hide)

          def on_menu_about_to_hide(self):
               tree_widget = self.tree_item.treeWidget()
               if tree_widget and self.tree_item not in tree_widget.selectedItems():
                    self.button.setVisible(False)

          def update_button_visibility(self):
               tree_widget = self.tree_item.treeWidget()
               if tree_widget:
                    is_selected = self.tree_item in tree_widget.selectedItems()
                    self.button.setVisible(is_selected)
                    
          def enterEvent(self, event):
               self.button.setVisible(True)
               super().enterEvent(event)

          def leaveEvent(self, event):
               tree_widget = self.tree_item.treeWidget()
               if tree_widget and self.tree_item not in tree_widget.selectedItems():
                    if self._menu:
                         if self._menu.is_open:
                              self.button.setVisible(False)
                    else:
                         self.button.setVisible(False)
               super().leaveEvent(event)

