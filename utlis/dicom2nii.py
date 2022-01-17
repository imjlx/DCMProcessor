import SimpleITK as sitk


reader = sitk.ImageSeriesReader()
dicom_names = reader.GetGDCMSeriesFileNames("D://Aro//ZS_Aorta//ZS11317273_ZS0003145526//WholeBody CTA//Segmented axial")
reader.SetFileNames(dicom_names)

imageCTA = reader.Execute()

# Seg 的信息
size = imageCTA.GetSize()
spacing = imageCTA.GetSpacing()
Origin = imageCTA.GetOrigin()
direction = imageCTA.GetDirection()

save_pathseg = "D://Aro//ZS_Aorta//ZS11317273_ZS0003145526//WholeBody CTA//Segmented_axial.nii"


reader = sitk.ImageSeriesReader()
###

dicom_names = reader.GetGDCMSeriesFileNames("D://Aro//ZS_Aorta//ZS11317273_ZS0003145526//WholeBody CTA//CTA 1.0 CE")
reader.SetFileNames(dicom_names)

image = reader.Execute()
new = sitk.Resample(image, size, sitk.TranslationTransform(3), sitk.sitkLinear,
                                                                Origin, spacing, direction, -1024, image.GetPixelID())
save_path = "D://Aro//ZS_Aorta//ZS11317273_ZS0003145526//WholeBody CTA//CTA_1.0_CE.nii"
sitk.WriteImage(new, save_path)
imageCTA = sitk.Cast(imageCTA, image.GetPixelID())
sitk.WriteImage(imageCTA, save_pathseg)
###
