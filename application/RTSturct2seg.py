

from utlis.RTStructProcess import RTStructExtractor

import os


def walk_all_folder(base_folder):
    wrong_folders: list = list()
    for f1 in os.listdir(base_folder):
        f1 = os.path.join(base_folder, f1)

        for f2 in os.listdir(f1):
            f2 = os.path.join(f1, f2)

            for f3 in os.listdir(f2):
                f3 = os.path.join(f2, f3)

                print("Current Folder: ", f3)

                e = RTStructExtractor(f3)
                isGenerated = e.Execute(os.path.join(f3, "seg.nii"))
                if isGenerated:
                    print("Missing file.")
                    wrong_folders.append(isGenerated)

    for folder in wrong_folders:
        print(folder)


def seg_check(base_folder, fpath):
    pass


if __name__ == "__main__":
    walk_all_folder(r"F:\Patients-CT_PET")
