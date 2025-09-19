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
from retro_data_structures.properties.prime.archetypes.PlayerHintStruct import PlayerHintStruct
from retro_data_structures.properties.prime.archetypes.SpindleCameraStruct import SpindleCameraStruct
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SpindleCameraJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        unknown_1: bool
        unnamed: json_util.JsonObject
        unknown_2: float
        unknown_3: float
        unknown_4: float
        unknown_5: float
        spindle_camera_struct_1: json_util.JsonObject
        spindle_camera_struct_2: json_util.JsonObject
        spindle_camera_struct_3: json_util.JsonObject
        spindle_camera_struct_4: json_util.JsonObject
        spindle_camera_struct_5: json_util.JsonObject
        spindle_camera_struct_6: json_util.JsonObject
        spindle_camera_struct_7: json_util.JsonObject
        spindle_camera_struct_8: json_util.JsonObject
        spindle_camera_struct_9: json_util.JsonObject
        spindle_camera_struct_10: json_util.JsonObject
        spindle_camera_struct_11: json_util.JsonObject
        spindle_camera_struct_12: json_util.JsonObject
        spindle_camera_struct_13: json_util.JsonObject
        spindle_camera_struct_14: json_util.JsonObject
        spindle_camera_struct_15: json_util.JsonObject
    

@dataclasses.dataclass()
class SpindleCamera(BaseObjectType):
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
    unnamed: PlayerHintStruct = dataclasses.field(default_factory=PlayerHintStruct, metadata={
        'reflection': FieldReflection[PlayerHintStruct](
            PlayerHintStruct, id=0x00000004, original_name='4', from_json=PlayerHintStruct.from_json, to_json=PlayerHintStruct.to_json
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000005, original_name='Unknown 2'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000006, original_name='Unknown 3'
        ),
    })
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Unknown 4'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000008, original_name='Unknown 5'
        ),
    })
    spindle_camera_struct_1: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x00000009, original_name='SpindleCameraStruct 1', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_2: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x0000000a, original_name='SpindleCameraStruct 2', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_3: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x0000000b, original_name='SpindleCameraStruct 3', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_4: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x0000000c, original_name='SpindleCameraStruct 4', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_5: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x0000000d, original_name='SpindleCameraStruct 5', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_6: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x0000000e, original_name='SpindleCameraStruct 6', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_7: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x0000000f, original_name='SpindleCameraStruct 7', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_8: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x00000010, original_name='SpindleCameraStruct 8', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_9: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x00000011, original_name='SpindleCameraStruct 9', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_10: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x00000012, original_name='SpindleCameraStruct 10', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_11: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x00000013, original_name='SpindleCameraStruct 11', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_12: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x00000014, original_name='SpindleCameraStruct 12', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_13: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x00000015, original_name='SpindleCameraStruct 13', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_14: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x00000016, original_name='SpindleCameraStruct 14', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
        ),
    })
    spindle_camera_struct_15: SpindleCameraStruct = dataclasses.field(default_factory=SpindleCameraStruct, metadata={
        'reflection': FieldReflection[SpindleCameraStruct](
            SpindleCameraStruct, id=0x00000017, original_name='SpindleCameraStruct 15', from_json=SpindleCameraStruct.from_json, to_json=SpindleCameraStruct.to_json
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
        return 0x71

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unnamed = PlayerHintStruct.from_stream(data, property_size)
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        spindle_camera_struct_1 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_2 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_3 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_4 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_5 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_6 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_7 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_8 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_9 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_10 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_11 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_12 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_13 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_14 = SpindleCameraStruct.from_stream(data, property_size)
        spindle_camera_struct_15 = SpindleCameraStruct.from_stream(data, property_size)
        return cls(name, position, rotation, unknown_1, unnamed, unknown_2, unknown_3, unknown_4, unknown_5, spindle_camera_struct_1, spindle_camera_struct_2, spindle_camera_struct_3, spindle_camera_struct_4, spindle_camera_struct_5, spindle_camera_struct_6, spindle_camera_struct_7, spindle_camera_struct_8, spindle_camera_struct_9, spindle_camera_struct_10, spindle_camera_struct_11, spindle_camera_struct_12, spindle_camera_struct_13, spindle_camera_struct_14, spindle_camera_struct_15)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x18')  # 24 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        data.write(struct.pack('>?', self.unknown_1))
        self.unnamed.to_stream(data)
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack('>f', self.unknown_5))
        self.spindle_camera_struct_1.to_stream(data)
        self.spindle_camera_struct_2.to_stream(data)
        self.spindle_camera_struct_3.to_stream(data)
        self.spindle_camera_struct_4.to_stream(data)
        self.spindle_camera_struct_5.to_stream(data)
        self.spindle_camera_struct_6.to_stream(data)
        self.spindle_camera_struct_7.to_stream(data)
        self.spindle_camera_struct_8.to_stream(data)
        self.spindle_camera_struct_9.to_stream(data)
        self.spindle_camera_struct_10.to_stream(data)
        self.spindle_camera_struct_11.to_stream(data)
        self.spindle_camera_struct_12.to_stream(data)
        self.spindle_camera_struct_13.to_stream(data)
        self.spindle_camera_struct_14.to_stream(data)
        self.spindle_camera_struct_15.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpindleCameraJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            unknown_1=json_data['unknown_1'],
            unnamed=PlayerHintStruct.from_json(json_data['unnamed']),
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            spindle_camera_struct_1=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_1']),
            spindle_camera_struct_2=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_2']),
            spindle_camera_struct_3=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_3']),
            spindle_camera_struct_4=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_4']),
            spindle_camera_struct_5=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_5']),
            spindle_camera_struct_6=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_6']),
            spindle_camera_struct_7=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_7']),
            spindle_camera_struct_8=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_8']),
            spindle_camera_struct_9=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_9']),
            spindle_camera_struct_10=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_10']),
            spindle_camera_struct_11=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_11']),
            spindle_camera_struct_12=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_12']),
            spindle_camera_struct_13=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_13']),
            spindle_camera_struct_14=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_14']),
            spindle_camera_struct_15=SpindleCameraStruct.from_json(json_data['spindle_camera_struct_15']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'unknown_1': self.unknown_1,
            'unnamed': self.unnamed.to_json(),
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'spindle_camera_struct_1': self.spindle_camera_struct_1.to_json(),
            'spindle_camera_struct_2': self.spindle_camera_struct_2.to_json(),
            'spindle_camera_struct_3': self.spindle_camera_struct_3.to_json(),
            'spindle_camera_struct_4': self.spindle_camera_struct_4.to_json(),
            'spindle_camera_struct_5': self.spindle_camera_struct_5.to_json(),
            'spindle_camera_struct_6': self.spindle_camera_struct_6.to_json(),
            'spindle_camera_struct_7': self.spindle_camera_struct_7.to_json(),
            'spindle_camera_struct_8': self.spindle_camera_struct_8.to_json(),
            'spindle_camera_struct_9': self.spindle_camera_struct_9.to_json(),
            'spindle_camera_struct_10': self.spindle_camera_struct_10.to_json(),
            'spindle_camera_struct_11': self.spindle_camera_struct_11.to_json(),
            'spindle_camera_struct_12': self.spindle_camera_struct_12.to_json(),
            'spindle_camera_struct_13': self.spindle_camera_struct_13.to_json(),
            'spindle_camera_struct_14': self.spindle_camera_struct_14.to_json(),
            'spindle_camera_struct_15': self.spindle_camera_struct_15.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed.dependencies_for, "unnamed", "PlayerHintStruct"),
            (self.spindle_camera_struct_1.dependencies_for, "spindle_camera_struct_1", "SpindleCameraStruct"),
            (self.spindle_camera_struct_2.dependencies_for, "spindle_camera_struct_2", "SpindleCameraStruct"),
            (self.spindle_camera_struct_3.dependencies_for, "spindle_camera_struct_3", "SpindleCameraStruct"),
            (self.spindle_camera_struct_4.dependencies_for, "spindle_camera_struct_4", "SpindleCameraStruct"),
            (self.spindle_camera_struct_5.dependencies_for, "spindle_camera_struct_5", "SpindleCameraStruct"),
            (self.spindle_camera_struct_6.dependencies_for, "spindle_camera_struct_6", "SpindleCameraStruct"),
            (self.spindle_camera_struct_7.dependencies_for, "spindle_camera_struct_7", "SpindleCameraStruct"),
            (self.spindle_camera_struct_8.dependencies_for, "spindle_camera_struct_8", "SpindleCameraStruct"),
            (self.spindle_camera_struct_9.dependencies_for, "spindle_camera_struct_9", "SpindleCameraStruct"),
            (self.spindle_camera_struct_10.dependencies_for, "spindle_camera_struct_10", "SpindleCameraStruct"),
            (self.spindle_camera_struct_11.dependencies_for, "spindle_camera_struct_11", "SpindleCameraStruct"),
            (self.spindle_camera_struct_12.dependencies_for, "spindle_camera_struct_12", "SpindleCameraStruct"),
            (self.spindle_camera_struct_13.dependencies_for, "spindle_camera_struct_13", "SpindleCameraStruct"),
            (self.spindle_camera_struct_14.dependencies_for, "spindle_camera_struct_14", "SpindleCameraStruct"),
            (self.spindle_camera_struct_15.dependencies_for, "spindle_camera_struct_15", "SpindleCameraStruct"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for SpindleCamera.{field_name} ({field_type}): {e}"
                )
