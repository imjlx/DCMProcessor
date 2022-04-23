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


def patient_folder(main_folder):
    """
    获取患者文件夹的名称，每个患者文件夹下有单独的DCM文件夹
    文件夹结构
    ZS_Aorta
        -20201030
            -ZS16093253_ZS0023607916_1
                -WholeBody CTA
                    -CTA 1.0 CE
                    -AAO, BCT, DAO, LCCA, LSA (部分问价夹有)
    :return: 所有 WholeBody CTA 路径
    """
    folders = []
    for root, dirs, files in os.walk(main_folder):
        # 对所有的root进行遍历，dirs和files是对应root下的问价夹和问价列表
        # root指包含全部路径的问价夹，dirs和files只有名称没有路径
        if len(dirs) == 1 and dirs[0] == "WholeBody CTA":
            folders.append(os.path.join(root, "WholeBody CTA"))

    return folders



