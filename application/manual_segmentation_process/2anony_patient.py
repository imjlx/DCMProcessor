"""
@file    :  2anony_patient.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/10 14:31   JHR          1.0         
"""
import os
import re
import shutil
import SimpleITK as sitk

from tqdm import tqdm

from utlis import Segmentation, DICOM


def convert_organs(folder_base):
    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            for f2 in os.listdir(f1_path):
                f2_path = os.path.join(f1_path, f2)
                organs = [f for f in os.listdir(f2_path)
                                if f not in ["all_organs_nii", "all_organs_split", "SCB", "SCB_Debug1", "SCB_Debug2", "SCB_Debug3", ]]
                pbar = tqdm(organs)
                for organ in pbar:
                    if os.path.isdir(os.path.join(f2_path, organ)):
                        pbar.set_description("Convert_organs: %s" % organ)
                        c = Segmentation.Dcm2niiConverter()
                        c.OrganConvert(folder_series=os.path.join(f2_path, organ),
                                       fpath_save=os.path.join(f2_path, "all_organs_nii", organ+".nii"))
                pbar.close()


def assemble_organs(folder_base):
    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            for f2 in os.listdir(f1_path):
                f2_path = os.path.join(f1_path, f2)
                folder_nii = os.path.join(f2_path, "all_organs_nii")
                a = Segmentation.SegmentAssembleImageFilter(folder_nii)
                a.ReadOriginImageSeries(f2_path)
                a.Execute(os.path.join(f2_path, "seg.nii"))

def split_organs_manual(folder_base):
    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            for f2 in os.listdir(f1_path):
                f2_path = os.path.join(f1_path, f2)

                f = Segmentation.SegmentSplitImageFilter(os.path.join(f2_path, "seg.nii"))
                f.Execute(os.path.join(f2_path, "all_organs_split"))


def move_organs_manual(folder_base):
    patient_name = folder_base.split("\\")[-1]
    folder_to = os.path.join(r"F:\need to sort\seg_per_organ", patient_name, "manual")
    if not os.path.exists(folder_to):
        os.makedirs(folder_to)

    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            for f2 in os.listdir(f1_path):
                f2_path = os.path.join(f1_path, f2)

                folder_from = os.path.join(f2_path, "all_organs_split")

                pbar = tqdm(os.listdir(folder_from))
                for fname in pbar:
                    pbar.set_description("Move manual：%s"%fname)
                    shutil.copyfile(src=os.path.join(folder_from, fname),
                                    dst=os.path.join(folder_to, fname))
                pbar.close()


def split_organs_auto(folder_base):
    patient_name = folder_base.split("\\")[-1]
    folder_base = os.path.join(r"F:\need to sort\seg_Auto", patient_name)
    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            for f2 in os.listdir(f1_path):
                f2_path = os.path.join(f1_path, f2)
                if re.match("CT", f2):
                    if not os.path.exists(os.path.join(f2_path, "seg.nii")):
                        pass
                    else:
                        f = Segmentation.SegmentSplitImageFilter(os.path.join(f2_path, "seg.nii"))
                        f.Execute(os.path.join(f1_path, "all_organs_split"))


def move_organs_auto(folder_base):
    patient_name = folder_base.split("\\")[-1]
    folder_to = os.path.join(r"F:\need to sort\seg_per_organ", patient_name, "auto")
    if not os.path.exists(folder_to):
        os.makedirs(folder_to)
    folder_base = os.path.join(r"F:\need to sort\seg_Auto", patient_name)
    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            folder_from = os.path.join(f1_path, "all_organs_split")

            pbar = tqdm(os.listdir(folder_from))
            for fname in pbar:
                pbar.set_description("Move auto：%s" % fname)
                shutil.copyfile(src=os.path.join(folder_from, fname),
                                dst=os.path.join(folder_to, fname))
            pbar.close()


def move_seg(folder_base):
    patient_name = folder_base.split("\\")[-1]

    # manual\
    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            for f2 in os.listdir(f1_path):
                f2_path = os.path.join(f1_path, f2)
                fpath_manual = os.path.join(f2_path, "seg.nii")

    # auto
    folder_base = os.path.join(r"F:\need to sort\seg_Auto", patient_name)
    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            for f2 in os.listdir(f1_path):
                f2_path = os.path.join(f1_path, f2)
                if re.match("CT", f2):
                    fpath_auto = os.path.join(f2_path, "seg.nii")

    folder_save = os.path.join(r"F:\need to sort\processed", patient_name)
    shutil.copyfile(src=fpath_auto, dst=os.path.join(folder_save, "seg_auto.nii"))
    shutil.copyfile(src=fpath_manual, dst=os.path.join(folder_save, "seg_manual.nii"))


def print_folder_as_list(folder_base):
    for fname in os.listdir(folder_base):
        print("r\"", os.path.join(folder_base, fname), "\",")


def move_origin(folder_base):
    folder_to = r"F:\PETCT_sorted"
    for folder_patient in os.listdir(folder_base):
        name = folder_patient.split("\\")[-1]
        print(name)
        if re.match(pattern="Anony", string=folder_patient):
            folder_patient = os.path.join(folder_base, folder_patient)
            for PET_01 in os.listdir(folder_patient):
                PET_01 = os.path.join(folder_patient, PET_01)
                for folder in os.listdir(PET_01):
                    if re.match("CT", folder):
                        print("CT....")
                        folder = os.path.join(PET_01, folder)
                        if not os.path.exists(os.path.join(folder_to, name, "CT")):
                            os.makedirs(os.path.join(folder_to, name, "CT"))
                        for fname in os.listdir(folder):
                            shutil.copyfile(src=os.path.join(folder, fname),
                                            dst=os.path.join(folder_to, name, "CT", fname))
                    elif re.match("PET", folder):
                        print("PET....")
                        folder = os.path.join(PET_01, folder)
                        if not os.path.exists(os.path.join(folder_to, name, "PET")):
                            os.makedirs(os.path.join(folder_to, name, "PET"))
                        for fname in os.listdir(folder):
                            shutil.copyfile(src=os.path.join(folder, fname),
                                            dst=os.path.join(folder_to, name, "PET", fname))


if __name__ == "__main__":
    folder_base = r"F:\need to sort\seg_Auto"
    move_origin(folder_base)
