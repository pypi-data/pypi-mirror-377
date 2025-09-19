# Generated File
from __future__ import annotations

import dataclasses
import enum
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

    class VisorParametersJson(typing_extensions.TypedDict):
        unknown_1: bool
        unknown_2: bool
        visor_flags: int
    

class VisorFlags(enum.IntFlag):
    Combat = 1
    Scan = 2
    Thermal = 4
    XRay = 8

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


@dataclasses.dataclass()
class VisorParameters(BaseProperty):
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000000, original_name='Unknown 1'
        ),
    })
    unknown_2: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000001, original_name='Unknown 2'
        ),
    })
    visor_flags: VisorFlags = dataclasses.field(default=VisorFlags(0), metadata={
        'reflection': FieldReflection[VisorFlags](
            VisorFlags, id=0x00000002, original_name='Visor Flags', from_json=VisorFlags.from_json, to_json=VisorFlags.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unknown_2 = struct.unpack('>?', data.read(1))[0]
        visor_flags = VisorFlags.from_stream(data)
        return cls(unknown_1, unknown_2, visor_flags)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>?', self.unknown_1))
        data.write(struct.pack('>?', self.unknown_2))
        self.visor_flags.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("VisorParametersJson", data)
        return cls(
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            visor_flags=VisorFlags.from_json(json_data['visor_flags']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'visor_flags': self.visor_flags.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
