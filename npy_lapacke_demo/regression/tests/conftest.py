__doc__ = """pytest test fixtures for regression.tests subpackage.

.. codeauthor:: Derek Huang <djh458@stern.nyu.edu>
"""

import numpy as np
import pytest
from sklearn.datasets import make_regression

# pylint: disable=no-name-in-module
from .._linreg import LinearRegression


@pytest.fixture
def lr_default():
    """LinearRegression instance with default parameters.

    Returns
    -------
    LinearRegression
        fit_intercept=False, solver="svd" are the defaults.
    """
    return LinearRegression()


@pytest.fixture(scope="session")
def lr_single(global_seed):
    """Toy single-output linear regression problem.

    Problem has 1000 data points with 5 features and a single output. All
    features are informative and are standard Gaussian, identity covariance.
    Standard deviation of the Gaussian noise applied to the response is 0.1.
    The intercept applied to each response is 7.

    Parameters
    ----------
    global_seed : int
        pytest fixture. See top-level package conftest.py.

    Returns
    -------
    X : numpy.ndarray
        Input matrix shape (1000, 5)
    y : numpy.ndarray
        Response vector shape (1000,)
    coef : numpy.ndarray
        True linear coefficients, shape (5,)
    bias : float
        The bias term of the model
    """
    bias = 7
    X, y, coef = make_regression(
        n_samples=1000, n_features=5, n_informative=5, bias=bias,
        noise=0.1, coef=True, random_state=global_seed
    )
    return X, y, coef, bias


@pytest.fixture(scope="session")
def lr_multi(global_seed):
    """Toy multi-output linear regression problem.

    Problem has 1000 data points with 5 features and 3 outputs. All features
    are informative and are standard Gaussian, identity covariance. Standard
    deviation of the Gaussian noise applied to the response is 0.1.
    The intercept applied to each response is [7, 4, 5].

    Parameters
    ----------
    global_seed : int
        pytest fixture. See top-level package conftest.py.

    Returns
    -------
    X : numpy.ndarray
        Input matrix shape (1000, 5)
    y : numpy.ndarray
        Response vector shape (1000, 3)
    coef : numpy.ndarray
        True linear coefficients, shape (3, 5), i.e. (n_targets, n_features).
        Transpose the output from sklearn.datasets.make_regression in order to
        allow comparing with LinearRegression.coef_ without transpose.
    bias : float
        The bias term of the model
    """
    bias = np.array([7, 4, 5])
    X, y, coef = make_regression(
        n_features=5, n_informative=5, n_targets=3, bias=bias,
        noise=0.1, coef=True, random_state=global_seed
    )
    return X, y, coef.T, bias