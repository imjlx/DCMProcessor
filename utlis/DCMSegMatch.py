"""
@file    :  DCMSegMatch.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  


@Modify Time      @Author      @Version     
------------      -------      --------     
2022/5/3 13:14   JHR          1.0         
"""

import SimpleITK as sitk
import os
import pandas as pd
import shutil
import re


def find_folders(folder_path, info_path):
    """
    总文件夹下三层子文件夹
    :param folder_path:
    :param info_path:
    :return:
    """
    folders = list()

    for f1 in os.listdir(folder_path):
        f1_full = os.path.join(folder_path, f1)
        for f2 in os.listdir(f1_full):
            f2_full = os.path.join(f1_full, f2)
            for f3 in os.listdir(f2_full):
                f3_full = os.path.join(f2_full, f3)
                folders.append(f3_full)

    info = pd.DataFrame(data={'index': range(1, len(folders)+1), 'folder': folders})
    info.to_excel(info_path, index=False)


def extract_info(info_path):
    info = pd.read_excel(io=info_path, sheet_name=0, index_col='index')
    for i, folder in enumerate(info.loc[:, 'folder']):
        series_id = sitk.ImageSeriesReader.GetGDCMSeriesIDs(folder)
        info.loc[i+1, 'Series_ID'] = series_id[0]
        print(i)
    info.to_excel(info_path)


def match(info_origin_path, info_seg_path):
    info_origin = pd.read_excel(info_origin_path, sheet_name=0, index_col='index')
    info_seg = pd.read_excel(info_seg_path, sheet_name=0, index_col='index')

    for i in range(1, len(info_origin) + 1):
        uid = info_origin.loc[i, 'Series_ID']
        folder_seg_list = info_seg.loc[info_seg['Series_ID'] == uid].loc[:, 'folder'].tolist()
        if len(folder_seg_list) == 1:
            folder_seg = folder_seg_list[0]
        elif len(folder_seg_list) == 0:
            folder_seg = "No matched seg"
        else:
            folder_seg = "Warning!!"
        info_origin.loc[i, 'matched_seg'] = folder_seg

    info_origin.to_excel(info_origin_path)


def move_rtstruct(info_path):
    info = pd.read_excel(io=info_path, sheet_name=0, index_col='index')
    for i in range(1, len(info) + 1):   # 对每一行数据进行循环

        source_folder = info.loc[i, 'matched_seg']  # 分割数据文件夹
        target_folder = info.loc[i, 'folder']   # 原始数据文件夹
        source_fpath = None     # RTSTRUCT***.dcm文件地址

        if source_folder == "No matched seg":   # 如果没有分割数据，跳过
            info.loc[i, 'isCopied'] = 0
            continue

        for fname in os.listdir(source_folder):     # 寻找匹配的文件
            if re.match(pattern="RTSTRUCT[0-9]+.dcm", string=fname):
                source_fpath = os.path.join(source_folder, source_fpath)

        if source_fpath is not None:    # 复制文件
            shutil.copyfile(src=source_fpath, dst=os.path.join(target_folder, "RTSTRUCT.dcm"))
            info.loc[i, 'isCopied'] = 1
        else:
            info.loc[i, 'isCopied'] = 0

    info.to_excel(info_path)


if __name__ == "__main__":
    # find_folders(folder_path=r'F:\WB', info_path=r'D:\脚本\生成DCM序列\dataset\info_origin.xlsx')
    # find_folders(folder_path=r'F:\WB_seg', info_path=r'D:\脚本\生成DCM序列\dataset\info_seg.xlsx')
    # extract_info(r'D:\脚本\生成DCM序列\dataset\info_origin.xlsx')
    # extract_info(r'D:\脚本\生成DCM序列\dataset\info_seg.xlsx')
    match(r"E:\other program\DCMProcessor\dataset\info_origin.xlsx", r"E:\other program\DCMProcessor\dataset\info_seg.xlsx")
