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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ThermalHeatFaderJson(typing_extensions.TypedDict):
        name: str
        active: bool
        faded_heat_level: float
        initial_heat_level: float
    

@dataclasses.dataclass()
class ThermalHeatFader(BaseObjectType):
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
    faded_heat_level: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000002, original_name='Faded Heat Level'
        ),
    })
    initial_heat_level: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000003, original_name='Initial Heat Level'
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
        return 0x7D

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        active = struct.unpack('>?', data.read(1))[0]
        faded_heat_level = struct.unpack('>f', data.read(4))[0]
        initial_heat_level = struct.unpack('>f', data.read(4))[0]
        return cls(name, active, faded_heat_level, initial_heat_level)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x04')  # 4 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>?', self.active))
        data.write(struct.pack('>f', self.faded_heat_level))
        data.write(struct.pack('>f', self.initial_heat_level))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ThermalHeatFaderJson", data)
        return cls(
            name=json_data['name'],
            active=json_data['active'],
            faded_heat_level=json_data['faded_heat_level'],
            initial_heat_level=json_data['initial_heat_level'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'active': self.active,
            'faded_heat_level': self.faded_heat_level,
            'initial_heat_level': self.initial_heat_level,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
