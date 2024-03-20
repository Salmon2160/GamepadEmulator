import datetime
import math
import os
import yaml
import copy

class FrameCount:
    def __init__(self):
        self.frame = 0
        self.dt_old = datetime.datetime.now()
        self.dt_start = copy.deepcopy(self.dt_old)
        self.old_delta = 0
        
    def update(self):
        self.frame += 1
        self.dt_old = datetime.datetime.now()
        
    def get_frame(self):
        return self.frame
    
    def get_time(self):
        return datetime.datetime.now() - self.dt_old
    
    def reset(self):
        self.frame = 0
        self.dt_old = datetime.datetime.now()
        self.dt_start = copy.deepcopy(self.dt_old)
        
    def get_milliseconds(self):
        new = int((datetime.datetime.now() - self.dt_start).total_seconds() *1000)
        # print("delta : " + str(new - self.old_delta))
        self.old_delta = new
        return int((datetime.datetime.now() - self.dt_start).total_seconds() *1000)

def InverseDict(d):
    return {v:k for k,v in d.items()}

def CalcDist(x, y):
    return math.pow(x*x + y*y, 0.5)

def LoadYaml(path):
    if os.path.exists(path):
        with open(path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    return None

def SaveYaml(path, dic):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except:
        pass
    
    with open(path, 'w') as file:
            yaml.dump(dic, file)
            
def Normalize(value, min, max):
    return (value - min) / (max - min) 