import numpy as np
from src.pre_process.mesh import mesh
from src.pre_process.mesh_node import node_set
from copy import deepcopy
from tqdm import tqdm
from src.pre_process.keyword_format import write_lines
from src.others.id_array_tools import sort_array_together_correspond_to_first_array

class rve(object):
    # Geometry
    #
    #       ' ------ '
    #      /|       /|
    #     ' ------ ' |          z
    #     | a -----| b          | __ x
    #     |/       |/          /
    #     d ______ c          y
    #
    face_nodes_set = [[np.empty(0,dtype=int)]*2 for _ in range(3)]  # (-+x), (-+y), (-+z)
    vertex_nodes_array = [np.empty(0,dtype=int) for _ in range(8)]  # a,b,c,d,a',b',c',d'
    edge_nodes_set = [[np.empty(0,dtype=int)]*4 for _ in range(3)] # //x [[b-a],[c-d],[c'-d'],[b'-a']] //y [[d-a],[c-b],[c'-b'],[d'-a']] //z [[a-a'],[b-b'],[c-c'],[d-d']]
    face_nodes_set_inner = [[np.empty(0,dtype=int)]*2 for _ in range(3)]
    edge_nodes_array_inner = [[np.empty(0,dtype=int)]*4 for _ in range(3)]
    size = np.array([0,0,0],dtype=float)
    reorder_flag = False

    def __init__(self,mesh_set: mesh):
        """
        init function for the RVE object
        :param mesh_set:
        """
        print("INFO: Initializing the RVE information.")
        # vertex value
        vertex_value = [[min(mesh_set.node_set.x_array), max(mesh_set.node_set.x_array)],
                        [min(mesh_set.node_set.y_array), max(mesh_set.node_set.y_array)],
                        [min(mesh_set.node_set.z_array), max(mesh_set.node_set.z_array)]]
        self.size = np.array([vertex_value[0][1] - vertex_value[0][0], vertex_value[1][1] - vertex_value[1][0], vertex_value[2][1] - vertex_value[2][0]], dtype=float)
        # detect ourter faces nodes
        faces_nodes_idx_array = [[np.where(mesh_set.node_set.x_array == vertex_value[0][0])[0], np.where(mesh_set.node_set.x_array == vertex_value[0][1])[0]],
                                 [np.where(mesh_set.node_set.y_array == vertex_value[1][0])[0], np.where(mesh_set.node_set.y_array == vertex_value[1][1])[0]],
                                 [np.where(mesh_set.node_set.z_array == vertex_value[2][0])[0], np.where(mesh_set.node_set.z_array == vertex_value[2][1])[0]]]
        # faces
        for i in range(3):
            if len(faces_nodes_idx_array[i][0]) != len(faces_nodes_idx_array[i][1]):
                raise Exception("class rve_set def __init__: Number of nodes on the periodic faces not equal.")
            self.face_nodes_set[i][0] = mesh_set.node_set.id_array[faces_nodes_idx_array[i][0]]
            self.face_nodes_set[i][1] = mesh_set.node_set.id_array[faces_nodes_idx_array[i][1]]

        # detect edges nodes //x [[b-a],[c-d],[c'-d'],[b'-a']] //y [[d-a],[c-b],[c'-b'],[d'-a']] //z [[a-a'],[b-b'],[c-c'],[d-d']]
        self.edge_nodes_set[0][0] = np.intersect1d(self.face_nodes_set[1][0], self.face_nodes_set[2][0])
        self.edge_nodes_set[0][1] = np.intersect1d(self.face_nodes_set[1][1], self.face_nodes_set[2][0])
        self.edge_nodes_set[0][2] = np.intersect1d(self.face_nodes_set[1][1], self.face_nodes_set[2][1])
        self.edge_nodes_set[0][3] = np.intersect1d(self.face_nodes_set[1][0], self.face_nodes_set[2][1])
        self.edge_nodes_set[1][0] = np.intersect1d(self.face_nodes_set[0][0], self.face_nodes_set[2][0])
        self.edge_nodes_set[1][1] = np.intersect1d(self.face_nodes_set[0][1], self.face_nodes_set[2][0])
        self.edge_nodes_set[1][2] = np.intersect1d(self.face_nodes_set[0][1], self.face_nodes_set[2][1])
        self.edge_nodes_set[1][3] = np.intersect1d(self.face_nodes_set[0][0], self.face_nodes_set[2][1])
        self.edge_nodes_set[2][0] = np.intersect1d(self.face_nodes_set[0][0], self.face_nodes_set[1][0])
        self.edge_nodes_set[2][1] = np.intersect1d(self.face_nodes_set[0][1], self.face_nodes_set[1][0])
        self.edge_nodes_set[2][2] = np.intersect1d(self.face_nodes_set[0][1], self.face_nodes_set[1][1])
        self.edge_nodes_set[2][3] = np.intersect1d(self.face_nodes_set[0][0], self.face_nodes_set[1][1])
        #       ' ------ '
        #      /|       /|
        #     ' ------ ' |          z
        #     | a -----| b          | __ x
        #     |/       |/          /
        #     d ______ c          y
        # detect vertex a,b,c,d,a',b',c',d'
        self.vertex_nodes_array[0] = np.intersect1d(self.edge_nodes_set[2][0], self.edge_nodes_set[1][0])[0]
        self.vertex_nodes_array[1] = np.intersect1d(self.edge_nodes_set[2][1], self.edge_nodes_set[1][1])[0]
        self.vertex_nodes_array[2] = np.intersect1d(self.edge_nodes_set[2][2], self.edge_nodes_set[1][1])[0]
        self.vertex_nodes_array[3] = np.intersect1d(self.edge_nodes_set[2][3], self.edge_nodes_set[1][0])[0]
        self.vertex_nodes_array[4] = np.intersect1d(self.edge_nodes_set[2][0], self.edge_nodes_set[0][3])[0]
        self.vertex_nodes_array[5] = np.intersect1d(self.edge_nodes_set[2][1], self.edge_nodes_set[0][3])[0]
        self.vertex_nodes_array[6] = np.intersect1d(self.edge_nodes_set[2][2], self.edge_nodes_set[0][2])[0]
        self.vertex_nodes_array[7] = np.intersect1d(self.edge_nodes_set[2][3], self.edge_nodes_set[0][2])[0]

        # create inner set
        for i in range(3):
            for j in range(4):
                mask = np.isin(self.edge_nodes_set[i][j], self.vertex_nodes_array)
                self.edge_nodes_array_inner[i][j] = self.edge_nodes_set[i][j][~mask]

        all_edges_nodes_array = np.concatenate(self.edge_nodes_set)
        all_edges_nodes_array = np.unique(all_edges_nodes_array)
        for i in range(3):
            for j in range(2):
                mask = np.isin(self.face_nodes_set[i][j], all_edges_nodes_array)
                self.face_nodes_set_inner[i][j] = self.face_nodes_set[i][j][~mask]

    def reorder_nodes_4mpc(self, mesh_nodes_set: node_set):
        """
        reorder the inner nodes for face and edges for mpc implementation
        :param mesh_nodes_set:
        :return:
        """
        print("INFO: Reordering the nodes arrangement for implementation of MPC.")
        nodes_coordinates_list = [mesh_nodes_set.x_array, mesh_nodes_set.y_array, mesh_nodes_set.z_array]
        COORDINATES = [[1, 2], [0, 2], [0, 1]]
        # reorder for the inner face
        for i in tqdm(range(3)):
            faces_nodes_inner_1, faces_nodes_inner_2 = self.face_nodes_set_inner[i][0],self.face_nodes_set_inner[i][1]
            COOR1, COOR2 = COORDINATES[i][0], COORDINATES[i][1]
            curr_coor1, curr_coor2 = nodes_coordinates_list[COOR1], nodes_coordinates_list[COOR2]
            cmp_nodes_coor_1, cmp_nodes_coor_2 = curr_coor1[mesh_nodes_set.id2idx_map_array[faces_nodes_inner_2]], curr_coor2[mesh_nodes_set.id2idx_map_array[faces_nodes_inner_2]]
            temp = np.empty(len(faces_nodes_inner_2),dtype=int)
            for j in range(len(faces_nodes_inner_1)):
                curr_node_id = faces_nodes_inner_1[j]
                curr_node_idx = mesh_nodes_set.id2idx_map_array[curr_node_id]
                curr_node_coor_1, curr_node_coor_2 = curr_coor1[curr_node_idx], curr_coor2[curr_node_idx]
                dist = np.abs(np.add(cmp_nodes_coor_1, -curr_node_coor_1)) + np.abs(np.add(cmp_nodes_coor_2, -curr_node_coor_2))
                near_idx = np.argmin(dist)
                near_id = faces_nodes_inner_2[near_idx]
                temp[j] = near_id
                # delete for speed-up
                faces_nodes_inner_2 = np.delete(faces_nodes_inner_2, near_idx)
                cmp_nodes_coor_1 = np.delete(cmp_nodes_coor_1, near_idx)
                cmp_nodes_coor_2 = np.delete(cmp_nodes_coor_2, near_idx)
            self.face_nodes_set_inner[i][1] = temp
        # reorder for the edges
        for i in tqdm(range(3)):
            edge_nodes_arr_1 = self.edge_nodes_array_inner[i][0]
            edge_nodes_set = [self.edge_nodes_array_inner[i][1],self.edge_nodes_array_inner[i][2],self.edge_nodes_array_inner[i][3]]
            cmp_nodes_coor_set = [nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][1]]],
                                  nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][2]]],
                                  nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][3]]]]
            temp = [np.empty(len(self.edge_nodes_array_inner[i][1]),dtype=int),
                    np.empty(len(self.edge_nodes_array_inner[i][2]),dtype=int),
                    np.empty(len(self.edge_nodes_array_inner[i][3]),dtype=int)]
            for j in range(len(edge_nodes_arr_1)):
                curr_node_id = edge_nodes_arr_1[j]
                curr_node_idx = mesh_nodes_set.id2idx_map_array[curr_node_id]
                curr_node_coor = nodes_coordinates_list[i][curr_node_idx]
                for k in range(3):
                    dist = np.abs(np.add(cmp_nodes_coor_set[k],-curr_node_coor))
                    near_idx = np.argmin(dist)
                    near_id = edge_nodes_set[k][near_idx]
                    temp[k][j] = near_id
                    # delete
                    edge_nodes_set[k] = np.delete(edge_nodes_set[k],near_idx)
                    cmp_nodes_coor_set[k] = np.delete(cmp_nodes_coor_set[k], near_idx)
            self.edge_nodes_array_inner[i][1] = temp[0]
            self.edge_nodes_array_inner[i][2] = temp[1]
            self.edge_nodes_array_inner[i][3] = temp[2]
        self.reorder_flag = True

    def adjust_nodes_pos_4mpc(self,mesh_nodes_set:node_set):
        """
        Adjust the nodes position for implementation of MPC
        :param mesh_nodes_set:
        :return:
        """
        print("INFO: Adjusting the nodes position for implementation of MPC.")
        if self.reorder_flag is False:
            self.reorder_nodes_4mpc(mesh_nodes_set)
        nodes_coordinates_list = [mesh_nodes_set.x_array, mesh_nodes_set.y_array, mesh_nodes_set.z_array]
        COORDINATES = [[1, 2], [0, 2], [0, 1]]
        for i in range(3):
            for j in range(2):
                avg = 0.5 * (nodes_coordinates_list[COORDINATES[i][j]][
                                 mesh_nodes_set.id2idx_map_array[self.face_nodes_set_inner[i][0]]] +
                             nodes_coordinates_list[COORDINATES[i][j]][
                                 mesh_nodes_set.id2idx_map_array[self.face_nodes_set_inner[i][1]]])
                nodes_coordinates_list[COORDINATES[i][j]][
                    mesh_nodes_set.id2idx_map_array[self.face_nodes_set_inner[i][0]]] = avg
                nodes_coordinates_list[COORDINATES[i][j]][
                    mesh_nodes_set.id2idx_map_array[self.face_nodes_set_inner[i][1]]] = avg
        for i in range(3):
            avg = 0.25 * (
                        nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][0]]] +
                        nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][1]]] +
                        nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][2]]] +
                        nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][3]]])
            nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][0]]] = avg
            nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][1]]] = avg
            nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][2]]] = avg
            nodes_coordinates_list[i][mesh_nodes_set.id2idx_map_array[self.edge_nodes_array_inner[i][3]]] = avg
        mesh_nodes_set.x_array = nodes_coordinates_list[0]
        mesh_nodes_set.y_array = nodes_coordinates_list[1]
        mesh_nodes_set.z_array = nodes_coordinates_list[2]

    def write_mpc_keyword(self, strain_tensor: list,max_node_id: int, file_dir: str):
        lines = []
        # header
        lines.append('*KEYWORD\n')
        lines.append('*RVE_INFO\n')
        lines.append(f'{max_node_id}'.rjust(20) + f'{self.size[0]}'.rjust(20) + f'{self.size[1]}'.rjust(20) + f'{self.size[2]}'.rjust(20) + '\n')
        lines.append('*INCLUDE\n')
        lines.append('mesh.k    \n')
        # create dummy nodes 1. tension
        dummy_nodes = [max_node_id + 1, max_node_id + 2, max_node_id + 3]
        lines.append('*NODE\n')
        lines += [f'{dummy_nodes[i]}'.rjust(8) + '           0.000           0.000           0.000       0\n' for i in range(len(dummy_nodes))]
        # face +x,-x
        # edge in x bb'->aa', cc'->dd', bc->ad, b'c'->a'd'
        # vertex c->d, b->a, c'->d', b'->a'
        lines.append('*CONSTRAINED_MULTIPLE_GLOBAL\n')
        lines.append('       1\n')
        couple_set = [
            [self.face_nodes_set_inner[0][1], self.face_nodes_set_inner[0][0]],
            [self.edge_nodes_array_inner[2][1], self.edge_nodes_array_inner[2][0]],
            [self.edge_nodes_array_inner[2][2], self.edge_nodes_array_inner[2][3]],
            [self.edge_nodes_array_inner[1][1], self.edge_nodes_array_inner[1][0]],
            [self.edge_nodes_array_inner[1][2], self.edge_nodes_array_inner[1][3]],
            [[self.vertex_nodes_array[2], self.vertex_nodes_array[1], self.vertex_nodes_array[6], self.vertex_nodes_array[5]],
             [self.vertex_nodes_array[3], self.vertex_nodes_array[0], self.vertex_nodes_array[7], self.vertex_nodes_array[4]]]
        ]
        mpc_lines = _prepare_mpc_set_lines(couple_set, dummy_nodes[0])
        lines += mpc_lines
        # face +y,-y
        # edge cd->ba, c'd'->b'a', dd'->aa'
        # vertex d->a , d'->a'
        lines.append('*CONSTRAINED_MULTIPLE_GLOBAL\n')
        lines.append('       2\n')
        couple_set = [
            [self.face_nodes_set_inner[1][1], self.face_nodes_set_inner[1][0]],
            [self.edge_nodes_array_inner[0][1], self.edge_nodes_array_inner[0][0]],
            [self.edge_nodes_array_inner[0][2], self.edge_nodes_array_inner[0][3]],
            [self.edge_nodes_array_inner[2][3], self.edge_nodes_array_inner[2][0]],
            [[self.vertex_nodes_array[3], self.vertex_nodes_array[7]],[self.vertex_nodes_array[0], self.vertex_nodes_array[4]]]
        ]
        mpc_lines = _prepare_mpc_set_lines(couple_set, dummy_nodes[1])
        lines += mpc_lines
        # face +z,-z
        # edge d'a'->da, b'a'->ba
        # vertex a'->a
        lines.append('*CONSTRAINED_MULTIPLE_GLOBAL\n')
        lines.append('       3\n')
        couple_set = [
            [self.face_nodes_set_inner[2][1], self.face_nodes_set_inner[2][0]],
            [self.edge_nodes_array_inner[1][3], self.edge_nodes_array_inner[1][0]],
            [self.edge_nodes_array_inner[0][3], self.edge_nodes_array_inner[0][0]],
            [[self.vertex_nodes_array[4]],[self.vertex_nodes_array[0]]]
        ]
        mpc_lines = _prepare_mpc_set_lines(couple_set, dummy_nodes[2])
        lines += mpc_lines
        # dummy points mpc
        lines.append('*CONSTRAINED_MULTIPLE_GLOBAL\n')
        lines.append('       4\n')
        lines.append('       2\n' + f'{dummy_nodes[0]}'.rjust(8) + ',  2,  1.000000\n' + f'{dummy_nodes[1]}'.rjust(8) + ',  1, -1.000000\n')
        lines.append('       2\n' + f'{dummy_nodes[0]}'.rjust(8) + ',  3,  1.000000\n' + f'{dummy_nodes[2]}'.rjust(8) + ',  1, -1.000000\n')
        lines.append('       2\n' + f'{dummy_nodes[1]}'.rjust(8) + ',  3,  1.000000\n' + f'{dummy_nodes[2]}'.rjust(8) + ',  2, -1.000000\n')
        # fix one node
        lines.append('*BOUNDARY_SPC_NODE\n')
        lines.append('        18         0         1         1         1\n')
        # strain tensor xx,yy,zz,xy,yz,xz
        uxx = strain_tensor[0] * self.size[0]
        uyy = strain_tensor[1] * self.size[1]
        uzz = strain_tensor[2] * self.size[2]
        uxy = strain_tensor[3] * self.size[0]
        uxz = strain_tensor[4] * self.size[0]
        uyz = strain_tensor[5] * self.size[1]
        lines.append('*BOUNDARY_PRESCRIBED_MOTION_NODE\n')
        lines.append(f'{dummy_nodes[0]}'.rjust(10) + '         1         2         1' + f'{uxx}'.rjust(10) + '\n')
        lines.append(f'{dummy_nodes[0]}'.rjust(10) + '         2         2         1' + f'{uyz}'.rjust(10) + '\n') # uyz
        lines.append(f'{dummy_nodes[0]}'.rjust(10) + '         3         2         1' + f'{uxy}'.rjust(10) + '\n') # uxy
        lines.append(f'{dummy_nodes[1]}'.rjust(10) + '         2         2         1' + f'{uyy}'.rjust(10) + '\n')
        lines.append(f'{dummy_nodes[1]}'.rjust(10) + '         3         2         1' + f'{uxz}'.rjust(10) + '\n')
        lines.append(f'{dummy_nodes[2]}'.rjust(10) + '         3         2         1' + f'{uzz}'.rjust(10) + '\n')
        lines.append('*END\n')
        # write
        write_io = open(file_dir, 'w')
        write_lines(write_io, lines)

def _prepare_mpc_set_lines(couple_set, dummy_node):
    lines = []
    node_1_array = []
    node_2_array = []
    for i in range(len(couple_set)):
        for j in range(len(couple_set[i][0])):
            node_1_array.append(couple_set[i][0][j])
            node_2_array.append(couple_set[i][1][j])
    node_1_array = np.array(node_1_array, dtype=int)
    node_2_array = np.array(node_2_array, dtype=int)
    node_1_array, node_2_array = sort_array_together_correspond_to_first_array(node_1_array, node_2_array)
    for i in range(len(node_1_array)):
        for k in range(3):
            lines.append('       3\n')
            lines.append(f'{node_1_array[i]}'.rjust(8) + f',  {int(k + 1)}, -1.000000\n')
            lines.append(f'{node_2_array[i]}'.rjust(8) + f',  {int(k + 1)},  1.000000\n')
            lines.append(f'{dummy_node}'.rjust(8) + f',  {int(k + 1)},  1.000000\n')
    return lines















