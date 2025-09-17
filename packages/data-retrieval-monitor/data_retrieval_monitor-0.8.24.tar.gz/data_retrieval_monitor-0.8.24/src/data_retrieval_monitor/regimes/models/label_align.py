# models/label_align.py
import numpy as np
from scipy.optimize import linear_sum_assignment

def align_labels(prev_centers: np.ndarray, new_centers: np.ndarray, labels: np.ndarray):
    """
    Align 'labels' produced from new_centers to match prev_centers ordering via Hungarian assignment.
    prev_centers: (K, d) previous window centers (or None on first window)
    new_centers:  (K, d) current window centers
    labels:       (n,) current labels in 0..K-1
    Returns: aligned_labels, perm (array where new_label -> prev_label)
    """
    if prev_centers is None or new_centers is None:
        K = new_centers.shape[0]
        return labels, np.arange(K, dtype=int)

    K = new_centers.shape[0]
    # cost = distance between centers
    C = np.linalg.norm(prev_centers[:, None, :] - new_centers[None, :, :], axis=-1)
    r, c = linear_sum_assignment(C)
    # c[j] is new index that maps to prev index r[j]
    # build inverse map: new_label -> aligned_label
    perm = np.zeros(K, dtype=int)
    for prev_idx, new_idx in zip(r, c):
        perm[new_idx] = prev_idx
    aligned = perm[labels]
    return aligned, perm