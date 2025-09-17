---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
---

# profinder

`profinder` is a collection of algorithms for finding profiles in ocean pressure data. 

# Usage

```{code-cell}
:tags: [hide-cell]
# Ignore this (it is helpful for the local docs build.)
import profinder
import importlib
importlib.reload(profinder)
```

Currently the package contains just one algorithm for identifying profiles, called `find_profiles`, which you can import from the main package. 

```{code-cell}
from profinder import get_example_data, find_profiles
```

The function operates on pressure or depth time series data with no explicit need for time information (it assumes uniformly spaced data) e.g.

```{code-cell}
pressure = get_example_data()
print(pressure[:10])
```

It will identify up and down pairs in the data. Each up or down part in a profile is defined by start and end indexes, `(down_start, down_end, up_start, up_end)`. If you are not applying a speed threshold, then down_end and up_start will be identical.

```{code-cell}
segments = find_profiles(pressure)
print(segments)
```

The default parameters may need to be changed to find the profiles properly. Note that some smaller profiles are not identified in the following example.

```{code-cell}
import plotly.graph_objects as go
import numpy as np
from IPython.display import HTML

segments = np.asarray(segments)
start = segments[:, 0]
peak = segments[:, 1]
end = segments[:, 3]
x = np.arange(0, pressure.size)
cut = slice(0, None, 8)  # reduce data for plotting

fig = go.Figure()
fig.add_trace(go.Scatter(x=x[cut], y=pressure[cut], mode="lines", name="pressure"))
fig.add_trace(go.Scatter(x=x[start], y=pressure[start], mode="markers", name="start", marker_color="green"))
fig.add_trace(go.Scatter(x=x[peak], y=pressure[peak], mode="markers", name="peak", marker_color="blue"))
fig.add_trace(go.Scatter(x=x[end], y=pressure[end], mode="markers", name="end", marker_color="red"))
fig.update_layout(yaxis_title="Pressure (dbar)", xaxis_title="Data index (-)", yaxis_autorange="reversed")
HTML(fig.to_html(include_plotlyjs='cdn'))
```

`find_profiles` accepts a number of arguments for fine-tuning profile identification. Underneath the hood it is applying `scipy` functions [`find_peaks`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html) and [`savgol_filter`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html). Consequently, most of the arguments to `find_profiles` alter the behaviour of these functions and it is helpful to be familiar with their operation. 

The profile finding algorithm roughly follows the steps below. The action of each step is modified by a set of arguments. 

| Step    | Arguments modifying the step |
| -------- | ------- |
| 1. Pressure data are smoothed to remove noise (optional) | `apply_smoothing`, `window_length`, `polyorder` |
| 2. Pressure maxima are identified | `peaks_kwargs` |
| 3. Pressure minima are identified, equivalent to searching for maxima in negative pressure | `troughs_kwargs` |
| 4. Segments are cleaned up to get better estimates of where the profiles start and end | `min_pressure`, `run_length`, `min_pressure_change`,  `apply_speed_threshold`, `time`, `velocity`, `min_speed`, `direction` | 

The results from the example above can be improved by modifying the peak finding steps. We identify by eye that some smaller peaks are missed, suggesting that we should decrease the minimum height and prominance thresholds when finding peaks and troughs. 

```{code-cell}
peaks_kwargs = {"height": 15, "distance": 200, "width": 200, "prominence": 15}

segments = find_profiles(pressure, apply_smoothing=True, peaks_kwargs=peaks_kwargs)
segments = np.asarray(segments)
start = segments[:, 0]
peak = segments[:, 1]
end = segments[:, 3]

fig = go.Figure()
fig.add_trace(go.Scatter(x=x[cut], y=pressure[cut], mode="lines", name="pressure"))
fig.add_trace(go.Scatter(x=x[start], y=pressure[start], mode="markers", name="start", marker_color="green"))
fig.add_trace(go.Scatter(x=x[peak], y=pressure[peak], mode="markers", name="peak", marker_color="blue"))
fig.add_trace(go.Scatter(x=x[end], y=pressure[end], mode="markers", name="end", marker_color="red"))
fig.update_layout(yaxis_title="Pressure (dbar)", xaxis_title="Data index (-)", yaxis_autorange="reversed")
HTML(fig.to_html(include_plotlyjs='cdn'))
```

We can also set a minimum pressure threshold for profiles to start and end. Note that this may not line up exactly with expectations when applying smoothing, since the smoothed pressure is used to identify points not meeting the threshold. 

```{code-cell}
segments = find_profiles(pressure, window_length=9, apply_smoothing=True, min_pressure=3.0, peaks_kwargs=peaks_kwargs)
segments = np.asarray(segments)
start = segments[:, 0]
peak = segments[:, 1]
end = segments[:, 3]

fig = go.Figure()
fig.add_trace(go.Scatter(x=x[cut], y=pressure[cut], mode="lines", name="pressure"))
fig.add_trace(go.Scatter(x=x[start], y=pressure[start], mode="markers", name="start", marker_color="green"))
fig.add_trace(go.Scatter(x=x[peak], y=pressure[peak], mode="markers", name="peak", marker_color="blue"))
fig.add_trace(go.Scatter(x=x[end], y=pressure[end], mode="markers", name="end", marker_color="red"))
fig.update_layout(yaxis_title="Pressure (dbar)", xaxis_title="Data index (-)", yaxis_autorange="reversed")
HTML(fig.to_html(include_plotlyjs='cdn'))
```

# Glider example

Gliders return decimated (low resolution) real-time pressure data and may undertake complex dive plans. The example below illustrates how to extract profiles in this case. 

```{code-cell}
from profinder import synthetic_glider_pressure

pressure = synthetic_glider_pressure()
peaks_kwargs = {"height": 100, "distance": 5, "width": 5, "prominence": 100}
segments = find_profiles(pressure, peaks_kwargs=peaks_kwargs)
segments = np.asarray(segments)
start = segments[:, 0]
peak = segments[:, 1]
end = segments[:, 3]
x = np.arange(0, pressure.size)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=pressure, mode="markers", name="pressure"))
fig.add_trace(go.Scatter(x=x[start], y=pressure[start], mode="markers", name="start", marker_color="green"))
fig.add_trace(go.Scatter(x=x[peak], y=pressure[peak], mode="markers", name="peak", marker_color="blue"))
fig.add_trace(go.Scatter(x=x[end], y=pressure[end], mode="markers", name="end", marker_color="red"))
fig.update_layout(yaxis_title="Pressure (dbar)", xaxis_title="Data index (-)", yaxis_autorange="reversed")
HTML(fig.to_html(include_plotlyjs='cdn'))
```

# Microstructure example

Microstructure instruments, such as the vertical microstructure profiler (VMP) or glider-based MicroRider require
additional constraints to identify profiles. The sensors needs to be moving fast enough through the water to collect useful data and data that fall outside of this speed threshold need to be discarded. Additionally, the MicroRider may only be turned on during a climb or dive, meaning that only half a profile of data are collected. 

Below, we create a toy model of a VMP that initially falls in free-fall, before being pulled up by a winch (constant force), with the goal of simulating velocity changes experienced by a real instrument. 

A possible system of differential equations for the instrument motion is:

$$
\begin{align*}
\frac{dz}{dt} &= w \\
\frac{dw}{dt} &= g \frac{m_v - m_w}{m_v} - \frac{m_w}{m_v} \frac{C_d}{L} w |w| + \frac{T(t)}{m_v}
\end{align*}
$$

where $z$ is the height, $w$ is the vertical velocity, $g$ is gravity, $m_v$ is the instrument mass, $m_w$ is the mass of water displaced, $C_d$ is the drag coefficient, $L$ is the hull length, and $T(t)$ is the time-dependent tension from the winch. These equations are solved in the code to produce a synthetic depth profile. We also mimic the sampling rate of a real VMP (60 Hz). 


```{code-cell}
:tags: [hide-input]
from scipy.integrate import solve_ivp
from plotly.subplots import make_subplots

# Physical parameters
mv = 14.0           # mass VMP (kg)
mw = 11.0           # mass water displaced (kg)
L = 1               # hull length (m)
g = -9.81           # gravity (m/s^2)
Cd = 3              # drag coefficient (-)
Tmax = 120.0        # max tension (N)
tension_tau = 8.0  # tension ramp-up time constant (s)
tension_on = 100.0  # time when tension starts (s)

# Time parameters
total_time = 200    # (s)
dt = 1/60           # Interpolation time step 60 Hz


def instrument_ode(t, y):
  z, w = y
  # Tension ramps up after tension_on
  if t < tension_on:
    T = 0.0
  else:
    T = Tmax * (1 - np.exp(-(t - tension_on) / tension_tau))
  dwdt = g * (mv - mw) / mv - (mw / mv) * (Cd / L) * w * np.abs(w) + T / mv
  return [w, dwdt]


def hit_surface(t, y):
  return y[0]
hit_surface.terminal = True
hit_surface.direction = 1  # Only trigger when crossing zero from below

sol = solve_ivp(
  instrument_ode,
  [0, total_time],
  [0.0, 0.0],  # Initial condition [z, w]
  events=hit_surface,
  vectorized=False
)

t_uniform = np.arange(0, sol.t[-1], dt)
z = np.interp(t_uniform, sol.t, sol.y[0])
w = np.interp(t_uniform, sol.t, sol.y[1])
t = t_uniform

fig = make_subplots(rows=1, cols=2)
fig.add_trace(go.Scatter(x=t, y=w, mode="lines", line=dict(color="firebrick")), row=1, col=1)
fig.update_xaxes(title_text="Time (s)", row=1, col=1)
fig.update_yaxes(title_text="w (m/s)", row=1, col=1)
fig.add_trace(go.Scatter(x=t[cut], y=z[cut], mode="lines"), row=1, col=2)
fig.update_xaxes(title_text="Time (s)", row=1, col=2)
fig.update_yaxes(title_text="z (m)", row=1, col=2)
fig.update_layout(showlegend=False)
HTML(fig.to_html(include_plotlyjs='cdn'))
```

We can apply `find_profiles` to this synthetic data like before, but data when the instrument is moving slowly may not be properly excluded. 

```{code-cell}
:tags: [hide-input]

segments = find_profiles(-z)
segments = np.asarray(segments)
down_start = segments[:, 0]
down_end = segments[:, 1]
up_start = segments[:, 2]
up_end = segments[:, 3]

segments_speed = find_profiles(-z, apply_speed_threshold=True, velocity=-w, min_speed=0.9, direction="down")
segments_speed = np.asarray(segments_speed)
down_start_speed = segments_speed[:, 0]
down_end_speed = segments_speed[:, 1]
up_start_speed = segments_speed[:, 2]
up_end_speed = segments_speed[:, 3]

fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=z, mode="lines", name="z"))

fig.add_trace(go.Scatter(x=t[down_start], y=z[down_start], mode="markers", name="down start", marker=dict(color="green", symbol="circle")))
fig.add_trace(go.Scatter(x=t[down_end], y=z[down_end], mode="markers", name="down end", marker=dict(color="red", symbol="circle")))
fig.add_trace(go.Scatter(x=t[up_start], y=z[up_start], mode="markers", name="up start", marker=dict(color="blue", symbol="circle")))
fig.add_trace(go.Scatter(x=t[up_end], y=z[up_end], mode="markers", name="up end", marker=dict(color="orange", symbol="circle")))

fig.add_trace(go.Scatter(x=t[down_start_speed], y=z[down_start_speed], mode="markers", name="down start (speed)", marker=dict(color="green", symbol="diamond")))
fig.add_trace(go.Scatter(x=t[down_end_speed], y=z[down_end_speed], mode="markers", name="down end (speed)", marker=dict(color="red", symbol="diamond")))
fig.add_trace(go.Scatter(x=t[up_start_speed], y=z[up_start_speed], mode="markers", name="up start (speed)", marker=dict(color="blue", symbol="diamond")))
fig.add_trace(go.Scatter(x=t[up_end_speed], y=z[up_end_speed], mode="markers", name="up end (speed)", marker=dict(color="orange", symbol="diamond")))

fig.update_layout(yaxis_title="z (m)", xaxis_title="Time (s)")
HTML(fig.to_html(include_plotlyjs='cdn'))
```