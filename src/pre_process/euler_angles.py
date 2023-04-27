
def write_euler_angles(file_dir,euler_angles_list):
    """
    Write the euler angles to the text file
    :param file_dir: directory to the text file to output euler angle
    :param phi1_list: list of euler angles of the grains
    :param Phi_list: list of euler angles of the grains
    :param phi2_list: list of euler angles of the grains
    :return:
    """
    write_io = open(file_dir,'w+')
    for i in range(len(euler_angles_list)):
        write_io.write(f'{euler_angles_list[i][0]},{euler_angles_list[i][1]},{euler_angles_list[i][2]}\n')
    write_io.close()