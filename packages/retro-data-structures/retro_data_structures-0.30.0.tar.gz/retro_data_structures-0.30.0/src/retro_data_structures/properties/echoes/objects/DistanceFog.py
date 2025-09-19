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
from retro_data_structures.properties.echoes.archetypes.Vector2f import Vector2f
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DistanceFogJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        mode: int
        color: json_util.JsonValue
        near_far_plane: json_util.JsonObject
        color_rate: float
        distance_rate: json_util.JsonObject
        force_settings: bool
    

@dataclasses.dataclass()
class DistanceFog(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    mode: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x09ad63de, original_name='Mode'
        ),
    })
    color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x37c7d09d, original_name='Color', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    near_far_plane: Vector2f = dataclasses.field(default_factory=Vector2f, metadata={
        'reflection': FieldReflection[Vector2f](
            Vector2f, id=0x652008da, original_name='NearFarPlane', from_json=Vector2f.from_json, to_json=Vector2f.to_json
        ),
    })
    color_rate: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x29ab4727, original_name='ColorRate'
        ),
    })
    distance_rate: Vector2f = dataclasses.field(default_factory=Vector2f, metadata={
        'reflection': FieldReflection[Vector2f](
            Vector2f, id=0xcc8e0f98, original_name='DistanceRate', from_json=Vector2f.from_json, to_json=Vector2f.to_json
        ),
    })
    force_settings: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc5935b67, original_name='ForceSettings'
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
        return 'DFOG'

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
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size, default_override={'active': False})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x09ad63de
        mode = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37c7d09d
        color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x652008da
        near_far_plane = Vector2f.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x29ab4727
        color_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcc8e0f98
        distance_rate = Vector2f.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc5935b67
        force_settings = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, mode, color, near_far_plane, color_rate, distance_rate, force_settings)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data, default_override={'active': False})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\t\xadc\xde')  # 0x9ad63de
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.mode))

        data.write(b'7\xc7\xd0\x9d')  # 0x37c7d09d
        data.write(b'\x00\x10')  # size
        self.color.to_stream(data)

        data.write(b'e \x08\xda')  # 0x652008da
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.near_far_plane.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b")\xabG'")  # 0x29ab4727
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.color_rate))

        data.write(b'\xcc\x8e\x0f\x98')  # 0xcc8e0f98
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.distance_rate.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc5\x93[g')  # 0xc5935b67
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.force_settings))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DistanceFogJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            mode=json_data['mode'],
            color=Color.from_json(json_data['color']),
            near_far_plane=Vector2f.from_json(json_data['near_far_plane']),
            color_rate=json_data['color_rate'],
            distance_rate=Vector2f.from_json(json_data['distance_rate']),
            force_settings=json_data['force_settings'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'mode': self.mode,
            'color': self.color.to_json(),
            'near_far_plane': self.near_far_plane.to_json(),
            'color_rate': self.color_rate,
            'distance_rate': self.distance_rate.to_json(),
            'force_settings': self.force_settings,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.near_far_plane.dependencies_for, "near_far_plane", "Vector2f"),
            (self.distance_rate.dependencies_for, "distance_rate", "Vector2f"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for DistanceFog.{field_name} ({field_type}): {e}"
                )


def _decode_editor_properties(data: typing.BinaryIO, property_size: int) -> EditorProperties:
    return EditorProperties.from_stream(data, property_size, default_override={'active': False})


def _decode_mode(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_color_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_force_settings(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', _decode_editor_properties),
    0x9ad63de: ('mode', _decode_mode),
    0x37c7d09d: ('color', _decode_color),
    0x652008da: ('near_far_plane', Vector2f.from_stream),
    0x29ab4727: ('color_rate', _decode_color_rate),
    0xcc8e0f98: ('distance_rate', Vector2f.from_stream),
    0xc5935b67: ('force_settings', _decode_force_settings),
}
