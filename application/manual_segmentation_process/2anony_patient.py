"""
@file    :  2anony_patient.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/7/10 14:31   JHR          1.0         
"""

from utlis import Segmentation

def convert_organs(folder_base=None):
    c = Segmentation.Dcm2niiConverter()
    c.OrganConvert(folder_series=r"E:\SS-DCMProcessor\dataset\AnonyP1S2_PETCT13098\PET_01_PETCT_WHOLEBODY_(ADULT)_20200406_125141_249000\CT_WB_3_0_B30F_0004\Body",
                   fpath_save=r"E:\SS-DCMProcessor\dataset\AnonyP1S2_PETCT13098\PET_01_PETCT_WHOLEBODY_(ADULT)_20200406_125141_249000\CT_WB_3_0_B30F_0004\all_organs\Body.nii"
                   )

if __name__ == "__main__":
    convert_organs()