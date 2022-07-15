"""
@file    :  2anony_patient.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :

@Modify Time      @Author      @Version
------------      -------      --------
2022/7/10 14:31   JHR          1.0
"""

import pandas as pd
import SimpleITK as sitk
import os
import numpy as np
from tqdm import tqdm


def organs_in_dataset():
    info:pd.DataFrame = pd.read_excel(io=r"D:\脚本\DCMProcessor\dataset\OrganID.xlsx", index_col="OrganID")

    for patient_name in os.listdir(r"F:\need to sort\seg_per_organ"):
        patient_path = os.path.join(r"F:\need to sort\seg_per_organ", patient_name)

        for fname in os.listdir(os.path.join(patient_path, "manual")):
            index = int(fname.split('_')[0])
            info.loc[index, patient_name+"manual"] = 1

        if os.path.exists(os.path.join(patient_path, "auto")):
            for fname in os.listdir(os.path.join(patient_path, "auto")):
                index = int(fname.split('_')[0])
                info.loc[index, patient_name+"auto"] = 1

    info.to_excel(r"D:\脚本\DCMProcessor\dataset\OrganID_statistic.xlsx")


def analyse_overlap(folder_patient):
    info: pd.DataFrame = pd.read_excel(io=r"D:\脚本\DCMProcessor\dataset\OrganID.xlsx", index_col="OrganID")
    info.drop("DeepViewer", axis=1, inplace=True)
    info.drop("Manual", axis=1, inplace=True)
    info["Manual_Volume"] = None
    info["Manual_Percent"] = None
    info["Auto_Volume"] = None
    info["Auto_Percent"] = None

    patient_name = folder_patient.split('\\')[-1]

    folder_manual = os.path.join(folder_patient, "manual")
    folder_auto = os.path.join(folder_patient, "auto")

    IDs_manual = [int(fname.split('_')[0]) for fname in os.listdir(folder_manual)]
    fpaths_manual = [os.path.join(folder_manual, fname) for fname in os.listdir(folder_manual)]
    IDs_auto = [int(fname.split('_')[0]) for fname in os.listdir(folder_auto)]
    fpaths_auto = [os.path.join(folder_auto, fname) for fname in os.listdir(folder_auto)]

    pbar = tqdm([row[0] for row in info.iterrows()])
    for ID in pbar:
        if ID in IDs_manual:
            if ID in IDs_auto:
                fpath_manual = fpaths_manual[IDs_manual.index(ID)]
                manual = sitk.GetArrayFromImage(sitk.ReadImage(fpath_manual)).astype(bool)
                n_manual = np.sum(manual)
                info.loc[ID, "Manual_Volume"] = n_manual

                fpath_auto = fpaths_auto[IDs_auto.index(ID)]
                auto = sitk.GetArrayFromImage(sitk.ReadImage(fpath_auto)).astype(bool)
                n_auto = np.sum(auto)
                info.loc[ID, "Auto_Volume"] = n_auto

                overlap = np.sum(auto * manual)

                info.loc[ID, "Manual_Percent"] = (1 - overlap/n_manual).round(decimals=4)
                info.loc[ID, "Auto_Percent"] = (1 - overlap/n_auto).round(decimals=4)
            else:
                fpath_manual = fpaths_manual[IDs_manual.index(ID)]
                manual = sitk.GetArrayFromImage(sitk.ReadImage(fpath_manual)).astype(bool)
                info.loc[ID, "Manual_Volume"] = np.sum(manual)
                info.loc[ID, "Manual_Percent"] = 0
        else:
            if ID in IDs_auto:
                fpath_auto = fpaths_auto[IDs_auto.index(ID)]
                auto = sitk.GetArrayFromImage(sitk.ReadImage(fpath_auto)).astype(bool)
                info.loc[ID, "Auto_Volume"] = np.sum(auto)
                info.loc[ID, "Auto_Percent"] = 0
            else:
                pass
        info.to_excel(os.path.join(folder_patient, "info.xlsx"))


def auto_analyse_apply(fpath, threshold=0.3):
    info = pd.read_excel(fpath, index_col="OrganID")
    for ID in [row[0] for row in info.iterrows()]:
        if (info.loc[ID, "Manual_Percent"] is None) and (info.loc[ID, "Auto_Percent"] is None):
            info.loc[ID, "Apply"] = "None"
        elif (info.loc[ID, "Manual_Percent"] is not None) and (info.loc[ID, "Auto_Percent"] is None):
            info.loc[ID, "Apply"] = "manual"
        elif (info.loc[ID, "Manual_Percent"] is None) and (info.loc[ID, "Auto_Percent"] is not None):
            info.loc[ID, "Apply"] = "auto"
        else:
            if (info.loc[ID, "Manual_Percent"] > threshold) or (info.loc[ID, "Auto_Percent"] > threshold):
                info.loc[ID, "Apply"] = "manual"

    info.to_excel(os.path.join(os.path.dirname(fpath), "info_apply.xlsx"))


def loop_apply(folder_base=r"F:\need to sort\processed"):
    for folder_patient in os.listdir(folder_base):
        folder_patient = os.path.join(folder_base, folder_patient)
        fpath = os.path.join(folder_patient, "info.xlsx")

        auto_analyse_apply(fpath)


if __name__ == "__main__":
    #　organs_in_dataset()
    auto_analyse_apply(r"F:\need to sort\processed\AnonyP2S1_PETCT08695\info.xlsx")
