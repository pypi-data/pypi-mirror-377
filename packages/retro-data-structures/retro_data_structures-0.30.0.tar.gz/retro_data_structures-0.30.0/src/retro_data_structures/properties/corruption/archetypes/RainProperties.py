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
from retro_data_structures.properties.corruption.archetypes.LayerInfo import LayerInfo
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Color import Color
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class RainPropertiesJson(typing_extensions.TypedDict):
        color: json_util.JsonValue
        velocity: float
        min_length: float
        max_length: float
        near_width: float
        far_width: float
        unknown: float
        sheet_texture: int
        sheet_motion: json_util.JsonObject
        enable_sheet: bool
        rain_sound: int
        density_volume_spline: json_util.JsonObject
    

@dataclasses.dataclass()
class RainProperties(BaseProperty):
    color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.1490200012922287), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x37c7d09d, original_name='Color', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    velocity: float = dataclasses.field(default=-40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x02f01683, original_name='Velocity'
        ),
    })
    min_length: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc616093d, original_name='MinLength'
        ),
    })
    max_length: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7f30924c, original_name='MaxLength'
        ),
    })
    near_width: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaead5259, original_name='NearWidth'
        ),
    })
    far_width: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf4f4e856, original_name='FarWidth'
        ),
    })
    unknown: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x708dfe03, original_name='Unknown'
        ),
    })
    sheet_texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3399d65b, original_name='SheetTexture'
        ),
    })
    sheet_motion: LayerInfo = dataclasses.field(default_factory=LayerInfo, metadata={
        'reflection': FieldReflection[LayerInfo](
            LayerInfo, id=0x8476c57c, original_name='SheetMotion', from_json=LayerInfo.from_json, to_json=LayerInfo.to_json
        ),
    })
    enable_sheet: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5deb4d57, original_name='EnableSheet'
        ),
    })
    rain_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x35355a0b, original_name='RainSound'
        ),
    })
    density_volume_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x1a59b781, original_name='DensityVolumeSpline', from_json=Spline.from_json, to_json=Spline.to_json
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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37c7d09d
        color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x02f01683
        velocity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc616093d
        min_length = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f30924c
        max_length = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaead5259
        near_width = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf4f4e856
        far_width = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x708dfe03
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3399d65b
        sheet_texture = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8476c57c
        sheet_motion = LayerInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5deb4d57
        enable_sheet = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x35355a0b
        rain_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a59b781
        density_volume_spline = Spline.from_stream(data, property_size)
    
        return cls(color, velocity, min_length, max_length, near_width, far_width, unknown, sheet_texture, sheet_motion, enable_sheet, rain_sound, density_volume_spline)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'7\xc7\xd0\x9d')  # 0x37c7d09d
        data.write(b'\x00\x10')  # size
        self.color.to_stream(data)

        data.write(b'\x02\xf0\x16\x83')  # 0x2f01683
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.velocity))

        data.write(b'\xc6\x16\t=')  # 0xc616093d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_length))

        data.write(b'\x7f0\x92L')  # 0x7f30924c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_length))

        data.write(b'\xae\xadRY')  # 0xaead5259
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.near_width))

        data.write(b'\xf4\xf4\xe8V')  # 0xf4f4e856
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.far_width))

        data.write(b'p\x8d\xfe\x03')  # 0x708dfe03
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'3\x99\xd6[')  # 0x3399d65b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sheet_texture))

        data.write(b'\x84v\xc5|')  # 0x8476c57c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sheet_motion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b']\xebMW')  # 0x5deb4d57
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.enable_sheet))

        data.write(b'55Z\x0b')  # 0x35355a0b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.rain_sound))

        data.write(b'\x1aY\xb7\x81')  # 0x1a59b781
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.density_volume_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RainPropertiesJson", data)
        return cls(
            color=Color.from_json(json_data['color']),
            velocity=json_data['velocity'],
            min_length=json_data['min_length'],
            max_length=json_data['max_length'],
            near_width=json_data['near_width'],
            far_width=json_data['far_width'],
            unknown=json_data['unknown'],
            sheet_texture=json_data['sheet_texture'],
            sheet_motion=LayerInfo.from_json(json_data['sheet_motion']),
            enable_sheet=json_data['enable_sheet'],
            rain_sound=json_data['rain_sound'],
            density_volume_spline=Spline.from_json(json_data['density_volume_spline']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'color': self.color.to_json(),
            'velocity': self.velocity,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'near_width': self.near_width,
            'far_width': self.far_width,
            'unknown': self.unknown,
            'sheet_texture': self.sheet_texture,
            'sheet_motion': self.sheet_motion.to_json(),
            'enable_sheet': self.enable_sheet,
            'rain_sound': self.rain_sound,
            'density_volume_spline': self.density_volume_spline.to_json(),
        }


def _decode_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_velocity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_length(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_length(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_near_width(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_far_width(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sheet_texture(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_enable_sheet(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_rain_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x37c7d09d: ('color', _decode_color),
    0x2f01683: ('velocity', _decode_velocity),
    0xc616093d: ('min_length', _decode_min_length),
    0x7f30924c: ('max_length', _decode_max_length),
    0xaead5259: ('near_width', _decode_near_width),
    0xf4f4e856: ('far_width', _decode_far_width),
    0x708dfe03: ('unknown', _decode_unknown),
    0x3399d65b: ('sheet_texture', _decode_sheet_texture),
    0x8476c57c: ('sheet_motion', LayerInfo.from_stream),
    0x5deb4d57: ('enable_sheet', _decode_enable_sheet),
    0x35355a0b: ('rain_sound', _decode_rain_sound),
    0x1a59b781: ('density_volume_spline', Spline.from_stream),
}
