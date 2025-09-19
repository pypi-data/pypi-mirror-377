# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class TweakTargeting_LockDaggerJson(typing_extensions.TypedDict):
        lock_dagger_normal_scale: float
        unknown: float
        lock_dagger_color: json_util.JsonValue
        lock_dagger0_angle: float
        lock_dagger1_angle: float
        lock_dagger2_angle: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x469550e8, 0x7b48e6f9, 0x53c2c9fc, 0xa29cdf22, 0x631200e2, 0xfaf066e3)


@dataclasses.dataclass()
class TweakTargeting_LockDagger(BaseProperty):
    lock_dagger_normal_scale: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x469550e8, original_name='LockDaggerNormalScale'
        ),
    })
    unknown: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7b48e6f9, original_name='Unknown'
        ),
    })
    lock_dagger_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x53c2c9fc, original_name='LockDaggerColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    lock_dagger0_angle: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa29cdf22, original_name='LockDagger0Angle'
        ),
    })
    lock_dagger1_angle: float = dataclasses.field(default=120.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x631200e2, original_name='LockDagger1Angle'
        ),
    })
    lock_dagger2_angle: float = dataclasses.field(default=240.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfaf066e3, original_name='LockDagger2Angle'
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
        if property_count != 6:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHffffLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(72))
        assert (dec[0], dec[3], dec[6], dec[12], dec[15], dec[18]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            Color(*dec[8:12]),
            dec[14],
            dec[17],
            dec[20],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'F\x95P\xe8')  # 0x469550e8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lock_dagger_normal_scale))

        data.write(b'{H\xe6\xf9')  # 0x7b48e6f9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'S\xc2\xc9\xfc')  # 0x53c2c9fc
        data.write(b'\x00\x10')  # size
        self.lock_dagger_color.to_stream(data)

        data.write(b'\xa2\x9c\xdf"')  # 0xa29cdf22
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lock_dagger0_angle))

        data.write(b'c\x12\x00\xe2')  # 0x631200e2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lock_dagger1_angle))

        data.write(b'\xfa\xf0f\xe3')  # 0xfaf066e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lock_dagger2_angle))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakTargeting_LockDaggerJson", data)
        return cls(
            lock_dagger_normal_scale=json_data['lock_dagger_normal_scale'],
            unknown=json_data['unknown'],
            lock_dagger_color=Color.from_json(json_data['lock_dagger_color']),
            lock_dagger0_angle=json_data['lock_dagger0_angle'],
            lock_dagger1_angle=json_data['lock_dagger1_angle'],
            lock_dagger2_angle=json_data['lock_dagger2_angle'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'lock_dagger_normal_scale': self.lock_dagger_normal_scale,
            'unknown': self.unknown,
            'lock_dagger_color': self.lock_dagger_color.to_json(),
            'lock_dagger0_angle': self.lock_dagger0_angle,
            'lock_dagger1_angle': self.lock_dagger1_angle,
            'lock_dagger2_angle': self.lock_dagger2_angle,
        }


def _decode_lock_dagger_normal_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_lock_dagger_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_lock_dagger0_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_lock_dagger1_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_lock_dagger2_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x469550e8: ('lock_dagger_normal_scale', _decode_lock_dagger_normal_scale),
    0x7b48e6f9: ('unknown', _decode_unknown),
    0x53c2c9fc: ('lock_dagger_color', _decode_lock_dagger_color),
    0xa29cdf22: ('lock_dagger0_angle', _decode_lock_dagger0_angle),
    0x631200e2: ('lock_dagger1_angle', _decode_lock_dagger1_angle),
    0xfaf066e3: ('lock_dagger2_angle', _decode_lock_dagger2_angle),
}
