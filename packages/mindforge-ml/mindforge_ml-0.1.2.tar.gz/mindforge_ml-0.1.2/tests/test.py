import pandas as pd
from mindforge_ml.unsupervised.model import Unsupervisedmodel
from mindforge_ml.utils import scale_data, cluster_kmeans, reduce_pca, detect_anomalies
from mindforge_ml.visualization import plot_anomalies, plot_clusters, plot_losses




df = pd.read_csv('mindforge-ml/hypertensiondataset.csv')
print(df.head())

df = pd.get_dummies(df)

X=df.values
X_scaled=scale_data(X)

# print(f"X : {X[:10]} | \n X_scaled : {X_scaled[:10]}")

model = Unsupervisedmodel(input_dim=X_scaled.shape[1])
model.fit(X_scaled, epochs=20)
# transform = model.transform(X_scaled)

#  python -m tests.output
# print(X_scaled[:10])
model
# print(f"transform: { transform }")
# train_losses = model.fit(X_scaled, epochs=20)
# plot_losses(train_losses)
# latent space
latent = model.transform(X_scaled)

kmeanscluster = cluster_kmeans(latent)
print(f"latent: {latent[:1]} \n kmeanscluster {len(kmeanscluster)}")

pca = reduce_pca(X=latent)
print(pca)

plot_clusters(X_2d=pca, clusters=kmeanscluster)
anomaly_scores = model.anomaly_scores(X_scaled)
print(anomaly_scores)

anomalies, threshold = detect_anomalies(errors=anomaly_scores)

# Pass the actual reconstruction errors, not the boolean mask
plot_anomalies(errors=anomaly_scores, anomalies=anomalies, threshold=threshold)

# model.save(path="/hypertension_model.pth")

# All these are yet to help us classify if the situation of the patient is hypertension or not, what do we do after all these, do we use the trained model to start classifying or what? What does Kmeans do, what's it's job, same as it's fellows like tsa, psme, anomaliasis. What's the transform, reconstruct and anomaly_score for?