import os
import time
import pygame
import vgamepad as vg
from multiprocessing import Process, Value, Array

from function.record import Record
from function.replay import Replay

if __name__ == "__main__": 
    joy_index = 1
    pygame.init()
    joy = pygame.joystick.Joystick(joy_index)
    joy.init()
    joy_name = joy.get_name()
    print(joy_name)
    joy.quit()
   
    macro_name = "macro"
    config = {
        "controller_type"   : "DS4",
        "result_path"       : os.path.join("output", joy_name, macro_name, "record.txt"),
        "fps"               : 60,
    }

    # active_flag, passed_milliseconds, arg2, arg3
    shared_states = Array('i', [1, 0, 0, 0])
    
    process = Process(target=Record, args=(config, joy_index, shared_states))
    process.start()
    print("start record")
    
    while shared_states[1] < 500:
        pass
    
    # 凡そ30msec後に終了（2030msec～に最後のタイムスタンプが記録される）
    print("deactivate record")
    shared_states[0] = 0
    process.join()
    print("finish record")  
    
    # active_flag, replay_num, arg2, arg3
    shared_states = Array('i', [1, 0, 0, 0])
    
    print("start replay")
    RESHAPE_DIRE = os.path.dirname(config["result_path"])
    RESHAPE_PATH = os.path.join(RESHAPE_DIRE, "reshape.yaml")
    print(RESHAPE_PATH)
    process = Process(target=Replay, args=(RESHAPE_PATH, shared_states))
    process.start()
    
    while shared_states[1] < 3:
        pass
    
    print("deactivate replay")
    shared_states[0] = 0
    process.join()
    print("finish replay")
    print(shared_states[1])