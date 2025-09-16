from functools import lru_cache
from .config import cond, Number, _mudim, getMudim
from mpmath import log, pi

@lru_cache(maxsize=150)
def A0fin(msq: Number, mudim = None) -> Number:
    """ Computes the UV finite part of the A0 integral.

    Args:
        msq: squared mass
        mudim: squared renormalization scale (if `None`, the global value is used)

    Returns:
        value of the finite part
    """
    if mudim is None:
        mudim = getMudim()

    try:
        if cond(msq, 0):
            return 0.0
        else:
            return msq*(1 - log(msq/mudim))
    except Exception as e:
        raise Exception(f"There was an error when evaluating the A0fin integral with arguments {msq} from {e}")


@lru_cache(maxsize=150)
def B0fin(p2: Number, m1sq: Number, m2sq: Number, mudim = None) -> Number:
    """ Computes the UV finite part of the B0 integral.
    **Only implemented for zero momentum!**

    Args:
        p2: squared momentum
        m1sq: first squared mass
        m2sq: second squared mass
        mudim: squared renormalization scale (if `None`, the global value is used)

    Returns:
        value of the finite part
    """
    if mudim is None:
        from .config import _mudim
        mudim = _mudim

    try:
        if p2 != 0:
            raise ValueError("B0fin only implemented for p2 = 0")

        if cond(m1sq, 0) and cond(m2sq, 0):
            return 0
        elif cond(m1sq, 0):
            return 1 - log(m2sq/mudim)
        elif cond(m2sq, 0):
            return 1 - log(m1sq / mudim)
        elif cond(m1sq, m2sq):
            return -log(m1sq / mudim)
        else:
            return (A0fin(m1sq, mudim) - A0fin(m2sq, mudim)) / (m1sq - m2sq)
    except Exception as e:
        raise Exception(f"There was an error when evaluating the B0fin integral with arguments {p2}, {m1sq}, {m2sq} from {e}")


@lru_cache(maxsize=150)
def B0del(p2: Number, m1sq: Number, m2sq: Number, mudim = None) -> Number:
    """ Computes the $\\epsilon^1$ part of the B0 integral.
    **Only implemented for zero momentum!**

    Args:
        p2: squared momentum
        m1sq: first squared mass
        m2sq: second squared mass
        mudim: squared renormalization scale (if `None`, the global value is used)

    Returns:
        value of the $\\epsilon^1$ part if `inclB0del == True`; `0` if `inclB0del == False`
    """
    from .config import _inclB0del

    if mudim is None:
        from .config import _mudim
        mudim = _mudim

    try:
        if not _inclB0del:
            return 0

        if p2 != 0:
            raise ValueError("B0del only implemented for p2 = 0")

        if cond(m1sq, 0) and cond(m2sq, 0):
            return 0
        elif cond(m1sq, 0):
            return 0.5 + pi**2 / 12 + 0.5 * (1 - log(m2sq / mudim)) ** 2
        elif cond(m2sq, 0):
            return 0.5 + pi**2 / 12 + 0.5 * (1 - log(m1sq / mudim)) ** 2
        elif cond(m1sq, m2sq):
            return pi**2 / 12 + 0.5 * log(m1sq / mudim) ** 2
        else:
            return (
                1
                / (m1sq - m2sq)
                * (
                    m1sq * (0.5 + pi**2 / 12 + 0.5 * (1 - log(m1sq / mudim)) ** 2)
                    - m2sq
                    * (0.5 + pi**2 / 12 + 0.5 * (1 - log(m2sq / mudim)) ** 2)
                )
            )
    except Exception as e:
        raise Exception(f"There was an error when evaluating the B0del integral with arguments {p2}, {m1sq}, {m2sq} from {e}")


@lru_cache(maxsize=150)
def C0fin(m1sq: Number, m2sq: Number, m3sq: Number, mudim = None) -> Number:
    """ Computes the UV finite part of the B0 integral.
    **Only implemented for zero momentum!**

    Args:
        p2: squared momentum
        m1sq: first squared mass
        m2sq: second squared mass
        m3sq: third squared mass
        mudim: squared renormalization scale (if `None`, the global value is used

    Returns:
        value of the finite part
    """
    if mudim is None:
        from .config import _mudim
        mudim = _mudim

    try:
        if cond(m1sq, 0):
            # raise ValueError("C0fin only implemented for m1sq != 0")
            if cond(m2sq,m3sq):
                return -1/m3sq
            elif cond(m2sq,0):
                return 1 / m3sq - log(m3sq / mudim) / m3sq
            else: 
                return -log(m2sq/m3sq)/(m2sq - m3sq)
        elif cond(m2sq, 0):
            # raise ValueError("C0fin only implemented for m2sq != 0")
            if cond(m1sq,m3sq):
                return -1/m3sq
            elif cond(m3sq,0):
                return 1 / m1sq - log(m1sq / mudim) / m1sq
            else: 
                return -log(m1sq/m3sq)/(m1sq - m3sq)            
        elif cond(m3sq, 0):
            # raise ValueError("C0fin only implemented for m3sq != 0")
            if cond(m1sq,m2sq):
                return -1/m2sq
            elif cond(m1sq,0):
                return 1 / m2sq - log(m2sq / mudim) / m2sq
            else: 
                return -log(m1sq/m2sq)/(m1sq - m2sq)            
        elif cond(m1sq, m2sq) and cond(m2sq, m3sq):
            return -1/(2*m1sq)
        elif cond(m1sq, m2sq):
            return (
                -log(m1sq / mudim)
                - (A0fin(m1sq, mudim) - A0fin(m3sq, mudim)) / (m1sq - m3sq)
            ) / (m1sq - m3sq)
        elif cond(m2sq, m3sq):
            return (
                -log(m2sq / mudim)
                - (A0fin(m2sq, mudim) - A0fin(m1sq, mudim)) / (m2sq - m1sq)
            ) / (m2sq - m1sq)
        else:
            return (
                (A0fin(m1sq, mudim) - A0fin(m2sq, mudim)) / (m1sq - m2sq)
                - (A0fin(m1sq, mudim) - A0fin(m3sq, mudim)) / (m1sq - m3sq)
            ) / (m2sq - m3sq)
    except Exception as e:
        raise Exception(f"There was an error when evaluating the C0fin integral with arguments {m1sq}, {m2sq}, {m3sq} from {e}")
