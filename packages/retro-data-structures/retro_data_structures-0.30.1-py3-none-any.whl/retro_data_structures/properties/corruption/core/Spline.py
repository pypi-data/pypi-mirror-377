# Generated file
import dataclasses
import struct
import typing
import typing_extensions

import construct

from retro_data_structures.common_types import MayaSpline
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_spline import BaseSpline, Knot


def _read_knot(data: typing.BinaryIO) -> Knot:
    header = typing.cast(tuple[float, float, int, int], struct.unpack(">ffBB", data.read(10)))
    cached_tangents_a = None
    cached_tangents_b = None
    if header[2] == 5:
        cached_tangents_a = typing.cast(tuple[float, float], struct.unpack(">ff", data.read(8)))
    if header[3] == 5:
        cached_tangents_b = typing.cast(tuple[float, float], struct.unpack(">ff", data.read(8)))

    return Knot(*header, cached_tangents_a=cached_tangents_a, cached_tangents_b=cached_tangents_b)


@dataclasses.dataclass()
class Spline(BaseSpline):

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        pre_infinity, post_infinity, knot_count = struct.unpack(">BBL", data.read(6))
        knots = [
            _read_knot(data)
            for _ in range(knot_count)
        ]
        clamp_mode, minimum_amplitude, maximum_amplitude = struct.unpack(">Bff", data.read(9))

        return cls(
            pre_infinity=pre_infinity,
            post_infinity=post_infinity,
            knots=knots,
            clamp_mode=clamp_mode,
            minimum_amplitude=minimum_amplitude,
            maximum_amplitude=maximum_amplitude,
        )

    def to_stream(self, data: typing.BinaryIO) -> None:
        MayaSpline.build_stream(construct.Container(
            pre_infinity=self.pre_infinity,
            post_infinity=self.post_infinity,
            knots=[
                construct.Container(
                    time=knot.time,
                    amplitude=knot.amplitude,
                    unk_a=knot.unk_a,
                    unk_b=knot.unk_b,
                    cached_tangents_a=knot.cached_tangents_a,
                    cached_tangents_b=knot.cached_tangents_b,
                )
                for knot in self.knots
            ],
            clamp_mode=self.clamp_mode,
            minimum_amplitude=self.minimum_amplitude,
            maximum_amplitude=self.maximum_amplitude,
        ), data)


    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION
