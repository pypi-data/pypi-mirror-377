from .base import BaseWidgetStyleSheet, BaseStyleSheet, BaseColor, BaseProperty, StyleSheets


class ScrollBarStyleSheet(BaseWidgetStyleSheet):
    def __init__(self, prefix=""):
        super().__init__(f"{prefix} QScrollBar")
        self.scrollBar = self.ScrollBar(prefix)
        self.upArrowVertical = self.UpArrowVertical(prefix)
        self.downArrowVertical = self.DownArrowVertical(prefix)
        self.addPageVertical = self.AddPageVertical(prefix)
        self.subPageVertical = self.SubPageVertical(prefix)
        self.upArrowHorizontal = self.UpArrowHorizontal(prefix)
        self.downArrowHorizontal = self.DownArrowHorizontal(prefix)
        self.addPageHorizontal = self.AddPageHorizontal(prefix)
        self.subPageHorizontal = self.SubPageHorizontal(prefix)
        self.addLineHorizontal = self.AddLineHorizontal(prefix)
        self.subLineHorizontal = self.SubLineHorizontal(prefix)
        self.subLineVertical = self.SubLineVertical(prefix)
        self.addLineVertical = self.AddLineVertical(prefix)
        self.handleVertical = self.HandleVertical(prefix)
        self.handleHorizontal = self.HandleHorizontal(prefix)
        self.horizontal = self.Horizontal(prefix)
        self.vertical = self.Vertical(prefix)

    class ScrollBar(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar', prefix)
            self.background_color = BaseProperty.BackgroundColor('transparent')

    class UpArrowVertical(StyleSheets.BackgroundNone):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::up-arrow:vertical', prefix)

    class DownArrowVertical(StyleSheets.BackgroundNone):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::down-arrow:vertical', prefix)

    class AddPageVertical(StyleSheets.BackgroundNone):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::add-page:vertical', prefix)

    class SubPageVertical(StyleSheets.BackgroundNone):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::sub-page:vertical', prefix)

    class UpArrowHorizontal(StyleSheets.BackgroundNone):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::up-arrow:horizontal', prefix)

    class DownArrowHorizontal(StyleSheets.BackgroundNone):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::down-arrow:horizontal', prefix)

    class AddPageHorizontal(StyleSheets.BackgroundNone):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::add-page:horizontal', prefix)

    class SubPageHorizontal(StyleSheets.BackgroundNone):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::sub-page:horizontal', prefix)
       
    class AddLineHorizontal(StyleSheets.WidthAndHeight):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::add-line:horizontal', prefix)

    class SubLineHorizontal(StyleSheets.WidthAndHeight):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::sub-line:horizontal', prefix)

    class SubLineVertical(StyleSheets.WidthAndHeight):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::sub-line:vertical', prefix)

    class AddLineVertical(StyleSheets.WidthAndHeight):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::add-line:vertical', prefix)

    class HandleVertical(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::handle:vertical', prefix)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.tertiary)
            self.height = BaseProperty.Height(min=20)
            self.border = BaseProperty.Border(radius=3)

    class HandleHorizontal(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar::handle:horizontal', prefix)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.tertiary)
            self.width = BaseProperty.Width(min=20)
            self.border = BaseProperty.Border(radius=3)
           
    class Horizontal(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar:horizontal', prefix)
            self.height = BaseProperty.Height(value=10)
            self.background_color = BaseProperty.BackgroundColor('transparent')
            self.border = BaseProperty.Border(radius=3)
            self.padding = BaseProperty.Padding(value=2)

    class Vertical(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QScrollBar:vertical', prefix)
            self.width = BaseProperty.Width(value=10)
            self.background_color = BaseProperty.BackgroundColor('transparent')
            self.border = BaseProperty.Border(radius=3)
            self.padding = BaseProperty.Padding(value=2)

class ScrollAreaStyleSheet(ScrollBarStyleSheet):
    def __init__(self, prefix=""):
        super().__init__(f"{prefix} QScrollArea")
        self.vertical.background_color.value = BaseColor.primary
        self.horizontal.background_color.value = BaseColor.primary





