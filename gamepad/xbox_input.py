import vgamepad as vg
from .xbox360 import XBOX360_BUTTON, XBOX360_STICK, XBOX360_HAT
from .controller_utils import BASE_INPUT
from function.utils import Normalize

class XBOX360_Input(BASE_INPUT):
    BUTTON = XBOX360_BUTTON
    STICK = XBOX360_STICK
    HAT = XBOX360_HAT
    
    IsVertivalFlip = True
    
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()