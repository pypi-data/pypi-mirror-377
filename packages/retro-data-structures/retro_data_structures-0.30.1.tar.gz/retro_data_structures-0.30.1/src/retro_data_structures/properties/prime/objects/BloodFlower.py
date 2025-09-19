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

    class BloodFlowerJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unnamed_0x00000004: json_util.JsonObject
        unnamed_0x00000005: json_util.JsonObject
        particle_1: int
        wpsc_1: int
        wpsc_2: int
        damage_info_1: json_util.JsonObject
        damage_info_2: json_util.JsonObject
        damage_info_3: json_util.JsonObject
        particle_2: int
        particle_3: int
        particle_4: int
        unknown_1: float
        particle_5: int
        unknown_2: int
    

@dataclasses.dataclass()
class BloodFlower(BaseObjectType):
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
    unnamed_0x00000004: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x00000004, original_name='4', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    unnamed_0x00000005: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x00000005, original_name='5', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    particle_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000006, original_name='Particle 1'
        ),
    })
    wpsc_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000007, original_name='WPSC 1'
        ),
    })
    wpsc_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000008, original_name='WPSC 2'
        ),
    })
    damage_info_1: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x00000009, original_name='DamageInfo 1', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_2: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000000a, original_name='DamageInfo 2', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_3: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000000b, original_name='DamageInfo 3', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    particle_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000c, original_name='Particle 2'
        ),
    })
    particle_3: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000d, original_name='Particle 3'
        ),
    })
    particle_4: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000e, original_name='Particle 4'
        ),
    })
    unknown_1: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000f, original_name='Unknown 1'
        ),
    })
    particle_5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000010, original_name='Particle 5'
        ),
    })
    unknown_2: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000011, original_name='Unknown 2'
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
        return 0x2D

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unnamed_0x00000004 = PatternedAITypedef.from_stream(data, property_size)
        unnamed_0x00000005 = ActorParameters.from_stream(data, property_size)
        particle_1 = struct.unpack(">L", data.read(4))[0]
        wpsc_1 = struct.unpack(">L", data.read(4))[0]
        wpsc_2 = struct.unpack(">L", data.read(4))[0]
        damage_info_1 = DamageInfo.from_stream(data, property_size)
        damage_info_2 = DamageInfo.from_stream(data, property_size)
        damage_info_3 = DamageInfo.from_stream(data, property_size)
        particle_2 = struct.unpack(">L", data.read(4))[0]
        particle_3 = struct.unpack(">L", data.read(4))[0]
        particle_4 = struct.unpack(">L", data.read(4))[0]
        unknown_1 = struct.unpack('>f', data.read(4))[0]
        particle_5 = struct.unpack(">L", data.read(4))[0]
        unknown_2 = struct.unpack('>l', data.read(4))[0]
        return cls(name, position, rotation, scale, unnamed_0x00000004, unnamed_0x00000005, particle_1, wpsc_1, wpsc_2, damage_info_1, damage_info_2, damage_info_3, particle_2, particle_3, particle_4, unknown_1, particle_5, unknown_2)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x12')  # 18 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.unnamed_0x00000004.to_stream(data)
        self.unnamed_0x00000005.to_stream(data)
        data.write(struct.pack(">L", self.particle_1))
        data.write(struct.pack(">L", self.wpsc_1))
        data.write(struct.pack(">L", self.wpsc_2))
        self.damage_info_1.to_stream(data)
        self.damage_info_2.to_stream(data)
        self.damage_info_3.to_stream(data)
        data.write(struct.pack(">L", self.particle_2))
        data.write(struct.pack(">L", self.particle_3))
        data.write(struct.pack(">L", self.particle_4))
        data.write(struct.pack('>f', self.unknown_1))
        data.write(struct.pack(">L", self.particle_5))
        data.write(struct.pack('>l', self.unknown_2))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("BloodFlowerJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unnamed_0x00000004=PatternedAITypedef.from_json(json_data['unnamed_0x00000004']),
            unnamed_0x00000005=ActorParameters.from_json(json_data['unnamed_0x00000005']),
            particle_1=json_data['particle_1'],
            wpsc_1=json_data['wpsc_1'],
            wpsc_2=json_data['wpsc_2'],
            damage_info_1=DamageInfo.from_json(json_data['damage_info_1']),
            damage_info_2=DamageInfo.from_json(json_data['damage_info_2']),
            damage_info_3=DamageInfo.from_json(json_data['damage_info_3']),
            particle_2=json_data['particle_2'],
            particle_3=json_data['particle_3'],
            particle_4=json_data['particle_4'],
            unknown_1=json_data['unknown_1'],
            particle_5=json_data['particle_5'],
            unknown_2=json_data['unknown_2'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unnamed_0x00000004': self.unnamed_0x00000004.to_json(),
            'unnamed_0x00000005': self.unnamed_0x00000005.to_json(),
            'particle_1': self.particle_1,
            'wpsc_1': self.wpsc_1,
            'wpsc_2': self.wpsc_2,
            'damage_info_1': self.damage_info_1.to_json(),
            'damage_info_2': self.damage_info_2.to_json(),
            'damage_info_3': self.damage_info_3.to_json(),
            'particle_2': self.particle_2,
            'particle_3': self.particle_3,
            'particle_4': self.particle_4,
            'unknown_1': self.unknown_1,
            'particle_5': self.particle_5,
            'unknown_2': self.unknown_2,
        }

    def _dependencies_for_particle_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_1)

    def _dependencies_for_wpsc_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc_1)

    def _dependencies_for_wpsc_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc_2)

    def _dependencies_for_particle_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_2)

    def _dependencies_for_particle_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_3)

    def _dependencies_for_particle_4(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_4)

    def _dependencies_for_particle_5(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_5)

    def _dependencies_for_unknown_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_2)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000004.dependencies_for, "unnamed_0x00000004", "PatternedAITypedef"),
            (self.unnamed_0x00000005.dependencies_for, "unnamed_0x00000005", "ActorParameters"),
            (self._dependencies_for_particle_1, "particle_1", "AssetId"),
            (self._dependencies_for_wpsc_1, "wpsc_1", "AssetId"),
            (self._dependencies_for_wpsc_2, "wpsc_2", "AssetId"),
            (self.damage_info_1.dependencies_for, "damage_info_1", "DamageInfo"),
            (self.damage_info_2.dependencies_for, "damage_info_2", "DamageInfo"),
            (self.damage_info_3.dependencies_for, "damage_info_3", "DamageInfo"),
            (self._dependencies_for_particle_2, "particle_2", "AssetId"),
            (self._dependencies_for_particle_3, "particle_3", "AssetId"),
            (self._dependencies_for_particle_4, "particle_4", "AssetId"),
            (self._dependencies_for_particle_5, "particle_5", "AssetId"),
            (self._dependencies_for_unknown_2, "unknown_2", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for BloodFlower.{field_name} ({field_type}): {e}"
                )
