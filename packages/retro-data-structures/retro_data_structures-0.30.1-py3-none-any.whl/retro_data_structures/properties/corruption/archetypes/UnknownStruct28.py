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

if typing.TYPE_CHECKING:
    class UnknownStruct28Json(typing_extensions.TypedDict):
        common_vertical_scale: float
        unknown_0x8ed32be8: float
        unknown_0xcfc4146e: float
        unknown_0x0479c95b: float
        unknown_0xdfc69abc: float
        unknown_0x9c27ea0d: float
        unknown_0xe8c00bb1: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x50af31e, 0x8ed32be8, 0xcfc4146e, 0x479c95b, 0xdfc69abc, 0x9c27ea0d, 0xe8c00bb1)


@dataclasses.dataclass()
class UnknownStruct28(BaseProperty):
    common_vertical_scale: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x050af31e, original_name='CommonVerticalScale'
        ),
    })
    unknown_0x8ed32be8: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8ed32be8, original_name='Unknown'
        ),
    })
    unknown_0xcfc4146e: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcfc4146e, original_name='Unknown'
        ),
    })
    unknown_0x0479c95b: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0479c95b, original_name='Unknown'
        ),
    })
    unknown_0xdfc69abc: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdfc69abc, original_name='Unknown'
        ),
    })
    unknown_0x9c27ea0d: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9c27ea0d, original_name='Unknown'
        ),
    })
    unknown_0xe8c00bb1: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe8c00bb1, original_name='Unknown'
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
        if property_count != 7:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(70))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'\x05\n\xf3\x1e')  # 0x50af31e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.common_vertical_scale))

        data.write(b'\x8e\xd3+\xe8')  # 0x8ed32be8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8ed32be8))

        data.write(b'\xcf\xc4\x14n')  # 0xcfc4146e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcfc4146e))

        data.write(b'\x04y\xc9[')  # 0x479c95b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0479c95b))

        data.write(b'\xdf\xc6\x9a\xbc')  # 0xdfc69abc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdfc69abc))

        data.write(b"\x9c'\xea\r")  # 0x9c27ea0d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9c27ea0d))

        data.write(b'\xe8\xc0\x0b\xb1')  # 0xe8c00bb1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe8c00bb1))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct28Json", data)
        return cls(
            common_vertical_scale=json_data['common_vertical_scale'],
            unknown_0x8ed32be8=json_data['unknown_0x8ed32be8'],
            unknown_0xcfc4146e=json_data['unknown_0xcfc4146e'],
            unknown_0x0479c95b=json_data['unknown_0x0479c95b'],
            unknown_0xdfc69abc=json_data['unknown_0xdfc69abc'],
            unknown_0x9c27ea0d=json_data['unknown_0x9c27ea0d'],
            unknown_0xe8c00bb1=json_data['unknown_0xe8c00bb1'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'common_vertical_scale': self.common_vertical_scale,
            'unknown_0x8ed32be8': self.unknown_0x8ed32be8,
            'unknown_0xcfc4146e': self.unknown_0xcfc4146e,
            'unknown_0x0479c95b': self.unknown_0x0479c95b,
            'unknown_0xdfc69abc': self.unknown_0xdfc69abc,
            'unknown_0x9c27ea0d': self.unknown_0x9c27ea0d,
            'unknown_0xe8c00bb1': self.unknown_0xe8c00bb1,
        }


def _decode_common_vertical_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8ed32be8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcfc4146e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0479c95b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdfc69abc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9c27ea0d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe8c00bb1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x50af31e: ('common_vertical_scale', _decode_common_vertical_scale),
    0x8ed32be8: ('unknown_0x8ed32be8', _decode_unknown_0x8ed32be8),
    0xcfc4146e: ('unknown_0xcfc4146e', _decode_unknown_0xcfc4146e),
    0x479c95b: ('unknown_0x0479c95b', _decode_unknown_0x0479c95b),
    0xdfc69abc: ('unknown_0xdfc69abc', _decode_unknown_0xdfc69abc),
    0x9c27ea0d: ('unknown_0x9c27ea0d', _decode_unknown_0x9c27ea0d),
    0xe8c00bb1: ('unknown_0xe8c00bb1', _decode_unknown_0xe8c00bb1),
}
