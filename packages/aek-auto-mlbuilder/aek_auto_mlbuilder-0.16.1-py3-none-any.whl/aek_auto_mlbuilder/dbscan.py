from sklearn.cluster import DBSCAN
from .base import BaseModel

class DBSCANModel(BaseModel):
    """
    DBSCAN clustering model (unsupervised learning)
    brute force searching is being used
    """
    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "eps": [0.3, 0.5, 0.7, 1.0],
            "min_samples": [3, 5, 10]
        }

    def train(self, X):
        best_score = -float("inf")
        best_model = None

        for eps in self.param_grid["eps"]:
            for min_samples in self.param_grid["min_samples"]:
                model = DBSCAN(eps=eps, min_samples=min_samples)
                labels = model.fit_predict(X)

                score = len(labels) - (labels == -1).sum()
                if score > best_score:
                    best_score = score
                    best_model = model
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model