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
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Color import Color
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DebrisJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unknown_1: float
        unknown_2: json_util.JsonValue
        unknown_3: json_util.JsonValue
        unknown_4: float
        unknown_5: float
        unknown_6: float
        unknown_7: int
        unknown_8: bool
        model: int
        unnamed: json_util.JsonObject
        particle: int
        unknown_9: json_util.JsonValue
        unknown_10: bool
        unknown_11: bool
    

@dataclasses.dataclass()
class Debris(BaseObjectType):
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
    unknown_1: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000004, original_name='Unknown 1'
        ),
    })
    unknown_2: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000005, original_name='Unknown 2', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_3: Color = dataclasses.field(default_factory=Color, metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x00000006, original_name='Unknown 3', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Unknown 4'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000008, original_name='Unknown 5'
        ),
    })
    unknown_6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000009, original_name='Unknown 6'
        ),
    })
    unknown_7: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000a, original_name='Unknown 7'
        ),
    })
    unknown_8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000b, original_name='Unknown 8'
        ),
    })
    model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000c, original_name='Model'
        ),
    })
    unnamed: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x0000000d, original_name='13', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000e, original_name='Particle'
        ),
    })
    unknown_9: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x0000000f, original_name='Unknown 9', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_10: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000010, original_name='Unknown 10'
        ),
    })
    unknown_11: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000011, original_name='Unknown 11'
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
        return 0x1B

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unknown_1 = struct.unpack('>f', data.read(4))[0]
        unknown_2 = Vector.from_stream(data)
        unknown_3 = Color.from_stream(data)
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        unknown_6 = struct.unpack('>f', data.read(4))[0]
        unknown_7 = struct.unpack('>l', data.read(4))[0]
        unknown_8 = struct.unpack('>?', data.read(1))[0]
        model = struct.unpack(">L", data.read(4))[0]
        unnamed = ActorParameters.from_stream(data, property_size)
        particle = struct.unpack(">L", data.read(4))[0]
        unknown_9 = Vector.from_stream(data)
        unknown_10 = struct.unpack('>?', data.read(1))[0]
        unknown_11 = struct.unpack('>?', data.read(1))[0]
        return cls(name, position, rotation, scale, unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8, model, unnamed, particle, unknown_9, unknown_10, unknown_11)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x12')  # 18 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        data.write(struct.pack('>f', self.unknown_1))
        self.unknown_2.to_stream(data)
        self.unknown_3.to_stream(data)
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack('>f', self.unknown_5))
        data.write(struct.pack('>f', self.unknown_6))
        data.write(struct.pack('>l', self.unknown_7))
        data.write(struct.pack('>?', self.unknown_8))
        data.write(struct.pack(">L", self.model))
        self.unnamed.to_stream(data)
        data.write(struct.pack(">L", self.particle))
        self.unknown_9.to_stream(data)
        data.write(struct.pack('>?', self.unknown_10))
        data.write(struct.pack('>?', self.unknown_11))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DebrisJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unknown_1=json_data['unknown_1'],
            unknown_2=Vector.from_json(json_data['unknown_2']),
            unknown_3=Color.from_json(json_data['unknown_3']),
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            unknown_6=json_data['unknown_6'],
            unknown_7=json_data['unknown_7'],
            unknown_8=json_data['unknown_8'],
            model=json_data['model'],
            unnamed=ActorParameters.from_json(json_data['unnamed']),
            particle=json_data['particle'],
            unknown_9=Vector.from_json(json_data['unknown_9']),
            unknown_10=json_data['unknown_10'],
            unknown_11=json_data['unknown_11'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2.to_json(),
            'unknown_3': self.unknown_3.to_json(),
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'unknown_6': self.unknown_6,
            'unknown_7': self.unknown_7,
            'unknown_8': self.unknown_8,
            'model': self.model,
            'unnamed': self.unnamed.to_json(),
            'particle': self.particle,
            'unknown_9': self.unknown_9.to_json(),
            'unknown_10': self.unknown_10,
            'unknown_11': self.unknown_11,
        }

    def _dependencies_for_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model)

    def _dependencies_for_particle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_model, "model", "AssetId"),
            (self.unnamed.dependencies_for, "unnamed", "ActorParameters"),
            (self._dependencies_for_particle, "particle", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Debris.{field_name} ({field_type}): {e}"
                )
