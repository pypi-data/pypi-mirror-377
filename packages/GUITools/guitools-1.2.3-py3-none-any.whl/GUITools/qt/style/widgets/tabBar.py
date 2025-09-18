from .base import BaseWidgetStyleSheet, BaseStyleSheet, BaseColor, BaseProperty
from .button import ButtonStyleSheet

class TabBarStyleSheet(BaseWidgetStyleSheet):
    def __init__(self, prefix=""):
        super().__init__(f"{prefix} QTabBar")
        self.tabBar = self.TabBar(prefix)
        self.tabBar_frame = self.TabBar_frame(prefix)
        self.pane = self.Pane(prefix)
        self.tab_first = self.Tab_first(prefix)
        self.tab_only_one = self.Tab_only_one(prefix)
        self.tab_last = self.Tab_last(prefix)
        self.tab = self.Tab(prefix)
        self.tab_selected = self.Tab_selected(prefix)
        self.tabBarButton = self.TabBarButton(prefix)
       
    class TabBar(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTabBar', prefix)
            self.border = BaseProperty.Border(top_right_radius=5, bottom_left_radius=5, bottom_right_radius=5, top_left_radius=0)
            self.background_color = BaseProperty.BackgroundColor(BaseColor.primary)

    class TabBar_frame(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTabBar QWidget', prefix)
            self.border = BaseProperty.Border(top_right_radius=5, bottom_left_radius=5, bottom_right_radius=5, top_left_radius=0)

    class Pane(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('pane', prefix)
            self.border = BaseProperty.Border(color=BaseColor.division, top_right_radius=5, bottom_left_radius=5, bottom_right_radius=5, top_left_radius=0)
            self.top = BaseProperty.Top(-1)
            self.background = BaseProperty.Background(BaseColor.primary)

    class Tab_first(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTabBar::tab:first', prefix)
            self.border = BaseProperty.Border(color=BaseColor.division, top_left_radius=5, top_right_radius=0, bottom_left_radius=0, bottom_right_radius=0)

    class Tab_only_one(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTabBar::tab:only-one', prefix)
            self.border = BaseProperty.Border(color=BaseColor.division, top_left_radius=5, top_right_radius=5, bottom_left_radius=0, bottom_right_radius=0)

    class Tab_last(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTabBar::tab:last', prefix)
            self.border = BaseProperty.Border(color=BaseColor.division, top_right_radius=5, top_left_radius=0, bottom_right_radius=0, bottom_left_radius=0)

    class Tab(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTabBar::tab', prefix)
            self.border = BaseProperty.Border(top=1, right=1, left=1, bottom=1, color=BaseColor.division)
            self.padding = BaseProperty.Padding(left=5, right=5, top=2, bottom=2)
            self.background = BaseProperty.Background(BaseColor.secondary)
            self.font = BaseProperty.Font("Segoe UI Semibold", "63 12")
            self.height = BaseProperty.Height(value=30)
           
    class Tab_selected(BaseStyleSheet):
        def __init__(self, prefix=""):
            super().__init__('QTabBar::tab:selected', prefix)
            self.background = BaseProperty.Background(BaseColor.primary)
            self.border = BaseProperty.Border(bottom=1, color=BaseColor.primary)
            self.color = BaseProperty.Color(BaseColor.Reverse.selected)

    class TabBarButton(ButtonStyleSheet):
        def __init__(self, prefix=""):
            super().__init__(transparent=True, hover=False, prefix=f"{prefix} QTabBar::tab")
   
    