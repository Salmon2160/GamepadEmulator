import vgamepad as vg
from function.utils import InverseDict
from .controller_utils import BASE_STICK_6, BASE_HAT

class XBOX360_BUTTON:
    A           = 0
    B           = 1
    X           = 2
    Y           = 3
    L1          = 4
    R1          = 5
    BACK        = 6
    START       = 7
    L3          = 8
    R3          = 9
    GUIDE       = 10
    NUM         = 11

    NAME = {
        A           : "A",
        B           : "B",
        X           : "X",
        Y           : "Y",
        L1          : "L1",
        R1          : "R1",
        BACK        : "バックボタン",
        START       : "スタートボタン",
        L3          : "L3",
        R3          : "R3",
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
        BACK        : vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        START       : vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        L3          : vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        R3          : vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    }
    
class XBOX360_STICK(BASE_STICK_6):
    pass
    
class XBOX360_HAT(BASE_HAT):
    pass