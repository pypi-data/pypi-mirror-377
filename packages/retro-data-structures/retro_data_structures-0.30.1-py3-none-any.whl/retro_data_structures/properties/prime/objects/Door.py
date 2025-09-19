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
from retro_data_structures.properties.prime.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.prime.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DoorJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        animation_parameters: json_util.JsonObject
        unnamed: json_util.JsonObject
        scan_offset: json_util.JsonValue
        collision_size: json_util.JsonValue
        collision_offset: json_util.JsonValue
        active: bool
        open: bool
        unknown_6: bool
        open_close_animation_length: float
        unknown_8: bool
    

@dataclasses.dataclass()
class Door(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    position: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000001, original_name='Position', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    rotation: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000002, original_name='Rotation', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000003, original_name='Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    animation_parameters: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x00000004, original_name='AnimationParameters', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unnamed: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x00000005, original_name='5', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    scan_offset: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000006, original_name='Scan Offset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    collision_size: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000007, original_name='Collision Size', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    collision_offset: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000008, original_name='Collision Offset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000009, original_name='Active'
        ),
    })
    open: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000a, original_name='Open'
        ),
    })
    unknown_6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000b, original_name='Unknown 6'
        ),
    })
    open_close_animation_length: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000c, original_name='Open/Close Animation Length'
        ),
    })
    unknown_8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000d, original_name='Unknown 8'
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
        return 0x3

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        animation_parameters = AnimationParameters.from_stream(data, property_size)
        unnamed = ActorParameters.from_stream(data, property_size)
        scan_offset = Vector.from_stream(data)
        collision_size = Vector.from_stream(data)
        collision_offset = Vector.from_stream(data)
        active = struct.unpack('>?', data.read(1))[0]
        open = struct.unpack('>?', data.read(1))[0]
        unknown_6 = struct.unpack('>?', data.read(1))[0]
        open_close_animation_length = struct.unpack('>f', data.read(4))[0]
        unknown_8 = struct.unpack('>?', data.read(1))[0]
        return cls(name, position, rotation, scale, animation_parameters, unnamed, scan_offset, collision_size, collision_offset, active, open, unknown_6, open_close_animation_length, unknown_8)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x0e')  # 14 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.animation_parameters.to_stream(data)
        self.unnamed.to_stream(data)
        self.scan_offset.to_stream(data)
        self.collision_size.to_stream(data)
        self.collision_offset.to_stream(data)
        data.write(struct.pack('>?', self.active))
        data.write(struct.pack('>?', self.open))
        data.write(struct.pack('>?', self.unknown_6))
        data.write(struct.pack('>f', self.open_close_animation_length))
        data.write(struct.pack('>?', self.unknown_8))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DoorJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            animation_parameters=AnimationParameters.from_json(json_data['animation_parameters']),
            unnamed=ActorParameters.from_json(json_data['unnamed']),
            scan_offset=Vector.from_json(json_data['scan_offset']),
            collision_size=Vector.from_json(json_data['collision_size']),
            collision_offset=Vector.from_json(json_data['collision_offset']),
            active=json_data['active'],
            open=json_data['open'],
            unknown_6=json_data['unknown_6'],
            open_close_animation_length=json_data['open_close_animation_length'],
            unknown_8=json_data['unknown_8'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'animation_parameters': self.animation_parameters.to_json(),
            'unnamed': self.unnamed.to_json(),
            'scan_offset': self.scan_offset.to_json(),
            'collision_size': self.collision_size.to_json(),
            'collision_offset': self.collision_offset.to_json(),
            'active': self.active,
            'open': self.open,
            'unknown_6': self.unknown_6,
            'open_close_animation_length': self.open_close_animation_length,
            'unknown_8': self.unknown_8,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.animation_parameters.dependencies_for, "animation_parameters", "AnimationParameters"),
            (self.unnamed.dependencies_for, "unnamed", "ActorParameters"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Door.{field_name} ({field_type}): {e}"
                )
