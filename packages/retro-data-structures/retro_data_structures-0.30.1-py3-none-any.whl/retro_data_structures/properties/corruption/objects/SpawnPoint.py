# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.archetypes.Inventory import Inventory

if typing.TYPE_CHECKING:
    class SpawnPointJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        first_spawn: bool
        morphed: bool
        unknown_0xa7a88fef: bool
        death_fall: bool
        unknown_0xab0b9ac4: bool
        unknown_0x4ad656da: bool
        inventory_player: json_util.JsonObject
    

@dataclasses.dataclass()
class SpawnPoint(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    first_spawn: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc0e4521b, original_name='FirstSpawn'
        ),
    })
    morphed: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb9c40f92, original_name='Morphed'
        ),
    })
    unknown_0xa7a88fef: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa7a88fef, original_name='Unknown'
        ),
    })
    death_fall: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x210f2626, original_name='DeathFall'
        ),
    })
    unknown_0xab0b9ac4: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xab0b9ac4, original_name='Unknown'
        ),
    })
    unknown_0x4ad656da: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4ad656da, original_name='Unknown'
        ),
    })
    inventory_player: Inventory = dataclasses.field(default_factory=Inventory, metadata={
        'reflection': FieldReflection[Inventory](
            Inventory, id=0xf4ed9547, original_name='InventoryPlayer', from_json=Inventory.from_json, to_json=Inventory.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'SPWN'

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        struct_id, size, property_count = struct.unpack(">LHH", data.read(8))
        assert struct_id == 0xFFFFFFFF
        root_size_start = data.tell() - 2

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

        assert data.tell() - root_size_start == size
        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc0e4521b
        first_spawn = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb9c40f92
        morphed = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7a88fef
        unknown_0xa7a88fef = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x210f2626
        death_fall = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xab0b9ac4
        unknown_0xab0b9ac4 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ad656da
        unknown_0x4ad656da = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf4ed9547
        inventory_player = Inventory.from_stream(data, property_size)
    
        return cls(editor_properties, first_spawn, morphed, unknown_0xa7a88fef, death_fall, unknown_0xab0b9ac4, unknown_0x4ad656da, inventory_player)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc0\xe4R\x1b')  # 0xc0e4521b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.first_spawn))

        data.write(b'\xb9\xc4\x0f\x92')  # 0xb9c40f92
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.morphed))

        data.write(b'\xa7\xa8\x8f\xef')  # 0xa7a88fef
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xa7a88fef))

        data.write(b'!\x0f&&')  # 0x210f2626
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.death_fall))

        data.write(b'\xab\x0b\x9a\xc4')  # 0xab0b9ac4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xab0b9ac4))

        data.write(b'J\xd6V\xda')  # 0x4ad656da
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4ad656da))

        data.write(b'\xf4\xed\x95G')  # 0xf4ed9547
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.inventory_player.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpawnPointJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            first_spawn=json_data['first_spawn'],
            morphed=json_data['morphed'],
            unknown_0xa7a88fef=json_data['unknown_0xa7a88fef'],
            death_fall=json_data['death_fall'],
            unknown_0xab0b9ac4=json_data['unknown_0xab0b9ac4'],
            unknown_0x4ad656da=json_data['unknown_0x4ad656da'],
            inventory_player=Inventory.from_json(json_data['inventory_player']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'first_spawn': self.first_spawn,
            'morphed': self.morphed,
            'unknown_0xa7a88fef': self.unknown_0xa7a88fef,
            'death_fall': self.death_fall,
            'unknown_0xab0b9ac4': self.unknown_0xab0b9ac4,
            'unknown_0x4ad656da': self.unknown_0x4ad656da,
            'inventory_player': self.inventory_player.to_json(),
        }


def _decode_first_spawn(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_morphed(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xa7a88fef(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_death_fall(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xab0b9ac4(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4ad656da(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xc0e4521b: ('first_spawn', _decode_first_spawn),
    0xb9c40f92: ('morphed', _decode_morphed),
    0xa7a88fef: ('unknown_0xa7a88fef', _decode_unknown_0xa7a88fef),
    0x210f2626: ('death_fall', _decode_death_fall),
    0xab0b9ac4: ('unknown_0xab0b9ac4', _decode_unknown_0xab0b9ac4),
    0x4ad656da: ('unknown_0x4ad656da', _decode_unknown_0x4ad656da),
    0xf4ed9547: ('inventory_player', Inventory.from_stream),
}
