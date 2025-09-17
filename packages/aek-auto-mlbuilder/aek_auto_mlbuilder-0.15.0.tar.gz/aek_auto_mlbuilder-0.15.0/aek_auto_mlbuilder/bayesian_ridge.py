from sklearn.linear_model import BayesianRidge
from .base import BaseModel

class BayesianRidgeModel(BaseModel):
    """
    Bayesian Ridge regression model
    brute force search is being used
    """

    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "alpha_1": [1e-6, 1e-5, 1e-4],
            "alpha_2": [1e-6, 1e-5, 1e-4],
            "lambda_1": [1e-6, 1e-5],
            "lambda_2": [1e-6, 1e-5],
            "max_iter": [300, 500]
        }

    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        for alpha_1 in self.param_grid["alpha_1"]:
            for alpha_2 in self.param_grid["alpha_2"]:
                for lambda_1 in self.param_grid["lambda_1"]:
                    for lambda_2 in self.param_grid["lambda_2"]:
                        for max_iter in self.param_grid["max_iter"]:
                            model = BayesianRidge(
                                alpha_1=alpha_1,
                                alpha_2=alpha_2,
                                lambda_1=lambda_1,
                                lambda_2=lambda_2,
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