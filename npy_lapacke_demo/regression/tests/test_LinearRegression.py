__doc__ = """Tests for the LinearRegression class provided by _linreg.

.. codeauthor:: Derek Huang <djh458@stern.nyu.edu>
"""

from functools import partial
import numpy as np
import pytest

# pylint: disable=no-name-in-module
from .._linreg import LinearRegression


def test_defaults(lr_default):
    """Test that LinearRegression defaults are as expected.

    Parameters
    ----------
    lr_default : LinearRegression
        pytest fixture. See local conftest.py.
    """
    assert lr_default.fit_intercept == True
    assert lr_default.solver == "svd"


def test_init_sanity():
    """Test sanity of LinearRegression.__init__."""
    # no positional arguments are accepted
    with pytest.raises(TypeError, match="no positional"):
        LinearRegression(False, "qr")
    # only solvers allowed are qr, svd. no checking fit_intercept since any
    # Python expression will be converted into a boolean expression
    with pytest.raises(ValueError, match="solver must be one of"):
        LinearRegression(solver="magic_solver")


def test_members(lr_default):
    """Members of the LinearRegression instance are read-only.

    Parameters
    ----------
    lr_default : LinearRegression
        pytest fixture. See local conftest.py.
    """
    # functools.partial factory for pytest exception context manager
    mgr_gen = partial(pytest.raises, AttributeError, match="readonly")
    # no type checking done since attributes are read-only.
    with mgr_gen():
        lr_default.fit_intercept = (3 + 5 == 6)
    with mgr_gen():
        lr_default.solver = "magic_solver"


def test_unfitted_getset(lr_default):
    """Test LinearRegression getsets, not available before fitting.

    Parameters
    ----------
    lr_default : LinearRegression
        pytest fixture. See local conftest.py.
    """
    # functools.partial factory for pytest exception context manager
    mgr_gen = partial(pytest.raises, AttributeError, match="after fitting")
    # need each access in its own block
    with mgr_gen():
        lr_default.coef_
    with mgr_gen():
        lr_default.intercept_
    with mgr_gen():
        lr_default.rank_
    with mgr_gen():
        lr_default.singular_


def test_fit_sanity(lr_default, lr_single):
    """Test sanity of LinearRegression fit method.

    Parameters
    ----------
    lr_default : LinearRegression
        pytest fixture. See local conftest.py.
    lr_single : tuple
        pytest fixture. See local conftest.py.
    """
    # get input and output data from lr_single
    X, y, _, _ = lr_single
    # PRNG used to generator some random values. actual values don't matter so
    # we don't have to seed this particular Generator
    rng = np.random.default_rng()
    # number of features (columns of X)
    _, n_features = X.shape
    # input_ar and output_ar must not be empty
    with pytest.raises(ValueError, match="X must be nonempty"):
        lr_default.fit([], y)
    with pytest.raises(ValueError, match="y must be nonempty"):
        lr_default.fit(X, [])
    # functools.partial factory for pytest context manager
    mgr_gen = partial(pytest.raises, ValueError, match="X must have shape")
    # shape of X must be appropriate. try 0, 1, > 2 dims
    with mgr_gen():
        lr_default.fit(2, y)
    with mgr_gen():
        lr_default.fit(X[:, 0], y)
    with mgr_gen():
        lr_default.fit(rng.normal(size=(8, 8, 8)), y)
    # update factory so for checking shape of y (different matching message)
    mgr_gen = partial(pytest.raises, ValueError, match="y must have shape")
    # shape of y must be appropriate. try 0, > 2 dims
    with mgr_gen():
        lr_default.fit(X, 2)
    with mgr_gen():
        lr_default.fit(X, rng.normal(size=(8, 8, 8)))
    # number of rows and columns of X, y must match
    with pytest.raises(ValueError, match="number of rows of X, y must match"):
        lr_default.fit(X[:-1, :], y)
    # need tall and thin matrix (note X has 3 columns)
    with pytest.raises(ValueError, match="n_samples >= n_features required"):
        lr_default.fit(X[:(n_features - 1), :], y[:(n_features - 1)])


def test_qr_solver_single(lr_single):
    """Test QR solver on single-response toy problem.

    The intercept is not checked since intercept computation is separate.

    .. note::

       We don't use the scikit-learn implementation as a benchmark since it
       uses dgelsd, i.e. SVD with a divide-and-conquer method, which is
       (surprisingly) less accurate on this particular problem.

    Parameters
    ----------
    lr_single : tuple
        pytest fixture. See local conftest.py.
    """
    # get input + output data, coefficients, from lr_single
    X, y, coef_, _ = lr_single
    # fit LinearRegression and check that coef_ is close to actual
    lr = LinearRegression(solver="qr").fit(X, y)
    np.testing.assert_allclose(lr.coef_, coef_, rtol=1e-2)