

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


def copy_last_dcm_to_auto(base_folder=r"F:\Patients-CT_PET", target_path=r"D:\DeepViewer\data\pacs"):
    """
    找出没有RTSTRUCT分割文件的患者，将其dcm文件从总文件夹中复制到自动处理文件夹
    :param base_folder:
    :param target_path:
    :return:
    """
    for f1 in os.listdir(base_folder):
        f1 = os.path.join(base_folder, f1)
        for f2 in os.listdir(f1):
            f2 = os.path.join(f1, f2)
            for f3 in os.listdir(f2):
                f3 = os.path.join(f2, f3)

                if "RTSTRUCT.dcm" in os.listdir(f3):    # 如果文件夹中已经有了自动分割结果，跳过文件夹
                    break

                for fname in os.listdir(f3):    # 如果没有，将所有文件拷贝到自动分割文件夹
                    fpath = os.path.join(f3, fname)
                    shutil.copyfile(fpath, os.path.join(target_path, fname))


def copy_specific_folder_to_seg(target_path=r"D:\DeepViewer\data\pacs"):
    folders = [
        # r"F:\Patients-CT_PET\Children_LUZIA_DA_CRUZ_SARAH_97290738\PET_PETCT_13_CBM_SPC_(ADULT)_20190528_172000_696000\CT_WB_2_0_I31F_3_0004",
        # r"F:\Patients-CT_PET\DE_BRAUX_GEORGES_EDOUARD_97120286\PETR_CT_BODY_F-18_F-DOPA_20130514_113616_875000\NON_DIAG_CT_WB_0003",
        # r"F:\Patients-CT_PET\DE_DOMPIERRE_DANIEL_FRANCOIS_356081\PET_PETCT_26_WB_MELANOME_CBM_SPC_(ADULT)_20190531_093815_470000\AC_CT_WB_VISION_0002",
        # r"F:\Patients-CT_PET\DGHINE_WASSILA_97598002\PET_WB_LOC_HDCHEST_GR_(ADULT)_20170310_102719_149000\CT_WB_1_0_I31F_3_0004",
        # r"F:\Patients-CT_PET\GHITIS_ALAN_ZACCARIA_EUGENIO_263107\PET_PETCT_27_MELANOME_WB_MINF_APC_(ADULT)_20180926_135534_847000\CT_WB+MI_AC_0002",
        # r"F:\Patients-CT_PET\HASSAN_ABDIRIZAK_715933\PET_PETCT_29_WB_CHOLINE_CBM_SPC_(ADULT)_20190227_154846_554000\CT_WB_2_0_I30F_3_0003",
        # r"F:\Patients-CT_PET\JACQUET_GISELE_FERNANDE_96039417\PET_PETCT_27_WB_MELANOMES_APC_THORAX_ABDO_20190527_090040_147000\CT_WB_2_0_I31F_3_IMAR_0003",
        # r"F:\Patients-CT_PET\OLIVEIRA_SILVA_MORAES_ANALIA_DACIA_97374207\PET_PETCT_17_WB_CBM_APC_THORAX_ABDO_1ACQ__20170224_100445_078000\AC_CT_WB_5_0_HD_FOV_0002",
        # r"F:\Patients-CT_PET\PINHO_REVELES_MARILYNE_FLAVIA_469367\PET_PETCT_25_CBM_RXTH_APC_THORAX_ABDO_1AC_20170706_153621_242000\CT_WB_NATIF_2MM_0003",
        # r"F:\Patients-CT_PET\VARELA_RUIZ_JUAN_MANUEL_872571\PET_PETCT_25_CBM_RXTH_APC_THORAX_ABDO_1AC_20190708_130124_490000\CT_WB_AC_0002",
        # r"F:\Patients-CT_PET\VEROLET_QUENTIN_CHARLES_360772\PET_WB_AC_HDCHEST_(ADULT)_20170307_092744_656000\CT_WB_1_0_I31F_3_0004",
        r"F:\Patients-CT_PET\ZAKARIA_LAKO_LADO_FLORIAN_RICHARD_556470\PET_PETCT_17_WB_CBM_APC_THORAX_ABDO_1ACQ__20160714_085518_676000\CT_WB_2_0_I30F_3_0004"
    ]
    for folder in folders:
        for fname in os.listdir(folder):  # 如果没有，将所有文件拷贝到自动分割文件夹
            fpath = os.path.join(folder, fname)
            shutil.copyfile(fpath, os.path.join(target_path, fname))


if __name__ == "__main__":
    walk_all_folder(r"F:\Patients-CT_PET")
    # seg_check(base_folder=r"F:\Patients-CT_PET", info_fpath=r"D:\脚本\DCMProcessor\dataset\info_Patient_petct.xlsx")
    # copy_last_dcm_to_auto()
    # copy_specific_folder_to_seg()
    pass

