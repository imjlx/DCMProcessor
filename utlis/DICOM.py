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
    def ReadDCMSeries(folder: str, load_metadata=False, load_private_tags=False):
        """
        利用sitk从文件夹中读取唯一序列的dcm文件
        :param folder: 读取文件夹
        :param load_metadata: 是否读取Metadata
        :param load_private_tags: 是否读取Private tags
        :return: 若不读取Metadata， 返回读取的图像；若读取，返回(img, reader)
        """
        reader = sitk.ImageSeriesReader()
        ID = reader.GetGDCMSeriesIDs(folder)
        assert len(ID) == 1, "No Series or more than one series in %s."%folder
        fnames = reader.GetGDCMSeriesFileNames(directory=folder, seriesID=ID[0])
        reader.SetFileNames(fnames)

        if load_metadata:
            reader.MetaDataDictionaryArrayUpdateOn()
            if load_private_tags:
                reader.LoadPrivateTagsOn()
            img = reader.Execute()
            return img, reader
        else:
            img = reader.Execute()
            return img

    @staticmethod
    def PrintMetaData(reader: sitk.ImageSeriesReader):
        # 先读取图片
        img = reader.Execute()
        # 通过任一（第0）层获取键值
        keys: tuple = reader.GetMetaDataKeys(slice=0)

        print(f"Total: {len(keys)} Tags, \t {img.GetSize()[2]} slices.")

        for key in reader.GetMetaDataKeys(slice=0):
            values = []
            for s in range(img.GetSize()[2]):
                values.append(reader.GetMetaData(s, key))
            values_set = set(values)
            if len(values_set) == 1:
                print(f"{key} equal:\t{reader.GetMetaData(0, key)}")
            else:
                print(f"{key} **{len(values_set)} values: eg. {reader.GetMetaData(0, key)}")

    @staticmethod
    def PrintImportantMetaData(reader: sitk.ImageSeriesReader):
        # 获取层数
        img = reader.Execute()
        slice = img.GetSize()[2]
        # 重建字典
        keys_same = {
            "0020|000e": "Series Instance UID",
            "0010|0010": "Patient's name",
            "0018|0008": "Image Type",
            "0028|0101": "Bits Stored",

            "0008|0050": "Slice Thickness",
            "0028|0030": "Pixel Spacing",
            "0028|0010": "Rows",
            "0028|0011": "Columns",
            "0020|0037": "Image Orientation (Patient)",
        }

        keys_diff = {
            "0020|0013": "Instance Number",
            "0020|1041": "Slice Location",
        }

        for key in keys_same:
            print(f"{key}: {keys_same[key]:<30}", end="\t")
            if reader.HasMetaDataKey(0, key):
                print(reader.GetMetaData(0, key))
            else:
                print()

        print()
        for key in keys_diff:
            print(f"{key}: {keys_diff[key]:<30}", end="\t")
            if reader.HasMetaDataKey(0, key):
                start = reader.GetMetaData(0, key)
                end = reader.GetMetaData(slice-1, key)
                print(f"{start} : {end} : {(float(start)-float(end))/(slice-1)}")
            else:
                print()

        print()
        print("0020|0032: {:<30}".format("Image Position (Patient)"), end="\t")
        if reader.HasMetaDataKey(0, "0020|0032"):
            start = reader.GetMetaData(0, "0020|0032")
            end = reader.GetMetaData(slice - 1, "0020|0032")
            print(start, end=" ,")
            s = start.split("\\")[-1]
            e = end.split("\\")[-1]
            print(f"{s} : {e} : {(float(s) - float(e)) / (slice - 1)}")
        else:
            print()


if __name__ == "__main__":
    folder_base = r"E:\SS-DCMProcessor\dataset\dcm2nii"
    folder_ct = r"E:\SS-DCMProcessor\dataset\dcm2nii\CT"
    folder_pet = r"E:\SS-DCMProcessor\dataset\dcm2nii\PET"

    ct, reader_ct = DCMBase.ReadDCMSeries(folder_ct, load_metadata=True)
    # pet, reader_pet = DCMBase.ReadDCMSeries(folder_pet, load_metadata=True)
    DCMBase.PrintImportantMetaData(reader_ct)







