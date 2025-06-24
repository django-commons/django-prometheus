from timeit import default_timer


def Time():
    """Returns some representation of the current time.

    This wrapper is meant to take advantage of a higher time
    resolution when available. Thus, its return value should be
    treated as an opaque object. It can be compared to the current
    time with TimeSince().
    """
    return default_timer()


def TimeSince(t):
    """Compares a value returned by Time() to the current time.

    Returns:
      the time since t, in fractional seconds.

    """
    return default_timer() - t


def PowersOf(logbase, count, lower=0, include_zero=True):
    """Returns a list of count powers of logbase (from logbase**lower)."""
    if not include_zero:
        return [logbase**i for i in range(lower, count + lower)]
    return [0] + [logbase**i for i in range(lower, count + lower)]
