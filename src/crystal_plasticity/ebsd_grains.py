import numpy as np
from src.others.text_tools import ret_form_lines

class ebsd_grains(object):
    num_grains = 0
    id_array = 0
    orientation_list = np.empty(0)
    phi1_list = np.empty(0)
    lphi_list = np.empty(0)
    phi2_list = np.empty(0)

    def __init__(self, input_file_dir:str):
        if input_file_dir.endswith(".txt"):
            # print("INFO: Reading ebsd grains information from self defined file")
            self._input_from_self_defined_text(input_file_dir)
        else:
            self.num_grains = 0
            self.id_array = 0
            self.phi1_list = np.empty(0)
            self.lphi_list = np.empty(0)
            self.phi2_list = np.empty(0)
            # print("INFO: Creating empty ebsd grains set")

    # input functions
    def _input_from_self_defined_text(self,input_file_dir):
        """
        Initialize ebsd_grains set from self defined text file
        :param input_file_dir:
        :return:
        """
        # get the information lines from text
        lines = ret_form_lines(input_file_dir, "*EBSD_GRAIN")[0][1:]
        # initialize empty array
        self.num_grains = len(lines)
        self.id_array = np.empty(self.num_grains, dtype=int)
        self.phi1_list = np.empty(self.num_grains, dtype=float)
        self.lphi_list = np.empty(self.num_grains, dtype=float)
        self.phi2_list = np.empty(self.num_grains, dtype=float)
        # give the information into the container
        for i in range(len(lines)):
            info = lines[i].replace("\n", '').split(",")
            self.id_array[i] = info[0]
            self.phi1_list[i] = info[1]
            self.lphi_list[i] = info[2]
            self.phi2_list[i] = info[3]