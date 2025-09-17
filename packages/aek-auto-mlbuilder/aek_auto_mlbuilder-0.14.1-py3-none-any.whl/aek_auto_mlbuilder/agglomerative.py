from sklearn.cluster import AgglomerativeClustering
from .base import BaseModel

class AgglomerativeModel(BaseModel):
    """
    Agglomerative clustering model
    brute force search is being used
    """

    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "n_clusters": [2, 3, 4, 5, 6],
            "linkage": ["ward", "complete", "average", "single"]
        }

    def train(self, X):
        best_score = -float("inf")
        best_model = None

        for n_clusters in self.param_grid["n_clusters"]:
            for linkage in self.param_grid["linkage"]:
                model = AgglomerativeClustering(
                    n_clusters=n_clusters,
                    linkage=linkage
                )
                labels = model.fit_predict(X)
                clusters = set(labels)
                score = 0
                for k in clusters:
                    cluster_size = (labels == k).sum()
                    score += 1 / cluster_size
                if score > best_score:
                    best_score = score
                    best_model = model
        
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model
    