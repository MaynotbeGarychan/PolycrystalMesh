from src.crystal_plasticity.ebsd import ebsd
from src.crystal_plasticity.ebsd_points import ebsd_points
from src.pre_process.mesh import mesh
from src.pre_process.mesh_elem import elem_set
import numpy as np
from src.others.geometry_tools import typical_retangle_region, is_point_in_convex_polygon
from src.pre_process.keyword_file import keyword_file

def ebsd_to_mesh_partitioning(map_elem_id_array ,ebsd_set: ebsd, mesh_set: mesh):

    # ================================================================= #
    #           processing the map array for element belonging          #
    # ================================================================= #
    print(fr"INFO: Begin processing map array")
    points_id_array_list = [[] for _ in range(mesh_set.elem_set.num)]
    points_id_array_list = process_map_array_to_elem_belonging(map_elem_id_array, mesh_set.elem_set.num)
    print(fr"INFO: FInish processing map array")

    # ================================================================= #
    #           clasify the element, with points inside, without        #
    # ================================================================= #
    print(fr"INFO: Begin classifying element which haves points or not")
    free_elem_id_list = []
    fix_elem_id_list = []
    free_elem_id_list, fix_elem_id_list = classfied_elem_no_points(points_id_array_list)
    print(fr"INFO: Finish classifying element which haves points or not")

    # ================================================================= #
    #           partition mesh for element                              #
    # ================================================================= #
    print(fr"INFO: Begin partition mesh")
    new_part_id_array = np.zeros(mesh_set.elem_set.num, dtype=int)
    new_part_id_array = partition_mesh(points_id_array_list, fix_elem_id_list,free_elem_id_list,mesh_set,ebsd_set)
    mesh_set.elem_set.part_list = new_part_id_array
    print(fr"INFO: Finish partition mesh")

    return new_part_id_array


def partition_mesh(points_id_array_list, fix_elem_id_list, free_elem_id_list, mesh_set: mesh, ebsd_set: ebsd):
    new_part_id_array = np.zeros(mesh_set.elem_set.num, dtype=int)

    # ================================================================= #
    #           partition mesh for element  with points                 #
    # ================================================================= #
    print(fr"INFO: Begin partition mesh with points")
    new_part_id_array = partition_mesh_with_points(new_part_id_array,fix_elem_id_list,points_id_array_list,ebsd_set.points_set.part_id_array)
    print(fr"INFO: Begin partition mesh without points")

    # ================================================================= #
    #           partition mesh for element without points               #
    # ================================================================= #
    print(fr"INFO: Begin partition mesh without points")
    new_part_id_array = partition_mesh_without_points(new_part_id_array,free_elem_id_list, points_id_array_list, mesh_set.elem_set, ebsd_set.points_set.part_id_array)
    print(fr"INFO: Begin partition mesh without points")

    return new_part_id_array

def partition_mesh_with_points(new_part_id_array, fix_elem_id_list: list, points_id_array_list: list, ebsd_grain_id_array):
    for i in range(len(fix_elem_id_list)):
        elem_id = fix_elem_id_list[i]
        elem_inx = elem_id - 1
        inside_points_list = points_id_array_list[elem_inx]
        grain_id = index_element_grain_id_by_point_list(inside_points_list, ebsd_grain_id_array)
        new_part_id_array[elem_inx] = grain_id
        print(fr"INFO: Partitioning the shell mesh (with point) in progress - {i + 1}/{len(fix_elem_id_list)}")
    return new_part_id_array

def partition_mesh_without_points(new_part_id_array, free_elem_id_list: list, points_id_array_list: list, elem_set: elem_set, ebsd_grain_id_array):
    num_free_elem = len(free_elem_id_list)
    progress = 0
    while (len(free_elem_id_list) > 0):

        for elem_id in free_elem_id_list:
            ajacent_elem_array = elem_set.search_ajacent_elem(elem_id)

            # append all the points to a list
            point_list = []
            for k in range(len(ajacent_elem_array)):
                adjacent_elem_id = ajacent_elem_array[k]
                point_list.extend(points_id_array_list[adjacent_elem_id - 1])

            if len(point_list) == 0:
                continue
            else:
                points_id_array_list[elem_id - 1] = point_list
                grain_id = index_element_grain_id_by_point_list(point_list, ebsd_grain_id_array)
                new_part_id_array[elem_id - 1] = grain_id
                free_elem_id_list.remove(elem_id)
                progress += 1
                print(fr"INFO: Partitioning the shell mesh (without points) in progress - {progress}/{num_free_elem}")
    return new_part_id_array

def process_map_array_to_elem_belonging(map_elem_id_array, num_elem):
    points_id_array_list = [[] for _ in range(num_elem)]
    for i in range(len(map_elem_id_array)):
        elem_id = map_elem_id_array[i]
        point_id = i + 1
        points_id_array_list[elem_id - 1].append(point_id)
    return points_id_array_list

def classfied_elem_no_points(points_id_array_list):
    num_elem = len(points_id_array_list)
    free_elem_id_list = []
    fix_elem_id_list = []
    for i in range(num_elem):
        elem_id = i + 1
        if len(points_id_array_list[i]) == 0:
            free_elem_id_list.append(elem_id)
        else:
            fix_elem_id_list.append(elem_id)
    return free_elem_id_list, fix_elem_id_list


def index_element_grain_id_by_point_list(points_id_array, points_set_grain_id_array) -> int:
    num_points = len(points_id_array)

    belong_grain_id_array = []

    for i in range(num_points):
        points_id = points_id_array[i]
        point_idx = points_id - 1
        belong_grain_id = points_set_grain_id_array[point_idx]
        belong_grain_id_array.append(belong_grain_id)

    belong_grain_id_array = np.array(belong_grain_id_array,dtype=int)

    result_grain_id = ret_most_frequent_values(belong_grain_id_array)

    return result_grain_id

def ret_most_frequent_values(array):
    freq = np.bincount(array)
    return np.argmax(freq)