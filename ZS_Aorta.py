#!/usr/bin/env python
# encoding: utf-8
"""
    @File       : ZS_Aorta.py
    @Time       : 2022/1/17 11:00
    @Author     : Haoran Jia
    @license    : Copyright(c) 2022 Haoran Jia. All rights reserved.
    @contact    : 21211140001@fudan.m.edu.cn
    @Description：
"""
import re
import time
import os
import tqdm

from utlis import DCMProcess

FOLDER_DICT = {
    "seg": "Segmented axial",
    "AAO": "AAO",
    "BCT": "BCT",
    "DAO": "DAO",
    "LCCA": "LCCA",
    "LSA": "LSA"
}


def test():
    folder = 'F:\\ZS_Aorta\\20201030\\ZS16093253_ZS0023607916_1\\WholeBody CTA\\CTA 1.0 CE'
    processor = DCMProcess.DCMSerieProcessor(folder)
    processor.read()
    processor.show()

    time.sleep(0.1)


class WholeBodyCTA(object):
    def __init__(self, folder):
        self.folder = folder
        self.folder_write = None
        self.create_folder_write()
        self.processor_ct = None

    def Execute(self):
        listdir = os.listdir(self.folder)
        if "CTA 1.0 CE" not in listdir:
            print("No \"CTA 1.0 CE\" folder!!")
            print("Wrong in \t\t", self.folder)
            return 1
        elif "Segmented axial" not in listdir:
            print("No \"Segmented axial\" folder!!")
            print("Wrong in \t\t", self.folder)
            return 2
        else:
            for seg_type in FOLDER_DICT:
                if seg_type in listdir:
                    self.save_other(seg_type)

    def create_folder_write(self):
        # 生成保存文件夹路径
        self.folder_write = re.search(r"202\d{5}\\ZS[0-9ZS_]*\\Wh", self.folder).group()[0:-3]
        self.folder_write = self.folder_write.replace("\\", "_")
        self.folder_write = "F:\\ZS_Aorta\\output\\" + self.folder_write

        # 创建文件夹
        if not os.path.exists(self.folder_write):
            os.makedirs(self.folder_write)

        return self.folder_write

    def load_ct(self):
        folder = os.path.join(self.folder, "CTA 1.0 CE")
        self.processor_ct = DCMProcess.DCMSerieProcessor(folder)
        self.processor_ct.read()
        self.processor_ct.clip()
        return self.processor_ct

    def save_ct(self):
        if self.processor_ct is None:
            self.load_ct()
        self.processor_ct.write(self.folder_write, "ct.nii")

    def load_other(self, seg_type):
        folder = os.path.join(self.folder, FOLDER_DICT[seg_type])
        processor = DCMProcess.DCMSerieProcessor(folder)
        processor.read()
        return processor

    def save_other(self, seg_type):
        if self.processor_ct is None:
            self.load_ct()
        processor = self.load_other(seg_type)
        processor.resample(self.processor_ct.img)
        processor.clip()
        processor.write(self.folder_write, seg_type + ".nii")


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


def loop(main_folder):
    folders = patient_folder(main_folder)

    with tqdm.tqdm(folders) as bar:
        for folder in bar:
            f = WholeBodyCTA(folder)
            f.Execute()
