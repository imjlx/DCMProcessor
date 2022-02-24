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
    """
    对一个患者的主文件夹下的所有图像进行处理
    分别读取CT、各种分割的DICOM文件序列，并生成nii文件
    """
    def __init__(self, folder):
        self.folder = folder    # 患者文件夹地址
        self.folder_write = None    # 保存提取的nii文件夹的地址
        self.create_folder_write()  # 创建保存nii的文件夹的地址
        self.processor_ct = None    #

    def Execute_manually(self, ct_folder):
        self.load_ct(ct_folder)
        n_slice = []
        n_slice.append(self.save_ct())

        for seg_type in SEG_FOLDER:
            if SEG_FOLDER[seg_type] in os.listdir(self.folder):
                n_slice.append(self.save_other(seg_type))

        # 输出信息
        print(ct_folder, end="\t")
        for i in range(len(n_slice)):
            print(", ".join([str(n) for n in n_slice[i]]), end="\t")

    def Execute(self, info=None):
        # 保存路径信息
        path_list = self.folder.split('\\')
        if info is not None:
            info.loc[len(info), "f1":"f3"] = [path_list[2], path_list[3], path_list[4]]
        # 全部的子文件夹
        sub_folders = os.listdir(self.folder)
        # 寻找ct的子文件夹
        ct_folder = None
        for sub_folder in sub_folders:
            if re.search(r"^CTA 1.0 CE$|0.75 *B2|^Recon 2_ CTA$", sub_folder):
                ct_folder = sub_folder

        # 如果早不到满足格式的CT文件夹，则保存错误信息
        if ct_folder is None:
            if info is not None:
                info.loc[len(info) - 1, "Exception"] = "No Expected CT"
        else:
            # 有CT文件夹，读取并保存CT和存在的分割
            self.load_ct(ct_folder)
            # 将CT文件夹下的序列数量保存在n_list中，并记录
            n_series_files_list = self.save_ct()
            if info is not None:
                info.loc[len(info) - 1, "ct_name"] = ct_folder
                info.loc[len(info) - 1, "ct"] = ", ".join([str(n) for n in n_series_files_list])

            seg_n = 0  # 保存分割图像的数量
            for seg_type in SEG_FOLDER:
                if SEG_FOLDER[seg_type] in sub_folders:
                    n_series_files_list = self.save_other(seg_type)
                    if info is not None:
                        seg_n += 1
                        if len(n_series_files_list) != 2:
                            info.loc[len(info) - 1, "Exception"] = "Too many Seg"
                        info.loc[len(info) - 1, seg_type] = ", ".join([str(n) for n in n_series_files_list])

            if info is not None:
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
                                    # 很奇怪，创造了两行，f1的时候就要减一
                                    info.loc[len(info) - 1, "f1"] = f1
                                    info.loc[len(info) - 1, "f2"] = f2
                                    info.loc[len(info) - 1, "f3"] = f3
                                    info.loc[len(info) - 1, "Exception"] = "Load Data Error"
                                    info.to_excel("dataset\\info.xlsx")
                            else:
                                print("已提取")
                            n_loop += 1


def fix_load_data_error():
    """
    执行loop循环的时候，判断ct文件夹的正则规则不完善，选到了名为”Vitrea Snapshot_ CTA 1.0 CE“的文件夹导致出错
    已改正PatientProcessor.Execute()函数，若彻底重新调用loop，无需本函数
    本函数用改正的Execute函数将”Load Data Error“的数据重新读取
    :return:
    """
    # 读取信息，创建一个待修改的list
    info_origin = pd.read_excel("dataset/info.xlsx", index_col=[0])
    info_origin = info_origin[info_origin.Exception == "Load Data Error"]
    folder_list = []
    for index, s in info_origin.iterrows():
        folder = "F:\\ZS_Aorta\\" + str(s["f1"]) + "\\" + s["f2"] + "\\" + s["f3"]
        folder_list.append((index, folder))

    # 对这个list进行循环，一一修改
    for index, folder in folder_list:
        info = pd.read_excel("dataset/info.xlsx", index_col=[0])
        print(f"index={index}")
        try:
            temp_info = pd.DataFrame(columns=EXCEL_COLUMNS)
            patient = PatientProcessor(folder)
            temp_info = patient.Execute(temp_info)
            info.loc[index] = temp_info.loc[0]
        except:
            print("又出错了。。。")
            info.loc[index, "Exception"] = "Load Data Error 2"

        info.to_excel("dataset\\info.xlsx")


if __name__ == '__main__':
    # loop("F:\\ZS_Aorta", isRefill=False)
    # fix_load_data_error()

    patient = PatientProcessor(folder="F:\\ZS_Aorta\\20201215\\ZS09021838_ZS0000050828\\PA")
    patient.Execute_manually(ct_folder="Recon 2_")
