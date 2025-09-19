# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
import retro_data_structures.enums.corruption as enums
from retro_data_structures.properties.corruption.archetypes.RevolutionControl_UnknownStruct2 import RevolutionControl_UnknownStruct2
from retro_data_structures.properties.corruption.archetypes.RevolutionControl_UnknownStruct3 import RevolutionControl_UnknownStruct3
from retro_data_structures.properties.corruption.archetypes.RevolutionControl_UnknownStruct4 import RevolutionControl_UnknownStruct4

if typing.TYPE_CHECKING:
    class RevolutionControl_UnknownStruct1Json(typing_extensions.TypedDict):
        unknown_0xe1c76bfb: int
        unknown_0x3d8010c2: json_util.JsonObject
        unknown_0x9e8e5bf9: json_util.JsonObject
        unknown_0x6d33ae8f: json_util.JsonObject
    

@dataclasses.dataclass()
class RevolutionControl_UnknownStruct1(BaseProperty):
    unknown_0xe1c76bfb: enums.RevolutionControl_UnknownEnum2Enum = dataclasses.field(default=enums.RevolutionControl_UnknownEnum2Enum.Unknown1, metadata={
        'reflection': FieldReflection[enums.RevolutionControl_UnknownEnum2Enum](
            enums.RevolutionControl_UnknownEnum2Enum, id=0xe1c76bfb, original_name='Unknown', from_json=enums.RevolutionControl_UnknownEnum2Enum.from_json, to_json=enums.RevolutionControl_UnknownEnum2Enum.to_json
        ),
    })
    unknown_0x3d8010c2: RevolutionControl_UnknownStruct2 = dataclasses.field(default_factory=RevolutionControl_UnknownStruct2, metadata={
        'reflection': FieldReflection[RevolutionControl_UnknownStruct2](
            RevolutionControl_UnknownStruct2, id=0x3d8010c2, original_name='Unknown', from_json=RevolutionControl_UnknownStruct2.from_json, to_json=RevolutionControl_UnknownStruct2.to_json
        ),
    })
    unknown_0x9e8e5bf9: RevolutionControl_UnknownStruct3 = dataclasses.field(default_factory=RevolutionControl_UnknownStruct3, metadata={
        'reflection': FieldReflection[RevolutionControl_UnknownStruct3](
            RevolutionControl_UnknownStruct3, id=0x9e8e5bf9, original_name='Unknown', from_json=RevolutionControl_UnknownStruct3.from_json, to_json=RevolutionControl_UnknownStruct3.to_json
        ),
    })
    unknown_0x6d33ae8f: RevolutionControl_UnknownStruct4 = dataclasses.field(default_factory=RevolutionControl_UnknownStruct4, metadata={
        'reflection': FieldReflection[RevolutionControl_UnknownStruct4](
            RevolutionControl_UnknownStruct4, id=0x6d33ae8f, original_name='Unknown', from_json=RevolutionControl_UnknownStruct4.from_json, to_json=RevolutionControl_UnknownStruct4.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
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

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 4:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe1c76bfb
        unknown_0xe1c76bfb = enums.RevolutionControl_UnknownEnum2Enum.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d8010c2
        unknown_0x3d8010c2 = RevolutionControl_UnknownStruct2.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9e8e5bf9
        unknown_0x9e8e5bf9 = RevolutionControl_UnknownStruct3.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d33ae8f
        unknown_0x6d33ae8f = RevolutionControl_UnknownStruct4.from_stream(data, property_size)
    
        return cls(unknown_0xe1c76bfb, unknown_0x3d8010c2, unknown_0x9e8e5bf9, unknown_0x6d33ae8f)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'\xe1\xc7k\xfb')  # 0xe1c76bfb
        data.write(b'\x00\x04')  # size
        self.unknown_0xe1c76bfb.to_stream(data)

        data.write(b'=\x80\x10\xc2')  # 0x3d8010c2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x3d8010c2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9e\x8e[\xf9')  # 0x9e8e5bf9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x9e8e5bf9.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'm3\xae\x8f')  # 0x6d33ae8f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x6d33ae8f.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RevolutionControl_UnknownStruct1Json", data)
        return cls(
            unknown_0xe1c76bfb=enums.RevolutionControl_UnknownEnum2Enum.from_json(json_data['unknown_0xe1c76bfb']),
            unknown_0x3d8010c2=RevolutionControl_UnknownStruct2.from_json(json_data['unknown_0x3d8010c2']),
            unknown_0x9e8e5bf9=RevolutionControl_UnknownStruct3.from_json(json_data['unknown_0x9e8e5bf9']),
            unknown_0x6d33ae8f=RevolutionControl_UnknownStruct4.from_json(json_data['unknown_0x6d33ae8f']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xe1c76bfb': self.unknown_0xe1c76bfb.to_json(),
            'unknown_0x3d8010c2': self.unknown_0x3d8010c2.to_json(),
            'unknown_0x9e8e5bf9': self.unknown_0x9e8e5bf9.to_json(),
            'unknown_0x6d33ae8f': self.unknown_0x6d33ae8f.to_json(),
        }


def _decode_unknown_0xe1c76bfb(data: typing.BinaryIO, property_size: int) -> enums.RevolutionControl_UnknownEnum2Enum:
    return enums.RevolutionControl_UnknownEnum2Enum.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xe1c76bfb: ('unknown_0xe1c76bfb', _decode_unknown_0xe1c76bfb),
    0x3d8010c2: ('unknown_0x3d8010c2', RevolutionControl_UnknownStruct2.from_stream),
    0x9e8e5bf9: ('unknown_0x9e8e5bf9', RevolutionControl_UnknownStruct3.from_stream),
    0x6d33ae8f: ('unknown_0x6d33ae8f', RevolutionControl_UnknownStruct4.from_stream),
}
