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
from retro_data_structures.properties.prime.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.prime.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.prime.archetypes.VisorParameters import VisorParameters
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DamageableTriggerJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        scale: json_util.JsonValue
        unnamed_0x00000003: json_util.JsonObject
        unnamed_0x00000004: json_util.JsonObject
        render_side: int
        texture_1: int
        texture_2: int
        texture_3: int
        enable_lock_on: bool
        active: bool
        unnamed_0x0000000b: json_util.JsonObject
    

class RenderSide(enum.IntEnum):
    _None = 0
    North = 1
    South = 2
    West = 4
    East = 8
    Top = 16
    Bottom = 32

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
class DamageableTrigger(BaseObjectType):
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
    scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000002, original_name='Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unnamed_0x00000003: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0x00000003, original_name='3', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    unnamed_0x00000004: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x00000004, original_name='4', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    render_side: RenderSide = dataclasses.field(default=RenderSide._None, metadata={
        'reflection': FieldReflection[RenderSide](
            RenderSide, id=0x00000005, original_name='Render Side', from_json=RenderSide.from_json, to_json=RenderSide.to_json
        ),
    })
    texture_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000006, original_name='Texture 1'
        ),
    })
    texture_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000007, original_name='Texture 2'
        ),
    })
    texture_3: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000008, original_name='Texture 3'
        ),
    })
    enable_lock_on: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000009, original_name='Enable Lock-On'
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000a, original_name='Active'
        ),
    })
    unnamed_0x0000000b: VisorParameters = dataclasses.field(default_factory=VisorParameters, metadata={
        'reflection': FieldReflection[VisorParameters](
            VisorParameters, id=0x0000000b, original_name='11', from_json=VisorParameters.from_json, to_json=VisorParameters.to_json
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
        return 0x1A

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unnamed_0x00000003 = HealthInfo.from_stream(data, property_size)
        unnamed_0x00000004 = DamageVulnerability.from_stream(data, property_size)
        render_side = RenderSide.from_stream(data)
        texture_1 = struct.unpack(">L", data.read(4))[0]
        texture_2 = struct.unpack(">L", data.read(4))[0]
        texture_3 = struct.unpack(">L", data.read(4))[0]
        enable_lock_on = struct.unpack('>?', data.read(1))[0]
        active = struct.unpack('>?', data.read(1))[0]
        unnamed_0x0000000b = VisorParameters.from_stream(data, property_size)
        return cls(name, position, scale, unnamed_0x00000003, unnamed_0x00000004, render_side, texture_1, texture_2, texture_3, enable_lock_on, active, unnamed_0x0000000b)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x0c')  # 12 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.scale.to_stream(data)
        self.unnamed_0x00000003.to_stream(data)
        self.unnamed_0x00000004.to_stream(data)
        self.render_side.to_stream(data)
        data.write(struct.pack(">L", self.texture_1))
        data.write(struct.pack(">L", self.texture_2))
        data.write(struct.pack(">L", self.texture_3))
        data.write(struct.pack('>?', self.enable_lock_on))
        data.write(struct.pack('>?', self.active))
        self.unnamed_0x0000000b.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DamageableTriggerJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            scale=Vector.from_json(json_data['scale']),
            unnamed_0x00000003=HealthInfo.from_json(json_data['unnamed_0x00000003']),
            unnamed_0x00000004=DamageVulnerability.from_json(json_data['unnamed_0x00000004']),
            render_side=RenderSide.from_json(json_data['render_side']),
            texture_1=json_data['texture_1'],
            texture_2=json_data['texture_2'],
            texture_3=json_data['texture_3'],
            enable_lock_on=json_data['enable_lock_on'],
            active=json_data['active'],
            unnamed_0x0000000b=VisorParameters.from_json(json_data['unnamed_0x0000000b']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'scale': self.scale.to_json(),
            'unnamed_0x00000003': self.unnamed_0x00000003.to_json(),
            'unnamed_0x00000004': self.unnamed_0x00000004.to_json(),
            'render_side': self.render_side.to_json(),
            'texture_1': self.texture_1,
            'texture_2': self.texture_2,
            'texture_3': self.texture_3,
            'enable_lock_on': self.enable_lock_on,
            'active': self.active,
            'unnamed_0x0000000b': self.unnamed_0x0000000b.to_json(),
        }

    def _dependencies_for_texture_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.texture_1)

    def _dependencies_for_texture_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.texture_2)

    def _dependencies_for_texture_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.texture_3)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000003.dependencies_for, "unnamed_0x00000003", "HealthInfo"),
            (self.unnamed_0x00000004.dependencies_for, "unnamed_0x00000004", "DamageVulnerability"),
            (self._dependencies_for_texture_1, "texture_1", "AssetId"),
            (self._dependencies_for_texture_2, "texture_2", "AssetId"),
            (self._dependencies_for_texture_3, "texture_3", "AssetId"),
            (self.unnamed_0x0000000b.dependencies_for, "unnamed_0x0000000b", "VisorParameters"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for DamageableTrigger.{field_name} ({field_type}): {e}"
                )
