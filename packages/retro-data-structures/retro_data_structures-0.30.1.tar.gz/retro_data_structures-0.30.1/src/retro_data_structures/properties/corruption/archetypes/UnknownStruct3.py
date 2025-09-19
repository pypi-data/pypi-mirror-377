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
from retro_data_structures.properties.corruption.archetypes.SpacePirateWeaponData import SpacePirateWeaponData

if typing.TYPE_CHECKING:
    class UnknownStruct3Json(typing_extensions.TypedDict):
        min_attack_range: float
        max_attack_range: float
        unknown_0xef6d8f65: float
        unknown_0xdb93d177: float
        unknown_0x0d49855c: float
        unknown_0x9dce6b35: float
        min_attack_time: float
        max_attack_time: float
        pickup_chance: float
        weapon_data: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct3(BaseProperty):
    min_attack_range: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x58434916, original_name='MinAttackRange'
        ),
    })
    max_attack_range: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xff77c96f, original_name='MaxAttackRange'
        ),
    })
    unknown_0xef6d8f65: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xef6d8f65, original_name='Unknown'
        ),
    })
    unknown_0xdb93d177: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdb93d177, original_name='Unknown'
        ),
    })
    unknown_0x0d49855c: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d49855c, original_name='Unknown'
        ),
    })
    unknown_0x9dce6b35: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9dce6b35, original_name='Unknown'
        ),
    })
    min_attack_time: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2edf3368, original_name='MinAttackTime'
        ),
    })
    max_attack_time: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d792b8c, original_name='MaxAttackTime'
        ),
    })
    pickup_chance: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6509d9b2, original_name='PickupChance'
        ),
    })
    weapon_data: SpacePirateWeaponData = dataclasses.field(default_factory=SpacePirateWeaponData, metadata={
        'reflection': FieldReflection[SpacePirateWeaponData](
            SpacePirateWeaponData, id=0xdc89cc3c, original_name='WeaponData', from_json=SpacePirateWeaponData.from_json, to_json=SpacePirateWeaponData.to_json
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
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58434916
        min_attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xff77c96f
        max_attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef6d8f65
        unknown_0xef6d8f65 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdb93d177
        unknown_0xdb93d177 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d49855c
        unknown_0x0d49855c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9dce6b35
        unknown_0x9dce6b35 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2edf3368
        min_attack_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d792b8c
        max_attack_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6509d9b2
        pickup_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdc89cc3c
        weapon_data = SpacePirateWeaponData.from_stream(data, property_size)
    
        return cls(min_attack_range, max_attack_range, unknown_0xef6d8f65, unknown_0xdb93d177, unknown_0x0d49855c, unknown_0x9dce6b35, min_attack_time, max_attack_time, pickup_chance, weapon_data)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\n')  # 10 properties

        data.write(b'XCI\x16')  # 0x58434916
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_range))

        data.write(b'\xffw\xc9o')  # 0xff77c96f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_range))

        data.write(b'\xefm\x8fe')  # 0xef6d8f65
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xef6d8f65))

        data.write(b'\xdb\x93\xd1w')  # 0xdb93d177
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdb93d177))

        data.write(b'\rI\x85\\')  # 0xd49855c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0d49855c))

        data.write(b'\x9d\xcek5')  # 0x9dce6b35
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9dce6b35))

        data.write(b'.\xdf3h')  # 0x2edf3368
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_time))

        data.write(b'}y+\x8c')  # 0x7d792b8c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_time))

        data.write(b'e\t\xd9\xb2')  # 0x6509d9b2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pickup_chance))

        data.write(b'\xdc\x89\xcc<')  # 0xdc89cc3c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weapon_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct3Json", data)
        return cls(
            min_attack_range=json_data['min_attack_range'],
            max_attack_range=json_data['max_attack_range'],
            unknown_0xef6d8f65=json_data['unknown_0xef6d8f65'],
            unknown_0xdb93d177=json_data['unknown_0xdb93d177'],
            unknown_0x0d49855c=json_data['unknown_0x0d49855c'],
            unknown_0x9dce6b35=json_data['unknown_0x9dce6b35'],
            min_attack_time=json_data['min_attack_time'],
            max_attack_time=json_data['max_attack_time'],
            pickup_chance=json_data['pickup_chance'],
            weapon_data=SpacePirateWeaponData.from_json(json_data['weapon_data']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'min_attack_range': self.min_attack_range,
            'max_attack_range': self.max_attack_range,
            'unknown_0xef6d8f65': self.unknown_0xef6d8f65,
            'unknown_0xdb93d177': self.unknown_0xdb93d177,
            'unknown_0x0d49855c': self.unknown_0x0d49855c,
            'unknown_0x9dce6b35': self.unknown_0x9dce6b35,
            'min_attack_time': self.min_attack_time,
            'max_attack_time': self.max_attack_time,
            'pickup_chance': self.pickup_chance,
            'weapon_data': self.weapon_data.to_json(),
        }


def _decode_min_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xef6d8f65(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdb93d177(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0d49855c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9dce6b35(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pickup_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x58434916: ('min_attack_range', _decode_min_attack_range),
    0xff77c96f: ('max_attack_range', _decode_max_attack_range),
    0xef6d8f65: ('unknown_0xef6d8f65', _decode_unknown_0xef6d8f65),
    0xdb93d177: ('unknown_0xdb93d177', _decode_unknown_0xdb93d177),
    0xd49855c: ('unknown_0x0d49855c', _decode_unknown_0x0d49855c),
    0x9dce6b35: ('unknown_0x9dce6b35', _decode_unknown_0x9dce6b35),
    0x2edf3368: ('min_attack_time', _decode_min_attack_time),
    0x7d792b8c: ('max_attack_time', _decode_max_attack_time),
    0x6509d9b2: ('pickup_chance', _decode_pickup_chance),
    0xdc89cc3c: ('weapon_data', SpacePirateWeaponData.from_stream),
}
