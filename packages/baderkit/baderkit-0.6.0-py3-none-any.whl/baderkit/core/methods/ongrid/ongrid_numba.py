# -*- coding: utf-8 -*-

import numpy as np
from numba import njit, prange
from numpy.typing import NDArray

from baderkit.core.methods.shared_numba import coords_to_flat, get_best_neighbor


@njit(parallel=True, cache=True)
def get_steepest_pointers(
    data: NDArray[np.float64],
    neighbor_transforms: NDArray[np.int64],
    neighbor_dists: NDArray[np.int64],
    vacuum_mask: NDArray[np.bool_],
):
    """
    For each voxel in a 3D grid of data, finds the index of the neighboring voxel with
    the highest value, weighted by distance.

    Parameters
    ----------
    data : NDArray[np.float64]
        A 3D grid of values for each point.
    neighbor_transforms : NDArray[np.int64]
        The transformations from each voxel to its neighbors.
    neighbor_dists : NDArray[np.int64]
        The distance to each neighboring voxel
    vacuum_mask : NDArray[np.bool_]
        A 3D array representing the location of the vacuum

    Returns
    -------
    pointers : NDArray[np.int64]
        A 3D array where each entry is the index of the neighbor that had the
        greatest increase in value. A value of -1 indicates a vacuum point.
    maxima_mask : NDArray[np.bool_]
        A 3D array that is True at maxima

    """
    nx, ny, nz = data.shape
    # create array to store the label of the neighboring voxel with the greatest
    # elf value
    pointers = np.empty(nx * ny * nz, dtype=np.int64)
    # create an array to store maxima
    maxima_mask = np.zeros(data.shape, dtype=np.bool_)
    # loop over each voxel in parallel
    for i in prange(nx):
        for j in range(ny):
            for k in range(nz):
                # get the flat index of this point
                flat_idx = coords_to_flat(i, j, k, nx, ny, nz)
                # check if this is a vacuum point. If so, we don't even bother
                # with the label.
                if vacuum_mask[i, j, k]:
                    pointers[flat_idx] = -1
                    continue
                # get the best neighbor
                _, (x, y, z), is_max = get_best_neighbor(
                    data=data,
                    i=i,
                    j=j,
                    k=k,
                    neighbor_transforms=neighbor_transforms,
                    neighbor_dists=neighbor_dists,
                )
                pointers[flat_idx] = coords_to_flat(x, y, z, nx, ny, nz)
                if is_max:
                    maxima_mask[i, j, k] = True
    return pointers, maxima_mask
