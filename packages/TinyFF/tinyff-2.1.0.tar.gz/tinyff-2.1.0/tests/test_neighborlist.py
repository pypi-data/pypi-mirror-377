# TinyFF is a minimalistic Force Field evaluator.
# Copyright (C) 2024 Toon Verstraelen
#
# This file is part of TinyFF.
#
# TinyFF is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# TinyFF is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""Unit tests for tinyff.neighborlist."""

import numpy as np
import pytest

from tinyff.neighborlist import (
    NBuildCellLists,
    NBuildSimple,
    _apply_mic,
    _assign_atoms_to_bins,
    _create_parts_nearby,
    _create_parts_self,
    _determine_nbins,
    _iter_nearby,
)


def test_mic():
    atpos = np.array([[0.1, 0.1, 0.2], [1.9, 1.9, 2.0]])
    cell_lengths = np.array([2.0, 2.0, 2.0])
    deltas = atpos[[1]] - atpos[[0]]
    dists = _apply_mic(deltas, cell_lengths)
    assert deltas == pytest.approx(np.array([[-0.2, -0.2, -0.2]]))
    assert dists == pytest.approx([np.sqrt(12) / 10])


def test_mic_random():
    rng = np.random.default_rng(42)
    natom = 100
    npair = 200
    atpos = rng.uniform(-50, 50, (natom, 3))
    iatoms0 = rng.integers(natom, size=npair)
    iatoms1 = rng.integers(natom, size=npair)
    cell_lengths = np.array([5.0, 10.0, 20.0])
    deltas = atpos[iatoms1] - atpos[iatoms0]
    dists = _apply_mic(deltas, cell_lengths)
    assert deltas.shape == (npair, 3)
    assert (abs(deltas) <= cell_lengths / 2).all()
    assert (dists <= np.linalg.norm(cell_lengths) / 2).all()


def test_determine_nbins_ortho1():
    cell_lengths = np.array([5.0, 10.0, 20.0])
    assert (_determine_nbins(cell_lengths, 2.0, 8) == [2, 2, 4]).all()
    assert (_determine_nbins(cell_lengths, 2.0, 15) == [2, 2, 4]).all()


def test_determine_nbins_ortho2():
    cell_lengths = np.array([10.0, 10.0, 20.0])
    assert (_determine_nbins(cell_lengths, 2.0, 8) == [2, 2, 3]).all()
    assert (_determine_nbins(cell_lengths, 2.0, 16) == [2, 2, 4]).all()


def test_determine_nbins_cubic():
    cell_lengths = np.array([10.0, 10.0, 10.0])
    assert (_determine_nbins(cell_lengths, 2.0, 8) == [2, 2, 2]).all()
    assert (_determine_nbins(cell_lengths, 2.0, 27) == [3, 3, 3]).all()


def test_determine_nbins_cubic_rmax():
    cell_lengths = np.array([100.0, 100.0, 100.0])
    assert (_determine_nbins(cell_lengths, 20.0, 1000) == [5, 5, 5]).all()


def test_assign_atoms_to_bins_simple():
    atpos = np.array([[0.0, 0.0, 0.0], [0.9, 0.1, 0.4], [1.5, 0.1, 4.1]])
    cell_lengths = np.array([2.0, 2.0, 2.0])
    nbins = np.array([2, 2, 2])
    bins = _assign_atoms_to_bins(atpos, cell_lengths, nbins)
    assert len(bins) == 2
    for idx in bins:
        assert len(idx) == 3
        assert isinstance(idx[0], int)
        assert isinstance(idx[1], int)
        assert isinstance(idx[2], int)
    assert (bins[(0, 0, 0)] == [0, 1]).all()
    assert (bins[(1, 0, 0)] == [2]).all()


def test_assign_atoms_to_bins_random():
    rng = np.random.default_rng(42)
    natom = 500
    atpos = rng.uniform(-50, 50, (natom, 3))
    cell_lengths = np.array([5.0, 3.0, 2.0])
    nbins = np.array([5, 3, 2])
    bins = _assign_atoms_to_bins(atpos, cell_lengths, nbins)
    for idx, atoms in bins.items():
        assert len(idx) == 3
        assert isinstance(idx[0], int)
        assert isinstance(idx[1], int)
        assert isinstance(idx[2], int)
        assert idx[0] >= 0
        assert idx[0] < 5
        assert idx[1] >= 0
        assert idx[1] < 3
        assert idx[2] >= 0
        assert idx[2] < 2
        assert (atoms[1:] > atoms[:-1]).all()
    assert len(bins) == 5 * 3 * 2
    assert sum(len(bin0) for bin0 in bins.values()) == natom


@pytest.mark.parametrize("with_bin", [True, False])
def test_create_parts_self_simple(with_bin):
    atpos = (
        np.array([[0.0, -1.0, -4.0], [0.0, 0.0, 1.0], [0.0, 1.0, 4.0], [2.0, 5.0, 7.0]])
        if with_bin
        else np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 4.0]])
    )
    cell_lengths = np.array([15.0, 15.0, 15.0])
    rcut = 4.5
    bin0 = np.array([1, 2]) if with_bin else None
    iatoms0, iatoms1, deltas, dists = _create_parts_self(atpos, bin0, cell_lengths, rcut)
    if not with_bin:
        bin0 = [0, 1]
    assert iatoms0.shape == (1,)
    assert iatoms0.dtype == int
    assert iatoms0[0] == bin0[0]
    assert iatoms1.shape == (1,)
    assert iatoms1.dtype == int
    assert iatoms1[0] == bin0[1]
    assert deltas.shape == (1, 3)
    assert deltas[0] == pytest.approx([0.0, 1.0, 3.0])
    assert dists.shape == (1,)
    assert dists[0] == pytest.approx(np.sqrt(10))


@pytest.mark.parametrize("with_bin", [True, False])
def test_create_parts_self_random(with_bin):
    rng = np.random.default_rng(42)
    natom = 200
    atpos = rng.uniform(-50, 50, (natom, 3))
    cell_lengths = np.array([10.0, 15.0, 20.0])
    rcut = 4.5
    if with_bin:
        bin0 = rng.choice(natom, natom // 2, replace=False)
        bin0.sort()
        assert len(np.unique(bin0)) == natom // 2
    else:
        bin0 = None
    iatoms0_a, iatoms1_a, deltas_a, dists_a = _create_parts_self(atpos, bin0, cell_lengths, rcut)
    if with_bin:
        assert all(iatom0 in bin0 for iatom0 in iatoms0_a)
        assert all(iatom1 in bin0 for iatom1 in iatoms1_a)
    npair = len(dists_a)
    assert iatoms0_a.shape == (npair,)
    assert iatoms0_a.dtype == int
    assert iatoms1_a.shape == (npair,)
    assert iatoms1_a.dtype == int
    assert (iatoms0_a < iatoms1_a).all()
    assert len(np.unique(iatoms0_a + natom * iatoms1_a)) == npair
    assert deltas_a.shape == (npair, 3)
    assert (abs(deltas_a) < cell_lengths / 2).all()
    assert dists_a.shape == (npair,)
    assert (dists_a < np.linalg.norm(cell_lengths) / 2).all()

    # Displace all atoms by an integer linear combination of cell vectors.
    # This should not have any influence on the result.
    atpos += rng.integers(-5, 5, size=(natom, 3)) * cell_lengths
    iatoms0_b, iatoms1_b, deltas_b, dists_b = _create_parts_self(atpos, bin0, cell_lengths, rcut)
    assert (iatoms0_a == iatoms0_b).all()
    assert (iatoms1_a == iatoms1_b).all()
    assert deltas_a == pytest.approx(deltas_b)
    assert dists_a == pytest.approx(dists_b)


def test_iter_nearby_simple():
    nbins = np.array([3, 4, 5])
    nearby = list(_iter_nearby((0, 1, 2), nbins))
    assert len(nearby) == len(set(nearby))
    assert nearby == [
        (2, 0, 1),
        (2, 1, 1),
        (2, 2, 1),
        (0, 0, 1),
        (0, 1, 1),
        (0, 2, 1),
        (1, 0, 1),
        (1, 1, 1),
        (1, 2, 1),
        (2, 0, 2),
        (0, 0, 2),
        (1, 0, 2),
        (2, 1, 2),
    ]


def test_iter_nearby_all():
    nbins = np.array([3, 4, 5])
    for n0 in range(nbins[0]):
        for n1 in range(nbins[1]):
            for n2 in range(nbins[2]):
                nearby = list(_iter_nearby((n0, n1, n2), nbins))
                assert len(nearby) == len(set(nearby))
                for o0, o1, o2 in nearby:
                    assert o0 >= 0
                    assert o0 < nbins[0]
                    assert o1 >= 0
                    assert o1 < nbins[1]
                    assert o2 >= 0
                    assert o2 < nbins[2]


def test_create_parts_nearby_simple():
    # Prepare example.
    atpos = np.array([[0.1, 0.1, 0.1], [0.9, 0.9, 2.5], [1.1, 1.2, -0.1], [1.9, 1.7, 1.8]])
    bin0 = np.array([0, 1])
    bin1 = np.array([2, 3])
    cell_lengths = np.array([2.0, 2.0, 2.0])
    rcut = 0.999
    iatoms0, iatoms1, deltas, dists = _create_parts_nearby(atpos, bin0, bin1, cell_lengths, rcut)

    # Two combinations are not expected to be present.
    all_deltas = atpos[[2, 3, 2, 3]] - atpos[[0, 0, 1, 1]]
    all_dists = _apply_mic(all_deltas, cell_lengths)
    assert all_dists[0] >= rcut
    assert all_dists[3] >= rcut

    # Check the other two.
    assert iatoms0.shape == (2,)
    assert iatoms0.dtype == int
    assert (iatoms0 == [0, 1]).all()
    assert iatoms1.shape == (2,)
    assert iatoms1.dtype == int
    assert (iatoms1 == [3, 2]).all()
    assert deltas.shape == (2, 3)
    assert dists.shape == (2,)
    assert deltas[0] == pytest.approx([-0.2, -0.4, -0.3])
    assert dists[0] == pytest.approx(np.sqrt(29) / 10)
    assert deltas[1] == pytest.approx([0.2, 0.3, -0.6])
    assert dists[1] == pytest.approx(0.7)


def test_create_parts_nearby_random():
    rng = np.random.default_rng(42)
    natom = 100
    atpos = np.concatenate(
        [
            rng.uniform(0, 1, (natom // 2, 3)),
            rng.uniform(0, 1, (natom // 2, 3)) + [1, 0, 0],  # noqa: RUF005
        ]
    )
    cell_lengths = np.array([3.0, 2.0, 5.0])
    rcut = 0.999
    bin0 = np.arange(natom // 2)
    bin1 = bin0 + natom // 2

    # Run with original input
    iatoms0_a, iatoms1_a, deltas_a, dists_a = _create_parts_nearby(
        atpos, bin0, bin1, cell_lengths, rcut
    )
    npair = len(dists_a)
    assert npair < ((natom // 2) * (natom // 2 - 1)) // 2
    assert iatoms0_a.shape == (npair,)
    assert iatoms1_a.shape == (npair,)
    assert deltas_a.shape == (npair, 3)
    assert dists_a.shape == (npair,)
    assert (dists_a < rcut).all()

    # Displace all atoms by an integer linear combination of cell vectors.
    # This should not have any influence on the result.
    atpos += rng.integers(-5, 5, size=(natom, 3)) * cell_lengths
    iatoms0_b, iatoms1_b, deltas_b, dists_b = _create_parts_nearby(
        atpos, bin0, bin1, cell_lengths, rcut
    )
    assert (iatoms0_a == iatoms0_b).all()
    assert (iatoms1_a == iatoms1_b).all()
    assert deltas_a == pytest.approx(deltas_b)
    assert dists_a == pytest.approx(dists_b)


@pytest.mark.parametrize(
    "nbuild",
    [
        NBuildSimple(rmax=0.4, nlist_reuse=2),
        NBuildCellLists(rmax=0.4, nlist_reuse=2, nbin_approx=8),
    ],
)
@pytest.mark.parametrize("cell_length", [1.0, 2.0, 3.0])
def test_build_cubic_simple(nbuild, cell_length):
    # Build
    atpos = np.array([[0.1, 0.1, 0.1], [-0.1, -0.1, -0.1]])
    atpos[1] += cell_length
    cell_lengths = [cell_length] * 3
    nbuild.update(atpos, cell_lengths)
    assert len(nbuild.nlist) == 1
    i, j, delta, _, dist, _, _ = nbuild.nlist[0]
    if i == 0:
        assert j == 1
        assert delta == pytest.approx([-0.2, -0.2, -0.2])
    else:
        assert i == 1
        assert j == 0
        assert delta == pytest.approx([0.2, 0.2, 0.2])
    assert dist == pytest.approx(np.sqrt(12) / 10)

    # Recompute
    atpos[1] = [0.5, 0.5, 0.5]
    nbuild.update(atpos, cell_lengths)
    assert len(nbuild.nlist) == 1
    i, j, delta, _, dist, _, _ = nbuild.nlist[0]
    if i == 0:
        assert j == 1
        assert delta == pytest.approx([0.4, 0.4, 0.4])
    else:
        assert i == 1
        assert j == 0
        assert delta == pytest.approx([-0.4, -0.4, -0.4])
    assert dist == pytest.approx(np.sqrt(48) / 10)


@pytest.mark.parametrize("nbuild", [NBuildSimple(0.4), NBuildCellLists(0.4, nbin_approx=8)])
def test_build_empty(nbuild):
    atpos = np.array([[0.1, 0.1, 0.1], [2.1, 2.1, 2.1]])
    cell_lenghts = 5.0
    nbuild.update(atpos, cell_lenghts)
    assert len(nbuild.nlist) == 0


@pytest.mark.parametrize(
    "cell_lengths", [[10.0, 15.0, 20.0], [15.0, 20.0, 10.0], [20.0, 10.0, 15.0]]
)
def test_build_ortho_random(cell_lengths):
    rmax = 4.999
    rng = np.random.default_rng(42)
    natom = 100
    atpos = rng.uniform(-50.0, 50.0, (natom, 3))

    # Compute with simple algorithm and with linked cell
    nbuild1 = NBuildSimple(rmax)
    nbuild1.update(atpos, cell_lengths)
    nbuild2 = NBuildCellLists(rmax, nbin_approx=8)
    nbuild2.update(atpos, cell_lengths)

    # Compare the results
    assert len(nbuild1.nlist) == len(nbuild2.nlist)

    def normalize(nlist):
        """Normalize neigbor lists to enable one-on-one comparison."""
        iatoms0 = nlist["iatom0"].copy()
        iatoms1 = nlist["iatom1"].copy()
        swap = iatoms0 < iatoms1
        nlist["iatom0"][swap] = iatoms1[swap]
        nlist["iatom1"][swap] = iatoms0[swap]
        nlist["delta"][swap] *= -1
        order = np.lexsort([nlist["iatom1"], nlist["iatom0"]])
        nlist[:] = nlist[order]

    # Sort both neighbor lists
    normalize(nbuild1.nlist)
    normalize(nbuild2.nlist)

    # Compare each field separately for more readable test outputs
    assert (nbuild1.nlist["iatom0"] == nbuild2.nlist["iatom0"]).all()
    assert (nbuild1.nlist["iatom1"] == nbuild2.nlist["iatom1"]).all()
    assert nbuild1.nlist["delta"] == pytest.approx(nbuild2.nlist["delta"])
    assert nbuild1.nlist["dist"] == pytest.approx(nbuild2.nlist["dist"])


@pytest.mark.parametrize(
    "nbuild",
    [
        NBuildSimple(rmax=9.0, nlist_reuse=3),
        NBuildCellLists(rmax=9.0, nlist_reuse=3, nbin_approx=8),
    ],
)
def test_nlist_reuse(nbuild):
    # Build a simple model for testing.
    cell_length = 20.0
    atpos = np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0]])

    # Define the force field.
    nbuild.update(atpos, cell_length)
    assert len(nbuild.nlist) == 1
    assert nbuild.nlist_use_count == 3
    assert nbuild.nlist["dist"][0] == pytest.approx(2.0)
    atpos = np.array([[0.0, 0.0, 0.0], [8.5, 0.0, 0.0]])
    nbuild.update(atpos, cell_length)
    assert len(nbuild.nlist) == 1
    assert nbuild.nlist_use_count == 2
    assert nbuild.nlist["dist"][0] == pytest.approx(8.5)
    atpos = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]])
    nbuild.update(atpos, cell_length)
    assert nbuild.nlist_use_count == 1
    assert len(nbuild.nlist) == 1
    assert nbuild.nlist["dist"][0] == pytest.approx(10)
    nbuild.update(atpos, cell_length)
    assert nbuild.nlist_use_count == 3
    assert len(nbuild.nlist) == 0
