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
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class IngSpaceJumpGuardianStructJson(typing_extensions.TypedDict):
        taunt_chance: float
        attack_chance: float
        unknown_0x03698c10: float
        locomotion_speed: float
        unknown_0x3e370622: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xa77f6212, 0x7eaf8d70, 0x3698c10, 0xfd46b85c, 0x3e370622)


@dataclasses.dataclass()
class IngSpaceJumpGuardianStruct(BaseProperty):
    taunt_chance: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa77f6212, original_name='TauntChance'
        ),
    })
    attack_chance: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7eaf8d70, original_name='AttackChance'
        ),
    })
    unknown_0x03698c10: float = dataclasses.field(default=33.29999923706055, metadata={
        'reflection': FieldReflection[float](
            float, id=0x03698c10, original_name='Unknown'
        ),
    })
    locomotion_speed: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfd46b85c, original_name='LocomotionSpeed'
        ),
    })
    unknown_0x3e370622: float = dataclasses.field(default=1500.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3e370622, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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

        data.write(b'\xa7\x7fb\x12')  # 0xa77f6212
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.taunt_chance))

        data.write(b'~\xaf\x8dp')  # 0x7eaf8d70
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_chance))

        data.write(b'\x03i\x8c\x10')  # 0x3698c10
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x03698c10))

        data.write(b'\xfdF\xb8\\')  # 0xfd46b85c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.locomotion_speed))

        data.write(b'>7\x06"')  # 0x3e370622
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3e370622))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("IngSpaceJumpGuardianStructJson", data)
        return cls(
            taunt_chance=json_data['taunt_chance'],
            attack_chance=json_data['attack_chance'],
            unknown_0x03698c10=json_data['unknown_0x03698c10'],
            locomotion_speed=json_data['locomotion_speed'],
            unknown_0x3e370622=json_data['unknown_0x3e370622'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'taunt_chance': self.taunt_chance,
            'attack_chance': self.attack_chance,
            'unknown_0x03698c10': self.unknown_0x03698c10,
            'locomotion_speed': self.locomotion_speed,
            'unknown_0x3e370622': self.unknown_0x3e370622,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_taunt_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x03698c10(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_locomotion_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3e370622(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xa77f6212: ('taunt_chance', _decode_taunt_chance),
    0x7eaf8d70: ('attack_chance', _decode_attack_chance),
    0x3698c10: ('unknown_0x03698c10', _decode_unknown_0x03698c10),
    0xfd46b85c: ('locomotion_speed', _decode_locomotion_speed),
    0x3e370622: ('unknown_0x3e370622', _decode_unknown_0x3e370622),
}
