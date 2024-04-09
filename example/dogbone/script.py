import os.path

import matplotlib.pyplot as plt

from src.pre_process.mesh import mesh
from src.post_process.dyna_csv_file import *
from src.pre_process.keyword_file import keyword_file
from src.crystal_plasticity.ebsd import ebsd
from src.others.plot_tools import visualization
from src.crystal_plasticity.ebsd_to_mesh_partitioning import ebsd_to_mesh_partitioning
from src.crystal_plasticity.ebsd_to_mesh_indexing import ebsd_to_mesh_indexing
import numpy as np
from src.pre_process.euler_angles import write_euler_angles
from src.pre_process.keyword_format import write_any_keyword
from math import radians


def make(input_mesh_file_dir,input_ebsd_file_dir,output_shell_mesh_dir,output_solid_mesh_dir,euler_angle_file_dir):
    # input shell mesh and ebsd data
    shell_mesh = mesh(input_mesh_file_dir)
    specimen_ebsd = ebsd(input_ebsd_file_dir)

    # adjust the region of mesh and ebsd data, to make them overlaying with each other
    #shell_mesh.node_set.rotate_node_set(90)
    #specimen_ebsd.points_set.rotate_poinst_region(90)
    specimen_ebsd.points_set.scale_points_coordinates(0.05)
    specimen_ebsd.points_set.scale_points_coordinates(0.9999)
    specimen_ebsd.points_set.adjust_points_region_into_specimen_positions(shell_mesh.node_set)
    shell_mesh.node_set.rotate_node_set(rot_degrees=45)
    #specimen_ebsd.points_set.scale_points_coordinates(1.03,'x')
    #specimen_ebsd.points_set.scale_points_coordinates(1.05,'y')
    #specimen_ebsd.points_set.translate_points_coodinates(-0.03,'x')
    #specimen_ebsd.points_set.translate_points_coodinates(-0.03,'y')

    # visualize the region of shell mesh and ebsd to check whether they are overlaying
    visual = visualization()

    visual.add_scatter_points(specimen_ebsd.points_set.x_array,
                              specimen_ebsd.points_set.y_array,
                              color=specimen_ebsd.points_set.phi1_array)

    visual.add_scatter_points(shell_mesh.node_set.x_array,shell_mesh.node_set.y_array)

    visual.adjust_equal_axes()
    visual.add_legend()
    visual.show_fig()

    # Check which point in which element region domain
    map_elem_id_array = np.zeros(specimen_ebsd.points_set.num_points, dtype=int)
    map_elem_id_array = ebsd_to_mesh_indexing(specimen_ebsd,shell_mesh, (20,20))

    # Partitioning the element based on the points inside the domain
    new_part_id_array = ebsd_to_mesh_partitioning(map_elem_id_array,specimen_ebsd,shell_mesh)
    shell_mesh.elem_set.part_list = new_part_id_array

    # output shell mesh
    output_mesh_io = keyword_file(output_shell_mesh_dir, 'w').file_io

    shell_mesh.write_keyword(output_mesh_io)
    output_mesh_io.close()

    # Drag the shell mesh to solid mesh
    solid_mesh = shell_mesh.drag_shell_to_solid(10, 0.02)

    # Output the model to LS-Dyna k file, also output the euler angle
    output_mesh_io = keyword_file(output_solid_mesh_dir, 'w').file_io

    solid_mesh.write_keyword(output_mesh_io)
    output_mesh_io.close()

    # Output the euler angle
    write_euler_angles(euler_angle_file_dir,specimen_ebsd.grains_set.phi1_list,
                       specimen_ebsd.grains_set.lphi_list, specimen_ebsd.grains_set.phi2_list)


if __name__ == "__main__":
    input_mesh_file_dir = 'shell_mesh.k'
    input_ebsd_file_dir = f'input.txt'
    output_shell_mesh_dir = f'output_shell.k'
    output_solid_mesh_dir = f'output_solid.k'
    euler_angle_file_dir = f'euler_angles.txt'

    make(input_mesh_file_dir, input_ebsd_file_dir, output_shell_mesh_dir, output_solid_mesh_dir, euler_angle_file_dir)