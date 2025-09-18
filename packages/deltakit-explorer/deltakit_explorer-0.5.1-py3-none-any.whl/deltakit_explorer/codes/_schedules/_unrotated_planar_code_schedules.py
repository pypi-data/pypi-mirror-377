# (c) Copyright Riverlane 2020-2025.
"""
Collection of dictionaries for different types of schedules for unrotated planar
codes.
"""

from dataclasses import dataclass
from typing import ClassVar, Dict, Tuple

from deltakit_circuit._basic_types import Coord2DDelta


@dataclass
class UnrotatedPlanarCodeSchedules:
    """
    Dataclass to capture default syndrome extraction schedules for the unrotated
    planar code.
    """

    # In default_N_Z_dict,
    #     "N" means the N-shaped schedule, i.e. for that plaquette we use the
    #     following schedule:
    #             -------------
    #             |    /      |
    #             |   /_>__   |
    #             |       /   |
    #             |     ./    |
    #             -------------
    #     and "Z" means the Z-shaped schedule, i.e. for that plaquette we use the
    #     following schedule:
    #             -------------
    #             |      \    |
    #             |    _<_\   |
    #             |    \      |
    #             |     \.    |
    #             -------------

    default_N_Z_dict: ClassVar[
        Dict[str, Tuple[Coord2DDelta, Coord2DDelta, Coord2DDelta, Coord2DDelta]]
    ] = {
        "N": (
            Coord2DDelta(0, 1),
            Coord2DDelta(-1, 0),
            Coord2DDelta(1, 0),
            Coord2DDelta(0, -1),
        ),
        "Z": (
            Coord2DDelta(0, 1),
            Coord2DDelta(1, 0),
            Coord2DDelta(-1, 0),
            Coord2DDelta(0, -1),
        ),
    }

    # Horizontally reflected version of default_N_Z_dict, i.e. with
    #             -------------
    #             |      \    |
    #             |    _<_\   |
    #             |    \      |
    #             |     \.    |
    #             -------------
    # and
    #             -------------
    #             |    /      |
    #             |   /_>__   |
    #             |       /   |
    #             |     ./    |
    #             -------------
    horizontally_reflected_N_Z_dict: ClassVar[
        Dict[str, Tuple[Coord2DDelta, Coord2DDelta, Coord2DDelta, Coord2DDelta]]
    ] = {
        "N": (
            Coord2DDelta(0, 1),
            Coord2DDelta(1, 0),
            Coord2DDelta(-1, 0),
            Coord2DDelta(0, -1),
        ),
        "Z": (
            Coord2DDelta(0, 1),
            Coord2DDelta(-1, 0),
            Coord2DDelta(1, 0),
            Coord2DDelta(0, -1),
        ),
    }

    # Vertically reflected version of default_N_Z_dict, i.e. with
    #             -------------
    #             |     '\    |
    #             |    _>_\   |
    #             |    \      |
    #             |     \     |
    #             -------------
    # and
    #             -------------
    #             |    /'     |
    #             |   /_<__   |
    #             |       /   |
    #             |      /    |
    #             -------------
    vertically_reflected_N_Z_dict: ClassVar[
        Dict[str, Tuple[Coord2DDelta, Coord2DDelta, Coord2DDelta, Coord2DDelta]]
    ] = {
        n_or_z: schedule[::-1]
        for n_or_z, schedule in horizontally_reflected_N_Z_dict.items()
    }

    # Doubly reflected version of default_N_Z_dict, i.e. with
    #             -------------
    #             |    /'     |
    #             |   /_<__   |
    #             |       /   |
    #             |      /    |
    #             -------------
    # and
    #             -------------
    #             |     '\    |
    #             |    _>_\   |
    #             |    \      |
    #             |     \     |
    #             -------------
    doubly_reflected_N_Z_dict: ClassVar[
        Dict[str, Tuple[Coord2DDelta, Coord2DDelta, Coord2DDelta, Coord2DDelta]]
    ] = {n_or_z: schedule[::-1] for n_or_z, schedule in default_N_Z_dict.items()}
