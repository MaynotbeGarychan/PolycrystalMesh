import numpy as np
from src.pre_process.keyword_file import keyword_file, ret_form_lines
from copy import copy, deepcopy

class node_set(object):
    num = 0
    id_array = np.empty(0)
    x_array = np.empty(0)
    y_array = np.empty(0)
    z_array = np.empty(0)
    #coordinates_list = np.array(0)

    def __init__(self, input_file_dir: str):
        if input_file_dir.endswith('.k'):
            # print("INFO: Reading node information from keyword file")
            self._input_from_keyword(input_file_dir)
        else:
            self.num = 0
            self.id_array = np.empty(0)
            self.x_array = np.empty(0)
            self.y_array = np.empty(0)
            self.z_array = np.empty(0)
            # print("INFO: Creating empty node set")

    # input functions
    def _input_from_keyword(self, input_file_dir):
        """
        Init the node set from keyword
        :param input_file_dir: directory of input keyword file
        :return:
        """
        # get the lines related to node from keyword
        keyword = keyword_file(input_file_dir, 'r')
        lines = keyword.read_lines()
        lines = ret_form_lines(lines,"*NODE")[0]  # now we just use one set of node
        lines = lines[1:] # neglect the first line *NODE
        # init the size of id_array, coordinates_list, etc.
        self.num = len(lines)
        self.id_array = np.empty(self.num, dtype=int)
        self.x_array = np.empty(self.num, dtype=float)
        self.y_array = np.empty(self.num, dtype=float)
        self.z_array = np.empty(self.num, dtype=float)
        # get the id_array, coordinates_list
        for i in range(self.num):
            line = lines[i]
            info = line.split()
            self.id_array[i] = info[0]
            self.x_array[i] = info[1]
            self.y_array[i] = info[2]
            self.z_array[i] = info[3]


    # Output functions
    def write_keyword(self, write_io):
        """
        Io to Output the node set keyword to the given directory
        :param write_io: io to keywore file
        :return:
        """
        write_io.write(f'*NODE\n')
        write_io.write(f'$#   nid               x               y               z      tc      rc\n')
        for i in range(self.num):
            write_io.write(f'{self.id_array[i]}'.rjust(8))
            write_io.write(f'{self.x_array[i]}'.rjust(16))
            write_io.write(f'{self.y_array[i]}'.rjust(16))
            write_io.write(f'{self.z_array[i]}'.rjust(16))
            write_io.write(f'0'.rjust(8))
            write_io.write(f'0'.rjust(8))
            write_io.write('\n')

    def offset_node_set(self,distance: float, coor_str: str):
        """
        Offset the node set to a direction with a distance
        :param distance: the distance for offset
        :param coor_str: the axis/direction for offset
        :return: NO
        """
        if coor_str == 'x':
            self.x_array = self.x_array + distance
        elif coor_str == 'y':
            self.y_array = self.y_array + distance
        elif coor_str == 'z':
            self.z_array = self.z_array + distance









