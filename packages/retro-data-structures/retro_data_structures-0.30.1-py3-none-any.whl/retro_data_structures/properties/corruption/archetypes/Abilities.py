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
    class AbilitiesJson(typing_extensions.TypedDict):
        double_jump: bool
        suit_type: int
        screw_attack: int
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x9dc3cdd, 0xc0bd8a5e, 0x5a066e2c)


@dataclasses.dataclass()
class Abilities(BaseProperty):
    double_jump: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x09dc3cdd, original_name='DoubleJump'
        ),
    })
    suit_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc0bd8a5e, original_name='SuitType'
        ),
    })
    screw_attack: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5a066e2c, original_name='ScrewAttack'
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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LH?LHlLHl')
    
        dec = _FAST_FORMAT.unpack(data.read(27))
        assert (dec[0], dec[3], dec[6]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\t\xdc<\xdd')  # 0x9dc3cdd
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.double_jump))

        data.write(b'\xc0\xbd\x8a^')  # 0xc0bd8a5e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.suit_type))

        data.write(b'Z\x06n,')  # 0x5a066e2c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.screw_attack))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AbilitiesJson", data)
        return cls(
            double_jump=json_data['double_jump'],
            suit_type=json_data['suit_type'],
            screw_attack=json_data['screw_attack'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'double_jump': self.double_jump,
            'suit_type': self.suit_type,
            'screw_attack': self.screw_attack,
        }


def _decode_double_jump(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_suit_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_screw_attack(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x9dc3cdd: ('double_jump', _decode_double_jump),
    0xc0bd8a5e: ('suit_type', _decode_suit_type),
    0x5a066e2c: ('screw_attack', _decode_screw_attack),
}
