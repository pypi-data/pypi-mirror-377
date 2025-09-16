# -*- coding: utf-8 -*-

import numpy as np
from numba import njit, prange  # , types
from numpy.typing import NDArray

###############################################################################
# General methods
###############################################################################


@njit(fastmath=True, cache=True, inline="always")
def flat_to_coords(idx, nx, ny, nz):
    i = idx // (ny * nz)
    j = (idx % (ny * nz)) // nz
    k = idx % nz
    return i, j, k


@njit(fastmath=True, cache=True, inline="always")
def coords_to_flat(i, j, k, nx, ny, nz):
    return i * (ny * nz) + j * nz + k


@njit(parallel=True, cache=True)
def get_edges(
    labeled_array: NDArray[np.int64],
    neighbor_transforms: NDArray[np.int64],
    vacuum_mask: NDArray[np.bool_],
):
    """
    In a 3D array of labeled voxels, finds the voxels that neighbor at
    least one voxel with a different label.

    Parameters
    ----------
    labeled_array : NDArray[np.int64]
        A 3D array where each entry represents the basin label of the point.
    neighbor_transforms : NDArray[np.int64]
        The transformations from each voxel to its neighbors.
    vacuum_mask : NDArray[np.bool_]
        A 3D array representing the location of the vacuum

    Returns
    -------
    edges : NDArray[np.bool_]
        A mask with the same shape as the input grid that is True at points
        on basin edges.

    """
    nx, ny, nz = labeled_array.shape
    # create 3D array to store edges
    edges = np.zeros_like(labeled_array, dtype=np.bool_)
    # loop over each voxel in parallel
    for i in prange(nx):
        for j in range(ny):
            for k in range(nz):
                # if this voxel is part of the vacuum, continue
                if vacuum_mask[i, j, k]:
                    continue
                # get this voxels label
                label = labeled_array[i, j, k]
                # iterate over the neighboring voxels
                for si, sj, sk in neighbor_transforms:
                    # wrap points
                    ii, jj, kk = wrap_point(i + si, j + sj, k + sk, nx, ny, nz)
                    # get neighbors label
                    neigh_label = labeled_array[ii, jj, kk]
                    # if any label is different, the current voxel is an edge.
                    # Note this in our edge array and break
                    # NOTE: we also check that the neighbor is not part of the
                    # vacuum
                    if neigh_label != label and not vacuum_mask[ii, jj, kk]:
                        edges[i, j, k] = True
                        break
    return edges


@njit(parallel=True, cache=True)
def get_maxima(
    data: NDArray[np.float64],
    neighbor_transforms: NDArray[np.int64],
    vacuum_mask: NDArray[np.bool_],
    use_minima: bool = False,
):
    """
    For a 3D array of data, return a mask that is True at local maxima.

    Parameters
    ----------
    data : NDArray[np.float64]
        A 3D array of data.
    neighbor_transforms : NDArray[np.int64]
        The transformations from each voxel to its neighbors.
    vacuum_mask : NDArray[np.bool_]
        A 3D array representing the location of the vacuum
    use_minima : bool, optional
        Whether or not to search for minima instead of maxima.

    Returns
    -------
    maxima : NDArray[np.bool_]
        A mask with the same shape as the input grid that is True at points
        that are local maxima.

    """
    nx, ny, nz = data.shape
    # create 3D array to store maxima
    maxima = np.zeros_like(data, dtype=np.bool_)
    # loop over each voxel in parallel
    for i in prange(nx):
        for j in range(ny):
            for k in range(nz):
                # if this voxel is part of the vacuum, continue
                if vacuum_mask[i, j, k]:
                    continue
                # get this voxels value
                value = data[i, j, k]
                is_max = True
                # iterate over the neighboring voxels
                for si, sj, sk in neighbor_transforms:
                    # wrap points
                    ii, jj, kk = wrap_point(i + si, j + sj, k + sk, nx, ny, nz)
                    if not use_minima:
                        if data[ii, jj, kk] > value:
                            is_max = False
                            break
                    else:
                        if data[ii, jj, kk] < value:
                            is_max = False
                            break
                if is_max:
                    maxima[i, j, k] = True
    return maxima


@njit(fastmath=True, cache=True)
def get_basin_charges_and_volumes(
    data: NDArray[np.float64],
    labels: NDArray[np.int64],
    cell_volume: np.float64,
    maxima_num: np.int64,
):
    nx, ny, nz = data.shape
    total_points = nx * ny * nz
    # create variables to store charges/volumes
    charges = np.zeros(maxima_num, dtype=np.float64)
    volumes = np.zeros(maxima_num, dtype=np.float64)
    vacuum_charge = 0.0
    vacuum_volume = 0.0
    # iterate in parallel over each voxel
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                charge = data[i, j, k]
                label = labels[i, j, k]
                if label < 0:
                    vacuum_charge += charge
                    vacuum_volume += 1
                else:
                    charges[label] += charge
                    volumes[label] += 1.0
    # calculate charge and volume
    volumes = volumes * cell_volume / total_points
    charges = charges / total_points
    vacuum_volume = vacuum_volume * cell_volume / total_points
    vacuum_charge = vacuum_charge / total_points
    return charges, volumes, vacuum_charge, vacuum_volume


@njit(cache=True, inline="always")
def wrap_point(
    i: np.int64, j: np.int64, k: np.int64, nx: np.int64, ny: np.int64, nz: np.int64
) -> tuple[np.int64, np.int64, np.int64]:
    """
    Wraps a 3D point (i, j, k) into the periodic bounds defined by the grid dimensions (nx, ny, nz).

    If any of the input coordinates are outside the bounds [0, nx), [0, ny), or [0, nz),
    they are wrapped around using periodic boundary conditions.

    Parameters
    ----------
    i : np.int64
        x-index of the point.
    j : np.int64
        y-index of the point.
    k : np.int64
        z-index of the point.
    nx : np.int64
        Number of grid points along x-direction.
    ny : np.int64
        Number of grid points along y-direction.
    nz : np.int64
        Number of grid points along z-direction.

    Returns
    -------
    tuple[np.int64, np.int64, np.int64]
        The wrapped (i, j, k) indices within the bounds.
    """
    if i >= nx:
        i -= nx
    elif i < 0:
        i += nx
    if j >= ny:
        j -= ny
    elif j < 0:
        j += ny
    if k >= nz:
        k -= nz
    elif k < 0:
        k += nz
    return i, j, k


@njit(cache=True, inline="always")
def get_gradient_simple(
    data: NDArray[np.float64],
    voxel_coord: NDArray[np.int64],
    # car2lat: NDArray[np.float64],
    dir2lat: NDArray[np.float64],
) -> tuple[NDArray[np.int64], NDArray[np.int64], np.bool_]:
    """
    Peforms a neargrid step from the provided voxel coordinate.

    Parameters
    ----------
    data : NDArray[np.float64]
        A 3D grid of values for each point.
    voxel_coord : NDArray[np.int64]
        The point to make the step from.
    car2lat : NDArray[np.float64]
        A matrix that converts a coordinate in cartesian space to fractional
        space.

    Returns
    -------
    charge_grad_frac : NDArray[np.float64]
        The gradient in direct space at this voxel coord

    """
    nx, ny, nz = data.shape
    i, j, k = voxel_coord
    # calculate the gradient at this point in voxel coords
    charge000 = data[i, j, k]
    charge001 = data[i, j, (k + 1) % nz]
    charge010 = data[i, (j + 1) % ny, k]
    charge100 = data[(i + 1) % nx, j, k]
    charge00_1 = data[i, j, (k - 1) % nz]
    charge0_10 = data[i, (j - 1) % ny, k]
    charge_100 = data[(i - 1) % nx, j, k]

    gi = (charge100 - charge_100) / 2.0
    gj = (charge010 - charge0_10) / 2.0
    gk = (charge001 - charge00_1) / 2.0

    if charge100 <= charge000 and charge_100 <= charge000:
        gi = 0.0
    if charge010 <= charge000 and charge0_10 <= charge000:
        gj = 0.0
    if charge001 <= charge000 and charge00_1 <= charge000:
        gk = 0.0

    # convert to direct
    # NOTE: Doing this rather than the original car2lat with two np.dot operations
    # saves about half the time.
    r0 = dir2lat[0, 0] * gi + dir2lat[0, 1] * gj + dir2lat[0, 2] * gk
    r1 = dir2lat[1, 0] * gi + dir2lat[1, 1] * gj + dir2lat[1, 2] * gk
    r2 = dir2lat[2, 0] * gi + dir2lat[2, 1] * gj + dir2lat[2, 2] * gk
    return r0, r1, r2


# NOTE
# This is an alternative method for calculating the gradient that uses all of
# the neighbors for each grid point to get an overdetermined system with improved
# sampling. I didn't find it made a big difference.
@njit(cache=True, inline="always")
def get_gradient_overdetermined(
    data,
    i,
    j,
    k,
    vox_transforms,
    transform_dists,
    car2lat,
    inv_norm_cart_trans,
):
    nx, ny, nz = data.shape
    # Value at the central point
    point_value = data[i, j, k]
    # Number of neighbor displacements/transforms
    num_transforms = len(vox_transforms)

    # Array to hold finite‐difference estimates along each transform direction
    diffs = np.zeros(num_transforms)
    # Loop over each neighbor transform
    for trans_idx in range(num_transforms):
        # Displacement vector in voxel (grid) coordinates
        x, y, z = vox_transforms[trans_idx]
        # Compute “upper” neighbor index, wrapped by periodic boundaries
        ui, uj, uk = wrap_point(i + x, j + y, k + z, nx, ny, nz)
        # Compute “lower” neighbor index (opposite direction), also wrapped
        li, lj, lk = wrap_point(i - x, j - y, k - z, nx, ny, nz)
        # Values at the neighboring points
        upper_value = data[ui, uj, uk]
        lower_value = data[li, lj, lk]

        # If both neighbors are below or equal to the center, zero out this direction
        # (prevents spurious negative slopes if data dips on both sides)
        if lower_value <= point_value and upper_value <= point_value:
            diffs[trans_idx] = 0.0
        else:
            # Standard central‐difference estimate: (f(i+Δ) – f(i–Δ)) / (2Δ)
            diffs[trans_idx] = (upper_value - lower_value) / (
                2.0 * transform_dists[trans_idx]
            )

    # Solve the overdetermined system to get the Cartesian gradient:
    #   norm_cart_transforms.T @ cart_grad ≈ diffs
    # Use the pseudoinverse to handle more directions than dimensions
    # inv_norm_cart_trans = np.linalg.pinv(norm_cart_transforms) where
    # norm_cart_transforms is an N, 3 shaped array pointing to 13 unique neighbors
    ti, tj, tk = inv_norm_cart_trans @ diffs
    # Convert Cartesian gradient to fractional (lattice) coordinates
    ti_new = car2lat[0, 0] * ti + car2lat[0, 1] * tj + car2lat[0, 2] * tk
    tj_new = car2lat[1, 0] * ti + car2lat[1, 1] * tj + car2lat[1, 2] * tk
    tk_new = car2lat[2, 0] * ti + car2lat[2, 1] * tj + car2lat[2, 2] * tk

    ti, tj, tk = ti_new, tj_new, tk_new
    return ti, tj, tk


@njit(fastmath=True, cache=True)
def merge_frac_coords(
    frac_coords,
):

    # We'll accumulate (unwrapped) coordinates into total
    total0 = 0.0
    total1 = 0.0
    total2 = 0.0
    count = 0

    # reference coord used for unwrapping
    ref0 = 0.0
    ref1 = 0.0
    ref2 = 0.0
    ref_set = False

    # scan all maxima and pick those that belong to this target_group
    for c0, c1, c2 in frac_coords:

        # first seen -> set reference for unwrapping
        if not ref_set:
            ref0, ref1, ref2 = c0, c1, c2
            ref_set = True

        # unwrap coordinate relative to reference: unwrapped = coord - round(coord - ref)
        # Using np.round via float -> use built-in round for numba compatibility
        # but call round(x) (returns float)
        un0 = c0 - round(c0 - ref0)
        un1 = c1 - round(c1 - ref1)
        un2 = c2 - round(c2 - ref2)

        # add to total
        total0 += un0
        total1 += un1
        total2 += un2
        count += 1

    if count == 1:
        # return original point wrapped to [0,1)
        return np.array((ref0 % 1.0, ref1 % 1.0, ref2 % 1.0), dtype=np.float64)

    else:
        # return average of points
        avg0 = (total0 / count) % 1.0
        avg1 = (total1 / count) % 1.0
        avg2 = (total2 / count) % 1.0
        return np.array((avg0, avg1, avg2), dtype=np.float64)


@njit(cache=True, fastmath=True)
def combine_maxima_frac(
    labels,
    maxima_vox,
    maxima_frac,
):
    # get the labels at each maximum
    maxima_labels = np.empty(len(maxima_vox), dtype=np.int64)
    for max_idx in prange(len(maxima_vox)):
        i, j, k = maxima_vox[max_idx]
        maxima_labels[max_idx] = labels[i, j, k]

    # find unique labels
    unique_labels = np.unique(maxima_labels)
    n_unique = len(unique_labels)

    # Prepare result arrays
    all_frac_coords = np.zeros((n_unique, 3), dtype=np.float64)

    # Parallel loop: for each unique label, scan new_labels and compute the average
    # frac coords
    for u_idx in prange(n_unique):
        target_label = unique_labels[u_idx]
        # get the frac coords for maxima with this label
        frac_coords = []
        for max_idx, label in enumerate(maxima_labels):
            if label == target_label:
                frac_coords.append(maxima_frac[max_idx])
        # get average frac coords and assign
        all_frac_coords[u_idx] = merge_frac_coords(frac_coords)
    return all_frac_coords


@njit(cache=True, parallel=True)
def combine_neigh_maxima(
    labels,
    neighbor_transforms,
    maxima_vox,
    maxima_frac,
    maxima_mask,
):
    nx, ny, nz = labels.shape
    initial_labels = np.arange(len(maxima_vox), dtype=np.int64)
    new_labels = np.zeros(len(maxima_vox), dtype=np.int64)
    # check each neighbor and if its a max with a lower index, update the index
    for max_idx in prange(len(maxima_vox)):
        i, j, k = maxima_vox[max_idx]
        best_label = initial_labels[max_idx]
        for si, sj, sk in neighbor_transforms:
            # get neighbor and wrap
            ii, jj, kk = wrap_point(i + si, j + sj, k + sk, nx, ny, nz)
            # check if new point is also a maximum
            if maxima_mask[ii, jj, kk] and labels[ii, jj, kk] < best_label:
                best_label = labels[ii, jj, kk]
        new_labels[max_idx] = best_label
    # TODO:
    # This may not fully reduce maxima. It may be possible for several voxels
    # in a row to all be maxima. If we had for example four voxels in a line
    # that are all maxima, the first two may be relabeld to the first and the
    # other two may be relabeld to the second or some other configuration. I
    # need to decide if these are physically reasonable situations where an
    # average should be taken.

    # Now we want to calculate the new frac coords for each group. We also want
    # to make sure the labels go from 0, 1, 2, ... so on, while currently they
    # may skip some (e.g. 0,2,3,5,...)
    # find unique labels and their count
    unique_labels = np.unique(new_labels)
    n_unique = len(unique_labels)

    # Prepare result arrays
    reduced_new_labels = np.empty(len(new_labels), dtype=np.int64)
    all_frac_coords = np.zeros((n_unique, 3), dtype=np.float64)

    # Parallel loop: for each unique label, scan new_labels and get average
    # frac coords
    for u_idx in prange(n_unique):
        target_label = unique_labels[u_idx]
        frac_coords = []
        for max_idx, label in enumerate(new_labels):
            if label == target_label:
                frac_coords.append(maxima_frac[max_idx])
                reduced_new_labels[max_idx] = u_idx
        # combine frac coords
        all_frac_coords[u_idx] = merge_frac_coords(frac_coords)

    return reduced_new_labels, all_frac_coords


@njit(cache=True, inline="always")
def get_best_neighbor(
    data: NDArray[np.float64],
    i: np.int64,
    j: np.int64,
    k: np.int64,
    neighbor_transforms: NDArray[np.int64],
    neighbor_dists: NDArray[np.int64],
):
    """
    For a given coordinate (i,j,k) in a grid (data), finds the neighbor with
    the largest gradient.

    Parameters
    ----------
    data : NDArray[np.float64]
        The data for each voxel.
    i : np.int64
        First coordinate
    j : np.int64
        Second coordinate
    k : np.int64
        Third coordinate
    neighbor_transforms : NDArray[np.int64]
        Transformations to apply to get to the voxels neighbors
    neighbor_dists : NDArray[np.int64]
        The distance to each voxels neighbor

    Returns
    -------
    best_transform : NDArray[np.int64]
        The transformation to the best neighbor
    best_neigh : NDArray[np.int64]
        The coordinates of the best neigbhor
    is_max: bool
        Whether or not this voxel is a local maximum

    """
    nx, ny, nz = data.shape
    # get the elf value and initial label for this voxel. This defaults
    # to the voxel pointing to itself
    base = data[i, j, k]
    best = 0.0
    # create initial best transform. Default to this point
    bti = 0
    btj = 0
    btk = 0
    # create initial best neighbor
    bni = i
    bnj = j
    bnk = k
    # best_neigh = np.array([i, j, k], dtype=np.int64)
    # For each neighbor get the difference in value and if its better
    # than any previous, replace the current best
    for (si, sj, sk), dist in zip(neighbor_transforms, neighbor_dists):
        # loop
        ii, jj, kk = wrap_point(i + si, j + sj, k + sk, nx, ny, nz)
        # calculate the difference in value taking into account distance
        diff = (data[ii, jj, kk] - base) / dist
        # if better than the current best, note the best and the
        # current label
        if diff > best:
            best = diff
            bti, btj, btk = (si, sj, sk)
            bni, bnj, bnk = (ii, jj, kk)
        # if the neighbor has the same value as the current point, we likely
        # have adjacent maxima. If the neighbor has a lower flat index than the
        # current point, we use it as our pointer
        elif diff == 0.0:
            # get the flat idx of the current best neighbor and this neighbor
            flat_idx = coords_to_flat(bni, bnj, bnk, nx, ny, nz)
            flat_neigh = coords_to_flat(ii, jj, kk, nx, ny, nz)
            # if the neighbors index is lower, update our best neigh/transform
            if flat_neigh < flat_idx:
                bti, btj, btk = (si, sj, sk)
                bni, bnj, bnk = (ii, jj, kk)
    # We've finished our loop. return the best shift, neighbor, and whether this
    # is a max
    # NOTE: Can't do is_max = best == 0.0 for older numba
    is_max = False
    if best == 0.0:
        is_max = True
    # return best_transform, best_neigh, is_max
    return (
        np.array((bti, btj, btk), dtype=np.int64),
        np.array((bni, bnj, bnk), dtype=np.int64),
        is_max,
    )


@njit(cache=True)
def climb_to_max(
    data: NDArray[np.float64],
    i: np.int64,
    j: np.int64,
    k: np.int64,
    neighbor_transforms: NDArray[np.int64],
    neighbor_dists: NDArray[np.int64],
):
    """
    For a given coordinate (i,j,k) in a grid (data), hill climbs until a maximum
    is reached.

    Parameters
    ----------
    data : NDArray[np.float64]
        The data for each voxel.
    i : np.int64
        First coordinate
    j : np.int64
        Second coordinate
    k : np.int64
        Third coordinate
    neighbor_transforms : NDArray[np.int64]
        Transformations to apply to get to the voxels neighbors
    neighbor_dists : NDArray[np.int64]
        The distance to each voxels neighbor

    Returns
    -------
    mi : np.int64
        The first coordinate of the maximum
    mj : np.int64
        The second coordinate of the maximum
    mk : np.int64
        The third coordinate of the maximum

    """
    # start hill climbing
    while True:
        _, (mi, mj, mk), is_max = get_best_neighbor(
            data,
            i,
            j,
            k,
            neighbor_transforms,
            neighbor_dists,
        )
        if is_max:
            break
        # otherwise, update coord
        i, j, k = (mi, mj, mk)
    return mi, mj, mk


@njit(cache=True, fastmath=True)
def get_min_dists(
    labels,
    frac_coords,
    edge_indices,
    matrix,
    max_value,
):
    nx, ny, nz = labels.shape
    # create array to store best dists
    dists = np.full(len(frac_coords), max_value, dtype=np.float64)
    for i, j, k in edge_indices:
        # get label at edge
        label = labels[i, j, k]
        # convert from voxel indices to frac
        fi = i / nx
        fj = j / ny
        fk = k / nz
        # calculate the distance to the appropriate frac coord
        ni, nj, nk = frac_coords[label]
        # get differences between each index
        di = ni - fi
        dj = nj - fj
        dk = nk - fk
        # wrap at edges to be as close as possible
        di -= round(di)
        dj -= round(dj)
        dk -= round(dk)
        # convert to cartesian coordinates
        ci = di * matrix[0, 0] + dj * matrix[1, 0] + dk * matrix[2, 0]
        cj = di * matrix[0, 1] + dj * matrix[1, 1] + dk * matrix[2, 1]
        ck = di * matrix[0, 2] + dj * matrix[1, 2] + dk * matrix[2, 2]
        # calculate distance
        dist = np.linalg.norm(np.array((ci, cj, ck), dtype=np.float64))
        # if this is the lowest distance, update radius
        if dist < dists[label]:
            dists[label] = dist
    return dists
