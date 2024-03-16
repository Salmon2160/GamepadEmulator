import vgamepad as vg
from function.utils import InverseDict, Normalize
import copy

class BASE_STICK_4:
    LEFT_STICK_X    = 0
    LEFT_STICK_Y    = 1
    RIGHT_STICK_X   = 2
    RIGHT_STICK_Y   = 3
    NUM             = 4
    
    NAME = {
        LEFT_STICK_X    : "左スティック（X）",
        LEFT_STICK_Y    : "左スティック（Y）",
        RIGHT_STICK_X   : "右スティック（X）",
        RIGHT_STICK_Y   : "右スティック（Y）",
    }
    
    INDEX = InverseDict(NAME)
    
    GROUP = [
        [LEFT_STICK_X   , LEFT_STICK_Y ],
        [RIGHT_STICK_X  , RIGHT_STICK_Y],
    ]
    
    DEFAULT = {}
    
    @staticmethod
    def IsLeftStick(stick):
        return stick == BASE_STICK_4.LEFT_STICK_X or stick == BASE_STICK_4.LEFT_STICK_Y
    
    @staticmethod
    def IsRightStick(stick):
        return stick == BASE_STICK_4.RIGHT_STICK_X or stick == BASE_STICK_4.RIGHT_STICK_Y

class BASE_STICK_6(BASE_STICK_4):
    L2              = 4
    R2              = 5
    NUM             = 6
    
    NAME = copy.deepcopy(BASE_STICK_4.NAME)
    NAME[L2] = "L2"
    NAME[R2] = "R2"
        
    INDEX = InverseDict(NAME)
    
    GROUP = copy.deepcopy(BASE_STICK_4.GROUP)
    GROUP.append([L2])
    GROUP.append([R2])

    DEFAULT = copy.deepcopy(BASE_STICK_4.DEFAULT)
    DEFAULT[L2] = -1
    DEFAULT[R2] = -1

    @staticmethod
    def IsL2Trigger(stick):
        return stick == BASE_STICK_6.L2
    
    @staticmethod
    def IsR2Trigger(stick):
        return stick == BASE_STICK_6.R2

class BASE_HAT:
    RIGHT_LEFT  = 0
    UP_DOWN     = 1 
    NUM         = 2

    NAME = {
        RIGHT_LEFT  : "十字キー（水平）",
        UP_DOWN     : "十字キー（垂直）",
    }
    
    INDEX = InverseDict(NAME)
    
    DEFAULT = {}
    
    RIGHT   = 0
    LEFT    = 1
    UP      = 2
    DOWN    = 3
    
    TABLE = {
        RIGHT   : vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
        LEFT    : vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        UP      : vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        DOWN    : vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    }
    
    @staticmethod
    def IsHorizontal(dire):
        return dire == BASE_HAT.RIGHT_LEFT
    
    @staticmethod
    def IsVertical(dire):
        return dire == BASE_HAT.UP_DOWN
    
    @staticmethod
    def GetHorizontalButton():
        buttons = []
        buttons += [BASE_HAT.TABLE[BASE_HAT.RIGHT]]
        buttons += [BASE_HAT.TABLE[BASE_HAT.LEFT]]
        return buttons
    
    @staticmethod
    def GetVirticalButton():
        buttons = []
        buttons += [BASE_HAT.TABLE[BASE_HAT.UP]]
        buttons += [BASE_HAT.TABLE[BASE_HAT.DOWN]]
        return buttons
    
    @staticmethod
    def GetDirection(dire, value):
        if BASE_HAT.IsHorizontal(dire):
            if value > 0:
                return BASE_HAT.RIGHT
            elif value < 0:
                return BASE_HAT.LEFT
        elif BASE_HAT.IsVertical(dire):
            if value > 0:
                return BASE_HAT.UP
            elif value < 0:
                return BASE_HAT.DOWN
        return None
    
    @staticmethod
    def GetButton(dire, value):
        dire = BASE_HAT.GetDirection(dire, value)
        return BASE_HAT.TABLE[dire] if dire in BASE_HAT.TABLE.keys() else None

class BASE_INPUT:
    gamepad = None
    BUTTON = None
    STICK = None
    HAT = None
    
    IsHorizontalFlip = False
    IsVertivalFlip = False
    
    def __init__(self):
        pass
    
    def InputButton(self, button, is_press = True):
        if self.gamepad is None:
            return
        input_func = self.gamepad.press_button if is_press else self.gamepad.release_button
        button = self.BUTTON.TABLE[button]
        input_func(button)
    
    def InputStick(self, stick, valueA, valueB = None):
        if self.gamepad is None:
            return
        if self.STICK.IsLeftStick(stick):
            valueA, valueB = self.ReshapeLRStickValue(valueA, valueB)
            self.gamepad.left_joystick_float(valueA, valueB)
        elif self.STICK.IsRightStick(stick):
            valueA, valueB = self.ReshapeLRStickValue(valueA, valueB)
            self.gamepad.right_joystick_float(valueA, valueB)
        elif self.STICK.IsL2Trigger(stick):
            self.gamepad.left_trigger_float(Normalize(valueA, -1, 1))
        elif self.STICK.IsR2Trigger(stick):
            self.gamepad.right_trigger_float(Normalize(valueA, -1, 1))          
    
    def InputHat(self, hat, value):
        if self.gamepad is None:
            return
        reset_buttons = []
        if self.HAT.IsHorizontal(hat):
            reset_buttons += self.HAT.GetHorizontalButton()
        if self.HAT.IsVertical(hat):
            reset_buttons += self.HAT.GetVirticalButton()  
        if len(reset_buttons) == 0:
            reset_buttons += self.HAT.GetHorizontalButton()
            reset_buttons += self.HAT.GetVirticalButton()
        for reset_button in reset_buttons:
            self.gamepad.release_button(reset_button)

        button = self.HAT.GetButton(hat, value)
        if button is not None:
            self.gamepad.press_button(button)
         
    def Update(self):
        if self.gamepad is not None:
            self.gamepad.update()
        
    def Reset(self):
        if self.gamepad is not None:
            self.gamepad.reset()

    @staticmethod        
    def FlipValue(value, is_flip = False):
        return value if not is_flip else -1 * value
    
    def ReshapeLRStickValue(self, valueX, valueY):
        valueX = self.FlipValue(valueX, self.IsHorizontalFlip)
        valueY = self.FlipValue(valueY, self.IsVertivalFlip)
        return valueX, valueY