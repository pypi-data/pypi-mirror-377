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
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.SplineType import SplineType
from retro_data_structures.properties.echoes.core.Spline import Spline

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class PathCameraJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        flags_path_camera: int
        unknown_0xd4b29446: int
        motion_spline_type: json_util.JsonObject
        motion_control_spline: json_util.JsonObject
        target_spline_type: json_util.JsonObject
        target_control_spline: json_util.JsonObject
        fov_spline: json_util.JsonObject
        speed_control_spline: json_util.JsonObject
        spline_type: json_util.JsonObject
        unknown_0x431769c6: bool
        distance: float
        speed: float
        dampen_distance: float
        initial_position: int
        angular_speed: float
        unknown_0x12861f7d: json_util.JsonObject
        unknown_0x96ac52b0: json_util.JsonObject
    

@dataclasses.dataclass()
class PathCamera(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    flags_path_camera: int = dataclasses.field(default=32, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5cbd5bae, original_name='FlagsPathCamera'
        ),
    })  # Flagset
    unknown_0xd4b29446: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd4b29446, original_name='Unknown'
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
    target_spline_type: SplineType = dataclasses.field(default_factory=SplineType, metadata={
        'reflection': FieldReflection[SplineType](
            SplineType, id=0x5604d304, original_name='TargetSplineType', from_json=SplineType.from_json, to_json=SplineType.to_json
        ),
    })
    target_control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xc4dfbfa7, original_name='TargetControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    fov_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x6868d4b3, original_name='FOVSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    speed_control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xedd07160, original_name='SpeedControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    spline_type: SplineType = dataclasses.field(default_factory=SplineType, metadata={
        'reflection': FieldReflection[SplineType](
            SplineType, id=0x33e4685b, original_name='SplineType', from_json=SplineType.from_json, to_json=SplineType.to_json
        ),
    })
    unknown_0x431769c6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x431769c6, original_name='Unknown'
        ),
    })
    distance: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3bf43be, original_name='Distance'
        ),
    })
    speed: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6392404e, original_name='Speed'
        ),
    })
    dampen_distance: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x32f835ec, original_name='DampenDistance'
        ),
    })
    initial_position: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe8fc72b6, original_name='InitialPosition'
        ),
    })
    angular_speed: float = dataclasses.field(default=120.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbcd7333f, original_name='AngularSpeed'
        ),
    })
    unknown_0x12861f7d: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x12861f7d, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x96ac52b0: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x96ac52b0, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'PCAM'

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
        if property_count != 18:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5cbd5bae
        flags_path_camera = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4b29446
        unknown_0xd4b29446 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x493d6a2d
        motion_spline_type = SplineType.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x27e5f874
        motion_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5604d304
        target_spline_type = SplineType.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4dfbfa7
        target_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6868d4b3
        fov_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xedd07160
        speed_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x33e4685b
        spline_type = SplineType.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x431769c6
        unknown_0x431769c6 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3bf43be
        distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6392404e
        speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32f835ec
        dampen_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8fc72b6
        initial_position = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbcd7333f
        angular_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12861f7d
        unknown_0x12861f7d = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x96ac52b0
        unknown_0x96ac52b0 = Spline.from_stream(data, property_size)
    
        return cls(editor_properties, flags_path_camera, unknown_0xd4b29446, motion_spline_type, motion_control_spline, target_spline_type, target_control_spline, fov_spline, speed_control_spline, spline_type, unknown_0x431769c6, distance, speed, dampen_distance, initial_position, angular_speed, unknown_0x12861f7d, unknown_0x96ac52b0)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x12')  # 18 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\\\xbd[\xae')  # 0x5cbd5bae
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.flags_path_camera))

        data.write(b'\xd4\xb2\x94F')  # 0xd4b29446
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xd4b29446))

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

        data.write(b'V\x04\xd3\x04')  # 0x5604d304
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.target_spline_type.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc4\xdf\xbf\xa7')  # 0xc4dfbfa7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.target_control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'hh\xd4\xb3')  # 0x6868d4b3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.fov_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed\xd0q`')  # 0xedd07160
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.speed_control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'3\xe4h[')  # 0x33e4685b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spline_type.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'C\x17i\xc6')  # 0x431769c6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x431769c6))

        data.write(b'\xc3\xbfC\xbe')  # 0xc3bf43be
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance))

        data.write(b'c\x92@N')  # 0x6392404e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed))

        data.write(b'2\xf85\xec')  # 0x32f835ec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dampen_distance))

        data.write(b'\xe8\xfcr\xb6')  # 0xe8fc72b6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.initial_position))

        data.write(b'\xbc\xd73?')  # 0xbcd7333f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.angular_speed))

        data.write(b'\x12\x86\x1f}')  # 0x12861f7d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x12861f7d.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x96\xacR\xb0')  # 0x96ac52b0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x96ac52b0.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PathCameraJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            flags_path_camera=json_data['flags_path_camera'],
            unknown_0xd4b29446=json_data['unknown_0xd4b29446'],
            motion_spline_type=SplineType.from_json(json_data['motion_spline_type']),
            motion_control_spline=Spline.from_json(json_data['motion_control_spline']),
            target_spline_type=SplineType.from_json(json_data['target_spline_type']),
            target_control_spline=Spline.from_json(json_data['target_control_spline']),
            fov_spline=Spline.from_json(json_data['fov_spline']),
            speed_control_spline=Spline.from_json(json_data['speed_control_spline']),
            spline_type=SplineType.from_json(json_data['spline_type']),
            unknown_0x431769c6=json_data['unknown_0x431769c6'],
            distance=json_data['distance'],
            speed=json_data['speed'],
            dampen_distance=json_data['dampen_distance'],
            initial_position=json_data['initial_position'],
            angular_speed=json_data['angular_speed'],
            unknown_0x12861f7d=Spline.from_json(json_data['unknown_0x12861f7d']),
            unknown_0x96ac52b0=Spline.from_json(json_data['unknown_0x96ac52b0']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'flags_path_camera': self.flags_path_camera,
            'unknown_0xd4b29446': self.unknown_0xd4b29446,
            'motion_spline_type': self.motion_spline_type.to_json(),
            'motion_control_spline': self.motion_control_spline.to_json(),
            'target_spline_type': self.target_spline_type.to_json(),
            'target_control_spline': self.target_control_spline.to_json(),
            'fov_spline': self.fov_spline.to_json(),
            'speed_control_spline': self.speed_control_spline.to_json(),
            'spline_type': self.spline_type.to_json(),
            'unknown_0x431769c6': self.unknown_0x431769c6,
            'distance': self.distance,
            'speed': self.speed,
            'dampen_distance': self.dampen_distance,
            'initial_position': self.initial_position,
            'angular_speed': self.angular_speed,
            'unknown_0x12861f7d': self.unknown_0x12861f7d.to_json(),
            'unknown_0x96ac52b0': self.unknown_0x96ac52b0.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.motion_spline_type.dependencies_for, "motion_spline_type", "SplineType"),
            (self.target_spline_type.dependencies_for, "target_spline_type", "SplineType"),
            (self.spline_type.dependencies_for, "spline_type", "SplineType"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for PathCamera.{field_name} ({field_type}): {e}"
                )


def _decode_flags_path_camera(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0xd4b29446(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x431769c6(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dampen_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_initial_position(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_angular_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x5cbd5bae: ('flags_path_camera', _decode_flags_path_camera),
    0xd4b29446: ('unknown_0xd4b29446', _decode_unknown_0xd4b29446),
    0x493d6a2d: ('motion_spline_type', SplineType.from_stream),
    0x27e5f874: ('motion_control_spline', Spline.from_stream),
    0x5604d304: ('target_spline_type', SplineType.from_stream),
    0xc4dfbfa7: ('target_control_spline', Spline.from_stream),
    0x6868d4b3: ('fov_spline', Spline.from_stream),
    0xedd07160: ('speed_control_spline', Spline.from_stream),
    0x33e4685b: ('spline_type', SplineType.from_stream),
    0x431769c6: ('unknown_0x431769c6', _decode_unknown_0x431769c6),
    0xc3bf43be: ('distance', _decode_distance),
    0x6392404e: ('speed', _decode_speed),
    0x32f835ec: ('dampen_distance', _decode_dampen_distance),
    0xe8fc72b6: ('initial_position', _decode_initial_position),
    0xbcd7333f: ('angular_speed', _decode_angular_speed),
    0x12861f7d: ('unknown_0x12861f7d', Spline.from_stream),
    0x96ac52b0: ('unknown_0x96ac52b0', Spline.from_stream),
}
