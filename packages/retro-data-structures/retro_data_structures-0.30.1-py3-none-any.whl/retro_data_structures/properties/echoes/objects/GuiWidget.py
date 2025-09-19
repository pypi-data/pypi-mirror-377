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

    class GuiWidgetJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        gui_widget_properties: json_util.JsonObject
        controller_number: int
    

@dataclasses.dataclass()
class GuiWidget(BaseObjectType):
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
    controller_number: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xdb7f4aa2, original_name='ControllerNumber'
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
        return 'GWIG'

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
        if property_count != 3:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size, default_override={'active': False})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x91cefa1e
        gui_widget_properties = GuiWidgetProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdb7f4aa2
        controller_number = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, gui_widget_properties, controller_number)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x02')  # 2 properties
        num_properties_written = 2

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

        if self.controller_number != default_override.get('controller_number', 1):
            num_properties_written += 1
            data.write(b'\xdb\x7fJ\xa2')  # 0xdb7f4aa2
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>l', self.controller_number))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.write(struct.pack(">H", num_properties_written))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("GuiWidgetJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            gui_widget_properties=GuiWidgetProperties.from_json(json_data['gui_widget_properties']),
            controller_number=json_data['controller_number'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'gui_widget_properties': self.gui_widget_properties.to_json(),
            'controller_number': self.controller_number,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.gui_widget_properties.dependencies_for, "gui_widget_properties", "GuiWidgetProperties"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for GuiWidget.{field_name} ({field_type}): {e}"
                )


def _decode_editor_properties(data: typing.BinaryIO, property_size: int) -> EditorProperties:
    return EditorProperties.from_stream(data, property_size, default_override={'active': False})


def _decode_controller_number(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', _decode_editor_properties),
    0x91cefa1e: ('gui_widget_properties', GuiWidgetProperties.from_stream),
    0xdb7f4aa2: ('controller_number', _decode_controller_number),
}
