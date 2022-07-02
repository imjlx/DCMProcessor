"""
@file    :  RTStructProcess.py
@License :  (C)Copyright 2022 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :

@Modify Time      @Author      @Version
------------      -------      --------
2022/6/30 12:10   JHR          1.0
"""
import os
import re
import shutil

TARGET_PATH = r"D:\DeepViewer\data\pacs"

# 对文件夹的下层结构敏感
def copy_dcm_to_auto(base_folder=r"D:\Aorta", target_path=TARGET_PATH):
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


def copy_last_dcm_to_auto(base_folder=r"F:\Patients-CT_PET", target_path=TARGET_PATH):
    """
    找出没有RTSTRUCT分割文件的患者，将其dcm文件从总文件夹中复制到自动处理文件夹
    :param base_folder:
    :param target_path:
    :return:
    """
    for f1 in os.listdir(base_folder):
        f1 = os.path.join(base_folder, f1)
        for f2 in os.listdir(f1):
            f2 = os.path.join(f1, f2)
            for f3 in os.listdir(f2):
                f3 = os.path.join(f2, f3)

                if "RTSTRUCT.dcm" in os.listdir(f3):    # 如果文件夹中已经有了自动分割结果，跳过文件夹
                    break

                for fname in os.listdir(f3):    # 如果没有，将所有文件拷贝到自动分割文件夹
                    fpath = os.path.join(f3, fname)
                    shutil.copyfile(fpath, os.path.join(target_path, fname))


def copy1(base_folder=r"F:\需整理\自动分割\未分割", target_path=TARGET_PATH):
    for i, f1 in enumerate(os.listdir(base_folder)):
        if i in range(15, 40):
            f1 = os.path.join(base_folder, f1)
            for f2 in os.listdir(f1):
                f2 = os.path.join(f1, f2)
                print(f2)
                for f3 in os.listdir(f2):
                    if re.match(pattern="CT", string=f3):
                        print("\t\t\t", f3)
                        f3 = os.path.join(f2, f3)
                        for fname in os.listdir(f3):
                            fpath = os.path.join(f3, fname)
                            shutil.copyfile(fpath, os.path.join(target_path, fname))
                    elif re.match(pattern="PET", string=f3):
                        print("\t\t\t", f3)
                    else:
                        print("---------------", f3)


if __name__ == "__main__":
    copy1()

