# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
import retro_data_structures.enums.prime as enums

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class PlayerStateChangeJson(typing_extensions.TypedDict):
        name: str
        active: bool
        unnamed: int
        amount: int
        capacity: int
        unknown_4: int
        unknown_5: int
    

@dataclasses.dataclass()
class PlayerStateChange(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000001, original_name='Active'
        ),
    })
    unnamed: enums.PlayerItemEnum = dataclasses.field(default=enums.PlayerItemEnum.PowerBeam, metadata={
        'reflection': FieldReflection[enums.PlayerItemEnum](
            enums.PlayerItemEnum, id=0x00000002, original_name='2', from_json=enums.PlayerItemEnum.from_json, to_json=enums.PlayerItemEnum.to_json
        ),
    })
    amount: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000003, original_name='Amount'
        ),
    })
    capacity: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000004, original_name='Capacity'
        ),
    })
    unknown_4: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000005, original_name='Unknown 4'
        ),
    })
    unknown_5: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000006, original_name='Unknown 5'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    def get_name(self) -> str | None:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    @classmethod
    def object_type(cls) -> int:
        return 0x57

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        active = struct.unpack('>?', data.read(1))[0]
        unnamed = enums.PlayerItemEnum.from_stream(data)
        amount = struct.unpack('>l', data.read(4))[0]
        capacity = struct.unpack('>l', data.read(4))[0]
        unknown_4 = struct.unpack('>l', data.read(4))[0]
        unknown_5 = struct.unpack('>l', data.read(4))[0]
        return cls(name, active, unnamed, amount, capacity, unknown_4, unknown_5)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x07')  # 7 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>?', self.active))
        self.unnamed.to_stream(data)
        data.write(struct.pack('>l', self.amount))
        data.write(struct.pack('>l', self.capacity))
        data.write(struct.pack('>l', self.unknown_4))
        data.write(struct.pack('>l', self.unknown_5))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PlayerStateChangeJson", data)
        return cls(
            name=json_data['name'],
            active=json_data['active'],
            unnamed=enums.PlayerItemEnum.from_json(json_data['unnamed']),
            amount=json_data['amount'],
            capacity=json_data['capacity'],
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'active': self.active,
            'unnamed': self.unnamed.to_json(),
            'amount': self.amount,
            'capacity': self.capacity,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
