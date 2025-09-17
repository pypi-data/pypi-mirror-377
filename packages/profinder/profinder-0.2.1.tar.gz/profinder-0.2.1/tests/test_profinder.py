import numpy as np
from scipy.integrate import solve_ivp

from profinder import find_profiles, get_example_data, synthetic_glider_pressure


def test_get_example_data() -> None:
    data = get_example_data()
    assert isinstance(data, np.ndarray)
    assert np.isfinite(data).all()


def test_synthetic_glider_pressure() -> None:
    pressure = synthetic_glider_pressure()
    assert pressure.shape == (200,)


def test_find_profiles() -> None:
    pressure = get_example_data()
    peaks_kwargs = {"height": 15, "distance": 200, "width": 200, "prominence": 15}
    segments = find_profiles(pressure, peaks_kwargs=peaks_kwargs, min_pressure=3.0)
    assert len(segments) == 12

    segments = find_profiles(
        pressure, peaks_kwargs=peaks_kwargs, min_pressure=3.0
    )  # , apply_speed_threshold=True, time=np.arange(0, pressure.size/32, 1/32))
    assert len(segments) == 12

    pressure = synthetic_glider_pressure(
        n_points=200, max_p=500.0, intermediate_p=200.0, n_cycles=5
    )
    peaks_kwargs = {"height": 100, "distance": 5, "width": 5, "prominence": 100}
    segments = find_profiles(pressure, apply_smoothing=False, peaks_kwargs=peaks_kwargs)
    assert len(segments) == 6

    # Handling missing
    np.random.seed(14123)

    pressure = synthetic_glider_pressure(
        n_points=1000, max_p=500.0, intermediate_p=200.0, n_cycles=5
    )

    # Add NaN
    pressure[::8] = np.nan
    pressure[::9] = np.nan
    indices = np.random.choice(pressure.size, 50, replace=False)
    pressure[indices] = np.nan

    peaks_kwargs = {"height": 100, "distance": 5, "width": 5, "prominence": 100}
    segments = find_profiles(
        pressure,
        apply_smoothing=False,
        peaks_kwargs=peaks_kwargs,
        missing="drop",
    )
    assert len(segments) == 6


def test_velocity() -> None:
    # Crazy test using a fake VMP
    # Physical parameters
    mv = 14.0  # mass VMP (kg)
    mw = 11.0  # mass water displaced (kg)
    L = 1  # hull length (m)
    g = -9.81  # gravity (m/s^2)
    Cd = 3  # drag coefficient (-)
    Tmax = 120.0  # max tension (N)
    tension_tau = 8.0  # tension ramp-up time constant (s)
    tension_on = 100.0  # time when tension starts (s)

    # Time parameters
    total_time = 200  # (s)
    dt = 1 / 60  # Interpolation time step 60 Hz

    def instrument_ode(t, y):
        z, w = y
        # Tension ramps up after tension_on
        if t < tension_on:
            T = 0.0
        else:
            T = Tmax * (1 - np.exp(-(t - tension_on) / tension_tau))
        dwdt = g * (mv - mw) / mv - (mw / mv) * (Cd / L) * w * np.abs(w) + T / mv
        return [w, dwdt]

    class HitSurface:
        terminal: bool = True
        direction: int = 1  # Only trigger when crossing zero from below

        def __call__(self, t: float, y: np.ndarray) -> float:  # type: ignore[override]
            return float(y[0])

    hit_surface = HitSurface()

    sol = solve_ivp(
        instrument_ode,
        [0, total_time],
        [0.0, 0.0],  # Initial condition [z, w]
        events=hit_surface,
        vectorized=False,
    )

    t_uniform = np.arange(0, sol.t[-1], dt)
    z = np.interp(t_uniform, sol.t, sol.y[0])
    w = np.interp(t_uniform, sol.t, sol.y[1])
    # t = t_uniform

    segments_speed = find_profiles(
        -z, apply_speed_threshold=True, velocity=-w, min_speed=0.9, direction="down"
    )
    assert len(segments_speed) == 1
