from datetime import datetime
import numpy as np

def write_line_with_vars_rjust(var_list, write_io, rjust_len:int):
    """
    Write a line of a list of constant, which right just in each space
    :param var_list: a list of variables
    :param write_io: txt file io to output
    :param rjust_len: total length of a var to be rjust
    :return: None
    """
    for var in var_list:
        write_io.write(f"{var}".rjust(rjust_len))
    write_io.write("\n")

def write_materials_models(write_io, model_id_list: list, hsv_num_list: list ,euler_angles_list: list, g0_list: list, gs_list: list, h0_list: list, hs_list: list):
    """
    Write information of a list of materials models into keyword file
    :param write_io:            txt file io to output
    :param model_id_list:       id list of material models
    :param euler_angles_list:   list of euler angles, [[phi1,PHI,phi2],[phi1,PHI,phi2],[phi1,PHI,phi2],...]
    :param g0_list:             list of g0
    :param gs_list:             list of gs
    :param h0_list:             list of h0
    :param hs_list:             list of hs
    :return:
    """
    for i in range(len(model_id_list)):
        model_id = model_id_list[i]
        euler_angles = euler_angles_list[i]
        g0 = g0_list[i]
        gs = gs_list[i]
        h0 = h0_list[i]
        hs = hs_list[i]
        hsv_num = hsv_num_list[i]
        write_io.write("*MAT_USER_DEFINED_MATERIAL_MODELS_TITLE\n")
        write_io.write(f"umat43_{model_id}\n")
        write_io.write("$#     mid        ro        mt       lmc       nhv    iortho     ibulk        ig\n")
        write_line_with_vars_rjust([model_id, 0.027, 43, 24, hsv_num, 0, 3, 4], write_io, 10)
        write_io.write(f"$#   ivect     ifail    itherm    ihyper      ieos      lmca    unused    unused\n")
        write_line_with_vars_rjust([0, 0, 0, 1, 0, 0], write_io, 10)
        write_io.write("$#      p1        p2        p3        p4        p5        p6        p7        p8\n")
        write_line_with_vars_rjust([70000.0, 0.3, 58333.33, 26923.08, 0.001, g0, 0.02, h0], write_io, 10)
        write_io.write("$#      p1        p2        p3        p4        p5        p6        p7        p8\n")
        write_line_with_vars_rjust([gs, hs, 1.4, 0.1, 0.0, 0.0, 1.0, 0.0], write_io, 10)
        write_io.write("$#      p1        p2        p3        p4        p5        p6        p7        p8\n")
        write_line_with_vars_rjust([euler_angles[0], euler_angles[1], euler_angles[2], 0,0,0,0,0], write_io, 10)

def write_parts(write_io, part_id_list: list, section_id_list: list, materials_model_id_list: list):
    """
    Write information of a list of parts into keyword file
    :param write_io:                     txt file io to output
    :param part_id_list:                 id list of parts
    :param section_id_list:              id list of sections
    :param materials_model_id_list:      id list of materials models
    :return:
    """
    for i in range(len(part_id_list)):
        part_id = part_id_list[i]
        section_id = section_id_list[i]
        model_id = materials_model_id_list[i]
        write_io.write("*PART\n")
        write_io.write("$#                                                                         title\n")
        write_io.write(f"boxsolid_{part_id}\n")
        write_io.write("$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid\n")
        write_line_with_vars_rjust([part_id, section_id, model_id, 0, 0, 0, 0, 0], write_io, 10)


def write_parts_with_materials_models(write_io,part_id_list: list, section_id_list: list, materials_model_id_list: list, hsv_num_list: list,
                                      euler_angles_list: list, g0_list: list, gs_list: list, h0_list: list, hs_list: list):
    """
    Write the part information with materials models into keyword file
    :param write_io:                    txt file io to output
    :param part_id_list:                id list of parts
    :param section_id_list:             id list of sections
    :param materials_model_id_list:     id list of materials models
    :param euler_angles_list:           list of euler angles, [[phi1,PHI,phi2],[phi1,PHI,phi2],[phi1,PHI,phi2],...]
    :param g0_list:                     list of g0
    :param gs_list:                     list of gs
    :param h0_list:                     list of h0
    :param hs_list:                     list of hs
    :param hsv_num_list:                list of hsv num
    :return:
    """
    for i in range(len(part_id_list)):
        part_id = part_id_list[i]
        section_id = section_id_list[i]
        model_id = materials_model_id_list[i]
        euler_angles = euler_angles_list[i]
        g0 = g0_list[i]
        gs = gs_list[i]
        h0 = h0_list[i]
        hs = hs_list[i]
        hsv_num = hsv_num_list[i]
        write_io.write("*PART\n")
        write_io.write("$#                                                                         title\n")
        write_io.write(f"boxsolid_{part_id}\n")
        write_io.write("$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid\n")
        write_line_with_vars_rjust([part_id, section_id, model_id, 0, 0, 0, 0, 0], write_io, 10)
        write_io.write("*MAT_USER_DEFINED_MATERIAL_MODELS_TITLE\n")
        write_io.write(f"umat43_{model_id}\n")
        write_io.write("$#     mid        ro        mt       lmc       nhv    iortho     ibulk        ig\n")
        write_line_with_vars_rjust([model_id, 0.027, 43, 24, hsv_num, 0, 3, 4], write_io, 10)
        write_io.write(f"$#   ivect     ifail    itherm    ihyper      ieos      lmca    unused    unused\n")
        write_line_with_vars_rjust([0, 0, 0, 1, 0, 0], write_io, 10)
        write_io.write("$#      p1        p2        p3        p4        p5        p6        p7        p8\n")
        write_line_with_vars_rjust([70000.0, 0.3, 58333.33, 26923.08, 0.001, g0, 0.02, h0], write_io, 10)
        write_io.write("$#      p1        p2        p3        p4        p5        p6        p7        p8\n")
        write_line_with_vars_rjust([gs, hs, 1.4, 0.1, 0.0, 0.0, 1.0, 0.0], write_io, 10)
        write_io.write("$#      p1        p2        p3        p4        p5        p6        p7        p8\n")
        write_line_with_vars_rjust([round(euler_angles[0],4), round(euler_angles[1],4), round(euler_angles[2],4), 0, 0, 0, 0, 0], write_io, 10)

def write_section_solid(write_io, section_id:int, element_form:int):
    """

    :param write_io:        txt file io to output
    :param section_id:      id of section
    :param element_form:    index of the element form for the section, 1 for constant stress solid element
    :return:
    """
    write_io.write("*SECTION_SOLID\n")
    write_io.write("$# secid    elform       aet    unused    unused    unused    cohoff   gaskeit\n")
    write_line_with_vars_rjust([section_id,element_form,0,0,0,0.0,0.0],write_io, 10)
    if element_form == 1:
        write_io.write('*CONTROL_HOURGLASS\n')
        write_io.write('$#     ihq        qh\n')
        write_io.write('         6       0.1\n')

def write_header(write_io):
    write_io.write("$# LS-DYNA Keyword file created by Python Script \n")
    write_io.write(f"$# Author: CHEN Jiawei, MFPL, UTokyo, Time: {datetime.now()}  \n")

def write_lines(write_io, lines):
    for line in lines:
        write_io.write(line)

def write_nodes_set(write_io, set_id, name: str, id_array):
    """
    Write dyna-style node set to keyword
    :param write_io: io of keyword file
    :param name: name of the node set
    :param id_array: array of id of nodes in node set
    :return:
    """
    # create the 2d array for write lines of node set
    num_node = len(id_array)
    num_line = int(num_node/8)+1
    num_node_write = num_line * 8
    id_array_write = np.zeros(num_node_write,dtype=int)
    for i in range(num_node):
        id_array_write[i] = id_array[i]
    id_array_write = id_array_write.reshape(num_line,8)
    # begin to write line
    write_io.write('*SET_NODE_LIST_TITLE\n')
    write_io.write(f'{name}\n')
    write_io.write('$#     sid       da1       da2       da3       da4    solver       its         -\n')
    write_line_with_vars_rjust([set_id,0.0,0.0,0.0,0.0,"MECH      ","1         ","          "],write_io,8)
    for i in range(num_line):
        write_line_with_vars_rjust(id_array_write[i],write_io,8)