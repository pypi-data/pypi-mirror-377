# (c) Copyright Riverlane 2020-2025.
"""Classes which represent depolarising noise on one or two qubits."""

from __future__ import annotations

import math
from typing import ClassVar, FrozenSet, Type, Union, get_args

from deltakit_circuit.noise_channels._abstract_noise_channels import (
    OneProbabilityNoiseChannel,
    OneQubitOneProbabilityNoiseChannel,
    TwoQubitNoiseChannel,
)
from deltakit_circuit._qubit_identifiers import Qubit, T


class Depolarise1(OneQubitOneProbabilityNoiseChannel[T]):
    """The one-qubit depolarising channel. Applies a randomly chosen Pauli
    with a given probability.

    Parameters
    ----------
    qubit : Qubit[T] | T
        The qubit to apply one-qubit depolarising noise to.
    probability : float
        A single float specifying the depolarisation strength.

    Notes
    -----
    | Pauli Mixture:
    |   ``1-p: I``
    |   ``p/3: X``
    |   ``p/3: Y``
    |   ``p/3: Z``
    """

    stim_string: ClassVar[str] = "DEPOLARIZE1"


class Depolarise2(OneProbabilityNoiseChannel[T], TwoQubitNoiseChannel[T]):
    """The two-qubit depolarising channel.  Applies a randomly chosen
    two-qubit Pauli product with a given probability.

    Parameters
    ----------
    qubit1: Qubit[T] | T
        The first qubit in the noise channel.
    qubit2: Qubit[T] | T
        The second qubit in the noise channel.
    probability : float
        A single float specifying the depolarisation strength.

    Notes
    -----
    | Pauli Mixture:
    |   ``1-p: II``
    |   ``p/15: IX``
    |   ``p/15: IY``
    |   ``p/15: IZ``
    |   ``p/15: XI``
    |   ``p/15: XX``
    |   ``p/15: XY``
    |   ``p/15: XZ``
    |   ``p/15: YI``
    |   ``p/15: YX``
    |   ``p/15: YY``
    |   ``p/15: YZ``
    |   ``p/15: ZI``
    |   ``p/15: ZX``
    |   ``p/15: ZY``
    |   ``p/15: ZZ``
    """

    stim_string: ClassVar[str] = "DEPOLARIZE2"

    def __init__(self, qubit1: Qubit[T] | T, qubit2: Qubit[T] | T, probability: float):
        super().__init__(qubit1=qubit1, qubit2=qubit2, probability=probability)

    def approx_equals(
        self, other: object, *, rel_tol: float = 1e-9, abs_tol: float = 0
    ) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.qubits == other.qubits
            and math.isclose(
                self.probability, other.probability, rel_tol=rel_tol, abs_tol=abs_tol
            )
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.qubits == other.qubits
            and self.probability == other.probability
        )

    def __hash__(self) -> int:
        return hash((self.__class__, self._qubit1, self._qubit2, self.probability))

    def __repr__(self) -> str:
        return (
            f"{self.stim_string}"
            f"(qubit1={self._qubit1}, qubit2={self._qubit2}, "
            f"probability={self.probability})"
        )


_DepolarisingNoise = Union[Depolarise1[T], Depolarise2[T]]
ALL_DEPOLARISING_NOISE: FrozenSet[Type[_DepolarisingNoise]] = frozenset(
    get_args(_DepolarisingNoise)
)
