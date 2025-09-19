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
from retro_data_structures.properties.prime.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.prime.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class EyeballJson(typing_extensions.TypedDict):
        name: str
        unknown_1: int
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unnamed_0x00000005: json_util.JsonObject
        unnamed_0x00000006: json_util.JsonObject
        unknown_2: float
        unknown_3: float
        wpsc: int
        unnamed_0x0000000a: json_util.JsonObject
        particle_1: int
        particle_2: int
        texture_1: int
        texture_2: int
        unknown_4: int
        always_ffffffff_1: int
        always_ffffffff_2: int
        always_ffffffff_3: int
        laser_sound: int
        unknown_6: bool
    

@dataclasses.dataclass()
class Eyeball(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    unknown_1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000001, original_name='Unknown 1'
        ),
    })
    position: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000002, original_name='Position', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    rotation: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000003, original_name='Rotation', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000004, original_name='Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unnamed_0x00000005: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x00000005, original_name='5', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    unnamed_0x00000006: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x00000006, original_name='6', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Unknown 2'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000008, original_name='Unknown 3'
        ),
    })
    wpsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000009, original_name='WPSC'
        ),
    })
    unnamed_0x0000000a: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000000a, original_name='10', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    particle_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000b, original_name='Particle 1'
        ),
    })
    particle_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000c, original_name='Particle 2'
        ),
    })
    texture_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000d, original_name='Texture 1'
        ),
    })
    texture_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000e, original_name='Texture 2'
        ),
    })
    unknown_4: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000f, original_name='Unknown 4'
        ),
    })
    always_ffffffff_1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000010, original_name='Always FFFFFFFF 1'
        ),
    })
    always_ffffffff_2: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000011, original_name='Always FFFFFFFF 2'
        ),
    })
    always_ffffffff_3: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000012, original_name='Always FFFFFFFF 3'
        ),
    })
    laser_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000013, original_name='Laser Sound'
        ),
    })
    unknown_6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000014, original_name='Unknown 6'
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
        return 0x67

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        unknown_1 = struct.unpack('>l', data.read(4))[0]
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unnamed_0x00000005 = PatternedAITypedef.from_stream(data, property_size)
        unnamed_0x00000006 = ActorParameters.from_stream(data, property_size)
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        wpsc = struct.unpack(">L", data.read(4))[0]
        unnamed_0x0000000a = DamageInfo.from_stream(data, property_size)
        particle_1 = struct.unpack(">L", data.read(4))[0]
        particle_2 = struct.unpack(">L", data.read(4))[0]
        texture_1 = struct.unpack(">L", data.read(4))[0]
        texture_2 = struct.unpack(">L", data.read(4))[0]
        unknown_4 = struct.unpack('>l', data.read(4))[0]
        always_ffffffff_1 = struct.unpack('>l', data.read(4))[0]
        always_ffffffff_2 = struct.unpack('>l', data.read(4))[0]
        always_ffffffff_3 = struct.unpack('>l', data.read(4))[0]
        laser_sound = struct.unpack('>l', data.read(4))[0]
        unknown_6 = struct.unpack('>?', data.read(1))[0]
        return cls(name, unknown_1, position, rotation, scale, unnamed_0x00000005, unnamed_0x00000006, unknown_2, unknown_3, wpsc, unnamed_0x0000000a, particle_1, particle_2, texture_1, texture_2, unknown_4, always_ffffffff_1, always_ffffffff_2, always_ffffffff_3, laser_sound, unknown_6)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x15')  # 21 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>l', self.unknown_1))
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.unnamed_0x00000005.to_stream(data)
        self.unnamed_0x00000006.to_stream(data)
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack(">L", self.wpsc))
        self.unnamed_0x0000000a.to_stream(data)
        data.write(struct.pack(">L", self.particle_1))
        data.write(struct.pack(">L", self.particle_2))
        data.write(struct.pack(">L", self.texture_1))
        data.write(struct.pack(">L", self.texture_2))
        data.write(struct.pack('>l', self.unknown_4))
        data.write(struct.pack('>l', self.always_ffffffff_1))
        data.write(struct.pack('>l', self.always_ffffffff_2))
        data.write(struct.pack('>l', self.always_ffffffff_3))
        data.write(struct.pack('>l', self.laser_sound))
        data.write(struct.pack('>?', self.unknown_6))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EyeballJson", data)
        return cls(
            name=json_data['name'],
            unknown_1=json_data['unknown_1'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unnamed_0x00000005=PatternedAITypedef.from_json(json_data['unnamed_0x00000005']),
            unnamed_0x00000006=ActorParameters.from_json(json_data['unnamed_0x00000006']),
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            wpsc=json_data['wpsc'],
            unnamed_0x0000000a=DamageInfo.from_json(json_data['unnamed_0x0000000a']),
            particle_1=json_data['particle_1'],
            particle_2=json_data['particle_2'],
            texture_1=json_data['texture_1'],
            texture_2=json_data['texture_2'],
            unknown_4=json_data['unknown_4'],
            always_ffffffff_1=json_data['always_ffffffff_1'],
            always_ffffffff_2=json_data['always_ffffffff_2'],
            always_ffffffff_3=json_data['always_ffffffff_3'],
            laser_sound=json_data['laser_sound'],
            unknown_6=json_data['unknown_6'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'unknown_1': self.unknown_1,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unnamed_0x00000005': self.unnamed_0x00000005.to_json(),
            'unnamed_0x00000006': self.unnamed_0x00000006.to_json(),
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'wpsc': self.wpsc,
            'unnamed_0x0000000a': self.unnamed_0x0000000a.to_json(),
            'particle_1': self.particle_1,
            'particle_2': self.particle_2,
            'texture_1': self.texture_1,
            'texture_2': self.texture_2,
            'unknown_4': self.unknown_4,
            'always_ffffffff_1': self.always_ffffffff_1,
            'always_ffffffff_2': self.always_ffffffff_2,
            'always_ffffffff_3': self.always_ffffffff_3,
            'laser_sound': self.laser_sound,
            'unknown_6': self.unknown_6,
        }

    def _dependencies_for_wpsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc)

    def _dependencies_for_particle_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_1)

    def _dependencies_for_particle_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_2)

    def _dependencies_for_texture_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.texture_1)

    def _dependencies_for_texture_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.texture_2)

    def _dependencies_for_laser_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.laser_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000005.dependencies_for, "unnamed_0x00000005", "PatternedAITypedef"),
            (self.unnamed_0x00000006.dependencies_for, "unnamed_0x00000006", "ActorParameters"),
            (self._dependencies_for_wpsc, "wpsc", "AssetId"),
            (self.unnamed_0x0000000a.dependencies_for, "unnamed_0x0000000a", "DamageInfo"),
            (self._dependencies_for_particle_1, "particle_1", "AssetId"),
            (self._dependencies_for_particle_2, "particle_2", "AssetId"),
            (self._dependencies_for_texture_1, "texture_1", "AssetId"),
            (self._dependencies_for_texture_2, "texture_2", "AssetId"),
            (self._dependencies_for_laser_sound, "laser_sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Eyeball.{field_name} ({field_type}): {e}"
                )
