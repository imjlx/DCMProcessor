
import SimpleITK as sitk
import os

from utlis.DCMGenerate import DCMGenerator


def generate_all_series(base_folder=r"D:\pinjie", r=None):
    if r is None:
        r = (0, len(os.listdir(base_folder)) - 1)

    for i, fname in enumerate(os.listdir(base_folder)):
        if r[0] <= i <= r[1]:
            fpath = os.path.join(base_folder, fname)
            dcm_folder = "D:\\pinjie_dcm\\" + fname[:-4]
            print(fname[:-4])
            g = DCMGenerator(fpath)
            g.Execute(out_dir=dcm_folder, PatientName=fname[:-4], PatientID=fname[:-4], inv_z=True)


if __name__ == "__main__":
    generate_all_series(r=(0, 5))