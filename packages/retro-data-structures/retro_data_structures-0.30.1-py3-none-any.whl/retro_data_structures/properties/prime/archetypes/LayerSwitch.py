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
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class LayerSwitchJson(typing_extensions.TypedDict):
        room_id: int
        layer_no: int
    

@dataclasses.dataclass()
class LayerSwitch(BaseProperty):
    room_id: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['MREA'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000000, original_name='Room ID'
        ),
    })
    layer_no: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000001, original_name='Layer no'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        room_id = struct.unpack(">L", data.read(4))[0]
        layer_no = struct.unpack('>l', data.read(4))[0]
        return cls(room_id, layer_no)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack(">L", self.room_id))
        data.write(struct.pack('>l', self.layer_no))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("LayerSwitchJson", data)
        return cls(
            room_id=json_data['room_id'],
            layer_no=json_data['layer_no'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'room_id': self.room_id,
            'layer_no': self.layer_no,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
