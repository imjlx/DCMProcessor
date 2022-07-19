"""
@file    :  DICOM.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/10 15:04   JHR          1.0         
"""

import os
import filetype
from tqdm import tqdm

import cv2
import pydicom
import SimpleITK as sitk

import matplotlib.pyplot as plt
import numpy as np

from utlis.Image import Image


class DCMBase(Image):
    def __init__(self):
        super(DCMBase, self).__init__()
        pass

    @staticmethod
    def _ReadDCMSeries(folder: str) -> sitk.Image:
        """
        利用sitk从文件夹中读取唯一序列的dcm文件
        :param folder: 读取文件夹
        :return: 读取的图像
        """
        reader = sitk.ImageSeriesReader()
        ID = reader.GetGDCMSeriesIDs(folder)
        assert len(ID) == 1, "No Series or more than one series in %s."%folder
        fnames = reader.GetGDCMSeriesFileNames(directory=folder, seriesID=ID[0])
        reader.SetFileNames(fnames)
        img = reader.Execute()
        return img

    @staticmethod
    def _ConvertImageDcm2nii(dcm: sitk.Image, dtype=None) -> sitk.Image:
        """
        直接将dcm读取后保存的nii在Amide中与原始图像朝向相反，需要进行翻转
        本函数实现对读取的dcm文件进行翻转操作，使可以直接保存为nii
        :param dcm: 原dcm图像
        :param dtype: 可转换图片的数据类型, 默认与原图相同
        :return: 转换后可保存为nii的图像
        """
        nii = sitk.GetArrayFromImage(dcm)
        nii = np.flip(nii, axis=(1, 2))
        nii = sitk.GetImageFromArray(nii)
        nii.CopyInformation(dcm)

        if dtype is not None:
            nii = sitk.Cast(nii, dtype)

        return nii


class DCMFormatConverter(DCMBase):
    def __init__(self):
        super().__init__()
        self.img: sitk.Image = sitk.Image()

    def ReadDCMSeries(self, folder):
        self.img = self._ReadDCMSeries(folder)
        return self.img

    def DCM2nii(self, fpath, dtype=None):
        img = self._ConvertImageDcm2nii(self.img, dtype=dtype)
        sitk.WriteImage(img, fpath)
        return img







