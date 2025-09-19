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

if typing.TYPE_CHECKING:
    class AreaStreamedAudioStateJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        area_state: int
        auto_set: bool
        global_: bool
    

class AreaState(enum.IntEnum):
    Unknown1 = 3421935818
    Unknown2 = 3169953884
    Unknown3 = 637073894
    Unknown4 = 1392494960
    Unknown5 = 3432733907
    Unknown6 = 3147590725
    Unknown7 = 580206079
    Unknown8 = 1435635049
    Unknown9 = 3308065016
    Unknown10 = 2989105262

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
class AreaStreamedAudioState(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    area_state: AreaState = dataclasses.field(default=AreaState.Unknown1, metadata={
        'reflection': FieldReflection[AreaState](
            AreaState, id=0xe7d8d823, original_name='AreaState', from_json=AreaState.from_json, to_json=AreaState.to_json
        ),
    })
    auto_set: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x05c9246c, original_name='AutoSet'
        ),
    })
    global_: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2409b906, original_name='Global'
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
        return 'ASAS'

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
        assert property_id == 0xe7d8d823
        area_state = AreaState.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x05c9246c
        auto_set = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2409b906
        global_ = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, area_state, auto_set, global_)

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

        data.write(b'\xe7\xd8\xd8#')  # 0xe7d8d823
        data.write(b'\x00\x04')  # size
        self.area_state.to_stream(data)

        data.write(b'\x05\xc9$l')  # 0x5c9246c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.auto_set))

        data.write(b'$\t\xb9\x06')  # 0x2409b906
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.global_))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AreaStreamedAudioStateJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            area_state=AreaState.from_json(json_data['area_state']),
            auto_set=json_data['auto_set'],
            global_=json_data['global_'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'area_state': self.area_state.to_json(),
            'auto_set': self.auto_set,
            'global_': self.global_,
        }


def _decode_area_state(data: typing.BinaryIO, property_size: int) -> AreaState:
    return AreaState.from_stream(data)


def _decode_auto_set(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_global_(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xe7d8d823: ('area_state', _decode_area_state),
    0x5c9246c: ('auto_set', _decode_auto_set),
    0x2409b906: ('global_', _decode_global_),
}
