from sklearn.svm import NuSVC
from .base import BaseModel

class NuSVCModel(BaseModel):
    """
    NuSVC classification model
    brute force search is being used
    """
    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "nu": [0.25, 0.5, 0.75],
            "kernel": ["linear", "poly", "rbf", "sigmoid"],
            "C": [0.1, 1, 10]
        }
    
    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        for nu in self.param_grid["nu"]:
            for kernel in self.param_grid["kernel"]:
                for C in self.param_grid["C"]:
                    model = NuSVC(
                        nu=nu,
                        kernel=kernel,
                        C=C
                    )
                    model.fit(X, y)
                    score = model.score(X, y)
                    if score > best_score:
                        best_score = score
                        best_model = model
        
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model
    