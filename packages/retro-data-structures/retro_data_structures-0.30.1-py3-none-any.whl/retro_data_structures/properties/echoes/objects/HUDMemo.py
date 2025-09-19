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
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class HUDMemoJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        display_time: float
        clear_window: bool
        player1: bool
        player2: bool
        player3: bool
        player4: bool
        type_out: bool
        use_originator: bool
        display_type: int
        string: int
    

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
    player1: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa8fadfa5, original_name='Player1'
        ),
    })
    player2: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xef5aa575, original_name='Player2'
        ),
    })
    player3: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xd23a8cc5, original_name='Player3'
        ),
    })
    player4: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x601a50d5, original_name='Player4'
        ),
    })
    type_out: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xafd0158e, original_name='TypeOut'
        ),
    })
    use_originator: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xbd6f7b11, original_name='UseOriginator'
        ),
    })
    display_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x4ab3b95b, original_name='DisplayType'
        ),
    })
    string: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRG'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9182250c, original_name='String'
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
        if property_count != 11:
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
        assert property_id == 0xa8fadfa5
        player1 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef5aa575
        player2 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd23a8cc5
        player3 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x601a50d5
        player4 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xafd0158e
        type_out = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbd6f7b11
        use_originator = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ab3b95b
        display_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9182250c
        string = struct.unpack(">L", data.read(4))[0]
    
        return cls(editor_properties, display_time, clear_window, player1, player2, player3, player4, type_out, use_originator, display_type, string)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0b')  # 11 properties

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

        data.write(b'\xa8\xfa\xdf\xa5')  # 0xa8fadfa5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.player1))

        data.write(b'\xefZ\xa5u')  # 0xef5aa575
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.player2))

        data.write(b'\xd2:\x8c\xc5')  # 0xd23a8cc5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.player3))

        data.write(b'`\x1aP\xd5')  # 0x601a50d5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.player4))

        data.write(b'\xaf\xd0\x15\x8e')  # 0xafd0158e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.type_out))

        data.write(b'\xbdo{\x11')  # 0xbd6f7b11
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.use_originator))

        data.write(b'J\xb3\xb9[')  # 0x4ab3b95b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.display_type))

        data.write(b'\x91\x82%\x0c')  # 0x9182250c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.string))

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
            player1=json_data['player1'],
            player2=json_data['player2'],
            player3=json_data['player3'],
            player4=json_data['player4'],
            type_out=json_data['type_out'],
            use_originator=json_data['use_originator'],
            display_type=json_data['display_type'],
            string=json_data['string'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'display_time': self.display_time,
            'clear_window': self.clear_window,
            'player1': self.player1,
            'player2': self.player2,
            'player3': self.player3,
            'player4': self.player4,
            'type_out': self.type_out,
            'use_originator': self.use_originator,
            'display_type': self.display_type,
            'string': self.string,
        }

    def _dependencies_for_string(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.string)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self._dependencies_for_string, "string", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for HUDMemo.{field_name} ({field_type}): {e}"
                )


def _decode_display_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_clear_window(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_player1(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_player2(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_player3(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_player4(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_type_out(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_use_originator(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_display_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_string(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x1a26c1cc: ('display_time', _decode_display_time),
    0x84e2496f: ('clear_window', _decode_clear_window),
    0xa8fadfa5: ('player1', _decode_player1),
    0xef5aa575: ('player2', _decode_player2),
    0xd23a8cc5: ('player3', _decode_player3),
    0x601a50d5: ('player4', _decode_player4),
    0xafd0158e: ('type_out', _decode_type_out),
    0xbd6f7b11: ('use_originator', _decode_use_originator),
    0x4ab3b95b: ('display_type', _decode_display_type),
    0x9182250c: ('string', _decode_string),
}
