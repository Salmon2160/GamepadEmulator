# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gamepad_emulator.py'],
    pathex=[],
    binaries=[
        (r"C:\Users\ryoichi\anaconda3\envs\macro_env\python310.dll", '.'),
        (r"C:\Users\ryoichi\anaconda3\envs\macro_env\Lib\site-packages\vgamepad\win\vigem\client\x64\ViGEmClient.dll", '.'),
    ],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
a.datas += [ 
    (r'.\image\movie_icon1.png', '.\image\movie_icon1.png', 'DATA'),
    (r'.\image\movie_icon2.png', '.\image\movie_icon2.png', 'DATA'),
    (r'.\image\stop_icon1.png', '.\image\stop_icon1.png', 'DATA'),
    (r'.\image\play_icon2.png', '.\image\play_icon2.png', 'DATA'),
    (r'.\image\config_icon.png', '.\image\config_icon.png', 'DATA'),
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

Key = ['mkl']
def remove_from_list(input, keys):
    outlist = []
    for item in input:
        name, _, _ = item
        flag = 0
        for key_word in keys:
            if name.find(key_word) > -1:
                flag = 1
        if flag != 1:
            outlist.append(item)
    return outlist

a.binaries += remove_from_list(a.binaries, Key)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='gamepad_recorder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gamepad_recorder',
)
