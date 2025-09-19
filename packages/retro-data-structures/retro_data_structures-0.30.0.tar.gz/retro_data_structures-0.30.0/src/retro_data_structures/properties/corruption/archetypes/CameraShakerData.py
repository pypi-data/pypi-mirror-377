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
from retro_data_structures.properties.corruption.archetypes.CameraShakerEnvelope import CameraShakerEnvelope
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class CameraShakerDataJson(typing_extensions.TypedDict):
        flags_camera_shaker: int
        attenuation_distance: float
        duration: float
        audio_effect: int
        horizontal_motion: json_util.JsonObject
        vertical_motion: json_util.JsonObject
        forward_motion: json_util.JsonObject
    

@dataclasses.dataclass()
class CameraShakerData(BaseProperty):
    flags_camera_shaker: int = dataclasses.field(default=48, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc3e75c5f, original_name='FlagsCameraShaker'
        ),
    })  # Flagset
    attenuation_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4d283ac5, original_name='AttenuationDistance'
        ),
    })
    duration: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b51e23f, original_name='Duration'
        ),
    })
    audio_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc2acb79e, original_name='AudioEffect'
        ),
    })
    horizontal_motion: CameraShakerEnvelope = dataclasses.field(default_factory=CameraShakerEnvelope, metadata={
        'reflection': FieldReflection[CameraShakerEnvelope](
            CameraShakerEnvelope, id=0xd9eb71e0, original_name='HorizontalMotion', from_json=CameraShakerEnvelope.from_json, to_json=CameraShakerEnvelope.to_json
        ),
    })
    vertical_motion: CameraShakerEnvelope = dataclasses.field(default_factory=CameraShakerEnvelope, metadata={
        'reflection': FieldReflection[CameraShakerEnvelope](
            CameraShakerEnvelope, id=0xc5b09632, original_name='VerticalMotion', from_json=CameraShakerEnvelope.from_json, to_json=CameraShakerEnvelope.to_json
        ),
    })
    forward_motion: CameraShakerEnvelope = dataclasses.field(default_factory=CameraShakerEnvelope, metadata={
        'reflection': FieldReflection[CameraShakerEnvelope](
            CameraShakerEnvelope, id=0x21b704e3, original_name='ForwardMotion', from_json=CameraShakerEnvelope.from_json, to_json=CameraShakerEnvelope.to_json
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
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3e75c5f
        flags_camera_shaker = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d283ac5
        attenuation_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b51e23f
        duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc2acb79e
        audio_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd9eb71e0
        horizontal_motion = CameraShakerEnvelope.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc5b09632
        vertical_motion = CameraShakerEnvelope.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x21b704e3
        forward_motion = CameraShakerEnvelope.from_stream(data, property_size)
    
        return cls(flags_camera_shaker, attenuation_distance, duration, audio_effect, horizontal_motion, vertical_motion, forward_motion)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'\xc3\xe7\\_')  # 0xc3e75c5f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.flags_camera_shaker))

        data.write(b'M(:\xc5')  # 0x4d283ac5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attenuation_distance))

        data.write(b'\x8bQ\xe2?')  # 0x8b51e23f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.duration))

        data.write(b'\xc2\xac\xb7\x9e')  # 0xc2acb79e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.audio_effect))

        data.write(b'\xd9\xebq\xe0')  # 0xd9eb71e0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.horizontal_motion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc5\xb0\x962')  # 0xc5b09632
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.vertical_motion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'!\xb7\x04\xe3')  # 0x21b704e3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.forward_motion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraShakerDataJson", data)
        return cls(
            flags_camera_shaker=json_data['flags_camera_shaker'],
            attenuation_distance=json_data['attenuation_distance'],
            duration=json_data['duration'],
            audio_effect=json_data['audio_effect'],
            horizontal_motion=CameraShakerEnvelope.from_json(json_data['horizontal_motion']),
            vertical_motion=CameraShakerEnvelope.from_json(json_data['vertical_motion']),
            forward_motion=CameraShakerEnvelope.from_json(json_data['forward_motion']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'flags_camera_shaker': self.flags_camera_shaker,
            'attenuation_distance': self.attenuation_distance,
            'duration': self.duration,
            'audio_effect': self.audio_effect,
            'horizontal_motion': self.horizontal_motion.to_json(),
            'vertical_motion': self.vertical_motion.to_json(),
            'forward_motion': self.forward_motion.to_json(),
        }


def _decode_flags_camera_shaker(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


def _decode_attenuation_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_audio_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc3e75c5f: ('flags_camera_shaker', _decode_flags_camera_shaker),
    0x4d283ac5: ('attenuation_distance', _decode_attenuation_distance),
    0x8b51e23f: ('duration', _decode_duration),
    0xc2acb79e: ('audio_effect', _decode_audio_effect),
    0xd9eb71e0: ('horizontal_motion', CameraShakerEnvelope.from_stream),
    0xc5b09632: ('vertical_motion', CameraShakerEnvelope.from_stream),
    0x21b704e3: ('forward_motion', CameraShakerEnvelope.from_stream),
}
