import vgamepad as vg
from .controller_config import ControllerConfig, CONTROLLER_TYPE_LIST
from .dual_shok4_input import DS4_Input
from .xbox_input import XBOX360_Input
from .direct_input13_input import DIRECT_INPUT13_Input

class ControllerVirtualInput:
    controller_type = None
    gamepad = None
    
    def __init__(self, controller_type):
        self.controller_type = controller_type
        self.controller_config = ControllerConfig(controller_type)
        
        if controller_type == CONTROLLER_TYPE_LIST[0]:
            self.gamepad = DS4_Input()
        elif controller_type == CONTROLLER_TYPE_LIST[1]:
            self.gamepad = XBOX360_Input()
        elif controller_type == CONTROLLER_TYPE_LIST[2]:
            self.gamepad = DIRECT_INPUT13_Input()
        else:
            self.gamepad = DS4_Input()
            
        print("Create Virtual Controller : " + controller_type)
    
    def InputButton(self, button, is_press = True):
        if self.controller_config.IsValidButtonIndex(button):
            self.gamepad.InputButton(button, is_press)
    
    def InputStick(self, stick, valueA, valueB = None):
        if self.controller_config.IsValidStickIndex(stick):
            self.gamepad.InputStick(stick, valueA, valueB)
    
    def InputHat(self, hat, value):
        if self.controller_config.IsValidHatIndex(hat):
            self.gamepad.InputHat(hat, value)
        
    def Update(self):
        self.gamepad.Update()
        
    def Reset(self):
        self.gamepad.Reset()