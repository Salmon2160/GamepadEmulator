import vgamepad as vg
from .direct_input13 import DIRECT_INPUT13_BUTTON, DIRECT_INPUT13_STICK, DIRECT_INPUT13_HAT
from .controller_utils import BASE_INPUT
from function.utils import Normalize

class DIRECT_INPUT13_Input(BASE_INPUT):
    BUTTON = DIRECT_INPUT13_BUTTON
    STICK = DIRECT_INPUT13_STICK
    HAT = DIRECT_INPUT13_HAT
    
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()
        
    def InputButton(self, button, is_press = True):
        input_func = self.gamepad.press_button if is_press else self.gamepad.release_button
        if button in self.BUTTON.TABLE.keys():
            button = self.BUTTON.TABLE[button]
            input_func(button)
        elif self.BUTTON.IsL2Trigger(button):
            self.gamepad.left_trigger_float( 1 if is_press else -1)
        elif self.BUTTON.IsR2Trigger(button):
            self.gamepad.right_trigger_float(1 if is_press else -1)