import vgamepad as vg
from function.utils import InverseDict
from .controller_utils import BASE_STICK_6

class DS4_BUTTON:
    CROSS       = 0
    CIRCLE      = 1
    SQUARE      = 2
    TRIANGLE    = 3
    SHARE       = 4
    PS          = 5
    OPTION      = 6
    L3          = 7
    R3          = 8
    L1          = 9
    R1          = 10
    UP          = 11
    DONW        = 12
    LEFT        = 13
    RIGHT       = 14
    TOUCH_PAD   = 15
    NUM         = 16

    NAME = {
        CROSS       : "バツボタン",
        CIRCLE      : "丸ボタン",
        SQUARE      : "四角ボタン",
        TRIANGLE    : "三角ボタン",
        SHARE       : "シェアボタン",
        PS          : "PSボタン",
        OPTION      : "オプションボタン",
        L3          : "L3",
        R3          : "R3",
        L1          : "L1",
        R1          : "R1",
        UP          : "上十字キー",
        DONW        : "下十字キー",
        LEFT        : "左十字キー",
        RIGHT       : "右十字キー",
        TOUCH_PAD   : "タッチパッド",
    }
    
    INDEX = InverseDict(NAME)
    
    DEFAULT = {}
    
    TABLE = {
        CROSS       : vg.DS4_BUTTONS.DS4_BUTTON_CROSS,
        CIRCLE      : vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE,
        SQUARE      : vg.DS4_BUTTONS.DS4_BUTTON_SQUARE,
        TRIANGLE    : vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE,
        SHARE       : vg.DS4_BUTTONS.DS4_BUTTON_SHARE,
        PS          : vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_PS,
        OPTION      : vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS,
        L3          : vg.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT,
        R3          : vg.DS4_BUTTONS.DS4_BUTTON_THUMB_RIGHT,
        L1          : vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT,
        R1          : vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT,
        UP          : vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH,
        DONW        : vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH,
        LEFT        : vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST,
        RIGHT       : vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST,
        TOUCH_PAD   : vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_TOUCHPAD,
    }
    
    @staticmethod
    def IsNormalButton(button):
        if button not in DS4_BUTTON.TABLE.keys():
            return False
        return isinstance(DS4_BUTTON.TABLE[button], vg.DS4_BUTTONS)
    
    @staticmethod
    def IsSpecialButton(button):
        if button not in DS4_BUTTON.TABLE.keys():
            return False
        return isinstance(DS4_BUTTON.TABLE[button], vg.DS4_SPECIAL_BUTTONS)
    
    @staticmethod
    def IsDirectionalButton(button):
        if button not in DS4_BUTTON.TABLE.keys():
            return False
        return isinstance(DS4_BUTTON.TABLE[button], vg.DS4_DPAD_DIRECTIONS)
    
class DS4_STICK(BASE_STICK_6):
    pass