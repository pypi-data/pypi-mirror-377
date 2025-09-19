# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class CameraShakerEnvelopeJson(typing_extensions.TypedDict):
        shake_shape: int
        amplitude: json_util.JsonObject
        period: json_util.JsonObject
    

class ShakeShape(enum.IntEnum):
    Unknown1 = 1492241241
    Unknown2 = 1817964322

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


@dataclasses.dataclass()
class CameraShakerEnvelope(BaseProperty):
    shake_shape: ShakeShape = dataclasses.field(default=ShakeShape.Unknown1, metadata={
        'reflection': FieldReflection[ShakeShape](
            ShakeShape, id=0xc6089a3f, original_name='ShakeShape', from_json=ShakeShape.from_json, to_json=ShakeShape.to_json
        ),
    })
    amplitude: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x90b3cc7e, original_name='Amplitude', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    period: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x69a81517, original_name='Period', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
        if (result := cls._fast_decode(data, property_count)) is not None:
            return result

        present_fields = default_override or {}
        for _ in range(property_count):
            property_id, property_size = struct.unpack(">LH", data.read(6))
            start = data.tell()
            try:
                property_name, decoder = _property_decoder[property_id]
                present_fields[property_name] = decoder(data, property_size)
            except KeyError:
                raise RuntimeError(f"Unknown property: 0x{property_id:08x}")
            assert data.tell() - start == property_size

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 3:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6089a3f
        shake_shape = ShakeShape.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90b3cc7e
        amplitude = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69a81517
        period = Spline.from_stream(data, property_size)
    
        return cls(shake_shape, amplitude, period)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\xc6\x08\x9a?')  # 0xc6089a3f
        data.write(b'\x00\x04')  # size
        self.shake_shape.to_stream(data)

        data.write(b'\x90\xb3\xcc~')  # 0x90b3cc7e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.amplitude.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'i\xa8\x15\x17')  # 0x69a81517
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.period.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraShakerEnvelopeJson", data)
        return cls(
            shake_shape=ShakeShape.from_json(json_data['shake_shape']),
            amplitude=Spline.from_json(json_data['amplitude']),
            period=Spline.from_json(json_data['period']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'shake_shape': self.shake_shape.to_json(),
            'amplitude': self.amplitude.to_json(),
            'period': self.period.to_json(),
        }


def _decode_shake_shape(data: typing.BinaryIO, property_size: int) -> ShakeShape:
    return ShakeShape.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc6089a3f: ('shake_shape', _decode_shake_shape),
    0x90b3cc7e: ('amplitude', Spline.from_stream),
    0x69a81517: ('period', Spline.from_stream),
}
