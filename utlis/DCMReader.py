#!/usr/bin/env python
# encoding: utf-8
"""
    @File       : DCMReader.py
    @Time       : 2022/1/7 15:50
    @Author     : Haoran Jia
    @license    : Copyright(c) 2022 Haoran Jia. All rights reserved.
    @contact    : 21211140001@fudan.m.edu.cn
    @Description：
"""

import SimpleITK as sitk
import numpy as np


class DCMSeriesReader(object):
    def __init__(self, folder):
        """
        将所有序列保存在列表中
        :param folder: 文件夹地址
        """
        # 文件夹地址
        self.folder = folder

        # 读取器和图像
        self.reader = []
        self.img = []

        # 删除了定位像后，每个序列的所有文件名
        self.series_file_names = []
        self.load_series_file_names()

        # 序列数量
        self.N = len(self.series_file_names)

        # 不同序列的关键信息: [分辨率, 窗位]
        self.infos = []

    def load_series_file_names(self):
        """
        加载删除了定位像的所有序列的所有文件名
        :return:
        """
        series_id = sitk.ImageSeriesReader.GetGDCMSeriesIDs(self.folder)
        for serie_id in series_id:
            serie_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(self.folder, serie_id)
            if len(serie_file_names) > 5:
                self.series_file_names.append(serie_file_names)

    def Execute(self):
        """
        读取Image，生成reader和img列表
        :return: 无
        """
        for i in range(self.N):
            # 实例化一个reader
            reader = sitk.ImageSeriesReader()
            # 设置读取Meta Data
            reader.MetaDataDictionaryArrayUpdateOn()
            reader.LoadPrivateTagsOn()
            # 设置读取路径和序列号
            reader.SetFileNames(self.series_file_names[i])
            # 读取文件
            img = reader.Execute()

            # 将img和reader保存
            self.reader.append(reader)
            self.img.append(img)

    def Distinguish(self):
        """
        分辨不同序列, 生成info
        :return:
        """
        for i in range(self.N):
            series_description = self.reader[i].GetMetaData(slice=0, key="0008|103e")
            slice_distance = self.img[i].GetSpacing()[2]
            convolutional_kernel = self.reader[i].GetMetaData(slice=0, key="0018|1210")
            content_time = self.reader[i].GetMetaData(slice=0, key="0008|0033")
            self.infos.append([series_description, slice_distance, convolutional_kernel, content_time])






