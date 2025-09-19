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
from retro_data_structures.properties.prime.archetypes.BehaveChance import BehaveChance
from retro_data_structures.properties.prime.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.prime.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ChozoGhostJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unnamed_0x00000004: json_util.JsonObject
        unnamed_0x00000005: json_util.JsonObject
        unknown_1: float
        unknown_2: float
        unknown_3: float
        unknown_4: float
        wpsc_1: int
        damage_info_1: json_util.JsonObject
        wpsc_2: int
        damage_info_2: json_util.JsonObject
        behave_chance_1: json_util.JsonObject
        behave_chance_2: json_util.JsonObject
        behave_chance_3: json_util.JsonObject
        sound_id_1: int
        unknown_5: float
        sound_id_2: int
        sound_id_3: int
        unknown_6: int
        unknown_7: float
        unknown_8: int
        unknown_9: float
        particle: int
        sound_id_4: int
        unknown_10: float
        unknown_11: float
        unknown_12: int
        unknown_13: int
    

@dataclasses.dataclass()
class ChozoGhost(BaseObjectType):
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
    wpsc_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000a, original_name='WPSC 1'
        ),
    })
    damage_info_1: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000000b, original_name='DamageInfo 1', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    wpsc_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000c, original_name='WPSC 2'
        ),
    })
    damage_info_2: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000000d, original_name='DamageInfo 2', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    behave_chance_1: BehaveChance = dataclasses.field(default_factory=BehaveChance, metadata={
        'reflection': FieldReflection[BehaveChance](
            BehaveChance, id=0x0000000e, original_name='BehaveChance 1', from_json=BehaveChance.from_json, to_json=BehaveChance.to_json
        ),
    })
    behave_chance_2: BehaveChance = dataclasses.field(default_factory=BehaveChance, metadata={
        'reflection': FieldReflection[BehaveChance](
            BehaveChance, id=0x0000000f, original_name='BehaveChance 2', from_json=BehaveChance.from_json, to_json=BehaveChance.to_json
        ),
    })
    behave_chance_3: BehaveChance = dataclasses.field(default_factory=BehaveChance, metadata={
        'reflection': FieldReflection[BehaveChance](
            BehaveChance, id=0x00000010, original_name='BehaveChance 3', from_json=BehaveChance.from_json, to_json=BehaveChance.to_json
        ),
    })
    sound_id_1: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000011, original_name='Sound ID 1'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000012, original_name='Unknown 5'
        ),
    })
    sound_id_2: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000013, original_name='Sound ID 2'
        ),
    })
    sound_id_3: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000014, original_name='Sound ID 3'
        ),
    })
    unknown_6: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000015, original_name='Unknown 6'
        ),
    })
    unknown_7: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000016, original_name='Unknown 7'
        ),
    })
    unknown_8: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000017, original_name='Unknown 8'
        ),
    })
    unknown_9: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000018, original_name='Unknown 9'
        ),
    })
    particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000019, original_name='Particle'
        ),
    })
    sound_id_4: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x0000001a, original_name='Sound ID 4'
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
    unknown_12: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001d, original_name='Unknown 12'
        ),
    })
    unknown_13: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001e, original_name='Unknown 13'
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
        return 0x28

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
        unknown_1 = struct.unpack('>f', data.read(4))[0]
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        wpsc_1 = struct.unpack(">L", data.read(4))[0]
        damage_info_1 = DamageInfo.from_stream(data, property_size)
        wpsc_2 = struct.unpack(">L", data.read(4))[0]
        damage_info_2 = DamageInfo.from_stream(data, property_size)
        behave_chance_1 = BehaveChance.from_stream(data, property_size)
        behave_chance_2 = BehaveChance.from_stream(data, property_size)
        behave_chance_3 = BehaveChance.from_stream(data, property_size)
        sound_id_1 = struct.unpack('>l', data.read(4))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        sound_id_2 = struct.unpack('>l', data.read(4))[0]
        sound_id_3 = struct.unpack('>l', data.read(4))[0]
        unknown_6 = struct.unpack('>l', data.read(4))[0]
        unknown_7 = struct.unpack('>f', data.read(4))[0]
        unknown_8 = struct.unpack('>l', data.read(4))[0]
        unknown_9 = struct.unpack('>f', data.read(4))[0]
        particle = struct.unpack(">L", data.read(4))[0]
        sound_id_4 = struct.unpack('>l', data.read(4))[0]
        unknown_10 = struct.unpack('>f', data.read(4))[0]
        unknown_11 = struct.unpack('>f', data.read(4))[0]
        unknown_12 = struct.unpack('>l', data.read(4))[0]
        unknown_13 = struct.unpack('>l', data.read(4))[0]
        return cls(name, position, rotation, scale, unnamed_0x00000004, unnamed_0x00000005, unknown_1, unknown_2, unknown_3, unknown_4, wpsc_1, damage_info_1, wpsc_2, damage_info_2, behave_chance_1, behave_chance_2, behave_chance_3, sound_id_1, unknown_5, sound_id_2, sound_id_3, unknown_6, unknown_7, unknown_8, unknown_9, particle, sound_id_4, unknown_10, unknown_11, unknown_12, unknown_13)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x1f')  # 31 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.unnamed_0x00000004.to_stream(data)
        self.unnamed_0x00000005.to_stream(data)
        data.write(struct.pack('>f', self.unknown_1))
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack(">L", self.wpsc_1))
        self.damage_info_1.to_stream(data)
        data.write(struct.pack(">L", self.wpsc_2))
        self.damage_info_2.to_stream(data)
        self.behave_chance_1.to_stream(data)
        self.behave_chance_2.to_stream(data)
        self.behave_chance_3.to_stream(data)
        data.write(struct.pack('>l', self.sound_id_1))
        data.write(struct.pack('>f', self.unknown_5))
        data.write(struct.pack('>l', self.sound_id_2))
        data.write(struct.pack('>l', self.sound_id_3))
        data.write(struct.pack('>l', self.unknown_6))
        data.write(struct.pack('>f', self.unknown_7))
        data.write(struct.pack('>l', self.unknown_8))
        data.write(struct.pack('>f', self.unknown_9))
        data.write(struct.pack(">L", self.particle))
        data.write(struct.pack('>l', self.sound_id_4))
        data.write(struct.pack('>f', self.unknown_10))
        data.write(struct.pack('>f', self.unknown_11))
        data.write(struct.pack('>l', self.unknown_12))
        data.write(struct.pack('>l', self.unknown_13))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ChozoGhostJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unnamed_0x00000004=PatternedAITypedef.from_json(json_data['unnamed_0x00000004']),
            unnamed_0x00000005=ActorParameters.from_json(json_data['unnamed_0x00000005']),
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            unknown_4=json_data['unknown_4'],
            wpsc_1=json_data['wpsc_1'],
            damage_info_1=DamageInfo.from_json(json_data['damage_info_1']),
            wpsc_2=json_data['wpsc_2'],
            damage_info_2=DamageInfo.from_json(json_data['damage_info_2']),
            behave_chance_1=BehaveChance.from_json(json_data['behave_chance_1']),
            behave_chance_2=BehaveChance.from_json(json_data['behave_chance_2']),
            behave_chance_3=BehaveChance.from_json(json_data['behave_chance_3']),
            sound_id_1=json_data['sound_id_1'],
            unknown_5=json_data['unknown_5'],
            sound_id_2=json_data['sound_id_2'],
            sound_id_3=json_data['sound_id_3'],
            unknown_6=json_data['unknown_6'],
            unknown_7=json_data['unknown_7'],
            unknown_8=json_data['unknown_8'],
            unknown_9=json_data['unknown_9'],
            particle=json_data['particle'],
            sound_id_4=json_data['sound_id_4'],
            unknown_10=json_data['unknown_10'],
            unknown_11=json_data['unknown_11'],
            unknown_12=json_data['unknown_12'],
            unknown_13=json_data['unknown_13'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unnamed_0x00000004': self.unnamed_0x00000004.to_json(),
            'unnamed_0x00000005': self.unnamed_0x00000005.to_json(),
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'unknown_4': self.unknown_4,
            'wpsc_1': self.wpsc_1,
            'damage_info_1': self.damage_info_1.to_json(),
            'wpsc_2': self.wpsc_2,
            'damage_info_2': self.damage_info_2.to_json(),
            'behave_chance_1': self.behave_chance_1.to_json(),
            'behave_chance_2': self.behave_chance_2.to_json(),
            'behave_chance_3': self.behave_chance_3.to_json(),
            'sound_id_1': self.sound_id_1,
            'unknown_5': self.unknown_5,
            'sound_id_2': self.sound_id_2,
            'sound_id_3': self.sound_id_3,
            'unknown_6': self.unknown_6,
            'unknown_7': self.unknown_7,
            'unknown_8': self.unknown_8,
            'unknown_9': self.unknown_9,
            'particle': self.particle,
            'sound_id_4': self.sound_id_4,
            'unknown_10': self.unknown_10,
            'unknown_11': self.unknown_11,
            'unknown_12': self.unknown_12,
            'unknown_13': self.unknown_13,
        }

    def _dependencies_for_wpsc_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc_1)

    def _dependencies_for_wpsc_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc_2)

    def _dependencies_for_sound_id_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_1)

    def _dependencies_for_sound_id_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_2)

    def _dependencies_for_sound_id_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_3)

    def _dependencies_for_particle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle)

    def _dependencies_for_sound_id_4(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_4)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000004.dependencies_for, "unnamed_0x00000004", "PatternedAITypedef"),
            (self.unnamed_0x00000005.dependencies_for, "unnamed_0x00000005", "ActorParameters"),
            (self._dependencies_for_wpsc_1, "wpsc_1", "AssetId"),
            (self.damage_info_1.dependencies_for, "damage_info_1", "DamageInfo"),
            (self._dependencies_for_wpsc_2, "wpsc_2", "AssetId"),
            (self.damage_info_2.dependencies_for, "damage_info_2", "DamageInfo"),
            (self.behave_chance_1.dependencies_for, "behave_chance_1", "BehaveChance"),
            (self.behave_chance_2.dependencies_for, "behave_chance_2", "BehaveChance"),
            (self.behave_chance_3.dependencies_for, "behave_chance_3", "BehaveChance"),
            (self._dependencies_for_sound_id_1, "sound_id_1", "int"),
            (self._dependencies_for_sound_id_2, "sound_id_2", "int"),
            (self._dependencies_for_sound_id_3, "sound_id_3", "int"),
            (self._dependencies_for_particle, "particle", "AssetId"),
            (self._dependencies_for_sound_id_4, "sound_id_4", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ChozoGhost.{field_name} ({field_type}): {e}"
                )
