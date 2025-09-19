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
from retro_data_structures.properties.corruption.archetypes.RevolutionControl import RevolutionControl

if typing.TYPE_CHECKING:
    class InventoryControlsJson(typing_extensions.TypedDict):
        unknown_0x340f912e: json_util.JsonObject
        menu_up: json_util.JsonObject
        menu_down: json_util.JsonObject
        menu_left: json_util.JsonObject
        menu_right: json_util.JsonObject
        menu_select: json_util.JsonObject
        unknown_0x68ea537d: json_util.JsonObject
    

@dataclasses.dataclass()
class InventoryControls(BaseProperty):
    unknown_0x340f912e: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x340f912e, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    menu_up: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x769909c1, original_name='MenuUp', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    menu_down: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x4dab695e, original_name='MenuDown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    menu_left: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xc7cae2d3, original_name='MenuLeft', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    menu_right: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x1595f276, original_name='MenuRight', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    menu_select: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xbf09b38b, original_name='MenuSelect', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0x68ea537d: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x68ea537d, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
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
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x340f912e
        unknown_0x340f912e = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x769909c1
        menu_up = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4dab695e
        menu_down = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc7cae2d3
        menu_left = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1595f276
        menu_right = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbf09b38b
        menu_select = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68ea537d
        unknown_0x68ea537d = RevolutionControl.from_stream(data, property_size)
    
        return cls(unknown_0x340f912e, menu_up, menu_down, menu_left, menu_right, menu_select, unknown_0x68ea537d)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'4\x0f\x91.')  # 0x340f912e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x340f912e.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'v\x99\t\xc1')  # 0x769909c1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.menu_up.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'M\xabi^')  # 0x4dab695e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.menu_down.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc7\xca\xe2\xd3')  # 0xc7cae2d3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.menu_left.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x15\x95\xf2v')  # 0x1595f276
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.menu_right.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbf\t\xb3\x8b')  # 0xbf09b38b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.menu_select.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'h\xeaS}')  # 0x68ea537d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x68ea537d.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("InventoryControlsJson", data)
        return cls(
            unknown_0x340f912e=RevolutionControl.from_json(json_data['unknown_0x340f912e']),
            menu_up=RevolutionControl.from_json(json_data['menu_up']),
            menu_down=RevolutionControl.from_json(json_data['menu_down']),
            menu_left=RevolutionControl.from_json(json_data['menu_left']),
            menu_right=RevolutionControl.from_json(json_data['menu_right']),
            menu_select=RevolutionControl.from_json(json_data['menu_select']),
            unknown_0x68ea537d=RevolutionControl.from_json(json_data['unknown_0x68ea537d']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x340f912e': self.unknown_0x340f912e.to_json(),
            'menu_up': self.menu_up.to_json(),
            'menu_down': self.menu_down.to_json(),
            'menu_left': self.menu_left.to_json(),
            'menu_right': self.menu_right.to_json(),
            'menu_select': self.menu_select.to_json(),
            'unknown_0x68ea537d': self.unknown_0x68ea537d.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x340f912e: ('unknown_0x340f912e', RevolutionControl.from_stream),
    0x769909c1: ('menu_up', RevolutionControl.from_stream),
    0x4dab695e: ('menu_down', RevolutionControl.from_stream),
    0xc7cae2d3: ('menu_left', RevolutionControl.from_stream),
    0x1595f276: ('menu_right', RevolutionControl.from_stream),
    0xbf09b38b: ('menu_select', RevolutionControl.from_stream),
    0x68ea537d: ('unknown_0x68ea537d', RevolutionControl.from_stream),
}
