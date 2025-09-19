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
from retro_data_structures.properties.prime.archetypes.LightParameters import LightParameters
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class EffectJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        particle: int
        elsc: int
        unknown_1: bool
        unknown_2: bool
        unknown_3: bool
        unknown_4: bool
        unknown_5: bool
        unknown_6: float
        unknown_7: float
        unknown_8: float
        unknown_9: float
        unknown_10: bool
        unknown_11: float
        unknown_12: float
        unknown_13: float
        unknown_14: bool
        unknown_15: bool
        unknown_16: bool
        unknown_17: bool
        unnamed: json_util.JsonObject
    

@dataclasses.dataclass()
class Effect(BaseObjectType):
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
    particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000004, original_name='Particle'
        ),
    })
    elsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000005, original_name='ELSC'
        ),
    })
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000006, original_name='Unknown 1'
        ),
    })
    unknown_2: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000007, original_name='Unknown 2'
        ),
    })
    unknown_3: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000008, original_name='Unknown 3'
        ),
    })
    unknown_4: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000009, original_name='Unknown 4'
        ),
    })
    unknown_5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000a, original_name='Unknown 5'
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
    unknown_9: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000e, original_name='Unknown 9'
        ),
    })
    unknown_10: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000f, original_name='Unknown 10'
        ),
    })
    unknown_11: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000010, original_name='Unknown 11'
        ),
    })
    unknown_12: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000011, original_name='Unknown 12'
        ),
    })
    unknown_13: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000012, original_name='Unknown 13'
        ),
    })
    unknown_14: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000013, original_name='Unknown 14'
        ),
    })
    unknown_15: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000014, original_name='Unknown 15'
        ),
    })
    unknown_16: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000015, original_name='Unknown 16'
        ),
    })
    unknown_17: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000016, original_name='Unknown 17'
        ),
    })
    unnamed: LightParameters = dataclasses.field(default_factory=LightParameters, metadata={
        'reflection': FieldReflection[LightParameters](
            LightParameters, id=0x00000017, original_name='23', from_json=LightParameters.from_json, to_json=LightParameters.to_json
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
        return 0x7

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        particle = struct.unpack(">L", data.read(4))[0]
        elsc = struct.unpack(">L", data.read(4))[0]
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unknown_2 = struct.unpack('>?', data.read(1))[0]
        unknown_3 = struct.unpack('>?', data.read(1))[0]
        unknown_4 = struct.unpack('>?', data.read(1))[0]
        unknown_5 = struct.unpack('>?', data.read(1))[0]
        unknown_6 = struct.unpack('>f', data.read(4))[0]
        unknown_7 = struct.unpack('>f', data.read(4))[0]
        unknown_8 = struct.unpack('>f', data.read(4))[0]
        unknown_9 = struct.unpack('>f', data.read(4))[0]
        unknown_10 = struct.unpack('>?', data.read(1))[0]
        unknown_11 = struct.unpack('>f', data.read(4))[0]
        unknown_12 = struct.unpack('>f', data.read(4))[0]
        unknown_13 = struct.unpack('>f', data.read(4))[0]
        unknown_14 = struct.unpack('>?', data.read(1))[0]
        unknown_15 = struct.unpack('>?', data.read(1))[0]
        unknown_16 = struct.unpack('>?', data.read(1))[0]
        unknown_17 = struct.unpack('>?', data.read(1))[0]
        unnamed = LightParameters.from_stream(data, property_size)
        return cls(name, position, rotation, scale, particle, elsc, unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8, unknown_9, unknown_10, unknown_11, unknown_12, unknown_13, unknown_14, unknown_15, unknown_16, unknown_17, unnamed)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x18')  # 24 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        data.write(struct.pack(">L", self.particle))
        data.write(struct.pack(">L", self.elsc))
        data.write(struct.pack('>?', self.unknown_1))
        data.write(struct.pack('>?', self.unknown_2))
        data.write(struct.pack('>?', self.unknown_3))
        data.write(struct.pack('>?', self.unknown_4))
        data.write(struct.pack('>?', self.unknown_5))
        data.write(struct.pack('>f', self.unknown_6))
        data.write(struct.pack('>f', self.unknown_7))
        data.write(struct.pack('>f', self.unknown_8))
        data.write(struct.pack('>f', self.unknown_9))
        data.write(struct.pack('>?', self.unknown_10))
        data.write(struct.pack('>f', self.unknown_11))
        data.write(struct.pack('>f', self.unknown_12))
        data.write(struct.pack('>f', self.unknown_13))
        data.write(struct.pack('>?', self.unknown_14))
        data.write(struct.pack('>?', self.unknown_15))
        data.write(struct.pack('>?', self.unknown_16))
        data.write(struct.pack('>?', self.unknown_17))
        self.unnamed.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EffectJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            particle=json_data['particle'],
            elsc=json_data['elsc'],
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
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
            unnamed=LightParameters.from_json(json_data['unnamed']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'particle': self.particle,
            'elsc': self.elsc,
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
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
            'unnamed': self.unnamed.to_json(),
        }

    def _dependencies_for_particle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle)

    def _dependencies_for_elsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.elsc)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_particle, "particle", "AssetId"),
            (self._dependencies_for_elsc, "elsc", "AssetId"),
            (self.unnamed.dependencies_for, "unnamed", "LightParameters"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Effect.{field_name} ({field_type}): {e}"
                )
