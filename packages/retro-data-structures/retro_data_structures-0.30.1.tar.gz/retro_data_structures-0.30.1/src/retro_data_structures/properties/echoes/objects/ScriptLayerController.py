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
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ScriptLayerControllerJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        layer: json_util.JsonObject
        is_dynamic: bool
    

@dataclasses.dataclass()
class ScriptLayerController(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    layer: LayerSwitch = dataclasses.field(default_factory=LayerSwitch, metadata={
        'reflection': FieldReflection[LayerSwitch](
            LayerSwitch, id=0x8249f6c7, original_name='Layer', from_json=LayerSwitch.from_json, to_json=LayerSwitch.to_json
        ),
    })
    is_dynamic: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x12a7d8b2, original_name='IsDynamic'
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
        return 'SLCT'

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
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8249f6c7
        layer = LayerSwitch.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12a7d8b2
        is_dynamic = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, layer, is_dynamic)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x82I\xf6\xc7')  # 0x8249f6c7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.layer.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x12\xa7\xd8\xb2')  # 0x12a7d8b2
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_dynamic))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ScriptLayerControllerJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            layer=LayerSwitch.from_json(json_data['layer']),
            is_dynamic=json_data['is_dynamic'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'layer': self.layer.to_json(),
            'is_dynamic': self.is_dynamic,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.layer.dependencies_for, "layer", "LayerSwitch"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ScriptLayerController.{field_name} ({field_type}): {e}"
                )


def _decode_is_dynamic(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x8249f6c7: ('layer', LayerSwitch.from_stream),
    0x12a7d8b2: ('is_dynamic', _decode_is_dynamic),
}
