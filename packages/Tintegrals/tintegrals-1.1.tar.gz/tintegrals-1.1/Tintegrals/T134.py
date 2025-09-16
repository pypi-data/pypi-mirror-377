from functools import lru_cache
from sympy import polylog, N
from .config import cond, Number
from .OneLoop import B0fin, B0del
from mpmath import mp, sqrt, pi, log, re

@lru_cache(maxsize=150)
def Li2(x : Number) -> Number:
    """ Computes $\\rm{Li}_2(x)$. """
    with mp.workdps(mp.dps):
        return mp.mpc(N(polylog(2, x), mp.dps))


@lru_cache(maxsize=150)
def T134uv2(m1: Number, m2: Number, m3: Number) -> Number:
    """Computes the double UV poles ($\\propto 1/\\epsilon^2$) of the T134 integral.

    Args:
        m1: first mass
        m2: second mass
        m3: third mass

    Returns:
        value of double UV pole
    """
    try:
        return 0.5 * (m1**2 + m2**2 + m3**2)
    except Exception as e:
        raise Exception(
            f"There was an error when evaluating the T134uv2 integral with masses {m1}, {m2}, {m3} from {e}"
        )


@lru_cache(maxsize=150)
def T134uv1(m1: Number, m2: Number, m3: Number, mudim=None) -> Number:
    """Computes the single UV pole ($\\propto 1/\\epsilon$) of the T134 integral.

    Args:
        m1: first mass
        m2: second mass
        m3: third mass

    Returns:
        value of single UV pole
    """
    try:
        m1sq = m1**2
        m2sq = m2**2
        m3sq = m3**2
        return (
            0.5 * (m1sq + m2sq + m3sq)
            + m1sq * B0fin(0, 0, m1sq, mudim)
            + m2sq * B0fin(0, 0, m2sq, mudim)
            + m3sq * B0fin(0, 0, m3sq, mudim)
        )
    except Exception as e:
        raise Exception(
            f"There was an error when evaluating the T134uv1 integral with masses {m1}, {m2}, {m3} from {e}"
        )


@lru_cache(maxsize=150)
def T134fin(m1: Number, m2: Number, m3: Number, mudim=None) -> Number:
    """Computes the UV finite part of the T134 integral.

    Args:
        m1: first mass
        m2: second mass
        m3: third mass

    Returns:
        value of the finite part
    """
    try:
        m1sq = m1**2
        m2sq = m2**2
        m3sq = m3**2
        return (
            m1sq
            + m2sq
            + m3sq
            + m1sq * B0del(0, 0, m1sq, mudim)
            + m2sq * B0del(0, 0, m2sq, mudim)
            + m3sq * B0del(0, 0, m3sq, mudim)
            + m1sq * B0fin(0, 0, m1sq, mudim)
            + m2sq * B0fin(0, 0, m2sq, mudim)
            + m3sq * B0fin(0, 0, m3sq, mudim)
            + 0.5
            * (
                m1sq * B0fin(0, 0, m1sq, mudim) ** 2
                + m2sq * B0fin(0, 0, m2sq, mudim) ** 2
                + m3sq * B0fin(0, 0, m3sq, mudim) ** 2
            )
            + PhiCyc(m1sq, m2sq, m3sq)
        )
    except Exception as e:
        raise Exception(
            f"There was an error when evaluating the T134fin integral with masses {m1}, {m2}, {m3} from {e}"
        )


@lru_cache(maxsize=150)
def PhiCyc(m1sq: Number, m2sq: Number, m3sq: Number) -> Number:
    """Computes cyclic Phi function entering T134fin

    Args:
        m1sq: first squared mass
        m2sq: second squared mass
        m3sq: third squared mass

    Returns:
        value of PhyCyc
    """
    m1, m2, m3 = sqrt(m1sq), sqrt(m2sq), sqrt(m3sq)
    if cond(m1, 0) and cond(m2, 0) and cond(m3, 0):
        return 0
    elif cond(m1, 0) and cond(m2, 0):
        return m3sq * pi**2 / 6
    elif cond(m1, 0) and cond(m3, 0):
        return m2sq * pi**2 / 6
    elif cond(m2, 0) and cond(m3, 0):
        return m1sq * pi**2 / 6
    elif cond(m1, 0):
        return re(m2sq * Li2((m2sq - m3sq) / m2sq) + m3sq * Li2((m3sq - m2sq) / m3sq))
    elif cond(m2, 0):
        return re(m1sq * Li2((m1sq - m3sq) / m1sq) + m3sq * Li2((m3sq - m1sq) / m3sq))
    elif cond(m3, 0):
        return re(m1sq * Li2((m1sq - m2sq) / m1sq) + m2sq * Li2((m2sq - m1sq) / m2sq))
    else:
        # use log and sqrt here to avoid issues with imaginary R
        R = sqrt(
            m1sq**2
            + m2sq**2
            + m3sq**2
            - 2 * m1sq * m2sq
            - 2 * m2sq * m3sq
            - 2 * m3sq * m1sq
        )
        res = re(
            -0.5 * m1sq * log(m1sq / m2sq) * log(m1sq / m3sq)
            - 0.5 * m2sq * log(m2sq / m3sq) * log(m2sq / m1sq)
            - 0.5 * m3sq * log(m3sq / m1sq) * log(m3sq / m2sq)
            + R
            * (
                pi**2 / 6
                - 0.5 * log(m1sq / m3sq) * log(m2sq / m3sq)
                + log((m1sq - m2sq + m3sq - R) / (2 * m3sq))
                * log((m2sq - m1sq + m3sq - R) / (2 * m3sq))
                - Li2((m1sq - m2sq + m3sq - R) / (2 * m3sq))
                - Li2((m2sq - m1sq + m3sq - R) / (2 * m3sq))
            )
        )
        return re(res)
