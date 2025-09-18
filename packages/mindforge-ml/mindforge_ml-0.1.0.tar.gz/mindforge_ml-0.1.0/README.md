# MindForge ML – Hypertension Anomaly Detection

`MindForge` is an open-source ML library offering simple, consistent, and extensible tools for building and experimenting with models. Starting with unsupervised learning and anomaly detection, it aims to expand into deep learning, NLP, and predictive analytics, making ML more accessible, modular, and production-ready.

`mindforge_ml` provides simple unsupervised ML tools for anomaly detection, clustering, and visualization.
The core component is an **AutoEncoder** wrapped in `Unsupervisedmodel`, with utilities for clustering (KMeans), dimensionality reduction (PCA/t-SNE), and visualization.

---

## 🚀 Model (from `mindforge_ml.unsupervised.model`)

### Importing the Model
```python
from mindforge_ml.unsupervised import AutoEncoder
```

### Importing the Model

```python
from mindforge_ml.unsupervised.model import Unsupervisedmodel
```

### Training

```python
model = Unsupervisedmodel(input_dim=X.shape[1])
model.fit(X_scaled, epochs=20, batch_size=32)
```

---

### 🔑 Core Methods

#### 1. `transform(X)` → Latent Features

* **Input:** Scaled data `X`
* **Why scaled?** Scaling ensures features with larger magnitudes don’t dominate training.
* **What it does:** Encodes the data into a **compressed latent representation** (low-dimensional).
* **Use case:** Great for clustering or dimensionality reduction.

```python
latent = model.transform(X_scaled)
```

---

#### 2. `reconstruct(X)` → Reconstructed Data

* **Input:** Latent features
* **Why latent?** The decoder learns to rebuild the original input from compressed representations.
* **What it does:** Produces a reconstruction close to the original scaled input.

```python
reconstructed = model.reconstruct(X_scaled)
```

---

#### 3. `anomaly_scores(X)` → Reconstruction Errors

* **Input:** Scaled data `X`
* **Why scaled?** Because reconstruction error depends on feature magnitudes; scaling avoids bias.
* **What it does:** Calculates per-sample **mean squared error** (original vs reconstruction).
* **Use case:** High scores indicate anomalies (e.g., hypertension cases).

```python
scores = model.anomaly_scores(X_scaled)
```

---

#### 4. Save / Load Model

```python
# Save model
model.save("hypertension_model.pth")

# Load model
model.load("hypertension_model.pth")
```






---

## 🔧 Utils (from `mindforge_ml.utils`)

Utility functions help prepare data, cluster, reduce dimensions, and detect anomalies.

---

### 1. `scale_data(X)`

Standardizes features by removing the mean and scaling to unit variance.

* **Why?** Autoencoders, PCA, and clustering methods are sensitive to feature magnitudes. Scaling prevents one feature from dominating.
* **What it returns:** Numpy array of scaled values.

```python
from mindforge_ml.utils import scale_data
X_scaled = scale_data(X)
```

---

### 2. `cluster_kmeans(X, n_clusters=3, random_state=42)`

Clusters data using **KMeans**.

* **Input:**

  * Usually **latent features** from the model (`model.transform(X_scaled)`).
  * Can also take scaled raw data or reconstructed data depending on the use case.

    * **Latent features** → clustering compressed representations (recommended).
    * **Scaled input** → clustering original data (baseline).
    * **Reconstructed data** → clustering the autoencoder’s “understanding” of the data.

* **n\_clusters:** Number of groups to form (default=3).

* **random\_state:** Ensures reproducibility.

```python
clusters = cluster_kmeans(latent, n_clusters=2)
```

---

### 3. `reduce_pca(X, n_components=2)`

Dimensionality reduction using **Principal Component Analysis (PCA)**.

* **n\_components:**

  * `2` (default) → for easy 2D visualization.
  * `3` → for 3D visualization.
  * Higher numbers (10, 50, …) → for preprocessing before clustering.

* **Input:** Typically latent features, but any scaled data can be reduced.

```python
X_pca = reduce_pca(latent, n_components=2)
```

---

### 4. `reduce_tsne(X, n_components=2, random_state=42, perplexity=30, lr=200)`

Dimensionality reduction using **t-SNE** (t-distributed stochastic neighbor embedding).

* **Parameters:**

  * `n_components`: Output dimensions (2D or 3D).
  * `perplexity`: Approximate number of nearest neighbors. Default = 30.
  * `learning_rate (lr)`: Step size; default = 200.

* **Input:** Usually latent features, since t-SNE works best on compressed, meaningful data.

* **Considerations:**

  * t-SNE is more computationally expensive than PCA.
  * Use PCA first to reduce dimensions (e.g., 50) before t-SNE if the dataset is large.

```python
X_tsne = reduce_tsne(latent, n_components=2, perplexity=30)
```

---

### 5. `detect_anomalies(errors, threshold=None)`

Identifies anomalies based on reconstruction error.

* **errors:** Output of `model.anomaly_scores(X_scaled)`.
* **threshold:**

  * If `None`: threshold = `mean + 2 * std` (default heuristic).
  * You can set your own cutoff depending on your domain.
* **Returns:**

  * `anomalies`: Boolean mask (`True` = anomaly).
  * `threshold`: Value used for detection.

```python
anomalies, threshold = detect_anomalies(scores)
```

---






## 📊 Visualization (from `mindforge_ml.visualization`)

This module provides functions to **visualize training progress, clusters, and anomaly detection**.

---

### 1. `plot_losses(train_losses, val_losses=None)`

Plots training (and optionally validation) loss over epochs.

* **Inputs:**

  * `train_losses`: List of training loss values per epoch.
  * `val_losses`: (Optional) List of validation losses per epoch.

```python
from mindforge_ml.visualization import plot_losses

plot_losses(train_losses, val_losses)
```

✅ Helps monitor overfitting (when validation diverges from training).

---

### 2. `plot_clusters(X_2d, clusters, method="PCA", cmap="viridis")`

Visualizes clusters in **2D space**.

* **Inputs:**

  * `X_2d`: Data reduced to 2D (via `reduce_pca` or `reduce_tsne`).
  * `clusters`: Cluster labels (from `cluster_kmeans`).
  * `method`: String label for plot title (“PCA” or “t-SNE”).
  * `cmap`: Colormap (default = `"viridis"`).

```python
from mindforge_ml.visualization import plot_clusters

X_pca = reduce_pca(latent, n_components=2)
clusters = cluster_kmeans(latent, n_clusters=3)
plot_clusters(X_pca, clusters, method="PCA")
```

💡 Works with **both PCA and t-SNE outputs** — just set `method` accordingly.

---

### 3. `plot_anomalies(errors, anomalies, threshold)`

Visualizes the **reconstruction error distribution** and highlights anomalies.

* **Inputs:**

  * `errors`: Reconstruction errors (from `model.anomaly_scores`).
  * `anomalies`: Boolean mask (`True` = anomaly). Optional — can be passed as `None`.
  * `threshold`: Cutoff value for anomaly detection.

* **Behavior:**

  * Plots error histogram.
  * Draws a **red vertical line** for threshold.
  * If `anomalies` is provided, highlights them in orange.

```python
from mindforge_ml.visualization import plot_anomalies

errors = model.anomaly_scores(X_scaled)
anomalies, threshold = detect_anomalies(errors)
plot_anomalies(errors, anomalies, threshold)
```

---

📌 **Note:**

* You should always scale your input before training (`scale_data`).
* Visualization is most meaningful when applied to **latent features** and **anomaly scores**.

---


## GET DEMO DATASET FOR USAGE 

from mindforge_ml.datasets.loader import load_hypertension_data

df = load_hypertension_data()
print(df.head())