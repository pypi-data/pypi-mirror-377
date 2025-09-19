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
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ElectroMagneticPulseJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        unknown_1: bool
        unknown_2: float
        unknown_3: float
        unknown_4: float
        unknown_5: float
        unknown_6: float
        unknown_7: float
        unknown_8: float
        particle: int
    

@dataclasses.dataclass()
class ElectroMagneticPulse(BaseObjectType):
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
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000003, original_name='Unknown 1'
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000004, original_name='Unknown 2'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000005, original_name='Unknown 3'
        ),
    })
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000006, original_name='Unknown 4'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Unknown 5'
        ),
    })
    unknown_6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000008, original_name='Unknown 6'
        ),
    })
    unknown_7: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000009, original_name='Unknown 7'
        ),
    })
    unknown_8: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000a, original_name='Unknown 8'
        ),
    })
    particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000b, original_name='Particle'
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
        return 0x4A

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        unknown_6 = struct.unpack('>f', data.read(4))[0]
        unknown_7 = struct.unpack('>f', data.read(4))[0]
        unknown_8 = struct.unpack('>f', data.read(4))[0]
        particle = struct.unpack(">L", data.read(4))[0]
        return cls(name, position, rotation, unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8, particle)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x0c')  # 12 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        data.write(struct.pack('>?', self.unknown_1))
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack('>f', self.unknown_5))
        data.write(struct.pack('>f', self.unknown_6))
        data.write(struct.pack('>f', self.unknown_7))
        data.write(struct.pack('>f', self.unknown_8))
        data.write(struct.pack(">L", self.particle))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ElectroMagneticPulseJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            unknown_6=json_data['unknown_6'],
            unknown_7=json_data['unknown_7'],
            unknown_8=json_data['unknown_8'],
            particle=json_data['particle'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'unknown_6': self.unknown_6,
            'unknown_7': self.unknown_7,
            'unknown_8': self.unknown_8,
            'particle': self.particle,
        }

    def _dependencies_for_particle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_particle, "particle", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ElectroMagneticPulse.{field_name} ({field_type}): {e}"
                )
