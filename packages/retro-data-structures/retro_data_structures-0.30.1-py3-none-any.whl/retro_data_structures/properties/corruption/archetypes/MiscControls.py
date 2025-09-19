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
from retro_data_structures.properties.corruption.archetypes.InventoryControls import InventoryControls
from retro_data_structures.properties.corruption.archetypes.MapControls import MapControls
from retro_data_structures.properties.corruption.archetypes.MiscControls_UnknownStruct1 import MiscControls_UnknownStruct1
from retro_data_structures.properties.corruption.archetypes.MiscControls_UnknownStruct2 import MiscControls_UnknownStruct2
from retro_data_structures.properties.corruption.archetypes.RevolutionControl import RevolutionControl

if typing.TYPE_CHECKING:
    class MiscControlsJson(typing_extensions.TypedDict):
        map: json_util.JsonObject
        inventory: json_util.JsonObject
        options_screen: json_util.JsonObject
        unknown_0xc6232204: json_util.JsonObject
        unknown_0x5126ffe7: json_util.JsonObject
        unknown_0x439f3678: json_util.JsonObject
    

@dataclasses.dataclass()
class MiscControls(BaseProperty):
    map: MapControls = dataclasses.field(default_factory=MapControls, metadata={
        'reflection': FieldReflection[MapControls](
            MapControls, id=0x9acb4ace, original_name='Map', from_json=MapControls.from_json, to_json=MapControls.to_json
        ),
    })
    inventory: InventoryControls = dataclasses.field(default_factory=InventoryControls, metadata={
        'reflection': FieldReflection[InventoryControls](
            InventoryControls, id=0xed3482b7, original_name='Inventory', from_json=InventoryControls.from_json, to_json=InventoryControls.to_json
        ),
    })
    options_screen: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x36e52f14, original_name='OptionsScreen', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xc6232204: MiscControls_UnknownStruct1 = dataclasses.field(default_factory=MiscControls_UnknownStruct1, metadata={
        'reflection': FieldReflection[MiscControls_UnknownStruct1](
            MiscControls_UnknownStruct1, id=0xc6232204, original_name='Unknown', from_json=MiscControls_UnknownStruct1.from_json, to_json=MiscControls_UnknownStruct1.to_json
        ),
    })
    unknown_0x5126ffe7: MiscControls_UnknownStruct2 = dataclasses.field(default_factory=MiscControls_UnknownStruct2, metadata={
        'reflection': FieldReflection[MiscControls_UnknownStruct2](
            MiscControls_UnknownStruct2, id=0x5126ffe7, original_name='Unknown', from_json=MiscControls_UnknownStruct2.from_json, to_json=MiscControls_UnknownStruct2.to_json
        ),
    })
    unknown_0x439f3678: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x439f3678, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
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
        if property_count != 6:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9acb4ace
        map = MapControls.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed3482b7
        inventory = InventoryControls.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x36e52f14
        options_screen = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6232204
        unknown_0xc6232204 = MiscControls_UnknownStruct1.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5126ffe7
        unknown_0x5126ffe7 = MiscControls_UnknownStruct2.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x439f3678
        unknown_0x439f3678 = RevolutionControl.from_stream(data, property_size)
    
        return cls(map, inventory, options_screen, unknown_0xc6232204, unknown_0x5126ffe7, unknown_0x439f3678)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'\x9a\xcbJ\xce')  # 0x9acb4ace
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.map.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed4\x82\xb7')  # 0xed3482b7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.inventory.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'6\xe5/\x14')  # 0x36e52f14
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.options_screen.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc6#"\x04')  # 0xc6232204
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xc6232204.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'Q&\xff\xe7')  # 0x5126ffe7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x5126ffe7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'C\x9f6x')  # 0x439f3678
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x439f3678.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MiscControlsJson", data)
        return cls(
            map=MapControls.from_json(json_data['map']),
            inventory=InventoryControls.from_json(json_data['inventory']),
            options_screen=RevolutionControl.from_json(json_data['options_screen']),
            unknown_0xc6232204=MiscControls_UnknownStruct1.from_json(json_data['unknown_0xc6232204']),
            unknown_0x5126ffe7=MiscControls_UnknownStruct2.from_json(json_data['unknown_0x5126ffe7']),
            unknown_0x439f3678=RevolutionControl.from_json(json_data['unknown_0x439f3678']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'map': self.map.to_json(),
            'inventory': self.inventory.to_json(),
            'options_screen': self.options_screen.to_json(),
            'unknown_0xc6232204': self.unknown_0xc6232204.to_json(),
            'unknown_0x5126ffe7': self.unknown_0x5126ffe7.to_json(),
            'unknown_0x439f3678': self.unknown_0x439f3678.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x9acb4ace: ('map', MapControls.from_stream),
    0xed3482b7: ('inventory', InventoryControls.from_stream),
    0x36e52f14: ('options_screen', RevolutionControl.from_stream),
    0xc6232204: ('unknown_0xc6232204', MiscControls_UnknownStruct1.from_stream),
    0x5126ffe7: ('unknown_0x5126ffe7', MiscControls_UnknownStruct2.from_stream),
    0x439f3678: ('unknown_0x439f3678', RevolutionControl.from_stream),
}
