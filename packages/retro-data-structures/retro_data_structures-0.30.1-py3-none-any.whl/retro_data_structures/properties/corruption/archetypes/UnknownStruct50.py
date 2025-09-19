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
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct50Json(typing_extensions.TypedDict):
        electric_effect: int
        electric_damage_info: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct50(BaseProperty):
    electric_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x49fae143, original_name='ElectricEffect'
        ),
    })
    electric_damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xf808c9ee, original_name='ElectricDamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
        if (result := cls._fast_decode(data, property_count)) is not None:
            return result

        present_fields = default_override or {}
        for _ in range(property_count):
            property_id, property_size = struct.unpack(">LH", data.read(6))
            start = data.tell()
            try:
                property_name, decoder = _property_decoder[property_id]
                present_fields[property_name] = decoder(data, property_size)
            except KeyError:
                raise RuntimeError(f"Unknown property: 0x{property_id:08x}")
            assert data.tell() - start == property_size

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 2:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49fae143
        electric_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf808c9ee
        electric_damage_info = DamageInfo.from_stream(data, property_size)
    
        return cls(electric_effect, electric_damage_info)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'I\xfa\xe1C')  # 0x49fae143
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.electric_effect))

        data.write(b'\xf8\x08\xc9\xee')  # 0xf808c9ee
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.electric_damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct50Json", data)
        return cls(
            electric_effect=json_data['electric_effect'],
            electric_damage_info=DamageInfo.from_json(json_data['electric_damage_info']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'electric_effect': self.electric_effect,
            'electric_damage_info': self.electric_damage_info.to_json(),
        }


def _decode_electric_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x49fae143: ('electric_effect', _decode_electric_effect),
    0xf808c9ee: ('electric_damage_info', DamageInfo.from_stream),
}
