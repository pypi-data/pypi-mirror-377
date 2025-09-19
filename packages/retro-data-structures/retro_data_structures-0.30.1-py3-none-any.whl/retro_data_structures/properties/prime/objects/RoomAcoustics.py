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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class RoomAcousticsJson(typing_extensions.TypedDict):
        name: str
        unknown_1: bool
        unknown_2: int
        unknown_3: bool
        unknown_4: bool
        unknown_5: float
        unknown_6: float
        unknown_7: float
        unknown_8: float
        unknown_9: float
        unknown_10: float
        unknown_11: bool
        unknown_12: float
        unknown_13: float
        unknown_14: float
        unknown_15: bool
        unknown_16: bool
        unknown_17: float
        unknown_18: float
        unknown_19: float
        unknown_20: float
        unknown_21: float
        unknown_22: bool
        unknown_23: int
        unknown_24: int
        unknown_25: int
        unknown_26: int
        unknown_27: int
        unknown_28: int
        unknown_29: int
        unknown_30: int
        unknown_31: int
    

@dataclasses.dataclass()
class RoomAcoustics(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000001, original_name='Unknown 1'
        ),
    })
    unknown_2: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000002, original_name='Unknown 2'
        ),
    })
    unknown_3: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000003, original_name='Unknown 3'
        ),
    })
    unknown_4: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000004, original_name='Unknown 4'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000005, original_name='Unknown 5'
        ),
    })
    unknown_6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000006, original_name='Unknown 6'
        ),
    })
    unknown_7: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Unknown 7'
        ),
    })
    unknown_8: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000008, original_name='Unknown 8'
        ),
    })
    unknown_9: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000009, original_name='Unknown 9'
        ),
    })
    unknown_10: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000a, original_name='Unknown 10'
        ),
    })
    unknown_11: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000b, original_name='Unknown 11'
        ),
    })
    unknown_12: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000c, original_name='Unknown 12'
        ),
    })
    unknown_13: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000d, original_name='Unknown 13'
        ),
    })
    unknown_14: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000e, original_name='Unknown 14'
        ),
    })
    unknown_15: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000f, original_name='Unknown 15'
        ),
    })
    unknown_16: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000010, original_name='Unknown 16'
        ),
    })
    unknown_17: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000011, original_name='Unknown 17'
        ),
    })
    unknown_18: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000012, original_name='Unknown 18'
        ),
    })
    unknown_19: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000013, original_name='Unknown 19'
        ),
    })
    unknown_20: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000014, original_name='Unknown 20'
        ),
    })
    unknown_21: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000015, original_name='Unknown 21'
        ),
    })
    unknown_22: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000016, original_name='Unknown 22'
        ),
    })
    unknown_23: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000017, original_name='Unknown 23'
        ),
    })
    unknown_24: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000018, original_name='Unknown 24'
        ),
    })
    unknown_25: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000019, original_name='Unknown 25'
        ),
    })
    unknown_26: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001a, original_name='Unknown 26'
        ),
    })
    unknown_27: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001b, original_name='Unknown 27'
        ),
    })
    unknown_28: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001c, original_name='Unknown 28'
        ),
    })
    unknown_29: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001d, original_name='Unknown 29'
        ),
    })
    unknown_30: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001e, original_name='Unknown 30'
        ),
    })
    unknown_31: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000001f, original_name='Unknown 31'
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
        return 0x5D

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unknown_2 = struct.unpack('>l', data.read(4))[0]
        unknown_3 = struct.unpack('>?', data.read(1))[0]
        unknown_4 = struct.unpack('>?', data.read(1))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        unknown_6 = struct.unpack('>f', data.read(4))[0]
        unknown_7 = struct.unpack('>f', data.read(4))[0]
        unknown_8 = struct.unpack('>f', data.read(4))[0]
        unknown_9 = struct.unpack('>f', data.read(4))[0]
        unknown_10 = struct.unpack('>f', data.read(4))[0]
        unknown_11 = struct.unpack('>?', data.read(1))[0]
        unknown_12 = struct.unpack('>f', data.read(4))[0]
        unknown_13 = struct.unpack('>f', data.read(4))[0]
        unknown_14 = struct.unpack('>f', data.read(4))[0]
        unknown_15 = struct.unpack('>?', data.read(1))[0]
        unknown_16 = struct.unpack('>?', data.read(1))[0]
        unknown_17 = struct.unpack('>f', data.read(4))[0]
        unknown_18 = struct.unpack('>f', data.read(4))[0]
        unknown_19 = struct.unpack('>f', data.read(4))[0]
        unknown_20 = struct.unpack('>f', data.read(4))[0]
        unknown_21 = struct.unpack('>f', data.read(4))[0]
        unknown_22 = struct.unpack('>?', data.read(1))[0]
        unknown_23 = struct.unpack('>l', data.read(4))[0]
        unknown_24 = struct.unpack('>l', data.read(4))[0]
        unknown_25 = struct.unpack('>l', data.read(4))[0]
        unknown_26 = struct.unpack('>l', data.read(4))[0]
        unknown_27 = struct.unpack('>l', data.read(4))[0]
        unknown_28 = struct.unpack('>l', data.read(4))[0]
        unknown_29 = struct.unpack('>l', data.read(4))[0]
        unknown_30 = struct.unpack('>l', data.read(4))[0]
        unknown_31 = struct.unpack('>l', data.read(4))[0]
        return cls(name, unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8, unknown_9, unknown_10, unknown_11, unknown_12, unknown_13, unknown_14, unknown_15, unknown_16, unknown_17, unknown_18, unknown_19, unknown_20, unknown_21, unknown_22, unknown_23, unknown_24, unknown_25, unknown_26, unknown_27, unknown_28, unknown_29, unknown_30, unknown_31)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00 ')  # 32 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>?', self.unknown_1))
        data.write(struct.pack('>l', self.unknown_2))
        data.write(struct.pack('>?', self.unknown_3))
        data.write(struct.pack('>?', self.unknown_4))
        data.write(struct.pack('>f', self.unknown_5))
        data.write(struct.pack('>f', self.unknown_6))
        data.write(struct.pack('>f', self.unknown_7))
        data.write(struct.pack('>f', self.unknown_8))
        data.write(struct.pack('>f', self.unknown_9))
        data.write(struct.pack('>f', self.unknown_10))
        data.write(struct.pack('>?', self.unknown_11))
        data.write(struct.pack('>f', self.unknown_12))
        data.write(struct.pack('>f', self.unknown_13))
        data.write(struct.pack('>f', self.unknown_14))
        data.write(struct.pack('>?', self.unknown_15))
        data.write(struct.pack('>?', self.unknown_16))
        data.write(struct.pack('>f', self.unknown_17))
        data.write(struct.pack('>f', self.unknown_18))
        data.write(struct.pack('>f', self.unknown_19))
        data.write(struct.pack('>f', self.unknown_20))
        data.write(struct.pack('>f', self.unknown_21))
        data.write(struct.pack('>?', self.unknown_22))
        data.write(struct.pack('>l', self.unknown_23))
        data.write(struct.pack('>l', self.unknown_24))
        data.write(struct.pack('>l', self.unknown_25))
        data.write(struct.pack('>l', self.unknown_26))
        data.write(struct.pack('>l', self.unknown_27))
        data.write(struct.pack('>l', self.unknown_28))
        data.write(struct.pack('>l', self.unknown_29))
        data.write(struct.pack('>l', self.unknown_30))
        data.write(struct.pack('>l', self.unknown_31))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RoomAcousticsJson", data)
        return cls(
            name=json_data['name'],
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
            unknown_20=json_data['unknown_20'],
            unknown_21=json_data['unknown_21'],
            unknown_22=json_data['unknown_22'],
            unknown_23=json_data['unknown_23'],
            unknown_24=json_data['unknown_24'],
            unknown_25=json_data['unknown_25'],
            unknown_26=json_data['unknown_26'],
            unknown_27=json_data['unknown_27'],
            unknown_28=json_data['unknown_28'],
            unknown_29=json_data['unknown_29'],
            unknown_30=json_data['unknown_30'],
            unknown_31=json_data['unknown_31'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
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
            'unknown_20': self.unknown_20,
            'unknown_21': self.unknown_21,
            'unknown_22': self.unknown_22,
            'unknown_23': self.unknown_23,
            'unknown_24': self.unknown_24,
            'unknown_25': self.unknown_25,
            'unknown_26': self.unknown_26,
            'unknown_27': self.unknown_27,
            'unknown_28': self.unknown_28,
            'unknown_29': self.unknown_29,
            'unknown_30': self.unknown_30,
            'unknown_31': self.unknown_31,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
