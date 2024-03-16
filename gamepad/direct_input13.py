import vgamepad as vg
from function.utils import InverseDict
from .controller_utils import BASE_STICK_4, BASE_HAT

class DIRECT_INPUT13_BUTTON:
    X           = 0
    Y           = 1
    A           = 2
    B           = 3
    L1          = 4
    R1          = 5
    L2          = 6
    R2          = 7
    L3          = 8
    R3          = 9
    BACK        = 10
    START       = 11
    GUIDE       = 12
    NUM         = 13

    NAME = {
        X           : "X",
        Y           : "Y",
        A           : "A",
        B           : "B",
        L1          : "L1",
        R1          : "R1",
        L2          : "L2",
        R2          : "R2",
        L3          : "L3",
        R3          : "R3",
        BACK        : "バックボタン",
        START       : "スタートボタン",
        GUIDE       : "ガイドボタン",
    }
    
    INDEX = InverseDict(NAME)
    
    DEFAULT = {}
    
    TABLE = {
        A           : vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        B           : vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        X           : vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        Y           : vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        L1          : vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        R1          : vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        L3          : vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        R3          : vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        BACK        : vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        START       : vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        GUIDE       : vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
    }
    
    @staticmethod
    def IsL2Trigger(button):
        return button == DIRECT_INPUT13_BUTTON.L2
    
    @staticmethod
    def IsR2Trigger(button):
        return button == DIRECT_INPUT13_BUTTON.R2
    
class DIRECT_INPUT13_STICK(BASE_STICK_4):
    pass
    
class DIRECT_INPUT13_HAT(BASE_HAT):
    pass