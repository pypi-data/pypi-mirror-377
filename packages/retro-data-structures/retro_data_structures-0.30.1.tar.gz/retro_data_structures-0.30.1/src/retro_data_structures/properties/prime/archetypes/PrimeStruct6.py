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
from retro_data_structures.properties.prime.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.prime.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class PrimeStruct6Json(typing_extensions.TypedDict):
        unnamed: json_util.JsonObject
        unknown_1: json_util.JsonValue
        unknown_2: int
        unknown_3: int
    

@dataclasses.dataclass()
class PrimeStruct6(BaseProperty):
    unnamed: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x00000000, original_name='0', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_1: Color = dataclasses.field(default_factory=Color, metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x00000001, original_name='Unknown 1', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_2: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000002, original_name='Unknown 2'
        ),
    })
    unknown_3: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000003, original_name='Unknown 3'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        unnamed = DamageVulnerability.from_stream(data, property_size)
        unknown_1 = Color.from_stream(data)
        unknown_2 = struct.unpack('>l', data.read(4))[0]
        unknown_3 = struct.unpack('>l', data.read(4))[0]
        return cls(unnamed, unknown_1, unknown_2, unknown_3)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        self.unnamed.to_stream(data)
        self.unknown_1.to_stream(data)
        data.write(struct.pack('>l', self.unknown_2))
        data.write(struct.pack('>l', self.unknown_3))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PrimeStruct6Json", data)
        return cls(
            unnamed=DamageVulnerability.from_json(json_data['unnamed']),
            unknown_1=Color.from_json(json_data['unknown_1']),
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unnamed': self.unnamed.to_json(),
            'unknown_1': self.unknown_1.to_json(),
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed.dependencies_for, "unnamed", "DamageVulnerability"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for PrimeStruct6.{field_name} ({field_type}): {e}"
                )
