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
    class UnknownStruct29Json(typing_extensions.TypedDict):
        blinking_enabled: bool
        unknown_0x9b131110: float
        unknown_0xa5a6d998: float
        unknown_0xd9f6253b: int
        unknown_0x0896fde0: float
        unknown_0x5f98ada3: float
        unknown_0xc3230652: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x47c836c5, 0x9b131110, 0xa5a6d998, 0xd9f6253b, 0x896fde0, 0x5f98ada3, 0xc3230652)


@dataclasses.dataclass()
class UnknownStruct29(BaseProperty):
    blinking_enabled: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x47c836c5, original_name='BlinkingEnabled'
        ),
    })
    unknown_0x9b131110: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9b131110, original_name='Unknown'
        ),
    })
    unknown_0xa5a6d998: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa5a6d998, original_name='Unknown'
        ),
    })
    unknown_0xd9f6253b: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd9f6253b, original_name='Unknown'
        ),
    })
    unknown_0x0896fde0: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0896fde0, original_name='Unknown'
        ),
    })
    unknown_0x5f98ada3: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5f98ada3, original_name='Unknown'
        ),
    })
    unknown_0xc3230652: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3230652, original_name='Unknown'
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
            _FAST_FORMAT = struct.Struct('>LH?LHfLHfLHlLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(67))
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

        data.write(b'G\xc86\xc5')  # 0x47c836c5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.blinking_enabled))

        data.write(b'\x9b\x13\x11\x10')  # 0x9b131110
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9b131110))

        data.write(b'\xa5\xa6\xd9\x98')  # 0xa5a6d998
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa5a6d998))

        data.write(b'\xd9\xf6%;')  # 0xd9f6253b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xd9f6253b))

        data.write(b'\x08\x96\xfd\xe0')  # 0x896fde0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0896fde0))

        data.write(b'_\x98\xad\xa3')  # 0x5f98ada3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5f98ada3))

        data.write(b'\xc3#\x06R')  # 0xc3230652
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc3230652))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct29Json", data)
        return cls(
            blinking_enabled=json_data['blinking_enabled'],
            unknown_0x9b131110=json_data['unknown_0x9b131110'],
            unknown_0xa5a6d998=json_data['unknown_0xa5a6d998'],
            unknown_0xd9f6253b=json_data['unknown_0xd9f6253b'],
            unknown_0x0896fde0=json_data['unknown_0x0896fde0'],
            unknown_0x5f98ada3=json_data['unknown_0x5f98ada3'],
            unknown_0xc3230652=json_data['unknown_0xc3230652'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'blinking_enabled': self.blinking_enabled,
            'unknown_0x9b131110': self.unknown_0x9b131110,
            'unknown_0xa5a6d998': self.unknown_0xa5a6d998,
            'unknown_0xd9f6253b': self.unknown_0xd9f6253b,
            'unknown_0x0896fde0': self.unknown_0x0896fde0,
            'unknown_0x5f98ada3': self.unknown_0x5f98ada3,
            'unknown_0xc3230652': self.unknown_0xc3230652,
        }


def _decode_blinking_enabled(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x9b131110(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa5a6d998(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd9f6253b(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x0896fde0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5f98ada3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc3230652(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x47c836c5: ('blinking_enabled', _decode_blinking_enabled),
    0x9b131110: ('unknown_0x9b131110', _decode_unknown_0x9b131110),
    0xa5a6d998: ('unknown_0xa5a6d998', _decode_unknown_0xa5a6d998),
    0xd9f6253b: ('unknown_0xd9f6253b', _decode_unknown_0xd9f6253b),
    0x896fde0: ('unknown_0x0896fde0', _decode_unknown_0x0896fde0),
    0x5f98ada3: ('unknown_0x5f98ada3', _decode_unknown_0x5f98ada3),
    0xc3230652: ('unknown_0xc3230652', _decode_unknown_0xc3230652),
}
