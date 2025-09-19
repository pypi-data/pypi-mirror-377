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

    class IntBoolJson(typing_extensions.TypedDict):
        unknown_1: int
        unknown_2: bool
    

@dataclasses.dataclass()
class IntBool(BaseProperty):
    unknown_1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000000, original_name='Unknown 1'
        ),
    })
    unknown_2: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000001, original_name='Unknown 2'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        unknown_1 = struct.unpack('>l', data.read(4))[0]
        unknown_2 = struct.unpack('>?', data.read(1))[0]
        return cls(unknown_1, unknown_2)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>l', self.unknown_1))
        data.write(struct.pack('>?', self.unknown_2))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("IntBoolJson", data)
        return cls(
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
