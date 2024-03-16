import vgamepad as vg
from .dual_shok4 import DS4_BUTTON, DS4_STICK
from .controller_utils import BASE_INPUT

class DS4_Input(BASE_INPUT):
    gamepad = None
    BUTTON = DS4_BUTTON
    STICK = DS4_STICK
    
    def __init__(self):
        self.gamepad = vg.VDS4Gamepad()
        
    def InputButton(self, button, is_press = True):
        # print(self.BUTTON.NAME[button] + " : " + str(is_press))
        input_func = None
        if self.BUTTON.IsNormalButton(button):
            input_func = self.gamepad.press_button if is_press else self.gamepad.release_button
            button = self.BUTTON.TABLE[button]
        elif self.BUTTON.IsSpecialButton(button):
            input_func = self.gamepad.press_button if is_press else self.gamepad.release_button
            button = self.BUTTON.TABLE[button]
        elif self.BUTTON.IsDirectionalButton(button):
            input_func = self.gamepad.directional_pad
            button = self.BUTTON.TABLE[button] if is_press else vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE        
            
        if input_func is not None:
            input_func(button)
    
    def InputHat(self, hat, value):
        pass