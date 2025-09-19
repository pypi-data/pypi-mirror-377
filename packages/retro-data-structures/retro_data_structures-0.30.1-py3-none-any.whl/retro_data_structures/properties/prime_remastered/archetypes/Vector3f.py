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
    class Vector3fJson(typing_extensions.TypedDict):
        x: float
        y: float
        z: float
    

@dataclasses.dataclass()
class Vector3f(BaseProperty):
    x: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000000, original_name='x'
        ),
    })
    y: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000001, original_name='y'
        ),
    })
    z: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000002, original_name='z'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME_REMASTER

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        x = struct.unpack('<f', data.read(4))[0]
        y = struct.unpack('<f', data.read(4))[0]
        z = struct.unpack('<f', data.read(4))[0]
        return cls(x, y, z)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('<f', self.x))
        data.write(struct.pack('<f', self.y))
        data.write(struct.pack('<f', self.z))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("Vector3fJson", data)
        return cls(
            x=json_data['x'],
            y=json_data['y'],
            z=json_data['z'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
        }
