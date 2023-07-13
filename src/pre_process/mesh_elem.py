from src.pre_process.keyword_file import keyword_file, ret_form_lines
from src.pre_process.keyword_format import write_line_with_vars_rjust
import numpy as np

class elem_set(object):
    type = ''
    num = 0
    id_array = np.empty(0)
    nodes_list = np.empty(0)
    part_list = np.empty(0)

    def __init__(self, input_file_dir: str):
        if input_file_dir.endswith('.k'):
            # print("INFO: Reading element information from keyword file")
            self._input_from_keyword(input_file_dir)
        else:
            self.type = ''
            self.num = 0
            self.id_array = np.empty(0)
            self.nodes_list = np.empty(0)
            self.part_list = np.empty(0)
            # print("INFO: Creating empty element set")

    # Input functions
    def _input_from_keyword(self, input_file_dir):
        """
        Init the element set by reading the keyword file
        :param input_file_dir: directory of input keyword file
        :return:
        """
        # get the lines related to elements from keyword
        keyword = keyword_file(input_file_dir,'r')
        lines = keyword.read_lines()
        lines = ret_form_lines(lines,"*ELEMENT_")[0]  # now we just use one set of element
        # detect element type, begin to parse the lines
        if lines[0].startswith("*ELEMENT_SHELL"):
            self.type = "ELEMENT_SHELL"
            self._init_elem_set(lines[1:], self.type)
        if lines[0].startswith("*ELEMENT_SOLID"):
            self.type = "ELEMENT_SOLID"
            self._init_elem_set(lines[1:], self.type)

    # Output functions
    def write_keyword(self, write_io):
        """
        Io to Output the elem set keyword to the given directory
        :param write_io: io to keywore file
        :return:
        """
        # write header and comments
        write_io.write(f'*KEYWORD  \n')
        write_io.write(f'*{self.type}  \n')
        write_io.write(f'$#   eid     pid      n1      n2      n3      n4      n5      n6      n7      n8  \n')
        # write information
        elem_line = np.empty(10, dtype=int)
        for i in range(self.num):
            elem_line.fill(0)
            elem_line[0] = self.id_array[i]
            elem_line[1] = self.part_list[i]
            elem_line[2:2+len(self.nodes_list[i])] = self.nodes_list[i]
            write_line_with_vars_rjust(elem_line,write_io,8)

    def _init_elem_set(self, lines, elem_type):
        """
        Init the element set by the keyword lines
        :return:
        """
        # get the number of element
        self.num = len(lines)
        # init the size of id_array, nodes_list, etc.
        self.id_array = np.empty(self.num,dtype=int)
        self.part_list = np.empty(self.num,dtype=int)

        num_node = 0
        if elem_type == "ELEMENT_SHELL":
            num_node = 4
        elif elem_type == "ELEMENT_SOLID":
            num_node = 8
        self.nodes_list = np.empty((self.num,num_node),dtype=int)
        # get the id_array, nodes_list, etc., from lines
        for i in range(self.num):
            line = lines[i]
            info = line.split()
            self.id_array[i], self.part_list[i] = info[0], info[1]
            self.nodes_list[i] = info[2:2+num_node]

    def search_ajacent_elem(self,elem_id):
        """
        Serch the adjacent element by using node lists of a specific element
        :param elem_id: id of an element
        :return: np.array, the array with the adjacent element id
        """
        idx = elem_id - 1
        nodes_list = self.nodes_list[idx]
        elem_id_array = np.empty(0,dtype=int)
        for i in range(len(nodes_list)):
            node_id = nodes_list[i]
            temp = self.search_elem_by_node(node_id)
            elem_id_array = np.concatenate((elem_id_array,temp))
        unique_elem_id_array = np.unique(elem_id_array)
        unique_elem_id_array = unique_elem_id_array[unique_elem_id_array != elem_id]

        thres = 2
        if self.type == "ELEMENT_SHELL":
            thres = 1
        elif self.type == "ELEMENT_SOLID":
            thres = 2
        ajacent_elem_id_array = []
        for i in range(len(unique_elem_id_array)):
            cur_elem_id = unique_elem_id_array[i]
            if np.count_nonzero(elem_id_array == cur_elem_id) > thres:
                ajacent_elem_id_array.append(cur_elem_id)
        return np.array(ajacent_elem_id_array)

    def search_elem_by_node(self,node_id):
        """
        Search the elements which has such node
        :param node_id: id of a specific node
        :return: the array of the elements which have this node
        """
        idx = np.where(self.nodes_list == node_id)[0]
        return self.id_array[idx]
