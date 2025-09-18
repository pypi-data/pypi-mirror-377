dt = DelTriC(prune_param=1.497, merge_param=-0.773, dim_reduction='umap', back_proj=True, anomaly_sensitivity=0.9)
labels = dt.fit_predict(X)