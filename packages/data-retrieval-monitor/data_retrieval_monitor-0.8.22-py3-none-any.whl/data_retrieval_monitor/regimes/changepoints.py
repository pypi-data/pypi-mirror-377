# changepoints.py
import numpy as np
try:
    import ruptures as rpt
    CPD = True
except Exception:
    CPD = False

def cpd_all(X, n_bkps=6):
    if not CPD:
        print("[INFO] ruptures not available — skipping CPD.")
        return {}
    labels = {}
    T = X.shape[0]
    n_bkps = max(1, min(n_bkps, T//50))
    # Binseg (l2)
    try:
        bkps = rpt.Binseg(model="l2").fit(X).predict(n_bkps=n_bkps)
        seg = np.zeros(T, dtype=int); start=0
        for seg_id, end in enumerate(bkps):
            seg[start:end] = seg_id; start=end
        labels[f"cpd_binseg_{n_bkps}"] = seg
    except Exception: pass
    # PELT (rbf)
    try:
        bkps = rpt.Pelt(model="rbf").fit(X).predict(pen=10.0*np.log(T)*(X.shape[1]**0.5))
        seg = np.zeros(T, dtype=int); start=0
        for seg_id, end in enumerate(bkps):
            seg[start:end] = seg_id; start=end
        labels["cpd_pelt_rbf"] = seg
    except Exception: pass
    # KernelCPD (rbf)
    try:
        bkps = rpt.KernelCPD(kernel="rbf").fit(X).predict(n_bkps=n_bkps)
        seg = np.zeros(T, dtype=int); start=0
        for seg_id, end in enumerate(bkps):
            seg[start:end] = seg_id; start=end
        labels[f"cpd_kernel_{n_bkps}"] = seg
    except Exception: pass
    return labels