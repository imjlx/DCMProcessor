"""
@file    :  DCMGenerate.py
@License :  (C)Copyright 2021 Haoran Jia, Fudan University. All Rights Reserved
@Contact :  21211140001@m.fudan.edu.cn
@Desc    :  生成DCM序列文件

@Modify Time      @Author      @Version     
------------      -------      --------     
2022/4/25 13:54   JHR          1.0         
"""

import SimpleITK as sitk
import time
import os


class DCMGenerator(object):
    """
    用于原始影像文件生成DCM序列
    """

    def __init__(self, fname: str):
        """
        声明生成DCM序列的工具类
        :param fname: 原始文件的路径
        """
        # 声明一个ImageFileReader
        reader = sitk.ImageFileReader()
        reader.SetFileName(fname)
        self.img: sitk.Image = reader.Execute()
        self.direction: tuple = self.img.GetDirection()

        # DCM序列相同的MetaData
        self.common_tags: dict = dict()

        # 声明一个ImageFileWriter
        self.writer = sitk.ImageFileWriter()
        self.writer.SetImageIO('GDCMImageIO')
        self.writer.KeepOriginalImageUIDOn()

    def SetCommonTags(self, **kwargs) -> dict:
        """
        设置层间相同的MetaData tags，常用tag有默认值
        :param kwargs: 输入的MetaData，部分ID可以用名称代替，规则见https://exiftool.org/TagNames/DICOM.html
        :return: MetaData的词典
        """
        # 设置默认的tag
        tags = {
            # "0008|0008": "DERIVED\\SECONDARY",  # "ImageType"
            "0008|0021": time.strftime("%Y%m%d"),  # "SeriesDate"
            "0008|0030": time.strftime("%H%M%S"),  # "StudyTime"
            "0008|0031": time.strftime("%H%M%S"),  # "SeriesTime"
            "0008|0060": "CT",  # "Modality",
            # "0008|1030": "StudyDescription",  # DeepViewer中显示
            # "0008|103e": "SeriesDescription",  # DeepViewer中显示
            "0018|0050": str(self.img.GetSpacing()[2]),    # SliceThickness
            "0018|5100": "FFS", # PatientPosition
            "0020|000d": "1.2.826.0.1.3680043.2.1125." + str(time.time()) + ".1",  # "StudyInstanceUID"
            "0020|000e": "1.2.826.0.1.3680043.2.1125." + str(time.time()) + ".2",  # "SeriesInstanceUID",
            "0020|0052": "1.2.826.0.1.3680043.2.1125." + str(time.time()) + ".3",  # "FrameOfReferenceUID"
            "0020|0037": '\\'.join(map(str, (self.direction[0], self.direction[3],
                                             self.direction[6], self.direction[1],
                                             self.direction[4], self.direction[7]))),  # "ImageOrientationPatient",

            "0010|0010": "AnonyPatient",  # "PatientName",
            "0010|0020": "AnonyID",  # "PatientID",

            # "0028|0100": "BitsAllocated",
            # "0028|0101": "BitsStored\t",
            # "0028|0102": "HighBit\t",
            # "0028|0103": "PixelRepresentation",
        }

        # 转换含义输入和ID输入
        for name, ID in zip(('PatientName', 'PatientID', 'SeriesInstanceUID', 'PatientPosition'),
                            ('0010|0010', '0010|0020', '0020|000e', '0018|5100')):
            if name in kwargs:
                kwargs[ID] = kwargs[name]
                kwargs.pop(name)
        # 根据输入修改tag
        for tag in kwargs:
            tags[tag] = kwargs[tag]

        self.common_tags = tags
        return tags

    def WriteSlice(self, out_dir: str, i: int, inv_x: bool = False, inv_y: bool = False, inv_z: bool = False) -> None:
        """
        根据读取的原始图像、MetaData标签和层序号i，生成一层的DCM序列
        :param out_dir: 保存序列文件的文件夹路径，文件名自动保存为 ”i.dcm“
        :param i: 层数，可以从0开始，到n-1
        :param inv_x: x方向是否翻转
        :param inv_y: y方向是否翻转
        :param inv_z: z方向是否翻转
        :return: None
        """
        # 设置x, y方向是否翻转
        gap_x = 1
        gap_y = 1
        if inv_x:
            gap_x = -1
        if inv_y:
            gap_y = -1
        # 从nii文件读取的整个图像中，切片出一层DCM的数据；要考虑z方向是否翻转
        if inv_z:   # z方向翻转
            img_slice: sitk.Image = sitk.Cast(self.img[::gap_x, ::gap_y, -i-1], sitk.sitkInt16)
        else:   # z方向不翻转
            img_slice: sitk.Image = sitk.Cast(self.img[::gap_x, ::gap_y, i], sitk.sitkInt16)

        # 设置层间相同的MetaData
        for tag in self.common_tags:
            img_slice.SetMetaData(tag, self.common_tags[tag])
        # 设置层间差异的MetaData
        img_slice.SetMetaData("0020|0032",  # ImagePositionPatient
                              '\\'.join(map(str, self.img.TransformIndexToPhysicalPoint((0, 0, i)))))
        img_slice.SetMetaData("0020|0013", str(i))  # InstanceNumber
        # 保存单层文件
        self.writer.SetFileName(os.path.join(out_dir, self.common_tags['0010|0010'] + "_" + str(i) + '.dcm'))
        self.writer.Execute(img_slice)

    def Execute(self, out_dir: str, inv_x: bool = False, inv_y: bool = False, inv_z: bool = False, **kwargs) -> None:
        """
        生成完整序列
        :param out_dir: 保存序列文件的文件夹路径，传给WriteSlice()
        :param inv_x: x方向是否翻转
        :param inv_y: y方向是否翻转
        :param inv_z: z方向是否翻转
        :param kwargs: 输入的MetaData，传给SetCommonTags()
        :return:
        """
        self.SetCommonTags(**kwargs)
        # 判断保存路径是否存在，不存在就创造
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for i in range(self.img.GetSize()[2]):
            self.WriteSlice(out_dir=out_dir, i=i, inv_x=inv_x, inv_y=inv_y, inv_z=inv_z)


if __name__ == "__main__":
    g = DCMGenerator(r"E:\other program\DCMProcessor\dataset\ct.nii")
    g.Execute(out_dir=r"E:\other program\DCMProcessor\dataset\ct_dcm", PatientName="test name")
    pass
