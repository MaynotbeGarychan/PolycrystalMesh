from src.crystal_plasticity.ebsd import ebsd
from src.crystal_plasticity.ebsd_points import ebsd_points
from src.pre_process.mesh import mesh
import numpy as np
from src.others.geometry_tools import typical_retangle_region, is_point_in_convex_polygon
from src.pre_process.keyword_file import keyword_file


# main function
def ebsd_to_mesh_indexing(ebsd_set: ebsd, mesh_set: mesh, divide_region_xy: tuple):
    # ================================================================= #
    #           define the subregion                                    #
    # ================================================================= #
    print("INFO: Begin ebsd_to_mesh.")
    full_region = typical_retangle_region(np.amin(mesh_set.node_set.x_array), np.amin(mesh_set.node_set.y_array),
                np.amax(mesh_set.node_set.x_array), np.amax(mesh_set.node_set.y_array))
    num_regions_x, num_region_y = divide_region_xy[0], divide_region_xy[1]
    num_region = num_regions_x * num_region_y
    sub_region_array = full_region.divide_into_sub_regions(num_regions_x,num_region_y)
    print(rf"INFO: Partition full region into {num_regions_x} * {num_region_y} sub region for speed-up.")
    del num_regions_x, num_region_y

    # ================================================================= #
    #           partitioning the region of mesh_set                     #
    # ================================================================= #
    print("INFO: Begin partitioning the region of mesh for speed-up")
    overlap_elem_id_array_list = [np.zeros(0,dtype=int)]*num_region
    overlap_elem_id_array_list = partition_mesh_by_sub_regions_definition(sub_region_array, mesh_set)
    print("INFO: Finish partitioning the region of mesh for speed-up")

    # ================================================================= #
    #           update the sub_region base on the element               #
    # ================================================================= #
    print("INFO: Begin updating the sub_region based on cut element")
    sub_region_array = update_sub_regions_based_on_elem(overlap_elem_id_array_list, mesh_set)
    print("INFO: Finish updating the sub_region based on cut element")

    # ================================================================= #
    #           partition the region of ebsd_set                        #
    # ================================================================= #
    print("INFO: Begin partitioning the region of ebsd points for speed-up")
    partition_points_id_array_list = partition_points_by_sub_regions_list(ebsd_set.points_set, sub_region_array)
    print("INFO: Finish partitioning the region of ebsd points for speed-up")

    # ================================================================= #
    #           Map the ebsd points to the elements domain              #
    # ================================================================= #
    print("INFO: Begin mapping ebsd points into element domains of mesh")
    map_point_id_elem_id = np.zeros(ebsd_set.points_set.num_points, dtype=int)
    map_point_id_elem_id = map_points_to_elem_domain(overlap_elem_id_array_list,partition_points_id_array_list,ebsd_set,mesh_set)
    return map_point_id_elem_id


def map_points_to_elem_domain(overlap_elem_id_array_list, partition_points_id_array_list, ebsd_set: ebsd, mesh_set: mesh):
    num_region = len(overlap_elem_id_array_list)
    map_point_id_elem_id = np.zeros(ebsd_set.points_set.num_points, dtype=int)
    index_progress = 0
    for i in range(num_region):
        sub_mesh_elems_id_array = overlap_elem_id_array_list[i]
        sub_ebsd_points_id_array = partition_points_id_array_list[i]
        # mapping for the first points
        for j in range(len(sub_ebsd_points_id_array)):
            point_id = sub_ebsd_points_id_array[j]
            point_x = ebsd_set.points_set.x_array[point_id - 1]
            point_y = ebsd_set.points_set.y_array[point_id - 1]

            for k in range(len(sub_mesh_elems_id_array)):
                elem_id = sub_mesh_elems_id_array[k]
                node_list = mesh_set.elem_set.nodes_list[elem_id - 1]

                polygon_x_array = []
                polygon_y_array = []

                for node_id in node_list:
                    polygon_x_array.append(mesh_set.node_set.x_array[node_id - 1])
                    polygon_y_array.append(mesh_set.node_set.y_array[node_id - 1])

                polygon_x_array = np.array(polygon_x_array, dtype=float)
                polygon_y_array = np.array(polygon_y_array, dtype=float)

                if is_point_in_convex_polygon(point_x, point_y, polygon_x_array, polygon_y_array) == True:
                    map_point_id_elem_id[point_id - 1] = elem_id
                    index_progress += 1
                    print(
                        fr"INFO: Mapping ebsd points into element domains of mesh in progress - {index_progress}/{ebsd_set.points_set.num_points}.")
                    break
    return map_point_id_elem_id

def partition_mesh_by_sub_regions_definition(sub_region_array, mesh_set: mesh):
    num_region = len(sub_region_array)
    overlap_elem_id_array_list = [np.zeros(0, dtype=int)] * num_region

    for i in range(num_region):
        sub_region = sub_region_array[i]

        overlap_elem_id_array = []
        for j in range(mesh_set.elem_set.num):
            elem_id = mesh_set.elem_set.id_array[j]

            elem_node_list = mesh_set.elem_set.nodes_list[j]
            elem_num_node = len(elem_node_list)
            elem_node_x_array = np.empty(elem_num_node)
            elem_node_y_array = np.empty(elem_num_node)
            for k in range(elem_num_node):
                node_id = elem_node_list[k]
                node_x = mesh_set.node_set.x_array[node_id - 1]
                node_y = mesh_set.node_set.y_array[node_id - 1]

                elem_node_x_array[k] = node_x
                elem_node_y_array[k] = node_y

            if sub_region.overlap_elem(elem_node_x_array, elem_node_y_array) == True:
                overlap_elem_id_array.append(elem_id)

        overlap_elem_id_array = np.array(overlap_elem_id_array)
        overlap_elem_id_array_list[i] = overlap_elem_id_array
        print(fr"INFO: Partitioning the region of mesh for speed-up in progress - {i + 1}/{num_region}")

    print("INFO: Finish partitioning the region of mesh for speed-up")
    return overlap_elem_id_array_list

def update_sub_regions_based_on_elem(overlap_elem_id_array_list: list, mesh_set: mesh):
    num_region = len(overlap_elem_id_array_list)
    sub_region_array = [None]*num_region
    for i in range(num_region):
        overlap_elem_id_array = overlap_elem_id_array_list[i]

        overlap_elem_nodes_list = mesh_set.elem_set.nodes_list[overlap_elem_id_array-1]
        overlap_elem_nodes_list = overlap_elem_nodes_list.flatten()
        overlap_elem_nodes_list = np.unique(overlap_elem_nodes_list)

        x_array = mesh_set.node_set.x_array[overlap_elem_nodes_list-1]
        y_array = mesh_set.node_set.y_array[overlap_elem_nodes_list-1]

        sub_region_array[i] = typical_retangle_region(np.amin(x_array), np.amin(y_array),
                            np.amax(x_array), np.amax(y_array))
    return sub_region_array


def partition_points_by_sub_regions_list(points_set: ebsd_points,
                                         sub_region_array):
    num_sub_region = len(sub_region_array)
    partition_points_id_array_list = [np.zeros(0,dtype=int)]*num_sub_region

    dynamic_id_array = points_set.id_array

    for i in range(num_sub_region):
        sub_region = sub_region_array[i]

        partition_points_id_array = []
        partition_points_idx_array_in_dynamic_array = []
        for j in range(len(dynamic_id_array)):
            point_id = dynamic_id_array[j]
            point_idx = point_id - 1

            x = points_set.x_array[point_idx]
            y = points_set.y_array[point_idx]

            if sub_region.in_region_and_boundary(x,y) == True:
                partition_points_id_array.append(point_id)
                partition_points_idx_array_in_dynamic_array.append(j)


        partition_points_id_array_list[i] = np.array(partition_points_id_array,dtype=int)
        dynamic_id_array = np.delete(dynamic_id_array, partition_points_idx_array_in_dynamic_array)
        print(fr"INFO: Partitioning the region of ebsd points for in progress - {i + 1}/{num_sub_region}")

    return partition_points_id_array_list