import numpy as np
from src.pre_process.mesh_elem import elem_set
from src.pre_process.mesh_node import node_set

class mesh(object):
    elem_set = elem_set('')
    node_set = node_set('')

    def __init__(self, input_file_dir:str):
        if input_file_dir.endswith('k'):
            # print("INFO: Reading mesh information from keyword file")
            self.elem_set = elem_set(input_file_dir)
            self.node_set = node_set(input_file_dir)
        else:
            self.elem_set = elem_set('')
            self.node_set = node_set('')
            # print("INFO: Creating empty mesh set")

    # Output mesh
    def write_keyword(self, write_io):
        """
        Io to Output the mesh set keyword to the given directory
        :param write_io: io to keywore file
        :return:
        """
        self.elem_set.write_keyword(write_io)
        self.node_set.write_keyword(write_io)

    # Mesh tools
    def drag_shell_to_solid(self, num_layers: int, thicknesss):
        """
        Drag the shell mesh to be solid mesh,
        This functions should be used in the mesh set which has been reordered.
        :param num_layers:
        :param thicknesss:
        :return:
        """
        print("INFO: Dragging shell mesh into solid/tshell mesh")
        # checking input
        shell_mesh = self
        if shell_mesh.elem_set.type != 'ELEMENT_SHELL':
            print("ERROR: obj.mesh - func.drag_shell_to_solid : Incorrect element type")
            return False
        if type(thicknesss) == float or int:
            thickness_list = [float(thicknesss)] * num_layers
        elif len(thicknesss) == num_layers:
            thickness_list = thicknesss
        else:
            print("ERROR: obj.mesh - func.drag_shell_to_solid : Incorrect thickness for shell drag")
            return False
        # make empty solid mesh set, and assign basic value to the mesh object
        solid_mesh = mesh('')
        solid_mesh.elem_set.num = shell_mesh.elem_set.num * num_layers
        solid_mesh.elem_set.type = "ELEMENT_SOLID"
        solid_mesh.node_set.num = shell_mesh.node_set.num * (num_layers + 1)

        # ==================================================== #
        #   important operations for dragging mesh             #
        # ==================================================== #

        #       Operation: Dragging the nodes set
        #       Description:
        #           for the new nodes of solid mesh, if we want to drag into 2 layer of solid mesh
        #           we have to drag the nodes for 3 layers
        #           1. id_array:
        #                   shell_mesh.nodes_set.id_array: [a,b,c,d,...]
        #                   solid_mesh.nodes_set.id_array:
        #                           [1,2,3,4,5,6,7,...] corresponding to:
        #                           [a1,a2,a3,b1,b2,b3,c1, ...]
        #                            from a, from b, from c, ...
        #           2. coordinates_list:
        #                   shell_mesh.nodes_set.coordinates_list:
        #                           [[x_a,y_a,z_a],[x_b,y_b,z_b],[x_c,y_c,z_c], ...]
        #                   solid_mesh.nodes_set.coordinates_list:
        #                           [[x_a1,y_a1,z_a1],[x_a2,y_a2,z_a2],[x_a3,y_a3,z_a3], ...]
        #                           following the sequence of id_array

        # id_array
        num_drag_nodes = num_layers + 1
        solid_mesh.node_set.id_array = np.arange(1,solid_mesh.node_set.num+1,dtype=int)
        # coordinates_list
        solid_mesh.node_set.x_array = np.empty(solid_mesh.node_set.num, dtype=float)
        solid_mesh.node_set.y_array = np.empty(solid_mesh.node_set.num, dtype=float)
        solid_mesh.node_set.z_array = np.empty(solid_mesh.node_set.num, dtype=float)
        for i in range(shell_mesh.node_set.num):
            ret = self._drag_node(shell_mesh.node_set.x_array[i],
                                shell_mesh.node_set.y_array[i],
                                shell_mesh.node_set.z_array[i],
                                thickness_list)
            solid_mesh.node_set.x_array[num_drag_nodes * i:num_drag_nodes * (i + 1)] = ret[0]
            solid_mesh.node_set.y_array[num_drag_nodes * i:num_drag_nodes * (i + 1)] = ret[1]
            solid_mesh.node_set.z_array[num_drag_nodes * i:num_drag_nodes * (i + 1)] = ret[2]

        id_map = np.arange(1, solid_mesh.node_set.num + 1, dtype=int).reshape((shell_mesh.node_set.num, num_drag_nodes))

        #       Operation: Dragging the elem set
        #       Description:
        #           for the new elements of solid mesh, if we want to drag into 2 layer of solid mesh
        #
        #           1. id_array:
        #                   shell_mesh.elem_set.id_array: [a,b,c,d,...]
        #                   solid_mesh.elem_set.id_array:
        #                           [1,2,3,4,5,6,7,...] corresponding to:
        #                           [a1,a2,b1,b2,c1, ...]
        #                            from a, from b, from c, ...
        #           2. nodes_list:
        #                   shell_mesh.elem_set.nodes_list:
        #                           [[a_n1,a_n2,a_n3,a_n4],[b_n1,b_n2,b_n3], ...]
        #                   solid_mesh.elem_set.nodes_list:
        #                           [[a1_n1,a1_n2,...,a1_n8],[a2_n1,a2_n2,...,a2_n8],
        #                            [b1_n1,b1_n2,...,b1_n8], ...]
        #                           following the sequence of id_array
        #           3. part_list:
        #                   shell_mesh.elem_set.part_list:  [1,3,4,...]
        #                   solid_mesh.elem_set.part_list:  [1,1,3,3,4,4,...]

        # id_array
        solid_mesh.elem_set.id_array = np.arange(1,solid_mesh.elem_set.num+1)
        # initialize part_list, nodes_list
        solid_mesh.elem_set.part_list = np.empty(solid_mesh.elem_set.num, dtype=int)
        solid_mesh.elem_set.nodes_list = np.empty((solid_mesh.elem_set.num,8), dtype=int)
        # begin to make part_list, nodes_list
        for i in range(shell_mesh.elem_set.num):
            shell_part_id = shell_mesh.elem_set.part_list[i]
            # create drag nodes list
            # [[],      -- drag nodes for original node 1         node 1  *-----------*  node 2
            #  [],      -- drag nodes for original node 2                 |           |         shell
            #  [],      -- drag nodes for original node 3                 |           |
            #  []]      -- drag nodes for original node 4         node 4  *-----------*  node 3
            shell_nodes = shell_mesh.elem_set.nodes_list[i]
            drag_nodes_list = np.empty((4,num_drag_nodes), dtype=int)
            for j in range(4):
                node_idx = shell_nodes[j] - 1
                drag_nodes_list[j] = id_map[node_idx]
            # transpose drag nodes list, then the definition of sequence changes
            # [[],      -- nodes for the first layers of nodes
            # [],       -- nodes for the second layers of nodes
            # [],   ...
            # []]
            drag_nodes_list = np.transpose(drag_nodes_list)
            # begin to lay the layers of nodes to be a solid
            #     node 8  *-----*  node 7
            #            /     /|
            #    node 5 *-----* | node 6
            #           |     | *  node 3
            #   node 1  *-----* node 2
            solid_messh_nodes_list = np.empty((num_layers,8), dtype=int)
            for j in range(num_layers):
                solid_messh_nodes_list[j] = np.hstack((drag_nodes_list[j],drag_nodes_list[j+1]))
            solid_mesh.elem_set.nodes_list[i*num_layers:(i+1)*num_layers] = solid_messh_nodes_list
            # part_list
            solid_mesh.elem_set.part_list[i*num_layers:(i+1)*num_layers] = np.full(num_layers,shell_part_id, dtype=int)
        # finish dragging the mesh
        return solid_mesh

    def _drag_node(self, original_x, original_y, original_z, distance_list):
        """
        Drag one original node in z direction with a list of distance
        :param original_node_coordinates: coordinate of the original node [x,y,z]
        :param distance_list: list of distance between a sequence nodes
        :return: coordinates_list: list of coordinates of the drag nodes
        """
        # given the original coordinate
        x_coordinate = original_x
        y_coordinate = original_y
        z_coordinate = original_z
        # initialize the drag x,y,z array
        num_drag_nodes = len(distance_list)+1
        drag_x_array = np.empty(num_drag_nodes, dtype=float)
        drag_y_array = np.empty(num_drag_nodes, dtype=float)
        drag_z_array = np.empty(num_drag_nodes, dtype=float)
        # original node
        drag_x_array[0] = original_x
        drag_y_array[0] = original_y
        drag_z_array[0] = original_z
        # calculate the coordinates of drag nodes
        drag_x_array.fill(original_x)
        drag_y_array.fill(original_y)
        for i in range(len(distance_list)):
            distance = distance_list[i]
            z_coordinate += distance
            drag_z_array[i+1] = z_coordinate
        # return the node coordinates list
        return drag_x_array, drag_y_array, drag_z_array

    # drag shell to tshell
    def drag_shell_to_tshell(self,thickness: float):
        tshell_mesh = self.drag_shell_to_solid(1,thickness)
        tshell_mesh.elem_set.type = "ELEMENT_TSHELL"
        return tshell_mesh




