import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from kneed import KneeLocator

def evaluar_kmeans_trabajadores(workers_df, k_min=2, k_max=30):
    coords = workers_df[["O_lat", "O_long"]].values

    inertias = []
    k_range = range(k_min, k_max + 1)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(coords)
        inertias.append(kmeans.inertia_)

    # Graficar método del codo
    plt.figure(figsize=(12, 5))

    plt.plot(k_range, inertias, marker='o')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Inertia')
    plt.title('Elbow Method')
    plt.grid(True)
    plt.savefig("elbow_method.png", dpi=300)

    kl = KneeLocator(range(k_min, k_max + 1), inertias, curve="convex", direction="decreasing")
    best_k = kl.elbow
    print(f"Valor óptimo de k (codo): {best_k}")
    return best_k
