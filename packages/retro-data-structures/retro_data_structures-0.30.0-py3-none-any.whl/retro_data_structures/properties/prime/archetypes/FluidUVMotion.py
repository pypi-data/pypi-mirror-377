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
from retro_data_structures.properties.prime.archetypes.FluidLayerMotion import FluidLayerMotion

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class FluidUVMotionJson(typing_extensions.TypedDict):
        fluid_layer_motion_1: json_util.JsonObject
        fluid_layer_motion_2: json_util.JsonObject
        fluid_layer_motion_3: json_util.JsonObject
        unknown_1: float
        unknown_2: float
    

@dataclasses.dataclass()
class FluidUVMotion(BaseProperty):
    fluid_layer_motion_1: FluidLayerMotion = dataclasses.field(default_factory=FluidLayerMotion, metadata={
        'reflection': FieldReflection[FluidLayerMotion](
            FluidLayerMotion, id=0x00000000, original_name='Fluid Layer Motion 1', from_json=FluidLayerMotion.from_json, to_json=FluidLayerMotion.to_json
        ),
    })
    fluid_layer_motion_2: FluidLayerMotion = dataclasses.field(default_factory=FluidLayerMotion, metadata={
        'reflection': FieldReflection[FluidLayerMotion](
            FluidLayerMotion, id=0x00000001, original_name='Fluid Layer Motion 2', from_json=FluidLayerMotion.from_json, to_json=FluidLayerMotion.to_json
        ),
    })
    fluid_layer_motion_3: FluidLayerMotion = dataclasses.field(default_factory=FluidLayerMotion, metadata={
        'reflection': FieldReflection[FluidLayerMotion](
            FluidLayerMotion, id=0x00000002, original_name='Fluid Layer Motion 3', from_json=FluidLayerMotion.from_json, to_json=FluidLayerMotion.to_json
        ),
    })
    unknown_1: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000003, original_name='Unknown 1'
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000004, original_name='Unknown 2'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        fluid_layer_motion_1 = FluidLayerMotion.from_stream(data, property_size)
        fluid_layer_motion_2 = FluidLayerMotion.from_stream(data, property_size)
        fluid_layer_motion_3 = FluidLayerMotion.from_stream(data, property_size)
        unknown_1 = struct.unpack('>f', data.read(4))[0]
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        return cls(fluid_layer_motion_1, fluid_layer_motion_2, fluid_layer_motion_3, unknown_1, unknown_2)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        self.fluid_layer_motion_1.to_stream(data)
        self.fluid_layer_motion_2.to_stream(data)
        self.fluid_layer_motion_3.to_stream(data)
        data.write(struct.pack('>f', self.unknown_1))
        data.write(struct.pack('>f', self.unknown_2))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("FluidUVMotionJson", data)
        return cls(
            fluid_layer_motion_1=FluidLayerMotion.from_json(json_data['fluid_layer_motion_1']),
            fluid_layer_motion_2=FluidLayerMotion.from_json(json_data['fluid_layer_motion_2']),
            fluid_layer_motion_3=FluidLayerMotion.from_json(json_data['fluid_layer_motion_3']),
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'fluid_layer_motion_1': self.fluid_layer_motion_1.to_json(),
            'fluid_layer_motion_2': self.fluid_layer_motion_2.to_json(),
            'fluid_layer_motion_3': self.fluid_layer_motion_3.to_json(),
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.fluid_layer_motion_1.dependencies_for, "fluid_layer_motion_1", "FluidLayerMotion"),
            (self.fluid_layer_motion_2.dependencies_for, "fluid_layer_motion_2", "FluidLayerMotion"),
            (self.fluid_layer_motion_3.dependencies_for, "fluid_layer_motion_3", "FluidLayerMotion"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for FluidUVMotion.{field_name} ({field_type}): {e}"
                )
