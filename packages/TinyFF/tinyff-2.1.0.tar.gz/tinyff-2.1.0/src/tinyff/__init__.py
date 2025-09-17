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
"""The TinyFF package."""

from .analysis import compute_acf, compute_rdf
from .atomsmithy import build_bcc_lattice, build_cubic_lattice, build_fcc_lattice, build_random_cell
from .forcefield import ForceField
from .neighborlist import NBuildCellLists, NBuildSimple
from .pairwise import CutOffWrapper, LennardJones, PairwiseTerm
from .trajectory import NPYWriter, PDBWriter

__all__ = (
    "CutOffWrapper",
    "ForceField",
    "LennardJones",
    "NBuildCellLists",
    "NBuildSimple",
    "NPYWriter",
    "PDBWriter",
    "PairwiseTerm",
    "build_bcc_lattice",
    "build_cubic_lattice",
    "build_fcc_lattice",
    "build_random_cell",
    "compute_acf",
    "compute_rdf",
)

try:
    from ._version import __version__, __version_tuple__
except ImportError:
    __version__ = "0.0.0a-dev"
    __version_tuple__ = (0, 0, 0, "a-dev")
