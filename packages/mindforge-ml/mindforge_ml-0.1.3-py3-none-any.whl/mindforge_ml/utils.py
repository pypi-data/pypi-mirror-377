import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def scale_data(X):
    scaler = StandardScaler()
    scaler = scaler.fit_transform(X)
    scaler = pd.DataFrame(scaler).fillna(0).values
    return scaler

def cluster_kmeans(X, n_clusters=3, random_state=42):
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    return kmeans.fit_predict(X)

def reduce_pca(X, n_components=2):
    pca = PCA(n_components=n_components)
    return pca.fit_transform(X)

def reduce_tsne(X, n_components=2, random_state=42, perplexity=30, lr=200):
    tsne = TSNE(n_components=n_components, random_state=random_state, perplexity=perplexity, learning_rate=lr)
    return tsne.fit_transform(X)

def detect_anomalies(errors, threshold=None):
    if threshold is None:
        threshold = errors.mean() + 2 * errors.std()
    anomalies = errors > threshold
    return anomalies, threshold
