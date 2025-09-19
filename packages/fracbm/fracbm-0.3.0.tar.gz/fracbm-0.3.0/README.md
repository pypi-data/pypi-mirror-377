# fracbm

  
Fractional Gaussian Noise (fGN) and Fractional Brownian Motion (fBM) tools.

<p align="left">
  <img src="terrain.gif" alt='terrain gen with fbm' width="400"/>
</p>
  

## Installation

```bash

pip  install  fracbm

```

## Usage

  
```bash
import matplotlib.pyplot as plt
import fracbm

# Parameters
n = 10000      # number of steps
H = 0.7       # Hurst parameter

# Fractional Brownian motion using Davies–Harte
fbm_path = fracbm.daviesharte.motion(n, H)      # cumulative sum of fGN
fgn_increments = fracbm.daviesharte.noise(n, H) # fractional Gaussian noise

# Wavelet based estimation of Hurst exponent
estimated_hurst = fracbm.invhurst(fbm_path)
print(f'Estimated Hurst Exponent = {estimated_hurst}')

# Plot the full fBm path
plt.figure(figsize=(10, 4))
plt.plot(fbm_path, label="fBM path (Davies–Harte)")
plt.xlabel("Step")
plt.ylabel("Value")
plt.title("Fractional Brownian Motion (H=0.8, Davies–Harte)")
plt.legend()
plt.show()

```


## Features

Generate exact fractional Brownian motion using:

-   **Cholesky decomposition**, order $\mathcal{O}(n^3)$
-   **Davies-Harte method**, order $\mathcal{O}(n \log n)$ 	(recommended)  

-   Vary the Hurst parameter $H \in [0,1]$:
-   $H = 0.5$ is regular Brownian motion.
-   $H > 0.5$ causes slowly decaying positive autocorrelations (positive increments tend to follow positive increments - increments follow a trend).
-   $H < 0.5$ causes fast-decaying negative autocorrelations (negative increments tend to follow positive increments - increments revert to the mean).

Determine the Hurst exponent of a time series:

-   **Wavelet transform** method
-   For n ~ 10000 or greater
