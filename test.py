import os
import time
import pygame
import vgamepad as vg
import schedule

from multiprocessing import Process, Value, Array

from function.record import Record
from function.replay import Replay, ReplayInput, ReadCSV, HeadReader
from function.repeat import Repeat, RepeatInput
from function.utils import *

from gamepad.controller_config import CONTROLLER_TYPE_LIST, ControllerConfig
from gamepad.controller_input import ControllerVirtualInput


import threading

def send_vgamepad(shared_states):
    joy_index = 0
    pygame.init()
    pygame.joystick.init()
    joy = pygame.joystick.Joystick(joy_index)
    
    joy_type = CONTROLLER_TYPE_LIST[0]
    macro_name = "macro"
    config = {
        "controller_type"   : joy_type,
        "reshape_path"       : os.path.join("output", joy_type, macro_name, "command.txt"),
        "fps"               : 60,
    }
    gamepad_input = ControllerVirtualInput(joy_type, 1)

    config["virtual_input"] = gamepad_input
    config["fps"] = 10000
    config["joy"] = joy
    
    Repeat(config, shared_states)
    
def merge_input(command_df, frame_count, head_reader, controller_config, virtual_input, config):
    ReplayInput(
            command_df = command_df , 
            frame_count = frame_count, 
            head_reader = head_reader, 
            controller_config = controller_config,
            virtual_input = virtual_input,
        )
        
    RepeatInput(
        frame_count,
        config
    )
    
def merge(config, shared_states):
    command_df = ReadCSV(config["reshape_path"])
    frame_count = FrameCount()
    head_reader = HeadReader(len(command_df))
    virtual_input = config["virtual_input"]
    controller_config = ControllerConfig(virtual_input.controller_type)
    joy = config["joy"]
    
    FPS = config["fps"]
    
    schedule.Scheduler()
    schedule.every(1 / FPS).seconds.do(
        merge_input,
        command_df = command_df, 
        frame_count = frame_count, 
        head_reader = head_reader, 
        controller_config = controller_config, 
        virtual_input = virtual_input, 
        config = config
        )
    while shared_states[0]:
        # update‚ª•K—v
        # merge_input(command_df, frame_count, head_reader, controller_config, virtual_input, config)
        schedule.run_pending()
    

def process_merge(shared_states):
    joy_index = 0
    pygame.init()
    pygame.joystick.init()
    joy = pygame.joystick.Joystick(joy_index)
    joy_name = joy.get_name()
    print(joy_name)
    
    joy_type = CONTROLLER_TYPE_LIST[0]
    macro_name = "macro"
    config = {
        "controller_type"   : joy_type,
        "reshape_path"       : os.path.join("output", joy_type, macro_name, "command.txt"),
        "fps"               : 60,
    }
    
    gamepad_input = ControllerVirtualInput(joy_type)
    gamepad = gamepad_input.gamepad.gamepad
    # print(vars(gamepad.vbus))
    
    config["virtual_input"] = gamepad_input
    config["fps"] = 60
    config["joy"] = joy
    
    merge(config, shared_states)

if __name__ == "__main__": 
    joy_index = 0
    pygame.init()
    pygame.joystick.init()
    joy = pygame.joystick.Joystick(joy_index)
    joy_name = joy.get_name()
    print(joy_name)
   
    # active_flag, passed_milliseconds, arg2, arg3
    # shared_states = [1, 0, 0, 0, 0, 0, 0]
    shared_states = Array("i",[1, 0, 0, 0, 0, 0, 0])
    
    joy_type = CONTROLLER_TYPE_LIST[0]
    macro_name = "macro"
    config = {
        "controller_type"   : joy_type,
        "reshape_path"       : os.path.join("output", joy_type, macro_name, "command.txt"),
        "fps"               : 60,
    }
    
    gamepad_input = ControllerVirtualInput(joy_type)
    gamepad = gamepad_input.gamepad.gamepad
    # print(vars(gamepad.vbus))
    
    config["virtual_input"] = gamepad_input
    config["fps"] = 60
    
    processA = threading.Thread(target=Replay, args=(config, shared_states))
    # processA = Process(target=send_vgamepad, args=(shared_states, ))
    # processA = threading.Thread(target=send_vgamepad, args=(shared_states, ))
    # processA.start()
    
    config["joy"] = joy
    processB = threading.Thread(target=Repeat, args=(config, shared_states))
    # processB.start()
    
    # merge(config, shared_states)
    # processC = threading.Thread(target=merge, args=(config, shared_states))
    processC = Process(target=process_merge, args=(shared_states, ))
    processC.start()
    
    try:
        while True: 
            pass
    except KeyboardInterrupt:
        shared_states[0] = 0
        processA.join()
        processB.join()
        processC.join()
        pygame.quit()