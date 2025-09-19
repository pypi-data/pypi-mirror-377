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

if typing.TYPE_CHECKING:
    class UnknownStruct63Json(typing_extensions.TypedDict):
        unknown_0x04131a2a: int
        unknown_0x868cfe92: bool
        unknown_0xf1943b5a: bool
        unknown_0x44bf1dc9: int
        unknown_0x7c538ed3: int
        unknown_0xfcd2a1a0: int
        unknown_0x1aec3e02: int
        unknown_0xe0e4573d: int
        unknown_0x21103ec1: int
        unknown_0xc7c06435: int
    

class Unknown(enum.IntEnum):
    Unknown1 = 2868300453
    Unknown2 = 881720149
    Unknown3 = 1464639200

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


_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x4131a2a, 0x868cfe92, 0xf1943b5a, 0x44bf1dc9, 0x7c538ed3, 0xfcd2a1a0, 0x1aec3e02, 0xe0e4573d, 0x21103ec1, 0xc7c06435)


@dataclasses.dataclass()
class UnknownStruct63(BaseProperty):
    unknown_0x04131a2a: Unknown = dataclasses.field(default=Unknown.Unknown1, metadata={
        'reflection': FieldReflection[Unknown](
            Unknown, id=0x04131a2a, original_name='Unknown', from_json=Unknown.from_json, to_json=Unknown.to_json
        ),
    })
    unknown_0x868cfe92: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x868cfe92, original_name='Unknown'
        ),
    })
    unknown_0xf1943b5a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf1943b5a, original_name='Unknown'
        ),
    })
    unknown_0x44bf1dc9: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x44bf1dc9, original_name='Unknown'
        ),
    })
    unknown_0x7c538ed3: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7c538ed3, original_name='Unknown'
        ),
    })
    unknown_0xfcd2a1a0: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xfcd2a1a0, original_name='Unknown'
        ),
    })
    unknown_0x1aec3e02: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1aec3e02, original_name='Unknown'
        ),
    })
    unknown_0xe0e4573d: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe0e4573d, original_name='Unknown'
        ),
    })
    unknown_0x21103ec1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x21103ec1, original_name='Unknown'
        ),
    })
    unknown_0xc7c06435: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc7c06435, original_name='Unknown'
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
        if property_count != 10:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHLLH?LH?LHlLHlLHlLHlLHlLHlLHl')
    
        dec = _FAST_FORMAT.unpack(data.read(94))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27]) == _FAST_IDS
        return cls(
            Unknown(dec[2]),
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
            dec[23],
            dec[26],
            dec[29],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\n')  # 10 properties

        data.write(b'\x04\x13\x1a*')  # 0x4131a2a
        data.write(b'\x00\x04')  # size
        self.unknown_0x04131a2a.to_stream(data)

        data.write(b'\x86\x8c\xfe\x92')  # 0x868cfe92
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x868cfe92))

        data.write(b'\xf1\x94;Z')  # 0xf1943b5a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xf1943b5a))

        data.write(b'D\xbf\x1d\xc9')  # 0x44bf1dc9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x44bf1dc9))

        data.write(b'|S\x8e\xd3')  # 0x7c538ed3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x7c538ed3))

        data.write(b'\xfc\xd2\xa1\xa0')  # 0xfcd2a1a0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xfcd2a1a0))

        data.write(b'\x1a\xec>\x02')  # 0x1aec3e02
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x1aec3e02))

        data.write(b'\xe0\xe4W=')  # 0xe0e4573d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xe0e4573d))

        data.write(b'!\x10>\xc1')  # 0x21103ec1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x21103ec1))

        data.write(b'\xc7\xc0d5')  # 0xc7c06435
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc7c06435))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct63Json", data)
        return cls(
            unknown_0x04131a2a=Unknown.from_json(json_data['unknown_0x04131a2a']),
            unknown_0x868cfe92=json_data['unknown_0x868cfe92'],
            unknown_0xf1943b5a=json_data['unknown_0xf1943b5a'],
            unknown_0x44bf1dc9=json_data['unknown_0x44bf1dc9'],
            unknown_0x7c538ed3=json_data['unknown_0x7c538ed3'],
            unknown_0xfcd2a1a0=json_data['unknown_0xfcd2a1a0'],
            unknown_0x1aec3e02=json_data['unknown_0x1aec3e02'],
            unknown_0xe0e4573d=json_data['unknown_0xe0e4573d'],
            unknown_0x21103ec1=json_data['unknown_0x21103ec1'],
            unknown_0xc7c06435=json_data['unknown_0xc7c06435'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x04131a2a': self.unknown_0x04131a2a.to_json(),
            'unknown_0x868cfe92': self.unknown_0x868cfe92,
            'unknown_0xf1943b5a': self.unknown_0xf1943b5a,
            'unknown_0x44bf1dc9': self.unknown_0x44bf1dc9,
            'unknown_0x7c538ed3': self.unknown_0x7c538ed3,
            'unknown_0xfcd2a1a0': self.unknown_0xfcd2a1a0,
            'unknown_0x1aec3e02': self.unknown_0x1aec3e02,
            'unknown_0xe0e4573d': self.unknown_0xe0e4573d,
            'unknown_0x21103ec1': self.unknown_0x21103ec1,
            'unknown_0xc7c06435': self.unknown_0xc7c06435,
        }


def _decode_unknown_0x04131a2a(data: typing.BinaryIO, property_size: int) -> Unknown:
    return Unknown.from_stream(data)


def _decode_unknown_0x868cfe92(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xf1943b5a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x44bf1dc9(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x7c538ed3(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xfcd2a1a0(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x1aec3e02(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xe0e4573d(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x21103ec1(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xc7c06435(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x4131a2a: ('unknown_0x04131a2a', _decode_unknown_0x04131a2a),
    0x868cfe92: ('unknown_0x868cfe92', _decode_unknown_0x868cfe92),
    0xf1943b5a: ('unknown_0xf1943b5a', _decode_unknown_0xf1943b5a),
    0x44bf1dc9: ('unknown_0x44bf1dc9', _decode_unknown_0x44bf1dc9),
    0x7c538ed3: ('unknown_0x7c538ed3', _decode_unknown_0x7c538ed3),
    0xfcd2a1a0: ('unknown_0xfcd2a1a0', _decode_unknown_0xfcd2a1a0),
    0x1aec3e02: ('unknown_0x1aec3e02', _decode_unknown_0x1aec3e02),
    0xe0e4573d: ('unknown_0xe0e4573d', _decode_unknown_0xe0e4573d),
    0x21103ec1: ('unknown_0x21103ec1', _decode_unknown_0x21103ec1),
    0xc7c06435: ('unknown_0xc7c06435', _decode_unknown_0xc7c06435),
}
