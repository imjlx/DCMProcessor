"""
@file    :  dcm2nii_test.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/20 18:02   JHR          1.0         
"""
import os
import SimpleITK as sitk
from utlis.DICOM import DCMFormatConverter, DCMBase
from utlis.Image import ImageResampler


def dcm2nii_directly(folder, fpath):
    img = DCMBase.ReadDCMSeries(folder)
    sitk.WriteImage(img, fpath)


def dcm2nii_flip(folder, fpath):
    c = DCMFormatConverter(folder)
    c.DCM2nii(fpath)


def resample_nii2nii(fpath, save_path):
    img = sitk.ReadImage(fpath)
    r = ImageResampler()
    img = r.ResampleToNewSpacing(img, (1,1,1))
    sitk.WriteImage(img, save_path)


def resample_dcm2nii(folder, fpath):
    img = DCMBase.ReadDCMSeries(folder)
    r = ImageResampler
    img = r.ResampleToNewSpacing(img, (1, 1, 1))
    sitk.WriteImage(img, fpath)


if __name__ == "__main__":
    folder_base = r"E:\SS-DCMProcessor\dataset\dcm2nii"
    folder_ct = r"E:\SS-DCMProcessor\dataset\dcm2nii\CT"
    folder_pet = r"E:\SS-DCMProcessor\dataset\dcm2nii\PET"

    # 直接生成nii
    # dcm2nii_directly(folder_ct, os.path.join(folder_base, "CT_directly.nii"))
    # dcm2nii_directly(folder_pet, os.path.join(folder_base, "PET_directly.nii"))

    # x、y轴翻转
    # dcm2nii_flip(folder_ct, os.path.join(folder_base, "CT_flip.nii"))
    # dcm2nii_flip(folder_pet, os.path.join(folder_base, "PET_flip.nii"))

    # 重采样
    # resample_nii2nii(os.path.join(folder_base, "CT_directly.nii"), os.path.join(folder_base, "CT_directly_1_1_1.nii"))
    # resample_nii2nii(os.path.join(folder_base, "PET_directly.nii"), os.path.join(folder_base, "PET_directly_1_1_1.nii"))
    # resample_nii2nii(os.path.join(folder_base, "CT_flip.nii"), os.path.join(folder_base, "CT_flip_1_1_1.nii"))
    # resample_nii2nii(os.path.join(folder_base, "PET_flip.nii"), os.path.join(folder_base, "PET_flip_1_1_1.nii"))

    resample_dcm2nii(folder_pet, os.path.join(folder_base, "CT_dcm_1_1_1.nii"))
    resample_dcm2nii(folder_ct, os.path.join(folder_base, "PET_dcm_1_1_1.nii"))