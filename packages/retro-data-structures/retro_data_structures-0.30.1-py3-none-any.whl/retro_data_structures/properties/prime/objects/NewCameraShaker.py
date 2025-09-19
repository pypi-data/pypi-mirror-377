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
from retro_data_structures.properties.prime.archetypes.GuessStruct import GuessStruct
from retro_data_structures.properties.prime.archetypes.IntBool import IntBool
from retro_data_structures.properties.prime.archetypes.NewCameraShakerStruct import NewCameraShakerStruct
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class NewCameraShakerJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        unknown_1: bool
        unnamed_0x00000003: json_util.JsonObject
        unnamed_0x00000004: json_util.JsonObject
        new_camera_shaker_struct_1: json_util.JsonObject
        new_camera_shaker_struct_2: json_util.JsonObject
        new_camera_shaker_struct_3: json_util.JsonObject
    

@dataclasses.dataclass()
class NewCameraShaker(BaseObjectType):
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
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000002, original_name='Unknown 1'
        ),
    })
    unnamed_0x00000003: IntBool = dataclasses.field(default_factory=IntBool, metadata={
        'reflection': FieldReflection[IntBool](
            IntBool, id=0x00000003, original_name='3', from_json=IntBool.from_json, to_json=IntBool.to_json
        ),
    })
    unnamed_0x00000004: GuessStruct = dataclasses.field(default_factory=GuessStruct, metadata={
        'reflection': FieldReflection[GuessStruct](
            GuessStruct, id=0x00000004, original_name='4', from_json=GuessStruct.from_json, to_json=GuessStruct.to_json
        ),
    })
    new_camera_shaker_struct_1: NewCameraShakerStruct = dataclasses.field(default_factory=NewCameraShakerStruct, metadata={
        'reflection': FieldReflection[NewCameraShakerStruct](
            NewCameraShakerStruct, id=0x00000005, original_name='NewCameraShakerStruct 1', from_json=NewCameraShakerStruct.from_json, to_json=NewCameraShakerStruct.to_json
        ),
    })
    new_camera_shaker_struct_2: NewCameraShakerStruct = dataclasses.field(default_factory=NewCameraShakerStruct, metadata={
        'reflection': FieldReflection[NewCameraShakerStruct](
            NewCameraShakerStruct, id=0x00000006, original_name='NewCameraShakerStruct 2', from_json=NewCameraShakerStruct.from_json, to_json=NewCameraShakerStruct.to_json
        ),
    })
    new_camera_shaker_struct_3: NewCameraShakerStruct = dataclasses.field(default_factory=NewCameraShakerStruct, metadata={
        'reflection': FieldReflection[NewCameraShakerStruct](
            NewCameraShakerStruct, id=0x00000007, original_name='NewCameraShakerStruct 3', from_json=NewCameraShakerStruct.from_json, to_json=NewCameraShakerStruct.to_json
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
        return 0x89

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unnamed_0x00000003 = IntBool.from_stream(data, property_size)
        unnamed_0x00000004 = GuessStruct.from_stream(data, property_size)
        new_camera_shaker_struct_1 = NewCameraShakerStruct.from_stream(data, property_size)
        new_camera_shaker_struct_2 = NewCameraShakerStruct.from_stream(data, property_size)
        new_camera_shaker_struct_3 = NewCameraShakerStruct.from_stream(data, property_size)
        return cls(name, position, unknown_1, unnamed_0x00000003, unnamed_0x00000004, new_camera_shaker_struct_1, new_camera_shaker_struct_2, new_camera_shaker_struct_3)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x08')  # 8 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        data.write(struct.pack('>?', self.unknown_1))
        self.unnamed_0x00000003.to_stream(data)
        self.unnamed_0x00000004.to_stream(data)
        self.new_camera_shaker_struct_1.to_stream(data)
        self.new_camera_shaker_struct_2.to_stream(data)
        self.new_camera_shaker_struct_3.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("NewCameraShakerJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            unknown_1=json_data['unknown_1'],
            unnamed_0x00000003=IntBool.from_json(json_data['unnamed_0x00000003']),
            unnamed_0x00000004=GuessStruct.from_json(json_data['unnamed_0x00000004']),
            new_camera_shaker_struct_1=NewCameraShakerStruct.from_json(json_data['new_camera_shaker_struct_1']),
            new_camera_shaker_struct_2=NewCameraShakerStruct.from_json(json_data['new_camera_shaker_struct_2']),
            new_camera_shaker_struct_3=NewCameraShakerStruct.from_json(json_data['new_camera_shaker_struct_3']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'unknown_1': self.unknown_1,
            'unnamed_0x00000003': self.unnamed_0x00000003.to_json(),
            'unnamed_0x00000004': self.unnamed_0x00000004.to_json(),
            'new_camera_shaker_struct_1': self.new_camera_shaker_struct_1.to_json(),
            'new_camera_shaker_struct_2': self.new_camera_shaker_struct_2.to_json(),
            'new_camera_shaker_struct_3': self.new_camera_shaker_struct_3.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000003.dependencies_for, "unnamed_0x00000003", "IntBool"),
            (self.unnamed_0x00000004.dependencies_for, "unnamed_0x00000004", "GuessStruct"),
            (self.new_camera_shaker_struct_1.dependencies_for, "new_camera_shaker_struct_1", "NewCameraShakerStruct"),
            (self.new_camera_shaker_struct_2.dependencies_for, "new_camera_shaker_struct_2", "NewCameraShakerStruct"),
            (self.new_camera_shaker_struct_3.dependencies_for, "new_camera_shaker_struct_3", "NewCameraShakerStruct"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for NewCameraShaker.{field_name} ({field_type}): {e}"
                )
