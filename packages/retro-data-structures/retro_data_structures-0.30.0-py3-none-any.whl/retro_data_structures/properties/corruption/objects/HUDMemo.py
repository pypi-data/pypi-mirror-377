# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class HUDMemoJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        display_time: float
        clear_window: bool
        type_out: bool
        display_type: int
        message_type: int
        has_border: bool
        priority: int
        string: int
        index_into_string: int
        font_scale: float
        enable_play_alert: bool
        unknown_0xb7a3e235: bool
        unknown_0x8f115e7a: bool
        unknown_0xd25a8445: bool
        animation: json_util.JsonObject
        model: int
        caad: int
        texture: int
        texture_static: float
        audio_stream: int
    

class MessageType(enum.IntEnum):
    Unknown1 = 903903793
    Unknown2 = 20004303
    Unknown3 = 353225947
    Unknown4 = 3457428906

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


@dataclasses.dataclass()
class HUDMemo(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    display_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1a26c1cc, original_name='DisplayTime'
        ),
    })
    clear_window: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x84e2496f, original_name='ClearWindow'
        ),
    })
    type_out: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xafd0158e, original_name='TypeOut'
        ),
    })
    display_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x4ab3b95b, original_name='DisplayType'
        ),
    })
    message_type: MessageType = dataclasses.field(default=MessageType.Unknown1, metadata={
        'reflection': FieldReflection[MessageType](
            MessageType, id=0x2b4e290c, original_name='MessageType', from_json=MessageType.from_json, to_json=MessageType.to_json
        ),
    })
    has_border: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe4c54c15, original_name='HasBorder'
        ),
    })
    priority: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x42087650, original_name='Priority'
        ),
    })
    string: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRG'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9182250c, original_name='String'
        ),
    })
    index_into_string: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x64124219, original_name='IndexIntoString'
        ),
    })
    font_scale: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x01009a8c, original_name='FontScale'
        ),
    })
    enable_play_alert: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xfb0e87da, original_name='EnablePlayAlert'
        ),
    })
    unknown_0xb7a3e235: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb7a3e235, original_name='Unknown'
        ),
    })
    unknown_0x8f115e7a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8f115e7a, original_name='Unknown'
        ),
    })
    unknown_0xd25a8445: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xd25a8445, original_name='Unknown'
        ),
    })
    animation: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa3d63f44, original_name='Animation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc27ffa8f, original_name='Model'
        ),
    })
    caad: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAAD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x95a100ab, original_name='CAAD'
        ),
    })
    texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd1f65872, original_name='Texture'
        ),
    })
    texture_static: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x46dca528, original_name='TextureStatic'
        ),
    })
    audio_stream: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRM'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe5deb9c4, original_name='AudioStream'
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
        return 'MEMO'

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
        if property_count != 21:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a26c1cc
        display_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84e2496f
        clear_window = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xafd0158e
        type_out = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ab3b95b
        display_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b4e290c
        message_type = MessageType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe4c54c15
        has_border = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42087650
        priority = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9182250c
        string = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x64124219
        index_into_string = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01009a8c
        font_scale = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfb0e87da
        enable_play_alert = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb7a3e235
        unknown_0xb7a3e235 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f115e7a
        unknown_0x8f115e7a = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd25a8445
        unknown_0xd25a8445 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa3d63f44
        animation = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc27ffa8f
        model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95a100ab
        caad = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd1f65872
        texture = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x46dca528
        texture_static = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe5deb9c4
        audio_stream = struct.unpack(">Q", data.read(8))[0]
    
        return cls(editor_properties, display_time, clear_window, type_out, display_type, message_type, has_border, priority, string, index_into_string, font_scale, enable_play_alert, unknown_0xb7a3e235, unknown_0x8f115e7a, unknown_0xd25a8445, animation, model, caad, texture, texture_static, audio_stream)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x15')  # 21 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1a&\xc1\xcc')  # 0x1a26c1cc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.display_time))

        data.write(b'\x84\xe2Io')  # 0x84e2496f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.clear_window))

        data.write(b'\xaf\xd0\x15\x8e')  # 0xafd0158e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.type_out))

        data.write(b'J\xb3\xb9[')  # 0x4ab3b95b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.display_type))

        data.write(b'+N)\x0c')  # 0x2b4e290c
        data.write(b'\x00\x04')  # size
        self.message_type.to_stream(data)

        data.write(b'\xe4\xc5L\x15')  # 0xe4c54c15
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.has_border))

        data.write(b'B\x08vP')  # 0x42087650
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.priority))

        data.write(b'\x91\x82%\x0c')  # 0x9182250c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.string))

        data.write(b'd\x12B\x19')  # 0x64124219
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.index_into_string))

        data.write(b'\x01\x00\x9a\x8c')  # 0x1009a8c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.font_scale))

        data.write(b'\xfb\x0e\x87\xda')  # 0xfb0e87da
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.enable_play_alert))

        data.write(b'\xb7\xa3\xe25')  # 0xb7a3e235
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xb7a3e235))

        data.write(b'\x8f\x11^z')  # 0x8f115e7a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x8f115e7a))

        data.write(b'\xd2Z\x84E')  # 0xd25a8445
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xd25a8445))

        data.write(b'\xa3\xd6?D')  # 0xa3d63f44
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc2\x7f\xfa\x8f')  # 0xc27ffa8f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model))

        data.write(b'\x95\xa1\x00\xab')  # 0x95a100ab
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caad))

        data.write(b'\xd1\xf6Xr')  # 0xd1f65872
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.texture))

        data.write(b'F\xdc\xa5(')  # 0x46dca528
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.texture_static))

        data.write(b'\xe5\xde\xb9\xc4')  # 0xe5deb9c4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.audio_stream))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("HUDMemoJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            display_time=json_data['display_time'],
            clear_window=json_data['clear_window'],
            type_out=json_data['type_out'],
            display_type=json_data['display_type'],
            message_type=MessageType.from_json(json_data['message_type']),
            has_border=json_data['has_border'],
            priority=json_data['priority'],
            string=json_data['string'],
            index_into_string=json_data['index_into_string'],
            font_scale=json_data['font_scale'],
            enable_play_alert=json_data['enable_play_alert'],
            unknown_0xb7a3e235=json_data['unknown_0xb7a3e235'],
            unknown_0x8f115e7a=json_data['unknown_0x8f115e7a'],
            unknown_0xd25a8445=json_data['unknown_0xd25a8445'],
            animation=AnimationParameters.from_json(json_data['animation']),
            model=json_data['model'],
            caad=json_data['caad'],
            texture=json_data['texture'],
            texture_static=json_data['texture_static'],
            audio_stream=json_data['audio_stream'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'display_time': self.display_time,
            'clear_window': self.clear_window,
            'type_out': self.type_out,
            'display_type': self.display_type,
            'message_type': self.message_type.to_json(),
            'has_border': self.has_border,
            'priority': self.priority,
            'string': self.string,
            'index_into_string': self.index_into_string,
            'font_scale': self.font_scale,
            'enable_play_alert': self.enable_play_alert,
            'unknown_0xb7a3e235': self.unknown_0xb7a3e235,
            'unknown_0x8f115e7a': self.unknown_0x8f115e7a,
            'unknown_0xd25a8445': self.unknown_0xd25a8445,
            'animation': self.animation.to_json(),
            'model': self.model,
            'caad': self.caad,
            'texture': self.texture,
            'texture_static': self.texture_static,
            'audio_stream': self.audio_stream,
        }


def _decode_display_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_clear_window(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_type_out(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_display_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_message_type(data: typing.BinaryIO, property_size: int) -> MessageType:
    return MessageType.from_stream(data)


def _decode_has_border(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_priority(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_string(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_index_into_string(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_font_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_enable_play_alert(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xb7a3e235(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x8f115e7a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xd25a8445(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caad(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_texture(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_texture_static(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_audio_stream(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x1a26c1cc: ('display_time', _decode_display_time),
    0x84e2496f: ('clear_window', _decode_clear_window),
    0xafd0158e: ('type_out', _decode_type_out),
    0x4ab3b95b: ('display_type', _decode_display_type),
    0x2b4e290c: ('message_type', _decode_message_type),
    0xe4c54c15: ('has_border', _decode_has_border),
    0x42087650: ('priority', _decode_priority),
    0x9182250c: ('string', _decode_string),
    0x64124219: ('index_into_string', _decode_index_into_string),
    0x1009a8c: ('font_scale', _decode_font_scale),
    0xfb0e87da: ('enable_play_alert', _decode_enable_play_alert),
    0xb7a3e235: ('unknown_0xb7a3e235', _decode_unknown_0xb7a3e235),
    0x8f115e7a: ('unknown_0x8f115e7a', _decode_unknown_0x8f115e7a),
    0xd25a8445: ('unknown_0xd25a8445', _decode_unknown_0xd25a8445),
    0xa3d63f44: ('animation', AnimationParameters.from_stream),
    0xc27ffa8f: ('model', _decode_model),
    0x95a100ab: ('caad', _decode_caad),
    0xd1f65872: ('texture', _decode_texture),
    0x46dca528: ('texture_static', _decode_texture_static),
    0xe5deb9c4: ('audio_stream', _decode_audio_stream),
}
