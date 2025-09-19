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
from retro_data_structures.properties.echoes.core.Spline import Spline

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class CameraShakerDataJson(typing_extensions.TypedDict):
        flags_camera_shaker: int
        attenuation_distance: float
        horizontal_motion: json_util.JsonObject
        vertical_motion: json_util.JsonObject
        forward_motion: json_util.JsonObject
        duration: float
        audio_effect: int
    

@dataclasses.dataclass()
class CameraShakerData(BaseProperty):
    flags_camera_shaker: int = dataclasses.field(default=16, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc3e75c5f, original_name='FlagsCameraShaker'
        ),
    })  # Flagset
    attenuation_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4d283ac5, original_name='AttenuationDistance'
        ),
    })
    horizontal_motion: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xf122cd97, original_name='HorizontalMotion', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    vertical_motion: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x2927e544, original_name='VerticalMotion', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    forward_motion: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x7cfa4678, original_name='ForwardMotion', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    duration: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b51e23f, original_name='Duration'
        ),
    })
    audio_effect: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x388d2e46, original_name='AudioEffect'
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
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3e75c5f
        flags_camera_shaker = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d283ac5
        attenuation_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf122cd97
        horizontal_motion = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2927e544
        vertical_motion = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7cfa4678
        forward_motion = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b51e23f
        duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x388d2e46
        audio_effect = struct.unpack('>l', data.read(4))[0]
    
        return cls(flags_camera_shaker, attenuation_distance, horizontal_motion, vertical_motion, forward_motion, duration, audio_effect)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'\xc3\xe7\\_')  # 0xc3e75c5f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.flags_camera_shaker))

        data.write(b'M(:\xc5')  # 0x4d283ac5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attenuation_distance))

        data.write(b'\xf1"\xcd\x97')  # 0xf122cd97
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.horizontal_motion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b")'\xe5D")  # 0x2927e544
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.vertical_motion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'|\xfaFx')  # 0x7cfa4678
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.forward_motion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8bQ\xe2?')  # 0x8b51e23f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.duration))

        data.write(b'8\x8d.F')  # 0x388d2e46
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.audio_effect))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraShakerDataJson", data)
        return cls(
            flags_camera_shaker=json_data['flags_camera_shaker'],
            attenuation_distance=json_data['attenuation_distance'],
            horizontal_motion=Spline.from_json(json_data['horizontal_motion']),
            vertical_motion=Spline.from_json(json_data['vertical_motion']),
            forward_motion=Spline.from_json(json_data['forward_motion']),
            duration=json_data['duration'],
            audio_effect=json_data['audio_effect'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'flags_camera_shaker': self.flags_camera_shaker,
            'attenuation_distance': self.attenuation_distance,
            'horizontal_motion': self.horizontal_motion.to_json(),
            'vertical_motion': self.vertical_motion.to_json(),
            'forward_motion': self.forward_motion.to_json(),
            'duration': self.duration,
            'audio_effect': self.audio_effect,
        }

    def _dependencies_for_audio_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.audio_effect)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_audio_effect, "audio_effect", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for CameraShakerData.{field_name} ({field_type}): {e}"
                )


def _decode_flags_camera_shaker(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


def _decode_attenuation_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_audio_effect(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc3e75c5f: ('flags_camera_shaker', _decode_flags_camera_shaker),
    0x4d283ac5: ('attenuation_distance', _decode_attenuation_distance),
    0xf122cd97: ('horizontal_motion', Spline.from_stream),
    0x2927e544: ('vertical_motion', Spline.from_stream),
    0x7cfa4678: ('forward_motion', Spline.from_stream),
    0x8b51e23f: ('duration', _decode_duration),
    0x388d2e46: ('audio_effect', _decode_audio_effect),
}
