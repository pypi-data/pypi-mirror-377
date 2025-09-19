# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.base_resource import Dependency
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class AreaAttributesJson(typing_extensions.TypedDict):
        unknown: int
        show_skybox: bool
        environmental_effect: int
        initial_environmental_effect_density: float
        initial_thermal_heat_level: float
        x_ray_fog_distance: float
        initial_world_lighting_level: float
        skybox_model: int
        phazon_type: int
    

class EnvironmentalEffect(enum.IntEnum):
    _None = 0
    Snow = 1
    Rain = 2
    Bubbles = 3

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


class PhazonType(enum.IntEnum):
    _None = 0
    Blue = 1
    Orange = 2

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
class AreaAttributes(BaseObjectType):
    unknown: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000000, original_name='Unknown'
        ),
    })
    show_skybox: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000001, original_name='Show Skybox'
        ),
    })
    environmental_effect: EnvironmentalEffect = dataclasses.field(default=EnvironmentalEffect._None, metadata={
        'reflection': FieldReflection[EnvironmentalEffect](
            EnvironmentalEffect, id=0x00000002, original_name='Environmental Effect', from_json=EnvironmentalEffect.from_json, to_json=EnvironmentalEffect.to_json
        ),
    })
    initial_environmental_effect_density: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000003, original_name='Initial Environmental Effect Density'
        ),
    })
    initial_thermal_heat_level: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000004, original_name='Initial Thermal Heat Level'
        ),
    })
    x_ray_fog_distance: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000005, original_name='X-Ray Fog Distance'
        ),
    })
    initial_world_lighting_level: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000006, original_name='Initial World Lighting Level'
        ),
    })
    skybox_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'ignore_dependencies_mlvl': True, 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000007, original_name='Skybox Model'
        ),
    })
    phazon_type: PhazonType = dataclasses.field(default=PhazonType._None, metadata={
        'reflection': FieldReflection[PhazonType](
            PhazonType, id=0x00000008, original_name='Phazon Type', from_json=PhazonType.from_json, to_json=PhazonType.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    def get_name(self) -> str | None:
        return None

    def set_name(self, name: str) -> None:
        raise RuntimeError(f"{self.__class__.__name__} does not have name")

    @classmethod
    def object_type(cls) -> int:
        return 0x4E

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        unknown = struct.unpack('>l', data.read(4))[0]
        show_skybox = struct.unpack('>?', data.read(1))[0]
        environmental_effect = EnvironmentalEffect.from_stream(data)
        initial_environmental_effect_density = struct.unpack('>f', data.read(4))[0]
        initial_thermal_heat_level = struct.unpack('>f', data.read(4))[0]
        x_ray_fog_distance = struct.unpack('>f', data.read(4))[0]
        initial_world_lighting_level = struct.unpack('>f', data.read(4))[0]
        skybox_model = struct.unpack(">L", data.read(4))[0]
        phazon_type = PhazonType.from_stream(data)
        return cls(unknown, show_skybox, environmental_effect, initial_environmental_effect_density, initial_thermal_heat_level, x_ray_fog_distance, initial_world_lighting_level, skybox_model, phazon_type)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\t')  # 9 properties
        data.write(struct.pack('>l', self.unknown))
        data.write(struct.pack('>?', self.show_skybox))
        self.environmental_effect.to_stream(data)
        data.write(struct.pack('>f', self.initial_environmental_effect_density))
        data.write(struct.pack('>f', self.initial_thermal_heat_level))
        data.write(struct.pack('>f', self.x_ray_fog_distance))
        data.write(struct.pack('>f', self.initial_world_lighting_level))
        data.write(struct.pack(">L", self.skybox_model))
        self.phazon_type.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AreaAttributesJson", data)
        return cls(
            unknown=json_data['unknown'],
            show_skybox=json_data['show_skybox'],
            environmental_effect=EnvironmentalEffect.from_json(json_data['environmental_effect']),
            initial_environmental_effect_density=json_data['initial_environmental_effect_density'],
            initial_thermal_heat_level=json_data['initial_thermal_heat_level'],
            x_ray_fog_distance=json_data['x_ray_fog_distance'],
            initial_world_lighting_level=json_data['initial_world_lighting_level'],
            skybox_model=json_data['skybox_model'],
            phazon_type=PhazonType.from_json(json_data['phazon_type']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown': self.unknown,
            'show_skybox': self.show_skybox,
            'environmental_effect': self.environmental_effect.to_json(),
            'initial_environmental_effect_density': self.initial_environmental_effect_density,
            'initial_thermal_heat_level': self.initial_thermal_heat_level,
            'x_ray_fog_distance': self.x_ray_fog_distance,
            'initial_world_lighting_level': self.initial_world_lighting_level,
            'skybox_model': self.skybox_model,
            'phazon_type': self.phazon_type.to_json(),
        }

    def _dependencies_for_skybox_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for it in asset_manager.get_dependencies_for_asset(self.skybox_model):
            yield Dependency(it.type, it.id, True)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_skybox_model, "skybox_model", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for AreaAttributes.{field_name} ({field_type}): {e}"
                )
