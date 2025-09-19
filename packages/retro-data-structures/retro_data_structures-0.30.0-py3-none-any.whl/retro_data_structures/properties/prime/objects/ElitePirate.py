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
from retro_data_structures.properties.prime.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ElitePirateJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unnamed: json_util.JsonObject
        actor_parameters_1: json_util.JsonObject
        unknown_1: float
        unknown_2: float
        unknown_3: float
        unknown_4: float
        unknown_5: float
        unknown_6: float
        unknown_7: float
        unknown_8: float
        particle_1: int
        sound_id_1: int
        actor_parameters_2: json_util.JsonObject
        animation_parameters: json_util.JsonObject
        particle_2: int
        sound_id_2: int
        model: int
        damage_info_1: json_util.JsonObject
        unknown_9: float
        particle_3: int
        particle_4: int
        particle_5: int
        particle_6: int
        unknown_10: float
        unknown_11: float
        unknown_12: float
        unknown_13: float
        unknown_14: float
        unknown_15: float
        unknown_16: int
        sound_id_3: int
        sound_id_4: int
        particle_7: int
        damage_info_2: json_util.JsonObject
        elsc: int
        sound_id_5: int
        unknown_17: bool
        unknown_18: bool
    

@dataclasses.dataclass()
class ElitePirate(BaseObjectType):
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
    unnamed: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x00000004, original_name='4', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    actor_parameters_1: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x00000005, original_name='ActorParameters 1', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    unknown_1: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000006, original_name='Unknown 1'
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
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000009, original_name='Unknown 4'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000a, original_name='Unknown 5'
        ),
    })
    unknown_6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000b, original_name='Unknown 6'
        ),
    })
    unknown_7: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000c, original_name='Unknown 7'
        ),
    })
    unknown_8: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000d, original_name='Unknown 8'
        ),
    })
    particle_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000e, original_name='Particle 1'
        ),
    })
    sound_id_1: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x0000000f, original_name='Sound ID 1'
        ),
    })
    actor_parameters_2: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x00000010, original_name='ActorParameters 2', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    animation_parameters: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x00000011, original_name='AnimationParameters', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    particle_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000012, original_name='Particle 2'
        ),
    })
    sound_id_2: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000013, original_name='Sound ID 2'
        ),
    })
    model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000014, original_name='Model'
        ),
    })
    damage_info_1: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x00000015, original_name='DamageInfo 1', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_9: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000016, original_name='Unknown 9'
        ),
    })
    particle_3: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000017, original_name='Particle 3'
        ),
    })
    particle_4: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000018, original_name='Particle 4'
        ),
    })
    particle_5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000019, original_name='Particle 5'
        ),
    })
    particle_6: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000001a, original_name='Particle 6'
        ),
    })
    unknown_10: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000001b, original_name='Unknown 10'
        ),
    })
    unknown_11: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000001c, original_name='Unknown 11'
        ),
    })
    unknown_12: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000001d, original_name='Unknown 12'
        ),
    })
    unknown_13: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000001e, original_name='Unknown 13'
        ),
    })
    unknown_14: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000001f, original_name='Unknown 14'
        ),
    })
    unknown_15: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000020, original_name='Unknown 15'
        ),
    })
    unknown_16: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000021, original_name='Unknown 16'
        ),
    })
    sound_id_3: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000022, original_name='Sound ID 3'
        ),
    })
    sound_id_4: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000023, original_name='Sound ID 4'
        ),
    })
    particle_7: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000024, original_name='Particle 7'
        ),
    })
    damage_info_2: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x00000025, original_name='DamageInfo 2', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    elsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000026, original_name='ELSC'
        ),
    })
    sound_id_5: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000027, original_name='Sound ID 5'
        ),
    })
    unknown_17: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000028, original_name='Unknown 17'
        ),
    })
    unknown_18: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000029, original_name='Unknown 18'
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
        return 0x26

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unnamed = PatternedAITypedef.from_stream(data, property_size)
        actor_parameters_1 = ActorParameters.from_stream(data, property_size)
        unknown_1 = struct.unpack('>f', data.read(4))[0]
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        unknown_6 = struct.unpack('>f', data.read(4))[0]
        unknown_7 = struct.unpack('>f', data.read(4))[0]
        unknown_8 = struct.unpack('>f', data.read(4))[0]
        particle_1 = struct.unpack(">L", data.read(4))[0]
        sound_id_1 = struct.unpack('>l', data.read(4))[0]
        actor_parameters_2 = ActorParameters.from_stream(data, property_size)
        animation_parameters = AnimationParameters.from_stream(data, property_size)
        particle_2 = struct.unpack(">L", data.read(4))[0]
        sound_id_2 = struct.unpack('>l', data.read(4))[0]
        model = struct.unpack(">L", data.read(4))[0]
        damage_info_1 = DamageInfo.from_stream(data, property_size)
        unknown_9 = struct.unpack('>f', data.read(4))[0]
        particle_3 = struct.unpack(">L", data.read(4))[0]
        particle_4 = struct.unpack(">L", data.read(4))[0]
        particle_5 = struct.unpack(">L", data.read(4))[0]
        particle_6 = struct.unpack(">L", data.read(4))[0]
        unknown_10 = struct.unpack('>f', data.read(4))[0]
        unknown_11 = struct.unpack('>f', data.read(4))[0]
        unknown_12 = struct.unpack('>f', data.read(4))[0]
        unknown_13 = struct.unpack('>f', data.read(4))[0]
        unknown_14 = struct.unpack('>f', data.read(4))[0]
        unknown_15 = struct.unpack('>f', data.read(4))[0]
        unknown_16 = struct.unpack('>l', data.read(4))[0]
        sound_id_3 = struct.unpack('>l', data.read(4))[0]
        sound_id_4 = struct.unpack('>l', data.read(4))[0]
        particle_7 = struct.unpack(">L", data.read(4))[0]
        damage_info_2 = DamageInfo.from_stream(data, property_size)
        elsc = struct.unpack(">L", data.read(4))[0]
        sound_id_5 = struct.unpack('>l', data.read(4))[0]
        unknown_17 = struct.unpack('>?', data.read(1))[0]
        unknown_18 = struct.unpack('>?', data.read(1))[0]
        return cls(name, position, rotation, scale, unnamed, actor_parameters_1, unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8, particle_1, sound_id_1, actor_parameters_2, animation_parameters, particle_2, sound_id_2, model, damage_info_1, unknown_9, particle_3, particle_4, particle_5, particle_6, unknown_10, unknown_11, unknown_12, unknown_13, unknown_14, unknown_15, unknown_16, sound_id_3, sound_id_4, particle_7, damage_info_2, elsc, sound_id_5, unknown_17, unknown_18)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00*')  # 42 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.unnamed.to_stream(data)
        self.actor_parameters_1.to_stream(data)
        data.write(struct.pack('>f', self.unknown_1))
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack('>f', self.unknown_5))
        data.write(struct.pack('>f', self.unknown_6))
        data.write(struct.pack('>f', self.unknown_7))
        data.write(struct.pack('>f', self.unknown_8))
        data.write(struct.pack(">L", self.particle_1))
        data.write(struct.pack('>l', self.sound_id_1))
        self.actor_parameters_2.to_stream(data)
        self.animation_parameters.to_stream(data)
        data.write(struct.pack(">L", self.particle_2))
        data.write(struct.pack('>l', self.sound_id_2))
        data.write(struct.pack(">L", self.model))
        self.damage_info_1.to_stream(data)
        data.write(struct.pack('>f', self.unknown_9))
        data.write(struct.pack(">L", self.particle_3))
        data.write(struct.pack(">L", self.particle_4))
        data.write(struct.pack(">L", self.particle_5))
        data.write(struct.pack(">L", self.particle_6))
        data.write(struct.pack('>f', self.unknown_10))
        data.write(struct.pack('>f', self.unknown_11))
        data.write(struct.pack('>f', self.unknown_12))
        data.write(struct.pack('>f', self.unknown_13))
        data.write(struct.pack('>f', self.unknown_14))
        data.write(struct.pack('>f', self.unknown_15))
        data.write(struct.pack('>l', self.unknown_16))
        data.write(struct.pack('>l', self.sound_id_3))
        data.write(struct.pack('>l', self.sound_id_4))
        data.write(struct.pack(">L", self.particle_7))
        self.damage_info_2.to_stream(data)
        data.write(struct.pack(">L", self.elsc))
        data.write(struct.pack('>l', self.sound_id_5))
        data.write(struct.pack('>?', self.unknown_17))
        data.write(struct.pack('>?', self.unknown_18))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ElitePirateJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unnamed=PatternedAITypedef.from_json(json_data['unnamed']),
            actor_parameters_1=ActorParameters.from_json(json_data['actor_parameters_1']),
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            unknown_6=json_data['unknown_6'],
            unknown_7=json_data['unknown_7'],
            unknown_8=json_data['unknown_8'],
            particle_1=json_data['particle_1'],
            sound_id_1=json_data['sound_id_1'],
            actor_parameters_2=ActorParameters.from_json(json_data['actor_parameters_2']),
            animation_parameters=AnimationParameters.from_json(json_data['animation_parameters']),
            particle_2=json_data['particle_2'],
            sound_id_2=json_data['sound_id_2'],
            model=json_data['model'],
            damage_info_1=DamageInfo.from_json(json_data['damage_info_1']),
            unknown_9=json_data['unknown_9'],
            particle_3=json_data['particle_3'],
            particle_4=json_data['particle_4'],
            particle_5=json_data['particle_5'],
            particle_6=json_data['particle_6'],
            unknown_10=json_data['unknown_10'],
            unknown_11=json_data['unknown_11'],
            unknown_12=json_data['unknown_12'],
            unknown_13=json_data['unknown_13'],
            unknown_14=json_data['unknown_14'],
            unknown_15=json_data['unknown_15'],
            unknown_16=json_data['unknown_16'],
            sound_id_3=json_data['sound_id_3'],
            sound_id_4=json_data['sound_id_4'],
            particle_7=json_data['particle_7'],
            damage_info_2=DamageInfo.from_json(json_data['damage_info_2']),
            elsc=json_data['elsc'],
            sound_id_5=json_data['sound_id_5'],
            unknown_17=json_data['unknown_17'],
            unknown_18=json_data['unknown_18'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unnamed': self.unnamed.to_json(),
            'actor_parameters_1': self.actor_parameters_1.to_json(),
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'unknown_6': self.unknown_6,
            'unknown_7': self.unknown_7,
            'unknown_8': self.unknown_8,
            'particle_1': self.particle_1,
            'sound_id_1': self.sound_id_1,
            'actor_parameters_2': self.actor_parameters_2.to_json(),
            'animation_parameters': self.animation_parameters.to_json(),
            'particle_2': self.particle_2,
            'sound_id_2': self.sound_id_2,
            'model': self.model,
            'damage_info_1': self.damage_info_1.to_json(),
            'unknown_9': self.unknown_9,
            'particle_3': self.particle_3,
            'particle_4': self.particle_4,
            'particle_5': self.particle_5,
            'particle_6': self.particle_6,
            'unknown_10': self.unknown_10,
            'unknown_11': self.unknown_11,
            'unknown_12': self.unknown_12,
            'unknown_13': self.unknown_13,
            'unknown_14': self.unknown_14,
            'unknown_15': self.unknown_15,
            'unknown_16': self.unknown_16,
            'sound_id_3': self.sound_id_3,
            'sound_id_4': self.sound_id_4,
            'particle_7': self.particle_7,
            'damage_info_2': self.damage_info_2.to_json(),
            'elsc': self.elsc,
            'sound_id_5': self.sound_id_5,
            'unknown_17': self.unknown_17,
            'unknown_18': self.unknown_18,
        }

    def _dependencies_for_particle_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_1)

    def _dependencies_for_sound_id_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_1)

    def _dependencies_for_particle_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_2)

    def _dependencies_for_sound_id_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_2)

    def _dependencies_for_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model)

    def _dependencies_for_particle_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_3)

    def _dependencies_for_particle_4(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_4)

    def _dependencies_for_particle_5(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_5)

    def _dependencies_for_particle_6(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_6)

    def _dependencies_for_sound_id_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_3)

    def _dependencies_for_sound_id_4(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_4)

    def _dependencies_for_particle_7(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_7)

    def _dependencies_for_elsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.elsc)

    def _dependencies_for_sound_id_5(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_5)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed.dependencies_for, "unnamed", "PatternedAITypedef"),
            (self.actor_parameters_1.dependencies_for, "actor_parameters_1", "ActorParameters"),
            (self._dependencies_for_particle_1, "particle_1", "AssetId"),
            (self._dependencies_for_sound_id_1, "sound_id_1", "int"),
            (self.actor_parameters_2.dependencies_for, "actor_parameters_2", "ActorParameters"),
            (self.animation_parameters.dependencies_for, "animation_parameters", "AnimationParameters"),
            (self._dependencies_for_particle_2, "particle_2", "AssetId"),
            (self._dependencies_for_sound_id_2, "sound_id_2", "int"),
            (self._dependencies_for_model, "model", "AssetId"),
            (self.damage_info_1.dependencies_for, "damage_info_1", "DamageInfo"),
            (self._dependencies_for_particle_3, "particle_3", "AssetId"),
            (self._dependencies_for_particle_4, "particle_4", "AssetId"),
            (self._dependencies_for_particle_5, "particle_5", "AssetId"),
            (self._dependencies_for_particle_6, "particle_6", "AssetId"),
            (self._dependencies_for_sound_id_3, "sound_id_3", "int"),
            (self._dependencies_for_sound_id_4, "sound_id_4", "int"),
            (self._dependencies_for_particle_7, "particle_7", "AssetId"),
            (self.damage_info_2.dependencies_for, "damage_info_2", "DamageInfo"),
            (self._dependencies_for_elsc, "elsc", "AssetId"),
            (self._dependencies_for_sound_id_5, "sound_id_5", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ElitePirate.{field_name} ({field_type}): {e}"
                )
