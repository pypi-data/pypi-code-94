#                 PyQt5 Custom Widgets                #
#                GPL 3.0 - Kadir Aksoy                #
#   https://github.com/kadir014/pyqt5-custom-widgets  #


__version__ = "1.0.1"

from .toggleswitch import ToggleSwitch
from .styledbutton import StyledButton
from .segbtngroup import SegmentedButtonGroup
from .imagebox import ImageBox
from .colorpicker import ColorPicker
from .dragdropfile import DragDropFile
from .embedwindow import EmbedWindow
from .codetextedit import CodeTextEdit
from .titlebar import TitleBar
from .spinner import Spinner
from .toast import Toast

from .dragdropfile import FileDetails
from .colorpicker import ColorPreview
from .animation import Animation, AnimationHandler
from .requesthandler import RequestHandler
from .syntaxhighlighter import SyntaxHighlighter

# 可拖动按钮， 可粘贴区域，单行技能区， 多行技能区，技能窗
from .drop_widgets import DroppableToolButton, DropButtonWidget, CustomToolRowWidget, CustomToolWidget, SkillListWidget

# not good
from .image_tooltip import ImageToolTip