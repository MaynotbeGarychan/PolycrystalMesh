from src.pre_process.keyword_file import keyword_file
from src.pre_process.keyword_format import write_any_keyword
from src.pre_process.euler_angles import read_euler_angles
from random import randint

euler_angle_file = r'C:\Users\Flab\Desktop\oya\euler_angles.txt'
phi1_list, Phi_list, phi2_list = read_euler_angles(euler_angle_file)

part_num = len(phi1_list)
part_mat_file_dir =  r'C:\Users\Flab\Desktop\oya\part_mat.k'
write_io = keyword_file(part_mat_file_dir,'w').file_io
for i in range(part_num):
    id = i+1
    param_form = [[id, 1, id, 0, 0, 0, 0, 0]]
    write_any_keyword(write_io,"*PART",f"part_{id}",param_form)
    phi1 = round(float(phi1_list[i]),3)
    Phi = round(float(Phi_list[i]), 3)
    phi2 = round(float(phi2_list[i]), 3)
    param_form = [[id, 0.027, 43, 24, 300, 0, 3, 4],
                  [0, 0, 0, 1, 0, 0],
                  [69000.0, 0.3, 58333.33, 26000.00, 0.001, 51, 0.02, 180],
                  [68, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [phi1, Phi, phi2, 0, 0.0, 0.0, 0.0, 0.0]]
    write_any_keyword(write_io, "*MAT_USER_DEFINED_MATERIAL_MODELS_TITLE",f"mat_{id}", param_form)

write_io.close()