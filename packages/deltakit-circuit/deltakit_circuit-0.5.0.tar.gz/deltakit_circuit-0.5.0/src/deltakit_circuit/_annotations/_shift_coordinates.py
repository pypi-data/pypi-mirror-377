# (c) Copyright Riverlane 2020-2025.
"""Module which defines a way to shift coordinates."""

from __future__ import annotations

from typing import Iterable

import stim
from deltakit_circuit._qubit_identifiers import Coordinate


class ShiftCoordinates:
    """Annotates a shift in the coordinates within a stim circuit. This
    modifies coordinates associated to detectors and the user is required to
    put each shift coordinate in manually.

    Parameters
    ----------
    coordinate_shift: Iterable[int | float]
        The coordinate shift to impose. Note that this is the delta and not
        the absolute coordinate.
    """

    def __init__(self, coordinate_shift: Iterable[int | float]):
        self._coordinate_shift = Coordinate(*coordinate_shift)

    def permute_stim_circuit(self, stim_circuit: stim.Circuit, _qubit_mapping=None):
        """Updates stim_circuit with the single stim circuit which contains
        this single coordinate shift

        Parameters
        ----------
        stim_circuit : stim.Circuit
            The stim circuit to be updated with the stim representation of
            this single coordinate shift

        _qubit_mapping : None
            Unused argument to keep interface with other layer classes clean.
        """
        stim_circuit.append("SHIFT_COORDS", [], self._coordinate_shift)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ShiftCoordinates)
            and self._coordinate_shift == other._coordinate_shift
        )

    def __hash__(self) -> int:
        return hash(self._coordinate_shift)

    def __repr__(self) -> str:
        return f"ShiftCoordinates({self._coordinate_shift})"
