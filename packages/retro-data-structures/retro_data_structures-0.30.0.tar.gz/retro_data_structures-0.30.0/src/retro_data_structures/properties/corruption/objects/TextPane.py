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
from retro_data_structures.properties.corruption.archetypes.TextProperties import TextProperties
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class TextPaneJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        gui_label: str
        text_properties: json_util.JsonObject
        japan_text_properties: json_util.JsonObject
        pivot_offset: json_util.JsonValue
        default_string: int
        default_string_name: str
        blend_mode: int
        fade_in_time: float
        fade_out_time: float
        depth_compare: bool
        depth_update: bool
        depth_backwards: bool
        unknown_0xf5937b1f: bool
        unknown_0x306a19b8: bool
        unknown_0xd62263af: bool
        unknown_0xa1d9802e: float
        unknown_0x7f451a89: float
        unknown_0xde56521d: bool
        show_cursor: bool
    

@dataclasses.dataclass()
class TextPane(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    gui_label: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x73939407, original_name='GuiLabel'
        ),
    })
    text_properties: TextProperties = dataclasses.field(default_factory=TextProperties, metadata={
        'reflection': FieldReflection[TextProperties](
            TextProperties, id=0xe0543e66, original_name='TextProperties', from_json=TextProperties.from_json, to_json=TextProperties.to_json
        ),
    })
    japan_text_properties: TextProperties = dataclasses.field(default_factory=TextProperties, metadata={
        'reflection': FieldReflection[TextProperties](
            TextProperties, id=0xc8e441fa, original_name='JapanTextProperties', from_json=TextProperties.from_json, to_json=TextProperties.to_json
        ),
    })
    pivot_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0xdef21bf5, original_name='PivotOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    default_string: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRG'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe7ac3927, original_name='DefaultString'
        ),
    })
    default_string_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xd501c87e, original_name='DefaultStringName'
        ),
    })
    blend_mode: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x94f0365c, original_name='Blend_Mode'
        ),
    })
    fade_in_time: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x90aa341f, original_name='FadeInTime'
        ),
    })
    fade_out_time: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7c269ebc, original_name='FadeOutTime'
        ),
    })
    depth_compare: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x94c01b0c, original_name='Depth_Compare'
        ),
    })
    depth_update: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xaed25a51, original_name='Depth_Update'
        ),
    })
    depth_backwards: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x35dc43d0, original_name='Depth_Backwards'
        ),
    })
    unknown_0xf5937b1f: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf5937b1f, original_name='Unknown'
        ),
    })
    unknown_0x306a19b8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x306a19b8, original_name='Unknown'
        ),
    })
    unknown_0xd62263af: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xd62263af, original_name='Unknown'
        ),
    })
    unknown_0xa1d9802e: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa1d9802e, original_name='Unknown'
        ),
    })
    unknown_0x7f451a89: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7f451a89, original_name='Unknown'
        ),
    })
    unknown_0xde56521d: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xde56521d, original_name='Unknown'
        ),
    })
    show_cursor: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5e385488, original_name='ShowCursor'
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
        return 'TXPN'

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
        if property_count != 20:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x73939407
        gui_label = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0543e66
        text_properties = TextProperties.from_stream(data, property_size, default_override={'text_bounding_width': 80, 'text_bounding_height': 10})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8e441fa
        japan_text_properties = TextProperties.from_stream(data, property_size, default_override={'text_bounding_width': 80, 'text_bounding_height': 10})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdef21bf5
        pivot_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe7ac3927
        default_string = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd501c87e
        default_string_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x94f0365c
        blend_mode = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90aa341f
        fade_in_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7c269ebc
        fade_out_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x94c01b0c
        depth_compare = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaed25a51
        depth_update = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x35dc43d0
        depth_backwards = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5937b1f
        unknown_0xf5937b1f = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x306a19b8
        unknown_0x306a19b8 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd62263af
        unknown_0xd62263af = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa1d9802e
        unknown_0xa1d9802e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f451a89
        unknown_0x7f451a89 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xde56521d
        unknown_0xde56521d = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e385488
        show_cursor = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, gui_label, text_properties, japan_text_properties, pivot_offset, default_string, default_string_name, blend_mode, fade_in_time, fade_out_time, depth_compare, depth_update, depth_backwards, unknown_0xf5937b1f, unknown_0x306a19b8, unknown_0xd62263af, unknown_0xa1d9802e, unknown_0x7f451a89, unknown_0xde56521d, show_cursor)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x14')  # 20 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b's\x93\x94\x07')  # 0x73939407
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.gui_label.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe0T>f')  # 0xe0543e66
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.text_properties.to_stream(data, default_override={'text_bounding_width': 80, 'text_bounding_height': 10})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc8\xe4A\xfa')  # 0xc8e441fa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.japan_text_properties.to_stream(data, default_override={'text_bounding_width': 80, 'text_bounding_height': 10})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xde\xf2\x1b\xf5')  # 0xdef21bf5
        data.write(b'\x00\x0c')  # size
        self.pivot_offset.to_stream(data)

        data.write(b"\xe7\xac9'")  # 0xe7ac3927
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.default_string))

        data.write(b'\xd5\x01\xc8~')  # 0xd501c87e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.default_string_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x94\xf06\\')  # 0x94f0365c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.blend_mode))

        data.write(b'\x90\xaa4\x1f')  # 0x90aa341f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_in_time))

        data.write(b'|&\x9e\xbc')  # 0x7c269ebc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_out_time))

        data.write(b'\x94\xc0\x1b\x0c')  # 0x94c01b0c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.depth_compare))

        data.write(b'\xae\xd2ZQ')  # 0xaed25a51
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.depth_update))

        data.write(b'5\xdcC\xd0')  # 0x35dc43d0
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.depth_backwards))

        data.write(b'\xf5\x93{\x1f')  # 0xf5937b1f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xf5937b1f))

        data.write(b'0j\x19\xb8')  # 0x306a19b8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x306a19b8))

        data.write(b'\xd6"c\xaf')  # 0xd62263af
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xd62263af))

        data.write(b'\xa1\xd9\x80.')  # 0xa1d9802e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa1d9802e))

        data.write(b'\x7fE\x1a\x89')  # 0x7f451a89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7f451a89))

        data.write(b'\xdeVR\x1d')  # 0xde56521d
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xde56521d))

        data.write(b'^8T\x88')  # 0x5e385488
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.show_cursor))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TextPaneJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            gui_label=json_data['gui_label'],
            text_properties=TextProperties.from_json(json_data['text_properties']),
            japan_text_properties=TextProperties.from_json(json_data['japan_text_properties']),
            pivot_offset=Vector.from_json(json_data['pivot_offset']),
            default_string=json_data['default_string'],
            default_string_name=json_data['default_string_name'],
            blend_mode=json_data['blend_mode'],
            fade_in_time=json_data['fade_in_time'],
            fade_out_time=json_data['fade_out_time'],
            depth_compare=json_data['depth_compare'],
            depth_update=json_data['depth_update'],
            depth_backwards=json_data['depth_backwards'],
            unknown_0xf5937b1f=json_data['unknown_0xf5937b1f'],
            unknown_0x306a19b8=json_data['unknown_0x306a19b8'],
            unknown_0xd62263af=json_data['unknown_0xd62263af'],
            unknown_0xa1d9802e=json_data['unknown_0xa1d9802e'],
            unknown_0x7f451a89=json_data['unknown_0x7f451a89'],
            unknown_0xde56521d=json_data['unknown_0xde56521d'],
            show_cursor=json_data['show_cursor'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'gui_label': self.gui_label,
            'text_properties': self.text_properties.to_json(),
            'japan_text_properties': self.japan_text_properties.to_json(),
            'pivot_offset': self.pivot_offset.to_json(),
            'default_string': self.default_string,
            'default_string_name': self.default_string_name,
            'blend_mode': self.blend_mode,
            'fade_in_time': self.fade_in_time,
            'fade_out_time': self.fade_out_time,
            'depth_compare': self.depth_compare,
            'depth_update': self.depth_update,
            'depth_backwards': self.depth_backwards,
            'unknown_0xf5937b1f': self.unknown_0xf5937b1f,
            'unknown_0x306a19b8': self.unknown_0x306a19b8,
            'unknown_0xd62263af': self.unknown_0xd62263af,
            'unknown_0xa1d9802e': self.unknown_0xa1d9802e,
            'unknown_0x7f451a89': self.unknown_0x7f451a89,
            'unknown_0xde56521d': self.unknown_0xde56521d,
            'show_cursor': self.show_cursor,
        }


def _decode_gui_label(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_text_properties(data: typing.BinaryIO, property_size: int) -> TextProperties:
    return TextProperties.from_stream(data, property_size, default_override={'text_bounding_width': 80, 'text_bounding_height': 10})


def _decode_japan_text_properties(data: typing.BinaryIO, property_size: int) -> TextProperties:
    return TextProperties.from_stream(data, property_size, default_override={'text_bounding_width': 80, 'text_bounding_height': 10})


def _decode_pivot_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_default_string(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_default_string_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_blend_mode(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_fade_in_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_out_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_depth_compare(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_depth_update(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_depth_backwards(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xf5937b1f(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x306a19b8(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xd62263af(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xa1d9802e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7f451a89(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xde56521d(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_show_cursor(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x73939407: ('gui_label', _decode_gui_label),
    0xe0543e66: ('text_properties', _decode_text_properties),
    0xc8e441fa: ('japan_text_properties', _decode_japan_text_properties),
    0xdef21bf5: ('pivot_offset', _decode_pivot_offset),
    0xe7ac3927: ('default_string', _decode_default_string),
    0xd501c87e: ('default_string_name', _decode_default_string_name),
    0x94f0365c: ('blend_mode', _decode_blend_mode),
    0x90aa341f: ('fade_in_time', _decode_fade_in_time),
    0x7c269ebc: ('fade_out_time', _decode_fade_out_time),
    0x94c01b0c: ('depth_compare', _decode_depth_compare),
    0xaed25a51: ('depth_update', _decode_depth_update),
    0x35dc43d0: ('depth_backwards', _decode_depth_backwards),
    0xf5937b1f: ('unknown_0xf5937b1f', _decode_unknown_0xf5937b1f),
    0x306a19b8: ('unknown_0x306a19b8', _decode_unknown_0x306a19b8),
    0xd62263af: ('unknown_0xd62263af', _decode_unknown_0xd62263af),
    0xa1d9802e: ('unknown_0xa1d9802e', _decode_unknown_0xa1d9802e),
    0x7f451a89: ('unknown_0x7f451a89', _decode_unknown_0x7f451a89),
    0xde56521d: ('unknown_0xde56521d', _decode_unknown_0xde56521d),
    0x5e385488: ('show_cursor', _decode_show_cursor),
}
