import os

class lspp(object):
    lspp_dir = ''

    def __init__(self,lspp_dir):
        self.lspp_dir = lspp_dir

    def get_ndforce(self,run_dir,csv_dir,node_set_id):
        cfile_dir = f'{run_dir}/macro.cfile'
        cfile_io = open(f"{cfile_dir}\n")

        d3plot_dir = f'{run_dir}\d3plot'
        nodfor_dir = f'{run_dir}\\nodfor'

        cfile_io.write(f"open d3plot '{d3plot_dir}'\n")
        cfile_io.write("ac\n")
        cfile_io.write(f"ascii nodfor open '{nodfor_dir}' 0\n")
        cfile_io.write(f"ascii nodfor plot {node_set_id} all\n")
        cfile_io.write(f"xyplot 1 savefile ms_csv '{csv_dir}' {node_set_id} all\n")
        cfile_io.close()

        os.system(f"{self.lspp_dir} -nographics c={cfile_dir}")
