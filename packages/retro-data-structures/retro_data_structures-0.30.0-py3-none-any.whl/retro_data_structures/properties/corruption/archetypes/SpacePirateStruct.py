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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class SpacePirateStructJson(typing_extensions.TypedDict):
        enable_hyper_mode: bool
        initial_hyper_mode_time: float
        hyper_mode_check_time: float
        hyper_mode_check_chance: float
        hyper_mode_duration: float
        skip_taunt: bool
        unknown_0xdb922374: bool
        shot_projectile: int
        sound_projectile: int
        shot_damage: json_util.JsonObject
        unknown_0x71587b45: float
        unknown_0x7903312e: float
        hyper_mode_attack_time: float
        unknown_0xca686731: float
        hyper_mode_vulnerability: json_util.JsonObject
    

@dataclasses.dataclass()
class SpacePirateStruct(BaseProperty):
    enable_hyper_mode: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xdd448cc9, original_name='EnableHyperMode'
        ),
    })
    initial_hyper_mode_time: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8a834618, original_name='InitialHyperModeTime'
        ),
    })
    hyper_mode_check_time: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe9fd5a01, original_name='HyperModeCheckTime'
        ),
    })
    hyper_mode_check_chance: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf04452f3, original_name='HyperModeCheckChance'
        ),
    })
    hyper_mode_duration: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa3f3be5d, original_name='HyperModeDuration'
        ),
    })
    skip_taunt: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x071d8999, original_name='SkipTaunt'
        ),
    })
    unknown_0xdb922374: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xdb922374, original_name='Unknown'
        ),
    })
    shot_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x51253ba3, original_name='ShotProjectile'
        ),
    })
    sound_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x10e3efdd, original_name='Sound_Projectile'
        ),
    })
    shot_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xcea30138, original_name='ShotDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x71587b45: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x71587b45, original_name='Unknown'
        ),
    })
    unknown_0x7903312e: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7903312e, original_name='Unknown'
        ),
    })
    hyper_mode_attack_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe9b7d4ee, original_name='HyperModeAttackTime'
        ),
    })
    unknown_0xca686731: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xca686731, original_name='Unknown'
        ),
    })
    hyper_mode_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xc8a1eac8, original_name='HyperModeVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
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
        if property_count != 15:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd448cc9
        enable_hyper_mode = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a834618
        initial_hyper_mode_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9fd5a01
        hyper_mode_check_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf04452f3
        hyper_mode_check_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa3f3be5d
        hyper_mode_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x071d8999
        skip_taunt = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdb922374
        unknown_0xdb922374 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x51253ba3
        shot_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x10e3efdd
        sound_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcea30138
        shot_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71587b45
        unknown_0x71587b45 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7903312e
        unknown_0x7903312e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9b7d4ee
        hyper_mode_attack_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xca686731
        unknown_0xca686731 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8a1eac8
        hyper_mode_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        return cls(enable_hyper_mode, initial_hyper_mode_time, hyper_mode_check_time, hyper_mode_check_chance, hyper_mode_duration, skip_taunt, unknown_0xdb922374, shot_projectile, sound_projectile, shot_damage, unknown_0x71587b45, unknown_0x7903312e, hyper_mode_attack_time, unknown_0xca686731, hyper_mode_vulnerability)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0f')  # 15 properties

        data.write(b'\xddD\x8c\xc9')  # 0xdd448cc9
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.enable_hyper_mode))

        data.write(b'\x8a\x83F\x18')  # 0x8a834618
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.initial_hyper_mode_time))

        data.write(b'\xe9\xfdZ\x01')  # 0xe9fd5a01
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hyper_mode_check_time))

        data.write(b'\xf0DR\xf3')  # 0xf04452f3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hyper_mode_check_chance))

        data.write(b'\xa3\xf3\xbe]')  # 0xa3f3be5d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hyper_mode_duration))

        data.write(b'\x07\x1d\x89\x99')  # 0x71d8999
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.skip_taunt))

        data.write(b'\xdb\x92#t')  # 0xdb922374
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xdb922374))

        data.write(b'Q%;\xa3')  # 0x51253ba3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.shot_projectile))

        data.write(b'\x10\xe3\xef\xdd')  # 0x10e3efdd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_projectile))

        data.write(b'\xce\xa3\x018')  # 0xcea30138
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shot_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'qX{E')  # 0x71587b45
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x71587b45))

        data.write(b'y\x031.')  # 0x7903312e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7903312e))

        data.write(b'\xe9\xb7\xd4\xee')  # 0xe9b7d4ee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hyper_mode_attack_time))

        data.write(b'\xcahg1')  # 0xca686731
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xca686731))

        data.write(b'\xc8\xa1\xea\xc8')  # 0xc8a1eac8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_mode_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpacePirateStructJson", data)
        return cls(
            enable_hyper_mode=json_data['enable_hyper_mode'],
            initial_hyper_mode_time=json_data['initial_hyper_mode_time'],
            hyper_mode_check_time=json_data['hyper_mode_check_time'],
            hyper_mode_check_chance=json_data['hyper_mode_check_chance'],
            hyper_mode_duration=json_data['hyper_mode_duration'],
            skip_taunt=json_data['skip_taunt'],
            unknown_0xdb922374=json_data['unknown_0xdb922374'],
            shot_projectile=json_data['shot_projectile'],
            sound_projectile=json_data['sound_projectile'],
            shot_damage=DamageInfo.from_json(json_data['shot_damage']),
            unknown_0x71587b45=json_data['unknown_0x71587b45'],
            unknown_0x7903312e=json_data['unknown_0x7903312e'],
            hyper_mode_attack_time=json_data['hyper_mode_attack_time'],
            unknown_0xca686731=json_data['unknown_0xca686731'],
            hyper_mode_vulnerability=DamageVulnerability.from_json(json_data['hyper_mode_vulnerability']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'enable_hyper_mode': self.enable_hyper_mode,
            'initial_hyper_mode_time': self.initial_hyper_mode_time,
            'hyper_mode_check_time': self.hyper_mode_check_time,
            'hyper_mode_check_chance': self.hyper_mode_check_chance,
            'hyper_mode_duration': self.hyper_mode_duration,
            'skip_taunt': self.skip_taunt,
            'unknown_0xdb922374': self.unknown_0xdb922374,
            'shot_projectile': self.shot_projectile,
            'sound_projectile': self.sound_projectile,
            'shot_damage': self.shot_damage.to_json(),
            'unknown_0x71587b45': self.unknown_0x71587b45,
            'unknown_0x7903312e': self.unknown_0x7903312e,
            'hyper_mode_attack_time': self.hyper_mode_attack_time,
            'unknown_0xca686731': self.unknown_0xca686731,
            'hyper_mode_vulnerability': self.hyper_mode_vulnerability.to_json(),
        }


def _decode_enable_hyper_mode(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_initial_hyper_mode_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hyper_mode_check_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hyper_mode_check_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hyper_mode_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_skip_taunt(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xdb922374(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_shot_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x71587b45(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7903312e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hyper_mode_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xca686731(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xdd448cc9: ('enable_hyper_mode', _decode_enable_hyper_mode),
    0x8a834618: ('initial_hyper_mode_time', _decode_initial_hyper_mode_time),
    0xe9fd5a01: ('hyper_mode_check_time', _decode_hyper_mode_check_time),
    0xf04452f3: ('hyper_mode_check_chance', _decode_hyper_mode_check_chance),
    0xa3f3be5d: ('hyper_mode_duration', _decode_hyper_mode_duration),
    0x71d8999: ('skip_taunt', _decode_skip_taunt),
    0xdb922374: ('unknown_0xdb922374', _decode_unknown_0xdb922374),
    0x51253ba3: ('shot_projectile', _decode_shot_projectile),
    0x10e3efdd: ('sound_projectile', _decode_sound_projectile),
    0xcea30138: ('shot_damage', DamageInfo.from_stream),
    0x71587b45: ('unknown_0x71587b45', _decode_unknown_0x71587b45),
    0x7903312e: ('unknown_0x7903312e', _decode_unknown_0x7903312e),
    0xe9b7d4ee: ('hyper_mode_attack_time', _decode_hyper_mode_attack_time),
    0xca686731: ('unknown_0xca686731', _decode_unknown_0xca686731),
    0xc8a1eac8: ('hyper_mode_vulnerability', DamageVulnerability.from_stream),
}
