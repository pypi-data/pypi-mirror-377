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

    class TweakGui_CompletionJson(typing_extensions.TypedDict):
        unknown_0x81fc78c2: str
        main_font: str
        secondary_font: str
        main_font_color: json_util.JsonValue
        main_font_outline_color: json_util.JsonValue
        stats_font_color: json_util.JsonValue
        stats_font_outline_color: json_util.JsonValue
        unlock_font_color: json_util.JsonValue
        unlock_font_outline_color: json_util.JsonValue
        unknown_0xb6fe7398: float
        unknown_0x6af2871b: float
        text_start_delay: float
    

@dataclasses.dataclass()
class TweakGui_Completion(BaseProperty):
    unknown_0x81fc78c2: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x81fc78c2, original_name='Unknown'
        ),
    })
    main_font: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x5e7f85c7, original_name='MainFont'
        ),
    })
    secondary_font: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x0a0d69d0, original_name='SecondaryFont'
        ),
    })
    main_font_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x5a24a7e4, original_name='MainFontColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    main_font_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xa938bf39, original_name='MainFontOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    stats_font_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xc6cc9d0c, original_name='StatsFontColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    stats_font_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xd3a4a180, original_name='StatsFontOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unlock_font_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x07ab5642, original_name='UnlockFontColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unlock_font_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x595c63ed, original_name='UnlockFontOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xb6fe7398: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb6fe7398, original_name='Unknown'
        ),
    })
    unknown_0x6af2871b: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6af2871b, original_name='Unknown'
        ),
    })
    text_start_delay: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2955d055, original_name='TextStartDelay'
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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81fc78c2
        unknown_0x81fc78c2 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e7f85c7
        main_font = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a0d69d0
        secondary_font = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5a24a7e4
        main_font_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa938bf39
        main_font_outline_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6cc9d0c
        stats_font_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd3a4a180
        stats_font_outline_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x07ab5642
        unlock_font_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x595c63ed
        unlock_font_outline_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb6fe7398
        unknown_0xb6fe7398 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6af2871b
        unknown_0x6af2871b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2955d055
        text_start_delay = struct.unpack('>f', data.read(4))[0]
    
        return cls(unknown_0x81fc78c2, main_font, secondary_font, main_font_color, main_font_outline_color, stats_font_color, stats_font_outline_color, unlock_font_color, unlock_font_outline_color, unknown_0xb6fe7398, unknown_0x6af2871b, text_start_delay)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'\x81\xfcx\xc2')  # 0x81fc78c2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x81fc78c2.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'^\x7f\x85\xc7')  # 0x5e7f85c7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.main_font.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\n\ri\xd0')  # 0xa0d69d0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.secondary_font.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'Z$\xa7\xe4')  # 0x5a24a7e4
        data.write(b'\x00\x10')  # size
        self.main_font_color.to_stream(data)

        data.write(b'\xa98\xbf9')  # 0xa938bf39
        data.write(b'\x00\x10')  # size
        self.main_font_outline_color.to_stream(data)

        data.write(b'\xc6\xcc\x9d\x0c')  # 0xc6cc9d0c
        data.write(b'\x00\x10')  # size
        self.stats_font_color.to_stream(data)

        data.write(b'\xd3\xa4\xa1\x80')  # 0xd3a4a180
        data.write(b'\x00\x10')  # size
        self.stats_font_outline_color.to_stream(data)

        data.write(b'\x07\xabVB')  # 0x7ab5642
        data.write(b'\x00\x10')  # size
        self.unlock_font_color.to_stream(data)

        data.write(b'Y\\c\xed')  # 0x595c63ed
        data.write(b'\x00\x10')  # size
        self.unlock_font_outline_color.to_stream(data)

        data.write(b'\xb6\xfes\x98')  # 0xb6fe7398
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb6fe7398))

        data.write(b'j\xf2\x87\x1b')  # 0x6af2871b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6af2871b))

        data.write(b')U\xd0U')  # 0x2955d055
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.text_start_delay))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakGui_CompletionJson", data)
        return cls(
            unknown_0x81fc78c2=json_data['unknown_0x81fc78c2'],
            main_font=json_data['main_font'],
            secondary_font=json_data['secondary_font'],
            main_font_color=Color.from_json(json_data['main_font_color']),
            main_font_outline_color=Color.from_json(json_data['main_font_outline_color']),
            stats_font_color=Color.from_json(json_data['stats_font_color']),
            stats_font_outline_color=Color.from_json(json_data['stats_font_outline_color']),
            unlock_font_color=Color.from_json(json_data['unlock_font_color']),
            unlock_font_outline_color=Color.from_json(json_data['unlock_font_outline_color']),
            unknown_0xb6fe7398=json_data['unknown_0xb6fe7398'],
            unknown_0x6af2871b=json_data['unknown_0x6af2871b'],
            text_start_delay=json_data['text_start_delay'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x81fc78c2': self.unknown_0x81fc78c2,
            'main_font': self.main_font,
            'secondary_font': self.secondary_font,
            'main_font_color': self.main_font_color.to_json(),
            'main_font_outline_color': self.main_font_outline_color.to_json(),
            'stats_font_color': self.stats_font_color.to_json(),
            'stats_font_outline_color': self.stats_font_outline_color.to_json(),
            'unlock_font_color': self.unlock_font_color.to_json(),
            'unlock_font_outline_color': self.unlock_font_outline_color.to_json(),
            'unknown_0xb6fe7398': self.unknown_0xb6fe7398,
            'unknown_0x6af2871b': self.unknown_0x6af2871b,
            'text_start_delay': self.text_start_delay,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_unknown_0x81fc78c2(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_main_font(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_secondary_font(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_main_font_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_main_font_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_stats_font_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_stats_font_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unlock_font_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unlock_font_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xb6fe7398(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6af2871b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_text_start_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x81fc78c2: ('unknown_0x81fc78c2', _decode_unknown_0x81fc78c2),
    0x5e7f85c7: ('main_font', _decode_main_font),
    0xa0d69d0: ('secondary_font', _decode_secondary_font),
    0x5a24a7e4: ('main_font_color', _decode_main_font_color),
    0xa938bf39: ('main_font_outline_color', _decode_main_font_outline_color),
    0xc6cc9d0c: ('stats_font_color', _decode_stats_font_color),
    0xd3a4a180: ('stats_font_outline_color', _decode_stats_font_outline_color),
    0x7ab5642: ('unlock_font_color', _decode_unlock_font_color),
    0x595c63ed: ('unlock_font_outline_color', _decode_unlock_font_outline_color),
    0xb6fe7398: ('unknown_0xb6fe7398', _decode_unknown_0xb6fe7398),
    0x6af2871b: ('unknown_0x6af2871b', _decode_unknown_0x6af2871b),
    0x2955d055: ('text_start_delay', _decode_text_start_delay),
}
