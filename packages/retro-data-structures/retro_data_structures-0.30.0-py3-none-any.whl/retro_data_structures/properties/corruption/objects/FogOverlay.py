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
from retro_data_structures.properties.corruption.core.Color import Color
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class FogOverlayJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        full_alpha: float
        fade_down_time: float
        fade_up_time: float
        start_faded_out: bool
        color: json_util.JsonValue
        ambient_radius_x: float
        ambient_radius_y: float
        ambient_speed: float
        ambient_speed_target: float
        unknown_0x6a111b96: float
        unknown_0xff226ea3: float
        unknown_0x2190ab0a: json_util.JsonValue
        unknown_0x9f19f0af: float
        unknown_0x90c10fe7: float
        unknown_0xd8daff1d: float
    

@dataclasses.dataclass()
class FogOverlay(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    full_alpha: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x547b28d5, original_name='FullAlpha'
        ),
    })
    fade_down_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf977cb35, original_name='FadeDownTime'
        ),
    })
    fade_up_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d21d348, original_name='FadeUpTime'
        ),
    })
    start_faded_out: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xeb250a0b, original_name='StartFadedOut'
        ),
    })
    color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x37c7d09d, original_name='Color', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    ambient_radius_x: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1b9046d6, original_name='AmbientRadiusX'
        ),
    })
    ambient_radius_y: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd0cc9573, original_name='AmbientRadiusY'
        ),
    })
    ambient_speed: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf76bcbdd, original_name='AmbientSpeed'
        ),
    })
    ambient_speed_target: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2c4c6785, original_name='AmbientSpeedTarget'
        ),
    })
    unknown_0x6a111b96: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6a111b96, original_name='Unknown'
        ),
    })
    unknown_0xff226ea3: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xff226ea3, original_name='Unknown'
        ),
    })
    unknown_0x2190ab0a: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x2190ab0a, original_name='Unknown', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_0x9f19f0af: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9f19f0af, original_name='Unknown'
        ),
    })
    unknown_0x90c10fe7: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x90c10fe7, original_name='Unknown'
        ),
    })
    unknown_0xd8daff1d: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd8daff1d, original_name='Unknown'
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
        return 'FOGO'

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
        if property_count != 16:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x547b28d5
        full_alpha = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf977cb35
        fade_down_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d21d348
        fade_up_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeb250a0b
        start_faded_out = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37c7d09d
        color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b9046d6
        ambient_radius_x = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0cc9573
        ambient_radius_y = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf76bcbdd
        ambient_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c4c6785
        ambient_speed_target = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6a111b96
        unknown_0x6a111b96 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xff226ea3
        unknown_0xff226ea3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2190ab0a
        unknown_0x2190ab0a = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f19f0af
        unknown_0x9f19f0af = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90c10fe7
        unknown_0x90c10fe7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd8daff1d
        unknown_0xd8daff1d = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, full_alpha, fade_down_time, fade_up_time, start_faded_out, color, ambient_radius_x, ambient_radius_y, ambient_speed, ambient_speed_target, unknown_0x6a111b96, unknown_0xff226ea3, unknown_0x2190ab0a, unknown_0x9f19f0af, unknown_0x90c10fe7, unknown_0xd8daff1d)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x10')  # 16 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'T{(\xd5')  # 0x547b28d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.full_alpha))

        data.write(b'\xf9w\xcb5')  # 0xf977cb35
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_down_time))

        data.write(b'\r!\xd3H')  # 0xd21d348
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_up_time))

        data.write(b'\xeb%\n\x0b')  # 0xeb250a0b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.start_faded_out))

        data.write(b'7\xc7\xd0\x9d')  # 0x37c7d09d
        data.write(b'\x00\x10')  # size
        self.color.to_stream(data)

        data.write(b'\x1b\x90F\xd6')  # 0x1b9046d6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ambient_radius_x))

        data.write(b'\xd0\xcc\x95s')  # 0xd0cc9573
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ambient_radius_y))

        data.write(b'\xf7k\xcb\xdd')  # 0xf76bcbdd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ambient_speed))

        data.write(b',Lg\x85')  # 0x2c4c6785
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ambient_speed_target))

        data.write(b'j\x11\x1b\x96')  # 0x6a111b96
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6a111b96))

        data.write(b'\xff"n\xa3')  # 0xff226ea3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xff226ea3))

        data.write(b'!\x90\xab\n')  # 0x2190ab0a
        data.write(b'\x00\x0c')  # size
        self.unknown_0x2190ab0a.to_stream(data)

        data.write(b'\x9f\x19\xf0\xaf')  # 0x9f19f0af
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9f19f0af))

        data.write(b'\x90\xc1\x0f\xe7')  # 0x90c10fe7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x90c10fe7))

        data.write(b'\xd8\xda\xff\x1d')  # 0xd8daff1d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd8daff1d))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("FogOverlayJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            full_alpha=json_data['full_alpha'],
            fade_down_time=json_data['fade_down_time'],
            fade_up_time=json_data['fade_up_time'],
            start_faded_out=json_data['start_faded_out'],
            color=Color.from_json(json_data['color']),
            ambient_radius_x=json_data['ambient_radius_x'],
            ambient_radius_y=json_data['ambient_radius_y'],
            ambient_speed=json_data['ambient_speed'],
            ambient_speed_target=json_data['ambient_speed_target'],
            unknown_0x6a111b96=json_data['unknown_0x6a111b96'],
            unknown_0xff226ea3=json_data['unknown_0xff226ea3'],
            unknown_0x2190ab0a=Vector.from_json(json_data['unknown_0x2190ab0a']),
            unknown_0x9f19f0af=json_data['unknown_0x9f19f0af'],
            unknown_0x90c10fe7=json_data['unknown_0x90c10fe7'],
            unknown_0xd8daff1d=json_data['unknown_0xd8daff1d'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'full_alpha': self.full_alpha,
            'fade_down_time': self.fade_down_time,
            'fade_up_time': self.fade_up_time,
            'start_faded_out': self.start_faded_out,
            'color': self.color.to_json(),
            'ambient_radius_x': self.ambient_radius_x,
            'ambient_radius_y': self.ambient_radius_y,
            'ambient_speed': self.ambient_speed,
            'ambient_speed_target': self.ambient_speed_target,
            'unknown_0x6a111b96': self.unknown_0x6a111b96,
            'unknown_0xff226ea3': self.unknown_0xff226ea3,
            'unknown_0x2190ab0a': self.unknown_0x2190ab0a.to_json(),
            'unknown_0x9f19f0af': self.unknown_0x9f19f0af,
            'unknown_0x90c10fe7': self.unknown_0x90c10fe7,
            'unknown_0xd8daff1d': self.unknown_0xd8daff1d,
        }


def _decode_full_alpha(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_down_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_up_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_start_faded_out(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_ambient_radius_x(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ambient_radius_y(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ambient_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ambient_speed_target(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6a111b96(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xff226ea3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2190ab0a(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0x9f19f0af(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x90c10fe7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd8daff1d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x547b28d5: ('full_alpha', _decode_full_alpha),
    0xf977cb35: ('fade_down_time', _decode_fade_down_time),
    0xd21d348: ('fade_up_time', _decode_fade_up_time),
    0xeb250a0b: ('start_faded_out', _decode_start_faded_out),
    0x37c7d09d: ('color', _decode_color),
    0x1b9046d6: ('ambient_radius_x', _decode_ambient_radius_x),
    0xd0cc9573: ('ambient_radius_y', _decode_ambient_radius_y),
    0xf76bcbdd: ('ambient_speed', _decode_ambient_speed),
    0x2c4c6785: ('ambient_speed_target', _decode_ambient_speed_target),
    0x6a111b96: ('unknown_0x6a111b96', _decode_unknown_0x6a111b96),
    0xff226ea3: ('unknown_0xff226ea3', _decode_unknown_0xff226ea3),
    0x2190ab0a: ('unknown_0x2190ab0a', _decode_unknown_0x2190ab0a),
    0x9f19f0af: ('unknown_0x9f19f0af', _decode_unknown_0x9f19f0af),
    0x90c10fe7: ('unknown_0x90c10fe7', _decode_unknown_0x90c10fe7),
    0xd8daff1d: ('unknown_0xd8daff1d', _decode_unknown_0xd8daff1d),
}
