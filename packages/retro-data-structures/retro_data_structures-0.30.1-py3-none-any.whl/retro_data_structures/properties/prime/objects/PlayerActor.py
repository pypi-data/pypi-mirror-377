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
from retro_data_structures.properties.prime.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.prime.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.prime.archetypes.PlayerActorStruct import PlayerActorStruct
from retro_data_structures.properties.prime.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class PlayerActorJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unknown_1: json_util.JsonValue
        scan_offset: json_util.JsonValue
        unknown_2: float
        unknown_3: float
        unnamed_0x00000008: json_util.JsonObject
        unnamed_0x00000009: json_util.JsonObject
        model: int
        animation_parameters: json_util.JsonObject
        unnamed_0x0000000c: json_util.JsonObject
        loop_animation: bool
        unknown_5: bool
        disable_movement: bool
        active: bool
        unnamed_0x00000011: json_util.JsonObject
        unknown_13: int
    

@dataclasses.dataclass()
class PlayerActor(BaseObjectType):
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
    unknown_1: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000004, original_name='Unknown 1', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    scan_offset: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000005, original_name='Scan Offset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000006, original_name='Unknown 2'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Unknown 3'
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
    model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000a, original_name='Model'
        ),
    })
    animation_parameters: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x0000000b, original_name='AnimationParameters', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unnamed_0x0000000c: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x0000000c, original_name='12', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    loop_animation: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000d, original_name='Loop Animation'
        ),
    })
    unknown_5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000e, original_name='Unknown 5'
        ),
    })
    disable_movement: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000f, original_name='Disable Movement?'
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000010, original_name='Active'
        ),
    })
    unnamed_0x00000011: PlayerActorStruct = dataclasses.field(default_factory=PlayerActorStruct, metadata={
        'reflection': FieldReflection[PlayerActorStruct](
            PlayerActorStruct, id=0x00000011, original_name='17', from_json=PlayerActorStruct.from_json, to_json=PlayerActorStruct.to_json
        ),
    })
    unknown_13: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000012, original_name='Unknown 13'
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
        return 0x4C

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unknown_1 = Vector.from_stream(data)
        scan_offset = Vector.from_stream(data)
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unnamed_0x00000008 = HealthInfo.from_stream(data, property_size)
        unnamed_0x00000009 = DamageVulnerability.from_stream(data, property_size)
        model = struct.unpack(">L", data.read(4))[0]
        animation_parameters = AnimationParameters.from_stream(data, property_size)
        unnamed_0x0000000c = ActorParameters.from_stream(data, property_size)
        loop_animation = struct.unpack('>?', data.read(1))[0]
        unknown_5 = struct.unpack('>?', data.read(1))[0]
        disable_movement = struct.unpack('>?', data.read(1))[0]
        active = struct.unpack('>?', data.read(1))[0]
        unnamed_0x00000011 = PlayerActorStruct.from_stream(data, property_size)
        unknown_13 = struct.unpack('>l', data.read(4))[0]
        return cls(name, position, rotation, scale, unknown_1, scan_offset, unknown_2, unknown_3, unnamed_0x00000008, unnamed_0x00000009, model, animation_parameters, unnamed_0x0000000c, loop_animation, unknown_5, disable_movement, active, unnamed_0x00000011, unknown_13)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x13')  # 19 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.unknown_1.to_stream(data)
        self.scan_offset.to_stream(data)
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        self.unnamed_0x00000008.to_stream(data)
        self.unnamed_0x00000009.to_stream(data)
        data.write(struct.pack(">L", self.model))
        self.animation_parameters.to_stream(data)
        self.unnamed_0x0000000c.to_stream(data)
        data.write(struct.pack('>?', self.loop_animation))
        data.write(struct.pack('>?', self.unknown_5))
        data.write(struct.pack('>?', self.disable_movement))
        data.write(struct.pack('>?', self.active))
        self.unnamed_0x00000011.to_stream(data)
        data.write(struct.pack('>l', self.unknown_13))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PlayerActorJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unknown_1=Vector.from_json(json_data['unknown_1']),
            scan_offset=Vector.from_json(json_data['scan_offset']),
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            unnamed_0x00000008=HealthInfo.from_json(json_data['unnamed_0x00000008']),
            unnamed_0x00000009=DamageVulnerability.from_json(json_data['unnamed_0x00000009']),
            model=json_data['model'],
            animation_parameters=AnimationParameters.from_json(json_data['animation_parameters']),
            unnamed_0x0000000c=ActorParameters.from_json(json_data['unnamed_0x0000000c']),
            loop_animation=json_data['loop_animation'],
            unknown_5=json_data['unknown_5'],
            disable_movement=json_data['disable_movement'],
            active=json_data['active'],
            unnamed_0x00000011=PlayerActorStruct.from_json(json_data['unnamed_0x00000011']),
            unknown_13=json_data['unknown_13'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unknown_1': self.unknown_1.to_json(),
            'scan_offset': self.scan_offset.to_json(),
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'unnamed_0x00000008': self.unnamed_0x00000008.to_json(),
            'unnamed_0x00000009': self.unnamed_0x00000009.to_json(),
            'model': self.model,
            'animation_parameters': self.animation_parameters.to_json(),
            'unnamed_0x0000000c': self.unnamed_0x0000000c.to_json(),
            'loop_animation': self.loop_animation,
            'unknown_5': self.unknown_5,
            'disable_movement': self.disable_movement,
            'active': self.active,
            'unnamed_0x00000011': self.unnamed_0x00000011.to_json(),
            'unknown_13': self.unknown_13,
        }

    def _dependencies_for_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000008.dependencies_for, "unnamed_0x00000008", "HealthInfo"),
            (self.unnamed_0x00000009.dependencies_for, "unnamed_0x00000009", "DamageVulnerability"),
            (self._dependencies_for_model, "model", "AssetId"),
            (self.animation_parameters.dependencies_for, "animation_parameters", "AnimationParameters"),
            (self.unnamed_0x0000000c.dependencies_for, "unnamed_0x0000000c", "ActorParameters"),
            (self.unnamed_0x00000011.dependencies_for, "unnamed_0x00000011", "PlayerActorStruct"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for PlayerActor.{field_name} ({field_type}): {e}"
                )
