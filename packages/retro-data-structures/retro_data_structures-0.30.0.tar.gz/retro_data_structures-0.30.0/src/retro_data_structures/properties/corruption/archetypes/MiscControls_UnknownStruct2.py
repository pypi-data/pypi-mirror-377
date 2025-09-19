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
from retro_data_structures.properties.corruption.archetypes.RevolutionControl import RevolutionControl

if typing.TYPE_CHECKING:
    class MiscControls_UnknownStruct2Json(typing_extensions.TypedDict):
        unknown_0x67739b75: int
        unknown_0xa5e20450: json_util.JsonObject
        unknown_0xa74987ff: json_util.JsonObject
        unknown_0x73eb9d04: json_util.JsonObject
    

@dataclasses.dataclass()
class MiscControls_UnknownStruct2(BaseProperty):
    unknown_0x67739b75: enums.MiscControls_UnknownEnum1Enum = dataclasses.field(default=enums.MiscControls_UnknownEnum1Enum.Unknown1, metadata={
        'reflection': FieldReflection[enums.MiscControls_UnknownEnum1Enum](
            enums.MiscControls_UnknownEnum1Enum, id=0x67739b75, original_name='Unknown', from_json=enums.MiscControls_UnknownEnum1Enum.from_json, to_json=enums.MiscControls_UnknownEnum1Enum.to_json
        ),
    })
    unknown_0xa5e20450: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xa5e20450, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xa74987ff: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xa74987ff, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0x73eb9d04: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x73eb9d04, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
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
        assert property_id == 0x67739b75
        unknown_0x67739b75 = enums.MiscControls_UnknownEnum1Enum.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa5e20450
        unknown_0xa5e20450 = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa74987ff
        unknown_0xa74987ff = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x73eb9d04
        unknown_0x73eb9d04 = RevolutionControl.from_stream(data, property_size)
    
        return cls(unknown_0x67739b75, unknown_0xa5e20450, unknown_0xa74987ff, unknown_0x73eb9d04)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'gs\x9bu')  # 0x67739b75
        data.write(b'\x00\x04')  # size
        self.unknown_0x67739b75.to_stream(data)

        data.write(b'\xa5\xe2\x04P')  # 0xa5e20450
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xa5e20450.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa7I\x87\xff')  # 0xa74987ff
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xa74987ff.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b's\xeb\x9d\x04')  # 0x73eb9d04
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x73eb9d04.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MiscControls_UnknownStruct2Json", data)
        return cls(
            unknown_0x67739b75=enums.MiscControls_UnknownEnum1Enum.from_json(json_data['unknown_0x67739b75']),
            unknown_0xa5e20450=RevolutionControl.from_json(json_data['unknown_0xa5e20450']),
            unknown_0xa74987ff=RevolutionControl.from_json(json_data['unknown_0xa74987ff']),
            unknown_0x73eb9d04=RevolutionControl.from_json(json_data['unknown_0x73eb9d04']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x67739b75': self.unknown_0x67739b75.to_json(),
            'unknown_0xa5e20450': self.unknown_0xa5e20450.to_json(),
            'unknown_0xa74987ff': self.unknown_0xa74987ff.to_json(),
            'unknown_0x73eb9d04': self.unknown_0x73eb9d04.to_json(),
        }


def _decode_unknown_0x67739b75(data: typing.BinaryIO, property_size: int) -> enums.MiscControls_UnknownEnum1Enum:
    return enums.MiscControls_UnknownEnum1Enum.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x67739b75: ('unknown_0x67739b75', _decode_unknown_0x67739b75),
    0xa5e20450: ('unknown_0xa5e20450', RevolutionControl.from_stream),
    0xa74987ff: ('unknown_0xa74987ff', RevolutionControl.from_stream),
    0x73eb9d04: ('unknown_0x73eb9d04', RevolutionControl.from_stream),
}
