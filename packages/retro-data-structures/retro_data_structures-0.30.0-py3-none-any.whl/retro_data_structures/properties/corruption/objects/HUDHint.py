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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class HUDHintJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        hud_texture: int
        unknown_0x6078a651: float
        unknown_0xf00bb6bb: float
        icon_scale: float
        animation_time: float
        animation_frames: int
        unknown_0xd993f97b: int
    

@dataclasses.dataclass()
class HUDHint(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    hud_texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd80447e0, original_name='HudTexture'
        ),
    })
    unknown_0x6078a651: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6078a651, original_name='Unknown'
        ),
    })
    unknown_0xf00bb6bb: float = dataclasses.field(default=16.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf00bb6bb, original_name='Unknown'
        ),
    })
    icon_scale: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1ad247a1, original_name='IconScale'
        ),
    })
    animation_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2a53245a, original_name='AnimationTime'
        ),
    })
    animation_frames: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6e88d6ad, original_name='AnimationFrames'
        ),
    })
    unknown_0xd993f97b: int = dataclasses.field(default=15, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd993f97b, original_name='Unknown'
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
        return 'HHNT'

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
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd80447e0
        hud_texture = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6078a651
        unknown_0x6078a651 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf00bb6bb
        unknown_0xf00bb6bb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ad247a1
        icon_scale = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2a53245a
        animation_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6e88d6ad
        animation_frames = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd993f97b
        unknown_0xd993f97b = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, hud_texture, unknown_0x6078a651, unknown_0xf00bb6bb, icon_scale, animation_time, animation_frames, unknown_0xd993f97b)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd8\x04G\xe0')  # 0xd80447e0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.hud_texture))

        data.write(b'`x\xa6Q')  # 0x6078a651
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6078a651))

        data.write(b'\xf0\x0b\xb6\xbb')  # 0xf00bb6bb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf00bb6bb))

        data.write(b'\x1a\xd2G\xa1')  # 0x1ad247a1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.icon_scale))

        data.write(b'*S$Z')  # 0x2a53245a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.animation_time))

        data.write(b'n\x88\xd6\xad')  # 0x6e88d6ad
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.animation_frames))

        data.write(b'\xd9\x93\xf9{')  # 0xd993f97b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xd993f97b))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("HUDHintJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            hud_texture=json_data['hud_texture'],
            unknown_0x6078a651=json_data['unknown_0x6078a651'],
            unknown_0xf00bb6bb=json_data['unknown_0xf00bb6bb'],
            icon_scale=json_data['icon_scale'],
            animation_time=json_data['animation_time'],
            animation_frames=json_data['animation_frames'],
            unknown_0xd993f97b=json_data['unknown_0xd993f97b'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'hud_texture': self.hud_texture,
            'unknown_0x6078a651': self.unknown_0x6078a651,
            'unknown_0xf00bb6bb': self.unknown_0xf00bb6bb,
            'icon_scale': self.icon_scale,
            'animation_time': self.animation_time,
            'animation_frames': self.animation_frames,
            'unknown_0xd993f97b': self.unknown_0xd993f97b,
        }


def _decode_hud_texture(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x6078a651(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf00bb6bb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_icon_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_animation_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_animation_frames(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xd993f97b(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xd80447e0: ('hud_texture', _decode_hud_texture),
    0x6078a651: ('unknown_0x6078a651', _decode_unknown_0x6078a651),
    0xf00bb6bb: ('unknown_0xf00bb6bb', _decode_unknown_0xf00bb6bb),
    0x1ad247a1: ('icon_scale', _decode_icon_scale),
    0x2a53245a: ('animation_time', _decode_animation_time),
    0x6e88d6ad: ('animation_frames', _decode_animation_frames),
    0xd993f97b: ('unknown_0xd993f97b', _decode_unknown_0xd993f97b),
}
