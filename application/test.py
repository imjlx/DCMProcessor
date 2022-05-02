
import SimpleITK as sitk
import os

from utlis.DCMGenerate import DCMGenerator


def generate_one_series(read_dir, save_dir, patient_name, patient_ID):
    g = DCMGenerator(read_dir)
    g.Execute(out_dir=save_dir, PatientName=patient_name, PatientID=patient_ID,
              inv_x=False, inv_y=True, inv_z=False)


if __name__ == "__main__":
    generate_one_series(read_dir="D:\\test\\amide_out.nii",
                        save_dir="D:\\test\\script_out",
                        patient_name="test", patient_ID="testID")