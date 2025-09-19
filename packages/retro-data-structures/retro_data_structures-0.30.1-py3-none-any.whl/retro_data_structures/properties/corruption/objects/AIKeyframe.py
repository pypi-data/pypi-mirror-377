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

if typing.TYPE_CHECKING:
    class AIKeyframeJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        animation_index: int
        unknown_0xc215a24f: int
        loop: bool
        loop_duration: float
        unknown_0x6d62ef74: int
        playback_rate: float
    

@dataclasses.dataclass()
class AIKeyframe(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    animation_index: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1ccd0586, original_name='Animation Index'
        ),
    })
    unknown_0xc215a24f: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc215a24f, original_name='Unknown'
        ),
    })
    loop: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xeda47ff6, original_name='Loop'
        ),
    })
    loop_duration: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcee68723, original_name='LoopDuration'
        ),
    })
    unknown_0x6d62ef74: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6d62ef74, original_name='Unknown'
        ),
    })
    playback_rate: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6f8d34ca, original_name='PlaybackRate'
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
        return 'AIKF'

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
        assert property_id == 0x1ccd0586
        animation_index = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc215a24f
        unknown_0xc215a24f = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeda47ff6
        loop = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcee68723
        loop_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d62ef74
        unknown_0x6d62ef74 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6f8d34ca
        playback_rate = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, animation_index, unknown_0xc215a24f, loop, loop_duration, unknown_0x6d62ef74, playback_rate)

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

        data.write(b'\x1c\xcd\x05\x86')  # 0x1ccd0586
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.animation_index))

        data.write(b'\xc2\x15\xa2O')  # 0xc215a24f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc215a24f))

        data.write(b'\xed\xa4\x7f\xf6')  # 0xeda47ff6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.loop))

        data.write(b'\xce\xe6\x87#')  # 0xcee68723
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.loop_duration))

        data.write(b'mb\xeft')  # 0x6d62ef74
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x6d62ef74))

        data.write(b'o\x8d4\xca')  # 0x6f8d34ca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.playback_rate))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AIKeyframeJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            animation_index=json_data['animation_index'],
            unknown_0xc215a24f=json_data['unknown_0xc215a24f'],
            loop=json_data['loop'],
            loop_duration=json_data['loop_duration'],
            unknown_0x6d62ef74=json_data['unknown_0x6d62ef74'],
            playback_rate=json_data['playback_rate'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'animation_index': self.animation_index,
            'unknown_0xc215a24f': self.unknown_0xc215a24f,
            'loop': self.loop,
            'loop_duration': self.loop_duration,
            'unknown_0x6d62ef74': self.unknown_0x6d62ef74,
            'playback_rate': self.playback_rate,
        }


def _decode_animation_index(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xc215a24f(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_loop(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_loop_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6d62ef74(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_playback_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x1ccd0586: ('animation_index', _decode_animation_index),
    0xc215a24f: ('unknown_0xc215a24f', _decode_unknown_0xc215a24f),
    0xeda47ff6: ('loop', _decode_loop),
    0xcee68723: ('loop_duration', _decode_loop_duration),
    0x6d62ef74: ('unknown_0x6d62ef74', _decode_unknown_0x6d62ef74),
    0x6f8d34ca: ('playback_rate', _decode_playback_rate),
}
