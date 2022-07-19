
import SimpleITK as sitk
import os
import filetype
import numpy as np

from utlis.Image import Image
import pandas as pd

def test_dtype():
    folder_dcm = r"F:\need to sort\seg_Auto\AnonyP1S2_PETCT13098\PET_01_PETCT_WHOLEBODY_(ADULT)_20200406_125141_249000\CT_WB_3_0_B30F_0004"
    fpath_pet = r"F:\need to sort\processed\AnonyP1S2_PETCT13098\resample_1_1_1\PET.nii"
    fpath_ct  = r"F:\need to sort\processed\AnonyP1S2_PETCT13098\resample_1_1_1\CT.nii"

    # reader = sitk.ImageSeriesReader()
    # fnames = reader.GetGDCMSeriesFileNames(folder_dcm)
    # reader.SetFileNames(fnames)
    # dcm = reader.Execute()
    # Image.PrintBasicInfo(dcm)
    print()
    Image.PrintBasicInfo(sitk.ReadImage(fpath_pet))
    print()
    Image.PrintBasicInfo(sitk.ReadImage(fpath_ct))



if __name__ == "__main__":

    test_dtype()