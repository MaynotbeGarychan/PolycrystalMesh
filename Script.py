import os.path
from src.pre_process.mesh import mesh
from src.post_process.dyna_csv_file import *
from src.pre_process.keyword_file import keyword_file
from src.crystal_plasticity.ebsd import ebsd
from src.others.plot_tools import visualization
from src.crystal_plasticity.ebsd_to_mesh_partitioning import ebsd_to_mesh_partitioning
from src.crystal_plasticity.ebsd_to_mesh_indexing import ebsd_to_mesh_indexing
from src.pre_process.keyword_format import write_parts_with_materials_models, write_header, write_parts,write_section_solid, write_nodes_set
import numpy as np
from src.pre_process.euler_angles import write_euler_angles


# specify the directory
# input_mesh_file_dir = '/home/chen/Desktop/PolycrystalMesh/example/retangle_region/shell_mesh.k'
# input_ebsd_file_dir = '/home/chen/Desktop/PolycrystalMesh/example/retangle_region/input.txt'
# output_mesh_dir = '/home/chen/Desktop/PolycrystalMesh/example/retangle_region/output_solid.k'
# euler_angle_file_dir = '/home/chen/Desktop/PolycrystalMesh/example/retangle_region/euler_angles.txt'

input_mesh_file_dir = '/home/chen/Desktop/kishimoto/gmsh_shell.k'
input_ebsd_file_dir = '/home/chen/Desktop/kishimoto/input.txt'
output_mesh_dir = '/home/chen/Desktop/kishimoto/output_solid.k'
euler_angle_file_dir = '/home/chen/Desktop/kishimoto/euler_angles.txt'

# input shell mesh and ebsd data
shell_mesh = mesh(input_mesh_file_dir)
specimen_ebsd = ebsd(input_ebsd_file_dir)

# adjust the region of mesh and ebsd data, to make them overlaying with each other
specimen_ebsd.points_set.adjust_points_region_with_specimen(shell_mesh.node_set)
specimen_ebsd.points_set.scale_points_coordinates(0.9999)
specimen_ebsd.points_set.adjust_points_region_into_specimen_positions(shell_mesh.node_set)
specimen_ebsd.points_set.scale_points_coordinates(1.03,'x')
specimen_ebsd.points_set.scale_points_coordinates(1.05,'y')
specimen_ebsd.points_set.translate_points_coodinates(-0.03,'x')
specimen_ebsd.points_set.translate_points_coodinates(-0.03,'y')

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
map_elem_id_array = ebsd_to_mesh_indexing(specimen_ebsd,shell_mesh, (30,2))

# write it to media file for debug
# media_file_dir = '/home/chen/Desktop/PolycrystalMesh/example/retangle_region/media.txt'
# media_io = open(media_file_dir,'w')
# for i in range(len(map_elem_id_array)):
#     point_id = i + 1
#     elem_id = map_elem_id_array[i]
#     media_io.write(f'{elem_id}\n')
# media_io.close()

# read it from media file
# media_io = open(media_file,'r')
# media_lines = media_io.readlines()
# for i in range(len(media_lines)):
#     line = media_lines[i]
#     info = line.replace('\n','')
#     map_elem_id_array[i] = info


# Partitioning the element based on the points inside the domain
new_part_id_array = ebsd_to_mesh_partitioning(map_elem_id_array,specimen_ebsd,shell_mesh)
shell_mesh.elem_set.part_list = new_part_id_array

# Drag the shell mesh to solid mesh
solid_mesh = shell_mesh.drag_shell_to_solid(20, 0.025)

# Output the model to LS-Dyna k file, also output the euler angle
output_mesh_io = keyword_file(output_mesh_dir, 'w').file_io
write_header(output_mesh_io)
solid_mesh.write_keyword(output_mesh_io)
output_mesh_io.close()

# Output the euler angle
write_euler_angles(euler_angle_file_dir,specimen_ebsd.grains_set.orientations_list)



