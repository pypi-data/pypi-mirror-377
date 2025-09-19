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
from retro_data_structures.properties.corruption.archetypes.PlasmaBeamInfo import PlasmaBeamInfo
from retro_data_structures.properties.corruption.archetypes.UnknownStruct56 import UnknownStruct56
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct57Json(typing_extensions.TypedDict):
        samus_gun_model: int
        min_roll_time: float
        max_roll_time: float
        min_attack_time: float
        max_attack_time: float
        min_attack_distance: float
        max_attack_distance: float
        unknown_0xce471a01: float
        attack_turn_threshold: float
        unknown_0x4113ffd8: float
        beam_tracking_speed: float
        unknown_struct56: json_util.JsonObject
        beam_attack: json_util.JsonObject
        beam_attack_damage: json_util.JsonObject
        unknown_0xe32082d1: float
        unknown_0xb71164a2: float
        unknown_0x3dc59b72: float
        unknown_0xba9eb1d2: float
        unknown_0xf0397134: float
        unknown_0x5dae4176: float
        radial_melee_damage: json_util.JsonObject
        elsc: int
        unknown_0xe0c37dfa: float
    

@dataclasses.dataclass()
class UnknownStruct57(BaseProperty):
    samus_gun_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x216ed1ad, original_name='SamusGunModel'
        ),
    })
    min_roll_time: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb8baa8c0, original_name='MinRollTime'
        ),
    })
    max_roll_time: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe943139d, original_name='MaxRollTime'
        ),
    })
    min_attack_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2edf3368, original_name='MinAttackTime'
        ),
    })
    max_attack_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d792b8c, original_name='MaxAttackTime'
        ),
    })
    min_attack_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfb825eaa, original_name='MinAttackDistance'
        ),
    })
    max_attack_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xba95612c, original_name='MaxAttackDistance'
        ),
    })
    unknown_0xce471a01: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xce471a01, original_name='Unknown'
        ),
    })
    attack_turn_threshold: float = dataclasses.field(default=70.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaf2cb0a3, original_name='AttackTurnThreshold'
        ),
    })
    unknown_0x4113ffd8: float = dataclasses.field(default=0.6499999761581421, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4113ffd8, original_name='Unknown'
        ),
    })
    beam_tracking_speed: float = dataclasses.field(default=9.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2d8a9352, original_name='BeamTrackingSpeed'
        ),
    })
    unknown_struct56: UnknownStruct56 = dataclasses.field(default_factory=UnknownStruct56, metadata={
        'reflection': FieldReflection[UnknownStruct56](
            UnknownStruct56, id=0x84605259, original_name='UnknownStruct56', from_json=UnknownStruct56.from_json, to_json=UnknownStruct56.to_json
        ),
    })
    beam_attack: PlasmaBeamInfo = dataclasses.field(default_factory=PlasmaBeamInfo, metadata={
        'reflection': FieldReflection[PlasmaBeamInfo](
            PlasmaBeamInfo, id=0x889672f5, original_name='BeamAttack', from_json=PlasmaBeamInfo.from_json, to_json=PlasmaBeamInfo.to_json
        ),
    })
    beam_attack_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x202afaa4, original_name='BeamAttackDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xe32082d1: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe32082d1, original_name='Unknown'
        ),
    })
    unknown_0xb71164a2: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb71164a2, original_name='Unknown'
        ),
    })
    unknown_0x3dc59b72: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3dc59b72, original_name='Unknown'
        ),
    })
    unknown_0xba9eb1d2: float = dataclasses.field(default=72.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xba9eb1d2, original_name='Unknown'
        ),
    })
    unknown_0xf0397134: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf0397134, original_name='Unknown'
        ),
    })
    unknown_0x5dae4176: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5dae4176, original_name='Unknown'
        ),
    })
    radial_melee_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x5f11893b, original_name='RadialMeleeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    elsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf3fa9b62, original_name='ELSC'
        ),
    })
    unknown_0xe0c37dfa: float = dataclasses.field(default=14.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe0c37dfa, original_name='Unknown'
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
        if property_count != 23:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x216ed1ad
        samus_gun_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb8baa8c0
        min_roll_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe943139d
        max_roll_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2edf3368
        min_attack_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d792b8c
        max_attack_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfb825eaa
        min_attack_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba95612c
        max_attack_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce471a01
        unknown_0xce471a01 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaf2cb0a3
        attack_turn_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4113ffd8
        unknown_0x4113ffd8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2d8a9352
        beam_tracking_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84605259
        unknown_struct56 = UnknownStruct56.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x889672f5
        beam_attack = PlasmaBeamInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x202afaa4
        beam_attack_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe32082d1
        unknown_0xe32082d1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb71164a2
        unknown_0xb71164a2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3dc59b72
        unknown_0x3dc59b72 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba9eb1d2
        unknown_0xba9eb1d2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf0397134
        unknown_0xf0397134 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5dae4176
        unknown_0x5dae4176 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5f11893b
        radial_melee_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3fa9b62
        elsc = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0c37dfa
        unknown_0xe0c37dfa = struct.unpack('>f', data.read(4))[0]
    
        return cls(samus_gun_model, min_roll_time, max_roll_time, min_attack_time, max_attack_time, min_attack_distance, max_attack_distance, unknown_0xce471a01, attack_turn_threshold, unknown_0x4113ffd8, beam_tracking_speed, unknown_struct56, beam_attack, beam_attack_damage, unknown_0xe32082d1, unknown_0xb71164a2, unknown_0x3dc59b72, unknown_0xba9eb1d2, unknown_0xf0397134, unknown_0x5dae4176, radial_melee_damage, elsc, unknown_0xe0c37dfa)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x17')  # 23 properties

        data.write(b'!n\xd1\xad')  # 0x216ed1ad
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.samus_gun_model))

        data.write(b'\xb8\xba\xa8\xc0')  # 0xb8baa8c0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_roll_time))

        data.write(b'\xe9C\x13\x9d')  # 0xe943139d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_roll_time))

        data.write(b'.\xdf3h')  # 0x2edf3368
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_time))

        data.write(b'}y+\x8c')  # 0x7d792b8c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_time))

        data.write(b'\xfb\x82^\xaa')  # 0xfb825eaa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_distance))

        data.write(b'\xba\x95a,')  # 0xba95612c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_distance))

        data.write(b'\xceG\x1a\x01')  # 0xce471a01
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xce471a01))

        data.write(b'\xaf,\xb0\xa3')  # 0xaf2cb0a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_turn_threshold))

        data.write(b'A\x13\xff\xd8')  # 0x4113ffd8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4113ffd8))

        data.write(b'-\x8a\x93R')  # 0x2d8a9352
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.beam_tracking_speed))

        data.write(b'\x84`RY')  # 0x84605259
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct56.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x88\x96r\xf5')  # 0x889672f5
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_attack.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b' *\xfa\xa4')  # 0x202afaa4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_attack_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe3 \x82\xd1')  # 0xe32082d1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe32082d1))

        data.write(b'\xb7\x11d\xa2')  # 0xb71164a2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb71164a2))

        data.write(b'=\xc5\x9br')  # 0x3dc59b72
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3dc59b72))

        data.write(b'\xba\x9e\xb1\xd2')  # 0xba9eb1d2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xba9eb1d2))

        data.write(b'\xf09q4')  # 0xf0397134
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf0397134))

        data.write(b']\xaeAv')  # 0x5dae4176
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5dae4176))

        data.write(b'_\x11\x89;')  # 0x5f11893b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.radial_melee_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf3\xfa\x9bb')  # 0xf3fa9b62
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.elsc))

        data.write(b'\xe0\xc3}\xfa')  # 0xe0c37dfa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe0c37dfa))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct57Json", data)
        return cls(
            samus_gun_model=json_data['samus_gun_model'],
            min_roll_time=json_data['min_roll_time'],
            max_roll_time=json_data['max_roll_time'],
            min_attack_time=json_data['min_attack_time'],
            max_attack_time=json_data['max_attack_time'],
            min_attack_distance=json_data['min_attack_distance'],
            max_attack_distance=json_data['max_attack_distance'],
            unknown_0xce471a01=json_data['unknown_0xce471a01'],
            attack_turn_threshold=json_data['attack_turn_threshold'],
            unknown_0x4113ffd8=json_data['unknown_0x4113ffd8'],
            beam_tracking_speed=json_data['beam_tracking_speed'],
            unknown_struct56=UnknownStruct56.from_json(json_data['unknown_struct56']),
            beam_attack=PlasmaBeamInfo.from_json(json_data['beam_attack']),
            beam_attack_damage=DamageInfo.from_json(json_data['beam_attack_damage']),
            unknown_0xe32082d1=json_data['unknown_0xe32082d1'],
            unknown_0xb71164a2=json_data['unknown_0xb71164a2'],
            unknown_0x3dc59b72=json_data['unknown_0x3dc59b72'],
            unknown_0xba9eb1d2=json_data['unknown_0xba9eb1d2'],
            unknown_0xf0397134=json_data['unknown_0xf0397134'],
            unknown_0x5dae4176=json_data['unknown_0x5dae4176'],
            radial_melee_damage=DamageInfo.from_json(json_data['radial_melee_damage']),
            elsc=json_data['elsc'],
            unknown_0xe0c37dfa=json_data['unknown_0xe0c37dfa'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'samus_gun_model': self.samus_gun_model,
            'min_roll_time': self.min_roll_time,
            'max_roll_time': self.max_roll_time,
            'min_attack_time': self.min_attack_time,
            'max_attack_time': self.max_attack_time,
            'min_attack_distance': self.min_attack_distance,
            'max_attack_distance': self.max_attack_distance,
            'unknown_0xce471a01': self.unknown_0xce471a01,
            'attack_turn_threshold': self.attack_turn_threshold,
            'unknown_0x4113ffd8': self.unknown_0x4113ffd8,
            'beam_tracking_speed': self.beam_tracking_speed,
            'unknown_struct56': self.unknown_struct56.to_json(),
            'beam_attack': self.beam_attack.to_json(),
            'beam_attack_damage': self.beam_attack_damage.to_json(),
            'unknown_0xe32082d1': self.unknown_0xe32082d1,
            'unknown_0xb71164a2': self.unknown_0xb71164a2,
            'unknown_0x3dc59b72': self.unknown_0x3dc59b72,
            'unknown_0xba9eb1d2': self.unknown_0xba9eb1d2,
            'unknown_0xf0397134': self.unknown_0xf0397134,
            'unknown_0x5dae4176': self.unknown_0x5dae4176,
            'radial_melee_damage': self.radial_melee_damage.to_json(),
            'elsc': self.elsc,
            'unknown_0xe0c37dfa': self.unknown_0xe0c37dfa,
        }


def _decode_samus_gun_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_min_roll_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_roll_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attack_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xce471a01(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_turn_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4113ffd8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_beam_tracking_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe32082d1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb71164a2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3dc59b72(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xba9eb1d2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf0397134(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5dae4176(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_elsc(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xe0c37dfa(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x216ed1ad: ('samus_gun_model', _decode_samus_gun_model),
    0xb8baa8c0: ('min_roll_time', _decode_min_roll_time),
    0xe943139d: ('max_roll_time', _decode_max_roll_time),
    0x2edf3368: ('min_attack_time', _decode_min_attack_time),
    0x7d792b8c: ('max_attack_time', _decode_max_attack_time),
    0xfb825eaa: ('min_attack_distance', _decode_min_attack_distance),
    0xba95612c: ('max_attack_distance', _decode_max_attack_distance),
    0xce471a01: ('unknown_0xce471a01', _decode_unknown_0xce471a01),
    0xaf2cb0a3: ('attack_turn_threshold', _decode_attack_turn_threshold),
    0x4113ffd8: ('unknown_0x4113ffd8', _decode_unknown_0x4113ffd8),
    0x2d8a9352: ('beam_tracking_speed', _decode_beam_tracking_speed),
    0x84605259: ('unknown_struct56', UnknownStruct56.from_stream),
    0x889672f5: ('beam_attack', PlasmaBeamInfo.from_stream),
    0x202afaa4: ('beam_attack_damage', DamageInfo.from_stream),
    0xe32082d1: ('unknown_0xe32082d1', _decode_unknown_0xe32082d1),
    0xb71164a2: ('unknown_0xb71164a2', _decode_unknown_0xb71164a2),
    0x3dc59b72: ('unknown_0x3dc59b72', _decode_unknown_0x3dc59b72),
    0xba9eb1d2: ('unknown_0xba9eb1d2', _decode_unknown_0xba9eb1d2),
    0xf0397134: ('unknown_0xf0397134', _decode_unknown_0xf0397134),
    0x5dae4176: ('unknown_0x5dae4176', _decode_unknown_0x5dae4176),
    0x5f11893b: ('radial_melee_damage', DamageInfo.from_stream),
    0xf3fa9b62: ('elsc', _decode_elsc),
    0xe0c37dfa: ('unknown_0xe0c37dfa', _decode_unknown_0xe0c37dfa),
}
