import os
import pandas as pd
import copy

from gamepad.controller_config import ControllerConfig
from function.utils import *

def ReadCSV(path):
    if not os.path.isfile(path):
        return None
    df = pd.read_csv(path, dtype=object)
    return df

def AppendDf(df, append_dic):
    for key, value in append_dic.items():
        df.loc[(df[key].isnull() == False).sum(), key] = value

# 時刻、ボタン名、引数０、引数１
def ConvertCommand(reshape_config):
    record_df = ReadCSV(reshape_config["record_path"])

    controller_config = ControllerConfig(reshape_config["controller_type"])
    
    timestamp_header = str(record_df.columns[-1])
    header = controller_config.GetHeader() + [timestamp_header]
    init_state = [0] * len(header)
    controller_config.SetInit(init_state)
    
    reshape_header = ["time", "command", "arg0", "arg1"]
    reshape_df = df = pd.DataFrame(columns=reshape_header)
    
    old_state = copy.deepcopy(init_state)
    
    btn_num = controller_config.GetButtonNum()
    stk_num = controller_config.GetStickNum()
    hat_num = controller_config.GetHatNum()
    for _, record in record_df.iterrows():
        for idx in range(btn_num):
            name = controller_config.GetButtonName(idx)
            new_value = int(record[name])
            old_value = old_state[idx]

            if new_value == old_value:
                continue
            
            reshape_list = [list(record)[-1], name, new_value, 0]
            reshape_dic = dict(zip(reshape_header, reshape_list))
            AppendDf(reshape_df, reshape_dic)
            old_state[idx] = new_value
        
        idx = 0
        for stick_group in controller_config.GetStickGroup():
            offset = btn_num
            
            size = len(stick_group)
            name_list = []
            for i in range(size):
                name_list += [controller_config.GetStickName(idx + i)]
            
            new_value_list = []
            old_value_list = []
            for i, name in enumerate(name_list):
                new_value_list.append(float(record[name]))
                old_value_list.append(old_state[offset + idx + i])
            
            is_change = False
            for new_value, old_value in zip(new_value_list, old_value_list):
                if new_value == old_value:
                    continue
                is_change = True
                break
            
            if is_change:
                if len(new_value_list) == 1:
                    new_value_list += [0.0]
                
                reshape_list = [list(record)[-1], name_list[0], *new_value_list]
                reshape_dic = dict(zip(reshape_header, reshape_list))
                AppendDf(reshape_df, reshape_dic)
                for i in range(size):
                    old_state[offset + idx + i] = new_value_list[i]
                    
            idx += size
            
        for idx in range(hat_num):
            offset = btn_num + stk_num
            
            name = controller_config.GetHatName(idx)
            new_value = int(record[name])
            old_value = old_state[offset + idx]

            if new_value == old_value:
                continue
            
            reshape_list = [list(record)[-1], name, new_value, 0]
            reshape_dic = dict(zip(reshape_header, reshape_list))
            AppendDf(reshape_df, reshape_dic)
            old_state[offset + idx] = new_value
                
    df.to_csv(reshape_config["reshape_path"], index=False)

def Reshape(record_path):
    record_config = LoadYaml(record_path)

    dir_path = os.path.dirname(record_path) 
    record_config["reshape_path"] = os.path.join(dir_path, "command.txt")
    print(record_config)
    SaveYaml(record_path, record_config)
    
    ConvertCommand(record_config)