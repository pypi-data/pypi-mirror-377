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
    class InterpolationMethodJson(typing_extensions.TypedDict):
        interpolation_control_type: int
        control_spline: json_util.JsonObject
        ease_in: float
        ease_out: float
        duration: float
    

class InterpolationControlType(enum.IntEnum):
    Unknown1 = 1464541212
    Unknown2 = 3715904643
    Unknown3 = 3342922233
    Unknown4 = 4055225324
    Unknown5 = 3980215693
    Unknown6 = 1935003390
    Unknown7 = 881774861

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
class InterpolationMethod(BaseProperty):
    interpolation_control_type: InterpolationControlType = dataclasses.field(default=InterpolationControlType.Unknown2, metadata={
        'reflection': FieldReflection[InterpolationControlType](
            InterpolationControlType, id=0x09b5957d, original_name='InterpolationControlType', from_json=InterpolationControlType.from_json, to_json=InterpolationControlType.to_json
        ),
    })
    control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x15567fe7, original_name='ControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    ease_in: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb08d3237, original_name='EaseIn'
        ),
    })
    ease_out: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x67e3836a, original_name='EaseOut'
        ),
    })
    duration: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b51e23f, original_name='Duration'
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
        if property_count != 5:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x09b5957d
        interpolation_control_type = InterpolationControlType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15567fe7
        control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb08d3237
        ease_in = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x67e3836a
        ease_out = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b51e23f
        duration = struct.unpack('>f', data.read(4))[0]
    
        return cls(interpolation_control_type, control_spline, ease_in, ease_out, duration)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'\t\xb5\x95}')  # 0x9b5957d
        data.write(b'\x00\x04')  # size
        self.interpolation_control_type.to_stream(data)

        data.write(b'\x15V\x7f\xe7')  # 0x15567fe7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb0\x8d27')  # 0xb08d3237
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ease_in))

        data.write(b'g\xe3\x83j')  # 0x67e3836a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ease_out))

        data.write(b'\x8bQ\xe2?')  # 0x8b51e23f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.duration))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("InterpolationMethodJson", data)
        return cls(
            interpolation_control_type=InterpolationControlType.from_json(json_data['interpolation_control_type']),
            control_spline=Spline.from_json(json_data['control_spline']),
            ease_in=json_data['ease_in'],
            ease_out=json_data['ease_out'],
            duration=json_data['duration'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'interpolation_control_type': self.interpolation_control_type.to_json(),
            'control_spline': self.control_spline.to_json(),
            'ease_in': self.ease_in,
            'ease_out': self.ease_out,
            'duration': self.duration,
        }


def _decode_interpolation_control_type(data: typing.BinaryIO, property_size: int) -> InterpolationControlType:
    return InterpolationControlType.from_stream(data)


def _decode_ease_in(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ease_out(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x9b5957d: ('interpolation_control_type', _decode_interpolation_control_type),
    0x15567fe7: ('control_spline', Spline.from_stream),
    0xb08d3237: ('ease_in', _decode_ease_in),
    0x67e3836a: ('ease_out', _decode_ease_out),
    0x8b51e23f: ('duration', _decode_duration),
}
