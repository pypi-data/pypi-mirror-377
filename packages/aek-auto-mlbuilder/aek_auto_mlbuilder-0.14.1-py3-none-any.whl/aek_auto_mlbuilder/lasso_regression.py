from sklearn.linear_model import Lasso
from .base import BaseModel


class LassoModel(BaseModel):
    """
    Lasso Regression model
    brute force search is being used
    """

    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "alpha": [0.1, 1.0, 10.0],
            "max_iter": [1000, 5000]
        }

    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        for alpha in self.param_grid["alpha"]:
            for max_iter in self.param_grid["max_iter"]:
                model = Lasso(alpha=alpha, max_iter=max_iter)
                model.fit(X, y)
                score = model.score(X, y)
                if score > best_score:
                    best_score = score
                    best_model = model
        
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model