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
from retro_data_structures.properties.corruption.archetypes.TriggerInfo import TriggerInfo

if typing.TYPE_CHECKING:
    class TriggerJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        shape: int
        trigger: json_util.JsonObject
        fix_position_on_activate: bool
    

@dataclasses.dataclass()
class Trigger(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    shape: int = dataclasses.field(default=1210786545, metadata={
        'reflection': FieldReflection[int](
            int, id=0x09ecee0c, original_name='Shape'
        ),
    })  # Choice
    trigger: TriggerInfo = dataclasses.field(default_factory=TriggerInfo, metadata={
        'reflection': FieldReflection[TriggerInfo](
            TriggerInfo, id=0x77a27411, original_name='Trigger', from_json=TriggerInfo.from_json, to_json=TriggerInfo.to_json
        ),
    })
    fix_position_on_activate: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x66a43eef, original_name='FixPositionOnActivate'
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
        return 'TRGR'

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
        if property_count != 4:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x09ecee0c
        shape = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77a27411
        trigger = TriggerInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66a43eef
        fix_position_on_activate = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, shape, trigger, fix_position_on_activate)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\t\xec\xee\x0c')  # 0x9ecee0c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.shape))

        data.write(b'w\xa2t\x11')  # 0x77a27411
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.trigger.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'f\xa4>\xef')  # 0x66a43eef
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.fix_position_on_activate))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TriggerJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            shape=json_data['shape'],
            trigger=TriggerInfo.from_json(json_data['trigger']),
            fix_position_on_activate=json_data['fix_position_on_activate'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'shape': self.shape,
            'trigger': self.trigger.to_json(),
            'fix_position_on_activate': self.fix_position_on_activate,
        }


def _decode_shape(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


def _decode_fix_position_on_activate(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x9ecee0c: ('shape', _decode_shape),
    0x77a27411: ('trigger', TriggerInfo.from_stream),
    0x66a43eef: ('fix_position_on_activate', _decode_fix_position_on_activate),
}
