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
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class StreamedMovieJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        movie_file: str
        loop: bool
        video_filter_enabled: bool
        unknown: int
        volume: int
        volume_type: int
        cache_length: float
        fade_out_time: float
    

@dataclasses.dataclass()
class StreamedMovie(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    movie_file: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x582b84a8, original_name='MovieFile'
        ),
    })
    loop: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xeda47ff6, original_name='Loop'
        ),
    })
    video_filter_enabled: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x36963bcc, original_name='VideoFilterEnabled'
        ),
    })
    unknown: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa78ac0c0, original_name='Unknown'
        ),
    })
    volume: int = dataclasses.field(default=127, metadata={
        'reflection': FieldReflection[int](
            int, id=0x80c66c37, original_name='Volume'
        ),
    })
    volume_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe1ff4f04, original_name='VolumeType'
        ),
    })
    cache_length: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad9eb77f, original_name='CacheLength'
        ),
    })
    fade_out_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7c269ebc, original_name='FadeOutTime'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'MOVI'

    @classmethod
    def modules(cls) -> list[str]:
        return ['ScriptStreamedMovie.rel']

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
        if property_count != 9:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x582b84a8
        movie_file = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeda47ff6
        loop = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x36963bcc
        video_filter_enabled = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa78ac0c0
        unknown = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80c66c37
        volume = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe1ff4f04
        volume_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad9eb77f
        cache_length = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7c269ebc
        fade_out_time = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, movie_file, loop, video_filter_enabled, unknown, volume, volume_type, cache_length, fade_out_time)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\t')  # 9 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'X+\x84\xa8')  # 0x582b84a8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.movie_file.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed\xa4\x7f\xf6')  # 0xeda47ff6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.loop))

        data.write(b'6\x96;\xcc')  # 0x36963bcc
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.video_filter_enabled))

        data.write(b'\xa7\x8a\xc0\xc0')  # 0xa78ac0c0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown))

        data.write(b'\x80\xc6l7')  # 0x80c66c37
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.volume))

        data.write(b'\xe1\xffO\x04')  # 0xe1ff4f04
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.volume_type))

        data.write(b'\xad\x9e\xb7\x7f')  # 0xad9eb77f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cache_length))

        data.write(b'|&\x9e\xbc')  # 0x7c269ebc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_out_time))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("StreamedMovieJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            movie_file=json_data['movie_file'],
            loop=json_data['loop'],
            video_filter_enabled=json_data['video_filter_enabled'],
            unknown=json_data['unknown'],
            volume=json_data['volume'],
            volume_type=json_data['volume_type'],
            cache_length=json_data['cache_length'],
            fade_out_time=json_data['fade_out_time'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'movie_file': self.movie_file,
            'loop': self.loop,
            'video_filter_enabled': self.video_filter_enabled,
            'unknown': self.unknown,
            'volume': self.volume,
            'volume_type': self.volume_type,
            'cache_length': self.cache_length,
            'fade_out_time': self.fade_out_time,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for StreamedMovie.{field_name} ({field_type}): {e}"
                )


def _decode_movie_file(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_loop(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_video_filter_enabled(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_volume_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_cache_length(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_out_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x582b84a8: ('movie_file', _decode_movie_file),
    0xeda47ff6: ('loop', _decode_loop),
    0x36963bcc: ('video_filter_enabled', _decode_video_filter_enabled),
    0xa78ac0c0: ('unknown', _decode_unknown),
    0x80c66c37: ('volume', _decode_volume),
    0xe1ff4f04: ('volume_type', _decode_volume_type),
    0xad9eb77f: ('cache_length', _decode_cache_length),
    0x7c269ebc: ('fade_out_time', _decode_fade_out_time),
}
