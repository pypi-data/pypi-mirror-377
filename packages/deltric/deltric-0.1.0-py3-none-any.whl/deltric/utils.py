import numpy as np

from sklearn.decomposition import PCA
from scipy.spatial import Delaunay
import networkx as nx
from sklearn.manifold import TSNE
from umap import UMAP
import pandas as pd

from statsmodels import robust

ANOMALY_THRESH = 3

def get_triangles_with_edges(X, project_dim=2, method='umap', back_proj=True):
    # Project if needed
    if method == 'pca' and X.shape[1] > project_dim:
        projector = PCA(n_components=project_dim, random_state=42)
        X_proj = projector.fit_transform(X)
    elif method == 'umap' and X.shape[1] > project_dim:
        projector = UMAP(n_components=project_dim, random_state=42)
        X_proj = projector.fit_transform(X)
    elif method == 'none' or X.shape[1] <= project_dim:
        X_proj = X
    else:
        raise ValueError("Invalid projection method. Choose from 'pca', 'umap', or 'none'.")

    tri = Delaunay(X_proj)
    triangles = tri.simplices  # shape (num_triangles, 3)

    # Calculate triangle sizes (max edge length)
    triangle_sizes = []
    triangle_sizes_proj = []
    for simplex in triangles:
        pts = X[list(simplex)]  # original space points for accurate edge lengths
        pts_proj = X_proj[list(simplex)]
        if back_proj==False:
            pts = pts_proj
        edges = [np.linalg.norm(pts[i] - pts[(i+1)%3]) for i in range(3)]
        edges_proj = [np.linalg.norm(pts_proj[i] - pts_proj[(i+1)%3]) for i in range(3)]
        max_edge = max(edges)
        max_edge_proj = max(edges_proj)
        triangle_sizes.append(max_edge)
        triangle_sizes_proj.append(max_edge_proj)

    return triangles, np.array(triangle_sizes), np.array(triangle_sizes_proj), X_proj


# 4️⃣ Get clusters from remaining edges
def get_clusters(edges, n_points):
    G = nx.Graph()
    G.add_nodes_from(range(n_points))
    G.add_edges_from(edges)
    clusters = [list(c) for c in nx.connected_components(G)]
    return clusters

def cluster_umap_representative(X, X_proj, clusters):
    reps = []
    for cluster in clusters:
        pts_proj = X_proj[cluster]
        center = pts_proj.mean(axis=0)
        # find the index in the original dataset
        idx = cluster[np.argmin(np.linalg.norm(pts_proj - center, axis=1))]
        reps.append(X_proj[idx])  # X would be actual point, if X_proj used, the merging effectively runs only in umap space. There is only few points after creating centroids, thus umap would create manifolds wrongly.
    return np.array(reps)

def merge_anomalies_triangles(X, X_proj, clusters, triangles, sizes, proj_sizes, dist_thresh=0.15,
                              anomaly_thresh=1, max_iter=1, debug=True):

    scaling_factor = (np.median(proj_sizes) / np.median(sizes))

    # Map point -> cluster
    point_to_cluster = {}
    for ci, cluster in enumerate(clusters):
        for p in cluster:
            point_to_cluster[p] = ci

    merged_clusters = [list(c) for c in clusters]  # deep copy

    for it in range(max_iter):
        if debug:
            print(f"\nIteration {it+1}/{max_iter}")

        merged_any = False
        anomaly_count = 0
        merged_count = 0

        for ci, cluster in enumerate(list(merged_clusters)):
            if len(cluster) > anomaly_thresh:
                continue  # only anomalies
            if len(cluster) == 0:
                continue

            anomaly_count += 1
            # p = cluster[0]

            dists = {}
            for p in cluster:
                
                # Find triangles containing this anomaly
                tri_mask = np.any(triangles == p, axis=1)
                tri_candidates = triangles[tri_mask]
                size_candidates = sizes[tri_mask]

                if tri_candidates.size == 0:
                    continue

                # Collect neighbors from all triangles
                neighbor_points = set()
                for tri in tri_candidates:
                    for q in tri:
                        if q != p and q in point_to_cluster and point_to_cluster[q] != ci:
                            neighbor_points.add(q)

                neighbor_points = list(neighbor_points)

                # Distances to anomaly in both spaces
                for q in neighbor_points:
                    d_X = scaling_factor * np.linalg.norm(X[p] - X[q])
                    d_Xproj = np.linalg.norm(X_proj[p] - X_proj[q])
                    _d = max(d_X, d_Xproj)
                    dists[q] = _d if _d < dists.get(q, float('inf')) else dists.get(q, float('inf'))

            n = len(dists)
            if n == 0:
                continue

            # Aggregate scores per cluster
            cluster_scores = {}
            mean_size = scaling_factor * np.mean(sizes)  # could also use np.mean(size_candidates)
            for q, dist in dists.items():
                if dist == 0:
                    continue
                neigh_cluster = point_to_cluster[q]
                contrib = 1.0 / dist
                cluster_scores[neigh_cluster] = cluster_scores.get(neigh_cluster, 0.0) + contrib

            if not cluster_scores:
                continue

            # Normalize by n and multiply by mean_size
            for k in cluster_scores:
                cluster_scores[k] = (1.0 / n) * mean_size * cluster_scores[k]

            # Pick cluster with max score
            target_cluster, best_score = max(cluster_scores.items(), key=lambda x: x[1])

            if best_score > dist_thresh:
                continue

            # Merge anomaly
            merged_clusters[target_cluster].extend(cluster)
            merged_clusters[ci] = []
            merged_any = True
            merged_count += 1

        if debug:
            print(f" - Anomalies processed: {anomaly_count}")
            print(f" - Merged this round: {merged_count}")

        # Update mapping if we merged
        if merged_any:
            point_to_cluster = {}
            for ci, cluster in enumerate(merged_clusters):
                for p in cluster:
                    point_to_cluster[p] = ci
        else:
            break  # no more merges → stop early

    # Remove empty clusters
    merged_clusters = [sorted(c) for c in merged_clusters if len(c) > 0]
    return merged_clusters


def sigma_prune_triangles(triangles, sizes, proj_sizes, sigma_factor):
    # Normalize sizes to have comparable scales
    #scaling_factor = (np.median(proj_sizes) / np.median(sizes))
    #sizes_z = sizes * scaling_factor
    #proj_sizes_z = proj_sizes

    # sizes_z = (sizes - sizes.mean()) / sizes.std()
    # proj_sizes_z = (proj_sizes - proj_sizes.mean()) / proj_sizes.std()
    # mean_size = np.mean(sizes_z)
    # sigma = np.std(sizes_z)
    # threshold = mean_size + sigma_factor * sigma

    # sizes_z = dominant_bump_normalization(sizes, sigma_factor)
    # proj_sizes_z = dominant_bump_normalization(proj_sizes, sigma_factor)
    # threshold = sigma_factor  # since sizes_z are already in z-score form

    mu = np.median(sizes)
    sigma = robust.mad(sizes)  # robust std
    sizes_z = (sizes - mu) / sigma
    mu = np.median(proj_sizes)
    sigma = robust.mad(proj_sizes)  # robust std
    proj_sizes_z = (proj_sizes - mu) / sigma

    mean_size = np.mean(sizes_z)
    sigma = np.std(sizes_z)
    threshold = mean_size + sigma_factor * sigma


    kept_triangles = triangles[np.maximum(sizes_z, proj_sizes_z) <= threshold]   # we trust umap to create a distinct clusters
    rm_triangles = triangles[np.maximum(sizes_z, proj_sizes_z) > threshold]
    edges = set()
    rm_edges = set()
    for tri in rm_triangles:
        for i in range(3):
            a, b = sorted((tri[i], tri[(i+1)%3]))
            rm_edges.add((a, b))
    for tri in kept_triangles:
        for i in range(3):
            a, b = sorted((tri[i], tri[(i+1)%3]))
            edges.add((a, b))
    return list(edges), list(rm_edges), threshold

def merge_clusters(X, X_proj, clusters, method, merge_param, back_proj=True, anomaly_thresh=2, min_centroids=5):
    # Compute centroids of clusters in original high-dimensional space
    # centroids = np.array([np.mean(X[cluster], axis=0) for cluster in clusters])
    anomalies = [cl for cl in clusters if len(cl) <= anomaly_thresh]
    rich_clusters = [cl for cl in clusters if len(cl) > anomaly_thresh]
    centroids = cluster_umap_representative(X, X_proj, rich_clusters)
    if len(centroids) < min_centroids:
        return clusters

    try:
        # Triangulate on centroids
        triangles, sizes, proj_sizes, _ = get_triangles_with_edges(centroids, project_dim=2, method=method, back_proj=back_proj)

        # Merge clusters if triangle size <= mean + merge_param*sigma
        edges_between_clusters, _, _ = sigma_prune_triangles(triangles, sizes, proj_sizes, sigma_factor=merge_param)

        # Build graph where nodes are clusters and edges mean merge
        G = nx.Graph()
        G.add_nodes_from(range(len(rich_clusters)))
        G.add_edges_from(edges_between_clusters)

        merged_clusters = []
        for comp in nx.connected_components(G):
            merged_points = []
            for cluster_idx in comp:
                merged_points.extend(rich_clusters[cluster_idx])
            merged_clusters.append(sorted(merged_points))

        return merged_clusters + anomalies  # add back anomalies as separate clusters
    except:
        print('!!! Cluster Merging Failed !!!')
        return clusters


def tri_cluster_sigma_merge(X, prune_param=0.15, merge_param=-0.2, method='umap', anomaly_sensitivity=0.5, back_proj=True, debug=False):
    # Step 1: Triangles & sigma pruning
    triangles, sizes, proj_sizes, X_proj = get_triangles_with_edges(X, project_dim=2, method=method, back_proj=back_proj)
    pruned_edges, rm_edges, threshold = sigma_prune_triangles(triangles, sizes, proj_sizes, sigma_factor=prune_param)
    clusters = get_clusters(pruned_edges, len(X))
    if debug:
        print(f"After pruning: {len(clusters)} clusters")
        print(f"Anomalies: {len([cl for cl in clusters if len(cl) <= ANOMALY_THRESH])}")

    # Step 2: Merge pass on centroids
    merged_clusters = merge_clusters(X, X_proj, clusters, method, merge_param, back_proj=back_proj, anomaly_thresh=ANOMALY_THRESH)
    if debug:
        print(f"After merging clusters: {len(merged_clusters)} clusters")

    if anomaly_sensitivity < 1.00:
        # threshold = np.mean(sizes) + np.std(sizes) * prune_param
        # dist_thresh = threshold / anomaly_sensitivity  # fix this completely to the projected space
        dist_thresh = 1.0 - anomaly_sensitivity
        # merged_clusters = merge_anomalies(X, X_proj, merged_clusters, dist_thresh=dist_thresh, anomaly_thresh=ANOMALY_THRESH)
        _X = X
        if back_proj==False:
            _X = X_proj
        merged_clusters = merge_anomalies_triangles(_X, X_proj, merged_clusters, triangles, sizes, proj_sizes, dist_thresh=dist_thresh, anomaly_thresh=ANOMALY_THRESH, max_iter=3, debug=True)

    if debug:
        print(f"After merging anomalies: {len(merged_clusters)} clusters")

    # Keeping same output structure, but adding merged_clusters as extra
    return triangles, sizes, pruned_edges, rm_edges, merged_clusters


def cluster_tri(X, prune_param=-0.8, merge_param=0.0, min_cluster_size=10, dim_reduction='umap', back_proj=True, anomaly_sensitivity=0.99):
    _, _, pruned_edges, _, clusters = tri_cluster_sigma_merge(X, prune_param=prune_param, merge_param=merge_param, method=dim_reduction, back_proj=back_proj, anomaly_sensitivity=anomaly_sensitivity)

    # Start with all points as noise
    labels = np.full(len(X), -1, dtype=int)

    label_id = 0
    for cluster in clusters:
        if len(cluster) > ANOMALY_THRESH:
            for idx in cluster:
                labels[idx] = label_id
            label_id += 1
        # else: keep as -1 (noise)

    return labels