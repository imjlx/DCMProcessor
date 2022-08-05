"""
@file    :  fusion.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/18 3:35   JHR          1.0         
"""
import shutil

import SimpleITK as sitk
import numpy as np
import pandas
import pandas as pd
import os
from tqdm import tqdm

from utlis.Segmentation import SegmentBase, SegmentAssembleImageFilter, SegmentSplitImageFilter
from utlis.Image import ImageResampler
from utlis.DICOM import DCMBase


# 从dcm生成CT、PET的原始nii
def dcm2nii(folder_base=r"D:\PETCT_sorted"):
    pbar = tqdm(os.listdir(folder_base))
    for folder_patient in pbar:
        pbar.set_description(folder_patient)
        folder_patient = os.path.join(folder_base, folder_patient)

        ct = DCMBase.ReadDCMSeries(os.path.join(folder_patient, "CT"))
        sitk.WriteImage(ct, os.path.join(folder_patient, "CT_origin.nii"))

        pet = DCMBase.ReadDCMSeries(os.path.join(folder_patient, "PET"))
        sitk.WriteImage(pet, os.path.join(folder_patient, "PET_origin.nii"))

    pbar.close()


# 翻转分割文件
def flip_seg(folder_base=r"D:\PETCT_sorted"):
    pbar = tqdm(os.listdir(folder_base))
    for folder_patient in pbar:
        pbar.set_description(folder_patient)
        folder_patient = os.path.join(folder_base, folder_patient)

        auto_path = os.path.join(folder_patient, "seg_auto.nii")
        if os.path.exists(auto_path):
            auto = sitk.GetArrayFromImage(sitk.ReadImage(auto_path))
            auto = sitk.GetImageFromArray(np.flip(auto, (1, 2)))
            auto.CopyInformation(sitk.ReadImage(auto_path))
            sitk.WriteImage(auto, auto_path)

        manual_path = os.path.join(folder_patient, "seg_manual.nii")
        manual = sitk.GetArrayFromImage(sitk.ReadImage(manual_path))
        manual = sitk.GetImageFromArray(np.flip(manual, (1, 2)))
        manual.CopyInformation(sitk.ReadImage(manual_path))
        sitk.WriteImage(manual, manual_path)

    pbar.close()


# 分割分割文件
def split_seg(folder_base=r"D:\PETCT_sorted"):
    for folder_patient in os.listdir(folder_base):
        print(folder_patient)
        folder_patient = os.path.join(folder_base, folder_patient)

        auto_path = os.path.join(folder_patient, "seg_auto.nii")
        manual_path = os.path.join(folder_patient, "seg_manual.nii")
        if os.path.exists(auto_path):
            spliter = SegmentSplitImageFilter(auto_path)
            spliter.Execute(os.path.join(folder_patient, "seg_split", "auto"))

        spliter = SegmentSplitImageFilter(manual_path)
        spliter.Execute(os.path.join(folder_patient, "seg_split", "manual"))


# 根据info的情况生成器官
def create_add(folder_base):    # 合并情况
    info = pd.read_excel(os.path.join(folder_base, "seg_split\\info.xlsx"), index_col="OrganID")
    for row in info.iterrows():
        if row[1]["OrganSelection"] == "manual+auto(合并)":
            print(folder_base)

            fname = str(row[0]) + "_" + row[1]["Standard"].strip() + ".nii"

            if not os.path.exists(os.path.join(folder_base, "seg_split", "manual", fname)):
                print("DO NOT exist")
                continue
            seg_manual = sitk.ReadImage(os.path.join(folder_base, "seg_split", "manual", fname))
            seg_auto = sitk.ReadImage(os.path.join(folder_base, "seg_split", "auto", fname))

            seg = seg_auto | seg_manual

            if not os.path.exists(os.path.join(folder_base, "seg_split", "process")):
                os.makedirs(os.path.join(folder_base, "seg_split", "process"))
            sitk.WriteImage(seg, os.path.join(folder_base, "seg_split", "process", fname))


# Intestine的情况
def create_Intestine_fat(folder_base):
    info = pd.read_excel(os.path.join(folder_base, "seg_split\\info.xlsx"), index_col="OrganID")
    if info.loc[44, "OrganSelection"] == "manual" and info.loc[44, "Manual_Percent"] != 0:
        folder = os.path.join(folder_base, "seg_split")
        # auto = sitk.ReadImage(os.path.join(folder, "auto", "44_Intestine.nii"))
        # manual = sitk.ReadImage(os.path.join(folder, "manual", "44_Intestine.nii"))

        print(folder)


def assemble(folder_base):
    info = pd.read_excel(os.path.join(folder_base, "seg_split\\info.xlsx"), index_col="OrganID")
    fpath_list = []
    for row in info.iterrows():
        fname = str(row[0]) + "_" + row[1]["Standard"].strip() + ".nii"
        if row[1]["OrganSelection"] == "manual":
            fpath_list.append(os.path.join(folder_base, "seg_split\\manual", fname))
        elif row[1]["OrganSelection"] == "auto":
            fpath_list.append(os.path.join(folder_base, "seg_split\\auto", fname))
        elif row[1]["OrganSelection"] == "manual+auto(合并)":
            fpath_list.append(os.path.join(folder_base, "seg_split\\process", fname))
        elif row[1]["OrganSelection"] == "无（分割失败）":
            pass
        elif pd.isnull(row[1]["OrganSelection"]):
            pass
        else:
            assert 0, "未考虑的标注"

    for i, fpath in enumerate(fpath_list):
        if not os.path.exists(fpath):
            print("未找到文件，请检查：", fpath)
            fpath_list.pop(i)

    assembler = SegmentAssembleImageFilter()
    assembler.SetFpathList(fpath_list=fpath_list)
    assembler.SetOrganIDDick(SegmentAssembleImageFilter.OrganID_standard)
    assembler.Execute(os.path.join(folder_base, "seg_fusion.nii"))
    pass


def resample_CT_PET_111(folder_base):

    ct = sitk.ReadImage(os.path.join(folder_base, "CT_origin.nii"))
    pet = sitk.ReadImage(os.path.join(folder_base, "PET_origin.nii"))
    atlas = sitk.ReadImage(os.path.join(folder_base, "seg_fusion.nii"))

    ct = ImageResampler.ResampleToNewSpacing(ct, (1, 1, 1), is_label=False, default_value=-1024, dtype=sitk.sitkInt16)
    pet = ImageResampler.ResampleToReferenceImage(pet, ref=ct, is_label=False, default_value=0, dtype=sitk.sitkFloat32)
    atlas = ImageResampler.ResampleToNewSpacing(atlas, (1, 1, 1), is_label=True, default_value=0, dtype=sitk.sitkUInt8)

    folder_save = os.path.join(folder_base, "resample_1_1_1")
    if not os.path.exists(folder_save):
        os.makedirs(folder_save)
    sitk.WriteImage(ct, os.path.join(folder_save, "CT.nii"))
    sitk.WriteImage(pet, os.path.join(folder_save, "PET.nii"))
    sitk.WriteImage(atlas, os.path.join(folder_save, "Atlas.nii"))


def resample_CT_PET_to_PET(folder_base):
    ct = sitk.ReadImage(os.path.join(folder_base, "CT_origin.nii"))
    pet = sitk.ReadImage(os.path.join(folder_base, "PET_origin.nii"))
    atlas = sitk.ReadImage(os.path.join(folder_base, "seg_fusion.nii"))

    ct = ImageResampler.ResampleToNewSpacing(ct, pet.GetSpacing(), is_label=False, default_value=-1024, dtype=sitk.sitkInt16)
    pet = ImageResampler.ResampleToReferenceImage(pet, ref=ct, is_label=False, default_value=0, dtype=sitk.sitkFloat32)
    atlas = ImageResampler.ResampleToNewSpacing(atlas, pet.GetSpacing(), is_label=True, default_value=0, dtype=sitk.sitkUInt8)

    folder_save = os.path.join(folder_base, "resample_to_pet")
    if not os.path.exists(folder_save):
        os.makedirs(folder_save)
    sitk.WriteImage(ct, os.path.join(folder_save, "CT.nii"))
    sitk.WriteImage(pet, os.path.join(folder_save, "PET.nii"))
    sitk.WriteImage(atlas, os.path.join(folder_save, "Atlas.nii"))


def create_info(folder_base):
    info: pd.DataFrame = pandas.read_excel(r"H:\info.xlsx", index_col="ID")
    pbar = tqdm(os.listdir(folder_base))
    for name in pbar:
        folder_patient = os.path.join(folder_base, name)
        # 分析分割出的器官
        seg = sitk.ReadImage(os.path.join(folder_patient, "seg_fusion.nii"))
        for row in info.iterrows():
            ID = row[0]
            if ID in sitk.GetArrayViewFromImage(seg):
                info.loc[ID, name] = 1

        # 分析原始DICOM文件
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(reader.GetGDCMSeriesFileNames(os.path.join(folder_patient, "CT")))
        reader.MetaDataDictionaryArrayUpdateOn()
        reader.Execute()
        info.loc[1, name] = reader.GetMetaData(slice=0, key="0010|0040")    # 性别
        info.loc[2, name] = reader.GetMetaData(slice=0, key="0010|0030")    # 出生日期

    info.to_excel(r"H:\info.xlsx")


if __name__ == "__main__":
    folder_base = r"H:\PETCT_sorted"
    pbar = tqdm(os.listdir(folder_base))
    for name in pbar:
        folder_patient = os.path.join(folder_base, name)
        shutil.rmtree(os.path.join(folder_patient, "resample_1_1_1"))
        shutil.rmtree(os.path.join(folder_patient, "seg_split"))










