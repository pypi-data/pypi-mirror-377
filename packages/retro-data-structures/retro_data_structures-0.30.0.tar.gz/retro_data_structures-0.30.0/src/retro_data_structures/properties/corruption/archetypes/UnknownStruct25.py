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
    class UnknownStruct25Json(typing_extensions.TypedDict):
        start_on_task: bool
        cover_search_radius: float
        unknown_0x95e7a2c2: float
        unknown_0x76ba1c18: float
        min_attack_time: float
        max_attack_time: float
        unknown_0x1109ad02: float
        unknown_0x15939c28: float
        unknown_0x761ed7af: int
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x1c81f07, 0x820cf2de, 0x95e7a2c2, 0x76ba1c18, 0x2edf3368, 0x7d792b8c, 0x1109ad02, 0x15939c28, 0x761ed7af)


@dataclasses.dataclass()
class UnknownStruct25(BaseProperty):
    start_on_task: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x01c81f07, original_name='StartOnTask'
        ),
    })
    cover_search_radius: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x820cf2de, original_name='CoverSearchRadius'
        ),
    })
    unknown_0x95e7a2c2: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95e7a2c2, original_name='Unknown'
        ),
    })
    unknown_0x76ba1c18: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x76ba1c18, original_name='Unknown'
        ),
    })
    min_attack_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2edf3368, original_name='MinAttackTime'
        ),
    })
    max_attack_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d792b8c, original_name='MaxAttackTime'
        ),
    })
    unknown_0x1109ad02: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1109ad02, original_name='Unknown'
        ),
    })
    unknown_0x15939c28: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x15939c28, original_name='Unknown'
        ),
    })
    unknown_0x761ed7af: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x761ed7af, original_name='Unknown'
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
        if property_count != 9:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LH?LHfLHfLHfLHfLHfLHfLHfLHl')
    
        dec = _FAST_FORMAT.unpack(data.read(87))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
            dec[23],
            dec[26],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\t')  # 9 properties

        data.write(b'\x01\xc8\x1f\x07')  # 0x1c81f07
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.start_on_task))

        data.write(b'\x82\x0c\xf2\xde')  # 0x820cf2de
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cover_search_radius))

        data.write(b'\x95\xe7\xa2\xc2')  # 0x95e7a2c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95e7a2c2))

        data.write(b'v\xba\x1c\x18')  # 0x76ba1c18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x76ba1c18))

        data.write(b'.\xdf3h')  # 0x2edf3368
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_time))

        data.write(b'}y+\x8c')  # 0x7d792b8c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_time))

        data.write(b'\x11\t\xad\x02')  # 0x1109ad02
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1109ad02))

        data.write(b'\x15\x93\x9c(')  # 0x15939c28
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x15939c28))

        data.write(b'v\x1e\xd7\xaf')  # 0x761ed7af
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x761ed7af))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct25Json", data)
        return cls(
            start_on_task=json_data['start_on_task'],
            cover_search_radius=json_data['cover_search_radius'],
            unknown_0x95e7a2c2=json_data['unknown_0x95e7a2c2'],
            unknown_0x76ba1c18=json_data['unknown_0x76ba1c18'],
            min_attack_time=json_data['min_attack_time'],
            max_attack_time=json_data['max_attack_time'],
            unknown_0x1109ad02=json_data['unknown_0x1109ad02'],
            unknown_0x15939c28=json_data['unknown_0x15939c28'],
            unknown_0x761ed7af=json_data['unknown_0x761ed7af'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'start_on_task': self.start_on_task,
            'cover_search_radius': self.cover_search_radius,
            'unknown_0x95e7a2c2': self.unknown_0x95e7a2c2,
            'unknown_0x76ba1c18': self.unknown_0x76ba1c18,
            'min_attack_time': self.min_attack_time,
            'max_attack_time': self.max_attack_time,
            'unknown_0x1109ad02': self.unknown_0x1109ad02,
            'unknown_0x15939c28': self.unknown_0x15939c28,
            'unknown_0x761ed7af': self.unknown_0x761ed7af,
        }


def _decode_start_on_task(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_cover_search_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x95e7a2c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x76ba1c18(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1109ad02(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x15939c28(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x761ed7af(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1c81f07: ('start_on_task', _decode_start_on_task),
    0x820cf2de: ('cover_search_radius', _decode_cover_search_radius),
    0x95e7a2c2: ('unknown_0x95e7a2c2', _decode_unknown_0x95e7a2c2),
    0x76ba1c18: ('unknown_0x76ba1c18', _decode_unknown_0x76ba1c18),
    0x2edf3368: ('min_attack_time', _decode_min_attack_time),
    0x7d792b8c: ('max_attack_time', _decode_max_attack_time),
    0x1109ad02: ('unknown_0x1109ad02', _decode_unknown_0x1109ad02),
    0x15939c28: ('unknown_0x15939c28', _decode_unknown_0x15939c28),
    0x761ed7af: ('unknown_0x761ed7af', _decode_unknown_0x761ed7af),
}
