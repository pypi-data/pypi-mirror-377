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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class LayerInfoJson(typing_extensions.TypedDict):
        motion_type: int
        unknown: float
        rotation: float
        amplitude: float
        texture_scale: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xe94f7e87, 0x3c5b0c98, 0x912954e6, 0x89e3d294, 0x80c7499)


@dataclasses.dataclass()
class LayerInfo(BaseProperty):
    motion_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe94f7e87, original_name='MotionType'
        ),
    })
    unknown: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3c5b0c98, original_name='Unknown'
        ),
    })
    rotation: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x912954e6, original_name='Rotation'
        ),
    })
    amplitude: float = dataclasses.field(default=-0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x89e3d294, original_name='Amplitude'
        ),
    })
    texture_scale: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x080c7499, original_name='TextureScale'
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
        if property_count != 5:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHlLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(50))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'\xe9O~\x87')  # 0xe94f7e87
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.motion_type))

        data.write(b'<[\x0c\x98')  # 0x3c5b0c98
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\x91)T\xe6')  # 0x912954e6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.rotation))

        data.write(b'\x89\xe3\xd2\x94')  # 0x89e3d294
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.amplitude))

        data.write(b'\x08\x0ct\x99')  # 0x80c7499
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.texture_scale))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("LayerInfoJson", data)
        return cls(
            motion_type=json_data['motion_type'],
            unknown=json_data['unknown'],
            rotation=json_data['rotation'],
            amplitude=json_data['amplitude'],
            texture_scale=json_data['texture_scale'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'motion_type': self.motion_type,
            'unknown': self.unknown,
            'rotation': self.rotation,
            'amplitude': self.amplitude,
            'texture_scale': self.texture_scale,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_motion_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_rotation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_amplitude(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_texture_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xe94f7e87: ('motion_type', _decode_motion_type),
    0x3c5b0c98: ('unknown', _decode_unknown),
    0x912954e6: ('rotation', _decode_rotation),
    0x89e3d294: ('amplitude', _decode_amplitude),
    0x80c7499: ('texture_scale', _decode_texture_scale),
}
