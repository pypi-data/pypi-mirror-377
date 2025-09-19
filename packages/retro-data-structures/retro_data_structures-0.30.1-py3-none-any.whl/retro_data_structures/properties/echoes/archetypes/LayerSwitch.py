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

    class LayerSwitchJson(typing_extensions.TypedDict):
        area_id: int
        layer_number: int
    

@dataclasses.dataclass()
class LayerSwitch(BaseProperty):
    area_id: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000000, original_name='Area ID'
        ),
    })
    layer_number: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000001, original_name='Layer #'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        area_id = struct.unpack('>L', data.read(4))[0]
        layer_number = struct.unpack('>l', data.read(4))[0]
        return cls(area_id, layer_number)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>L', self.area_id))
        data.write(struct.pack('>l', self.layer_number))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("LayerSwitchJson", data)
        return cls(
            area_id=json_data['area_id'],
            layer_number=json_data['layer_number'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'area_id': self.area_id,
            'layer_number': self.layer_number,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
