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


def write_any_keyword(write_io,keyword_header:str,name:str,param_form:list):
    """
    Write keword like the LS-DYNA style
    :param write_io: keyword io
    :param keyword_header: keyword type, e.x. *PART
    :param name: name of this set of keyword
    :param param_form: a form of to store the keyword in sequences
    :return:
    """
    # write_io = open(write_dir,'w')
    write_io.write(keyword_header)
    write_io.write('\n')
    write_io.write(name)
    write_io.write('\n')
    for i in range(len(param_form)):
        param_list = param_form[i]
        write_line_with_vars_rjust(param_list, write_io, 10)
    # write_io.close()

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