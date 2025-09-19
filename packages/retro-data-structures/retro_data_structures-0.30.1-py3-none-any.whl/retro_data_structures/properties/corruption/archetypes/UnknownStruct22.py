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
    class UnknownStruct22Json(typing_extensions.TypedDict):
        unknown_0x1b07123d: float
        unknown_0x52f88637: float
        unknown_0x413b2f46: float
        unknown_0x5a7ca693: float
        unknown_0x9acd94e4: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x1b07123d, 0x52f88637, 0x413b2f46, 0x5a7ca693, 0x9acd94e4)


@dataclasses.dataclass()
class UnknownStruct22(BaseProperty):
    unknown_0x1b07123d: float = dataclasses.field(default=-0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1b07123d, original_name='Unknown'
        ),
    })
    unknown_0x52f88637: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x52f88637, original_name='Unknown'
        ),
    })
    unknown_0x413b2f46: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x413b2f46, original_name='Unknown'
        ),
    })
    unknown_0x5a7ca693: float = dataclasses.field(default=-0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5a7ca693, original_name='Unknown'
        ),
    })
    unknown_0x9acd94e4: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9acd94e4, original_name='Unknown'
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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(50))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'\x1b\x07\x12=')  # 0x1b07123d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1b07123d))

        data.write(b'R\xf8\x867')  # 0x52f88637
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x52f88637))

        data.write(b'A;/F')  # 0x413b2f46
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x413b2f46))

        data.write(b'Z|\xa6\x93')  # 0x5a7ca693
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5a7ca693))

        data.write(b'\x9a\xcd\x94\xe4')  # 0x9acd94e4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9acd94e4))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct22Json", data)
        return cls(
            unknown_0x1b07123d=json_data['unknown_0x1b07123d'],
            unknown_0x52f88637=json_data['unknown_0x52f88637'],
            unknown_0x413b2f46=json_data['unknown_0x413b2f46'],
            unknown_0x5a7ca693=json_data['unknown_0x5a7ca693'],
            unknown_0x9acd94e4=json_data['unknown_0x9acd94e4'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x1b07123d': self.unknown_0x1b07123d,
            'unknown_0x52f88637': self.unknown_0x52f88637,
            'unknown_0x413b2f46': self.unknown_0x413b2f46,
            'unknown_0x5a7ca693': self.unknown_0x5a7ca693,
            'unknown_0x9acd94e4': self.unknown_0x9acd94e4,
        }


def _decode_unknown_0x1b07123d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x52f88637(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x413b2f46(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5a7ca693(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9acd94e4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1b07123d: ('unknown_0x1b07123d', _decode_unknown_0x1b07123d),
    0x52f88637: ('unknown_0x52f88637', _decode_unknown_0x52f88637),
    0x413b2f46: ('unknown_0x413b2f46', _decode_unknown_0x413b2f46),
    0x5a7ca693: ('unknown_0x5a7ca693', _decode_unknown_0x5a7ca693),
    0x9acd94e4: ('unknown_0x9acd94e4', _decode_unknown_0x9acd94e4),
}
