import numpy as np
from scipy.optimize import linear_sum_assignment

def align_labels(prev_centers, new_centers, labels):
    if new_centers is None: return labels
    if prev_centers is None: return labels
    C = np.linalg.norm(prev_centers[:,None,:] - new_centers[None,:,:], axis=-1)
    r,c = linear_sum_assignment(C)
    perm = np.zeros(new_centers.shape[0], dtype=int)
    for i,j in zip(r,c): perm[j]=i
    return perm[labels]