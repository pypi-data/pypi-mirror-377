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
    class TweakPlayer_ShieldJson(typing_extensions.TypedDict):
        max_energy: float
        usage_rate: float
        recharge_rate: float
        allows_motion: bool
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xd42fa1c1, 0x787855e6, 0x5dadd6ab, 0x59efbb34)


@dataclasses.dataclass()
class TweakPlayer_Shield(BaseProperty):
    max_energy: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd42fa1c1, original_name='MaxEnergy'
        ),
    })
    usage_rate: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x787855e6, original_name='UsageRate'
        ),
    })
    recharge_rate: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5dadd6ab, original_name='RechargeRate'
        ),
    })
    allows_motion: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x59efbb34, original_name='AllowsMotion'
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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLH?')
    
        dec = _FAST_FORMAT.unpack(data.read(37))
        assert (dec[0], dec[3], dec[6], dec[9]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'\xd4/\xa1\xc1')  # 0xd42fa1c1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_energy))

        data.write(b'xxU\xe6')  # 0x787855e6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.usage_rate))

        data.write(b']\xad\xd6\xab')  # 0x5dadd6ab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.recharge_rate))

        data.write(b'Y\xef\xbb4')  # 0x59efbb34
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.allows_motion))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayer_ShieldJson", data)
        return cls(
            max_energy=json_data['max_energy'],
            usage_rate=json_data['usage_rate'],
            recharge_rate=json_data['recharge_rate'],
            allows_motion=json_data['allows_motion'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'max_energy': self.max_energy,
            'usage_rate': self.usage_rate,
            'recharge_rate': self.recharge_rate,
            'allows_motion': self.allows_motion,
        }


def _decode_max_energy(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_usage_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_recharge_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_allows_motion(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xd42fa1c1: ('max_energy', _decode_max_energy),
    0x787855e6: ('usage_rate', _decode_usage_rate),
    0x5dadd6ab: ('recharge_rate', _decode_recharge_rate),
    0x59efbb34: ('allows_motion', _decode_allows_motion),
}
