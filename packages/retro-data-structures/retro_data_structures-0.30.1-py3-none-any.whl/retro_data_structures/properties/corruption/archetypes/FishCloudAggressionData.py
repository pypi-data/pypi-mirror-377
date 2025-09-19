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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class FishCloudAggressionDataJson(typing_extensions.TypedDict):
        attack_distance: float
        attack_cone: float
        attack_priority: float
        attack_kill_time: float
        attack_effect: int
        attack_effect_count: int
        attack_effect_scale: float
        attack_effect_rate: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x5eda8d99, 0xe387d414, 0x8d1cf97a, 0x4e815e64, 0xb258d3e8, 0x39e08c8e, 0x34d4321c, 0x2459fc0a)


@dataclasses.dataclass()
class FishCloudAggressionData(BaseProperty):
    attack_distance: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5eda8d99, original_name='AttackDistance'
        ),
    })
    attack_cone: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe387d414, original_name='AttackCone'
        ),
    })
    attack_priority: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8d1cf97a, original_name='AttackPriority'
        ),
    })
    attack_kill_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4e815e64, original_name='AttackKillTime'
        ),
    })
    attack_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb258d3e8, original_name='AttackEffect'
        ),
    })
    attack_effect_count: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x39e08c8e, original_name='AttackEffectCount'
        ),
    })
    attack_effect_scale: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x34d4321c, original_name='AttackEffectScale'
        ),
    })
    attack_effect_rate: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2459fc0a, original_name='AttackEffectRate'
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
        if property_count != 8:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHQLHlLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(84))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
            dec[23],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'^\xda\x8d\x99')  # 0x5eda8d99
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_distance))

        data.write(b'\xe3\x87\xd4\x14')  # 0xe387d414
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_cone))

        data.write(b'\x8d\x1c\xf9z')  # 0x8d1cf97a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_priority))

        data.write(b'N\x81^d')  # 0x4e815e64
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_kill_time))

        data.write(b'\xb2X\xd3\xe8')  # 0xb258d3e8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.attack_effect))

        data.write(b'9\xe0\x8c\x8e')  # 0x39e08c8e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.attack_effect_count))

        data.write(b'4\xd42\x1c')  # 0x34d4321c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_effect_scale))

        data.write(b'$Y\xfc\n')  # 0x2459fc0a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_effect_rate))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("FishCloudAggressionDataJson", data)
        return cls(
            attack_distance=json_data['attack_distance'],
            attack_cone=json_data['attack_cone'],
            attack_priority=json_data['attack_priority'],
            attack_kill_time=json_data['attack_kill_time'],
            attack_effect=json_data['attack_effect'],
            attack_effect_count=json_data['attack_effect_count'],
            attack_effect_scale=json_data['attack_effect_scale'],
            attack_effect_rate=json_data['attack_effect_rate'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'attack_distance': self.attack_distance,
            'attack_cone': self.attack_cone,
            'attack_priority': self.attack_priority,
            'attack_kill_time': self.attack_kill_time,
            'attack_effect': self.attack_effect,
            'attack_effect_count': self.attack_effect_count,
            'attack_effect_scale': self.attack_effect_scale,
            'attack_effect_rate': self.attack_effect_rate,
        }


def _decode_attack_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_cone(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_kill_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_attack_effect_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_attack_effect_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_effect_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x5eda8d99: ('attack_distance', _decode_attack_distance),
    0xe387d414: ('attack_cone', _decode_attack_cone),
    0x8d1cf97a: ('attack_priority', _decode_attack_priority),
    0x4e815e64: ('attack_kill_time', _decode_attack_kill_time),
    0xb258d3e8: ('attack_effect', _decode_attack_effect),
    0x39e08c8e: ('attack_effect_count', _decode_attack_effect_count),
    0x34d4321c: ('attack_effect_scale', _decode_attack_effect_scale),
    0x2459fc0a: ('attack_effect_rate', _decode_attack_effect_rate),
}
