"""
@file    :  fusion.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/18 3:35   JHR          1.0         
"""
import SimpleITK as sitk
import pandas as pd
import os
from utlis.Segmentation import SegmentBase, SegmentAssembleImageFilter
from utlis.Image import ImageResampler


def create_add(folder_base):
    info = pd.read_excel(os.path.join(folder_base, "info.xlsx"), index_col="OrganID")
    for row in info.iterrows():
        if row[1]["OrganSelection"] == "manual+auto(合并)":
            fname = str(row[0]) + "_" + row[1]["Standard"] + ".nii"

            seg_manual = sitk.ReadImage(os.path.join(folder_base, "manual", fname))
            seg_auto = sitk.ReadImage(os.path.join(folder_base, "auto", fname))
            seg = seg_auto | seg_manual

            if not os.path.exists(os.path.join(folder_base, "process")):
                os.makedirs(os.path.join(folder_base, "process"))
            sitk.WriteImage(seg, os.path.join(folder_base, "process", fname))


def assemble(folder_base):
    info = pd.read_excel(os.path.join(folder_base, "info.xlsx"), index_col="OrganID")
    fpath_list = []
    for row in info.iterrows():
        fname = str(row[0]) + "_" + row[1]["Standard"].strip() + ".nii"
        if row[1]["OrganSelection"] == "manual":
            fpath_list.append(os.path.join(folder_base, "manual", fname))
        elif row[1]["OrganSelection"] == "auto":
            fpath_list.append(os.path.join(folder_base, "auto", fname))
        elif row[1]["OrganSelection"] == "manual+auto(合并)":
            fpath_list.append(os.path.join(folder_base, "process", fname))
        else:
            print(f"No such organ: {fname}\t\t", row[1]["OrganSelection"])

    assembler = SegmentAssembleImageFilter()
    assembler.SetFpathList(fpath_list=fpath_list)
    assembler.SetOrganIDDick(SegmentAssembleImageFilter.OrganID_standard)
    assembler.Execute(os.path.join(folder_base, "seg_fusion.nii"))
    pass


def Resample(folder_base):

    ct = sitk.ReadImage(os.path.join(folder_base, "img.nii"))
    pet = sitk.ReadImage(os.path.join(folder_base, "PET.nii"))
    atlas = sitk.ReadImage(os.path.join(folder_base, "seg_fusion.nii"))

    # ct = ImageResampler.ResampleToNewSpacing(ct, (1, 1, 1), is_label=False, default_value=-1024)
    pet = ImageResampler.ResampleToNewSpacing(pet, (1, 1, 1), is_label=False, default_value=0)
    ct = ImageResampler.ResampleToReferenceImage(ct, ref=pet, is_label=False, default_value=-1024)
    # pet = ImageResampler.ResampleToReferenceImage(pet, ref=ct, is_label=False, default_value=0)
    atlas = ImageResampler.ResampleToNewSpacing(atlas, (1, 1, 1), is_label=True, default_value=0)

    folder_save = os.path.join(folder_base, "resample_1_1_1")
    if not os.path.exists(folder_save):
        os.makedirs(folder_save)
    sitk.WriteImage(ct, os.path.join(folder_save, "CT.nii"))
    sitk.WriteImage(pet, os.path.join(folder_save, "PET.nii"))
    sitk.WriteImage(atlas, os.path.join(folder_save, "Atlas.nii"))


if __name__ == "__main__":
    folder = r"F:\need to sort\processed\AnonyP1S2_PETCT13098"
    # create_add(folder)
    # assemble(folder)
    Resample(folder)












