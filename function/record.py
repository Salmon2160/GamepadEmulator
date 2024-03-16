import os

import pandas as pd
import schedule
import pygame

from gamepad.controller_config import ControllerConfig
from function.utils import *
from function.reshape import Reshape
    
def get_joy_index():
    try:
        pygame.init()
        joy_num = pygame.joystick.get_count()
        joy_names = []
        for i in range(joy_num):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            print("["+ str(i) +"] : " + joy.get_name())
            joy_names += [joy.get_name()]
            joy.quit()
    
        while True:
            joy_index = input('使用コントローラーを選択（インデックス指定） : ')
            if joy_index.isdecimal() and (0 <= int(joy_index) < joy_num):
                joy_index = int(joy_index)
                break
            print("無効なコントローラーを指定しています") 
        pygame.quit()
        return joy_index, joy_names[joy_index]
    except KeyboardInterrupt:
        joy.quit()
        return None, None
    
def MakeCSV(path, header):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(columns=header, dtype=object)
    df.to_csv(path, index=False)
    return df

def AppendEndRecord(record_df, init_func, time):
    init_list = [0] * len(record_df.colums)
    init_func(init_list) 
    init_list[-1] = time
    record_df.Append(init_list)
    
def RecordInput(joy, frame_count, config, record_df):
    controller_config = ControllerConfig(config["controller_type"])        
    result_header = record_df.GetDf().columns
    result_list = [0] * len(result_header)
    controller_config.SetInit(result_list) 
    result_list[-1] = frame_count.get_milliseconds()
        
    btn_num = controller_config.GetButtonNum()
    stk_num = controller_config.GetStickNum()
    
    is_save_flag = False
        
    events = pygame.event.get()
        
    for event in events:
        if event.type == pygame.JOYBUTTONDOWN: #ボタンが押された場合
            result_list[event.button] = 1
            print(controller_config.GetButtonName(event.button) + "を押しました")
            is_save_flag = True

        elif event.type == pygame.JOYBUTTONUP: #ボタンが離された場合
            print(controller_config.GetButtonName(event.button) + "を離しました")
            is_save_flag = True

        elif event.type == pygame.JOYAXISMOTION:
            idx = 0
            for stick_group in controller_config.GetStickGroup():
                size = len(stick_group)
                if size == 2:
                    valueX = joy.get_axis(idx)
                    valueY = joy.get_axis(idx + 1)
                    dist = CalcDist(valueX, valueY)
                    threshStick = 0.15
                    if dist > threshStick:
                        result_list[btn_num + idx] = valueX
                        result_list[btn_num + idx + 1] = valueY
                        stk0 = controller_config.GetStickName(idx)                            
                        stk1 = controller_config.GetStickName(idx + 1)                            
                        print(stk0 + ", " + stk1 + " : (" + str(valueX) + ", "+ str(valueY) +")")

                        is_save_flag = True
                elif size == 1:
                    value = joy.get_axis(idx)
                    threshTriger = -0.95
                    if value > threshTriger: 
                        result_list[btn_num + idx] = value
                        stk = controller_config.GetStickName(idx)
                        print(stk + " : " + str(value))
                        is_save_flag = True
                idx += size

        elif event.type == pygame.JOYHATMOTION:
            for idx in range(controller_config.GetHatNum()):
                value = event.value[idx]
                if value != 0:
                    result_list[btn_num + stk_num + idx] = value
                    hat = controller_config.GetHatName(idx)
                    print(hat + " : " + str(value))
                    is_save_flag = True

    if(is_save_flag):
        record_df.Append(result_list)
            
    # print("" + str(frame_count.get_frame()) + " : " + str(frame_count.get_time())[:-3])
    # print("" + str(frame_count.get_milliseconds()) + " : " + str(frame_count.get_time())[:-3])
                    
    frame_count.update()
        
class RecordDf():
    def __init__(self, df):
       self.df = df
       
    def Append(self, append_list):
        header = self.df.columns
        append_dic = dict(zip(header, [[item] for item in append_list]))
        append_df = pd.DataFrame(append_dic, dtype=object)
        self.df = pd.concat([self.df, append_df])

    def AppendEndRecord(self, init_func, time):
        init_list = [0] * len(self.df.columns)
        init_func(init_list) 
        init_list[-1] = time
        self.Append(init_list)
        
    def GetDf(self):
        return self.df

def Record(config, joy_index, shared_states):        
    controller_config = ControllerConfig(config["controller_type"])
    
    record_path = config[ "record_path"]
    record_df = MakeCSV(record_path, controller_config.GetHeader() + ["時刻"])
    record_df = RecordDf(record_df)
    
    FPS = config["fps"]
    pygame.init()
    joy = pygame.joystick.Joystick(joy_index)
    joy.init()
    joy_name = joy.get_name()
            
    print(joy.get_numbuttons())
    print(joy.get_numaxes())
    print(joy.get_numhats())
    frame_count = FrameCount()
            
    schedule.every(1 / FPS).seconds.do(
        RecordInput, 
        joy = joy , 
        frame_count = frame_count, 
        config = config,
        record_df = record_df,
        )
    while shared_states[0]:
        schedule.run_pending()
        shared_states[1] = frame_count.get_milliseconds()
        
    joy.quit()
    pygame.quit()
    schedule.clear()
    
    record_df.AppendEndRecord(controller_config.SetInit, frame_count.get_milliseconds())
    record_df.GetDf().to_csv(record_path, index=False)
    OUTPUT_PATH = os.path.dirname(record_path)
    OUTPUT_PATH = os.path.join(OUTPUT_PATH, "setting.yaml")
    print(config)
    SaveYaml(OUTPUT_PATH, config)
    Reshape(OUTPUT_PATH)