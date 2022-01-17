#!/usr/bin/env python
# encoding: utf-8
"""
    @File       : DCMReader.py
    @Time       : 2022/1/7 15:48
    @Author     : Haoran Jia
    @license    : Copyright(c) 2022 Haoran Jia. All rights reserved.
    @contact    : 21211140001@fudan.m.edu.cn
    @Description：
"""

from utlis import folderControl
from utlis import DCMReader
import SimpleITK as sitk

folder = "dataset/S0006/P0566783_2020-02-12"
folders = folderControl.all_folders("dataset")

for folder in folders:
    reader = DCMReader.DCMSeriesReader(folder)
    reader.Execute()
    reader.Distinguish()
    print(folder)
    print(reader.infos)


