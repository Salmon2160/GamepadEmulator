import os

import pandas as pd
import schedule
import pygame

from gamepad.controller_config import ControllerConfig
from function.utils import *

    
def RepeatInput(frame_count, joy, controller_config, virtual_input):
        
    btn_num = controller_config.GetButtonNum()
    stk_num = controller_config.GetStickNum()
    
    is_any_press = False
    
    events = pygame.event.get()
        
    for event in events:
        if event.type == pygame.JOYBUTTONDOWN: #ボタンが押された場合
            btn_idx = event.button 
            if not controller_config.IsValidButtonIndex(btn_idx):
                continue
            virtual_input.InputButton(btn_idx, True)
            # print(controller_config.GetButtonName(event.button) + "を押しました")
            is_any_press = True

        elif event.type == pygame.JOYBUTTONUP: #ボタンが離された場合
            btn_idx = event.button 
            if not controller_config.IsValidButtonIndex(btn_idx):
                continue
            virtual_input.InputButton(btn_idx, False)
            # print(controller_config.GetButtonName(event.button) + "を離しました")
            is_any_press = True

        elif event.type == pygame.JOYAXISMOTION:
            idx = 0
            for stick_group in controller_config.GetStickGroup():
                size = len(stick_group)
                if size == 2:
                    valueX = joy.get_axis(idx)
                    valueY = joy.get_axis(idx + 1)
                    dist = CalcDist(valueX, valueY)
                    threshStick = 0.00
                    if dist >= threshStick:
                        if not controller_config.IsValidStickIndex(idx):
                            continue
                        virtual_input.InputStick(idx, valueX, valueY)
                        stk0 = controller_config.GetStickName(idx)                            
                        stk1 = controller_config.GetStickName(idx + 1)
                        # print(stk0 + ", " + stk1 + " : (" + str(valueX) + ", "+ str(valueY) +")")
                        is_any_press = True
                        
                elif size == 1:
                    value = joy.get_axis(idx)
                    threshTriger = -1.00
                    if value >= threshTriger:
                        if not controller_config.IsValidStickIndex(idx):
                            continue
                        virtual_input.InputStick(idx, value, 0.0)
                        stk = controller_config.GetStickName(idx)
                        # print(stk + " : " + str(value))
                        is_any_press = True
                        
                idx += size

        elif event.type == pygame.JOYHATMOTION:
            for idx in range(controller_config.GetHatNum()):
                value = event.value[idx]
                if not controller_config.IsValidHatIndex(idx):
                        continue
                virtual_input.InputHat(idx, value)
                hat = controller_config.GetHatName(idx)
                # print(hat + " : " + str(value))
                is_any_press = True

    if is_any_press:
        virtual_input.Update()
        
    # print("repeat " + str(frame_count.get_frame()) + " : " + str(frame_count.get_time())[:-3])
    # print("repeat " + str(frame_count.get_milliseconds()) + " : " + str(frame_count.get_time())[:-3])
                    
    frame_count.update()