from sklearn.linear_model import Perceptron
from .base import BaseModel

class PerceptronModel(BaseModel):
    """
    Perceptron classification model
    brute force search is being used
    """

    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "penalty": [None, "l2", "l1", "elasticnet"],
            "alpha": [0.0001, 0.001, 0.01],
            "max_iter": [1000, 2000, 3000]
        }

    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        for penalty in self.param_grid["penalty"]:
            for alpha in self.param_grid["alpha"]:
                for max_iter in self.param_grid["max_iter"]:
                    model = Perceptron(
                        penalty=penalty,
                        alpha=alpha,
                        max_iter=max_iter
                    )
                    model.fit(X, y)
                    score = model.score(X, y)
                    if score > best_score:
                        best_score = score
                        best_model = model
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model