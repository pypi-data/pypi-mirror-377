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
from retro_data_structures.properties.corruption.archetypes.InterpolationMethod import InterpolationMethod

if typing.TYPE_CHECKING:
    class PlayerHintJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        priority: int
        timer: float
        flags_player_hint: int
        unknown_0xb2367a60: float
        unknown_0x68d9122a: float
        control_frame_interpolation: json_util.JsonObject
    

@dataclasses.dataclass()
class PlayerHint(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    priority: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x42087650, original_name='Priority'
        ),
    })
    timer: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8747552e, original_name='Timer'
        ),
    })
    flags_player_hint: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1bce57e1, original_name='FlagsPlayerHint'
        ),
    })  # Flagset
    unknown_0xb2367a60: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb2367a60, original_name='Unknown'
        ),
    })
    unknown_0x68d9122a: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x68d9122a, original_name='Unknown'
        ),
    })
    control_frame_interpolation: InterpolationMethod = dataclasses.field(default_factory=InterpolationMethod, metadata={
        'reflection': FieldReflection[InterpolationMethod](
            InterpolationMethod, id=0x95d0d437, original_name='ControlFrameInterpolation', from_json=InterpolationMethod.from_json, to_json=InterpolationMethod.to_json
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
        return 'HINT'

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
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42087650
        priority = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8747552e
        timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1bce57e1
        flags_player_hint = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2367a60
        unknown_0xb2367a60 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68d9122a
        unknown_0x68d9122a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95d0d437
        control_frame_interpolation = InterpolationMethod.from_stream(data, property_size)
    
        return cls(editor_properties, priority, timer, flags_player_hint, unknown_0xb2367a60, unknown_0x68d9122a, control_frame_interpolation)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'B\x08vP')  # 0x42087650
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.priority))

        data.write(b'\x87GU.')  # 0x8747552e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.timer))

        data.write(b'\x1b\xceW\xe1')  # 0x1bce57e1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.flags_player_hint))

        data.write(b'\xb26z`')  # 0xb2367a60
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb2367a60))

        data.write(b'h\xd9\x12*')  # 0x68d9122a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x68d9122a))

        data.write(b'\x95\xd0\xd47')  # 0x95d0d437
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.control_frame_interpolation.to_stream(data)
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
        json_data = typing.cast("PlayerHintJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            priority=json_data['priority'],
            timer=json_data['timer'],
            flags_player_hint=json_data['flags_player_hint'],
            unknown_0xb2367a60=json_data['unknown_0xb2367a60'],
            unknown_0x68d9122a=json_data['unknown_0x68d9122a'],
            control_frame_interpolation=InterpolationMethod.from_json(json_data['control_frame_interpolation']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'priority': self.priority,
            'timer': self.timer,
            'flags_player_hint': self.flags_player_hint,
            'unknown_0xb2367a60': self.unknown_0xb2367a60,
            'unknown_0x68d9122a': self.unknown_0x68d9122a,
            'control_frame_interpolation': self.control_frame_interpolation.to_json(),
        }


def _decode_priority(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flags_player_hint(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0xb2367a60(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x68d9122a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x42087650: ('priority', _decode_priority),
    0x8747552e: ('timer', _decode_timer),
    0x1bce57e1: ('flags_player_hint', _decode_flags_player_hint),
    0xb2367a60: ('unknown_0xb2367a60', _decode_unknown_0xb2367a60),
    0x68d9122a: ('unknown_0x68d9122a', _decode_unknown_0x68d9122a),
    0x95d0d437: ('control_frame_interpolation', InterpolationMethod.from_stream),
}
