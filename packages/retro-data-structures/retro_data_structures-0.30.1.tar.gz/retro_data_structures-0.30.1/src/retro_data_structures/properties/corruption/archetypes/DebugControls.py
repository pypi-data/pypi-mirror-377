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
    class DebugControlsJson(typing_extensions.TypedDict):
        move_camera: json_util.JsonObject
        unknown_0xce9d8f9b: json_util.JsonObject
        unknown_0xcf8d32f4: json_util.JsonObject
        unknown_0x6e2701e2: json_util.JsonObject
        unknown_0x233dfcb8: json_util.JsonObject
        unknown_0x6c8eda79: json_util.JsonObject
        unknown_0x52739b7b: json_util.JsonObject
        unknown_0x936c903d: json_util.JsonObject
        unknown_0xf3e413f0: json_util.JsonObject
        unknown_0x769412eb: json_util.JsonObject
        toggle_camera: json_util.JsonObject
        unknown_0xfc31e19e: json_util.JsonObject
        menu_start: json_util.JsonObject
        menu_up: json_util.JsonObject
        menu_down: json_util.JsonObject
        menu_left: json_util.JsonObject
        menu_right: json_util.JsonObject
        menu_select: json_util.JsonObject
        menu_back: json_util.JsonObject
        unknown_0xd38203d7: json_util.JsonObject
        unknown_0xed1235d3: json_util.JsonObject
        unknown_0xc73501a3: json_util.JsonObject
        restart_level: json_util.JsonObject
        map_teleport: json_util.JsonObject
        advance_frame: json_util.JsonObject
    

@dataclasses.dataclass()
class DebugControls(BaseProperty):
    move_camera: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x38ed0ec3, original_name='MoveCamera', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xce9d8f9b: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xce9d8f9b, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xcf8d32f4: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xcf8d32f4, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0x6e2701e2: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x6e2701e2, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0x233dfcb8: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x233dfcb8, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0x6c8eda79: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x6c8eda79, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0x52739b7b: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x52739b7b, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0x936c903d: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x936c903d, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xf3e413f0: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xf3e413f0, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0x769412eb: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x769412eb, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    toggle_camera: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xce92be94, original_name='ToggleCamera', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xfc31e19e: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xfc31e19e, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    menu_start: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x0bfcb7a2, original_name='MenuStart', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
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
    menu_back: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xbcbe70f0, original_name='MenuBack', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xd38203d7: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xd38203d7, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xed1235d3: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xed1235d3, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xc73501a3: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xc73501a3, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    restart_level: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xc578ca0d, original_name='RestartLevel', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    map_teleport: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x8bb24630, original_name='MapTeleport', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    advance_frame: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x4c3fa03b, original_name='AdvanceFrame', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
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
        if property_count != 25:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x38ed0ec3
        move_camera = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce9d8f9b
        unknown_0xce9d8f9b = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf8d32f4
        unknown_0xcf8d32f4 = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6e2701e2
        unknown_0x6e2701e2 = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x233dfcb8
        unknown_0x233dfcb8 = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c8eda79
        unknown_0x6c8eda79 = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x52739b7b
        unknown_0x52739b7b = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x936c903d
        unknown_0x936c903d = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3e413f0
        unknown_0xf3e413f0 = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x769412eb
        unknown_0x769412eb = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce92be94
        toggle_camera = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfc31e19e
        unknown_0xfc31e19e = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0bfcb7a2
        menu_start = RevolutionControl.from_stream(data, property_size)
    
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
        assert property_id == 0xbcbe70f0
        menu_back = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd38203d7
        unknown_0xd38203d7 = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed1235d3
        unknown_0xed1235d3 = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc73501a3
        unknown_0xc73501a3 = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc578ca0d
        restart_level = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8bb24630
        map_teleport = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4c3fa03b
        advance_frame = RevolutionControl.from_stream(data, property_size)
    
        return cls(move_camera, unknown_0xce9d8f9b, unknown_0xcf8d32f4, unknown_0x6e2701e2, unknown_0x233dfcb8, unknown_0x6c8eda79, unknown_0x52739b7b, unknown_0x936c903d, unknown_0xf3e413f0, unknown_0x769412eb, toggle_camera, unknown_0xfc31e19e, menu_start, menu_up, menu_down, menu_left, menu_right, menu_select, menu_back, unknown_0xd38203d7, unknown_0xed1235d3, unknown_0xc73501a3, restart_level, map_teleport, advance_frame)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x19')  # 25 properties

        data.write(b'8\xed\x0e\xc3')  # 0x38ed0ec3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.move_camera.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xce\x9d\x8f\x9b')  # 0xce9d8f9b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xce9d8f9b.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xcf\x8d2\xf4')  # 0xcf8d32f4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xcf8d32f4.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"n'\x01\xe2")  # 0x6e2701e2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x6e2701e2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'#=\xfc\xb8')  # 0x233dfcb8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x233dfcb8.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'l\x8e\xday')  # 0x6c8eda79
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x6c8eda79.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'Rs\x9b{')  # 0x52739b7b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x52739b7b.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x93l\x90=')  # 0x936c903d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x936c903d.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf3\xe4\x13\xf0')  # 0xf3e413f0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xf3e413f0.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'v\x94\x12\xeb')  # 0x769412eb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x769412eb.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xce\x92\xbe\x94')  # 0xce92be94
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.toggle_camera.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfc1\xe1\x9e')  # 0xfc31e19e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xfc31e19e.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0b\xfc\xb7\xa2')  # 0xbfcb7a2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.menu_start.to_stream(data)
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

        data.write(b'\xbc\xbep\xf0')  # 0xbcbe70f0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.menu_back.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd3\x82\x03\xd7')  # 0xd38203d7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xd38203d7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed\x125\xd3')  # 0xed1235d3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xed1235d3.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc75\x01\xa3')  # 0xc73501a3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xc73501a3.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc5x\xca\r')  # 0xc578ca0d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.restart_level.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8b\xb2F0')  # 0x8bb24630
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.map_teleport.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'L?\xa0;')  # 0x4c3fa03b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.advance_frame.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DebugControlsJson", data)
        return cls(
            move_camera=RevolutionControl.from_json(json_data['move_camera']),
            unknown_0xce9d8f9b=RevolutionControl.from_json(json_data['unknown_0xce9d8f9b']),
            unknown_0xcf8d32f4=RevolutionControl.from_json(json_data['unknown_0xcf8d32f4']),
            unknown_0x6e2701e2=RevolutionControl.from_json(json_data['unknown_0x6e2701e2']),
            unknown_0x233dfcb8=RevolutionControl.from_json(json_data['unknown_0x233dfcb8']),
            unknown_0x6c8eda79=RevolutionControl.from_json(json_data['unknown_0x6c8eda79']),
            unknown_0x52739b7b=RevolutionControl.from_json(json_data['unknown_0x52739b7b']),
            unknown_0x936c903d=RevolutionControl.from_json(json_data['unknown_0x936c903d']),
            unknown_0xf3e413f0=RevolutionControl.from_json(json_data['unknown_0xf3e413f0']),
            unknown_0x769412eb=RevolutionControl.from_json(json_data['unknown_0x769412eb']),
            toggle_camera=RevolutionControl.from_json(json_data['toggle_camera']),
            unknown_0xfc31e19e=RevolutionControl.from_json(json_data['unknown_0xfc31e19e']),
            menu_start=RevolutionControl.from_json(json_data['menu_start']),
            menu_up=RevolutionControl.from_json(json_data['menu_up']),
            menu_down=RevolutionControl.from_json(json_data['menu_down']),
            menu_left=RevolutionControl.from_json(json_data['menu_left']),
            menu_right=RevolutionControl.from_json(json_data['menu_right']),
            menu_select=RevolutionControl.from_json(json_data['menu_select']),
            menu_back=RevolutionControl.from_json(json_data['menu_back']),
            unknown_0xd38203d7=RevolutionControl.from_json(json_data['unknown_0xd38203d7']),
            unknown_0xed1235d3=RevolutionControl.from_json(json_data['unknown_0xed1235d3']),
            unknown_0xc73501a3=RevolutionControl.from_json(json_data['unknown_0xc73501a3']),
            restart_level=RevolutionControl.from_json(json_data['restart_level']),
            map_teleport=RevolutionControl.from_json(json_data['map_teleport']),
            advance_frame=RevolutionControl.from_json(json_data['advance_frame']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'move_camera': self.move_camera.to_json(),
            'unknown_0xce9d8f9b': self.unknown_0xce9d8f9b.to_json(),
            'unknown_0xcf8d32f4': self.unknown_0xcf8d32f4.to_json(),
            'unknown_0x6e2701e2': self.unknown_0x6e2701e2.to_json(),
            'unknown_0x233dfcb8': self.unknown_0x233dfcb8.to_json(),
            'unknown_0x6c8eda79': self.unknown_0x6c8eda79.to_json(),
            'unknown_0x52739b7b': self.unknown_0x52739b7b.to_json(),
            'unknown_0x936c903d': self.unknown_0x936c903d.to_json(),
            'unknown_0xf3e413f0': self.unknown_0xf3e413f0.to_json(),
            'unknown_0x769412eb': self.unknown_0x769412eb.to_json(),
            'toggle_camera': self.toggle_camera.to_json(),
            'unknown_0xfc31e19e': self.unknown_0xfc31e19e.to_json(),
            'menu_start': self.menu_start.to_json(),
            'menu_up': self.menu_up.to_json(),
            'menu_down': self.menu_down.to_json(),
            'menu_left': self.menu_left.to_json(),
            'menu_right': self.menu_right.to_json(),
            'menu_select': self.menu_select.to_json(),
            'menu_back': self.menu_back.to_json(),
            'unknown_0xd38203d7': self.unknown_0xd38203d7.to_json(),
            'unknown_0xed1235d3': self.unknown_0xed1235d3.to_json(),
            'unknown_0xc73501a3': self.unknown_0xc73501a3.to_json(),
            'restart_level': self.restart_level.to_json(),
            'map_teleport': self.map_teleport.to_json(),
            'advance_frame': self.advance_frame.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x38ed0ec3: ('move_camera', RevolutionControl.from_stream),
    0xce9d8f9b: ('unknown_0xce9d8f9b', RevolutionControl.from_stream),
    0xcf8d32f4: ('unknown_0xcf8d32f4', RevolutionControl.from_stream),
    0x6e2701e2: ('unknown_0x6e2701e2', RevolutionControl.from_stream),
    0x233dfcb8: ('unknown_0x233dfcb8', RevolutionControl.from_stream),
    0x6c8eda79: ('unknown_0x6c8eda79', RevolutionControl.from_stream),
    0x52739b7b: ('unknown_0x52739b7b', RevolutionControl.from_stream),
    0x936c903d: ('unknown_0x936c903d', RevolutionControl.from_stream),
    0xf3e413f0: ('unknown_0xf3e413f0', RevolutionControl.from_stream),
    0x769412eb: ('unknown_0x769412eb', RevolutionControl.from_stream),
    0xce92be94: ('toggle_camera', RevolutionControl.from_stream),
    0xfc31e19e: ('unknown_0xfc31e19e', RevolutionControl.from_stream),
    0xbfcb7a2: ('menu_start', RevolutionControl.from_stream),
    0x769909c1: ('menu_up', RevolutionControl.from_stream),
    0x4dab695e: ('menu_down', RevolutionControl.from_stream),
    0xc7cae2d3: ('menu_left', RevolutionControl.from_stream),
    0x1595f276: ('menu_right', RevolutionControl.from_stream),
    0xbf09b38b: ('menu_select', RevolutionControl.from_stream),
    0xbcbe70f0: ('menu_back', RevolutionControl.from_stream),
    0xd38203d7: ('unknown_0xd38203d7', RevolutionControl.from_stream),
    0xed1235d3: ('unknown_0xed1235d3', RevolutionControl.from_stream),
    0xc73501a3: ('unknown_0xc73501a3', RevolutionControl.from_stream),
    0xc578ca0d: ('restart_level', RevolutionControl.from_stream),
    0x8bb24630: ('map_teleport', RevolutionControl.from_stream),
    0x4c3fa03b: ('advance_frame', RevolutionControl.from_stream),
}
