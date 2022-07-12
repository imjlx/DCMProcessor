
import SimpleITK as sitk
import os
import filetype
import numpy as np

from utlis.DCMGenerate import DCMGenerator
import pandas as pd

def func():
    info = pd.read_excel(io=r"D:\脚本\DCMProcessor\dataset\OrganID_statistic.xlsx")

    for patient_name in os.listdir(r"F:\need to sort\seg_per_organ"):
        patient_path = os.path.join(r"F:\need to sort\seg_per_organ", patient_name)





if __name__ == "__main__":
    func()
