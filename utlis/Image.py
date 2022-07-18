"""
@file    :  Image.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/15 15:37   JHR          1.0         
"""

import os
import filetype
from tqdm import tqdm

import cv2
import pydicom
import SimpleITK as sitk

import matplotlib.pyplot as plt
import numpy as np


class Image(object):
    def __init__(self):
        self.img: sitk.Image = sitk.Image()

    @staticmethod
    def PrintBasicInfo(img: sitk.Image):
        print("Size: \t\t", img.GetSize())
        print("Spacing: \t", img.GetSpacing())
        print("Origin: \t", img.GetOrigin())
        print("Direction: \t", img.GetDirection())
        print("PixelID: \t", img.GetPixelID())
        print("PixelType: \t", sitk.GetPixelIDValueAsString(img.GetPixelID()))

    @staticmethod
    def ResampleToNewSpacing(img: sitk.Image, new_spacing: tuple, is_label: bool = False, default_value=0):
        """
        将原图像重采样到新的分辨率
        :param img: 原图像
        :param new_spacing: 新的分辨率
        :param is_label: 是否为分割图像（决定插值方式）
        :param default_value: 空白默认值0，PET、seg为0，CT为-1024
        :return: 重采样后的图像
        """
        # 读取原图像的信息
        original_spacing = img.GetSpacing()
        original_size = img.GetSize()
        # 计算新图像的size
        new_size = [int(round(osz * ospc / nspc)) for osz, ospc, nspc in
                    zip(original_size, original_spacing, new_spacing)]

        # 调用sitk.Resample()
        resampler = sitk.ResampleImageFilter()
        # 基本信息
        resampler.SetOutputSpacing(new_spacing)  # 间距
        resampler.SetSize(new_size)  # 大小
        resampler.SetOutputOrigin(img.GetOrigin())  # 原点
        resampler.SetOutputDirection(img.GetDirection())  # 朝向
        # 变换类型
        resampler.SetTransform(sitk.Transform())
        # 空白默认值
        resampler.SetDefaultPixelValue(default_value)
        # 插值方式
        if is_label:
            resampler.SetInterpolator(sitk.sitkNearestNeighbor)
        else:
            resampler.SetInterpolator(sitk.sitkLinear)

        # 执行并返回
        return resampler.Execute(img)


if __name__ == "__main__":
    img = sitk.ReadImage(r"E:\SS-DCMProcessor\dataset\processed\ARMIJOS_DE_DUQUE_ROSA_MARIA_97030634(chenxin)\seg_manual.nii")
    # new = Image.ResampleToNewSpacing(img, new_spacing=(1, 1, 1), is_label=True)
    # sitk.Show(new)
    Image.PrintBasicInfo(img)
