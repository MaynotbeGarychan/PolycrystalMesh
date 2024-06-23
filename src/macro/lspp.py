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

    def save_part_hsv(self,kfile_dir,hsv_id,part_id,d3plot_dir,save_csv_dir):
        kfile_folder_dir = path.dirname(kfile_dir)
        src_cfile_dir = f'{self.cfile_folder_dir}//save_part_hsv.cfile'
        dst_cfile_dir = f'{kfile_folder_dir}//save_part_hsv.cfile'
        couple_list = [['$d3plot_dir$', f'{d3plot_dir}'],
                       ['$part_id$', f'{part_id}'],
                       ['$hsv_id$', f'{hsv_id+1000}'],
                       ['$save_csv_dir$', f'{save_csv_dir}']]
        self._make_cfile(src_cfile_dir, dst_cfile_dir, couple_list)
        self._run(dst_cfile_dir)

    def save_part_list_hsv(self,kfile_dir,hsv_id,part_id_list,d3plot_dir,save_csv_folder_dir):
        kfile_folder_dir = path.dirname(kfile_dir)
        cfile_dir = f'{kfile_folder_dir}//save_part_list_hsv.cfile'
        lines = []
        lines.append(f'open d3plot "{d3plot_dir}"\n')
        lines.append('ac\n')
        lines.append('genselect target element\n')
        for part_id in part_id_list:
            lines.append(f'genselect element add part {part_id}/0 \n')
            lines.append(f'etime {1000+hsv_id} \n')
            save_csv_dir = path.join(save_csv_folder_dir,f'hsv{hsv_id}_{part_id}.csv')
            lines.append(f'xyplot 1 savefile ms_csv_multiple "{save_csv_dir}" 1 all\n')
            lines.append(f'genselect element remove part {part_id}/0 \n')
        lines.append('switch2pick\n')
        lines.append('exit')
        write_io = open(cfile_dir,'w')
        write_io.writelines(lines)
        write_io.close()
        self._run(cfile_dir)

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




