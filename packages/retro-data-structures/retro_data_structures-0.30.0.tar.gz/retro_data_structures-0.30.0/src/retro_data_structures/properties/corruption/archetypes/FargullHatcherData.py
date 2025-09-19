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
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability

if typing.TYPE_CHECKING:
    class FargullHatcherDataJson(typing_extensions.TypedDict):
        is_crouching: bool
        attack_range: float
        min_hatch_time: float
        max_hatch_time: float
        sonic_pulse_vulnerability: json_util.JsonObject
        sonic_pulse_damage: json_util.JsonObject
        unknown_0xa5692479: float
        min_hatch_size: int
        min_taunt_time: float
        max_taunt_time: float
        taunt_probability: float
        unknown_0x248bc9f9: float
    

@dataclasses.dataclass()
class FargullHatcherData(BaseProperty):
    is_crouching: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0c36eb18, original_name='IsCrouching'
        ),
    })
    attack_range: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x39dac81e, original_name='AttackRange'
        ),
    })
    min_hatch_time: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe29543ef, original_name='MinHatchTime'
        ),
    })
    max_hatch_time: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf71e971d, original_name='MaxHatchTime'
        ),
    })
    sonic_pulse_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x537f9f4d, original_name='SonicPulseVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    sonic_pulse_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x2c746d2c, original_name='SonicPulseDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xa5692479: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa5692479, original_name='Unknown'
        ),
    })
    min_hatch_size: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9f7ca9d1, original_name='MinHatchSize'
        ),
    })
    min_taunt_time: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3718ea0, original_name='MinTauntTime'
        ),
    })
    max_taunt_time: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd6fa5a52, original_name='MaxTauntTime'
        ),
    })
    taunt_probability: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfcdcaa4e, original_name='TauntProbability'
        ),
    })
    unknown_0x248bc9f9: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x248bc9f9, original_name='Unknown'
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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0c36eb18
        is_crouching = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x39dac81e
        attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe29543ef
        min_hatch_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf71e971d
        max_hatch_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x537f9f4d
        sonic_pulse_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c746d2c
        sonic_pulse_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa5692479
        unknown_0xa5692479 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f7ca9d1
        min_hatch_size = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3718ea0
        min_taunt_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd6fa5a52
        max_taunt_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfcdcaa4e
        taunt_probability = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x248bc9f9
        unknown_0x248bc9f9 = struct.unpack('>f', data.read(4))[0]
    
        return cls(is_crouching, attack_range, min_hatch_time, max_hatch_time, sonic_pulse_vulnerability, sonic_pulse_damage, unknown_0xa5692479, min_hatch_size, min_taunt_time, max_taunt_time, taunt_probability, unknown_0x248bc9f9)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'\x0c6\xeb\x18')  # 0xc36eb18
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_crouching))

        data.write(b'9\xda\xc8\x1e')  # 0x39dac81e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_range))

        data.write(b'\xe2\x95C\xef')  # 0xe29543ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_hatch_time))

        data.write(b'\xf7\x1e\x97\x1d')  # 0xf71e971d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_hatch_time))

        data.write(b'S\x7f\x9fM')  # 0x537f9f4d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sonic_pulse_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b',tm,')  # 0x2c746d2c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sonic_pulse_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa5i$y')  # 0xa5692479
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa5692479))

        data.write(b'\x9f|\xa9\xd1')  # 0x9f7ca9d1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.min_hatch_size))

        data.write(b'\xc3q\x8e\xa0')  # 0xc3718ea0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_taunt_time))

        data.write(b'\xd6\xfaZR')  # 0xd6fa5a52
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_taunt_time))

        data.write(b'\xfc\xdc\xaaN')  # 0xfcdcaa4e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.taunt_probability))

        data.write(b'$\x8b\xc9\xf9')  # 0x248bc9f9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x248bc9f9))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("FargullHatcherDataJson", data)
        return cls(
            is_crouching=json_data['is_crouching'],
            attack_range=json_data['attack_range'],
            min_hatch_time=json_data['min_hatch_time'],
            max_hatch_time=json_data['max_hatch_time'],
            sonic_pulse_vulnerability=DamageVulnerability.from_json(json_data['sonic_pulse_vulnerability']),
            sonic_pulse_damage=DamageInfo.from_json(json_data['sonic_pulse_damage']),
            unknown_0xa5692479=json_data['unknown_0xa5692479'],
            min_hatch_size=json_data['min_hatch_size'],
            min_taunt_time=json_data['min_taunt_time'],
            max_taunt_time=json_data['max_taunt_time'],
            taunt_probability=json_data['taunt_probability'],
            unknown_0x248bc9f9=json_data['unknown_0x248bc9f9'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'is_crouching': self.is_crouching,
            'attack_range': self.attack_range,
            'min_hatch_time': self.min_hatch_time,
            'max_hatch_time': self.max_hatch_time,
            'sonic_pulse_vulnerability': self.sonic_pulse_vulnerability.to_json(),
            'sonic_pulse_damage': self.sonic_pulse_damage.to_json(),
            'unknown_0xa5692479': self.unknown_0xa5692479,
            'min_hatch_size': self.min_hatch_size,
            'min_taunt_time': self.min_taunt_time,
            'max_taunt_time': self.max_taunt_time,
            'taunt_probability': self.taunt_probability,
            'unknown_0x248bc9f9': self.unknown_0x248bc9f9,
        }


def _decode_is_crouching(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_hatch_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_hatch_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa5692479(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_hatch_size(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_min_taunt_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_taunt_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_taunt_probability(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x248bc9f9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc36eb18: ('is_crouching', _decode_is_crouching),
    0x39dac81e: ('attack_range', _decode_attack_range),
    0xe29543ef: ('min_hatch_time', _decode_min_hatch_time),
    0xf71e971d: ('max_hatch_time', _decode_max_hatch_time),
    0x537f9f4d: ('sonic_pulse_vulnerability', DamageVulnerability.from_stream),
    0x2c746d2c: ('sonic_pulse_damage', DamageInfo.from_stream),
    0xa5692479: ('unknown_0xa5692479', _decode_unknown_0xa5692479),
    0x9f7ca9d1: ('min_hatch_size', _decode_min_hatch_size),
    0xc3718ea0: ('min_taunt_time', _decode_min_taunt_time),
    0xd6fa5a52: ('max_taunt_time', _decode_max_taunt_time),
    0xfcdcaa4e: ('taunt_probability', _decode_taunt_probability),
    0x248bc9f9: ('unknown_0x248bc9f9', _decode_unknown_0x248bc9f9),
}
