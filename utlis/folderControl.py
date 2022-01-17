#!/usr/bin/env python
# encoding: utf-8
"""
    @File       : folderControl.py
    @Time       : 2022/1/7 20:57
    @Author     : Haoran Jia
    @license    : Copyright(c) 2022 Haoran Jia. All rights reserved.
    @contact    : 21211140001@fudan.m.edu.cn
    @Description：关于文件夹, 文件的操作
"""
import os


def all_folders(main_folder):
    """
    获取主文件夹下所有包含dcm文件的子文件夹路径
    :param main_folder: 主文件夹
    :return: 子文件夹list
    """
    folders = []
    for root, dirs, files in os.walk(main_folder):
        for file in files:
            if file.endswith(".dcm"):
                folders.append(root)
                break
    return folders

def ZS_Aorta():
    pass



