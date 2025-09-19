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
from retro_data_structures.properties.corruption.archetypes.CounterConditions import CounterConditions
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties

if typing.TYPE_CHECKING:
    class CounterJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        initial_count: int
        max_count: int
        auto_reset: bool
        wrap: bool
        counter_conditions: json_util.JsonObject
    

@dataclasses.dataclass()
class Counter(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    initial_count: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xfd179a6f, original_name='Initial_Count'
        ),
    })
    max_count: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5b851589, original_name='Max_Count'
        ),
    })
    auto_reset: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7bef45ca, original_name='AutoReset'
        ),
    })
    wrap: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf076cef5, original_name='Wrap'
        ),
    })
    counter_conditions: CounterConditions = dataclasses.field(default_factory=CounterConditions, metadata={
        'reflection': FieldReflection[CounterConditions](
            CounterConditions, id=0x9c1d33de, original_name='CounterConditions', from_json=CounterConditions.from_json, to_json=CounterConditions.to_json
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
        return 'CNTR'

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
        if property_count != 6:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd179a6f
        initial_count = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5b851589
        max_count = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7bef45ca
        auto_reset = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf076cef5
        wrap = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9c1d33de
        counter_conditions = CounterConditions.from_stream(data, property_size)
    
        return cls(editor_properties, initial_count, max_count, auto_reset, wrap, counter_conditions)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfd\x17\x9ao')  # 0xfd179a6f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.initial_count))

        data.write(b'[\x85\x15\x89')  # 0x5b851589
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_count))

        data.write(b'{\xefE\xca')  # 0x7bef45ca
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.auto_reset))

        data.write(b'\xf0v\xce\xf5')  # 0xf076cef5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.wrap))

        data.write(b'\x9c\x1d3\xde')  # 0x9c1d33de
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.counter_conditions.to_stream(data)
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
        json_data = typing.cast("CounterJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            initial_count=json_data['initial_count'],
            max_count=json_data['max_count'],
            auto_reset=json_data['auto_reset'],
            wrap=json_data['wrap'],
            counter_conditions=CounterConditions.from_json(json_data['counter_conditions']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'initial_count': self.initial_count,
            'max_count': self.max_count,
            'auto_reset': self.auto_reset,
            'wrap': self.wrap,
            'counter_conditions': self.counter_conditions.to_json(),
        }


def _decode_initial_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_max_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_auto_reset(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_wrap(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xfd179a6f: ('initial_count', _decode_initial_count),
    0x5b851589: ('max_count', _decode_max_count),
    0x7bef45ca: ('auto_reset', _decode_auto_reset),
    0xf076cef5: ('wrap', _decode_wrap),
    0x9c1d33de: ('counter_conditions', CounterConditions.from_stream),
}
