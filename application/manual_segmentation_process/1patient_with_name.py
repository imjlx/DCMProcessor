"""
@file    :  1patient_with_name.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/8 22:24   JHR          1.0         
"""
import re
import shutil
import SimpleITK as sitk
from utlis import Segmentation, DICOM
from tqdm import tqdm
import os


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


def organs_convert(folder_base, rewrite=False):
    folder_organs = os.path.join(folder_base, "Segment")
    folders_organ = [f for f in os.listdir(folder_organs)
                     if f not in ["Current", "Current2", "Origin","Origin2", "1", "2", "3"]]
    pbar = tqdm(folders_organ)
    for fname in pbar:
        fpath = os.path.join(folder_organs, fname)
        if os.path.isdir(fpath):
            pbar.set_description("Converting organs: %s" % fname)
            folder_jpg = os.path.join(fpath, "3")
            fpath_save = os.path.join(folder_base, "Segment_organs_nii", fname + ".nii")

            if os.path.exists(fpath_save) and (rewrite is False):
                pass
            else:
                converter = Segmentation.Jpg2niiConverter()
                converter.ReadOriginImageSeries(os.path.join(folder_base, "DICOM\\CT"))
                converter.OrganConvert(folder_jpg=folder_jpg, fpath_save=fpath_save)


def assemble_organs(folder_base):
    folder_organs = os.path.join(folder_base, "Segment_organs_nii")
    fpath_save = os.path.join(folder_base, "seg.nii")

    f = Segmentation.SegmentAssembleImageFilter(folder_organs)
    f.ReadOriginImageSeries(os.path.join(folder_base, "DICOM\\CT"))
    f.Execute(fpath_save)


def split_organs_manual(folder_base):
    # 手动分割部分
    fpath_seg = os.path.join(folder_base, "seg.nii")
    folder_save = os.path.join(folder_base, "Segment_split_manual")
    f = Segmentation.SegmentSplitImageFilter(fpath_seg)
    f.Execute(folder_save)


def split_organs_auto(folder_base):
    # 自动分割部分
    fpath_seg = os.path.join(folder_base, "DICOM\\CT\\seg.nii")
    fpath_rt = os.path.join(folder_base, "DICOM\\CT\\RTSTRUCT.dcm")
    patient_name = folder_base.split("\\")[-1]
    folder_base = os.path.join(r"F:\need to sort\seg_Auto", patient_name)
    if not os.path.exists(folder_base):
        os.makedirs(folder_base)
    shutil.copyfile(src=fpath_seg, dst=os.path.join(folder_base, "seg.nii"))
    shutil.copyfile(src=fpath_rt, dst=os.path.join(folder_base, "RTSTRUCT.dcm"))

    f = Segmentation.SegmentSplitImageFilter(os.path.join(folder_base, "seg.nii"))
    f.Execute(os.path.join(folder_base, "Segment_split_auto"))


def move_splited_organs(folder_base):
    patient_name = folder_base.split("\\")[-1]
    folder_manual = os.path.join(folder_base, "Segment_split_manual")
    folder_auto = os.path.join(r"F:\need to sort\seg_Auto", patient_name, "Segment_split_auto")

    folder_save_base = os.path.join(r"F:\need to sort\seg_per_organ", patient_name)
    folder_save_manual = os.path.join(folder_save_base, "manual")
    folder_save_auto = os.path.join(folder_save_base, "auto")

    if not os.path.exists(folder_save_manual):
        os.makedirs(folder_save_manual)
    if not os.path.exists(folder_save_auto):
        os.makedirs(folder_save_auto)

    pbar = tqdm(os.listdir(folder_manual))
    for fname in pbar:
        pbar.set_description("Move files(manual)")
        shutil.copyfile(src=os.path.join(folder_manual, fname), dst=os.path.join(folder_save_manual, fname))
    pbar.close()

    pbar = tqdm(os.listdir(folder_auto))
    for fname in pbar:
        pbar.set_description("Move files(auto)")
        shutil.copyfile(src=os.path.join(folder_auto, fname), dst=os.path.join(folder_save_auto, fname))
    pbar.close()


def move_seg(folder_base):
    patient_name = folder_base.split("\\")[-1]
    fpath_manual = os.path.join(folder_base, "seg.nii")
    fpath_auto = os.path.join(folder_base, "DICOM", "CT", "seg.nii")

    folder_save = os.path.join(r"F:\need to sort\processed", patient_name)
    shutil.copyfile(src=fpath_auto, dst=os.path.join(folder_save, "seg_auto.nii"))
    shutil.copyfile(src=fpath_manual, dst=os.path.join(folder_save, "seg_manual.nii"))


def print_folder_as_list(folder_base):
    for fname in os.listdir(folder_base):
        print("r\"", os.path.join(folder_base, fname), "\",")


def generate_pet_nii(folder_base):
    folder = os.path.join(folder_base, "DICOM", "PET")
    patient_name = folder_base.split("\\")[-1]
    folder_save = os.path.join(r"F:\need to sort\processed", patient_name)

    a = DICOM.DCMFormatConverter()
    a.ReadSeries(folder)
    a.DCM2nii(os.path.join(folder_save, "PET.nii"))


def move_origin(folder_base):
    for name in os.listdir(folder_base):
        if re.match("Anony", name):
            pass
        else:
            print(name)
            CT = os.path.join(folder_base, name, "DICOM", "CT")
            PET = os.path.join(folder_base, name, "DICOM", "PET")

            if not os.path.exists(os.path.join("F:\PETCT_sorted", name, "CT")):
                os.makedirs(os.path.join("F:\PETCT_sorted", name, "CT"))

            if not os.path.exists(os.path.join("F:\PETCT_sorted", name, "PET")):
                os.makedirs(os.path.join("F:\PETCT_sorted", name, "PET"))

            for fname in os.listdir(CT):
                shutil.copyfile(src=os.path.join(CT, fname),
                                dst=os.path.join("F:\PETCT_sorted", name, "CT", fname))

            for fname in os.listdir(PET):
                shutil.copyfile(src=os.path.join(PET, fname),
                                dst=os.path.join("F:\PETCT_sorted", name, "PET", fname))


if __name__ == "__main__":
    folder_base = r"F:\need to sort\seg_Manual"
    move_origin(folder_base)







