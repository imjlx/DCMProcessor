

from utlis.RTStructProcess import RTStructExtractor

import os


def func(base_folder):
    for f1 in os.listdir(base_folder):
        f1 = os.path.join(base_folder, f1)

        for f2 in os.listdir(f1):
            f2 = os.path.join(f1, f2)

            for f3 in os.listdir(f2):
                f3 = os.path.join(f2, f3)

                print("Current Folder: ", f3)

                e = RTStructExtractor(f3)
                e.Execute(os.path.join(f3, "seg.nii"))


if __name__ == "__main__":
    func(r"F:\Patients-CT_PET")
