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
from retro_data_structures.properties.prime.archetypes.BoolFloat import BoolFloat
from retro_data_structures.properties.prime.archetypes.BoolVec3f import BoolVec3f
from retro_data_structures.properties.prime.archetypes.CameraHintStruct import CameraHintStruct
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class CameraHintJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        unknown_1: bool
        unknown_2: int
        unknown_3: int
        unnamed_0x00000006: json_util.JsonObject
        unnamed_0x00000007: json_util.JsonObject
        unnamed_0x00000008: json_util.JsonObject
        unnamed_0x00000009: json_util.JsonObject
        unnamed_0x0000000a: json_util.JsonObject
        unnamed_0x0000000b: json_util.JsonObject
        unknown_36: json_util.JsonValue
        unnamed_0x0000000d: json_util.JsonObject
        unnamed_0x0000000e: json_util.JsonObject
        unnamed_0x0000000f: json_util.JsonObject
        unnamed_0x00000010: json_util.JsonObject
        unknown_45: float
        unknown_46: float
        unnamed_0x00000013: json_util.JsonObject
        unknown_49: float
        unknown_50: float
        unknown_51: float
    

@dataclasses.dataclass()
class CameraHint(BaseObjectType):
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
    unknown_2: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000004, original_name='Unknown 2'
        ),
    })
    unknown_3: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000005, original_name='Unknown 3'
        ),
    })
    unnamed_0x00000006: CameraHintStruct = dataclasses.field(default_factory=CameraHintStruct, metadata={
        'reflection': FieldReflection[CameraHintStruct](
            CameraHintStruct, id=0x00000006, original_name='6', from_json=CameraHintStruct.from_json, to_json=CameraHintStruct.to_json
        ),
    })
    unnamed_0x00000007: BoolFloat = dataclasses.field(default_factory=BoolFloat, metadata={
        'reflection': FieldReflection[BoolFloat](
            BoolFloat, id=0x00000007, original_name='7', from_json=BoolFloat.from_json, to_json=BoolFloat.to_json
        ),
    })
    unnamed_0x00000008: BoolFloat = dataclasses.field(default_factory=BoolFloat, metadata={
        'reflection': FieldReflection[BoolFloat](
            BoolFloat, id=0x00000008, original_name='8', from_json=BoolFloat.from_json, to_json=BoolFloat.to_json
        ),
    })
    unnamed_0x00000009: BoolFloat = dataclasses.field(default_factory=BoolFloat, metadata={
        'reflection': FieldReflection[BoolFloat](
            BoolFloat, id=0x00000009, original_name='9', from_json=BoolFloat.from_json, to_json=BoolFloat.to_json
        ),
    })
    unnamed_0x0000000a: BoolVec3f = dataclasses.field(default_factory=BoolVec3f, metadata={
        'reflection': FieldReflection[BoolVec3f](
            BoolVec3f, id=0x0000000a, original_name='10', from_json=BoolVec3f.from_json, to_json=BoolVec3f.to_json
        ),
    })
    unnamed_0x0000000b: BoolVec3f = dataclasses.field(default_factory=BoolVec3f, metadata={
        'reflection': FieldReflection[BoolVec3f](
            BoolVec3f, id=0x0000000b, original_name='11', from_json=BoolVec3f.from_json, to_json=BoolVec3f.to_json
        ),
    })
    unknown_36: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x0000000c, original_name='Unknown 36', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unnamed_0x0000000d: BoolFloat = dataclasses.field(default_factory=BoolFloat, metadata={
        'reflection': FieldReflection[BoolFloat](
            BoolFloat, id=0x0000000d, original_name='13', from_json=BoolFloat.from_json, to_json=BoolFloat.to_json
        ),
    })
    unnamed_0x0000000e: BoolFloat = dataclasses.field(default_factory=BoolFloat, metadata={
        'reflection': FieldReflection[BoolFloat](
            BoolFloat, id=0x0000000e, original_name='14', from_json=BoolFloat.from_json, to_json=BoolFloat.to_json
        ),
    })
    unnamed_0x0000000f: BoolFloat = dataclasses.field(default_factory=BoolFloat, metadata={
        'reflection': FieldReflection[BoolFloat](
            BoolFloat, id=0x0000000f, original_name='15', from_json=BoolFloat.from_json, to_json=BoolFloat.to_json
        ),
    })
    unnamed_0x00000010: BoolFloat = dataclasses.field(default_factory=BoolFloat, metadata={
        'reflection': FieldReflection[BoolFloat](
            BoolFloat, id=0x00000010, original_name='16', from_json=BoolFloat.from_json, to_json=BoolFloat.to_json
        ),
    })
    unknown_45: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000011, original_name='Unknown 45'
        ),
    })
    unknown_46: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000012, original_name='Unknown 46'
        ),
    })
    unnamed_0x00000013: BoolFloat = dataclasses.field(default_factory=BoolFloat, metadata={
        'reflection': FieldReflection[BoolFloat](
            BoolFloat, id=0x00000013, original_name='19', from_json=BoolFloat.from_json, to_json=BoolFloat.to_json
        ),
    })
    unknown_49: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000014, original_name='Unknown 49'
        ),
    })
    unknown_50: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000015, original_name='Unknown 50'
        ),
    })
    unknown_51: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000016, original_name='Unknown 51'
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
        return 0x10

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unknown_2 = struct.unpack('>l', data.read(4))[0]
        unknown_3 = struct.unpack('>l', data.read(4))[0]
        unnamed_0x00000006 = CameraHintStruct.from_stream(data, property_size)
        unnamed_0x00000007 = BoolFloat.from_stream(data, property_size)
        unnamed_0x00000008 = BoolFloat.from_stream(data, property_size)
        unnamed_0x00000009 = BoolFloat.from_stream(data, property_size)
        unnamed_0x0000000a = BoolVec3f.from_stream(data, property_size)
        unnamed_0x0000000b = BoolVec3f.from_stream(data, property_size)
        unknown_36 = Vector.from_stream(data)
        unnamed_0x0000000d = BoolFloat.from_stream(data, property_size)
        unnamed_0x0000000e = BoolFloat.from_stream(data, property_size)
        unnamed_0x0000000f = BoolFloat.from_stream(data, property_size)
        unnamed_0x00000010 = BoolFloat.from_stream(data, property_size)
        unknown_45 = struct.unpack('>f', data.read(4))[0]
        unknown_46 = struct.unpack('>f', data.read(4))[0]
        unnamed_0x00000013 = BoolFloat.from_stream(data, property_size)
        unknown_49 = struct.unpack('>f', data.read(4))[0]
        unknown_50 = struct.unpack('>f', data.read(4))[0]
        unknown_51 = struct.unpack('>f', data.read(4))[0]
        return cls(name, position, rotation, unknown_1, unknown_2, unknown_3, unnamed_0x00000006, unnamed_0x00000007, unnamed_0x00000008, unnamed_0x00000009, unnamed_0x0000000a, unnamed_0x0000000b, unknown_36, unnamed_0x0000000d, unnamed_0x0000000e, unnamed_0x0000000f, unnamed_0x00000010, unknown_45, unknown_46, unnamed_0x00000013, unknown_49, unknown_50, unknown_51)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x17')  # 23 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        data.write(struct.pack('>?', self.unknown_1))
        data.write(struct.pack('>l', self.unknown_2))
        data.write(struct.pack('>l', self.unknown_3))
        self.unnamed_0x00000006.to_stream(data)
        self.unnamed_0x00000007.to_stream(data)
        self.unnamed_0x00000008.to_stream(data)
        self.unnamed_0x00000009.to_stream(data)
        self.unnamed_0x0000000a.to_stream(data)
        self.unnamed_0x0000000b.to_stream(data)
        self.unknown_36.to_stream(data)
        self.unnamed_0x0000000d.to_stream(data)
        self.unnamed_0x0000000e.to_stream(data)
        self.unnamed_0x0000000f.to_stream(data)
        self.unnamed_0x00000010.to_stream(data)
        data.write(struct.pack('>f', self.unknown_45))
        data.write(struct.pack('>f', self.unknown_46))
        self.unnamed_0x00000013.to_stream(data)
        data.write(struct.pack('>f', self.unknown_49))
        data.write(struct.pack('>f', self.unknown_50))
        data.write(struct.pack('>f', self.unknown_51))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraHintJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            unnamed_0x00000006=CameraHintStruct.from_json(json_data['unnamed_0x00000006']),
            unnamed_0x00000007=BoolFloat.from_json(json_data['unnamed_0x00000007']),
            unnamed_0x00000008=BoolFloat.from_json(json_data['unnamed_0x00000008']),
            unnamed_0x00000009=BoolFloat.from_json(json_data['unnamed_0x00000009']),
            unnamed_0x0000000a=BoolVec3f.from_json(json_data['unnamed_0x0000000a']),
            unnamed_0x0000000b=BoolVec3f.from_json(json_data['unnamed_0x0000000b']),
            unknown_36=Vector.from_json(json_data['unknown_36']),
            unnamed_0x0000000d=BoolFloat.from_json(json_data['unnamed_0x0000000d']),
            unnamed_0x0000000e=BoolFloat.from_json(json_data['unnamed_0x0000000e']),
            unnamed_0x0000000f=BoolFloat.from_json(json_data['unnamed_0x0000000f']),
            unnamed_0x00000010=BoolFloat.from_json(json_data['unnamed_0x00000010']),
            unknown_45=json_data['unknown_45'],
            unknown_46=json_data['unknown_46'],
            unnamed_0x00000013=BoolFloat.from_json(json_data['unnamed_0x00000013']),
            unknown_49=json_data['unknown_49'],
            unknown_50=json_data['unknown_50'],
            unknown_51=json_data['unknown_51'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'unnamed_0x00000006': self.unnamed_0x00000006.to_json(),
            'unnamed_0x00000007': self.unnamed_0x00000007.to_json(),
            'unnamed_0x00000008': self.unnamed_0x00000008.to_json(),
            'unnamed_0x00000009': self.unnamed_0x00000009.to_json(),
            'unnamed_0x0000000a': self.unnamed_0x0000000a.to_json(),
            'unnamed_0x0000000b': self.unnamed_0x0000000b.to_json(),
            'unknown_36': self.unknown_36.to_json(),
            'unnamed_0x0000000d': self.unnamed_0x0000000d.to_json(),
            'unnamed_0x0000000e': self.unnamed_0x0000000e.to_json(),
            'unnamed_0x0000000f': self.unnamed_0x0000000f.to_json(),
            'unnamed_0x00000010': self.unnamed_0x00000010.to_json(),
            'unknown_45': self.unknown_45,
            'unknown_46': self.unknown_46,
            'unnamed_0x00000013': self.unnamed_0x00000013.to_json(),
            'unknown_49': self.unknown_49,
            'unknown_50': self.unknown_50,
            'unknown_51': self.unknown_51,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000006.dependencies_for, "unnamed_0x00000006", "CameraHintStruct"),
            (self.unnamed_0x00000007.dependencies_for, "unnamed_0x00000007", "BoolFloat"),
            (self.unnamed_0x00000008.dependencies_for, "unnamed_0x00000008", "BoolFloat"),
            (self.unnamed_0x00000009.dependencies_for, "unnamed_0x00000009", "BoolFloat"),
            (self.unnamed_0x0000000a.dependencies_for, "unnamed_0x0000000a", "BoolVec3f"),
            (self.unnamed_0x0000000b.dependencies_for, "unnamed_0x0000000b", "BoolVec3f"),
            (self.unnamed_0x0000000d.dependencies_for, "unnamed_0x0000000d", "BoolFloat"),
            (self.unnamed_0x0000000e.dependencies_for, "unnamed_0x0000000e", "BoolFloat"),
            (self.unnamed_0x0000000f.dependencies_for, "unnamed_0x0000000f", "BoolFloat"),
            (self.unnamed_0x00000010.dependencies_for, "unnamed_0x00000010", "BoolFloat"),
            (self.unnamed_0x00000013.dependencies_for, "unnamed_0x00000013", "BoolFloat"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for CameraHint.{field_name} ({field_type}): {e}"
                )
