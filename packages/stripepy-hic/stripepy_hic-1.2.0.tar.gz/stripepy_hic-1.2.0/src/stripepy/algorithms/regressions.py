# Copyright (C) 2024 Andrea Raffo <andrea.raffo@ibv.uio.no>
#
# SPDX-License-Identifier: MIT

import numpy as np
import numpy.typing as npt


def compute_wQISA_predictions(Y: npt.NDArray, k: int) -> npt.NDArray[float]:
    """
    Given a 1D profile and a positive integer k, it smooths the profile
    via weighted quasi-interpolant (spline) approximation.

    Parameters
    ----------
    Y : npt.NDArray
        1D array representing a uniformly-sample scalar function works.
    k: int
        neighborhood diameter (ordinates in the neighborhood are averaged).

    Returns
    -------
    npt.NDArray[float]
        The smoothed profile, as a 1D array with same length as the input array
    """
    assert k >= 1
    # Control points of a weighted quasi-interpolant spline approximation with a k-NN weight function:
    kernel = np.full(k, 1 / k)
    radius = (k - 1) // 2
    Y_ext = np.pad(Y, (radius, radius), mode="edge")
    predictions = np.convolve(Y_ext, kernel, "valid")

    return predictions
