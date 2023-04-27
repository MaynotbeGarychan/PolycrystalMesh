import numpy as np

def ret_idx_by_id(id ,id_array) -> int:
    """
    calculate the index of the id in the id_array
    :param id:
    :param id_array:
    :return: index
    """
    return np.where(id_array == id)[0][0]