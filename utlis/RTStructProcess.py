"""
@file    :  RTStructProcess.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/5/12 12:10   JHR          1.0         
"""

import SimpleITK as sitk
import pydicom
import numpy as np
import pandas as pd
import os
import re
from skimage.draw import polygon as ski_polygon
from tqdm import tqdm
from typing import List

OrganID = {
    # 有重复部分
    "BODY": 10, "Spinal_Cord": 65,
    "Brain": 18, "Brain_Stem": 76, "Temporal_Lobe_R": 77, "Temporal_Lobe_L": 77,
    "Eye_L": 22, "Eye_R": 22, "Len_L": 23, "Len_R": 23,
    "Lung_All": 33, "Lung_L": 33, "Lung_R": 33,
    # 头颈部
    "Cochlea_R": 75, "Cochlea_L": 75, "Larynx": 29, "Mandible": 46, "Optic_Chiasm": 78,
    "Optical_Nerve_L": 79, "Optical_Nerve_R": 79, "Oral_Cavity": 37,
    "Parotid_L": 43, "Parotid_R": 43, "Pituitary": 42, "Thyroid_Gland": 70, "TMJ_L": 63, "TMJ_R": 63,
    # 胸部
    "Esophagus": 21, "Heart": 26, "Trachea": 73,
    # 腹部
    "Bowel": 44, "Duodenum": 82, "Kidney_L": 28, "Kidney_R": 28, "Liver": 32, "Pancreas": 38, "Stomach": 67,
    # 盆腔
    "Bladder": 15, 'Femoris_L': 46, 'Femoris_R': 46, 'Pelvis': 46, 'Rectum': 80, 'Sigmoid': 81
}


class RTStructExtractor(object):
    def __init__(self, folder):
        self.base_folder = folder
        self.ROIs: List[dict] = list()
        self.img: sitk.Image = sitk.Image()
        self.organ_ID: dict = OrganID

    def Execute(self, fpath, jump_mode=True):

        if jump_mode:   # 如果检测到seg.nii文件，则跳过
            for fname in os.listdir(self.base_folder):
                if re.match(pattern="seg.nii", string=fname):
                    # print("seg.nii exists, jumping this folder.")
                    return 0

        isRTSTRUCT = self.load_rtstruct()   # 读取RTSTRUCT分割文件
        if isinstance(isRTSTRUCT, int):     # 根据读取情况返回错误值
            return self.base_folder, 1

        isImage = self.load_image()     # 读取原始图像
        if isinstance(isImage, int):
            return self.base_folder, 2

        else:   # 成功读取，生产seg.nii文件
            try:
                self.contours2mesh()
                self.generate_seg(fpath=fpath)
            except:
                print("Error occurred in contours2mesh() or generate_seg()")
            return 0

    def load_rtstruct(self):
        """
        读取患者的RTSTRUCT文件，提取其中的原始数据到list中
        :return: ROIs
        """
        # 在总文件夹中寻找 RTSTRUCTxxx.dcm 文件
        structure = None
        for fname in os.listdir(self.base_folder):
            if re.match(pattern="RTSTRUCT[0-9]*.dcm", string=fname):
                structure = os.path.join(self.base_folder, fname)
                break
        if structure is None:  # 如果没找到分割文件，返回1
            print("No RTStruct file in ", self.base_folder)
            return 1

        structure = pydicom.dcmread(structure)  # 读取文件
        ROIs = list()  # 用ROIs保存所有ROI的信息
        # 对每个ROI进行遍历, 保存其编号、名称和数据：
        for i in range(len(structure.ROIContourSequence)):
            ROI = dict()
            ROI['number'] = structure.ROIContourSequence[i].ReferencedROINumber
            assert structure.StructureSetROISequence[i].ROINumber == \
                   structure.ROIContourSequence[i].ReferencedROINumber, "ROI number/name miss match"
            ROI['name'] = structure.StructureSetROISequence[i].ROIName
            ROI['contours'] = [contours.ContourData for contours in structure.ROIContourSequence[i].ContourSequence]
            ROIs.append(ROI)
        self.ROIs = ROIs
        return self.ROIs

    def load_image(self):
        """
        加载原始图像，其信息用于参考
        :return: 原始图像
        """
        fnames = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(self.base_folder)
        if len(fnames) == 0:    # 如果读取不到原始文件，返回1
            print("No origin image file in ", self.base_folder)
            return 1
        else:   # 有原始文件，但可能会读取失败
            try:
                reader = sitk.ImageSeriesReader()
                reader.SetFileNames(fnames)
                self.img = reader.Execute()
            except RuntimeError:
                print("Run time Error, possibly name is too long.")
                return 1

            return self.img

    def contours2mesh(self):
        """
        将边界点转换为格点，在self.ROIs的ROI中新建一个key来保存
        :return:无
        """
        bar = tqdm(self.ROIs)   # 用tqdm显示进度
        for ROI in bar:
            bar.set_description(desc="contours2mesh")
            bar.set_postfix(organ=ROI['name'])
            meshes: list = list()
            for polygon in ROI["contours"]:
                contour_points = np.array(polygon).reshape(-1, 3)
                contour_points = np.array([self.img.TransformPhysicalPointToIndex(p) for p in contour_points])
                contour_points_x = contour_points[:, 0]  # 所有边界点的x序号
                contour_points_y = contour_points[:, 1]  # 所有边界点的y序号
                contour_points_z = contour_points[:, 2]  # 所有边界点的z序号
                assert len(set(contour_points_z)) == 1, "polygon points do not in the same layer"
                z = contour_points_z[0]
                # 从边界点获取全部点坐标
                mesh_points_x, mesh_points_y = ski_polygon(contour_points_x, contour_points_y)
                mesh_points = [(x, y, z) for x, y in zip(mesh_points_x, mesh_points_y)]
                meshes.extend(mesh_points)  # 将一层的mesh点添加到全部mesh点列表中
            ROI['meshes'] = meshes
        bar.close()

    def generate_seg(self, fpath):
        """
        生成分割的seg.nii图像
        :param fpath: 保存路径
        :return:
        """
        # 创建一个原始图像大小的全零Image，作为保存分割数据的背景板
        seg = np.zeros_like(sitk.GetArrayViewFromImage(self.img))
        # 根据完整器官列表进行循环
        bar = tqdm(self.organ_ID)
        for organ in bar:
            bar.set_description(desc="filling organs")
            bar.set_postfix(organ=organ)
            # 在分割中寻找当前organ
            ROIs_index = None  # 在ROIs列表中，当前器官的index
            for ROI in self.ROIs:
                if ROI['name'] == organ:
                    ROIs_index = self.ROIs.index(ROI)
            # 根据有没有找到当前器官的分割结果：
            if ROIs_index is not None:
                points = self.ROIs[ROIs_index]['meshes']
                for point in points:
                    seg[point[2], point[1], point[0]] = self.organ_ID[organ]
        bar.close()

        seg = sitk.GetImageFromArray(seg[:, ::-1, ::-1])
        seg.CopyInformation(self.img)
        seg = sitk.Cast(seg, sitk.sitkUInt8)
        sitk.WriteImage(image=seg, fileName=fpath)
        return 0

    def analyse_overlap(self):
        """
        功能函数，分析器官之间有没有重合的点
        :return: 重合的情况
        """
        n_ROI = len(self.ROIs)
        overlap = list()
        for i in tqdm(range(n_ROI)):
            if self.ROIs[i]["name"] == "BODY":
                continue
            for j in range(i + 1, n_ROI):
                if self.ROIs[j]["name"] == "BODY":
                    continue
                p1 = set(self.ROIs[i]["meshes"])
                p2 = set(self.ROIs[j]["meshes"])
                intersection = p1 & p2
                if len(intersection) != 0:
                    overlap.append(((self.ROIs[i]["name"], len(p1)),
                                    (self.ROIs[j]["name"], len(p2)),
                                    len(intersection)))
        print(overlap)
        return overlap


if __name__ == "__main__":
    folder_path = r"F:\Patients-CT_PET\OLIVEIRA_SILVA_MORAES_ANALIA_DACIA_97374207\PET_PETCT_13_WB_CBM_SPC_(ADULT)_20190527_091112_733000\AC_CT_WB_5_0_HD_FOV_0003"
    e = RTStructExtractor(folder_path)
    e.load_rtstruct()
    e.load_image()
    e.contours2mesh()
    e.generate_seg(os.path.join(folder_path, "seg.nii"))
    pass
