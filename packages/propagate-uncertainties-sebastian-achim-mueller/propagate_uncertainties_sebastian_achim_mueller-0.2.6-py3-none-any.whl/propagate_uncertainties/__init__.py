"""
Propagate Uncertainties
-----------------------

Propagate the absolute uncertainties of your variables in simple expressions.
"""

import numpy as np
from .version import __version__


def auN(dfdx, x_au):
    """
    Absolute uncertainty of function f(x1, x2, ..., xN), assuming the
    N parameters x1 to xN are not correlated.

    Parameters
    ----------
    dfdx : array of floats, length N
        Derivatives of f w.r.t. x1 to xN.
    x_au : array of floats, length N
        Absolute uncertainties of x1 to xN.
    Returns
    -------
    Absolute uncertainty : float
    """
    dfdx = np.array(dfdx)
    x_au = np.array(x_au)
    assert len(dfdx) == len(x_au)
    S = 0.0
    for i in range(len(x_au)):
        S += (dfdx[i] * x_au[i]) ** 2.0
    return np.sqrt(S)


def add(x, x_au, y, y_au):
    """
    Add x to y.

    Parameters
    ----------
    x : float
        Value of x.
    x_au : float
        Absolute uncertainty of x.
    y : float
        Value of y.
    y_au : float
        Absolute uncertainty of y.

    Returns
    -------
    x + y and absolute uncertainty : tuple(float, float)

    Derivative
    ----------
    f(x,y) = x + y
    df/dx = 1
    df/dy = 1
    """
    dfdx = 1.0
    dfdy = 1.0
    return x + y, auN(dfdx=[dfdx, dfdy], x_au=[x_au, y_au])


def multiply(x, x_au, y, y_au):
    """
    Multiply x by y.

    Parameters
    ----------
    x : float
        Value of x.
    x_au : float
        Absolute uncertainty of x.
    y : float
        Value of y.
    y_au : float
        Absolute uncertainty of y.

    Returns
    -------
    x * y and abs. uncertainty : tuple(float, float)

    Derivative
    ----------
    f(x,y) = x * y
    df/dx = y
    df/dy = x
    """
    dfdx = y
    dfdy = x
    return x * y, auN(dfdx=[dfdx, dfdy], x_au=[x_au, y_au])


def divide(x, x_au, y, y_au):
    """
    Divide x by y.

    Parameters
    ----------
    x : float
        Value of x.
    x_au : float
        Absolute uncertainty of x.
    y : float
        Value of y.
    y_au : float
        Absolute uncertainty of y.

    Returns
    -------
    x / y and abs. uncertainty : tuple(float, float)

    derivative
    ----------
    f(x,y) = x * y^{-1}
    df/dx = y^{-1}
    df/dy = -1x * y^{-2}
    """
    dfdx = y ** (-1)
    dfdy = -1.0 * x * y ** (-2)
    return x / y, auN(dfdx=[dfdx, dfdy], x_au=[x_au, y_au])


def prod(x, x_au):
    """
    Multilpy all elements in x

    Parameters
    ----------
    x : array of N floats
        Values x.
    x_au : array of N floats
        Absolute uncertainties of x.

    Returns
    -------
    Product and abs. uncertainty : tuple(float, float)
    """
    x = np.array(x)
    x_au = np.array(x_au)
    assert len(x) == len(x_au)
    P = np.prod(x)
    dfdxs = []
    for i in range(len(x)):
        mask_i = np.ones(len(x), dtype=bool)
        mask_i[i] = False
        dfdxi = np.prod(x[mask_i])
        dfdxs.append(dfdxi)

    Pau = auN(dfdx=dfdxs, x_au=x_au)
    return P, Pau


def sum(x, x_au):
    """
    Add all elements in x

    Parameters
    ----------
    x : array of N floats
        Values x.
    x_au : array of N floats
        Absolute uncertainties of x.

    Returns
    -------
    Sum and abs. uncertainty : tuple(float, float)
    """
    x = np.array(x)
    x_au = np.array(x_au)
    assert len(x) == len(x_au)
    S = np.sum(x)
    dfdxs = np.ones(len(x))
    S_au = auN(dfdx=dfdxs, x_au=x_au)
    return S, S_au


def sum_axis0(x, x_au):
    """
    Add all elements in x along an axis.

    Parameters
    ----------
    x : array of (N, M) floats
        Values x.
    x_au : array of (N, M) floats
        Absolute uncertainties of x.

    Returns
    -------
    Sum and abs. uncertainty : tuple(array of M floats, array of M floats)
    """
    N = len(x)
    assert N >= 1
    assert N == len(x_au)
    M = len(x[0])

    # assert rectangular
    for n in range(N):
        assert M == len(x[n])
        assert M == len(x_au[n])

    s = tmp = np.zeros(M)
    s_au = tmp = np.zeros(M)
    for m in range(M):
        tmp = np.zeros(N)
        tmp_au = np.zeros(N)

        for n in range(N):
            tmp[n] = x[n][m]
            tmp_au[n] = x_au[n][m]

        s[m], s_au[m] = sum(x=tmp, x_au=tmp_au)

    return s, s_au


def integrate(f, f_au, x_bin_edges):
    """
    Integrate function f(x).

    Parameters
    ----------
    f : array of N floats
        Values of f(x).
    f_au : array of N floats
        Absolute uncertainties of f(x).
    x_bin_edges : array of floats
        Edges of bins in x.

    Returns
    -------
    Integral and uncertainty : tuple(float, float)
    """
    f = np.array(f)
    f_au = np.array(f_au)
    num_bins = len(x_bin_edges) - 1
    assert len(f) == len(f_au)
    assert len(f) == num_bins

    a = np.zeros(num_bins)
    a_au = np.zeros(num_bins)
    for i in range(num_bins):
        step = x_bin_edges[i + 1] - x_bin_edges[i]
        assert step >= 0.0
        a[i], a_au[i] = multiply(x=f[i], x_au=f_au[i], y=step, y_au=0.0)
    return sum(x=a, x_au=a_au)


def sqrt(x, x_au):
    """
    ASquare root of x.

    Parameters
    ----------
    x : float
        Value of x.
    x_au : float
        Absolute uncertainty of x.

    Returns
    -------
    x + y and absolute uncertainty : tuple(float, float)

    Derivative
    ----------
    f(x) = x ** (1/2)
    df/dx = (1/2) * x ** (-1/2)
    """
    return np.sqrt(x), auN(dfdx=[0.5 * x ** (-0.5)], x_au=[x_au])


def max(x, x_au):
    """
    Find the max value in x.

    Parameters
    ----------
    x : float
        Value of x.
    x_au : float
        Absolute uncertainty of x.

    Returns
    -------
    max(x) and corresponding x_au : (float, float)
    """
    am = np.argmax(x)
    return x[am], x_au[am]


def hypot(x, x_au, y, y_au):
    """
    Hypothenous of x and y.

    Parameters
    ----------
    x : float
        Value of x.
    x_au : float
        Absolute uncertainty of x.
    y : float
        Value of y.
    y_au : float
        Absolute uncertainty of y.

    Returns
    -------
    sqrt(x**2 + y**2) and abs. uncertainty : tuple(float, float)

    derivative
    ----------
    f(x, y) = (x^2 + y^2)^{1/2}

    outer
    g(w) = w^{1/2}
    dg/dw = -1/2 w^{-1/2}

    inner
    u(x) = x^2 + y^2
    du/dx = 2x
    du/dy = 2y

    df/dx = -1/2 (x^2 + y^2)^{-1/2} * 2x
    df/dy = -1/2 (x^2 + y^2)^{-1/2} * 2y

    df/dx = - x(x^2 + y^2)^{-1/2}
    df/dy = - y(x^2 + y^2)^{-1/2}
    """
    Q = x**2 + y**2

    dfdx = -x * Q ** (-1 / 2)
    dfdy = -y * Q ** (-1 / 2)

    return Q ** (1 / 2), auN(dfdx=[dfdx, dfdy], x_au=[x_au, y_au])
