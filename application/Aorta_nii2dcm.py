"""
@file    :  Aorta_nii2dcm.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/4/27 10:39   JHR          1.0         
"""

import os
import shutil
from utlis.DCMGenerate import DCMGenerator


def copy_ct(extract_path=r"F:\ZS_Aorta\output", target_path=r"D:\Aorta", r=None):
    """
    将ct.nii文件从F盘拷贝到工作盘D，只拷贝ct，不拷贝其他分割
    :param extract_path:
    :param target_path:
    :param r:
    :return:
    """

    if r is None:
        r = (0, len(os.listdir(extract_path))-1)

    for i, folder_path in enumerate(os.listdir(extract_path)):
        if r[0] <= i <= r[1]:
            extract_fpath = os.path.join(extract_path, folder_path + "\\ct.nii")

            target_folder = os.path.join(target_path, folder_path)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            target_fpath = os.path.join(target_path, folder_path + "\\ct.nii")
            if not os.path.isfile(target_fpath):
                try:
                    shutil.copyfile(extract_fpath, target_fpath)
                except FileNotFoundError:
                    print(extract_fpath, " Not Found")


def generate_one_series(read_dir, save_dir, patient_name):
    g = DCMGenerator(read_dir)
    g.Execute(out_dir=save_dir, PatientName=patient_name)


def generate_all_series(base_folder=r"D:\Aorta"):
    for folder in os.listdir(base_folder):
        fpath = base_folder + "\\" + folder + "\\ct.nii"
        dcm_folder = base_folder + "\\" + folder + "\\dcm"
        g = DCMGenerator(fpath)
        g.Execute(out_dir=dcm_folder, PatientName=folder)


def copy_dcm_to_auto(base_folder=r"D:\Aorta", target_path=r"D:\DeepViewer\data\pacs"):
    """
    将dcm文件从总文件夹中复制到自动处理文件夹
    :param base_folder:
    :param target_path:
    :return:
    """
    for folder in os.listdir(base_folder):
        dcm_folder = base_folder + "\\" + folder + "\\dcm"
        for fname in os.listdir(dcm_folder):
            fpath = os.path.join(dcm_folder, fname)
            shutil.copyfile(fpath, os.path.join(target_path, fname))


if __name__ == "__main__":
    # copy_ct(r=(0, 5))
    # generate_all_series()
    copy_dcm_to_auto()

