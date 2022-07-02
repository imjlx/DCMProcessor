"""
@file    :  DCMSegMatch.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  从DeepViewer批量导出的数据，具有固定的文件夹结构，但是不好直接将分割文件与原文件配对整理。
            此脚本实现了根据图像Series ID对分割数据和原始数据配对的功能


@Modify Time      @Author      @Version     
------------      -------      --------     
2022/5/3 13:14   JHR          1.0         
"""

import SimpleITK as sitk
import os
import pandas as pd
import shutil
import re
from tqdm import tqdm


def find_seg(folder_path, info_path):
    """
    找出导出的分割文件的所有底层文件夹，总文件夹下三层子文件夹
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


def find_origin1(folder_path, info_path):
    """
    找出原始文件的所有底层文件夹，总文件夹下三层子文件夹
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


def find_origin2(folder_path, info_path):
    """
    找出原始文件的所有底层文件夹，总文件夹下三层子文件夹，但第三层需要进行判断
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
                if re.match(pattern="CT", string=f3):
                    f3_full = os.path.join(f2_full, f3)
                    folders.append(f3_full)

    info = pd.DataFrame(data={'index': range(1, len(folders)+1), 'folder': folders})
    info.to_excel(info_path, index=False)


def extract_id(info_path):
    """
    根据文件夹列表信息，提取每个文件夹下的序列ID
    :param info_path:
    :return:
    """
    info = pd.read_excel(io=info_path, sheet_name=0, index_col='index')
    pbar = tqdm(info.loc[:, 'folder'])
    for i, folder in enumerate(pbar):
        series_id = sitk.ImageSeriesReader.GetGDCMSeriesIDs(folder)
        info.loc[i+1, 'Series_ID'] = series_id[0]
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
    """
    根据配对的文件路径自动整理分割文件
    :param info_path:
    :return:
    """
    info = pd.read_excel(io=info_path, sheet_name=0, index_col='index')
    for i in range(1, len(info) + 1):   # 对每一行数据进行循环
        print(i)
        source_folder = info.loc[i, 'matched_seg']  # 分割数据文件夹
        target_folder = info.loc[i, 'folder']   # 原始数据文件夹
        source_fpath = None     # RTSTRUCT***.dcm文件地址

        if source_folder == "No matched seg":   # 如果没有分割数据，跳过
            info.loc[i, 'isCopied'] = 0
            continue

        for fname in os.listdir(source_folder):     # 寻找匹配的文件
            if re.match(pattern="RTSTRUCT[0-9]+.dcm", string=fname):
                source_fpath = os.path.join(source_folder, fname)

        if source_fpath is not None:    # 复制文件
            shutil.copyfile(src=source_fpath, dst=os.path.join(target_folder, "RTSTRUCT.dcm"))
            info.loc[i, 'isCopied'] = 1
        else:
            info.loc[i, 'isCopied'] = 0

    info.to_excel(info_path)


if __name__ == "__main__":
    folder_path_origin = r"F:\need to sort\seg_Auto\1to_be_seged"
    folder_path_seg = r"C:\Users\Wisdom\Desktop\seg"
    info_path_origin = r"D:\脚本\DCMProcessor\dataset\info_origin.xlsx"
    info_path_seg = r"D:\脚本\DCMProcessor\dataset\info_seg.xlsx"

    # find_origin2(folder_path=folder_path_origin, info_path=info_path_origin)
    # extract_id(info_path=info_path_origin)
    # find_seg(folder_path=folder_path_seg, info_path=info_path_seg)
    # extract_id(info_path=info_path_seg)

    match(info_origin_path=info_path_origin, info_seg_path=info_path_seg)
    move_rtstruct(info_path=info_path_origin)



