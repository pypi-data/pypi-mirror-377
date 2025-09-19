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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class CameraBlurKeyframeJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        blur_type: int
        blur_radius: float
        which_filter_group: int
        interpolate_in_time: float
        interpolate_out_time: float
    

@dataclasses.dataclass()
class CameraBlurKeyframe(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    blur_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe9359148, original_name='BlurType'
        ),
    })
    blur_radius: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6f6eb1f4, original_name='BlurRadius'
        ),
    })
    which_filter_group: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x3fdc4b2e, original_name='WhichFilterGroup'
        ),
    })
    interpolate_in_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xabd41a36, original_name='InterpolateInTime'
        ),
    })
    interpolate_out_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3eaf78fe, original_name='InterpolateOutTime'
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
        return 'BLUR'

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
        if property_count != 6:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9359148
        blur_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6f6eb1f4
        blur_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3fdc4b2e
        which_filter_group = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xabd41a36
        interpolate_in_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3eaf78fe
        interpolate_out_time = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, blur_type, blur_radius, which_filter_group, interpolate_in_time, interpolate_out_time)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe95\x91H')  # 0xe9359148
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.blur_type))

        data.write(b'on\xb1\xf4')  # 0x6f6eb1f4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.blur_radius))

        data.write(b'?\xdcK.')  # 0x3fdc4b2e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.which_filter_group))

        data.write(b'\xab\xd4\x1a6')  # 0xabd41a36
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.interpolate_in_time))

        data.write(b'>\xafx\xfe')  # 0x3eaf78fe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.interpolate_out_time))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraBlurKeyframeJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            blur_type=json_data['blur_type'],
            blur_radius=json_data['blur_radius'],
            which_filter_group=json_data['which_filter_group'],
            interpolate_in_time=json_data['interpolate_in_time'],
            interpolate_out_time=json_data['interpolate_out_time'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'blur_type': self.blur_type,
            'blur_radius': self.blur_radius,
            'which_filter_group': self.which_filter_group,
            'interpolate_in_time': self.interpolate_in_time,
            'interpolate_out_time': self.interpolate_out_time,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for CameraBlurKeyframe.{field_name} ({field_type}): {e}"
                )


def _decode_blur_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_blur_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_which_filter_group(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_interpolate_in_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_interpolate_out_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xe9359148: ('blur_type', _decode_blur_type),
    0x6f6eb1f4: ('blur_radius', _decode_blur_radius),
    0x3fdc4b2e: ('which_filter_group', _decode_which_filter_group),
    0xabd41a36: ('interpolate_in_time', _decode_interpolate_in_time),
    0x3eaf78fe: ('interpolate_out_time', _decode_interpolate_out_time),
}
