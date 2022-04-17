import numpy as np


def modulus(vector):
    dist = np.sqrt(np.einsum('...i,...i', vector, vector))
    return dist


def euclidean_distance(vector1, vector2):
    dist = modulus(vector2 - vector1)
    return dist


def calculate_averaged_euclidean_distance(real_positions, predicted_positions):
    """ Returns the average euclidean distance.
    First, calculate the euclidean distance between each of the real and predicted positions.
    Then, average it to obtain a single metric.
    """
    nb_gratings = np.max(np.shape(real_positions))
    dist_list = np.zeros(nb_gratings)
    for i_pos in range(nb_gratings):
        dist_list[i_pos] = euclidean_distance(real_positions[:, i_pos], predicted_positions[:, i_pos])
    return np.sum(dist_list) / nb_gratings


def results_to_string(list_results):
    s = f"""
    # Avg position error: {list_results}
    # Avg curvature error: {list_results}
    """
    return s
