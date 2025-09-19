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
    class MiscJson(typing_extensions.TypedDict):
        energy: json_util.JsonObject
        energy_tank: json_util.JsonObject
        fuses: json_util.JsonObject
        player_inventory_item: json_util.JsonObject
    

@dataclasses.dataclass()
class Misc(BaseProperty):
    energy: PlayerInventoryItem = dataclasses.field(default_factory=PlayerInventoryItem, metadata={
        'reflection': FieldReflection[PlayerInventoryItem](
            PlayerInventoryItem, id=0x336bd471, original_name='Energy', from_json=PlayerInventoryItem.from_json, to_json=PlayerInventoryItem.to_json
        ),
    })
    energy_tank: PlayerInventoryItem = dataclasses.field(default_factory=PlayerInventoryItem, metadata={
        'reflection': FieldReflection[PlayerInventoryItem](
            PlayerInventoryItem, id=0xd31b2209, original_name='EnergyTank', from_json=PlayerInventoryItem.from_json, to_json=PlayerInventoryItem.to_json
        ),
    })
    fuses: PlayerInventoryItem = dataclasses.field(default_factory=PlayerInventoryItem, metadata={
        'reflection': FieldReflection[PlayerInventoryItem](
            PlayerInventoryItem, id=0x152ed0d9, original_name='Fuses', from_json=PlayerInventoryItem.from_json, to_json=PlayerInventoryItem.to_json
        ),
    })
    player_inventory_item: PlayerInventoryItem = dataclasses.field(default_factory=PlayerInventoryItem, metadata={
        'reflection': FieldReflection[PlayerInventoryItem](
            PlayerInventoryItem, id=0x950a91ae, original_name='PlayerInventoryItem', from_json=PlayerInventoryItem.from_json, to_json=PlayerInventoryItem.to_json
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
        if property_count != 4:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x336bd471
        energy = PlayerInventoryItem.from_stream(data, property_size, default_override={'amount': 1, 'capacity': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd31b2209
        energy_tank = PlayerInventoryItem.from_stream(data, property_size, default_override={'amount': 1, 'capacity': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x152ed0d9
        fuses = PlayerInventoryItem.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x950a91ae
        player_inventory_item = PlayerInventoryItem.from_stream(data, property_size)
    
        return cls(energy, energy_tank, fuses, player_inventory_item)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'3k\xd4q')  # 0x336bd471
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.energy.to_stream(data, default_override={'amount': 1, 'capacity': 1})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd3\x1b"\t')  # 0xd31b2209
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.energy_tank.to_stream(data, default_override={'amount': 1, 'capacity': 1})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x15.\xd0\xd9')  # 0x152ed0d9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.fuses.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x95\n\x91\xae')  # 0x950a91ae
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.player_inventory_item.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MiscJson", data)
        return cls(
            energy=PlayerInventoryItem.from_json(json_data['energy']),
            energy_tank=PlayerInventoryItem.from_json(json_data['energy_tank']),
            fuses=PlayerInventoryItem.from_json(json_data['fuses']),
            player_inventory_item=PlayerInventoryItem.from_json(json_data['player_inventory_item']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'energy': self.energy.to_json(),
            'energy_tank': self.energy_tank.to_json(),
            'fuses': self.fuses.to_json(),
            'player_inventory_item': self.player_inventory_item.to_json(),
        }


def _decode_energy(data: typing.BinaryIO, property_size: int) -> PlayerInventoryItem:
    return PlayerInventoryItem.from_stream(data, property_size, default_override={'amount': 1, 'capacity': 1})


def _decode_energy_tank(data: typing.BinaryIO, property_size: int) -> PlayerInventoryItem:
    return PlayerInventoryItem.from_stream(data, property_size, default_override={'amount': 1, 'capacity': 1})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x336bd471: ('energy', _decode_energy),
    0xd31b2209: ('energy_tank', _decode_energy_tank),
    0x152ed0d9: ('fuses', PlayerInventoryItem.from_stream),
    0x950a91ae: ('player_inventory_item', PlayerInventoryItem.from_stream),
}
