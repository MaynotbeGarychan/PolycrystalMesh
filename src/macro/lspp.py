from os import system, path
from shutil import copyfile

class lspp(object):
    lspp_dir = ''
    cfile_folder_dir = ''

    def __init__(self,lspp_dir,cfile_folder_dir):
        self.lspp_dir = lspp_dir
        self.cfile_folder_dir = cfile_folder_dir

    def _run(self,cfile_dir):
        system(f'"{self.lspp_dir}" c={cfile_dir}')

    def _make_cfile(self,src_cfile_dir,dst_cfile_dir,couple_list):
        src_cfile_io = open(src_cfile_dir, 'r')
        lines = src_cfile_io.readlines()
        src_cfile_io.close()

        new_lines = _replace(lines, couple_list)

        dst_cfile_io = open(dst_cfile_dir, 'w')
        dst_cfile_io.writelines(new_lines)
        dst_cfile_io.close()

    def get_ndforce(self,run_dir,csv_dir,node_set_id):
        src_cfile_dir = f'{self.cfile_folder_dir}//get_ndforce.cfile'
        dst_cfile_dir = f'{run_dir}//get_ndforce.cfile'
        couple_list = [['$run_dir$',f'{run_dir}'],
                       ['$node_set_id$',f'{node_set_id}'],
                       ['$csv_dir$',f'{csv_dir}']]
        self._make_cfile(src_cfile_dir, dst_cfile_dir, couple_list)
        self._run(dst_cfile_dir)

    def reorder_all(self,kfile_dir):
        kfile_folder_dir = path.dirname(kfile_dir)
        src_cfile_dir = f'{self.cfile_folder_dir}//reorder_all.cfile'
        dst_cfile_dir = f'{kfile_folder_dir}//reorder_all.cfile'
        couple_list = [['$kfile_dir$', f'{kfile_dir}']]
        self._make_cfile(src_cfile_dir,dst_cfile_dir,couple_list)
        self._run(dst_cfile_dir)


def _replace(lines,couple_list):
    new_lines = []
    for i in range(len(lines)):
        line = lines[i]
        for j in range(len(couple_list)):
            target_term = couple_list[j][0]
            replace_term = couple_list[j][1]
            line = line.replace(target_term, replace_term)
        new_lines.append(line)
    return new_lines

    #
    # for line in lines:
    #     for i in range(len(couple_list)):
    #         lines[i] = line.replace(couple_list[i][0],couple_list[i][1])




