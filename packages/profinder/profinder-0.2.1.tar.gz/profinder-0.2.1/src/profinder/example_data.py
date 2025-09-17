from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike


def get_example_data() -> ArrayLike:
    """
    Load example pressure data from the tests/data directory.
    Returns:
        ArrayLike: 1D array of pressure values.
    """
    csv_path = str(
        Path(__file__).parent.parent.parent / "tests" / "data" / "rbr_pressure.csv"
    )
    pressure = np.loadtxt(csv_path, delimiter=",", skiprows=2)
    return pressure


def synthetic_glider_pressure(
    n_points: int = 200,
    max_p: float = 500.0,
    intermediate_p: float = 200.0,
    n_cycles: int = 5,
) -> np.ndarray:
    """
    Generate synthetic ocean glider pressure data with a sawtooth pattern.

    The pressure profile starts at 0 dbar, descends to `max_p`, then oscillates
    between `max_p` and `intermediate_p` for `n_cycles` cycles, and finally ascends
    back to 0 dbar.

    Parameters
    ----------
    n_points : int, optional
        Total number of points in the generated profile (default: 1000).
    max_p : float, optional
        Maximum pressure value in dbar (default: 500.0).
    intermediate_p : float, optional
        Intermediate pressure value in dbar for the sawtooth pattern (default: 200.0).
    n_cycles : int, optional
        Number of sawtooth cycles between `max_p` and `intermediate_p` (default: 5).

    Returns
    -------
    pressure : ndarray
        1D array of synthetic pressure values.
    """
    total_distance = 2 * max_p + 2 * n_cycles * (max_p - intermediate_p)
    delta_p = total_distance / n_points

    yos = [np.arange(0, max_p, delta_p)]  # Descent is first part
    for _ in range(n_cycles):
        up = np.arange(max_p, intermediate_p, -delta_p)
        down = np.arange(intermediate_p, max_p, delta_p)
        yos.append(up)
        yos.append(down)

    yos.append(np.arange(max_p, 0, -delta_p))
    pressure = np.concatenate(yos)
    return pressure
