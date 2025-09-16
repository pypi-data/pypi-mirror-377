"""
#####################################################################
Copyright (C) 2025 Michele Cappellari  
E-mail: michele.cappellari_at_physics.ox.ac.uk  

Updated versions of this software are available at:  
https://pypi.org/project/powerbin/  

If you use this software in published research, please acknowledge it as:  
“PowerBin method by Cappellari (2025, MNRAS submitted)”  
https://arxiv.org/abs/2509.06903  

This software is provided “as is”, without any warranty of any kind,  
express or implied.  

Permission is granted for:  
 - Non-commercial use.  
 - Modification for personal or internal use, provided that this  
   copyright notice and disclaimer remain intact and unaltered  
   at the beginning of the file.  

All other rights are reserved. Redistribution of the code, in whole or in part,  
is strictly prohibited without prior written permission from the author.  

#####################################################################

V1.0.0: PowerBin created — MC, Oxford, 10 September 2025

"""
import heapq

import numpy as np
from numpy.typing import ArrayLike
import matplotlib.pyplot as plt
from scipy import ndimage, spatial

from plotbin.display_pixels import display_pixels

#----------------------------------------------------------------------------

def reassign_bad_bins(bin_num, xy):
    """Implements steps (vi)-(vii) in section 5.1 of Cappellari & Copin (2003)"""

    # Find the geometric centroid of all successful bins.
    # bin_num = 0 are unbinned pixels which are excluded.
    good = np.unique(bin_num[bin_num > 0])
    xnode = ndimage.mean(xy[:, 0], labels=bin_num, index=good)
    ynode = ndimage.mean(xy[:, 1], labels=bin_num, index=good)

    # Reassign pixels of bins with S/N < target_sn
    # to the closest centroid of a good bin
    bad = bin_num == 0
    xybin = np.column_stack([xnode, ynode])
    index = spatial.KDTree(xybin).query(xy[bad])[1]
    bin_num[bad] = good[index]

    # Recompute geometric centroids of the reassigned bins.
    # These will be used as starting points for the CVT.
    good = np.unique(bin_num)
    xnode = ndimage.mean(xy[:, 0], labels=bin_num, index=good)
    ynode = ndimage.mean(xy[:, 1], labels=bin_num, index=good)
    xybin = np.column_stack([xnode, ynode])

    return xybin

#----------------------------------------------------------------------------

def roundness(xy):
    """Implements equation (5) of Cappellari & Copin (2003)"""
    equivalent_radius = np.sqrt(xy.shape[0]/np.pi)
    centroid = xy.mean(axis=0)  # Geometric centroid here!
    max_distance = np.linalg.norm(xy - centroid, axis=1).max()
    return max_distance/equivalent_radius

#----------------------------------------------------------------------------

def bin_accretion(
    xy: ArrayLike,
    target_capacity: float,
    fun_capacity: callable,
    verbose: int,
    args: tuple = ()
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate initial bin centers using a bin-accretion algorithm.

    This function computes an initial set of bin generators to serve as a
    starting guess for the subsequent regularization step. It implements the
    bin‑accretion algorithm of Cappellari & Copin (2003) [1], with algorithmic
    improvements that reduce the time complexity from O(N^2) to O(N log N)
    (see Cappellari 2025 [2]).

    The algorithm proceeds as follows:
      1. Identify the "brightest" (highest capacity) unbinned pixel to use as
         a seed for a new bin.
      2. Iteratively "accrete" the nearest unbinned neighboring pixels into
         the current bin.
      3. Stop accretion when the bin is disconnected, becomes too non‑circular,
         or its capacity starts moving away from the target.
      4. Seed a new bin from the next brightest available pixel and repeat
         until all pixels are binned.
      5. Reassign pixels belonging to bins that failed to reach a significant
         fraction of the target capacity to the nearest successful bin.

    Key differences from the original Cappellari & Copin (2003) algorithm:
      * **Neighbor finding**: Pixel neighbors are pre‑computed once using a
        Delaunay triangulation for efficiency, instead of being searched at
        each step.
      * **Bin seeding**: A max‑heap data structure is used to efficiently
        select the brightest unbinned pixel as the next seed in O(log N) time,
        improving over the original O(N) search.
      * **Stopping criterion**: Accretion is guided by a generic
        ``target_capacity`` and stops when the bin's capacity overshoots or
        moves away from this target, rather than simply exceeding a
        signal‑to‑noise threshold.

    Parameters
    ----------
    xy : array_like of shape (N, 2)
        Coordinates of the pixels to be binned.
    target_capacity : float
        The target capacity for each bin.
    fun_capacity : callable
        Function to compute the capacity of a set of pixels, with the
        signature ``fun_capacity(indices, *args)``.
    verbose : int
        Controls the level of printed output:
          * 0 — no output
          * 1 — basic summary (default)
          * 2 — detailed progress
          * 3 — detailed progress plus plots
    args : tuple, optional
        Additional positional arguments to pass to ``fun_capacity``.

    Returns
    -------
    xybin : ndarray of shape (nbin, 2)
        Coordinates of the centroids of the generated bins.
    dens : ndarray of shape (N,)
        The initial capacity density for each input pixel.

    References
    ----------
    .. [1] Cappellari, M. & Copin, Y. 2003, MNRAS, 342, 345
           (Section 5.1) https://ui.adsabs.harvard.edu/abs/2003MNRAS.342..345C
    .. [2] Cappellari, M. 2025, MNRAS submitted,
           https://arxiv.org/abs/2509.06903 (Section 6)
    """
    if verbose >= 1:
        print('Bin-accretion Delaunay...')

    n = xy.shape[0]
    bin_num = np.zeros(n, dtype=int)     # bin label per pixel
    bad = np.ones(n, dtype=bool)         # True means "potentially bad" until bin reaches threshold
    dens = np.array([fun_capacity(j, *args) for j in range(n)])  # per-pixel capacity ("brightness")

    # Rough estimate of expected final bin count (informational only)
    # This number is meaningless if dens is not additive.
    w = dens < target_capacity
    maxnum = int(np.sum(dens[w]) / target_capacity + np.sum(~w))

    # Precompute neighbors once via Delaunay
    tri = spatial.Delaunay(xy, qhull_options="QJ")  # QJ needed for regular grids
    indices, indptr = tri.vertex_neighbor_vertices

    def neighbours(j):
        return indptr[indices[j]:indices[j + 1]]

    # Build a max-heap of seeds keyed by brightness (dens).
    # Python heapq is a min-heap; use negative key for max behavior.
    density_heap = [(-dens[i], i) for i in range(n)]
    heapq.heapify(density_heap)

    # Helper: pop the brightest unbinned pixel or return None if none remains
    def pop_next_seed():
        while density_heap:
            _, idx = heapq.heappop(density_heap)
            if bin_num[idx] == 0:
                return idx
        return None

    # Outer loop: at most n bins
    for ind in range(1, n + 1):

        if verbose >= 2 and (ind % 1000 == 0):
            print(f'{ind} / {maxnum}')

        # Start new bin: pick brightest unbinned pixel from the heap
        current_bin = pop_next_seed()
        if current_bin is None:            
            break    # No unbinned pixels remain in heap

        # Initialize a new bin (single pixel)
        bin_num[current_bin] = ind
        centroid = xy[current_bin]
        capacity = dens[current_bin]
        neigh = neighbours(current_bin)

        # Inner bin-accretion loop
        while capacity < target_capacity:

            ok = (bin_num[neigh] == 0)
            if not np.any(ok):
                break

            # Candidate: unbinned neighbor closest to current bin centroid
            unbin_neigh = neigh[ok]
            d2 = np.linalg.norm(xy[unbin_neigh] - centroid, axis=1)
            newpix = unbin_neigh[np.argmin(d2)]

            # Test roundness of the possible new bin
            next_bin = np.append(current_bin, newpix)
            if roundness(xy[next_bin]) > 2:
                break

            # Update capacity for candidate bin
            capacity_old, capacity = capacity, fun_capacity(next_bin, *args)

            # Stop if new capacity overshoots target and is farther away
            if capacity + capacity_old > 2*target_capacity:
                break

            # Accept candidate pixel and continue accretion
            bin_num[newpix] = ind
            current_bin = next_bin
            centroid = xy[current_bin].mean(axis=0)
            neigh = np.union1d(unbin_neigh, neighbours(newpix))

        # Bin considered "good enough" if it approached target capacity
        if capacity > 0.8 * target_capacity:
            bad[current_bin] = False

    # Zero out pixels that remained "bad" (bins that did not reach threshold)
    bin_num[bad] = 0

    if verbose >= 3:
        rng = np.random.default_rng(826)
        rnd = rng.permutation(xy.shape[0])   # Randomize bin colors
        bins = np.unique(bin_num[bin_num > 0])
        xbin_plot = ndimage.mean(xy[:, 0], labels=bin_num, index=bins)
        ybin_plot = ndimage.mean(xy[:, 1], labels=bin_num, index=bins)

        plt.clf()
        display_pixels(*xy.T, rnd[bin_num], cmap='Set3')
        plt.plot(*xy[bad].T, 'k+')
        plt.plot(xbin_plot, ybin_plot, 'o', mfc='none', mec='k', ms=4)
        plt.title('Initial Bin Accretion')
        plt.pause(5)

    # Final reassignment of bad bins as in original
    xybin = reassign_bad_bins(bin_num, xy)

    if verbose >= 1:
        print(np.max(bin_num), ' initial bins.')
        print(xybin.shape[0], ' good bins.')

    return xybin, dens

#----------------------------------------------------------------------------
