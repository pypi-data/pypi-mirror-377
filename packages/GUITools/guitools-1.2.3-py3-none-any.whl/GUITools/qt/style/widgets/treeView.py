from .base import BaseWidgetStyleSheet, BaseStyleSheet, BaseColor, BaseProperty
from .checkBox import indicatorStyleCheet
from .scrollBar import ScrollBarStyleSheet

class BaseTreeView(BaseStyleSheet):
        def __init__(self, class_name : str, prefix=""):
            super().__init__(class_name, prefix)
            self.font = BaseProperty.FontSegoeUI(12)
            self.border = BaseProperty.Border(radius=5)
            self.padding = BaseProperty.Padding(value=0)
            self.margin = BaseProperty.Margin(value=0)

class TreeViewStyleSheet(BaseWidgetStyleSheet):

    def __init__(self, *, prefix="", single_background_color : BaseColor = None, scrollBar_handle_color :  BaseColor = None): 
        super().__init__(f"{prefix} QTreeView")
        self.widgetAction = self.WidgetAction(prefix)
        self.treeView = self.TreeView(prefix)
        self.itemOpen = self.ItemOpen(prefix)
        self.itemSelected = self.ItemSelected(prefix)
        self.itemDisabled = self.ItemDisabled(prefix)
        self.itemNotselectedDisabled = self.ItemNotselectedDisabled(prefix)
        self.itemSelectedDisabled = self.ItemSelectedDisabled(prefix)

        #self.branchHasSiblingsNotAdjoinsItem = self.BranchHasSiblingsNotAdjoinsItem()
        #self.branchHasSiblingsAdjoinsItem = self.BranchHasSiblingsAdjoinsItem()
        #self.branchHasNotSiblingsAdjoinsItem = self.BranchHasNotSiblingsAdjoinsItem()
        self.branchClosed = self.BranchClosed()
        self.branchOpen = self.BranchOpen()
      
        self.indicator = self.Indicator(prefix)
        self.label = self.Label(prefix)

        self.treeWidget = self.TreeWidget()
        self.item = self.Item(prefix)
        self.itemSelected = self.ItemSelected(prefix)
        self.itemFocus = self.ItemFocus(prefix)
        self.itemHover = self.ItemHover(prefix)
        self.itemSelectedHover = self.ItemSelectedHover(prefix)
        self.itemNotselected = self.ItemNotselected(prefix)
        self.itemNotselectedHover = self.ItemNotselectedHover(prefix)

        self.scrollBarHorizontal = self.ScrollBarHorizontal(prefix)
        self.scrollBarVertical= self.ScrollBarVertical(prefix)

        self.scrollBarHandleHorizontal = self.ScrollBarHandleHorizontal(prefix, scrollBar_handle_color)
        self.scrollBarHandleVertical = self.ScrollBarHandleVertical(prefix, scrollBar_handle_color)

        if single_background_color:
            self.treeView.background_color.value = single_background_color
            self.treeWidget.background_color.value = single_background_color
            self.item.background_color.value = single_background_color
            self.itemHover.background_color.value = single_background_color
            self.itemFocus.background_color.value = single_background_color
            self.itemNotselected.background_color.value = single_background_color
            self.itemNotselectedHover.background_color.value = single_background_color
            self.scrollBarHorizontal.background_color.value = single_background_color
            self.scrollBarVertical.background_color.value = single_background_color

    class ScrollBarHorizontal(ScrollBarStyleSheet.Horizontal):
        def __init__(self, prefix=""):
            super().__init__(f'{prefix} QTreeWidget')
            self.background_color.value = BaseColor.table

    class ScrollBarVertical(ScrollBarStyleSheet.Vertical):
        def __init__(self, prefix=""):
            super().__init__(f'{prefix} QTreeWidget')
            self.background_color.value = BaseColor.table

    class ScrollBarHandleVertical(ScrollBarStyleSheet.HandleVertical):
        def __init__(self,  prefix="", background_color : BaseColor = None):
            super().__init__(f'{prefix} QTreeWidget')
            self.background_color = BaseProperty.BackgroundColor(background_color if background_color else BaseColor.tertiary)

    class ScrollBarHandleHorizontal(ScrollBarStyleSheet.HandleHorizontal):
        def __init__(self, prefix="", background_color : BaseColor = None):
            super().__init__(f'{prefix} QTreeWidget')
            self.background_color = BaseProperty.BackgroundColor(background_color if background_color else BaseColor.tertiary)
           
    class Item(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeWidget::item', prefix)
            self.background_color = BaseProperty.Background(BaseColor.table)
            self.color = BaseProperty.Color(value=BaseColor.Reverse.primary)

    class ItemDisabled(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeWidget::item:disabled', prefix)
            self.background_color = BaseProperty.Background(BaseColor.table)
            self.color = BaseProperty.Color(value=BaseColor.Reverse.primary.fromRgba(200))

    class ItemNotselectedDisabled(BaseStyleSheet):
         def __init__(self, prefix=""):
            super().__init__('QTreeWidget::item:!selected:disabled', f"{prefix}")
            self.background_color = BaseProperty.Background(BaseColor.table)
            self.color = BaseProperty.Color(value=BaseColor.Reverse.primary.fromRgba(200))

    class ItemSelectedDisabled(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeView:item:selected:disabled', prefix)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.table_selection_background)
            self.color = BaseProperty.Color(value=BaseColor.Reverse.selected)

    class ItemNotselected(BaseStyleSheet):
         def __init__(self, prefix=""):
            super().__init__('QTreeWidget::item:!selected', f"{prefix}")
            self.background_color = BaseProperty.Background(BaseColor.table)
            self.color = BaseProperty.Color(value=BaseColor.Reverse.primary)

    class ItemNotselectedHover(BaseStyleSheet):
         def __init__(self, prefix=""):
            super().__init__('QTreeWidget::item:!selected:hover', f"{prefix}")
            self.background_color = BaseProperty.Background(BaseColor.table_alternate)

    class ItemFocus(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeWidget::item:focus', prefix)
            self.background_color = BaseProperty.Background(BaseColor.table_selection_background)

    class ItemHover(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeWidget::item:hover', prefix)
            self.background_color = BaseProperty.Background(BaseColor.table_alternate)

    class ItemSelectedHover(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeWidget::item:selected:hover', prefix)
            self.background_color = BaseProperty.Background(BaseColor.table_selection_background)

    class WidgetAction(BaseTreeView):
        def __init__(self, prefix=""):
            super().__init__('QTreeWidget QWidgetAction', prefix)

    class TreeWidget(BaseTreeView):
        def __init__(self, prefix=""):
            super().__init__('QTreeWidget', prefix)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.table)

    class TreeView(BaseTreeView):
        def __init__(self, prefix=""):
            super().__init__('QTreeView', prefix)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.table)

    class ItemOpen(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeView:item:open', prefix)
            self.color = BaseProperty.Color(value=BaseColor.Reverse.selected)

    class ItemSelected(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeView:item:selected', prefix)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.table_selection_background)
            self.color = BaseProperty.Color(value=BaseColor.Reverse.selected)

    class Indicator(indicatorStyleCheet):
        def __init__(self, prefix=""):
            super().__init__("QTreeView", prefix)

    class Label(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QLabel', f"{prefix} QTreeView")
            self.background_color = BaseProperty.BackgroundColor("transparent")
        
    class BranchHasSiblingsNotAdjoinsItem(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeView::branch:has-siblings:!adjoins-item', prefix)
            #self.image = f'border-image: url(:/{Icons.Name.add_suffix_theme(Icons.Name.vline)}) 0;'
               
    class BranchHasSiblingsAdjoinsItem(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeView::branch:has-siblings:adjoins-item', prefix)
            #self.image = f'border-image: url(:/{Icons.Name.add_suffix_theme(Icons.Name.vline)}) 0;'
           
    class BranchHasNotSiblingsAdjoinsItem(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeView::branch:!has-children:!has-siblings:adjoins-item', prefix)
            #self.image = f'border-image: url(:/{Icons.Name.add_suffix_theme(Icons.Name.branch_end)}) 0;'
            
    class BranchClosed(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeView::branch:closed:has-children', prefix)
            self.image = BaseProperty.Image('branch_closed.png')
            self.add_additional_style("border-image: none;")

    class BranchOpen(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTreeView::branch:open:has-children', prefix)
            self.image = BaseProperty.Image('branch_open.png')
            self.add_additional_style("border-image: none;")

    



