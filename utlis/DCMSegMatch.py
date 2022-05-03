"""
@file    :  DCMSegMatch.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  


@Modify Time      @Author      @Version     
------------      -------      --------     
2022/5/3 13:14   JHR          1.0         
"""

import SimpleITK as sitk
import os
import pandas as pd


class DCMSegMatcher(object):
    def __init__(self):
        pass

    def find_folders(self, folder_path, info_path):
        """
        总文件夹下三层子文件夹
        :param folder_path:
        :param info_path:
        :return:
        """
        folders = list()

        for f1 in os.listdir(folder_path):
            f1_full = os.path.join(folder_path, f1)
            for f2 in os.listdir(f1_full):
                f2_full = os.path.join(f1_full, f2)
                for f3 in os.listdir(f2_full):
                    f3_full = os.path.join(f2_full, f3)
                    folders.append(f3_full)

        info = pd.DataFrame(data={'index': range(1, len(folders)+1), 'folder': folders})
        info.to_excel(info_path, index=False)

    def extract_info(self, info_path):
        info = pd.read_excel(info_path, index_col='index')
        for i, folder in enumerate(info.loc[:, 'folder']):
            series_id = sitk.ImageSeriesReader.GetGDCMSeriesIDs(folder)
            info.loc[i+1, 'Series_ID'] = series_id[0]
        info.to_excel(info_path)

if __name__ == "__main__":
    m = DCMSegMatcher()
    # m.find_folders(folder_path=r'E:\other program\DCMProcessor\dataset\1', info_path=r'E:\other program\DCMProcessor\dataset\info.xlsx')
    m.extract_info(r'E:\other program\DCMProcessor\dataset\info.xlsx')
