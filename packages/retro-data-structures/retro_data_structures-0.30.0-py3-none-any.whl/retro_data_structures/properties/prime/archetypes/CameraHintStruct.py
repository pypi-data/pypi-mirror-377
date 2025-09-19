# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class CameraHintStructJson(typing_extensions.TypedDict):
        unknown_1: bool
        unknown_2: bool
        unknown_3: bool
        unknown_4: bool
        unknown_5: bool
        unknown_6: bool
        unknown_7: bool
        unknown_8: bool
        unknown_9: bool
        unknown_10: bool
        unknown_11: bool
        unknown_12: bool
        unknown_13: bool
        unknown_14: bool
        unknown_15: bool
        unknown_16: bool
        unknown_17: bool
        unknown_18: bool
        unknown_19: bool
        unknown_21: bool
        unknown_22: bool
        unknown_23: bool
    

@dataclasses.dataclass()
class CameraHintStruct(BaseProperty):
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000000, original_name='Unknown 1'
        ),
    })
    unknown_2: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000001, original_name='Unknown 2'
        ),
    })
    unknown_3: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000002, original_name='Unknown 3'
        ),
    })
    unknown_4: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000003, original_name='Unknown 4'
        ),
    })
    unknown_5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000004, original_name='Unknown 5'
        ),
    })
    unknown_6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000005, original_name='Unknown 6'
        ),
    })
    unknown_7: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000006, original_name='Unknown 7'
        ),
    })
    unknown_8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000007, original_name='Unknown 8'
        ),
    })
    unknown_9: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000008, original_name='Unknown 9'
        ),
    })
    unknown_10: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000009, original_name='Unknown 10'
        ),
    })
    unknown_11: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000a, original_name='Unknown 11'
        ),
    })
    unknown_12: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000b, original_name='Unknown 12'
        ),
    })
    unknown_13: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000c, original_name='Unknown 13'
        ),
    })
    unknown_14: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000d, original_name='Unknown 14'
        ),
    })
    unknown_15: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000e, original_name='Unknown 15'
        ),
    })
    unknown_16: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000f, original_name='Unknown 16'
        ),
    })
    unknown_17: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000010, original_name='Unknown 17'
        ),
    })
    unknown_18: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000011, original_name='Unknown 18'
        ),
    })
    unknown_19: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000012, original_name='Unknown 19'
        ),
    })
    unknown_21: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000013, original_name='Unknown 21'
        ),
    })
    unknown_22: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000014, original_name='Unknown 22'
        ),
    })
    unknown_23: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000015, original_name='Unknown 23'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unknown_2 = struct.unpack('>?', data.read(1))[0]
        unknown_3 = struct.unpack('>?', data.read(1))[0]
        unknown_4 = struct.unpack('>?', data.read(1))[0]
        unknown_5 = struct.unpack('>?', data.read(1))[0]
        unknown_6 = struct.unpack('>?', data.read(1))[0]
        unknown_7 = struct.unpack('>?', data.read(1))[0]
        unknown_8 = struct.unpack('>?', data.read(1))[0]
        unknown_9 = struct.unpack('>?', data.read(1))[0]
        unknown_10 = struct.unpack('>?', data.read(1))[0]
        unknown_11 = struct.unpack('>?', data.read(1))[0]
        unknown_12 = struct.unpack('>?', data.read(1))[0]
        unknown_13 = struct.unpack('>?', data.read(1))[0]
        unknown_14 = struct.unpack('>?', data.read(1))[0]
        unknown_15 = struct.unpack('>?', data.read(1))[0]
        unknown_16 = struct.unpack('>?', data.read(1))[0]
        unknown_17 = struct.unpack('>?', data.read(1))[0]
        unknown_18 = struct.unpack('>?', data.read(1))[0]
        unknown_19 = struct.unpack('>?', data.read(1))[0]
        unknown_21 = struct.unpack('>?', data.read(1))[0]
        unknown_22 = struct.unpack('>?', data.read(1))[0]
        unknown_23 = struct.unpack('>?', data.read(1))[0]
        return cls(unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8, unknown_9, unknown_10, unknown_11, unknown_12, unknown_13, unknown_14, unknown_15, unknown_16, unknown_17, unknown_18, unknown_19, unknown_21, unknown_22, unknown_23)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>?', self.unknown_1))
        data.write(struct.pack('>?', self.unknown_2))
        data.write(struct.pack('>?', self.unknown_3))
        data.write(struct.pack('>?', self.unknown_4))
        data.write(struct.pack('>?', self.unknown_5))
        data.write(struct.pack('>?', self.unknown_6))
        data.write(struct.pack('>?', self.unknown_7))
        data.write(struct.pack('>?', self.unknown_8))
        data.write(struct.pack('>?', self.unknown_9))
        data.write(struct.pack('>?', self.unknown_10))
        data.write(struct.pack('>?', self.unknown_11))
        data.write(struct.pack('>?', self.unknown_12))
        data.write(struct.pack('>?', self.unknown_13))
        data.write(struct.pack('>?', self.unknown_14))
        data.write(struct.pack('>?', self.unknown_15))
        data.write(struct.pack('>?', self.unknown_16))
        data.write(struct.pack('>?', self.unknown_17))
        data.write(struct.pack('>?', self.unknown_18))
        data.write(struct.pack('>?', self.unknown_19))
        data.write(struct.pack('>?', self.unknown_21))
        data.write(struct.pack('>?', self.unknown_22))
        data.write(struct.pack('>?', self.unknown_23))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraHintStructJson", data)
        return cls(
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
            unknown_18=json_data['unknown_18'],
            unknown_19=json_data['unknown_19'],
            unknown_21=json_data['unknown_21'],
            unknown_22=json_data['unknown_22'],
            unknown_23=json_data['unknown_23'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
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
            'unknown_18': self.unknown_18,
            'unknown_19': self.unknown_19,
            'unknown_21': self.unknown_21,
            'unknown_22': self.unknown_22,
            'unknown_23': self.unknown_23,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
