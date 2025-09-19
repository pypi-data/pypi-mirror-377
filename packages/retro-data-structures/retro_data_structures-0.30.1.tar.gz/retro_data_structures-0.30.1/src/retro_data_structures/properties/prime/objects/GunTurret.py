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

    class GunTurretJson(typing_extensions.TypedDict):
        name: str
        unknown_1: int
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unknown_2: json_util.JsonValue
        scan_offset: json_util.JsonValue
        animation_parameters: json_util.JsonObject
        unnamed_0x00000008: json_util.JsonObject
        unnamed_0x00000009: json_util.JsonObject
        unnamed_0x0000000a: json_util.JsonObject
        unknown_3: float
        unknown_4: float
        unknown_5: float
        unknown_6: float
        unknown_7: float
        unknown_8: float
        unknown_9: float
        unknown_10: float
        unknown_11: float
        unknown_12: float
        unknown_13: float
        unknown_14: float
        unknown_15: float
        unknown_16: float
        unknown_17: bool
        unknown_18: int
        unnamed_0x0000001b: json_util.JsonObject
        particle_1: int
        particle_2: int
        particle_3: int
        particle_4: int
        particle_5: int
        particle_6: int
        particle_7: int
        unknown_19: int
        unknown_20: int
        unknown_21: int
        unknown_22: int
        unknown_23: int
        unknown_24: int
        model: int
        unknown_25: float
        unknown_26: int
        unknown_27: int
        unknown_28: int
        unknown_29: float
        unknown_30: bool
    

@dataclasses.dataclass()
class GunTurret(BaseObjectType):
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
    unknown_2: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000005, original_name='Unknown 2', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    scan_offset: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000006, original_name='Scan Offset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    animation_parameters: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x00000007, original_name='AnimationParameters', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unnamed_0x00000008: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x00000008, original_name='8', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    unnamed_0x00000009: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0x00000009, original_name='9', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    unnamed_0x0000000a: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x0000000a, original_name='10', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000b, original_name='Unknown 3'
        ),
    })
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000c, original_name='Unknown 4'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000d, original_name='Unknown 5'
        ),
    })
    unknown_6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000e, original_name='Unknown 6'
        ),
    })
    unknown_7: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000f, original_name='Unknown 7'
        ),
    })
    unknown_8: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000010, original_name='Unknown 8'
        ),
    })
    unknown_9: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000011, original_name='Unknown 9'
        ),
    })
    unknown_10: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000012, original_name='Unknown 10'
        ),
    })
    unknown_11: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000013, original_name='Unknown 11'
        ),
    })
    unknown_12: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000014, original_name='Unknown 12'
        ),
    })
    unknown_13: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000015, original_name='Unknown 13'
        ),
    })
    unknown_14: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000016, original_name='Unknown 14'
        ),
    })
    unknown_15: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000017, original_name='Unknown 15'
        ),
    })
    unknown_16: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000018, original_name='Unknown 16'
        ),
    })
    unknown_17: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000019, original_name='Unknown 17'
        ),
    })
    unknown_18: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000001a, original_name='Unknown 18'
        ),
    })
    unnamed_0x0000001b: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000001b, original_name='27', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    particle_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000001c, original_name='Particle 1'
        ),
    })
    particle_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000001d, original_name='Particle 2'
        ),
    })
    particle_3: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000001e, original_name='Particle 3'
        ),
    })
    particle_4: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000001f, original_name='Particle 4'
        ),
    })
    particle_5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000020, original_name='Particle 5'
        ),
    })
    particle_6: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000021, original_name='Particle 6'
        ),
    })
    particle_7: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000022, original_name='Particle 7'
        ),
    })
    unknown_19: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000023, original_name='Unknown 19'
        ),
    })
    unknown_20: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000024, original_name='Unknown 20'
        ),
    })
    unknown_21: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000025, original_name='Unknown 21'
        ),
    })
    unknown_22: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000026, original_name='Unknown 22'
        ),
    })
    unknown_23: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000027, original_name='Unknown 23'
        ),
    })
    unknown_24: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000028, original_name='Unknown 24'
        ),
    })
    model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000029, original_name='Model'
        ),
    })
    unknown_25: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000002a, original_name='Unknown 25'
        ),
    })
    unknown_26: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000002b, original_name='Unknown 26'
        ),
    })
    unknown_27: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000002c, original_name='Unknown 27'
        ),
    })
    unknown_28: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000002d, original_name='Unknown 28'
        ),
    })
    unknown_29: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000002e, original_name='Unknown 29'
        ),
    })
    unknown_30: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000002f, original_name='Unknown 30'
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
        return 0x64

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        unknown_1 = struct.unpack('>l', data.read(4))[0]
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unknown_2 = Vector.from_stream(data)
        scan_offset = Vector.from_stream(data)
        animation_parameters = AnimationParameters.from_stream(data, property_size)
        unnamed_0x00000008 = ActorParameters.from_stream(data, property_size)
        unnamed_0x00000009 = HealthInfo.from_stream(data, property_size)
        unnamed_0x0000000a = DamageVulnerability.from_stream(data, property_size)
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        unknown_6 = struct.unpack('>f', data.read(4))[0]
        unknown_7 = struct.unpack('>f', data.read(4))[0]
        unknown_8 = struct.unpack('>f', data.read(4))[0]
        unknown_9 = struct.unpack('>f', data.read(4))[0]
        unknown_10 = struct.unpack('>f', data.read(4))[0]
        unknown_11 = struct.unpack('>f', data.read(4))[0]
        unknown_12 = struct.unpack('>f', data.read(4))[0]
        unknown_13 = struct.unpack('>f', data.read(4))[0]
        unknown_14 = struct.unpack('>f', data.read(4))[0]
        unknown_15 = struct.unpack('>f', data.read(4))[0]
        unknown_16 = struct.unpack('>f', data.read(4))[0]
        unknown_17 = struct.unpack('>?', data.read(1))[0]
        unknown_18 = struct.unpack(">L", data.read(4))[0]
        unnamed_0x0000001b = DamageInfo.from_stream(data, property_size)
        particle_1 = struct.unpack(">L", data.read(4))[0]
        particle_2 = struct.unpack(">L", data.read(4))[0]
        particle_3 = struct.unpack(">L", data.read(4))[0]
        particle_4 = struct.unpack(">L", data.read(4))[0]
        particle_5 = struct.unpack(">L", data.read(4))[0]
        particle_6 = struct.unpack(">L", data.read(4))[0]
        particle_7 = struct.unpack(">L", data.read(4))[0]
        unknown_19 = struct.unpack('>l', data.read(4))[0]
        unknown_20 = struct.unpack('>l', data.read(4))[0]
        unknown_21 = struct.unpack('>l', data.read(4))[0]
        unknown_22 = struct.unpack('>l', data.read(4))[0]
        unknown_23 = struct.unpack('>l', data.read(4))[0]
        unknown_24 = struct.unpack('>l', data.read(4))[0]
        model = struct.unpack(">L", data.read(4))[0]
        unknown_25 = struct.unpack('>f', data.read(4))[0]
        unknown_26 = struct.unpack('>l', data.read(4))[0]
        unknown_27 = struct.unpack('>l', data.read(4))[0]
        unknown_28 = struct.unpack('>l', data.read(4))[0]
        unknown_29 = struct.unpack('>f', data.read(4))[0]
        unknown_30 = struct.unpack('>?', data.read(1))[0]
        return cls(name, unknown_1, position, rotation, scale, unknown_2, scan_offset, animation_parameters, unnamed_0x00000008, unnamed_0x00000009, unnamed_0x0000000a, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8, unknown_9, unknown_10, unknown_11, unknown_12, unknown_13, unknown_14, unknown_15, unknown_16, unknown_17, unknown_18, unnamed_0x0000001b, particle_1, particle_2, particle_3, particle_4, particle_5, particle_6, particle_7, unknown_19, unknown_20, unknown_21, unknown_22, unknown_23, unknown_24, model, unknown_25, unknown_26, unknown_27, unknown_28, unknown_29, unknown_30)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x000')  # 48 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>l', self.unknown_1))
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.unknown_2.to_stream(data)
        self.scan_offset.to_stream(data)
        self.animation_parameters.to_stream(data)
        self.unnamed_0x00000008.to_stream(data)
        self.unnamed_0x00000009.to_stream(data)
        self.unnamed_0x0000000a.to_stream(data)
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack('>f', self.unknown_5))
        data.write(struct.pack('>f', self.unknown_6))
        data.write(struct.pack('>f', self.unknown_7))
        data.write(struct.pack('>f', self.unknown_8))
        data.write(struct.pack('>f', self.unknown_9))
        data.write(struct.pack('>f', self.unknown_10))
        data.write(struct.pack('>f', self.unknown_11))
        data.write(struct.pack('>f', self.unknown_12))
        data.write(struct.pack('>f', self.unknown_13))
        data.write(struct.pack('>f', self.unknown_14))
        data.write(struct.pack('>f', self.unknown_15))
        data.write(struct.pack('>f', self.unknown_16))
        data.write(struct.pack('>?', self.unknown_17))
        data.write(struct.pack(">L", self.unknown_18))
        self.unnamed_0x0000001b.to_stream(data)
        data.write(struct.pack(">L", self.particle_1))
        data.write(struct.pack(">L", self.particle_2))
        data.write(struct.pack(">L", self.particle_3))
        data.write(struct.pack(">L", self.particle_4))
        data.write(struct.pack(">L", self.particle_5))
        data.write(struct.pack(">L", self.particle_6))
        data.write(struct.pack(">L", self.particle_7))
        data.write(struct.pack('>l', self.unknown_19))
        data.write(struct.pack('>l', self.unknown_20))
        data.write(struct.pack('>l', self.unknown_21))
        data.write(struct.pack('>l', self.unknown_22))
        data.write(struct.pack('>l', self.unknown_23))
        data.write(struct.pack('>l', self.unknown_24))
        data.write(struct.pack(">L", self.model))
        data.write(struct.pack('>f', self.unknown_25))
        data.write(struct.pack('>l', self.unknown_26))
        data.write(struct.pack('>l', self.unknown_27))
        data.write(struct.pack('>l', self.unknown_28))
        data.write(struct.pack('>f', self.unknown_29))
        data.write(struct.pack('>?', self.unknown_30))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("GunTurretJson", data)
        return cls(
            name=json_data['name'],
            unknown_1=json_data['unknown_1'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unknown_2=Vector.from_json(json_data['unknown_2']),
            scan_offset=Vector.from_json(json_data['scan_offset']),
            animation_parameters=AnimationParameters.from_json(json_data['animation_parameters']),
            unnamed_0x00000008=ActorParameters.from_json(json_data['unnamed_0x00000008']),
            unnamed_0x00000009=HealthInfo.from_json(json_data['unnamed_0x00000009']),
            unnamed_0x0000000a=DamageVulnerability.from_json(json_data['unnamed_0x0000000a']),
            unknown_3=json_data['unknown_3'],
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            unknown_6=json_data['unknown_6'],
            unknown_7=json_data['unknown_7'],
            unknown_8=json_data['unknown_8'],
            unknown_9=json_data['unknown_9'],
            unknown_10=json_data['unknown_10'],
            unknown_11=json_data['unknown_11'],
            unknown_12=json_data['unknown_12'],
            unknown_13=json_data['unknown_13'],
            unknown_14=json_data['unknown_14'],
            unknown_15=json_data['unknown_15'],
            unknown_16=json_data['unknown_16'],
            unknown_17=json_data['unknown_17'],
            unknown_18=json_data['unknown_18'],
            unnamed_0x0000001b=DamageInfo.from_json(json_data['unnamed_0x0000001b']),
            particle_1=json_data['particle_1'],
            particle_2=json_data['particle_2'],
            particle_3=json_data['particle_3'],
            particle_4=json_data['particle_4'],
            particle_5=json_data['particle_5'],
            particle_6=json_data['particle_6'],
            particle_7=json_data['particle_7'],
            unknown_19=json_data['unknown_19'],
            unknown_20=json_data['unknown_20'],
            unknown_21=json_data['unknown_21'],
            unknown_22=json_data['unknown_22'],
            unknown_23=json_data['unknown_23'],
            unknown_24=json_data['unknown_24'],
            model=json_data['model'],
            unknown_25=json_data['unknown_25'],
            unknown_26=json_data['unknown_26'],
            unknown_27=json_data['unknown_27'],
            unknown_28=json_data['unknown_28'],
            unknown_29=json_data['unknown_29'],
            unknown_30=json_data['unknown_30'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'unknown_1': self.unknown_1,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unknown_2': self.unknown_2.to_json(),
            'scan_offset': self.scan_offset.to_json(),
            'animation_parameters': self.animation_parameters.to_json(),
            'unnamed_0x00000008': self.unnamed_0x00000008.to_json(),
            'unnamed_0x00000009': self.unnamed_0x00000009.to_json(),
            'unnamed_0x0000000a': self.unnamed_0x0000000a.to_json(),
            'unknown_3': self.unknown_3,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'unknown_6': self.unknown_6,
            'unknown_7': self.unknown_7,
            'unknown_8': self.unknown_8,
            'unknown_9': self.unknown_9,
            'unknown_10': self.unknown_10,
            'unknown_11': self.unknown_11,
            'unknown_12': self.unknown_12,
            'unknown_13': self.unknown_13,
            'unknown_14': self.unknown_14,
            'unknown_15': self.unknown_15,
            'unknown_16': self.unknown_16,
            'unknown_17': self.unknown_17,
            'unknown_18': self.unknown_18,
            'unnamed_0x0000001b': self.unnamed_0x0000001b.to_json(),
            'particle_1': self.particle_1,
            'particle_2': self.particle_2,
            'particle_3': self.particle_3,
            'particle_4': self.particle_4,
            'particle_5': self.particle_5,
            'particle_6': self.particle_6,
            'particle_7': self.particle_7,
            'unknown_19': self.unknown_19,
            'unknown_20': self.unknown_20,
            'unknown_21': self.unknown_21,
            'unknown_22': self.unknown_22,
            'unknown_23': self.unknown_23,
            'unknown_24': self.unknown_24,
            'model': self.model,
            'unknown_25': self.unknown_25,
            'unknown_26': self.unknown_26,
            'unknown_27': self.unknown_27,
            'unknown_28': self.unknown_28,
            'unknown_29': self.unknown_29,
            'unknown_30': self.unknown_30,
        }

    def _dependencies_for_unknown_18(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.unknown_18)

    def _dependencies_for_particle_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_1)

    def _dependencies_for_particle_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_2)

    def _dependencies_for_particle_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_3)

    def _dependencies_for_particle_4(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_4)

    def _dependencies_for_particle_5(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_5)

    def _dependencies_for_particle_6(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_6)

    def _dependencies_for_particle_7(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_7)

    def _dependencies_for_unknown_19(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_19)

    def _dependencies_for_unknown_20(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_20)

    def _dependencies_for_unknown_21(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_21)

    def _dependencies_for_unknown_22(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_22)

    def _dependencies_for_unknown_23(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_23)

    def _dependencies_for_unknown_24(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_24)

    def _dependencies_for_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.animation_parameters.dependencies_for, "animation_parameters", "AnimationParameters"),
            (self.unnamed_0x00000008.dependencies_for, "unnamed_0x00000008", "ActorParameters"),
            (self.unnamed_0x00000009.dependencies_for, "unnamed_0x00000009", "HealthInfo"),
            (self.unnamed_0x0000000a.dependencies_for, "unnamed_0x0000000a", "DamageVulnerability"),
            (self._dependencies_for_unknown_18, "unknown_18", "AssetId"),
            (self.unnamed_0x0000001b.dependencies_for, "unnamed_0x0000001b", "DamageInfo"),
            (self._dependencies_for_particle_1, "particle_1", "AssetId"),
            (self._dependencies_for_particle_2, "particle_2", "AssetId"),
            (self._dependencies_for_particle_3, "particle_3", "AssetId"),
            (self._dependencies_for_particle_4, "particle_4", "AssetId"),
            (self._dependencies_for_particle_5, "particle_5", "AssetId"),
            (self._dependencies_for_particle_6, "particle_6", "AssetId"),
            (self._dependencies_for_particle_7, "particle_7", "AssetId"),
            (self._dependencies_for_unknown_19, "unknown_19", "int"),
            (self._dependencies_for_unknown_20, "unknown_20", "int"),
            (self._dependencies_for_unknown_21, "unknown_21", "int"),
            (self._dependencies_for_unknown_22, "unknown_22", "int"),
            (self._dependencies_for_unknown_23, "unknown_23", "int"),
            (self._dependencies_for_unknown_24, "unknown_24", "int"),
            (self._dependencies_for_model, "model", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for GunTurret.{field_name} ({field_type}): {e}"
                )
