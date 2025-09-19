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
from retro_data_structures.properties.corruption.archetypes.UnknownStruct65 import UnknownStruct65

if typing.TYPE_CHECKING:
    class WorldTeleporterAttributesJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        unknown_struct65: json_util.JsonObject
        unknown_0xfae81682: json_util.JsonObject
        unknown_0x5f63868c: json_util.JsonObject
        unknown_0x91337a24: json_util.JsonObject
        unknown_0x34b8ea2a: json_util.JsonObject
        unknown_0x01555c79: json_util.JsonObject
        unknown_0xa4decc77: json_util.JsonObject
        unknown_0x4685a368: json_util.JsonObject
        unknown_0xe30e3366: json_util.JsonObject
        unknown_0xee37cd3c: json_util.JsonObject
        unknown_0x4bbc5d32: json_util.JsonObject
        unknown_0x7e51eb61: json_util.JsonObject
        unknown_0xdbda7b6f: json_util.JsonObject
        unknown_0x158a87c7: json_util.JsonObject
        unknown_0xb00117c9: json_util.JsonObject
        unknown_0x85eca19a: json_util.JsonObject
        unknown_0x20673194: json_util.JsonObject
        unknown_0xc23c5e8b: json_util.JsonObject
        unknown_0x67b7ce85: json_util.JsonObject
        unknown_0x1c6020c4: json_util.JsonObject
    

@dataclasses.dataclass()
class WorldTeleporterAttributes(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    unknown_struct65: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0xcf05a0d1, original_name='UnknownStruct65', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0xfae81682: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0xfae81682, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x5f63868c: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x5f63868c, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x91337a24: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x91337a24, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x34b8ea2a: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x34b8ea2a, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x01555c79: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x01555c79, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0xa4decc77: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0xa4decc77, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x4685a368: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x4685a368, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0xe30e3366: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0xe30e3366, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0xee37cd3c: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0xee37cd3c, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x4bbc5d32: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x4bbc5d32, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x7e51eb61: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x7e51eb61, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0xdbda7b6f: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0xdbda7b6f, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x158a87c7: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x158a87c7, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0xb00117c9: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0xb00117c9, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x85eca19a: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x85eca19a, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x20673194: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x20673194, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0xc23c5e8b: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0xc23c5e8b, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x67b7ce85: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x67b7ce85, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
        ),
    })
    unknown_0x1c6020c4: UnknownStruct65 = dataclasses.field(default_factory=UnknownStruct65, metadata={
        'reflection': FieldReflection[UnknownStruct65](
            UnknownStruct65, id=0x1c6020c4, original_name='Unknown', from_json=UnknownStruct65.from_json, to_json=UnknownStruct65.to_json
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
        return 'WTAT'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_ScriptWorldTeleporterAttributes.rso']

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
        if property_count != 21:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf05a0d1
        unknown_struct65 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfae81682
        unknown_0xfae81682 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5f63868c
        unknown_0x5f63868c = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x91337a24
        unknown_0x91337a24 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x34b8ea2a
        unknown_0x34b8ea2a = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01555c79
        unknown_0x01555c79 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa4decc77
        unknown_0xa4decc77 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4685a368
        unknown_0x4685a368 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe30e3366
        unknown_0xe30e3366 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xee37cd3c
        unknown_0xee37cd3c = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4bbc5d32
        unknown_0x4bbc5d32 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e51eb61
        unknown_0x7e51eb61 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdbda7b6f
        unknown_0xdbda7b6f = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x158a87c7
        unknown_0x158a87c7 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb00117c9
        unknown_0xb00117c9 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x85eca19a
        unknown_0x85eca19a = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x20673194
        unknown_0x20673194 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc23c5e8b
        unknown_0xc23c5e8b = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x67b7ce85
        unknown_0x67b7ce85 = UnknownStruct65.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1c6020c4
        unknown_0x1c6020c4 = UnknownStruct65.from_stream(data, property_size)
    
        return cls(editor_properties, unknown_struct65, unknown_0xfae81682, unknown_0x5f63868c, unknown_0x91337a24, unknown_0x34b8ea2a, unknown_0x01555c79, unknown_0xa4decc77, unknown_0x4685a368, unknown_0xe30e3366, unknown_0xee37cd3c, unknown_0x4bbc5d32, unknown_0x7e51eb61, unknown_0xdbda7b6f, unknown_0x158a87c7, unknown_0xb00117c9, unknown_0x85eca19a, unknown_0x20673194, unknown_0xc23c5e8b, unknown_0x67b7ce85, unknown_0x1c6020c4)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0f')  # 15 properties
        num_properties_written = 15

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xcf\x05\xa0\xd1')  # 0xcf05a0d1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct65.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfa\xe8\x16\x82')  # 0xfae81682
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xfae81682.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'_c\x86\x8c')  # 0x5f63868c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x5f63868c.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x913z$')  # 0x91337a24
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x91337a24.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'4\xb8\xea*')  # 0x34b8ea2a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x34b8ea2a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x01U\\y')  # 0x1555c79
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x01555c79.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa4\xde\xccw')  # 0xa4decc77
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xa4decc77.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'F\x85\xa3h')  # 0x4685a368
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x4685a368.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe3\x0e3f')  # 0xe30e3366
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xe30e3366.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xee7\xcd<')  # 0xee37cd3c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xee37cd3c.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'K\xbc]2')  # 0x4bbc5d32
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x4bbc5d32.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'~Q\xeba')  # 0x7e51eb61
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x7e51eb61.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdb\xda{o')  # 0xdbda7b6f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xdbda7b6f.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x15\x8a\x87\xc7')  # 0x158a87c7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x158a87c7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        if self.unknown_0xb00117c9 != default_override.get('unknown_0xb00117c9', UnknownStruct65()):
            num_properties_written += 1
            data.write(b'\xb0\x01\x17\xc9')  # 0xb00117c9
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0xb00117c9.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0x85eca19a != default_override.get('unknown_0x85eca19a', UnknownStruct65()):
            num_properties_written += 1
            data.write(b'\x85\xec\xa1\x9a')  # 0x85eca19a
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0x85eca19a.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0x20673194 != default_override.get('unknown_0x20673194', UnknownStruct65()):
            num_properties_written += 1
            data.write(b' g1\x94')  # 0x20673194
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0x20673194.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0xc23c5e8b != default_override.get('unknown_0xc23c5e8b', UnknownStruct65()):
            num_properties_written += 1
            data.write(b'\xc2<^\x8b')  # 0xc23c5e8b
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0xc23c5e8b.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0x67b7ce85 != default_override.get('unknown_0x67b7ce85', UnknownStruct65()):
            num_properties_written += 1
            data.write(b'g\xb7\xce\x85')  # 0x67b7ce85
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0x67b7ce85.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0x1c6020c4 != default_override.get('unknown_0x1c6020c4', UnknownStruct65()):
            num_properties_written += 1
            data.write(b'\x1c` \xc4')  # 0x1c6020c4
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0x1c6020c4.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.write(struct.pack(">H", num_properties_written))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("WorldTeleporterAttributesJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            unknown_struct65=UnknownStruct65.from_json(json_data['unknown_struct65']),
            unknown_0xfae81682=UnknownStruct65.from_json(json_data['unknown_0xfae81682']),
            unknown_0x5f63868c=UnknownStruct65.from_json(json_data['unknown_0x5f63868c']),
            unknown_0x91337a24=UnknownStruct65.from_json(json_data['unknown_0x91337a24']),
            unknown_0x34b8ea2a=UnknownStruct65.from_json(json_data['unknown_0x34b8ea2a']),
            unknown_0x01555c79=UnknownStruct65.from_json(json_data['unknown_0x01555c79']),
            unknown_0xa4decc77=UnknownStruct65.from_json(json_data['unknown_0xa4decc77']),
            unknown_0x4685a368=UnknownStruct65.from_json(json_data['unknown_0x4685a368']),
            unknown_0xe30e3366=UnknownStruct65.from_json(json_data['unknown_0xe30e3366']),
            unknown_0xee37cd3c=UnknownStruct65.from_json(json_data['unknown_0xee37cd3c']),
            unknown_0x4bbc5d32=UnknownStruct65.from_json(json_data['unknown_0x4bbc5d32']),
            unknown_0x7e51eb61=UnknownStruct65.from_json(json_data['unknown_0x7e51eb61']),
            unknown_0xdbda7b6f=UnknownStruct65.from_json(json_data['unknown_0xdbda7b6f']),
            unknown_0x158a87c7=UnknownStruct65.from_json(json_data['unknown_0x158a87c7']),
            unknown_0xb00117c9=UnknownStruct65.from_json(json_data['unknown_0xb00117c9']),
            unknown_0x85eca19a=UnknownStruct65.from_json(json_data['unknown_0x85eca19a']),
            unknown_0x20673194=UnknownStruct65.from_json(json_data['unknown_0x20673194']),
            unknown_0xc23c5e8b=UnknownStruct65.from_json(json_data['unknown_0xc23c5e8b']),
            unknown_0x67b7ce85=UnknownStruct65.from_json(json_data['unknown_0x67b7ce85']),
            unknown_0x1c6020c4=UnknownStruct65.from_json(json_data['unknown_0x1c6020c4']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'unknown_struct65': self.unknown_struct65.to_json(),
            'unknown_0xfae81682': self.unknown_0xfae81682.to_json(),
            'unknown_0x5f63868c': self.unknown_0x5f63868c.to_json(),
            'unknown_0x91337a24': self.unknown_0x91337a24.to_json(),
            'unknown_0x34b8ea2a': self.unknown_0x34b8ea2a.to_json(),
            'unknown_0x01555c79': self.unknown_0x01555c79.to_json(),
            'unknown_0xa4decc77': self.unknown_0xa4decc77.to_json(),
            'unknown_0x4685a368': self.unknown_0x4685a368.to_json(),
            'unknown_0xe30e3366': self.unknown_0xe30e3366.to_json(),
            'unknown_0xee37cd3c': self.unknown_0xee37cd3c.to_json(),
            'unknown_0x4bbc5d32': self.unknown_0x4bbc5d32.to_json(),
            'unknown_0x7e51eb61': self.unknown_0x7e51eb61.to_json(),
            'unknown_0xdbda7b6f': self.unknown_0xdbda7b6f.to_json(),
            'unknown_0x158a87c7': self.unknown_0x158a87c7.to_json(),
            'unknown_0xb00117c9': self.unknown_0xb00117c9.to_json(),
            'unknown_0x85eca19a': self.unknown_0x85eca19a.to_json(),
            'unknown_0x20673194': self.unknown_0x20673194.to_json(),
            'unknown_0xc23c5e8b': self.unknown_0xc23c5e8b.to_json(),
            'unknown_0x67b7ce85': self.unknown_0x67b7ce85.to_json(),
            'unknown_0x1c6020c4': self.unknown_0x1c6020c4.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xcf05a0d1: ('unknown_struct65', UnknownStruct65.from_stream),
    0xfae81682: ('unknown_0xfae81682', UnknownStruct65.from_stream),
    0x5f63868c: ('unknown_0x5f63868c', UnknownStruct65.from_stream),
    0x91337a24: ('unknown_0x91337a24', UnknownStruct65.from_stream),
    0x34b8ea2a: ('unknown_0x34b8ea2a', UnknownStruct65.from_stream),
    0x1555c79: ('unknown_0x01555c79', UnknownStruct65.from_stream),
    0xa4decc77: ('unknown_0xa4decc77', UnknownStruct65.from_stream),
    0x4685a368: ('unknown_0x4685a368', UnknownStruct65.from_stream),
    0xe30e3366: ('unknown_0xe30e3366', UnknownStruct65.from_stream),
    0xee37cd3c: ('unknown_0xee37cd3c', UnknownStruct65.from_stream),
    0x4bbc5d32: ('unknown_0x4bbc5d32', UnknownStruct65.from_stream),
    0x7e51eb61: ('unknown_0x7e51eb61', UnknownStruct65.from_stream),
    0xdbda7b6f: ('unknown_0xdbda7b6f', UnknownStruct65.from_stream),
    0x158a87c7: ('unknown_0x158a87c7', UnknownStruct65.from_stream),
    0xb00117c9: ('unknown_0xb00117c9', UnknownStruct65.from_stream),
    0x85eca19a: ('unknown_0x85eca19a', UnknownStruct65.from_stream),
    0x20673194: ('unknown_0x20673194', UnknownStruct65.from_stream),
    0xc23c5e8b: ('unknown_0xc23c5e8b', UnknownStruct65.from_stream),
    0x67b7ce85: ('unknown_0x67b7ce85', UnknownStruct65.from_stream),
    0x1c6020c4: ('unknown_0x1c6020c4', UnknownStruct65.from_stream),
}
