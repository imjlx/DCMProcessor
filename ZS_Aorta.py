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
import os
import time

import pandas as pd

from utlis.DCMProcess import DCMSerieProcessor

# 不同分割对应的文件夹名
SEG_FOLDER = {
    "seg": "Segmented axial",
    "AAO": "AAO",
    "BCT": "BCT",
    "DAO": "DAO",
    "LCCA": "LCCA",
    "LSA": "LSA"
}

CT_FOLDER = ["WholeBody CTA", "Aortic CTA", "CTA", "Aortic Dissection"]
EXCEL_COLUMNS = ["index", "f1", "f2", "f3", "Exception", "ct_name", "ct", "seg", "AAO", "BCT", "DAO", "LCCA", "LSA"]


class PatientProcessor(object):
    def __init__(self, folder):
        self.folder = folder
        self.folder_write = None
        self.create_folder_write()
        self.processor_ct = None

    def Execute(self, info):
        # 保存路径信息
        path_list = self.folder.split('\\')
        info.loc[len(info), "f1":"f3"] = [path_list[2], path_list[3], path_list[4]]
        # 全部的子文件夹
        sub_folders = os.listdir(self.folder)
        # 寻找ct的子文件夹
        ct_folder = None
        for sub_folder in sub_folders:
            if re.search(r"CTA 1.0 CE|0.75 *B2|Recon 2_ CTA", sub_folder):
                ct_folder = sub_folder

        if ct_folder is None:
            info.loc[len(info) - 1, "Exception"] = "No Expected CT"
        else:
            # 读取并保存CT和存在的分割
            self.load_ct(ct_folder)
            n_list = self.save_ct()
            info.loc[len(info) - 1, "ct_name"] = ct_folder
            info.loc[len(info) - 1, "ct"] = ", ".join([str(n) for n in n_list])
            seg_n = 0  # 保存分割图像的数量
            for seg_type in SEG_FOLDER:
                if SEG_FOLDER[seg_type] in sub_folders:
                    n_list = self.save_other(seg_type)
                    seg_n += 1
                    if len(n_list) != 2:
                        info.loc[len(info) - 1, "Exception"] = "Too many Seg"
                    info.loc[len(info) - 1, seg_type] = ", ".join([str(n) for n in n_list])
            if seg_n not in [1, 6]:
                info.loc[len(info) - 1, "Exception"] = "Miss Seg"

        return info

    def create_folder_write(self):
        # 生成保存文件夹路径
        self.folder_write = re.search(r"202\d{5}\\ZS[0-9ZS_]*\\", self.folder).group()[0:-1]
        self.folder_write = self.folder_write.replace("\\", "_")
        self.folder_write = "F:\\ZS_Aorta\\output\\" + self.folder_write

        # 创建文件夹
        if not os.path.exists(self.folder_write):
            os.makedirs(self.folder_write)

        return self.folder_write

    def load_ct(self, sub_folder):
        folder = os.path.join(self.folder, sub_folder)
        self.processor_ct = DCMSerieProcessor(folder)
        self.processor_ct.read()
        self.processor_ct.clip()
        return self.processor_ct

    def save_ct(self):
        fpath = os.path.join(self.folder_write, "ct.nii")
        if os.path.isfile(fpath):
            return self.processor_ct.N_files
        else:
            self.processor_ct.write(fpath)
            return self.processor_ct.N_files

    def load_other(self, seg_type):
        folder = os.path.join(self.folder, SEG_FOLDER[seg_type])
        processor = DCMSerieProcessor(folder)
        processor.read()
        return processor

    def save_other(self, seg_type):
        fpath = os.path.join(self.folder_write, seg_type + ".nii")
        processor = self.load_other(seg_type)
        if os.path.isfile(fpath):
            return processor.N_files
        else:
            processor.resample(self.processor_ct.img)
            processor.clip()
            processor.write(fpath)
            return processor.N_files


def wholeBodyCTAPath(main_folder):
    """
    获取患者文件夹的名称，每个患者文件夹下有单独的DCM文件夹
    文件夹结构
    ZS_Aorta
        -20201030
            -ZS16093253_ZS0023607916_1
                -WholeBody CTA
                    -CTA 1.0 CE
                    -AAO, BCT, DAO, LCCA, LSA (部分文件夹有)
    :return: 所有 WholeBody CTA 路径
    """
    folders = []
    for root, dirs, files in os.walk(main_folder):
        # 对所有的root进行遍历，dirs和files是对应root下的问价夹和问价列表
        # root指包含全部路径的问价夹，dirs和files只有名称没有路径
        if len(dirs) == 1 and dirs[0] == "WholeBody CTA":
            folders.append(os.path.join(root, "WholeBody CTA"))

    return folders


def specialCase(f0_path):
    cases = []
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if not re.match(r"202\d{5}$", f1):
            print(f1_path)
            cases.append(f1_path)
        else:
            for f2 in os.listdir(f1_path):
                f2_path = os.path.join(f1_path, f2)
                if not re.match(r"ZS\d{8}_ZS\d{10}_?\d?", f2):
                    print(f2_path)
                    cases.append(f2_path)
                else:
                    for f3 in os.listdir(f2_path):
                        if not re.match(r"WholeBody CTA", f3):
                            f3_path = os.path.join(f2_path, f3)
                            print(f3_path)
                            cases.append(f3_path)
    with open("dataset/specialCase.txt", 'w') as f:
        f.writelines([case + "\n" for case in cases])


def loop(f0_path, isRefill=True):
    n_loops = 0
    print("计算患者文件夹数量， 共：", end=" ")
    for f1 in os.listdir(f0_path):
        if f1 != "output":
            f1_path = os.path.join(f0_path, f1)
            for _ in os.listdir(f1_path):
                n_loops += 1
    print(n_loops, " 个")

    if isRefill:
        # 如果 isRefill，重新生成Excel
        info = pd.DataFrame(columns=EXCEL_COLUMNS)
        info.to_excel("dataset/info.xlsx", index=False)
        loaded_n = 0
    else:
        # 根据之前生成的Excel继续读取
        info = pd.read_excel("dataset\\info.xlsx", index_col=[0])
        loaded_n = len(info)

    # 对文件夹分层循环
    n_loop = 1
    for f1 in os.listdir(f0_path):
        print("f1: ", f1)
        f1_path = os.path.join(f0_path, f1)
        if not re.match(r"202\d{5}$", f1):
            if n_loop > loaded_n:
                info = pd.read_excel("dataset\\info.xlsx", index_col=[0])
                info.loc[len(info), "f1"] = f1
                info.loc[len(info) - 1, "Exception"] = "Folder Error"
                info.to_excel("dataset\\info.xlsx")
            else:
                print("已提取")
            n_loop += 1
        else:
            for f2 in os.listdir(f1_path):
                print("\tf2: ", f2)
                f2_path = os.path.join(f1_path, f2)
                if not re.match(r"ZS\d{8}_ZS\d{10}_?\d?", f2):
                    if n_loop > loaded_n:
                        info = pd.read_excel("dataset\\info.xlsx", index_col=[0])
                        info.loc[len(info), "f1"] = f1
                        info.loc[len(info) - 1, "f2"] = f2
                        info.loc[len(info) - 1, "Exception"] = "Folder Error"
                        info.to_excel("dataset\\info.xlsx")
                    else:
                        print("已提取")
                    n_loop += 1
                else:
                    for f3 in os.listdir(f2_path):
                        print(f"\t\tf3: {f3} \t 进度: {n_loop}/{n_loops}")
                        f3_path = os.path.join(f2_path, f3)
                        if f3 not in CT_FOLDER:
                            if n_loop > loaded_n:
                                info = pd.read_excel("dataset\\info.xlsx", index_col=[0])
                                info.loc[len(info), "f1"] = f1
                                info.loc[len(info) - 1, "f2"] = f2
                                info.loc[len(info) - 1, "f3"] = f3
                                info.loc[len(info) - 1, "Exception"] = "Folder Error"
                                info.to_excel("dataset\\info.xlsx")
                            else:
                                print("已提取")
                            n_loop += 1
                        else:
                            info = pd.read_excel("dataset\\info.xlsx", index_col=[0])
                            if n_loop > loaded_n:
                                try:
                                    patient = PatientProcessor(f3_path)
                                    info = patient.Execute(info)
                                    info.to_excel("dataset\\info.xlsx")
                                except:
                                    info.loc[len(info), "f1"] = f1
                                    info.loc[len(info) - 1, "f2"] = f2
                                    info.loc[len(info) - 1, "f3"] = f3
                                    info.loc[len(info) - 1, "Exception"] = "Load Data Error"
                                    info.to_excel("dataset\\info.xlsx")
                            else:
                                print("已提取")
                            n_loop += 1


def check_patient(patient_folder):
    p = PatientProcessor(patient_folder)
    p.lo
    ct_processor = DCMSerieProcessor(os.path.join(patient_folder, "CTA 1.0 CE"))
    ct_processor.read()
    ct_processor.basic_info()
    time.sleep(0.1)


if __name__ == '__main__':
    # loop("F:\\ZS_Aorta", isRefill=False)
    check_patient("F:\\ZS_Aorta\\20201224\\ZS11087592_ZS0002168998\\WholeBody CTA")

    time.sleep(0.1)
