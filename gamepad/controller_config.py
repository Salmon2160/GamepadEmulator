from .dual_shok4 import DS4_BUTTON, DS4_STICK
from .xbox360 import XBOX360_BUTTON, XBOX360_STICK, XBOX360_HAT
from .direct_input13 import DIRECT_INPUT13_BUTTON, DIRECT_INPUT13_STICK, DIRECT_INPUT13_HAT

CONTROLLER_TYPE_LIST = [
        "DS4",
        "XBOX360",
        "DIRECT_INPUT13"
    ]

class ControllerConfig:
    controller_type = None
    BUTTON          = None
    STICK           = None
    HAT             = None
    
    def __init__(self, controller_type):
        self.controller_type = controller_type
        
        if controller_type == "DS4":
            self.BUTTON = DS4_BUTTON
            self.STICK = DS4_STICK
            self.HAT = None
        elif controller_type == "XBOX360":
            self.BUTTON = XBOX360_BUTTON
            self.STICK = XBOX360_STICK
            self.HAT = XBOX360_HAT
        elif controller_type == "DIRECT_INPUT13":
            self.BUTTON = DIRECT_INPUT13_BUTTON
            self.STICK = DIRECT_INPUT13_STICK
            self.HAT = DIRECT_INPUT13_HAT
        else:
            assert(False)
            return
    
    def GetHeader(self):
        header = []
        for dic in [self.BUTTON, self.STICK, self.HAT]:
            if dic is not None:
                header += list(dic.NAME.values())
        return header
    
    def GetButtonNum(self):
        return self.BUTTON.NUM if self.BUTTON is not None else 0

    def GetButtonName(self, button):
        if self.BUTTON is None or button not in self.BUTTON.NAME.keys():
            return ""
        return self.BUTTON.NAME[button]
    
    def GetButtonIndex(self, name):
        if self.BUTTON is None or name not in self.BUTTON.INDEX.keys():
            return 0
        return self.BUTTON.INDEX[name]
    
    def GetButtonDefault(self):
        return self.BUTTON.DEFAULT if self.BUTTON is not None else {}
    
    def GetButtonTable(self, button):
        if self.BUTTON is None or button not in self.BUTTON.TABLE.keys():
            return None
        return self.BUTTON.TABLE[button]
    
    def GetStickNum(self):
        return self.STICK.NUM if self.STICK is not None else 0

    def GetStickName(self, stick):
        if self.STICK is None or stick not in self.STICK.NAME.keys():
            return ""
        return self.STICK.NAME[stick]
    
    def GetStickIndex(self, name):
        if self.STICK is None or name not in self.STICK.INDEX.keys():
            return 0
        return self.STICK.INDEX[name]
    
    def GetStickGroup(self):
        return self.STICK.GROUP if self.STICK is not None else []
    
    def GetStickDefault(self):
        return self.STICK.DEFAULT if self.STICK is not None else {}
    
    def GetHatNum(self):
        return self.HAT.NUM if self.HAT is not None else 0
    
    def GetHatName(self, hat):
        if self.HAT is None or hat not in self.HAT.NAME.keys():
            return ""
        return self.HAT.NAME[hat]
    
    def GetHatIndex(self, name):
        if self.HAT is None or name not in self.HAT.INDEX.keys():
            return 0
        return self.HAT.INDEX[name]
    
    def GetHatDefault(self):
        return self.HAT.DEFAULT if self.HAT is not None else {}
    
    def SetInit(self, init_list):
        offset = 0
        default_list = [self.GetButtonDefault(), self.GetStickDefault(), self.GetHatDefault()]
        num_list = [self.GetButtonNum(), self.GetStickNum(), self.GetHatNum()]
        for default_dic, num in zip(default_list, num_list):
            for key, default in default_dic.items():
                init_list[offset + key] = default
            offset += num
            
    def IsValidButtonIndex(self, idx):
        return self.BUTTON is not None and 0 <= idx < self.GetButtonNum()
    
    def IsValidStickIndex(self, idx):
        return self.STICK is not None and 0 <= idx < self.GetStickNum()
    
    def IsValidHatIndex(self, idx):
        return self.HAT is not None and 0 <= idx < self.GetHatNum()

    def IsValidButtonKey(self, key):
        return self.BUTTON is not None and key in self.BUTTON.INDEX.keys()
    
    def IsValidStickKey(self, key):
        return self.STICK is not None and key in self.STICK.INDEX.keys()
    
    def IsValidHatKey(self, key):
        return self.HAT is not None and key in self.HAT.INDEX.keys()
        