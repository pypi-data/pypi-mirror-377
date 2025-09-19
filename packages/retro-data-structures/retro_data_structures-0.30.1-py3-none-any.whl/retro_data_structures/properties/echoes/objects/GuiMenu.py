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
from retro_data_structures.properties.echoes.archetypes.GuiWidgetProperties import GuiWidgetProperties

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class GuiMenuJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        gui_widget_properties: json_util.JsonObject
        control_direction: int
        wrap_selection: bool
        selection_changed_sound: int
    

@dataclasses.dataclass()
class GuiMenu(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    gui_widget_properties: GuiWidgetProperties = dataclasses.field(default_factory=GuiWidgetProperties, metadata={
        'reflection': FieldReflection[GuiWidgetProperties](
            GuiWidgetProperties, id=0x91cefa1e, original_name='GuiWidgetProperties', from_json=GuiWidgetProperties.from_json, to_json=GuiWidgetProperties.to_json
        ),
    })
    control_direction: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa714d574, original_name='ControlDirection'
        ),
    })
    wrap_selection: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x84f708c8, original_name='WrapSelection'
        ),
    })
    selection_changed_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xbe50269e, original_name='SelectionChangedSound'
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
        return 'GMNU'

    @classmethod
    def modules(cls) -> list[str]:
        return ['ScriptGui.rel']

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
        if property_count != 5:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size, default_override={'active': False})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x91cefa1e
        gui_widget_properties = GuiWidgetProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa714d574
        control_direction = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84f708c8
        wrap_selection = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe50269e
        selection_changed_sound = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, gui_widget_properties, control_direction, wrap_selection, selection_changed_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data, default_override={'active': False})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x91\xce\xfa\x1e')  # 0x91cefa1e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.gui_widget_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa7\x14\xd5t')  # 0xa714d574
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.control_direction))

        data.write(b'\x84\xf7\x08\xc8')  # 0x84f708c8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.wrap_selection))

        data.write(b'\xbeP&\x9e')  # 0xbe50269e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.selection_changed_sound))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("GuiMenuJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            gui_widget_properties=GuiWidgetProperties.from_json(json_data['gui_widget_properties']),
            control_direction=json_data['control_direction'],
            wrap_selection=json_data['wrap_selection'],
            selection_changed_sound=json_data['selection_changed_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'gui_widget_properties': self.gui_widget_properties.to_json(),
            'control_direction': self.control_direction,
            'wrap_selection': self.wrap_selection,
            'selection_changed_sound': self.selection_changed_sound,
        }

    def _dependencies_for_selection_changed_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.selection_changed_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.gui_widget_properties.dependencies_for, "gui_widget_properties", "GuiWidgetProperties"),
            (self._dependencies_for_selection_changed_sound, "selection_changed_sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for GuiMenu.{field_name} ({field_type}): {e}"
                )


def _decode_editor_properties(data: typing.BinaryIO, property_size: int) -> EditorProperties:
    return EditorProperties.from_stream(data, property_size, default_override={'active': False})


def _decode_control_direction(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_wrap_selection(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_selection_changed_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', _decode_editor_properties),
    0x91cefa1e: ('gui_widget_properties', GuiWidgetProperties.from_stream),
    0xa714d574: ('control_direction', _decode_control_direction),
    0x84f708c8: ('wrap_selection', _decode_wrap_selection),
    0xbe50269e: ('selection_changed_sound', _decode_selection_changed_sound),
}
