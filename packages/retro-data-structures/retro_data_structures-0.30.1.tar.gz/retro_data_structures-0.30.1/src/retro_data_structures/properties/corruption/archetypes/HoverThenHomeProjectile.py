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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class HoverThenHomeProjectileJson(typing_extensions.TypedDict):
        hover_time: float
        hover_speed: float
        hover_distance: float
        unknown_0x5a310c3b: float
        unknown_0x66284bf9: float
        initial_speed: float
        final_speed: float
        optional_homing_sound: int
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x30aa9af1, 0x845ef489, 0x452426bb, 0x5a310c3b, 0x66284bf9, 0xcb14d97c, 0x806d064f, 0x4b1c5766)


@dataclasses.dataclass()
class HoverThenHomeProjectile(BaseProperty):
    hover_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x30aa9af1, original_name='HoverTime'
        ),
    })
    hover_speed: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x845ef489, original_name='HoverSpeed'
        ),
    })
    hover_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x452426bb, original_name='HoverDistance'
        ),
    })
    unknown_0x5a310c3b: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5a310c3b, original_name='Unknown'
        ),
    })
    unknown_0x66284bf9: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x66284bf9, original_name='Unknown'
        ),
    })
    initial_speed: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcb14d97c, original_name='InitialSpeed'
        ),
    })
    final_speed: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x806d064f, original_name='FinalSpeed'
        ),
    })
    optional_homing_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4b1c5766, original_name='OptionalHomingSound'
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
        if property_count != 8:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHfLHQ')
    
        dec = _FAST_FORMAT.unpack(data.read(84))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
            dec[23],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'0\xaa\x9a\xf1')  # 0x30aa9af1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_time))

        data.write(b'\x84^\xf4\x89')  # 0x845ef489
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_speed))

        data.write(b'E$&\xbb')  # 0x452426bb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_distance))

        data.write(b'Z1\x0c;')  # 0x5a310c3b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5a310c3b))

        data.write(b'f(K\xf9')  # 0x66284bf9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x66284bf9))

        data.write(b'\xcb\x14\xd9|')  # 0xcb14d97c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.initial_speed))

        data.write(b'\x80m\x06O')  # 0x806d064f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.final_speed))

        data.write(b'K\x1cWf')  # 0x4b1c5766
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.optional_homing_sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("HoverThenHomeProjectileJson", data)
        return cls(
            hover_time=json_data['hover_time'],
            hover_speed=json_data['hover_speed'],
            hover_distance=json_data['hover_distance'],
            unknown_0x5a310c3b=json_data['unknown_0x5a310c3b'],
            unknown_0x66284bf9=json_data['unknown_0x66284bf9'],
            initial_speed=json_data['initial_speed'],
            final_speed=json_data['final_speed'],
            optional_homing_sound=json_data['optional_homing_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'hover_time': self.hover_time,
            'hover_speed': self.hover_speed,
            'hover_distance': self.hover_distance,
            'unknown_0x5a310c3b': self.unknown_0x5a310c3b,
            'unknown_0x66284bf9': self.unknown_0x66284bf9,
            'initial_speed': self.initial_speed,
            'final_speed': self.final_speed,
            'optional_homing_sound': self.optional_homing_sound,
        }


def _decode_hover_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hover_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hover_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5a310c3b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x66284bf9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_initial_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_final_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_optional_homing_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x30aa9af1: ('hover_time', _decode_hover_time),
    0x845ef489: ('hover_speed', _decode_hover_speed),
    0x452426bb: ('hover_distance', _decode_hover_distance),
    0x5a310c3b: ('unknown_0x5a310c3b', _decode_unknown_0x5a310c3b),
    0x66284bf9: ('unknown_0x66284bf9', _decode_unknown_0x66284bf9),
    0xcb14d97c: ('initial_speed', _decode_initial_speed),
    0x806d064f: ('final_speed', _decode_final_speed),
    0x4b1c5766: ('optional_homing_sound', _decode_optional_homing_sound),
}
