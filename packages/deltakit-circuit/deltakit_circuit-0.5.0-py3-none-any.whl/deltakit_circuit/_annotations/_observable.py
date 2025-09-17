# (c) Copyright Riverlane 2020-2025.
"""Module which provides the Observable class."""

from __future__ import annotations

from itertools import chain
from typing import FrozenSet, Iterable

import stim
from deltakit_circuit._annotations._detector import MeasurementRecord


class Observable:
    """A logical observable as defined by stim.

    Parameters
    ----------
    observable_index: int
        Give a way of identifying this observable
    measurements: MeasurementRecord | Iterable[MeasurementRecord]
        The measurement records which identify the logical observable.
    """

    stim_string = "OBSERVABLE_INCLUDE"

    def __init__(
        self,
        observable_index: int,
        measurements: MeasurementRecord | Iterable[MeasurementRecord],
    ):
        if observable_index < 0:
            raise ValueError("Observable index cannot be negative.")
        self._observable_index = observable_index
        self._measurements = (
            frozenset((measurements,))
            if isinstance(measurements, MeasurementRecord)
            else frozenset(measurements)
        )

    @property
    def measurements(self) -> FrozenSet[MeasurementRecord]:
        return self._measurements

    def permute_stim_circuit(self, stim_circuit: stim.Circuit, _qubit_mapping=None):
        """Updates stim_circuit with the stim circuit which includes this
        logical observable.

        Parameters
        ----------
        stim_circuit : stim.Circuit
            The stim circuit to be updated with the stim representation of
            this observable

        _qubit_mapping : None, optional
            Unused argument to make interface to this method equal to the
            same methods in layer classes.
        """
        stim_targets = chain.from_iterable(
            record.stim_targets() for record in self.measurements
        )
        stim_circuit.append(self.stim_string, stim_targets, self._observable_index)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Observable)
            and self._observable_index == other._observable_index
            and self.measurements == other.measurements
        )

    def __hash__(self) -> int:
        return hash((self._observable_index, self._measurements))

    def __repr__(self) -> str:
        return f"Observable({list(self.measurements)}, index={self._observable_index})"

    @property
    def observable_index(self) -> int:
        """
        Read-only id property, passed at initialisation.

        Returns
        -------
        int
            Observable index, passed at initialisation.
        """
        return self._observable_index
