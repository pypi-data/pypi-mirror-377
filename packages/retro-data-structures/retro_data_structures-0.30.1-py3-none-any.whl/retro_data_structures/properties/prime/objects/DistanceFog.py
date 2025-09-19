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
from retro_data_structures.properties.prime.archetypes.Vector2f import Vector2f
from retro_data_structures.properties.prime.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DistanceFogJson(typing_extensions.TypedDict):
        name: str
        mode: int
        color: json_util.JsonValue
        range: json_util.JsonObject
        color_delta: float
        range_delta: json_util.JsonObject
        explicit: bool
        active: bool
    

@dataclasses.dataclass()
class DistanceFog(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    mode: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000001, original_name='Mode'
        ),
    })
    color: Color = dataclasses.field(default_factory=Color, metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x00000002, original_name='Color', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    range: Vector2f = dataclasses.field(default_factory=Vector2f, metadata={
        'reflection': FieldReflection[Vector2f](
            Vector2f, id=0x00000003, original_name='Range', from_json=Vector2f.from_json, to_json=Vector2f.to_json
        ),
    })
    color_delta: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000004, original_name='Color Delta'
        ),
    })
    range_delta: Vector2f = dataclasses.field(default_factory=Vector2f, metadata={
        'reflection': FieldReflection[Vector2f](
            Vector2f, id=0x00000005, original_name='Range Delta', from_json=Vector2f.from_json, to_json=Vector2f.to_json
        ),
    })
    explicit: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000006, original_name='Explicit'
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000007, original_name='Active'
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
        return 0x35

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        mode = struct.unpack('>l', data.read(4))[0]
        color = Color.from_stream(data)
        range = Vector2f.from_stream(data, property_size)
        color_delta = struct.unpack('>f', data.read(4))[0]
        range_delta = Vector2f.from_stream(data, property_size)
        explicit = struct.unpack('>?', data.read(1))[0]
        active = struct.unpack('>?', data.read(1))[0]
        return cls(name, mode, color, range, color_delta, range_delta, explicit, active)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x08')  # 8 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>l', self.mode))
        self.color.to_stream(data)
        self.range.to_stream(data)
        data.write(struct.pack('>f', self.color_delta))
        self.range_delta.to_stream(data)
        data.write(struct.pack('>?', self.explicit))
        data.write(struct.pack('>?', self.active))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DistanceFogJson", data)
        return cls(
            name=json_data['name'],
            mode=json_data['mode'],
            color=Color.from_json(json_data['color']),
            range=Vector2f.from_json(json_data['range']),
            color_delta=json_data['color_delta'],
            range_delta=Vector2f.from_json(json_data['range_delta']),
            explicit=json_data['explicit'],
            active=json_data['active'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'mode': self.mode,
            'color': self.color.to_json(),
            'range': self.range.to_json(),
            'color_delta': self.color_delta,
            'range_delta': self.range_delta.to_json(),
            'explicit': self.explicit,
            'active': self.active,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.range.dependencies_for, "range", "Vector2f"),
            (self.range_delta.dependencies_for, "range_delta", "Vector2f"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for DistanceFog.{field_name} ({field_type}): {e}"
                )
