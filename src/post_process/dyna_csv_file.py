import pandas as pd

class dyna_csv_file(object):
    file_dir = None
    dataframe = pd.DataFrame() # self.data_frame['Hsvxxx']

    def __init__(self, csv_dir):
        self.file_dir = csv_dir
        self._read()

    def _read(self):
        """
        Read the output variables data from csv into dataframe
        :return:
        """
        # init csv io
        csv_io = open(self.file_dir, 'r')  # init csv io
        lines = csv_io.readlines()
        csv_io.close()
        # make name columns
        name_col = []
        raw_name_list = lines[1].split(',')
        for name in raw_name_list:
            if name.startswith('Time'):
                name_col.append('Time')
            if name.startswith('History Variable#'):
                name_col.append(name.replace('History Variable#', 'Hsv').split('-')[0])
        # make data columns
        data = []
        for line in lines[2:]:
            alist = []
            for val in line.split(',')[:-1]:
                alist.append(float(val))
            data.append(alist)
        self.dataframe = pd.DataFrame(data, columns=name_col, dtype=float)

    def add_col(self, name: str, data_list):
        """
        Add a new column to the dataframe
        :param name: name of the variables
        :param data_list: a list of the data
        :return:
        """
        self.dataframe.insert(len(self.dataframe.columns), name,
                              data_list, allow_duplicates=False)
