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


def generate_img_nii(folder_base):
    patient_name = folder_base.split("\\")[-1]
    folder_save = os.path.join(r"F:\need to sort\processed", patient_name)

    folder_base = os.path.join(r"F:\need to sort\seg_Auto", patient_name)
    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            for f2 in os.listdir(f1_path):
                if re.match("CT", f2):
                    folder = os.path.join(f1_path, f2)

    a = DICOM.DCMFormatConverter()
    a.ReadDCMSeries(folder)
    a.DCM2nii(os.path.join(folder_save, "img.nii"), dtype=sitk.sitkInt16)


def generate_pet_nii(folder_base):
    patient_name = folder_base.split("\\")[-1]
    folder_save = os.path.join(r"F:\need to sort\processed", patient_name)
    folder_base = os.path.join(r"F:\need to sort\seg_Auto", patient_name)
    f0_path = folder_base
    for f1 in os.listdir(f0_path):
        f1_path = os.path.join(f0_path, f1)
        if os.path.isdir(f1_path):
            for f2 in os.listdir(f1_path):
                if re.match("PET", f2):
                    folder = os.path.join(f1_path, f2)

    a = DICOM.DCMFormatConverter()
    a.ReadDCMSeries(folder)
    a.DCM2nii(os.path.join(folder_save, "PET.nii"))

if __name__ == "__main__":
    folders_base = [
        r"F:\need to sort\seg_Manual\AnonyP1S1_PETCT19659",
        r"F:\need to sort\seg_Manual\AnonyP1S2_PETCT13098",
        r"F:\need to sort\seg_Manual\AnonyP2S1_PETCT08695",
        r"F:\need to sort\seg_Manual\AnonyP2S1_PETCT15840",
        r"F:\need to sort\seg_Manual\AnonyP4S1_PETCT13930",
        r"F:\need to sort\seg_Manual\AnonyP6S1_PETCT04344",
        r"F:\need to sort\seg_Manual\AnonyP7S1_PETCT07775",
        r"F:\need to sort\seg_Manual\AnonyP7S1_PETCT20247",
        r"F:\need to sort\seg_Manual\AnonyP11S1_PETCT07347",
        r"F:\need to sort\seg_Manual\AnonyP12S3_PETCT13166",
        r"F:\need to sort\seg_Manual\AnonyP15S2_PETCT16905",
        r"F:\need to sort\seg_Manual\AnonyP17S1_PETCT19111",
        r"F:\need to sort\seg_Manual\AnonyP18S1_PETCT19738",
        r"F:\need to sort\seg_Manual\AnonyP18S2_PETCT18822",
        r"F:\need to sort\seg_Manual\AnonyP18S3_PETCT20454",
        r"F:\need to sort\seg_Manual\AnonyP21S1_PETCT02616",
        r"F:\need to sort\seg_Manual\AnonyP21S3_PETCT11232",
        r"F:\need to sort\seg_Manual\AnonyP46S1_PETCT03359",
        r"F:\need to sort\seg_Manual\AnonyP24S1_PETCT17219",
        r"F:\need to sort\seg_Manual\AnonyP25S1_PETCT02437",
        r"F:\need to sort\seg_Manual\AnonyP25S2_PETCT13079",
        r"F:\need to sort\seg_Manual\AnonyP28S1_PETCT03330",
        r"F:\need to sort\seg_Manual\AnonyP29S1_PETCT01835",
        r"F:\need to sort\seg_Manual\AnonyP30S1_PETCT03388",
        r"F:\need to sort\seg_Manual\AnonyP30S1_PETCT08560",
        r"F:\need to sort\seg_Manual\AnonyP32S1_PETCT04649",
        r"F:\need to sort\seg_Manual\AnonyP33S1_PETCT09798",
        r"F:\need to sort\seg_Manual\AnonyP36S1_PETCT00837",
        r"F:\need to sort\seg_Manual\AnonyP36S1_PETCT05060",
        r"F:\need to sort\seg_Manual\AnonyP37S1_PETCT09454",
        r"F:\need to sort\seg_Manual\AnonyP38S1_PETCT00566",
        r"F:\need to sort\seg_Manual\AnonyP42S1_PETCT06512",
        r"F:\need to sort\seg_Manual\AnonyP44S1_PETCT02304",
    ]
    for folder_base in folders_base:
        print(folder_base)
        # convert_organs(folder_base)
        # assemble_organs(folder_base)
        # split_organs_manual(folder_base)
        # move_organs_manual(folder_base)
        # split_organs_auto(folder_base)
        # move_organs_auto(folder_base)
        # move_seg(folder_base)
        generate_img_nii(folder_base)
        # generate_pet_nii(folder_base)
        pass

    # print_folder_as_list(folder_base=r"F:\need to sort\seg_Manual")