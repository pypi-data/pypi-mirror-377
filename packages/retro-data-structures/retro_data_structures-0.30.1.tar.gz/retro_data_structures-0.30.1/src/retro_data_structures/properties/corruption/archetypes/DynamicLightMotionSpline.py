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

if typing.TYPE_CHECKING:
    class DynamicLightMotionSplineJson(typing_extensions.TypedDict):
        motion_spline_path_loops: bool
        motion_spline_type: json_util.JsonObject
        motion_control_spline: json_util.JsonObject
        motion_spline_duration: float
    

@dataclasses.dataclass()
class DynamicLightMotionSpline(BaseProperty):
    motion_spline_path_loops: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3d7406af, original_name='MotionSplinePathLoops'
        ),
    })
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
        if property_count != 4:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d7406af
        motion_spline_path_loops = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x493d6a2d
        motion_spline_type = SplineType.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x27e5f874
        motion_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd1e2f56
        motion_spline_duration = struct.unpack('>f', data.read(4))[0]
    
        return cls(motion_spline_path_loops, motion_spline_type, motion_control_spline, motion_spline_duration)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'=t\x06\xaf')  # 0x3d7406af
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.motion_spline_path_loops))

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

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DynamicLightMotionSplineJson", data)
        return cls(
            motion_spline_path_loops=json_data['motion_spline_path_loops'],
            motion_spline_type=SplineType.from_json(json_data['motion_spline_type']),
            motion_control_spline=Spline.from_json(json_data['motion_control_spline']),
            motion_spline_duration=json_data['motion_spline_duration'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'motion_spline_path_loops': self.motion_spline_path_loops,
            'motion_spline_type': self.motion_spline_type.to_json(),
            'motion_control_spline': self.motion_control_spline.to_json(),
            'motion_spline_duration': self.motion_spline_duration,
        }


def _decode_motion_spline_path_loops(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_motion_spline_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x3d7406af: ('motion_spline_path_loops', _decode_motion_spline_path_loops),
    0x493d6a2d: ('motion_spline_type', SplineType.from_stream),
    0x27e5f874: ('motion_control_spline', Spline.from_stream),
    0xfd1e2f56: ('motion_spline_duration', _decode_motion_spline_duration),
}
