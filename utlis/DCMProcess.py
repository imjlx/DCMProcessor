#!/usr/bin/env python
# encoding: utf-8
"""
    @File       : DCMProcess.py
    @Time       : 2022/1/7 15:50
    @Author     : Haoran Jia
    @license    : Copyright(c) 2022 Haoran Jia. All rights reserved.
    @contact    : 21211140001@fudan.m.edu.cn
    @Description：
"""

import SimpleITK as sitk
import numpy as np
import os


class DCMSerieProcessor(object):
    """
    作用： 读取文件夹中的DCM文件序列，然后进行分析
    目标情况：一个文件夹中只有一个有价值的目标序列，但是可能掺杂着若干定位像
    """
    def __init__(self, folder):
        """
        将所有序列保存在列表中
        :param folder: 文件夹地址
        """
        # 文件夹地址
        self.folder = folder
        # 每个序列的ID, 以及对应的所有文件名
        self.series_ID = []
        self.series_fnames = []
        self.load_series_fnames()
        # 序列数量
        self.N = len(self.series_fnames)
        self.N_files = [len(fnames) for fnames in self.series_fnames]

        # 需要的序列
        self.serie_ID = None
        self.serie_fnames = None
        self.reader = None
        self.img = None

        # 信息
        self.size = None
        self.spacing = None
        self.origin = None
        self.direction = None

    def load_series_fnames(self):
        """
        加载所有序列, 以及对应的所有文件名
        :return: 无
        """
        self.series_ID = sitk.ImageSeriesReader.GetGDCMSeriesIDs(self.folder)
        for serie_ID in self.series_ID:
            serie_fnames = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(self.folder, serie_ID)
            self.series_fnames.append(serie_fnames)

    def find_target_serie(self, method="Longest"):

        if method == "Longest":
            n_files = [len(serie_file_names) for serie_file_names in self.series_fnames]
            self.serie_ID = self.series_ID[np.argmax(n_files)]
            self.serie_fnames = self.series_fnames[np.argmax(n_files)]

    def read(self, isInfo=True):
        """
        读取目标Image
        :return: 无
        """
        # 找到目标序列
        self.find_target_serie()

        self.reader = sitk.ImageSeriesReader()
        # 设置是否读取Meta Data
        if isInfo:
            self.reader.MetaDataDictionaryArrayUpdateOn()
            self.reader.LoadPrivateTagsOn()
        # 设置读取路径和序列号
        self.reader.SetFileNames(self.serie_fnames)
        # 读取文件
        self.img = self.reader.Execute()

        return self.img

    def show(self):
        sitk.Show(self.img, "ha")

    def basic_info(self):
        self.size = self.img.GetSize()
        self.spacing = self.img.GetSpacing()
        self.origin = self.img.GetOrigin()
        self.direction = self.img.GetDirection()

    def clip(self):
        """
        将图像的范围裁剪到-1024到3071之间
        :return: 裁剪后的图像
        """
        arr = sitk.GetArrayFromImage(self.img)
        arr = np.clip(arr, -1024, 3071)
        img = sitk.GetImageFromArray(arr)
        img.CopyInformation(self.img)
        self.img = img
        return img

    def resample(self, img_reference):
        """
        根据参考图像对图像进行重采样
        :param img_reference: 参考图像
        :return: 无
        """
        resampler = sitk.ResampleImageFilter()
        resampler.SetReferenceImage(img_reference)
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetTransform(sitk.TranslationTransform(3))
        resampler.SetOutputPixelType(sitk.sitkInt16)
        resampler.SetDefaultPixelValue(-1024)
        self.img = resampler.Execute(self.img)

    def write(self, fpath):
        sitk.WriteImage(self.img, fpath)


class DCMSeriesProcessor(DCMSerieProcessor):
    def __init__(self, folder):
        super().__init__(folder)
        self.readers = []
        self.imgs = []
        self.infos = []

    def Distinguish(self):
        """
        分辨不同序列, 生成info
        :return:
        """
        for i in range(self.N):
            series_description = self.readers[i].GetMetaData(slice=0, key="0008|103e")
            slice_distance = self.imgs[i].GetSpacing()[2]
            convolutional_kernel = self.readers[i].GetMetaData(slice=0, key="0018|1210")
            content_time = self.readers[i].GetMetaData(slice=0, key="0008|0033")
            self.infos.append([series_description, slice_distance, convolutional_kernel, content_time])




