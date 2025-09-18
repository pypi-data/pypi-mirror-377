from .base import BaseWidgetStyleSheet, BaseStyleSheet, BaseColor, BaseProperty
from .checkBox import CheckBoxStyleCheet
from .listView import ListViewStyleCheet
from .scrollBar import ScrollBarStyleSheet

class ComboBoxStyleCheet(BaseWidgetStyleSheet):
    def __init__(self, prefix="", height : int | None = 25):
        super().__init__(f"{prefix} QComboBox")
        self.comboBox = self.ComboBox(prefix, height)
        self.dropDownOn = self.DropDownOn(prefix)
        self.dropDownHover = self.DropDownHover(prefix)
        self.abstractItemView = self.AbstractItemView(prefix)
        self.hover = self.Hover(prefix)
        self.on = self.On(prefix)
        self.listView = self.ListView(prefix)
        self.checkBox = self.CheckBox(prefix)
        self.scrollBarHorizontal = self.ScrollBarHorizontal(prefix)
        self.scrollBarVertical= self.ScrollBarVertical(prefix)
        self.onPopupOpen = self.OnPopupOpen(prefix)
        self.dropDownOnPopupOpen = self.DropDownOnPopupOpen(prefix=prefix)
        self.onPopupOpenUp = self.OnPopupOpenUp(prefix)
        self.dropDownOnPopupOpenUp = self.DropDownOnPopupOpenUp(prefix=prefix)
        self.abstractItemViewSelected = self.AbstractItemViewSelected(prefix=prefix)

    class ScrollBarHorizontal(ScrollBarStyleSheet.Horizontal):
        def __init__(self,  prefix=""):
            super().__init__(f'{prefix} QComboBox')
            self.background_color.value = BaseColor.Widget.background
          
    class ScrollBarVertical(ScrollBarStyleSheet.Vertical):
        def __init__(self,  prefix=""):
            super().__init__(f'{prefix} QComboBox')
            self.background_color.value = BaseColor.Widget.background
          
    class ComboBox(BaseStyleSheet):
        def __init__(self, prefix="", height : int | None = 25):
            super().__init__('QComboBox', prefix)
            self.font = BaseProperty.FontSegoeUI(12)
            self.height = BaseProperty.Height(value=height, min=height, max=height)
            self.border = BaseProperty.Border(radius=5, color=BaseColor.Widget.background)
            self.padding = BaseProperty.Padding(left=2)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.Widget.background)
            self.color = BaseProperty.Color(BaseColor.Reverse.primary)
            self.selection_background_color = BaseProperty.BackgroundColor(BaseColor.Widget.selected_background, 'selection')
            self.selection_color = BaseProperty.Color(BaseColor.Reverse.primary, 'selection')

    class DropDownOn(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox::drop-down:on', prefix)
            self.image = BaseProperty.Image("arrow_down.png", "73_145_246") 

    class DropDownOnPopupOpen(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox::drop-down[popup_open="true"]', prefix)
            self.image = BaseProperty.Image("arrow_down.png", "73_145_246") 

    class DropDownOnPopupOpenUp(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox::drop-down[popup_open_up="true"]', prefix)
            self.image = BaseProperty.Image("arrow_up.png", "73_145_246")

    class DropDownHover(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox::drop-down:hover', prefix)
            self.image = BaseProperty.Image("arrow_down.png", "73_145_246")

    class AbstractItemView(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox QAbstractItemView', prefix)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.Widget.background)
            self.border = BaseProperty.Border(
                color=BaseColor.Widget.focus_border,
                bottom_left_radius=5,
                bottom_right_radius=0,
                top_left_radius=0,
                top_right_radius=0
            )

    class AbstractItemViewSelected(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox QAbstractItemView::item:selected', prefix)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.Widget.selected_background)
            self.color = BaseProperty.Color(BaseColor.Reverse.primary)

    class Hover(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox:hover', prefix)
            self.border = BaseProperty.Border(color=BaseColor.Widget.hover_border)

    class On(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox:on', prefix)
            self.border = BaseProperty.Border(color=BaseColor.Widget.focus_border, bottom_left_radius=0, bottom_right_radius=0)

    class OnPopupOpen(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox[popup_open="true"]', prefix)
            self.border = BaseProperty.Border(color=BaseColor.Widget.focus_border, bottom_left_radius=0, bottom_right_radius=0)

    class OnPopupOpenUp(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QComboBox[popup_open_up="true"]', prefix)
            self.border = BaseProperty.Border(color=BaseColor.Widget.focus_border, top_left_radius=0, top_right_radius=0)

    class ListView(ListViewStyleCheet):
        def __init__(self, prefix=""):
            super().__init__(f"{prefix} QComboBox")

    class CheckBox(CheckBoxStyleCheet):
        def __init__(self, prefix=""):
            super().__init__(f"{prefix} QComboBox")
