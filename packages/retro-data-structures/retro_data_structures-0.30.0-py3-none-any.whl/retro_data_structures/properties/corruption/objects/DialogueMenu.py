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
from retro_data_structures.properties.corruption.archetypes.TextProperties import TextProperties
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class DialogueMenuJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        text_properties: json_util.JsonObject
        japan_text_properties: json_util.JsonObject
        text_position_y: int
        japan_text_position_y: int
        selected_font_color: json_util.JsonValue
        unknown_0x69fdb265: json_util.JsonValue
        selection_model: int
        unknown_0x3c5e109a: int
        default_selection: int
        highlight_sound: int
        select_sound: int
    

class DefaultSelection(enum.IntEnum):
    Unknown1 = 703550369
    Unknown2 = 3553383554
    Unknown3 = 2736090902

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
class DialogueMenu(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
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
    text_position_y: int = dataclasses.field(default=100, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7b86e0a2, original_name='TextPositionY'
        ),
    })
    japan_text_position_y: int = dataclasses.field(default=100, metadata={
        'reflection': FieldReflection[int](
            int, id=0xeb1b90c2, original_name='JapanTextPositionY'
        ),
    })
    selected_font_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xef505965, original_name='SelectedFontColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x69fdb265: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x69fdb265, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    selection_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd1b74151, original_name='SelectionModel'
        ),
    })
    unknown_0x3c5e109a: int = dataclasses.field(default=110, metadata={
        'reflection': FieldReflection[int](
            int, id=0x3c5e109a, original_name='Unknown'
        ),
    })
    default_selection: DefaultSelection = dataclasses.field(default=DefaultSelection.Unknown1, metadata={
        'reflection': FieldReflection[DefaultSelection](
            DefaultSelection, id=0x58cbcbca, original_name='DefaultSelection', from_json=DefaultSelection.from_json, to_json=DefaultSelection.to_json
        ),
    })
    highlight_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe8fe6e9d, original_name='HighlightSound'
        ),
    })
    select_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9e87e0eb, original_name='SelectSound'
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
        return 'DGMN'

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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0543e66
        text_properties = TextProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8e441fa
        japan_text_properties = TextProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b86e0a2
        text_position_y = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeb1b90c2
        japan_text_position_y = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef505965
        selected_font_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69fdb265
        unknown_0x69fdb265 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd1b74151
        selection_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c5e109a
        unknown_0x3c5e109a = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58cbcbca
        default_selection = DefaultSelection.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8fe6e9d
        highlight_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9e87e0eb
        select_sound = struct.unpack(">Q", data.read(8))[0]
    
        return cls(editor_properties, text_properties, japan_text_properties, text_position_y, japan_text_position_y, selected_font_color, unknown_0x69fdb265, selection_model, unknown_0x3c5e109a, default_selection, highlight_sound, select_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe0T>f')  # 0xe0543e66
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.text_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc8\xe4A\xfa')  # 0xc8e441fa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.japan_text_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'{\x86\xe0\xa2')  # 0x7b86e0a2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.text_position_y))

        data.write(b'\xeb\x1b\x90\xc2')  # 0xeb1b90c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.japan_text_position_y))

        data.write(b'\xefPYe')  # 0xef505965
        data.write(b'\x00\x10')  # size
        self.selected_font_color.to_stream(data)

        data.write(b'i\xfd\xb2e')  # 0x69fdb265
        data.write(b'\x00\x10')  # size
        self.unknown_0x69fdb265.to_stream(data)

        data.write(b'\xd1\xb7AQ')  # 0xd1b74151
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.selection_model))

        data.write(b'<^\x10\x9a')  # 0x3c5e109a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x3c5e109a))

        data.write(b'X\xcb\xcb\xca')  # 0x58cbcbca
        data.write(b'\x00\x04')  # size
        self.default_selection.to_stream(data)

        data.write(b'\xe8\xfen\x9d')  # 0xe8fe6e9d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.highlight_sound))

        data.write(b'\x9e\x87\xe0\xeb')  # 0x9e87e0eb
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.select_sound))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DialogueMenuJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            text_properties=TextProperties.from_json(json_data['text_properties']),
            japan_text_properties=TextProperties.from_json(json_data['japan_text_properties']),
            text_position_y=json_data['text_position_y'],
            japan_text_position_y=json_data['japan_text_position_y'],
            selected_font_color=Color.from_json(json_data['selected_font_color']),
            unknown_0x69fdb265=Color.from_json(json_data['unknown_0x69fdb265']),
            selection_model=json_data['selection_model'],
            unknown_0x3c5e109a=json_data['unknown_0x3c5e109a'],
            default_selection=DefaultSelection.from_json(json_data['default_selection']),
            highlight_sound=json_data['highlight_sound'],
            select_sound=json_data['select_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'text_properties': self.text_properties.to_json(),
            'japan_text_properties': self.japan_text_properties.to_json(),
            'text_position_y': self.text_position_y,
            'japan_text_position_y': self.japan_text_position_y,
            'selected_font_color': self.selected_font_color.to_json(),
            'unknown_0x69fdb265': self.unknown_0x69fdb265.to_json(),
            'selection_model': self.selection_model,
            'unknown_0x3c5e109a': self.unknown_0x3c5e109a,
            'default_selection': self.default_selection.to_json(),
            'highlight_sound': self.highlight_sound,
            'select_sound': self.select_sound,
        }


def _decode_text_position_y(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_japan_text_position_y(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_selected_font_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x69fdb265(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_selection_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x3c5e109a(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_default_selection(data: typing.BinaryIO, property_size: int) -> DefaultSelection:
    return DefaultSelection.from_stream(data)


def _decode_highlight_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_select_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xe0543e66: ('text_properties', TextProperties.from_stream),
    0xc8e441fa: ('japan_text_properties', TextProperties.from_stream),
    0x7b86e0a2: ('text_position_y', _decode_text_position_y),
    0xeb1b90c2: ('japan_text_position_y', _decode_japan_text_position_y),
    0xef505965: ('selected_font_color', _decode_selected_font_color),
    0x69fdb265: ('unknown_0x69fdb265', _decode_unknown_0x69fdb265),
    0xd1b74151: ('selection_model', _decode_selection_model),
    0x3c5e109a: ('unknown_0x3c5e109a', _decode_unknown_0x3c5e109a),
    0x58cbcbca: ('default_selection', _decode_default_selection),
    0xe8fe6e9d: ('highlight_sound', _decode_highlight_sound),
    0x9e87e0eb: ('select_sound', _decode_select_sound),
}
