"""
@file    :  SegJpgProcess.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  部分手动分割的结果以jpg格式保存，且张数不全，需要转换为nii格式

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/2 11:58   JHR          1.0         
"""

import os
import cv2
import filetype
import numpy as np
import SimpleITK as sitk
from tqdm import tqdm

import matplotlib.pyplot as plt

# 保存各器官数据的文件夹（folder_organs）下其他文件夹
STOP_FOLDER_in_Folder_organs = ["all_organs_nii", "Current", "Origin", "SCB_Debug1", "SCB_Debug2", "SCB_Debug3", "SCB"]
# 保存器官nii的文件夹（all_organ_nii）下其他文件
STOP_ORGAN_in_All_Organs_nii = ["seg.nii"]

# 器官标准值
OrganID = {
    # 有重叠部分, 先写大体积的，然后往上覆盖
    "Outline": 10, "Body": 10,
    "Skin": 11, "Muscle": 13,
    "Bone": 111, "Skeleton": 111, "Marrow": 47,
    "SCord": 65, "SpinalCore": 65, "Brain": 18, "Eyes": 22,
    "Lung": 33, "Heart": 26, "Breast": 19,

    "Intestine": 44, "Liver": 32, "Kidney": 28, "Stomach": 67,
    "ParotidGland": 43,

    "Bladder": 15, "Ovary": 86, "Spleen": 66,  "Thyroid": 70,
    "Pancrease": 38, "GallBladder": 24,

}


def display_folder_structure(folder_base, n=1):
    """
    打印文件夹结构
    :param folder_base:
    :param n:
    :return:
    """
    if n == 1:
        print(folder_base, end="")
    fnames = os.listdir(folder_base)
    fpaths = [os.path.join(folder_base, fname) for fname in fnames]
    isfile = [os.path.isfile(fpath) for fpath in fpaths]
    n_file = sum(isfile)
    print(f" ({n_file} files)")
    for fname in os.listdir(folder_base):
        fpath = os.path.join(folder_base, fname)

        if os.path.isfile(fpath):
            # print("\t-", fname)
            pass
        elif os.path.isdir(fpath):
            print("\t" * n, "-", fname, end="")
            m = n + 1
            display_folder_structure(fpath, n=m)


class JpgProcessor(object):
    def __init__(self, folder_base):
        # 路径
        self.folder_base: str = folder_base
        self.folder_origin: str = ""
        self.folder_organs: str = ""
        # 图像文件
        self.img: sitk.Image = sitk.Image()
        self.img_seg: sitk.Image = sitk.Image()

    def set_folders(self, folder_origin=None, folder_organs=None):
        if folder_origin is None:
            self.folder_origin = os.path.join(self.folder_base, "DICOM", "CT")
        else:
            self.folder_origin = folder_origin

        if folder_organs is None:
            self.folder_organs = os.path.join(self.folder_base, "Segment")
        else:
            self.folder_organs = folder_organs

    def load_origin(self):
        """
        读取跟jpg分割文件对应的原始图像序列
        :param folder_origin:
        :return:
        """
        reader = sitk.ImageSeriesReader()
        ids = reader.GetGDCMSeriesIDs(self.folder_origin)
        assert len(ids) == 1, "源文件错误：没有找到序列或多个序列"
        fnames = reader.GetGDCMSeriesFileNames(directory=self.folder_origin, seriesID=ids[0])
        reader.SetFileNames(fnames)
        self.img = reader.Execute()
        return self.img

    def convert_origin_dcm2nii(self, fpath=None):
        """
        将原图像从dcm转换为nii
        :param fpath:
        :return:
        """
        if fpath is None:
            fpath = os.path.join(self.folder_base, "ct.nii")
        sitk.WriteImage(image=self.img, fileName=fpath)

    def convert_organ_jpg2nii(self, organ, threshold=200):
        """
        将某一器官的分割结果，从部分层的jpg保存为完整nii
        :param organ: 处理的器官
        :param threshold:
        :return:
        """
        # 获取直接保存jpg文件的文件夹路径
        folder_organ = os.path.join(self.folder_organs, organ, "3")
        # 根据原始图像生成空白背景
        seg = np.zeros_like(sitk.GetArrayViewFromImage(self.img))
        # 对每一张进行处理，得到完整的CT图
        for fname in os.listdir(folder_organ):
            fpath = os.path.join(folder_organ, fname)
            kind = filetype.guess(fpath)
            assert kind.extension == 'jpg', "分割jpg图片中含有其他格式文件"
            z = int(fname[-8:-4])  # 文件名中后四位是层数
            seg_slice = cv2.imread(filename=fpath, flags=0)
            seg[z] = seg_slice
        # jpg图片读取后有非0或255的数，需要处理, 以250为界限
        seg[seg > threshold] = 255
        seg[seg <= threshold] = 0

        # 转换为Image
        seg = sitk.GetImageFromArray(np.flip(seg))  # 输出需要完全翻转才能跟dcm一致
        seg.CopyInformation(self.img)
        seg = sitk.Cast(image=seg, pixelID=sitk.sitkUInt8)

        # 创建保存所有器官分割结果的文件夹
        folder_save = os.path.join(self.folder_organs, STOP_FOLDER_in_Folder_organs[0])
        if not os.path.exists(folder_save):
            os.mkdir(folder_save)

        sitk.WriteImage(image=seg, fileName=os.path.join(folder_save, organ + ".nii"))

        return seg

    def convert_organs_jpg2nii(self):
        pbar = tqdm(os.listdir(self.folder_organs))
        for fname in pbar:  # 对所有器官进行循环
            pbar.set_description(desc="Jpg2nii: %s" % fname)
            fpath = os.path.join(self.folder_organs, fname)
            if os.path.isdir(fpath):  # 判读是否是文件夹，排除其他文件
                if fname in STOP_FOLDER_in_Folder_organs:
                    continue
                else:
                    self.convert_organ_jpg2nii(organ=fname)
        pbar.close()

    def combine_organs(self):
        # 保存器官nii文件的路径
        folder_nii = os.path.join(self.folder_organs, STOP_FOLDER_in_Folder_organs[0])
        # 所有器官文件的list（除去特殊的如seg.nii)
        fnames = [i for i in os.listdir(folder_nii) if i not in STOP_ORGAN_in_All_Organs_nii]
        for fname in fnames:
            if fname[0:-4] not in OrganID:
                print(f"Organ {fname[0:-4]} not included in OrganID")
        # 根据原图像生成空白分割背景
        seg = np.zeros_like(sitk.GetArrayViewFromImage(self.img)).astype(np.uint8)
        seg_bool = seg.astype(bool)

        pbar = tqdm(OrganID)
        for organ_name in pbar:     # 对字典中的器官名进行循环
            fname = organ_name + ".nii"
            if fname in fnames:     # 在文件夹中寻找器官
                pbar.set_description(desc=organ_name)
                # 读取器官为数组，转换bool值
                organ = sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(folder_nii, fname)))
                organ_bool = organ.astype(bool)
                # 算差集
                seg_minus_organ = seg_bool ^ (seg_bool & organ_bool)
                # 将新器官添加到seg中
                seg = seg * seg_minus_organ + organ_bool * OrganID[organ_name]
                seg_bool = seg.astype(bool)
        pbar.close()

        seg = sitk.GetImageFromArray(seg)
        seg.CopyInformation(self.img)
        sitk.WriteImage(seg, os.path.join(folder_nii, "seg.nii"))

    def analyse_overlap(self):
        """
        功能函数，分析器官之间有没有重合的点
        :return: 重合的情况
        """
        folder_nii = os.path.join(self.folder_organs, STOP_FOLDER_in_Folder_organs[0])
        ROIs: list = os.listdir(folder_nii)
        stop_ROI: list = STOP_ORGAN_in_All_Organs_nii + ['Outline.nii', 'Body.nii'] \
                         + ['Muscle.nii', 'Skeleton.nii', 'Skin.nii']
        ROIs = [ROI for ROI in ROIs if ROI not in stop_ROI]

        for i in range(len(ROIs)):
            for j in range(i + 1, len(ROIs)):
                # 器官名称
                organ_i = ROIs[i][0:-4]
                organ_j = ROIs[j][0:-4]
                # 读取图像
                img_i = sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(folder_nii, ROIs[i]))).astype(bool)
                img_j = sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(folder_nii, ROIs[j]))).astype(bool)
                # 计算点数
                n_i = np.sum(img_i)
                n_j = np.sum(img_j)
                # 分析重合情况
                overlap = np.sum(img_i * img_j)
                percent_i = (overlap / n_i * 100).round(decimals=1)
                percent_j = (overlap / n_j * 100).round(decimals=1)
                ratio = (n_i / n_j).round(2)
                if overlap != 0 and (percent_i >= 0 or percent_j >= 0):
                    print(f"overlap: {overlap} ({percent_i}%, {percent_j}%)\t\t{organ_i}: {n_i};\t{organ_j}: {n_j};"
                          f"\t\t{ratio}")


if __name__ == "__main__":
    p = JpgProcessor(r"E:\SS-DCMProcessor\dataset\seg_manual\ARMIJOS_DE_DUQUE_ROSA_MARIA_97030634")
    p.set_folders()
    p.load_origin()
    # p.convert_organ_jpg2nii(organ="Outline")
    # p.convert_organs_jpg2nii()
    # p.analyse_overlap()
    p.combine_organs()
    pass
