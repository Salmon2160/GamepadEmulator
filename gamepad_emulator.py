#!/usr/bin/python -S
# coding: utf-8
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from PIL import Image,ImageTk
import time
import datetime
import os
import sys
import copy
import pygame
import threading 

from function.record import Record
from function.replay import Replay
from function.utils import *
from gamepad.controller_config import CONTROLLER_TYPE_LIST
from gamepad.controller_input import ControllerVirtualInput

SELECTABLE_BASE_FPS = 60
SELECTABLE_FPS_LIST = [1, 2, 5, 15, 30, 60, 120, 240, 480, 960]
OUTPUT_PATH = "output"
DEFAULT_FONT=("", 12)

def get_init_shared_states():
    return [1, 0, 0, 0, 0, 0, 0]

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_joy_name_list():
    pygame.init()
    joy_num = pygame.joystick.get_count()
    joy_names = []
    for i in range(joy_num):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        joy_names += [joy.get_name()]
        joy.quit()
    pygame.quit()
    return joy_names

def get_joy_index_from_name(target_joy_name):
    pygame.init()
    joy_num = pygame.joystick.get_count()
    
    is_find = False
    for i in range(joy_num):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        joy_name = joy.get_name()
        joy.quit()
        if target_joy_name == joy_name:
            is_find = True
            break
    pygame.quit()
    return i if is_find else 0

def get_joy_name(joy_index):
    # コントローラー名を取得する為に、一時的にpygameを起動
    pygame.init()
    joy = pygame.joystick.Joystick(joy_index)
    joy.init()
    joy_name = joy.get_name()
    print(joy_name)
    joy.quit()
    pygame.quit()
    return joy_name

def start_record(joy_index, joy_type, macro_name, fps):
    joy_name = get_joy_name(joy_index)
   
    config = {
        "controller_type"   : joy_type,
        "record_path"       : os.path.join(OUTPUT_PATH, joy_name, macro_name, "record.txt"),
        "fps"               : fps,
    }

    # active_flag, passed_milliseconds, ...
    shared_states = get_init_shared_states()
    
    process = threading.Thread(target=Record, args=(config, joy_index, shared_states))
    process.start()
    print("start record")
    
    return process, shared_states

def end_record(process, shared_states):
    shared_states[0] = 0
    process.join()
    print("finish record : " + str(shared_states[1]))
    
    process = None
    shared_states = None
    
def start_replay(replay_config):
    # active_flag, replay_num, ...
    shared_states = get_init_shared_states()

    process = threading.Thread(target=Replay, args=(replay_config, shared_states))
    process.start()
    print("start replay")
    
    return process, shared_states

def end_replay(process, shared_states):
    shared_states[0] = 0
    process.join()
    print("finish replay")
    
    process = None
    shared_states = None

class main_frm(Frame):

    def __init__(self, master):
        super().__init__(master=master)
        self.master = master
        self.grid(column=0, row=0, sticky=(N, S, W, E)) # capture_frmをマスターウィンドウに貼り付ける
        self.make_widget()
        
        self.process = None
        self.shared_states = None
        self.gamepad_input = None
        
        self.master.register_finish(self.finish)
        
    def finish(self):
        if self.process is not None and self.shared_states is not None:
            self.shared_states[0] = 0
            self.process.join()
            self.process = None
            self.shared_states = None

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
        self.record_key = record_key
        
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
        self.process, self.shared_states = start_record(*record_input)
        button_key = self.record_key
        self.button_dict[button_key]["image"]   = self.icon_img_list["recording"]
        self.button_dict[button_key]["text"]    = "終了"
        self.button_state_dict[button_key]      = True
        self.deactivate_all_button([button_key])
    
    def deactive_record_button(self):
        self.deactive_record()
        
    def deactive_record(self):
        if self.process is not None and self.shared_states is not None:
            end_record(self.process, self.shared_states)
        button_key = self.record_key
        self.button_dict[button_key]["image"]   = self.icon_img_list["record"]
        self.button_dict[button_key]["text"]    = "記録"
        self.button_state_dict[button_key]      = False
        self.activate_all_button()
    
    def active_replay_button(self):
        replay_setting_win(self)
    
    def active_replay(self, replay_input):
        replay_path = replay_input[0]
        replay_config = LoadYaml(replay_path)
        
        replay_controller_type = replay_config["controller_type"]
        if self.gamepad_input is None or self.gamepad_input.controller_type != replay_controller_type:
            self.gamepad_input = ControllerVirtualInput(replay_config["controller_type"])             
        replay_config["virtual_input"] = self.gamepad_input

        self.process, self.shared_states = start_replay(replay_config)
        button_key = self.replay_key
        self.button_dict[button_key]["image"]   = self.icon_img_list["replaying"]
        self.button_dict[button_key]["text"]    = "終了"
        self.button_state_dict[button_key]      = True
        self.deactivate_all_button([button_key])
    
    def deactive_replay_button(self):
        self.deactive_replay()
    
    def deactive_replay(self):
        if self.process is not None and self.shared_states is not None:
            end_replay(self.process, self.shared_states)
        button_key = self.replay_key
        self.button_dict[button_key]["image"]   = self.icon_img_list["replay"]
        self.button_dict[button_key]["text"]    = "再生"
        self.button_state_dict[button_key]      = False
        self.activate_all_button()
    
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

class record_setting_win(Toplevel):
    def __init__(self,master):
        self.master = master
        super().__init__(master=master)
        self.make_widget()

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
            text="FPS",
            font=DEFAULT_FONT,
        )
        text_label.grid(column=0, row=2, sticky=text_sticky)
        
        text_label = ttk.Label(
            setting_frm,
            text="保存先マクロ名",
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
        self.input_controller_combo_box["values"] = get_joy_name_list()
        self.input_controller_combo_box.current(0)
        self.input_controller_combo_box.grid(column=1, row=0, sticky=input_sticky)

        # 仮想コントローラーの選択
        self.virtual_controller_type_combo_box = ttk.Combobox(
            setting_frm,
            font=DEFAULT_FONT,
            state="readonly"  # コンボボックスからの選択のみ（プルダウン式）
        )
        self.virtual_controller_type_combo_box["values"] = CONTROLLER_TYPE_LIST
        self.virtual_controller_type_combo_box.current(0)
        self.virtual_controller_type_combo_box.grid(column=1, row=1, sticky=input_sticky)
        
        # FPSの選択
        self.fps_combo_box = ttk.Combobox(
            setting_frm,
            font=DEFAULT_FONT,
            state="readonly"  # コンボボックスからの選択のみ（プルダウン式）
        )
        self.fps_combo_box["values"] = SELECTABLE_FPS_LIST
        self.fps_combo_box.current(SELECTABLE_FPS_LIST.index(SELECTABLE_BASE_FPS))
        self.fps_combo_box.grid(column=1, row=2, sticky=input_sticky)
        
        # マクロ名の入力
        self.macro_name_entry = ttk.Entry(
            setting_frm,
            font=DEFAULT_FONT,
        )
        self.macro_name_entry.insert(0, "macro")
        self.macro_name_entry.grid(column=1, row=3, sticky=input_sticky)

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
        record_input += [get_joy_index_from_name(self.input_controller_combo_box.get())]
        record_input += [self.virtual_controller_type_combo_box.get()]
        record_input += [self.macro_name_entry.get()]
        record_input += [int(self.fps_combo_box.get())]
        
        # input [joy_index, controller_type, macro_name, fps]
        self.master.active_record(record_input)
        self.destroy() # ウィンドウの削除

class replay_setting_win(Toplevel):
    def __init__(self,master):
        self.master = master
        super().__init__(master=master)
        self.make_widget()

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
        output_controller_list = [os.path.join(OUTPUT_PATH, f) for f in os.listdir(OUTPUT_PATH) if os.path.isdir(os.path.join(OUTPUT_PATH, f))]
        macro_path_list = [os.path.join(output_path, f) for output_path in output_controller_list for f in os.listdir(output_path) if os.path.isdir(os.path.join(output_path, f))]
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
        
        if not os.path.isfile(replay_path):
            # 設定ファイルが存在しないのでキャンセル
            messagebox.showerror('選択エラー', '有効なマクロが選択されていません。')
            self.master.deactive_replay()
            return

        replay_input += [replay_path] 

        # input [replay_input_path]
        self.master.active_replay(replay_input)
        self.destroy()
        
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
    main_win.title("Gamepad Recorder")

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
    main()