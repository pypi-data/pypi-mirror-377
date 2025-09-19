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
from retro_data_structures.properties.prime.archetypes.LightParameters import LightParameters
from retro_data_structures.properties.prime.archetypes.ScannableParameters import ScannableParameters
from retro_data_structures.properties.prime.archetypes.VisorParameters import VisorParameters
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ActorParametersJson(typing_extensions.TypedDict):
        unnamed_0x00000000: json_util.JsonObject
        unnamed_0x00000001: json_util.JsonObject
        x_ray_visor_model: int
        x_ray_visor_skin: int
        thermal_visor_model: int
        thermal_visor_skin: int
        unknown_1: bool
        unknown_2: float
        unknown_3: float
        unnamed_0x00000009: json_util.JsonObject
        enable_thermal_heat: bool
        unknown_4: bool
        unknown_5: bool
        unknown_6: float
    

@dataclasses.dataclass()
class ActorParameters(BaseProperty):
    unnamed_0x00000000: LightParameters = dataclasses.field(default_factory=LightParameters, metadata={
        'reflection': FieldReflection[LightParameters](
            LightParameters, id=0x00000000, original_name='0', from_json=LightParameters.from_json, to_json=LightParameters.to_json
        ),
    })
    unnamed_0x00000001: ScannableParameters = dataclasses.field(default_factory=ScannableParameters, metadata={
        'reflection': FieldReflection[ScannableParameters](
            ScannableParameters, id=0x00000001, original_name='1', from_json=ScannableParameters.from_json, to_json=ScannableParameters.to_json
        ),
    })
    x_ray_visor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000002, original_name='X-Ray Visor Model'
        ),
    })
    x_ray_visor_skin: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CSKR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000003, original_name='X-Ray Visor Skin'
        ),
    })
    thermal_visor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000004, original_name='Thermal Visor Model'
        ),
    })
    thermal_visor_skin: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CSKR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000005, original_name='Thermal Visor Skin'
        ),
    })
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000006, original_name='Unknown 1'
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Unknown 2'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000008, original_name='Unknown 3'
        ),
    })
    unnamed_0x00000009: VisorParameters = dataclasses.field(default_factory=VisorParameters, metadata={
        'reflection': FieldReflection[VisorParameters](
            VisorParameters, id=0x00000009, original_name='9', from_json=VisorParameters.from_json, to_json=VisorParameters.to_json
        ),
    })
    enable_thermal_heat: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000a, original_name='Enable Thermal Heat'
        ),
    })
    unknown_4: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000b, original_name='Unknown 4'
        ),
    })
    unknown_5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000c, original_name='Unknown 5'
        ),
    })
    unknown_6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000d, original_name='Unknown 6'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        unnamed_0x00000000 = LightParameters.from_stream(data, property_size)
        unnamed_0x00000001 = ScannableParameters.from_stream(data, property_size)
        x_ray_visor_model = struct.unpack(">L", data.read(4))[0]
        x_ray_visor_skin = struct.unpack(">L", data.read(4))[0]
        thermal_visor_model = struct.unpack(">L", data.read(4))[0]
        thermal_visor_skin = struct.unpack(">L", data.read(4))[0]
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unnamed_0x00000009 = VisorParameters.from_stream(data, property_size)
        enable_thermal_heat = struct.unpack('>?', data.read(1))[0]
        unknown_4 = struct.unpack('>?', data.read(1))[0]
        unknown_5 = struct.unpack('>?', data.read(1))[0]
        unknown_6 = struct.unpack('>f', data.read(4))[0]
        return cls(unnamed_0x00000000, unnamed_0x00000001, x_ray_visor_model, x_ray_visor_skin, thermal_visor_model, thermal_visor_skin, unknown_1, unknown_2, unknown_3, unnamed_0x00000009, enable_thermal_heat, unknown_4, unknown_5, unknown_6)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        self.unnamed_0x00000000.to_stream(data)
        self.unnamed_0x00000001.to_stream(data)
        data.write(struct.pack(">L", self.x_ray_visor_model))
        data.write(struct.pack(">L", self.x_ray_visor_skin))
        data.write(struct.pack(">L", self.thermal_visor_model))
        data.write(struct.pack(">L", self.thermal_visor_skin))
        data.write(struct.pack('>?', self.unknown_1))
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        self.unnamed_0x00000009.to_stream(data)
        data.write(struct.pack('>?', self.enable_thermal_heat))
        data.write(struct.pack('>?', self.unknown_4))
        data.write(struct.pack('>?', self.unknown_5))
        data.write(struct.pack('>f', self.unknown_6))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ActorParametersJson", data)
        return cls(
            unnamed_0x00000000=LightParameters.from_json(json_data['unnamed_0x00000000']),
            unnamed_0x00000001=ScannableParameters.from_json(json_data['unnamed_0x00000001']),
            x_ray_visor_model=json_data['x_ray_visor_model'],
            x_ray_visor_skin=json_data['x_ray_visor_skin'],
            thermal_visor_model=json_data['thermal_visor_model'],
            thermal_visor_skin=json_data['thermal_visor_skin'],
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            unnamed_0x00000009=VisorParameters.from_json(json_data['unnamed_0x00000009']),
            enable_thermal_heat=json_data['enable_thermal_heat'],
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            unknown_6=json_data['unknown_6'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unnamed_0x00000000': self.unnamed_0x00000000.to_json(),
            'unnamed_0x00000001': self.unnamed_0x00000001.to_json(),
            'x_ray_visor_model': self.x_ray_visor_model,
            'x_ray_visor_skin': self.x_ray_visor_skin,
            'thermal_visor_model': self.thermal_visor_model,
            'thermal_visor_skin': self.thermal_visor_skin,
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'unnamed_0x00000009': self.unnamed_0x00000009.to_json(),
            'enable_thermal_heat': self.enable_thermal_heat,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'unknown_6': self.unknown_6,
        }

    def _dependencies_for_x_ray_visor_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.x_ray_visor_model)

    def _dependencies_for_x_ray_visor_skin(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.x_ray_visor_skin)

    def _dependencies_for_thermal_visor_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.thermal_visor_model)

    def _dependencies_for_thermal_visor_skin(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.thermal_visor_skin)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000000.dependencies_for, "unnamed_0x00000000", "LightParameters"),
            (self.unnamed_0x00000001.dependencies_for, "unnamed_0x00000001", "ScannableParameters"),
            (self._dependencies_for_x_ray_visor_model, "x_ray_visor_model", "AssetId"),
            (self._dependencies_for_x_ray_visor_skin, "x_ray_visor_skin", "AssetId"),
            (self._dependencies_for_thermal_visor_model, "thermal_visor_model", "AssetId"),
            (self._dependencies_for_thermal_visor_skin, "thermal_visor_skin", "AssetId"),
            (self.unnamed_0x00000009.dependencies_for, "unnamed_0x00000009", "VisorParameters"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ActorParameters.{field_name} ({field_type}): {e}"
                )
