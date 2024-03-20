#!/usr/bin/python -S
# coding: utf-8

# 環境設定より、pygameのウェルカムメッセージを非表示に設定
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from PIL import Image,ImageTk
import os
import sys
import pygame
from multiprocessing import Process, Array, freeze_support, Manager
import subprocess
import webbrowser

from function.record import Record
from function.utils import *
from gamepad.controller_config import CONTROLLER_TYPE_LIST, ControllerConfig
from process_wrapper import State, gamepad_start

SELECTABLE_BASE_FPS = 60
SELECTABLE_FPS_LIST = [1, 2, 5, 15, 30, 60, 120, 240, 480, 960]
VGAMEPAD_DEFOULT_FPS = 2000
OUTPUT_PATH = "output"
DEFAULT_FONT=("", 12)
DEFOULT_DELAY_TIME = 0.1
SETTING_PATH = "setting.yaml"

def get_init_shared_states():
    return Array('i', [1, 0, 0, 0, 0, 0, 0])

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_joy_name_list():
    pygame.init()
    joy_num = pygame.joystick.get_count()
    pygame.quit()            
    joy_names = []
    for i in range(joy_num):
        joy_names += [get_joy_name_from_index(i)]
    return joy_names

def get_joy_name_from_index(joy_index):
    pygame.init()
    pygame.joystick.init()
    
    if joy_index >= pygame.joystick.get_count():
        return ""
    
    joy = pygame.joystick.Joystick(joy_index)
    joy.init()
    joy_name = joy.get_name()
    joy.quit()

    pygame.quit()
    return joy_name

def get_joy_index_from_name(target_joy_name):
    pygame.init()
    pygame.joystick.init()
    
    joy_num = pygame.joystick.get_count()
    for joy_index in range(joy_num):
        joy = pygame.joystick.Joystick(joy_index)
        joy.init()
        joy_name = joy.get_name()
        joy.quit()

        if joy_name == target_joy_name:
            pygame.quit()
            return joy_index
        
    pygame.quit()
    return 0

def start_record(joy_index, controller_type, macro_name, fps):
   
    config = {
        "controller_type"   : controller_type,
        "record_path"       : os.path.join(OUTPUT_PATH, controller_type, macro_name, "record.txt"),
        "fps"               : fps,
    }

    # active_flag, passed_milliseconds, ...
    shared_states = get_init_shared_states()
    
    process = Process(target=Record, args=(config, joy_index, shared_states))
    process.start()
    print("Start Record")
    
    return process, shared_states

def end_record(process, shared_states):
    shared_states[0] = 0
    process.join()
    print("Finish Record : " + str(shared_states[1]))
    
    process = None
    shared_states = None
    
def start_vgamepad(shared_args, controller_type, fps):
    shared_args["controller_type"] = controller_type
    shared_args["fps"] = fps
    shared_args["vgamepad_state"] = State.START
    print("Start VGamepad")

def start_replay(shared_args, reshape_path):
    shared_args["reshape_path"] = reshape_path
    shared_args["replay_state"] = State.START
    print("Start Replay")

def end_replay(shared_args):
    shared_args["replay_state"] = State.IDLE
    print("Finish Replay")
    
def start_repeat(shared_args, joy_index):
    shared_args["joy_index"] = joy_index
    shared_args["repeat_state"] = State.START
    print("Start Repeat")

def end_repeat(shared_args):
    shared_args["repeat_state"] = State.IDLE
    print("Finish Repeat")
    
def setup_process_dict(process_dict):
    process_dict["record"] = None
    process_dict["vgamepad"] = None
    
def setup_shared_states_dict(shared_states_dict):
    shared_states_dict["record"] = None
    shared_states_dict["vgamepad"] = None
    
def setup_shared_args_dict(shared_args_dict):
    manager =  Manager()
    shared_args_dict["vgamepad"] = manager.dict()
    return manager

class main_frm(Frame):

    def __init__(self, master):
        super().__init__(master=master)
        self.master = master
        self.grid(column=0, row=0, sticky=(N, S, W, E)) # capture_frmをマスターウィンドウに貼り付ける
        self.make_widget()

        self.process_dict = {}
        setup_process_dict(self.process_dict)
        
        self.shared_states_dict = {}
        setup_shared_states_dict(self.shared_states_dict)
        
        self.shared_args_dict = {}
        self.shared_manager = setup_shared_args_dict(self.shared_args_dict)
        
        self.shared_states_dict["vgamepad"] = get_init_shared_states()
        self.process_dict["vgamepad"] = Process(target=gamepad_start, args=(self.shared_states_dict["vgamepad"], self.shared_args_dict["vgamepad"]))
        self.process_dict["vgamepad"].start()
        
        self.master.register_finish(self.finish)
        
        self.setting_dic = {
                "joy_name" : get_joy_name_from_index(0),
                "controller_type" : CONTROLLER_TYPE_LIST[0]
        }
        if os.path.isfile(SETTING_PATH):
            self.setting_dic = LoadYaml(SETTING_PATH)
        else:
            SaveYaml(SETTING_PATH, self.setting_dic)

        self.active_config(get_joy_index_from_name(self.setting_dic["joy_name"]), self.setting_dic["controller_type"])
        
    def finish(self):
        for key in self.process_dict.keys():
            if self.process_dict[key] is None:
                continue
            self.shared_states_dict[key][0] = 0
            self.process_dict[key].join()

    # フレームやボタンの配置
    def make_widget(self):
        self.operation_frm = Frame(
            self,
            background="white",
            relief="ridge",
            borderwidth=2
        )
        self.operation_frm.grid(column=0, row=0, sticky=(N, W, E))

        icon_size = [45, 45]  # icon の大きさ
        self.icon_img_list = {
            # tkinterのPhotoImageは「画像を表示しつづけている間、アプリケーションでPhotoImageインスタンスの参照をどこかにキープしておかなければならない」
            # 以下のアイコンのライセンスは完全無料なので、商業用途でも利用できる
            "record"    : ImageTk.PhotoImage(Image.open(resource_path(".\\image\\movie_icon2.png")).resize(icon_size)),
            "recording" : ImageTk.PhotoImage(Image.open(resource_path(".\\image\\movie_icon1.png")).resize(icon_size)),
            "replay"    : ImageTk.PhotoImage(Image.open(resource_path(".\\image\\play_icon2.png")).resize(icon_size)),
            "replaying" : ImageTk.PhotoImage(Image.open(resource_path(".\\image\\stop_icon1.png")).resize(icon_size)),
            "config"    : ImageTk.PhotoImage(Image.open(resource_path(".\\image\\config_icon.png")).resize(icon_size)),
        }

        self.button_dict = {} # ボタン変数を格納
        self.button_state_dict = {} # ボタンの状態（enable or disable）を記録
        self.button_activate_func = {}
        self.button_deactivate_func = {}

        # 記録ボタン
        record_key = "record_button"
        self.button_dict[record_key] = ttk.Button(
            self.operation_frm,
            image=self.icon_img_list["record"],
            text="記憶",
            compound=TOP,
            style="TButton",
            command=lambda: self.callback_button(record_key),
        )
        self.button_dict[record_key].grid(column=0, row=0, sticky=(N, S))
        self.button_state_dict[record_key] = False
        self.button_activate_func[record_key] = self.active_record_button
        self.button_deactivate_func[record_key] = self.deactive_record_button
        self.record_button_key = record_key
        
        # 再生ボタン
        replay_key = "replay_button"
        self.button_dict[replay_key] = ttk.Button(
            self.operation_frm,
            image=self.icon_img_list["replay"],
            text="再生",
            compound=TOP,
            style="TButton",
            command=lambda: self.callback_button(replay_key),
        )
        self.button_dict[replay_key].grid(column=1, row=0, sticky=(N, S))
        self.button_state_dict[replay_key] = False
        self.button_activate_func[replay_key] = self.active_replay_button
        self.button_deactivate_func[replay_key] = self.deactive_replay_button
        self.replay_key = replay_key
        
        # 設定ボタン
        config_key = "config_button"
        self.button_dict[config_key] = ttk.Button(
            self.operation_frm,
            image=self.icon_img_list["config"],
            text="設定",
            compound=TOP,
            style="TButton",
            command=lambda: self.callback_button(config_key),
        )
        self.button_dict[config_key].grid(column=2, row=0, sticky=(N, S))
        self.button_state_dict[config_key] = False
        self.button_activate_func[config_key] = self.active_config_button
        self.button_deactivate_func[config_key] = self.deactive_config_button
        self.config_key = config_key

    def callback_button(self, button_key):
        # 他のボタンの状態に依存する場合は、ここで条件を追加する
        if not self.button_state_dict[button_key]:
            self.button_activate_func[button_key]()
        else:
            self.button_state_dict[button_key] = False
            self.button_deactivate_func[button_key]()
            
    def active_record_button(self):
        record_setting_win(self)

    def active_record(self, record_input):
        record_input.insert(0, self.shared_args_dict["vgamepad"]["joy_index"])
        record_input.insert(1, self.shared_args_dict["vgamepad"]["controller_type"])
        self.process_dict["record"], self.shared_states_dict["record"] = start_record(*record_input)
        
        button_key = self.record_button_key
        self.button_dict[button_key]["image"]   = self.icon_img_list["recording"]
        self.button_dict[button_key]["text"]    = "終了"
        self.button_state_dict[button_key]      = True
        self.deactivate_all_button([button_key])
    
    def deactive_record_button(self):
        self.deactive_record()
        
    def deactive_record(self):
        if self.process_dict["record"]:
            end_record(self.process_dict["record"], self.shared_states_dict["record"])
        button_key = self.record_button_key
        self.button_dict[button_key]["image"]   = self.icon_img_list["record"]
        self.button_dict[button_key]["text"]    = "記録"
        self.button_state_dict[button_key]      = False
        self.activate_all_button()
    
    def active_replay_button(self):
        replay_setting_win(self)
    
    def active_replay(self, replay_input):
        config = LoadYaml(replay_input[0])
        reshape_path = config["reshape_path"]
        if not os.path.isfile(reshape_path):
            print("Not Found command.txt in setting.yaml: " + reshape_path)
        
        start_replay(self.shared_args_dict["vgamepad"], reshape_path)

        button_key = self.replay_key
        self.button_dict[button_key]["image"]   = self.icon_img_list["replaying"]
        self.button_dict[button_key]["text"]    = "終了"
        self.button_state_dict[button_key]      = True
        self.deactivate_all_button([button_key])
    
    def deactive_replay_button(self):
        self.deactive_replay()
    
    def deactive_replay(self):
        if self.process_dict["vgamepad"] is not None:
            end_replay(self.shared_args_dict["vgamepad"])
            
        button_key = self.replay_key
        self.button_dict[button_key]["image"]   = self.icon_img_list["replay"]
        self.button_dict[button_key]["text"]    = "再生"
        self.button_state_dict[button_key]      = False
        self.activate_all_button()
        
    def active_config_button(self):
        setting_setting_win(self)
        
    def active_config(self, joy_index, controller_type):
        setting_dic = LoadYaml(SETTING_PATH)
        
        if ((get_joy_name_from_index(joy_index) != self.setting_dic["joy_name"])
            or (controller_type != self.setting_dic["controller_type"])):
            self.setting_dic["joy_name"] = get_joy_name_from_index(joy_index)
            self.setting_dic["controller_type"] = controller_type
            SaveYaml(SETTING_PATH, self.setting_dic)
        
        if ((self.process_dict["vgamepad"] is None) 
            or ("joy_index" not in self.shared_args_dict["vgamepad"]) 
            or ("controller_type" not in self.shared_args_dict["vgamepad"]) 
            or (joy_index != self.shared_args_dict["vgamepad"]["joy_index"])
            or (controller_type != self.shared_args_dict["vgamepad"]["controller_type"])):
            
            start_vgamepad(self.shared_args_dict["vgamepad"], controller_type, VGAMEPAD_DEFOULT_FPS)
            end_replay(self.shared_args_dict["vgamepad"])
            start_repeat(self.shared_args_dict["vgamepad"], joy_index)
        
    def deactive_config_button(self):
        pass
    
    def activate_all_button(self, except_key_list = []):
        for key, value in self.button_dict.items():
            if key in except_key_list:
                continue
            value.configure(state="normal")

    def deactivate_all_button(self, except_key_list = []):
        for key, value in self.button_dict.items():
            if key in except_key_list:
                continue
            value.configure(state="disabled")
            
    def get_vgamepad_type(self):
        controller_type = self.shared_args_dict["vgamepad"]["controller_type"]
        return controller_type
    
    def get_joy_name(self):
        joy_index = self.shared_args_dict["vgamepad"]["joy_index"]
        joy_name = get_joy_name_from_index(joy_index)
        return joy_name
    
class record_setting_win(Toplevel):
    def __init__(self,master):
        self.master = master
        super().__init__(master=master)
        self.make_widget()

        # サイズ固定
        self.wm_resizable(False, False)

    def make_widget(self):
        def _on_closing():  # ウィンドウの右上の✖アイコンから閉じるときの処理（ウィンドウを閉じる処理を書き換える）
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", _on_closing)  # ウィンドウを閉じる処理を書き換える
        
        setting_frm = Frame(
            self,
            relief="ridge",
            borderwidth=2,
        )
        setting_frm.grid(column=0, row=0, sticky=(N, S, W, E))
        
        # text setting
        text_sticky = (N, S, W)
        
        text_label = ttk.Label(
            setting_frm,
            text="FPS",
            font=DEFAULT_FONT,
        )
        text_label.grid(column=0, row=0, sticky=text_sticky)
        
        text_label = ttk.Label(
            setting_frm,
            text="保存先マクロ名",
            font=DEFAULT_FONT,
        )
        text_label.grid(column=0, row=1, sticky=text_sticky)

        # input setting
        input_sticky = (N, S, W)
        
        # FPSの選択
        self.fps_combo_box = ttk.Combobox(
            setting_frm,
            font=DEFAULT_FONT,
            state="readonly"  # コンボボックスからの選択のみ（プルダウン式）
        )
        self.fps_combo_box["values"] = SELECTABLE_FPS_LIST
        self.fps_combo_box.current(SELECTABLE_FPS_LIST.index(SELECTABLE_BASE_FPS))
        self.fps_combo_box.grid(column=1, row=0, sticky=input_sticky)
        
        # マクロ名の入力
        self.macro_name_entry = ttk.Entry(
            setting_frm,
            font=DEFAULT_FONT,
        )
        self.macro_name_entry.insert(0, "macro")
        self.macro_name_entry.grid(column=1, row=1, sticky=input_sticky)

        self.decide_button = Button(
            self,
            text='記録開始',
            command=lambda: self.decide_record(),
            font=DEFAULT_FONT,
            padx=15,
        )
        self.decide_button.grid(column=0, row=1, sticky=(N, S, E))

        """ フォーカス """
        self.transient(self.master)
        self.grab_set()

    # 決定ボタンの処理
    def decide_record(self):
        # record
        record_input  = []
        record_input += [self.macro_name_entry.get()]
        record_input += [int(self.fps_combo_box.get())]
        
        # input [macro_name, fps]
        self.master.active_record(record_input)
        self.destroy() # ウィンドウの削除

class replay_setting_win(Toplevel):
    def __init__(self,master):
        self.master = master
        super().__init__(master=master)
        self.make_widget()
        
        # サイズ固定
        self.wm_resizable(False, False)

    def make_widget(self):
        def _on_closing():  # ウィンドウの右上の✖アイコンから閉じるときの処理（ウィンドウを閉じる処理を書き換える）
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", _on_closing)  # ウィンドウを閉じる処理を書き換える
        
        setting_frm = Frame(
            self,
            relief="ridge",
            borderwidth=2,
        )
        setting_frm.grid(column=0, row=0, sticky=(N, S, W, E))
        
        # text setting
        text_sticky = (N, S, W)
        text_label = ttk.Label(
            setting_frm,
            width=10,
            font=DEFAULT_FONT,
            text="再生マクロ",
        )
        text_label.grid(column=0, row=0, sticky=text_sticky)

        # input setting
        input_sticky = (N, S, W)
        
        # マクロの選択
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH, exist_ok=True)

        controller_type = self.master.get_vgamepad_type()
        controller_path = os.path.join(OUTPUT_PATH, controller_type)
        macro_path_list = [os.path.join(controller_path, f) for f in os.listdir(controller_path) if os.path.isdir(os.path.join(controller_path, f))]
        self.macro_path_combo_box = ttk.Combobox(
            setting_frm,
            width=50,
            font=DEFAULT_FONT,
            state="readonly",  # コンボボックスからの選択のみ（プルダウン式）
        )
        self.macro_path_combo_box["values"] = macro_path_list
        if len(macro_path_list) > 0:
            self.macro_path_combo_box.current(0)
        self.macro_path_combo_box.grid(column=1, row=0, sticky=input_sticky)

        self.decide_button = Button(
            self,
            text='再生開始',
            command=lambda: self.decide_replay(),
            font=DEFAULT_FONT,
            padx=15,
        )
        self.decide_button.grid(column=0, row=1, sticky=(N, S, E))

        """ フォーカス """
        self.transient(self.master)
        self.grab_set()

    # 決定ボタンの処理
    def decide_replay(self):
        # replay
        replay_input  = []
        macro_path = self.macro_path_combo_box.get()
        replay_path = os.path.join(macro_path, "setting.yaml")
        is_valid_path = True
        if not os.path.isfile(replay_path):
            is_valid_path = False
        
        is_valid_replay_path = os.path.isfile(replay_path)
        if is_valid_replay_path:       
            config = LoadYaml(replay_path)
            is_valid_replay_path = "reshape_path" in config.keys() and os.path.isfile(config["reshape_path"])
        
        if not is_valid_replay_path:
            # 設定ファイルが無効なのでキャンセル
            messagebox.showerror('選択エラー', '有効なマクロが選択されていません。')
            self.master.deactive_replay()
            return

        replay_input += [replay_path] 

        # input [replay_input_path]
        self.master.active_replay(replay_input)
        self.destroy()
     
class setting_setting_win(Toplevel):
    def __init__(self,master):
        self.master = master
        super().__init__(master=master)
        self.make_widget()
        
        # サイズ固定
        self.wm_resizable(False, False)

    def make_widget(self):
        def _on_closing():  # ウィンドウの右上の✖アイコンから閉じるときの処理（ウィンドウを閉じる処理を書き換える）
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", _on_closing)  # ウィンドウを閉じる処理を書き換える
        
        setting_frm = Frame(
            self,
            relief="ridge",
            borderwidth=2,
        )
        setting_frm.grid(column=0, row=0, sticky=(N, S, W, E))
        
        # text setting
        text_sticky = (N, S, W)
        text_label = ttk.Label(
            setting_frm,
            text="入力コントローラー",
            font=DEFAULT_FONT,
        )
        text_label.grid(column=0, row=0, sticky=text_sticky)
        
        text_label = ttk.Label(
            setting_frm,
            text="仮想コントローラー",
            font=DEFAULT_FONT,
        )
        text_label.grid(column=0, row=1, sticky=text_sticky)
        
        text_label = ttk.Label(
            setting_frm,
            text="HidHide 設定",
            font=DEFAULT_FONT,
        )
        text_label.grid(column=0, row=2, sticky=text_sticky)

        text_label = ttk.Label(
            setting_frm,
            text="接続確認（Gamepad Tester）",
            font=DEFAULT_FONT,
        )
        text_label.grid(column=0, row=3, sticky=text_sticky)

        # input setting
        # 入力コントローラーの選択
        input_sticky = (N, S, W)
        self.input_controller_combo_box = ttk.Combobox(
            setting_frm,
            font=DEFAULT_FONT,
            state="readonly"  # コンボボックスからの選択のみ（プルダウン式）
        )
        
        joy_name_list = get_joy_name_list()
        if len(joy_name_list) == 0:
            joy_name_list += [""]
        self.input_controller_combo_box["values"] = joy_name_list
        self.input_controller_combo_box.set(self.master.get_joy_name())
        self.input_controller_combo_box.grid(column=1, row=0, sticky=input_sticky)

        # 仮想コントローラーの選択
        self.virtual_controller_type_combo_box = ttk.Combobox(
            setting_frm,
            font=DEFAULT_FONT,
            state="readonly"  # コンボボックスからの選択のみ（プルダウン式）
        )
        self.virtual_controller_type_combo_box["values"] = CONTROLLER_TYPE_LIST
        self.virtual_controller_type_combo_box.set(self.master.get_vgamepad_type())
        self.virtual_controller_type_combo_box.grid(column=1, row=1, sticky=input_sticky)
        
        # HidHideボタン
        self.hid_hide_button  = Button(
            setting_frm,
            text='開く',
            command=lambda: subprocess.Popen(r"C:\Program Files\Nefarius Software Solutions\HidHide\x64\HidHideClient.exe"),
            font=DEFAULT_FONT,
            padx=15,
        )
        self.hid_hide_button.grid(column=1, row=2, sticky=(N, S, E))
        
        # Gamepad Testerボタン
        self.gamepad_tester_button  = Button(
            setting_frm,
            text='開く',
            command=lambda: webbrowser.open(r"https://hardwaretester.com/gamepad"),
            font=DEFAULT_FONT,
            padx=15,
        )
        self.gamepad_tester_button.grid(column=1, row=3, sticky=(N, S, E))

        self.decide_button = Button(
            self,
            text='適応',
            command=lambda: self.decide_record(),
            font=DEFAULT_FONT,
            padx=15,
        )
        self.decide_button.grid(column=0, row=1, sticky=(N, S, E))

        """ フォーカス """
        self.transient(self.master)
        self.grab_set()

    # 決定ボタンの処理
    def decide_record(self):
        joy_index = self.input_controller_combo_box.current()
        controller_type = self.virtual_controller_type_combo_box.get()
        self.master.active_config(joy_index, controller_type)
        self.destroy() # ウィンドウの削除
        

def fix_window_size(win, size):
    h,w = size
    win.columnconfigure(0, weight=1)    # 列についての重みを決定
    win.rowconfigure(0, weight=1)       # 行についての重みを設定
    win.minsize(h,w)                    # ウィンドウの最小のサイズ
    win.maxsize(h,w)                    # ウィンドウの最小のサイズ

class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.finish_resource = []
        
        def close():  # ウィンドウの右上の✖アイコンから閉じるときの処理（ウィンドウを閉じる処理を書き換える）
            self.finish()
            self.quit()
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", close)  # ウィンドウを閉じる処理を書き換える
        
    def register_finish(self,func):
        self.finish_resource.append(func)
        
    def finish(self):
        for finish_item in self.finish_resource:
            finish_item()

def main():
    # メインウィンドウの設定
    main_win = MainWindow()
    main_win.title("Gamepad Emulator")

    # フレームの設定
    main_frm(master=main_win)

    # ウィンドウのサイズ変を固定
    fix_window_size(main_win, [500, 95])

    # サイズグリップを貼り付ける用のフレームの設定
    sizegrip_frm = ttk.Frame(main_win, style="Sizegrip.TFrame")
    sizegrip_frm.grid(column=0, row=1, sticky=(N, S, W, E))
    sizegrip_frm.columnconfigure(0, weight=1)
    sizegrip_frm.rowconfigure(0, weight=1)
    sizegrip_frm_style = ttk.Style()
    sizegrip_frm_style.configure("Sizegrip.TFrame", background="white") # 背景を白に指定

    # サイズグリップの設定(サブフレームへ配置)
    sizegrip = ttk.Sizegrip(sizegrip_frm)
    sizegrip.grid(row=500, column=100, sticky=(S, E))

    main_win.mainloop()  # メインウィンドウがここで動く

if __name__=="__main__":
    # pyinstallerとmultiprocessingを併用する場合は以下の関数を初回に呼び出しておく
    freeze_support()
    main()