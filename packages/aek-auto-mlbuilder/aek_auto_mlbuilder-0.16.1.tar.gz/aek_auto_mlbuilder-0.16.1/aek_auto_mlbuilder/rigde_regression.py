from sklearn.linear_model import Ridge
from .base import BaseModel

class RidgeModel(BaseModel):
    """
    Ridge Regression model
    brute force search is being used
    """

    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "alpha": [0.1, 1.0, 10.0],
            "solver": ["auto", "svd", "cholesky", "lsqr"]
        }
    
    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        for alpha in self.param_grid["alpha"]:
            for solver in self.param_grid["solver"]:
                model = Ridge(alpha=alpha, solver=solver)
                model.fit(X, y)
                score = model.score(X, y)
                if score > best_score:
                    best_score = score
                    best_model = model
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model