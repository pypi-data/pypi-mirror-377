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
from retro_data_structures.properties.prime.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.prime.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.prime.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ActorContraptionJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        collision_extent: json_util.JsonValue
        collision_scan_offset: json_util.JsonValue
        mass: float
        z_momentum: float
        unnamed_0x00000008: json_util.JsonObject
        unnamed_0x00000009: json_util.JsonObject
        animation_parameters: json_util.JsonObject
        unnamed_0x0000000b: json_util.JsonObject
        flame_particle: int
        unnamed_0x0000000d: json_util.JsonObject
        active: bool
    

@dataclasses.dataclass()
class ActorContraption(BaseObjectType):
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
    collision_extent: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000004, original_name='Collision Extent', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    collision_scan_offset: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000005, original_name='Collision/Scan Offset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    mass: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000006, original_name='Mass'
        ),
    })
    z_momentum: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Z Momentum'
        ),
    })
    unnamed_0x00000008: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0x00000008, original_name='8', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    unnamed_0x00000009: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x00000009, original_name='9', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    animation_parameters: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x0000000a, original_name='AnimationParameters', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unnamed_0x0000000b: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x0000000b, original_name='11', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    flame_particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000c, original_name='Flame Particle'
        ),
    })
    unnamed_0x0000000d: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000000d, original_name='13', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000e, original_name='Active'
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
        return 0x6E

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        collision_extent = Vector.from_stream(data)
        collision_scan_offset = Vector.from_stream(data)
        mass = struct.unpack('>f', data.read(4))[0]
        z_momentum = struct.unpack('>f', data.read(4))[0]
        unnamed_0x00000008 = HealthInfo.from_stream(data, property_size)
        unnamed_0x00000009 = DamageVulnerability.from_stream(data, property_size)
        animation_parameters = AnimationParameters.from_stream(data, property_size)
        unnamed_0x0000000b = ActorParameters.from_stream(data, property_size)
        flame_particle = struct.unpack(">L", data.read(4))[0]
        unnamed_0x0000000d = DamageInfo.from_stream(data, property_size)
        active = struct.unpack('>?', data.read(1))[0]
        return cls(name, position, rotation, scale, collision_extent, collision_scan_offset, mass, z_momentum, unnamed_0x00000008, unnamed_0x00000009, animation_parameters, unnamed_0x0000000b, flame_particle, unnamed_0x0000000d, active)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x0f')  # 15 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.collision_extent.to_stream(data)
        self.collision_scan_offset.to_stream(data)
        data.write(struct.pack('>f', self.mass))
        data.write(struct.pack('>f', self.z_momentum))
        self.unnamed_0x00000008.to_stream(data)
        self.unnamed_0x00000009.to_stream(data)
        self.animation_parameters.to_stream(data)
        self.unnamed_0x0000000b.to_stream(data)
        data.write(struct.pack(">L", self.flame_particle))
        self.unnamed_0x0000000d.to_stream(data)
        data.write(struct.pack('>?', self.active))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ActorContraptionJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            collision_extent=Vector.from_json(json_data['collision_extent']),
            collision_scan_offset=Vector.from_json(json_data['collision_scan_offset']),
            mass=json_data['mass'],
            z_momentum=json_data['z_momentum'],
            unnamed_0x00000008=HealthInfo.from_json(json_data['unnamed_0x00000008']),
            unnamed_0x00000009=DamageVulnerability.from_json(json_data['unnamed_0x00000009']),
            animation_parameters=AnimationParameters.from_json(json_data['animation_parameters']),
            unnamed_0x0000000b=ActorParameters.from_json(json_data['unnamed_0x0000000b']),
            flame_particle=json_data['flame_particle'],
            unnamed_0x0000000d=DamageInfo.from_json(json_data['unnamed_0x0000000d']),
            active=json_data['active'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'collision_extent': self.collision_extent.to_json(),
            'collision_scan_offset': self.collision_scan_offset.to_json(),
            'mass': self.mass,
            'z_momentum': self.z_momentum,
            'unnamed_0x00000008': self.unnamed_0x00000008.to_json(),
            'unnamed_0x00000009': self.unnamed_0x00000009.to_json(),
            'animation_parameters': self.animation_parameters.to_json(),
            'unnamed_0x0000000b': self.unnamed_0x0000000b.to_json(),
            'flame_particle': self.flame_particle,
            'unnamed_0x0000000d': self.unnamed_0x0000000d.to_json(),
            'active': self.active,
        }

    def _dependencies_for_flame_particle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.flame_particle)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000008.dependencies_for, "unnamed_0x00000008", "HealthInfo"),
            (self.unnamed_0x00000009.dependencies_for, "unnamed_0x00000009", "DamageVulnerability"),
            (self.animation_parameters.dependencies_for, "animation_parameters", "AnimationParameters"),
            (self.unnamed_0x0000000b.dependencies_for, "unnamed_0x0000000b", "ActorParameters"),
            (self._dependencies_for_flame_particle, "flame_particle", "AssetId"),
            (self.unnamed_0x0000000d.dependencies_for, "unnamed_0x0000000d", "DamageInfo"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ActorContraption.{field_name} ({field_type}): {e}"
                )
