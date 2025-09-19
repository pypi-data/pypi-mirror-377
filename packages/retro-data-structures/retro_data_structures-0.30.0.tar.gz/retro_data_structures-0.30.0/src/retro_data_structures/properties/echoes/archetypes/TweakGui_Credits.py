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
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakGui_CreditsJson(typing_extensions.TypedDict):
        unknown_0x81fc78c2: str
        unknown_0x2bcd300d: str
        alternate_font: str
        font_color: json_util.JsonValue
        font_outline_color: json_util.JsonValue
        total_time: float
        text_fade_time: float
        movie_fade_time: float
    

@dataclasses.dataclass()
class TweakGui_Credits(BaseProperty):
    unknown_0x81fc78c2: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x81fc78c2, original_name='Unknown'
        ),
    })
    unknown_0x2bcd300d: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x2bcd300d, original_name='Unknown'
        ),
    })
    alternate_font: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xcef90c00, original_name='AlternateFont'
        ),
    })
    font_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x1a96ec67, original_name='FontColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    font_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x844ab6b0, original_name='FontOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    total_time: float = dataclasses.field(default=191.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x19686bf6, original_name='TotalTime'
        ),
    })
    text_fade_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x52985ad1, original_name='TextFadeTime'
        ),
    })
    movie_fade_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf0f977e6, original_name='MovieFadeTime'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81fc78c2
        unknown_0x81fc78c2 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2bcd300d
        unknown_0x2bcd300d = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcef90c00
        alternate_font = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a96ec67
        font_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x844ab6b0
        font_outline_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19686bf6
        total_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x52985ad1
        text_fade_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf0f977e6
        movie_fade_time = struct.unpack('>f', data.read(4))[0]
    
        return cls(unknown_0x81fc78c2, unknown_0x2bcd300d, alternate_font, font_color, font_outline_color, total_time, text_fade_time, movie_fade_time)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'\x81\xfcx\xc2')  # 0x81fc78c2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x81fc78c2.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'+\xcd0\r')  # 0x2bcd300d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x2bcd300d.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xce\xf9\x0c\x00')  # 0xcef90c00
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.alternate_font.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1a\x96\xecg')  # 0x1a96ec67
        data.write(b'\x00\x10')  # size
        self.font_color.to_stream(data)

        data.write(b'\x84J\xb6\xb0')  # 0x844ab6b0
        data.write(b'\x00\x10')  # size
        self.font_outline_color.to_stream(data)

        data.write(b'\x19hk\xf6')  # 0x19686bf6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.total_time))

        data.write(b'R\x98Z\xd1')  # 0x52985ad1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.text_fade_time))

        data.write(b'\xf0\xf9w\xe6')  # 0xf0f977e6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movie_fade_time))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakGui_CreditsJson", data)
        return cls(
            unknown_0x81fc78c2=json_data['unknown_0x81fc78c2'],
            unknown_0x2bcd300d=json_data['unknown_0x2bcd300d'],
            alternate_font=json_data['alternate_font'],
            font_color=Color.from_json(json_data['font_color']),
            font_outline_color=Color.from_json(json_data['font_outline_color']),
            total_time=json_data['total_time'],
            text_fade_time=json_data['text_fade_time'],
            movie_fade_time=json_data['movie_fade_time'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x81fc78c2': self.unknown_0x81fc78c2,
            'unknown_0x2bcd300d': self.unknown_0x2bcd300d,
            'alternate_font': self.alternate_font,
            'font_color': self.font_color.to_json(),
            'font_outline_color': self.font_outline_color.to_json(),
            'total_time': self.total_time,
            'text_fade_time': self.text_fade_time,
            'movie_fade_time': self.movie_fade_time,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_unknown_0x81fc78c2(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x2bcd300d(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_alternate_font(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_font_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_font_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_total_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_text_fade_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movie_fade_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x81fc78c2: ('unknown_0x81fc78c2', _decode_unknown_0x81fc78c2),
    0x2bcd300d: ('unknown_0x2bcd300d', _decode_unknown_0x2bcd300d),
    0xcef90c00: ('alternate_font', _decode_alternate_font),
    0x1a96ec67: ('font_color', _decode_font_color),
    0x844ab6b0: ('font_outline_color', _decode_font_outline_color),
    0x19686bf6: ('total_time', _decode_total_time),
    0x52985ad1: ('text_fade_time', _decode_text_fade_time),
    0xf0f977e6: ('movie_fade_time', _decode_movie_fade_time),
}
