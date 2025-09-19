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
from retro_data_structures.properties.corruption.archetypes.PlayerInventoryItem import PlayerInventoryItem

if typing.TYPE_CHECKING:
    class ShipJson(typing_extensions.TypedDict):
        ship_missile: json_util.JsonObject
        ship_grapple: bool
    

@dataclasses.dataclass()
class Ship(BaseProperty):
    ship_missile: PlayerInventoryItem = dataclasses.field(default_factory=PlayerInventoryItem, metadata={
        'reflection': FieldReflection[PlayerInventoryItem](
            PlayerInventoryItem, id=0x398a3608, original_name='ShipMissile', from_json=PlayerInventoryItem.from_json, to_json=PlayerInventoryItem.to_json
        ),
    })
    ship_grapple: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf9aee109, original_name='ShipGrapple'
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
        assert property_id == 0x398a3608
        ship_missile = PlayerInventoryItem.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf9aee109
        ship_grapple = struct.unpack('>?', data.read(1))[0]
    
        return cls(ship_missile, ship_grapple)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'9\x8a6\x08')  # 0x398a3608
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ship_missile.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf9\xae\xe1\t')  # 0xf9aee109
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.ship_grapple))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ShipJson", data)
        return cls(
            ship_missile=PlayerInventoryItem.from_json(json_data['ship_missile']),
            ship_grapple=json_data['ship_grapple'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'ship_missile': self.ship_missile.to_json(),
            'ship_grapple': self.ship_grapple,
        }


def _decode_ship_grapple(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x398a3608: ('ship_missile', PlayerInventoryItem.from_stream),
    0xf9aee109: ('ship_grapple', _decode_ship_grapple),
}
