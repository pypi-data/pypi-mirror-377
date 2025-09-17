import numpy as np
import scipy
from scipy.stats import chi
from sklearn.covariance import MinCovDet
import logging

class Regression(object):
    def __init__(self, outlier_threshold=0.975):
        self.use_mcd = False
        self.outlier_threshold = outlier_threshold

    def mean_and_covar(self, z):
        mu = np.mean(z, axis=0)
        covar = (z - mu).T @ (z - mu)
        return mu, covar

    def fit(self, x, y):
        z = np.hstack([x, y])
        if len(z) == 0:
            print(f"no data available", file=sys.stderr)
            return None

        n, x_dim = x.shape
        y_n, y_dim = y.shape
        assert n == y_n, "input x and y must have the name number of data points."
        assert n > 0, "number of data points must be greater than 0."

        shift_z = - z.min(axis=0) / (z.max(axis=0) - z.min(axis=0))
        scale_z = 1 / (z.max(axis=0) - z.min(axis=0))
        assert not np.any(np.isnan(scale_z)) and not np.any(np.isinf(scale_z)), "the input must not contain duplicate values"

        A = np.diag(scale_z)
        inv_A = np.diag(1/scale_z)
        inv_A_T = inv_A
        b = shift_z
        z = z @ A + b

        _mu, _covar = self.mean_and_covar(z)
        
        mu = (_mu - b) @ inv_A
        covar = inv_A_T @ _covar @ inv_A

        mu_x = mu[:x_dim]
        mu_y = mu[x_dim:]

        sigma_xx = covar[:x_dim, :x_dim]
        sigma_xy = covar[:x_dim, x_dim:]
        sigma_yy = covar[x_dim:, x_dim:]

        beta = scipy.linalg.pinvh(sigma_xx) @ sigma_xy
        sigma_e = sigma_yy - beta.T @ sigma_xx @ beta

        alpha = mu_y - beta.T @ mu_x

        self.beta = beta
        self.alpha = alpha
        y_hat = self.predict(x)
        r = y - y_hat

        self.d_r = ((r @ scipy.linalg.pinvh(sigma_e) * r).sum(1))**0.5
        self.d_x = (((x - mu_x) @ scipy.linalg.pinvh(sigma_xx) * (x - mu_x)).sum(1))**0.5
        assert not np.any(np.isnan(self.d_r)), "regression returned NaN results"

        self.outlier_r_threshold = scipy.stats.chi.ppf(self.outlier_threshold, df=y_dim)
        self.outlier_x_threshold = scipy.stats.chi.ppf(self.outlier_threshold, df=x_dim)

        self.outliers_r = self.d_r > self.outlier_r_threshold
        self.outliers_x = self.d_x > self.outlier_x_threshold
        self.outliers = self.outliers_r | self.outliers_x

        self.sigma_e = sigma_e
        self.sigma_xx = sigma_xx
    
    def predict(self, x):
        if self.beta is None or self.alpha is None:
            raise Exception("Must fit regressor to data before calling predict.")
        return x @ self.beta + self.alpha

class MCDRegression(Regression):
    def __init__(self, support_fraction=None, outlier_threshold=0.975):
        super().__init__(outlier_threshold=outlier_threshold)
        self.support_fraction = support_fraction
            
    def mean_and_covar(self, z):
        mcd = MinCovDet(support_fraction=self.support_fraction)
        mcd.fit(z)
        mu = mcd.location_
        covar = mcd.covariance_
        return mu, covar
