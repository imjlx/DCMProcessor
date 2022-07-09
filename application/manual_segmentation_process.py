"""
@file    :  manual_segmentation_process.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/8 22:24   JHR          1.0         
"""

from utlis import Segmentation
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


def organs_convert(folder_base):
    folder_organs = os.path.join(folder_base, "Segment")
    folders_organ = [f for f in os.listdir(folder_organs)
                     if f not in ["Current", "Origin"]]
    pbar = tqdm(folders_organ)
    for fname in pbar:
        fpath = os.path.join(folder_organs, fname)
        if os.path.isdir(fpath):
            pbar.set_description(fname)
            folder_jpg = os.path.join(fpath, "3")
            fpath_save = os.path.join(folder_base, "Segment_organs_nii", fname+".nii")

            converter = Segmentation.Jpg2niiConverter()
            converter.ReadOriginImageSeries(os.path.join(folder_base, "DICOM\\CT"))
            converter.OrganConvert(folder_jpg=folder_jpg, fpath_save=fpath_save)


def assemble_organs(folder_base):
    folder_organs = os.path.join(folder_base, "Segment_organs_nii")
    fpath_save = os.path.join(folder_base, "seg.nii")

    f = Segmentation.SegmentAssembleImageFilter(folder_organs)
    f.ReadOriginImageSeries(os.path.join(folder_base, "DICOM\\CT"))
    f.Execute(fpath_save)


def split_organs(folder_base):
    fpath_seg = os.path.join(folder_base, "seg.nii")
    folder_save = os.path.join(folder_base, "Segment_split")
    f = Segmentation.SegmentSplitImageFilter(fpath_seg)
    f.Execute(folder_save)


if __name__ == "__main__":
    folder_base = r"E:\SS-DCMProcessor\dataset\seg_manual\ARMIJOS_DE_DUQUE_ROSA_MARIA_97030634"
    # organs_convert(folder_base)
    # assemble_organs(folder_base)
    split_organs(folder_base)

