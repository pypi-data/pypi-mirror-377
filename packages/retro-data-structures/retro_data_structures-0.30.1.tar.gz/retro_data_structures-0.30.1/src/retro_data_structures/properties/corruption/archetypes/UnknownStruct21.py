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

if typing.TYPE_CHECKING:
    class UnknownStruct21Json(typing_extensions.TypedDict):
        difficulty: int
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x2b082c6d)


@dataclasses.dataclass()
class UnknownStruct21(BaseProperty):
    difficulty: enums.BerserkerEnumEnum = dataclasses.field(default=enums.BerserkerEnumEnum.Unknown4, metadata={
        'reflection': FieldReflection[enums.BerserkerEnumEnum](
            enums.BerserkerEnumEnum, id=0x2b082c6d, original_name='Difficulty', from_json=enums.BerserkerEnumEnum.from_json, to_json=enums.BerserkerEnumEnum.to_json
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
            enums.BerserkerEnumEnum(dec[2]),
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x01')  # 1 properties

        data.write(b'+\x08,m')  # 0x2b082c6d
        data.write(b'\x00\x04')  # size
        self.difficulty.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct21Json", data)
        return cls(
            difficulty=enums.BerserkerEnumEnum.from_json(json_data['difficulty']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'difficulty': self.difficulty.to_json(),
        }


def _decode_difficulty(data: typing.BinaryIO, property_size: int) -> enums.BerserkerEnumEnum:
    return enums.BerserkerEnumEnum.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x2b082c6d: ('difficulty', _decode_difficulty),
}
