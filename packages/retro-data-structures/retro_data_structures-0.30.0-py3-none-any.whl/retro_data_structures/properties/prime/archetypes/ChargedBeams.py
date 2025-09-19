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
import retro_data_structures.enums.prime as enums

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ChargedBeamsJson(typing_extensions.TypedDict):
        power: int
        ice: int
        wave: int
        plasma: int
        phazon: int
    

@dataclasses.dataclass()
class ChargedBeams(BaseProperty):
    power: enums.VulnerabilityTypeEnum = dataclasses.field(default=enums.VulnerabilityTypeEnum.DoubleDamage, metadata={
        'reflection': FieldReflection[enums.VulnerabilityTypeEnum](
            enums.VulnerabilityTypeEnum, id=0x00000000, original_name='Power', from_json=enums.VulnerabilityTypeEnum.from_json, to_json=enums.VulnerabilityTypeEnum.to_json
        ),
    })
    ice: enums.VulnerabilityTypeEnum = dataclasses.field(default=enums.VulnerabilityTypeEnum.DoubleDamage, metadata={
        'reflection': FieldReflection[enums.VulnerabilityTypeEnum](
            enums.VulnerabilityTypeEnum, id=0x00000001, original_name='Ice', from_json=enums.VulnerabilityTypeEnum.from_json, to_json=enums.VulnerabilityTypeEnum.to_json
        ),
    })
    wave: enums.VulnerabilityTypeEnum = dataclasses.field(default=enums.VulnerabilityTypeEnum.DoubleDamage, metadata={
        'reflection': FieldReflection[enums.VulnerabilityTypeEnum](
            enums.VulnerabilityTypeEnum, id=0x00000002, original_name='Wave', from_json=enums.VulnerabilityTypeEnum.from_json, to_json=enums.VulnerabilityTypeEnum.to_json
        ),
    })
    plasma: enums.VulnerabilityTypeEnum = dataclasses.field(default=enums.VulnerabilityTypeEnum.DoubleDamage, metadata={
        'reflection': FieldReflection[enums.VulnerabilityTypeEnum](
            enums.VulnerabilityTypeEnum, id=0x00000003, original_name='Plasma', from_json=enums.VulnerabilityTypeEnum.from_json, to_json=enums.VulnerabilityTypeEnum.to_json
        ),
    })
    phazon: enums.VulnerabilityTypeEnum = dataclasses.field(default=enums.VulnerabilityTypeEnum.DoubleDamage, metadata={
        'reflection': FieldReflection[enums.VulnerabilityTypeEnum](
            enums.VulnerabilityTypeEnum, id=0x00000004, original_name='Phazon', from_json=enums.VulnerabilityTypeEnum.from_json, to_json=enums.VulnerabilityTypeEnum.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        power = enums.VulnerabilityTypeEnum.from_stream(data)
        ice = enums.VulnerabilityTypeEnum.from_stream(data)
        wave = enums.VulnerabilityTypeEnum.from_stream(data)
        plasma = enums.VulnerabilityTypeEnum.from_stream(data)
        phazon = enums.VulnerabilityTypeEnum.from_stream(data)
        return cls(power, ice, wave, plasma, phazon)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        self.power.to_stream(data)
        self.ice.to_stream(data)
        self.wave.to_stream(data)
        self.plasma.to_stream(data)
        self.phazon.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ChargedBeamsJson", data)
        return cls(
            power=enums.VulnerabilityTypeEnum.from_json(json_data['power']),
            ice=enums.VulnerabilityTypeEnum.from_json(json_data['ice']),
            wave=enums.VulnerabilityTypeEnum.from_json(json_data['wave']),
            plasma=enums.VulnerabilityTypeEnum.from_json(json_data['plasma']),
            phazon=enums.VulnerabilityTypeEnum.from_json(json_data['phazon']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'power': self.power.to_json(),
            'ice': self.ice.to_json(),
            'wave': self.wave.to_json(),
            'plasma': self.plasma.to_json(),
            'phazon': self.phazon.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
