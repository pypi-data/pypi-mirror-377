# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.OffsetInterpolant import OffsetInterpolant

if typing.TYPE_CHECKING:
    class OffsetPositionJson(typing_extensions.TypedDict):
        offset_type: int
        offset: json_util.JsonObject
    

class OffsetType(enum.IntEnum):
    Unknown1 = 2512106878
    Unknown2 = 142006047
    Unknown3 = 3952570983
    Unknown4 = 3725467126
    Unknown5 = 1409063055

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
class OffsetPosition(BaseProperty):
    offset_type: OffsetType = dataclasses.field(default=OffsetType.Unknown1, metadata={
        'reflection': FieldReflection[OffsetType](
            OffsetType, id=0x70c78c3e, original_name='OffsetType', from_json=OffsetType.from_json, to_json=OffsetType.to_json
        ),
    })
    offset: OffsetInterpolant = dataclasses.field(default_factory=OffsetInterpolant, metadata={
        'reflection': FieldReflection[OffsetInterpolant](
            OffsetInterpolant, id=0x3769a209, original_name='Offset', from_json=OffsetInterpolant.from_json, to_json=OffsetInterpolant.to_json
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
        if property_count != 2:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x70c78c3e
        offset_type = OffsetType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3769a209
        offset = OffsetInterpolant.from_stream(data, property_size)
    
        return cls(offset_type, offset)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'p\xc7\x8c>')  # 0x70c78c3e
        data.write(b'\x00\x04')  # size
        self.offset_type.to_stream(data)

        data.write(b'7i\xa2\t')  # 0x3769a209
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.offset.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("OffsetPositionJson", data)
        return cls(
            offset_type=OffsetType.from_json(json_data['offset_type']),
            offset=OffsetInterpolant.from_json(json_data['offset']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'offset_type': self.offset_type.to_json(),
            'offset': self.offset.to_json(),
        }


def _decode_offset_type(data: typing.BinaryIO, property_size: int) -> OffsetType:
    return OffsetType.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x70c78c3e: ('offset_type', _decode_offset_type),
    0x3769a209: ('offset', OffsetInterpolant.from_stream),
}
