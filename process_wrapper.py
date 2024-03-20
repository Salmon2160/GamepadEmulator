import os
import pygame
import schedule
import time

from multiprocessing import Process, Value, Array, Manager

from function.replay import ReplayInput, ReadCSV, HeadReader
from function.repeat import RepeatInput
from function.utils import *

from gamepad.controller_config import CONTROLLER_TYPE_LIST, ControllerConfig
from gamepad.controller_input import ControllerVirtualInput

from enum import IntEnum

class State(IntEnum):
    IDLE    = 0
    START   = 1
    UPDATE  = 2
    END     = 3
    
def create_joy(joy_index):
    pygame.joystick.init()
    joy = pygame.joystick.Joystick(joy_index)    
    print("Connect Joy : " + joy.get_name())   
    return joy

def gamepad_input(config, shared_args):   
    args_keys = shared_args.keys()
    if "replay_state" in args_keys and (shared_args["replay_state"] == State.UPDATE):
        ReplayInput(
            command_df = config["command_df"] , 
            frame_count = config["replay_frame_count"], 
            head_reader = config["head_reader"], 
            controller_config = config["controller_config"],
            virtual_input = config["virtual_input"],
        )
        
    if "repeat_state" in args_keys and (shared_args["repeat_state"] == State.UPDATE):
        RepeatInput(
            frame_count = config["repeat_frame_count"], 
            joy = config["joy"],
            controller_config = config["controller_config"],
            virtual_input = config["virtual_input"],
        )
        
def gamepad_start(shared_states, shared_args):
    pygame.init()    
    gamepad_update(shared_states, shared_args)
    pygame.quit()

def update_config(config, shared_args):
    args_keys = shared_args.keys()
    is_vgamepad_start =  "vgamepad_state" in args_keys and (shared_args["vgamepad_state"] == State.START)
    is_replay_start = "replay_state" in args_keys and (shared_args["replay_state"] == State.START)
    is_repeat_start =  "repeat_state" in args_keys and (shared_args["repeat_state"] == State.START)
    
    if is_vgamepad_start:
        vgamepad_setup(config, shared_args)
        shared_args["vgamepad_state"] = State.UPDATE
    
    if is_replay_start:
        replay_setup(config, shared_args)
        shared_args["replay_state"] = State.UPDATE
    
    if is_repeat_start:
        repeat_setup(config, shared_args)
        shared_args["repeat_state"] = State.UPDATE
    
    
# shared_args
# - controller_type
# - fps    
def vgamepad_setup(config, shared_args):
    config["controller_config"] = ControllerConfig(shared_args["controller_type"])
    config["virtual_input"] = ControllerVirtualInput(shared_args["controller_type"])
    config["fps"] = shared_args["fps"]
    
# shared_args
# - reshape_path
def replay_setup(config, shared_args):
    config["replay_frame_count"] = FrameCount()
    path = shared_args["reshape_path"]
    print(path)
    config["command_df"] = ReadCSV(path)
    config["head_reader"] = HeadReader(len(config["command_df"]))

# shared_args
# - joy_index
def repeat_setup(config, shared_args):
    config["repeat_frame_count"] = FrameCount()
    config["joy"] = create_joy(shared_args["joy_index"])
    
def is_valid_config(config):
    config_keys = config.keys()
    if "fps" not in config_keys:
            return False
    return True
    
def gamepad_update(shared_states, shared_args):
    
    config = {}
    config_keys = config.keys()
    while not is_valid_config(config):
        update_config(config, shared_args)

    schedule.Scheduler()
    schedule.every(1 / config["fps"]).seconds.do(
        gamepad_input,
        config = config,
        shared_args = shared_args, 
        )
    while shared_states[0]:
       try:
            update_config(config, shared_args)
            schedule.run_pending()
       except:
           print("catch")
           update_config(config, shared_args)
           schedule.run_pending()
           
    schedule.clear()
    
def setup_state(shared_args):
    shared_args["vgamepad_state"] = State.IDLE
    shared_args["replay_state"] = State.IDLE
    shared_args["repeat_state"] = State.IDLE
    

if __name__ == "__main__":
    pygame.init()
    joy = create_joy(0)
    print(joy)
    print(joy)
    # create_joy(1)
    pygame.quit()

    joy_index = 0
    joy_type = CONTROLLER_TYPE_LIST[joy_index]
    macro_name = "macro"
    config = {
        "joy_index"         : joy_index,
        "controller_type"   : joy_type,
        "reshape_path"      : os.path.join("output", joy_type, macro_name, "command.txt"),
        "fps"               : 1000,
    }
    
    shared_states = Array("i",[1, 0, 0, 0, 0, 0, 0])
    
    switch_args = {
        "joy_index" : [0, 2],
        "controller_type" : [CONTROLLER_TYPE_LIST[0], CONTROLLER_TYPE_LIST[1]],
    }
    
    # with Manager() as manager:
    #     shared_args = manager.dict()
    #     shared_args["joy_index"] = config["joy_index"]
    #     shared_args["controller_type"] = config["controller_type"]
    #     shared_args["reshape_path"] = config["reshape_path"]
    #     shared_args["fps"] = config["fps"]
        
    #     setup_state(shared_args)  

    #     shared_args["vgamepad_state"] = State.START
    #     shared_args["replay_state"] = State.START
    #     shared_args["repeat_state"] = State.START
    #     process = Process(target=gamepad_start, args=(shared_states, shared_args))
    #     process.start()
    
    #     try:
    #         switch = False
    #         while True: 
    #             pass

    #     except KeyboardInterrupt:
    #         print("abort")
    #         shared_states[0] = 0
    #         process.join()