
import SimpleITK as sitk
import os
import filetype
import numpy as np

from utlis.DCMGenerate import DCMGenerator





if __name__ == "__main__":
    a = np.array([4, 0, 3, 0])
    a_bool = a.astype(bool)

    b = np.array([0, 2, 2, 0])
    b_bool = b.astype(bool)

    c = a_bool ^ (a_bool & b_bool)
    a = a * c + b_bool * 10
    pass
