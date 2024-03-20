import os
import time
import pandas as pd
import schedule

from gamepad.controller_config import ControllerConfig
from gamepad.controller_input import ControllerVirtualInput
from function.utils import *

    
def ReadCSV(path):
    if not os.path.isfile(path):
        return None
    
    df = pd.read_csv(path, dtype=object)
    return df

def ReplayInput(command_df, frame_count, head_reader, controller_config, virtual_input):
    if head_reader.is_last():
        return
    
    now_time = frame_count.get_milliseconds()
        
    btn_num = controller_config.GetButtonNum()
    stk_num = controller_config.GetStickNum()

    while not head_reader.is_last():
        head_pos = head_reader.get_pos()
        time, command, arg0, arg1 = list(command_df.iloc[head_pos, :])
            
        if now_time < int(time):
            break
            
        # print(time + " : " + command + ", (" + arg0 + ", " + arg1 + ")")
        if controller_config.IsValidButtonKey(command):
            btn_idx = controller_config.GetButtonIndex(command)
            is_press = int(arg0) != 0
            virtual_input.InputButton(btn_idx, is_press)
        elif controller_config.IsValidStickKey(command):
            stk_idx = controller_config.GetStickIndex(command)
            virtual_input.InputStick(stk_idx, float(arg0), float(arg1))
        elif controller_config.IsValidHatKey(command):
            hat_idx = controller_config.GetHatIndex(command)
            virtual_input.InputHat(hat_idx, float(arg0))
                
        head_reader.increment()
        virtual_input.Update()
            
    # print("replay " + str(frame_count.get_frame()) + " : " + str(frame_count.get_time())[:-3])
    # print("replay " + str(frame_count.get_milliseconds()) + " : " + str(frame_count.get_time())[:-3])
    frame_count.update()
    
    if head_reader.is_last():
        frame_count.reset()
        head_reader.reset()
        virtual_input.Reset()
        virtual_input.Update()
    
class HeadReader:
    def __init__(self, size):
        self.pos = 0
        self.size = size
        
    def get_pos(self):
        return self.pos
        
    def increment(self):
        if self.is_last():
            return
        self.pos += 1
        
    def is_last(self):
        return self.pos == self.size
    
    def reset(self):
        self.pos = 0