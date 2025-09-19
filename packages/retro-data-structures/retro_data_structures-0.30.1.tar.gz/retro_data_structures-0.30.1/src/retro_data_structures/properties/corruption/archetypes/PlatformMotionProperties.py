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
from retro_data_structures.properties.corruption.archetypes.SplineType import SplineType
from retro_data_structures.properties.corruption.core.Spline import Spline
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class PlatformMotionPropertiesJson(typing_extensions.TypedDict):
        motion_spline_type: json_util.JsonObject
        motion_control_spline: json_util.JsonObject
        motion_spline_duration: float
        initial_time: float
        unknown: int
        roll_control_spline: json_util.JsonObject
        yaw_control_spline: json_util.JsonObject
        pitch_control_spline: json_util.JsonObject
        target_object_offset: json_util.JsonValue
    

@dataclasses.dataclass()
class PlatformMotionProperties(BaseProperty):
    motion_spline_type: SplineType = dataclasses.field(default_factory=SplineType, metadata={
        'reflection': FieldReflection[SplineType](
            SplineType, id=0x493d6a2d, original_name='MotionSplineType', from_json=SplineType.from_json, to_json=SplineType.to_json
        ),
    })
    motion_control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x27e5f874, original_name='MotionControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    motion_spline_duration: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfd1e2f56, original_name='MotionSplineDuration'
        ),
    })
    initial_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa5753d52, original_name='InitialTime'
        ),
    })
    unknown: int = dataclasses.field(default=288, metadata={
        'reflection': FieldReflection[int](
            int, id=0xae80628f, original_name='Unknown'
        ),
    })  # Flagset
    roll_control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x628bdf0f, original_name='RollControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    yaw_control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x78d03a32, original_name='YawControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    pitch_control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xb4a2e15a, original_name='PitchControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    target_object_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0xb5bfab00, original_name='TargetObjectOffset', from_json=Vector.from_json, to_json=Vector.to_json
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
        if property_count != 9:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x493d6a2d
        motion_spline_type = SplineType.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x27e5f874
        motion_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd1e2f56
        motion_spline_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa5753d52
        initial_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xae80628f
        unknown = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x628bdf0f
        roll_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78d03a32
        yaw_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb4a2e15a
        pitch_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5bfab00
        target_object_offset = Vector.from_stream(data)
    
        return cls(motion_spline_type, motion_control_spline, motion_spline_duration, initial_time, unknown, roll_control_spline, yaw_control_spline, pitch_control_spline, target_object_offset)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\t')  # 9 properties

        data.write(b'I=j-')  # 0x493d6a2d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.motion_spline_type.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"'\xe5\xf8t")  # 0x27e5f874
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.motion_control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfd\x1e/V')  # 0xfd1e2f56
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.motion_spline_duration))

        data.write(b'\xa5u=R')  # 0xa5753d52
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.initial_time))

        data.write(b'\xae\x80b\x8f')  # 0xae80628f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.unknown))

        data.write(b'b\x8b\xdf\x0f')  # 0x628bdf0f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.roll_control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'x\xd0:2')  # 0x78d03a32
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.yaw_control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb4\xa2\xe1Z')  # 0xb4a2e15a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.pitch_control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb5\xbf\xab\x00')  # 0xb5bfab00
        data.write(b'\x00\x0c')  # size
        self.target_object_offset.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PlatformMotionPropertiesJson", data)
        return cls(
            motion_spline_type=SplineType.from_json(json_data['motion_spline_type']),
            motion_control_spline=Spline.from_json(json_data['motion_control_spline']),
            motion_spline_duration=json_data['motion_spline_duration'],
            initial_time=json_data['initial_time'],
            unknown=json_data['unknown'],
            roll_control_spline=Spline.from_json(json_data['roll_control_spline']),
            yaw_control_spline=Spline.from_json(json_data['yaw_control_spline']),
            pitch_control_spline=Spline.from_json(json_data['pitch_control_spline']),
            target_object_offset=Vector.from_json(json_data['target_object_offset']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'motion_spline_type': self.motion_spline_type.to_json(),
            'motion_control_spline': self.motion_control_spline.to_json(),
            'motion_spline_duration': self.motion_spline_duration,
            'initial_time': self.initial_time,
            'unknown': self.unknown,
            'roll_control_spline': self.roll_control_spline.to_json(),
            'yaw_control_spline': self.yaw_control_spline.to_json(),
            'pitch_control_spline': self.pitch_control_spline.to_json(),
            'target_object_offset': self.target_object_offset.to_json(),
        }


def _decode_motion_spline_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_initial_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


def _decode_target_object_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x493d6a2d: ('motion_spline_type', SplineType.from_stream),
    0x27e5f874: ('motion_control_spline', Spline.from_stream),
    0xfd1e2f56: ('motion_spline_duration', _decode_motion_spline_duration),
    0xa5753d52: ('initial_time', _decode_initial_time),
    0xae80628f: ('unknown', _decode_unknown),
    0x628bdf0f: ('roll_control_spline', Spline.from_stream),
    0x78d03a32: ('yaw_control_spline', Spline.from_stream),
    0xb4a2e15a: ('pitch_control_spline', Spline.from_stream),
    0xb5bfab00: ('target_object_offset', _decode_target_object_offset),
}
