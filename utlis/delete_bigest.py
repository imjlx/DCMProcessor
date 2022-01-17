#!/usr/bin/env python
# encoding: utf-8
"""
    @File       : DCMProcess.py
    @Time       : 2022/1/5 14:32
    @Author     : Haoran Jia
    @license    : Copyright(c) 2022 Haoran Jia. All rights reserved.
    @contact    : 21211140001@fudan.m.edu.cn
    @Description：
"""

import os
import numpy as np


def remove_biggest(folder_name):

    sizes = []
    names = []

    for file_name in os.listdir(folder_name):
        fpath = os.path.join(folder_name, file_name)
        size = os.stat(fpath).st_size
        sizes.append(size)
        names.append(file_name)

    sizes = np.array(sizes)
    names = np.array(names)

    delete = True
    while delete:
        # 最大值的列表
        index = np.argwhere(sizes == sizes.max())
        if len(index) == 1:
            # 找到最大的文件的名字
            file_name = names[index[0, 0]]
            # 获得其路径
            fpath = os.path.join(folder_name, file_name)
            # 删除
            os.remove(fpath)
            sizes = np.delete(sizes, [index[0, 0]])
            names = np.delete(names, [index[0, 0]])
        else:
            delete = False


remove_biggest("P0566783_2020-03-13")
