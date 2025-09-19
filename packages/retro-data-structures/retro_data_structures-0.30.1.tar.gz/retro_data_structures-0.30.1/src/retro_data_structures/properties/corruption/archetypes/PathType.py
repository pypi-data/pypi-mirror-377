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

if typing.TYPE_CHECKING:
    class PathTypeJson(typing_extensions.TypedDict):
        curvature: int
    

class Curvature(enum.IntEnum):
    Unknown1 = 3115803663
    Unknown2 = 1176110616
    Unknown3 = 3253497337
    Unknown4 = 2350587168
    Unknown5 = 3709664811
    Unknown6 = 1108898616
    Unknown7 = 1705490000

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


_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xf4ac7caa)


@dataclasses.dataclass()
class PathType(BaseProperty):
    curvature: Curvature = dataclasses.field(default=Curvature.Unknown4, metadata={
        'reflection': FieldReflection[Curvature](
            Curvature, id=0xf4ac7caa, original_name='Curvature', from_json=Curvature.from_json, to_json=Curvature.to_json
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
        if property_count != 1:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHL')
    
        dec = _FAST_FORMAT.unpack(data.read(10))
        assert (dec[0]) == _FAST_IDS
        return cls(
            Curvature(dec[2]),
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x01')  # 1 properties

        data.write(b'\xf4\xac|\xaa')  # 0xf4ac7caa
        data.write(b'\x00\x04')  # size
        self.curvature.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PathTypeJson", data)
        return cls(
            curvature=Curvature.from_json(json_data['curvature']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'curvature': self.curvature.to_json(),
        }


def _decode_curvature(data: typing.BinaryIO, property_size: int) -> Curvature:
    return Curvature.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xf4ac7caa: ('curvature', _decode_curvature),
}
