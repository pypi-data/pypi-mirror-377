import numpy as np

class GDLinearRegression:
    """
    Linear Regression using Gradient Descent.

    Parameters
    ----------
    learning_rate : float, default=0.1
        Step size for gradient descent.
    iterations : int, default=1000
        Maximum number of iterations.
    tolerance : float, default=1e-8
        Minimum change in parameters to stop early.
    """

    def __init__(self, learning_rate=0.1, iterations=1000, tolerance=1e-8):
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.tolerance = tolerance
        self.weights = None
        self.bias = None

    def fit(self, X, y):
        """
        Fit the model to the data using gradient descent.
        """
        X = np.array(X)
        y = np.array(y).reshape(-1)

        n, f = X.shape
        self.bias = 0
        self.weights = np.zeros(f)

        for _ in range(self.iterations):
            y_pred = X @ self.weights + self.bias
            error = y_pred - y

            db = 2 / n * np.sum(error)
            dw = 2 / n * (X.T @ error)

            old_weights = self.weights.copy()
            old_bias = self.bias

            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

            # Early stopping
            if (np.linalg.norm(self.weights - old_weights) < self.tolerance 
                and abs(self.bias - old_bias) < self.tolerance):
                break

    def predict(self, X):
        """
        Predict target values for given data.
        """
        return np.array(X) @ self.weights + self.bias

    def get_params(self):
        """
        Get learned weights and bias.
        """
        return self.weights, self.bias

    def score(self, X, y):
        """
        Return R^2 score (coefficient of determination).
        """
        y = np.array(y)
        y_pred = self.predict(X)
        ss_total = np.sum((y - np.mean(y))**2)
        ss_res = np.sum((y - y_pred)**2)
        return 1 - ss_res / ss_total