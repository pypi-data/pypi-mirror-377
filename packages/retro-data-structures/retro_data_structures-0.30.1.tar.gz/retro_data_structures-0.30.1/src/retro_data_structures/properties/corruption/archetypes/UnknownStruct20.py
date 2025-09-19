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
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData
from retro_data_structures.properties.corruption.archetypes.ShockWaveInfo import ShockWaveInfo

if typing.TYPE_CHECKING:
    class UnknownStruct20Json(typing_extensions.TypedDict):
        health: float
        animation_speed: float
        heart_vulnerability: json_util.JsonObject
        body_vulnerability: json_util.JsonObject
        mouth_vulnerability: json_util.JsonObject
        stun_threshold: float
        stun_decay: float
        unknown_0x7d185e91: float
        unknown_0x9b78f170: float
        damage_info: json_util.JsonObject
        unknown_0x93b08ac8: float
        dash_delay_maximum: float
        dash_delay_minimum: float
        dash_delay_variance: float
        wander_distance: float
        too_far_distance: float
        berserk_distance: float
        shock_wave_info: json_util.JsonObject
        bomb: json_util.JsonObject
        unknown_0x54cfed2a: float
        unknown_0x94a19a8b: float
        unknown_0x72c1356a: float
        unknown_0xe291a671: int
        unknown_0xa793e5f3: int
        unknown_0x19774dec: int
        circle_chance: float
        circle_right_chance: float
        circle_left_chance: float
        circle_north_chance: float
        circle_south_chance: float
        circle_pause_chance: float
        bomb_chance: float
        fade_out_target_alpha: float
        fade_out_delta: float
        fade_in_target_alpha: float
        fade_in_delta: float
        unknown_0x20dc1c96: float
    

@dataclasses.dataclass()
class UnknownStruct20(BaseProperty):
    health: float = dataclasses.field(default=750.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf0668919, original_name='Health'
        ),
    })
    animation_speed: float = dataclasses.field(default=1.100000023841858, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc5407757, original_name='AnimationSpeed'
        ),
    })
    heart_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xf064b3bc, original_name='HeartVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    body_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x0d9230d1, original_name='BodyVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    mouth_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xed7edca3, original_name='MouthVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    stun_threshold: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5bdd1e4c, original_name='StunThreshold'
        ),
    })
    stun_decay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6082430f, original_name='StunDecay'
        ),
    })
    unknown_0x7d185e91: float = dataclasses.field(default=7.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d185e91, original_name='Unknown'
        ),
    })
    unknown_0x9b78f170: float = dataclasses.field(default=11.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9b78f170, original_name='Unknown'
        ),
    })
    damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x24b933d3, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x93b08ac8: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x93b08ac8, original_name='Unknown'
        ),
    })
    dash_delay_maximum: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1b37eda7, original_name='DashDelayMaximum'
        ),
    })
    dash_delay_minimum: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b44fd4d, original_name='DashDelayMinimum'
        ),
    })
    dash_delay_variance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdac05eb5, original_name='DashDelayVariance'
        ),
    })
    wander_distance: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaf270c93, original_name='WanderDistance'
        ),
    })
    too_far_distance: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8819688d, original_name='TooFarDistance'
        ),
    })
    berserk_distance: float = dataclasses.field(default=44.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbc9bbaf9, original_name='BerserkDistance'
        ),
    })
    shock_wave_info: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0x9c32d0a0, original_name='ShockWaveInfo', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })
    bomb: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x4ea6c6a9, original_name='Bomb', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    unknown_0x54cfed2a: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x54cfed2a, original_name='Unknown'
        ),
    })
    unknown_0x94a19a8b: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x94a19a8b, original_name='Unknown'
        ),
    })
    unknown_0x72c1356a: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x72c1356a, original_name='Unknown'
        ),
    })
    unknown_0xe291a671: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe291a671, original_name='Unknown'
        ),
    })
    unknown_0xa793e5f3: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa793e5f3, original_name='Unknown'
        ),
    })
    unknown_0x19774dec: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x19774dec, original_name='Unknown'
        ),
    })
    circle_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x482b7704, original_name='CircleChance'
        ),
    })
    circle_right_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3544d67, original_name='CircleRightChance'
        ),
    })
    circle_left_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa247c47c, original_name='CircleLeftChance'
        ),
    })
    circle_north_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6515999e, original_name='CircleNorthChance'
        ),
    })
    circle_south_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xefb54f99, original_name='CircleSouthChance'
        ),
    })
    circle_pause_chance: float = dataclasses.field(default=200.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc8d2e4a8, original_name='CirclePauseChance'
        ),
    })
    bomb_chance: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf3ad3881, original_name='BombChance'
        ),
    })
    fade_out_target_alpha: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x036e3c74, original_name='FadeOutTargetAlpha'
        ),
    })
    fade_out_delta: float = dataclasses.field(default=-0.02500000037252903, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2171c5ed, original_name='FadeOutDelta'
        ),
    })
    fade_in_target_alpha: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2515641c, original_name='FadeInTargetAlpha'
        ),
    })
    fade_in_delta: float = dataclasses.field(default=0.02500000037252903, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6e42bb15, original_name='FadeInDelta'
        ),
    })
    unknown_0x20dc1c96: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x20dc1c96, original_name='Unknown'
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
        if property_count != 37:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf0668919
        health = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc5407757
        animation_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf064b3bc
        heart_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d9230d1
        body_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed7edca3
        mouth_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5bdd1e4c
        stun_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6082430f
        stun_decay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d185e91
        unknown_0x7d185e91 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9b78f170
        unknown_0x9b78f170 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24b933d3
        damage_info = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 3.0, 'di_radius': 1.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x93b08ac8
        unknown_0x93b08ac8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b37eda7
        dash_delay_maximum = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b44fd4d
        dash_delay_minimum = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdac05eb5
        dash_delay_variance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaf270c93
        wander_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8819688d
        too_far_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc9bbaf9
        berserk_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9c32d0a0
        shock_wave_info = ShockWaveInfo.from_stream(data, property_size, default_override={'duration': 5.0, 'height': 2.0, 'radial_velocity': 45.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ea6c6a9
        bomb = LaunchProjectileData.from_stream(data, property_size, default_override={'delay': 0.20000000298023224, 'delay_variance': 0.10000000149011612, 'stop_homing_range': 30.0, 'generate_pickup_chance': 1.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x54cfed2a
        unknown_0x54cfed2a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x94a19a8b
        unknown_0x94a19a8b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x72c1356a
        unknown_0x72c1356a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe291a671
        unknown_0xe291a671 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa793e5f3
        unknown_0xa793e5f3 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19774dec
        unknown_0x19774dec = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x482b7704
        circle_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3544d67
        circle_right_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa247c47c
        circle_left_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6515999e
        circle_north_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xefb54f99
        circle_south_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8d2e4a8
        circle_pause_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3ad3881
        bomb_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x036e3c74
        fade_out_target_alpha = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2171c5ed
        fade_out_delta = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2515641c
        fade_in_target_alpha = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6e42bb15
        fade_in_delta = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x20dc1c96
        unknown_0x20dc1c96 = struct.unpack('>f', data.read(4))[0]
    
        return cls(health, animation_speed, heart_vulnerability, body_vulnerability, mouth_vulnerability, stun_threshold, stun_decay, unknown_0x7d185e91, unknown_0x9b78f170, damage_info, unknown_0x93b08ac8, dash_delay_maximum, dash_delay_minimum, dash_delay_variance, wander_distance, too_far_distance, berserk_distance, shock_wave_info, bomb, unknown_0x54cfed2a, unknown_0x94a19a8b, unknown_0x72c1356a, unknown_0xe291a671, unknown_0xa793e5f3, unknown_0x19774dec, circle_chance, circle_right_chance, circle_left_chance, circle_north_chance, circle_south_chance, circle_pause_chance, bomb_chance, fade_out_target_alpha, fade_out_delta, fade_in_target_alpha, fade_in_delta, unknown_0x20dc1c96)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00%')  # 37 properties

        data.write(b'\xf0f\x89\x19')  # 0xf0668919
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.health))

        data.write(b'\xc5@wW')  # 0xc5407757
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.animation_speed))

        data.write(b'\xf0d\xb3\xbc')  # 0xf064b3bc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.heart_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\r\x920\xd1')  # 0xd9230d1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.body_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed~\xdc\xa3')  # 0xed7edca3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.mouth_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'[\xdd\x1eL')  # 0x5bdd1e4c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.stun_threshold))

        data.write(b'`\x82C\x0f')  # 0x6082430f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.stun_decay))

        data.write(b'}\x18^\x91')  # 0x7d185e91
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7d185e91))

        data.write(b'\x9bx\xf1p')  # 0x9b78f170
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9b78f170))

        data.write(b'$\xb93\xd3')  # 0x24b933d3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info.to_stream(data, default_override={'di_damage': 3.0, 'di_radius': 1.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x93\xb0\x8a\xc8')  # 0x93b08ac8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x93b08ac8))

        data.write(b'\x1b7\xed\xa7')  # 0x1b37eda7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dash_delay_maximum))

        data.write(b'\x8bD\xfdM')  # 0x8b44fd4d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dash_delay_minimum))

        data.write(b'\xda\xc0^\xb5')  # 0xdac05eb5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dash_delay_variance))

        data.write(b"\xaf'\x0c\x93")  # 0xaf270c93
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.wander_distance))

        data.write(b'\x88\x19h\x8d')  # 0x8819688d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.too_far_distance))

        data.write(b'\xbc\x9b\xba\xf9')  # 0xbc9bbaf9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.berserk_distance))

        data.write(b'\x9c2\xd0\xa0')  # 0x9c32d0a0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shock_wave_info.to_stream(data, default_override={'duration': 5.0, 'height': 2.0, 'radial_velocity': 45.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'N\xa6\xc6\xa9')  # 0x4ea6c6a9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.bomb.to_stream(data, default_override={'delay': 0.20000000298023224, 'delay_variance': 0.10000000149011612, 'stop_homing_range': 30.0, 'generate_pickup_chance': 1.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'T\xcf\xed*')  # 0x54cfed2a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x54cfed2a))

        data.write(b'\x94\xa1\x9a\x8b')  # 0x94a19a8b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x94a19a8b))

        data.write(b'r\xc15j')  # 0x72c1356a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x72c1356a))

        data.write(b'\xe2\x91\xa6q')  # 0xe291a671
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xe291a671))

        data.write(b'\xa7\x93\xe5\xf3')  # 0xa793e5f3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xa793e5f3))

        data.write(b'\x19wM\xec')  # 0x19774dec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x19774dec))

        data.write(b'H+w\x04')  # 0x482b7704
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.circle_chance))

        data.write(b'\xc3TMg')  # 0xc3544d67
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.circle_right_chance))

        data.write(b'\xa2G\xc4|')  # 0xa247c47c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.circle_left_chance))

        data.write(b'e\x15\x99\x9e')  # 0x6515999e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.circle_north_chance))

        data.write(b'\xef\xb5O\x99')  # 0xefb54f99
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.circle_south_chance))

        data.write(b'\xc8\xd2\xe4\xa8')  # 0xc8d2e4a8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.circle_pause_chance))

        data.write(b'\xf3\xad8\x81')  # 0xf3ad3881
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.bomb_chance))

        data.write(b'\x03n<t')  # 0x36e3c74
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_out_target_alpha))

        data.write(b'!q\xc5\xed')  # 0x2171c5ed
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_out_delta))

        data.write(b'%\x15d\x1c')  # 0x2515641c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_in_target_alpha))

        data.write(b'nB\xbb\x15')  # 0x6e42bb15
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_in_delta))

        data.write(b' \xdc\x1c\x96')  # 0x20dc1c96
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x20dc1c96))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct20Json", data)
        return cls(
            health=json_data['health'],
            animation_speed=json_data['animation_speed'],
            heart_vulnerability=DamageVulnerability.from_json(json_data['heart_vulnerability']),
            body_vulnerability=DamageVulnerability.from_json(json_data['body_vulnerability']),
            mouth_vulnerability=DamageVulnerability.from_json(json_data['mouth_vulnerability']),
            stun_threshold=json_data['stun_threshold'],
            stun_decay=json_data['stun_decay'],
            unknown_0x7d185e91=json_data['unknown_0x7d185e91'],
            unknown_0x9b78f170=json_data['unknown_0x9b78f170'],
            damage_info=DamageInfo.from_json(json_data['damage_info']),
            unknown_0x93b08ac8=json_data['unknown_0x93b08ac8'],
            dash_delay_maximum=json_data['dash_delay_maximum'],
            dash_delay_minimum=json_data['dash_delay_minimum'],
            dash_delay_variance=json_data['dash_delay_variance'],
            wander_distance=json_data['wander_distance'],
            too_far_distance=json_data['too_far_distance'],
            berserk_distance=json_data['berserk_distance'],
            shock_wave_info=ShockWaveInfo.from_json(json_data['shock_wave_info']),
            bomb=LaunchProjectileData.from_json(json_data['bomb']),
            unknown_0x54cfed2a=json_data['unknown_0x54cfed2a'],
            unknown_0x94a19a8b=json_data['unknown_0x94a19a8b'],
            unknown_0x72c1356a=json_data['unknown_0x72c1356a'],
            unknown_0xe291a671=json_data['unknown_0xe291a671'],
            unknown_0xa793e5f3=json_data['unknown_0xa793e5f3'],
            unknown_0x19774dec=json_data['unknown_0x19774dec'],
            circle_chance=json_data['circle_chance'],
            circle_right_chance=json_data['circle_right_chance'],
            circle_left_chance=json_data['circle_left_chance'],
            circle_north_chance=json_data['circle_north_chance'],
            circle_south_chance=json_data['circle_south_chance'],
            circle_pause_chance=json_data['circle_pause_chance'],
            bomb_chance=json_data['bomb_chance'],
            fade_out_target_alpha=json_data['fade_out_target_alpha'],
            fade_out_delta=json_data['fade_out_delta'],
            fade_in_target_alpha=json_data['fade_in_target_alpha'],
            fade_in_delta=json_data['fade_in_delta'],
            unknown_0x20dc1c96=json_data['unknown_0x20dc1c96'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'health': self.health,
            'animation_speed': self.animation_speed,
            'heart_vulnerability': self.heart_vulnerability.to_json(),
            'body_vulnerability': self.body_vulnerability.to_json(),
            'mouth_vulnerability': self.mouth_vulnerability.to_json(),
            'stun_threshold': self.stun_threshold,
            'stun_decay': self.stun_decay,
            'unknown_0x7d185e91': self.unknown_0x7d185e91,
            'unknown_0x9b78f170': self.unknown_0x9b78f170,
            'damage_info': self.damage_info.to_json(),
            'unknown_0x93b08ac8': self.unknown_0x93b08ac8,
            'dash_delay_maximum': self.dash_delay_maximum,
            'dash_delay_minimum': self.dash_delay_minimum,
            'dash_delay_variance': self.dash_delay_variance,
            'wander_distance': self.wander_distance,
            'too_far_distance': self.too_far_distance,
            'berserk_distance': self.berserk_distance,
            'shock_wave_info': self.shock_wave_info.to_json(),
            'bomb': self.bomb.to_json(),
            'unknown_0x54cfed2a': self.unknown_0x54cfed2a,
            'unknown_0x94a19a8b': self.unknown_0x94a19a8b,
            'unknown_0x72c1356a': self.unknown_0x72c1356a,
            'unknown_0xe291a671': self.unknown_0xe291a671,
            'unknown_0xa793e5f3': self.unknown_0xa793e5f3,
            'unknown_0x19774dec': self.unknown_0x19774dec,
            'circle_chance': self.circle_chance,
            'circle_right_chance': self.circle_right_chance,
            'circle_left_chance': self.circle_left_chance,
            'circle_north_chance': self.circle_north_chance,
            'circle_south_chance': self.circle_south_chance,
            'circle_pause_chance': self.circle_pause_chance,
            'bomb_chance': self.bomb_chance,
            'fade_out_target_alpha': self.fade_out_target_alpha,
            'fade_out_delta': self.fade_out_delta,
            'fade_in_target_alpha': self.fade_in_target_alpha,
            'fade_in_delta': self.fade_in_delta,
            'unknown_0x20dc1c96': self.unknown_0x20dc1c96,
        }


def _decode_health(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_animation_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_stun_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_stun_decay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7d185e91(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9b78f170(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_damage_info(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 3.0, 'di_radius': 1.0, 'di_knock_back_power': 10.0})


def _decode_unknown_0x93b08ac8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dash_delay_maximum(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dash_delay_minimum(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dash_delay_variance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_wander_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_too_far_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_berserk_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shock_wave_info(data: typing.BinaryIO, property_size: int) -> ShockWaveInfo:
    return ShockWaveInfo.from_stream(data, property_size, default_override={'duration': 5.0, 'height': 2.0, 'radial_velocity': 45.0})


def _decode_bomb(data: typing.BinaryIO, property_size: int) -> LaunchProjectileData:
    return LaunchProjectileData.from_stream(data, property_size, default_override={'delay': 0.20000000298023224, 'delay_variance': 0.10000000149011612, 'stop_homing_range': 30.0, 'generate_pickup_chance': 1.0})


def _decode_unknown_0x54cfed2a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x94a19a8b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x72c1356a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe291a671(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xa793e5f3(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x19774dec(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_circle_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_circle_right_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_circle_left_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_circle_north_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_circle_south_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_circle_pause_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bomb_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_out_target_alpha(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_out_delta(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_in_target_alpha(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_in_delta(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x20dc1c96(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xf0668919: ('health', _decode_health),
    0xc5407757: ('animation_speed', _decode_animation_speed),
    0xf064b3bc: ('heart_vulnerability', DamageVulnerability.from_stream),
    0xd9230d1: ('body_vulnerability', DamageVulnerability.from_stream),
    0xed7edca3: ('mouth_vulnerability', DamageVulnerability.from_stream),
    0x5bdd1e4c: ('stun_threshold', _decode_stun_threshold),
    0x6082430f: ('stun_decay', _decode_stun_decay),
    0x7d185e91: ('unknown_0x7d185e91', _decode_unknown_0x7d185e91),
    0x9b78f170: ('unknown_0x9b78f170', _decode_unknown_0x9b78f170),
    0x24b933d3: ('damage_info', _decode_damage_info),
    0x93b08ac8: ('unknown_0x93b08ac8', _decode_unknown_0x93b08ac8),
    0x1b37eda7: ('dash_delay_maximum', _decode_dash_delay_maximum),
    0x8b44fd4d: ('dash_delay_minimum', _decode_dash_delay_minimum),
    0xdac05eb5: ('dash_delay_variance', _decode_dash_delay_variance),
    0xaf270c93: ('wander_distance', _decode_wander_distance),
    0x8819688d: ('too_far_distance', _decode_too_far_distance),
    0xbc9bbaf9: ('berserk_distance', _decode_berserk_distance),
    0x9c32d0a0: ('shock_wave_info', _decode_shock_wave_info),
    0x4ea6c6a9: ('bomb', _decode_bomb),
    0x54cfed2a: ('unknown_0x54cfed2a', _decode_unknown_0x54cfed2a),
    0x94a19a8b: ('unknown_0x94a19a8b', _decode_unknown_0x94a19a8b),
    0x72c1356a: ('unknown_0x72c1356a', _decode_unknown_0x72c1356a),
    0xe291a671: ('unknown_0xe291a671', _decode_unknown_0xe291a671),
    0xa793e5f3: ('unknown_0xa793e5f3', _decode_unknown_0xa793e5f3),
    0x19774dec: ('unknown_0x19774dec', _decode_unknown_0x19774dec),
    0x482b7704: ('circle_chance', _decode_circle_chance),
    0xc3544d67: ('circle_right_chance', _decode_circle_right_chance),
    0xa247c47c: ('circle_left_chance', _decode_circle_left_chance),
    0x6515999e: ('circle_north_chance', _decode_circle_north_chance),
    0xefb54f99: ('circle_south_chance', _decode_circle_south_chance),
    0xc8d2e4a8: ('circle_pause_chance', _decode_circle_pause_chance),
    0xf3ad3881: ('bomb_chance', _decode_bomb_chance),
    0x36e3c74: ('fade_out_target_alpha', _decode_fade_out_target_alpha),
    0x2171c5ed: ('fade_out_delta', _decode_fade_out_delta),
    0x2515641c: ('fade_in_target_alpha', _decode_fade_in_target_alpha),
    0x6e42bb15: ('fade_in_delta', _decode_fade_in_delta),
    0x20dc1c96: ('unknown_0x20dc1c96', _decode_unknown_0x20dc1c96),
}
