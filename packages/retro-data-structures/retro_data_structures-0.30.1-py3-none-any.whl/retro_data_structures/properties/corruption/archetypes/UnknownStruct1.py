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
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class UnknownStruct1Json(typing_extensions.TypedDict):
        character_animation_information: json_util.JsonObject
        light_color: json_util.JsonValue
        light_intensity: float
        light_attenuation: float
        hover_height: float
        min_rattle_time: float
        max_rattle_time: float
        unknown: float
        max_flight_speed: float
        in_flight_sound: int
        landed_sound: int
    

@dataclasses.dataclass()
class UnknownStruct1(BaseProperty):
    character_animation_information: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa244c9d8, original_name='CharacterAnimationInformation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    light_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xbd3efe7d, original_name='LightColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    light_intensity: float = dataclasses.field(default=500.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xede7b374, original_name='LightIntensity'
        ),
    })
    light_attenuation: float = dataclasses.field(default=0.019999999552965164, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd24b888f, original_name='LightAttenuation'
        ),
    })
    hover_height: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc75998aa, original_name='HoverHeight'
        ),
    })
    min_rattle_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x805bcac6, original_name='MinRattleTime'
        ),
    })
    max_rattle_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd3fdd222, original_name='MaxRattleTime'
        ),
    })
    unknown: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfa08f034, original_name='Unknown'
        ),
    })
    max_flight_speed: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe18486ed, original_name='MaxFlightSpeed'
        ),
    })
    in_flight_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1a092829, original_name='InFlightSound'
        ),
    })
    landed_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0105a02f, original_name='LandedSound'
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
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa244c9d8
        character_animation_information = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbd3efe7d
        light_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xede7b374
        light_intensity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd24b888f
        light_attenuation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc75998aa
        hover_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x805bcac6
        min_rattle_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd3fdd222
        max_rattle_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfa08f034
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe18486ed
        max_flight_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a092829
        in_flight_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0105a02f
        landed_sound = struct.unpack(">Q", data.read(8))[0]
    
        return cls(character_animation_information, light_color, light_intensity, light_attenuation, hover_height, min_rattle_time, max_rattle_time, unknown, max_flight_speed, in_flight_sound, landed_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'\xa2D\xc9\xd8')  # 0xa244c9d8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.character_animation_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbd>\xfe}')  # 0xbd3efe7d
        data.write(b'\x00\x10')  # size
        self.light_color.to_stream(data)

        data.write(b'\xed\xe7\xb3t')  # 0xede7b374
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.light_intensity))

        data.write(b'\xd2K\x88\x8f')  # 0xd24b888f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.light_attenuation))

        data.write(b'\xc7Y\x98\xaa')  # 0xc75998aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_height))

        data.write(b'\x80[\xca\xc6')  # 0x805bcac6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_rattle_time))

        data.write(b'\xd3\xfd\xd2"')  # 0xd3fdd222
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_rattle_time))

        data.write(b'\xfa\x08\xf04')  # 0xfa08f034
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\xe1\x84\x86\xed')  # 0xe18486ed
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_flight_speed))

        data.write(b'\x1a\t()')  # 0x1a092829
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.in_flight_sound))

        data.write(b'\x01\x05\xa0/')  # 0x105a02f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.landed_sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct1Json", data)
        return cls(
            character_animation_information=AnimationParameters.from_json(json_data['character_animation_information']),
            light_color=Color.from_json(json_data['light_color']),
            light_intensity=json_data['light_intensity'],
            light_attenuation=json_data['light_attenuation'],
            hover_height=json_data['hover_height'],
            min_rattle_time=json_data['min_rattle_time'],
            max_rattle_time=json_data['max_rattle_time'],
            unknown=json_data['unknown'],
            max_flight_speed=json_data['max_flight_speed'],
            in_flight_sound=json_data['in_flight_sound'],
            landed_sound=json_data['landed_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'character_animation_information': self.character_animation_information.to_json(),
            'light_color': self.light_color.to_json(),
            'light_intensity': self.light_intensity,
            'light_attenuation': self.light_attenuation,
            'hover_height': self.hover_height,
            'min_rattle_time': self.min_rattle_time,
            'max_rattle_time': self.max_rattle_time,
            'unknown': self.unknown,
            'max_flight_speed': self.max_flight_speed,
            'in_flight_sound': self.in_flight_sound,
            'landed_sound': self.landed_sound,
        }


def _decode_light_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_light_intensity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_light_attenuation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hover_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_rattle_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_rattle_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_flight_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_in_flight_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_landed_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xa244c9d8: ('character_animation_information', AnimationParameters.from_stream),
    0xbd3efe7d: ('light_color', _decode_light_color),
    0xede7b374: ('light_intensity', _decode_light_intensity),
    0xd24b888f: ('light_attenuation', _decode_light_attenuation),
    0xc75998aa: ('hover_height', _decode_hover_height),
    0x805bcac6: ('min_rattle_time', _decode_min_rattle_time),
    0xd3fdd222: ('max_rattle_time', _decode_max_rattle_time),
    0xfa08f034: ('unknown', _decode_unknown),
    0xe18486ed: ('max_flight_speed', _decode_max_flight_speed),
    0x1a092829: ('in_flight_sound', _decode_in_flight_sound),
    0x105a02f: ('landed_sound', _decode_landed_sound),
}
