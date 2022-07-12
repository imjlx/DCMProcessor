

from utlis.RTStructProcess import RTStructExtractor

import os
import re
import shutil
import pandas as pd


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


def seg_check(base_folder, info_fpath):

    # 读取全部文件夹的信息
    fpaths: list = list()
    for f1 in os.listdir(base_folder):
        f1 = os.path.join(base_folder, f1)
        for f2 in os.listdir(f1):
            f2 = os.path.join(f1, f2)
            for f3 in os.listdir(f2):
                fpaths.append(os.path.join(f2, f3))

    # 将文件夹按照结构保存到excel
    info = pd.DataFrame(data=None, columns=["f1", "f2", "f3", "RTSTRUCT", "seg"])
    for i, fpath in enumerate(fpaths):
        # 填补文件夹路径
        info.loc[i, "f1"] = fpath.split("\\")[-3]
        info.loc[i, "f2"] = fpath.split("\\")[-2]
        info.loc[i, "f3"] = fpath.split("\\")[-1]
        # 对特殊文件是否存在进行分析
        for fname in os.listdir(fpath):
            if re.match(pattern="RTSTRUCT[0-9]*.dcm", string=fname):
                info.loc[i, "RTSTRUCT"] = 1
            elif re.match(pattern="seg.nii", string=fname):
                info.loc[i, "seg"] = 1
            else:
                pass
    info.to_excel(info_fpath, index=True, index_label="index")

    for i in range(len(info)):
        if info.loc[i, "RTSTRUCT"] != 1:
            print("r\"F:\\Patients-CT_PET" + "\\" + info.loc[i, "f1"] + "\\" + info.loc[i, "f2"] + "\\" + info.loc[i, "f3"] + "\",")


def func():
    for folder_base in os.listdir(r"F:\need to sort\seg_Auto"):
        if re.match(pattern="Anony", string=folder_base):
            f0_path = os.path.join(r"F:\need to sort\seg_Auto", folder_base)
            for f1 in os.listdir(f0_path):
                f1_path = os.path.join(f0_path, f1)
                for f2 in os.listdir(f1_path):
                    if re.match("CT", f2):
                        folder_path = os.path.join(f1_path, f2)
                        e = RTStructExtractor(folder_path)
                        e.Execute(os.path.join(folder_path, "seg.nii"))


if __name__ == "__main__":
    func()
    pass

