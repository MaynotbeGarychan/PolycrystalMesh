import numpy as np

def ret_idx_by_id(id ,id_array) -> int:
    """
    calculate the index of the id in the id_array
    :param id:
    :param id_array:
    :return: index
    """
    return np.where(id_array == id)[0][0]

def ret_indices_of_id_array(id_array,selected_id_array):
    """
    given a selected id list, return the indices of the selected id
    from the id_array
    :param selected_id:
    :return:
    """
    num = len(selected_id_array)
    indices = np.zeros(num,dtype=int)
    for i in range(num):
        selected_id = selected_id_array[i]
        indices[i] = np.where(id_array == selected_id)[0][0]
    return indices

def ret_id2idx_map_array(id_array):
    """
    provide an array for mapping the id to the idx
    given the id, will return the idx of the given id in the id array
    :param id_array:
    :return:
    """
    map_array = np.zeros(max(id_array)+1,dtype=int)
    for i in range(len(id_array)):
        map_array[id_array[i]] = np.where(id_array == id_array[i])[0][0]
    return map_array