#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/28 12:52
# @Author  :
# @email    : 1747193328@qq.com


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'neptrainkit.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

import os
import platform
import sys
from loguru import logger
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from NepTrainKit import src_rc

try:
    # Actual if statement not needed, but keeps code inspectors more happy
    if __nuitka_binary_dir is not None: # type: ignore  
        is_nuitka_compiled = True
    else:
        is_nuitka_compiled = False
except NameError:
    is_nuitka_compiled = False



if is_nuitka_compiled:


    logger.add("./Log/{time:%Y-%m}.log",
               level="DEBUG",
                )
    module_path="./"
else:

    module_path = os.path.dirname(__file__)

def get_user_config_path():
    if platform.system() == 'Windows':
        # Windows 系统通常使用 AppData 路径存放应用数据
        local_path = os.getenv('LOCALAPPDATA', None)
        if local_path is None:
            local_path = os.getenv('USERPROFILE', '') + '\\AppData\\Local '
        user_config_path = os.path.join(local_path, 'NepTrainKit')
    else:
        user_config_path = os.path.expanduser("~/.config/NepTrainKit")
    return user_config_path
