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
    class SeedBoss1ActionJson(typing_extensions.TypedDict):
        enabled: bool
        chance: float
        modifier: float
        min_range: float
        max_range: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x29c77d27, 0x7a7b330e, 0xed2d546f, 0x9744971e, 0xd70bef68)


@dataclasses.dataclass()
class SeedBoss1Action(BaseProperty):
    enabled: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x29c77d27, original_name='Enabled'
        ),
    })
    chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a7b330e, original_name='Chance'
        ),
    })
    modifier: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed2d546f, original_name='Modifier'
        ),
    })
    min_range: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9744971e, original_name='MinRange'
        ),
    })
    max_range: float = dataclasses.field(default=1000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd70bef68, original_name='MaxRange'
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
            _FAST_FORMAT = struct.Struct('>LH?LHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(47))
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

        data.write(b")\xc7}'")  # 0x29c77d27
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.enabled))

        data.write(b'z{3\x0e')  # 0x7a7b330e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.chance))

        data.write(b'\xed-To')  # 0xed2d546f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.modifier))

        data.write(b'\x97D\x97\x1e')  # 0x9744971e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_range))

        data.write(b'\xd7\x0b\xefh')  # 0xd70bef68
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_range))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SeedBoss1ActionJson", data)
        return cls(
            enabled=json_data['enabled'],
            chance=json_data['chance'],
            modifier=json_data['modifier'],
            min_range=json_data['min_range'],
            max_range=json_data['max_range'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'enabled': self.enabled,
            'chance': self.chance,
            'modifier': self.modifier,
            'min_range': self.min_range,
            'max_range': self.max_range,
        }


def _decode_enabled(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_modifier(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x29c77d27: ('enabled', _decode_enabled),
    0x7a7b330e: ('chance', _decode_chance),
    0xed2d546f: ('modifier', _decode_modifier),
    0x9744971e: ('min_range', _decode_min_range),
    0xd70bef68: ('max_range', _decode_max_range),
}
