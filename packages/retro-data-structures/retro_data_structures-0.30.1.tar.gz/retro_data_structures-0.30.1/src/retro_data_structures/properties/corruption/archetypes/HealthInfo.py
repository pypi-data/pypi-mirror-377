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

if typing.TYPE_CHECKING:
    class HealthInfoJson(typing_extensions.TypedDict):
        health: float
        hi_knock_back_resistance: float
        adjust_for_difficulty: bool
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xf0668919, 0x3a2d17e4, 0xefe9e465)


@dataclasses.dataclass()
class HealthInfo(BaseProperty):
    health: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf0668919, original_name='Health'
        ),
    })
    hi_knock_back_resistance: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3a2d17e4, original_name='HI_KnockBackResistance'
        ),
    })
    adjust_for_difficulty: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xefe9e465, original_name='AdjustForDifficulty'
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
        if property_count != 3:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLH?')
    
        dec = _FAST_FORMAT.unpack(data.read(27))
        assert (dec[0], dec[3], dec[6]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\xf0f\x89\x19')  # 0xf0668919
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.health))

        data.write(b':-\x17\xe4')  # 0x3a2d17e4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hi_knock_back_resistance))

        data.write(b'\xef\xe9\xe4e')  # 0xefe9e465
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.adjust_for_difficulty))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("HealthInfoJson", data)
        return cls(
            health=json_data['health'],
            hi_knock_back_resistance=json_data['hi_knock_back_resistance'],
            adjust_for_difficulty=json_data['adjust_for_difficulty'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'health': self.health,
            'hi_knock_back_resistance': self.hi_knock_back_resistance,
            'adjust_for_difficulty': self.adjust_for_difficulty,
        }


def _decode_health(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hi_knock_back_resistance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_adjust_for_difficulty(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xf0668919: ('health', _decode_health),
    0x3a2d17e4: ('hi_knock_back_resistance', _decode_hi_knock_back_resistance),
    0xefe9e465: ('adjust_for_difficulty', _decode_adjust_for_difficulty),
}
