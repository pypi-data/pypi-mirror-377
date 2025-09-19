# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.prime.core.Color import Color
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class LightParametersJson(typing_extensions.TypedDict):
        unknown_1: bool
        unknown_2: float
        shadow_tessellation: int
        unknown_3: float
        unknown_4: float
        unknown_5: json_util.JsonValue
        unknown_6: bool
        world_lighting_options: int
        light_recalculation_options: int
        unknown_7: json_util.JsonValue
        unknown_8: int
        unknown_9: int
        unknown_10: bool
        light_layer_index: int
    

class WorldLightingOptions(enum.IntEnum):
    Unknown1 = 0
    NormalWorldLighting = 1
    Unknown2 = 2
    DisableWorldLighting = 3
    Unknown3 = 4
    Unknown4 = 5

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


class LightRecalculationOptions(enum.IntEnum):
    Never = 0
    _8Frames = 1
    _4Frames = 2
    EveryFrame = 3

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


@dataclasses.dataclass()
class LightParameters(BaseProperty):
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000000, original_name='Unknown 1'
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000001, original_name='Unknown 2'
        ),
    })
    shadow_tessellation: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000002, original_name='Shadow Tessellation'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000003, original_name='Unknown 3'
        ),
    })
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000004, original_name='Unknown 4'
        ),
    })
    unknown_5: Color = dataclasses.field(default_factory=Color, metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x00000005, original_name='Unknown 5', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000006, original_name='Unknown 6'
        ),
    })
    world_lighting_options: WorldLightingOptions = dataclasses.field(default=WorldLightingOptions.Unknown1, metadata={
        'reflection': FieldReflection[WorldLightingOptions](
            WorldLightingOptions, id=0x00000007, original_name='World Lighting Options', from_json=WorldLightingOptions.from_json, to_json=WorldLightingOptions.to_json
        ),
    })
    light_recalculation_options: LightRecalculationOptions = dataclasses.field(default=LightRecalculationOptions.Never, metadata={
        'reflection': FieldReflection[LightRecalculationOptions](
            LightRecalculationOptions, id=0x00000008, original_name='Light Recalculation Options', from_json=LightRecalculationOptions.from_json, to_json=LightRecalculationOptions.to_json
        ),
    })
    unknown_7: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000009, original_name='Unknown 7', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_8: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000a, original_name='Unknown 8'
        ),
    })
    unknown_9: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000b, original_name='Unknown 9'
        ),
    })
    unknown_10: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000c, original_name='Unknown 10'
        ),
    })
    light_layer_index: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000d, original_name='Light Layer Index'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        shadow_tessellation = struct.unpack('>l', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        unknown_5 = Color.from_stream(data)
        unknown_6 = struct.unpack('>?', data.read(1))[0]
        world_lighting_options = WorldLightingOptions.from_stream(data)
        light_recalculation_options = LightRecalculationOptions.from_stream(data)
        unknown_7 = Vector.from_stream(data)
        unknown_8 = struct.unpack('>l', data.read(4))[0]
        unknown_9 = struct.unpack('>l', data.read(4))[0]
        unknown_10 = struct.unpack('>?', data.read(1))[0]
        light_layer_index = struct.unpack('>l', data.read(4))[0]
        return cls(unknown_1, unknown_2, shadow_tessellation, unknown_3, unknown_4, unknown_5, unknown_6, world_lighting_options, light_recalculation_options, unknown_7, unknown_8, unknown_9, unknown_10, light_layer_index)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>?', self.unknown_1))
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>l', self.shadow_tessellation))
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack('>f', self.unknown_4))
        self.unknown_5.to_stream(data)
        data.write(struct.pack('>?', self.unknown_6))
        self.world_lighting_options.to_stream(data)
        self.light_recalculation_options.to_stream(data)
        self.unknown_7.to_stream(data)
        data.write(struct.pack('>l', self.unknown_8))
        data.write(struct.pack('>l', self.unknown_9))
        data.write(struct.pack('>?', self.unknown_10))
        data.write(struct.pack('>l', self.light_layer_index))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("LightParametersJson", data)
        return cls(
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            shadow_tessellation=json_data['shadow_tessellation'],
            unknown_3=json_data['unknown_3'],
            unknown_4=json_data['unknown_4'],
            unknown_5=Color.from_json(json_data['unknown_5']),
            unknown_6=json_data['unknown_6'],
            world_lighting_options=WorldLightingOptions.from_json(json_data['world_lighting_options']),
            light_recalculation_options=LightRecalculationOptions.from_json(json_data['light_recalculation_options']),
            unknown_7=Vector.from_json(json_data['unknown_7']),
            unknown_8=json_data['unknown_8'],
            unknown_9=json_data['unknown_9'],
            unknown_10=json_data['unknown_10'],
            light_layer_index=json_data['light_layer_index'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'shadow_tessellation': self.shadow_tessellation,
            'unknown_3': self.unknown_3,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5.to_json(),
            'unknown_6': self.unknown_6,
            'world_lighting_options': self.world_lighting_options.to_json(),
            'light_recalculation_options': self.light_recalculation_options.to_json(),
            'unknown_7': self.unknown_7.to_json(),
            'unknown_8': self.unknown_8,
            'unknown_9': self.unknown_9,
            'unknown_10': self.unknown_10,
            'light_layer_index': self.light_layer_index,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
