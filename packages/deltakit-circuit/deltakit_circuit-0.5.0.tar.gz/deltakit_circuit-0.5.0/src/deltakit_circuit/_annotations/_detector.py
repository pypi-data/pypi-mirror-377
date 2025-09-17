# (c) Copyright Riverlane 2020-2025.
"""Module which provides detectors and measurement records."""

from __future__ import annotations

from itertools import chain
from typing import FrozenSet, Iterable, Mapping

import stim
from deltakit_circuit._qubit_identifiers import Coordinate, MeasurementRecord


class Detector:
    """Annotates that a set of measurements can be used to detect errors,
    because the set's parity should be deterministic.

    Parameters
    ----------
    measurements : MeasurementRecord | Iterable[MeasurementRecord]
        The measurements that this is the detectors of.
    coordinate: Iterable[float] | None
        An optional coordinate to associate with this detector.
    """

    stim_string = "DETECTOR"

    def __init__(
        self,
        measurements: MeasurementRecord | Iterable[MeasurementRecord],
        coordinate: Iterable[float] | None = None,
    ):
        self._measurements = (
            frozenset((measurements,))
            if isinstance(measurements, MeasurementRecord)
            else frozenset(measurements)
        )
        self._coordinate = Coordinate(*coordinate) if coordinate is not None else None

    @property
    def coordinate(self) -> Coordinate | None:
        """Get the coordinate which specifies this detector."""
        return self._coordinate

    @property
    def measurements(self) -> FrozenSet[MeasurementRecord]:
        return self._measurements

    def transform_coordinates(
        self, coordinate_mapping: Mapping[Coordinate, Coordinate]
    ):
        """
        Transform this detectors coordinates according to the coordinate
        mapping. No transformation is performed if coordinate is not in the
        mapping.

        Parameters
        ----------
        coordinate_mapping : Mapping[Coordinate, Coordinate]
            A mapping of qubit types to other qubit types
        """
        # Functionally passing None to the get method is fine but mypy doesn't
        # like argument to get being Optional[Coordinate].
        if (current_coordinate := self._coordinate) is not None:
            self._coordinate = coordinate_mapping.get(
                current_coordinate, current_coordinate
            )

    def permute_stim_circuit(self, stim_circuit: stim.Circuit, _qubit_mapping=None):
        """Updates stim_circuit with the stim circuit which specifies this
        single detector.

        Parameters
        ----------
        stim_circuit : stim.Circuit
            The stim circuit to be updated with the stim representation of
            this detector

        _qubit_mapping : None, optional
            Unused argument to make interface to this method equal to the
            same methods in layer classes.
        """
        stim_targets = chain.from_iterable(
            record.stim_targets() for record in self.measurements
        )
        if (coordinate := self.coordinate) is None:
            stim_circuit.append(self.stim_string, stim_targets)
        else:
            stim_circuit.append(self.stim_string, stim_targets, coordinate)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Detector)
            and self.measurements == other.measurements
            and self.coordinate == other.coordinate
        )

    def __hash__(self) -> int:
        return hash((self._measurements, self._coordinate))

    def __repr__(self) -> str:
        return f"Detector({list(self.measurements)}, coordinate={self.coordinate})"
