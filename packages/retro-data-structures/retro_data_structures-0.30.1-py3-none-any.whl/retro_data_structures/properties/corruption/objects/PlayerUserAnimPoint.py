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
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters

if typing.TYPE_CHECKING:
    class PlayerUserAnimPointJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        animation: json_util.JsonObject
        attach_dist: float
        unknown_0xad2d4f53: float
        unknown_0x285b4540: float
        unknown_0x6806d0b3: float
        unknown_0x1ce620a7: int
    

@dataclasses.dataclass()
class PlayerUserAnimPoint(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    animation: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa3d63f44, original_name='Animation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    attach_dist: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x643d2769, original_name='AttachDist'
        ),
    })
    unknown_0xad2d4f53: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad2d4f53, original_name='Unknown'
        ),
    })
    unknown_0x285b4540: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x285b4540, original_name='Unknown'
        ),
    })
    unknown_0x6806d0b3: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6806d0b3, original_name='Unknown'
        ),
    })
    unknown_0x1ce620a7: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1ce620a7, original_name='Unknown'
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
        return 'PUAP'

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
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa3d63f44
        animation = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x643d2769
        attach_dist = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad2d4f53
        unknown_0xad2d4f53 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x285b4540
        unknown_0x285b4540 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6806d0b3
        unknown_0x6806d0b3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ce620a7
        unknown_0x1ce620a7 = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, animation, attach_dist, unknown_0xad2d4f53, unknown_0x285b4540, unknown_0x6806d0b3, unknown_0x1ce620a7)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa3\xd6?D')  # 0xa3d63f44
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"d='i")  # 0x643d2769
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attach_dist))

        data.write(b'\xad-OS')  # 0xad2d4f53
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xad2d4f53))

        data.write(b'([E@')  # 0x285b4540
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x285b4540))

        data.write(b'h\x06\xd0\xb3')  # 0x6806d0b3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6806d0b3))

        data.write(b'\x1c\xe6 \xa7')  # 0x1ce620a7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x1ce620a7))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PlayerUserAnimPointJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            animation=AnimationParameters.from_json(json_data['animation']),
            attach_dist=json_data['attach_dist'],
            unknown_0xad2d4f53=json_data['unknown_0xad2d4f53'],
            unknown_0x285b4540=json_data['unknown_0x285b4540'],
            unknown_0x6806d0b3=json_data['unknown_0x6806d0b3'],
            unknown_0x1ce620a7=json_data['unknown_0x1ce620a7'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'animation': self.animation.to_json(),
            'attach_dist': self.attach_dist,
            'unknown_0xad2d4f53': self.unknown_0xad2d4f53,
            'unknown_0x285b4540': self.unknown_0x285b4540,
            'unknown_0x6806d0b3': self.unknown_0x6806d0b3,
            'unknown_0x1ce620a7': self.unknown_0x1ce620a7,
        }


def _decode_attach_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xad2d4f53(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x285b4540(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6806d0b3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1ce620a7(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xa3d63f44: ('animation', AnimationParameters.from_stream),
    0x643d2769: ('attach_dist', _decode_attach_dist),
    0xad2d4f53: ('unknown_0xad2d4f53', _decode_unknown_0xad2d4f53),
    0x285b4540: ('unknown_0x285b4540', _decode_unknown_0x285b4540),
    0x6806d0b3: ('unknown_0x6806d0b3', _decode_unknown_0x6806d0b3),
    0x1ce620a7: ('unknown_0x1ce620a7', _decode_unknown_0x1ce620a7),
}
