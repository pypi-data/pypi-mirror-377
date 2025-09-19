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
from retro_data_structures.properties.corruption.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.corruption.archetypes.SwarmSoundData import SwarmSoundData
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class SwarmBasicsDataJson(typing_extensions.TypedDict):
        contact_damage: json_util.JsonObject
        damage_wait_time: float
        collision_radius: float
        unknown_0xed999133: float
        touch_radius: float
        damage_radius: float
        speed: float
        count: int
        max_count: int
        influence_radius: float
        unknown_0x61959f0d: float
        alignment_priority: float
        separation_priority: float
        path_following_priority: float
        repulsor_avoidance_priority: float
        player_attract_priority: float
        player_attract_distance: float
        spawn_speed: float
        attacker_count: int
        attack_proximity: float
        attack_timer: float
        health: json_util.JsonObject
        damage_vulnerability: json_util.JsonObject
        death_particle_effect: int
        unknown_0x84f81f55: int
        attack_death_particle_effect: int
        unknown_0x90610f1a: int
        turn_rate: float
        unknown_0x7eb5d9e8: bool
        is_orbitable: bool
        unknown_0xbc01a28e: bool
        life_time: float
        locomotion_looped_sound: json_util.JsonObject
        attack_looped_sound: json_util.JsonObject
        swarm_sound_data_0x2646819a: json_util.JsonObject
        swarm_sound_data_0x373bebe3: json_util.JsonObject
        swarm_sound_data_0x9c417339: json_util.JsonObject
        swarm_sound_data_0x8d3c1940: json_util.JsonObject
        death_sound: int
        unknown_0x56c0d040: int
    

@dataclasses.dataclass()
class SwarmBasicsData(BaseProperty):
    contact_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xd756416e, original_name='ContactDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_wait_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe0cdc7e3, original_name='DamageWaitTime'
        ),
    })
    collision_radius: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8a6ab139, original_name='CollisionRadius'
        ),
    })
    unknown_0xed999133: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed999133, original_name='Unknown'
        ),
    })
    touch_radius: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x068c8e81, original_name='TouchRadius'
        ),
    })
    damage_radius: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0f598739, original_name='DamageRadius'
        ),
    })
    speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6392404e, original_name='Speed'
        ),
    })
    count: int = dataclasses.field(default=50, metadata={
        'reflection': FieldReflection[int](
            int, id=0x3291b8a2, original_name='Count'
        ),
    })
    max_count: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x54b68c4c, original_name='MaxCount'
        ),
    })
    influence_radius: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb160450e, original_name='InfluenceRadius'
        ),
    })
    unknown_0x61959f0d: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x61959f0d, original_name='Unknown'
        ),
    })
    alignment_priority: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4841f1de, original_name='AlignmentPriority'
        ),
    })
    separation_priority: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd293ebc4, original_name='SeparationPriority'
        ),
    })
    path_following_priority: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0xae11f975, original_name='PathFollowingPriority'
        ),
    })
    repulsor_avoidance_priority: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa9322755, original_name='RepulsorAvoidancePriority'
        ),
    })
    player_attract_priority: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x87edbcf1, original_name='PlayerAttractPriority'
        ),
    })
    player_attract_distance: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x542bc812, original_name='PlayerAttractDistance'
        ),
    })
    spawn_speed: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa355c04f, original_name='SpawnSpeed'
        ),
    })
    attacker_count: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x523a405c, original_name='AttackerCount'
        ),
    })
    attack_proximity: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1ca0e760, original_name='AttackProximity'
        ),
    })
    attack_timer: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x88df3ea8, original_name='AttackTimer'
        ),
    })
    health: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0xcf90d15e, original_name='Health', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    damage_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x382e406e, original_name='DamageVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    death_particle_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7d462930, original_name='DeathParticleEffect'
        ),
    })
    unknown_0x84f81f55: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x84f81f55, original_name='Unknown'
        ),
    })
    attack_death_particle_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x16e6e8bd, original_name='AttackDeathParticleEffect'
        ),
    })
    unknown_0x90610f1a: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x90610f1a, original_name='Unknown'
        ),
    })
    turn_rate: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe34dc703, original_name='TurnRate'
        ),
    })
    unknown_0x7eb5d9e8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7eb5d9e8, original_name='Unknown'
        ),
    })
    is_orbitable: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x826bec80, original_name='IsOrbitable'
        ),
    })
    unknown_0xbc01a28e: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xbc01a28e, original_name='Unknown'
        ),
    })
    life_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb02de555, original_name='LifeTime'
        ),
    })
    locomotion_looped_sound: SwarmSoundData = dataclasses.field(default_factory=SwarmSoundData, metadata={
        'reflection': FieldReflection[SwarmSoundData](
            SwarmSoundData, id=0x80bba072, original_name='LocomotionLoopedSound', from_json=SwarmSoundData.from_json, to_json=SwarmSoundData.to_json
        ),
    })
    attack_looped_sound: SwarmSoundData = dataclasses.field(default_factory=SwarmSoundData, metadata={
        'reflection': FieldReflection[SwarmSoundData](
            SwarmSoundData, id=0x49cfba93, original_name='AttackLoopedSound', from_json=SwarmSoundData.from_json, to_json=SwarmSoundData.to_json
        ),
    })
    swarm_sound_data_0x2646819a: SwarmSoundData = dataclasses.field(default_factory=SwarmSoundData, metadata={
        'reflection': FieldReflection[SwarmSoundData](
            SwarmSoundData, id=0x2646819a, original_name='SwarmSoundData', from_json=SwarmSoundData.from_json, to_json=SwarmSoundData.to_json
        ),
    })
    swarm_sound_data_0x373bebe3: SwarmSoundData = dataclasses.field(default_factory=SwarmSoundData, metadata={
        'reflection': FieldReflection[SwarmSoundData](
            SwarmSoundData, id=0x373bebe3, original_name='SwarmSoundData', from_json=SwarmSoundData.from_json, to_json=SwarmSoundData.to_json
        ),
    })
    swarm_sound_data_0x9c417339: SwarmSoundData = dataclasses.field(default_factory=SwarmSoundData, metadata={
        'reflection': FieldReflection[SwarmSoundData](
            SwarmSoundData, id=0x9c417339, original_name='SwarmSoundData', from_json=SwarmSoundData.from_json, to_json=SwarmSoundData.to_json
        ),
    })
    swarm_sound_data_0x8d3c1940: SwarmSoundData = dataclasses.field(default_factory=SwarmSoundData, metadata={
        'reflection': FieldReflection[SwarmSoundData](
            SwarmSoundData, id=0x8d3c1940, original_name='SwarmSoundData', from_json=SwarmSoundData.from_json, to_json=SwarmSoundData.to_json
        ),
    })
    death_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc7c3f610, original_name='DeathSound'
        ),
    })
    unknown_0x56c0d040: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x56c0d040, original_name='Unknown'
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
        if property_count != 40:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd756416e
        contact_damage = DamageInfo.from_stream(data, property_size, default_override={'di_radius': 5.0, 'di_knock_back_power': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0cdc7e3
        damage_wait_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a6ab139
        collision_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed999133
        unknown_0xed999133 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x068c8e81
        touch_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0f598739
        damage_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6392404e
        speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3291b8a2
        count = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x54b68c4c
        max_count = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb160450e
        influence_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x61959f0d
        unknown_0x61959f0d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4841f1de
        alignment_priority = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd293ebc4
        separation_priority = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xae11f975
        path_following_priority = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa9322755
        repulsor_avoidance_priority = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87edbcf1
        player_attract_priority = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x542bc812
        player_attract_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa355c04f
        spawn_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x523a405c
        attacker_count = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ca0e760
        attack_proximity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88df3ea8
        attack_timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf90d15e
        health = HealthInfo.from_stream(data, property_size, default_override={'health': 2.0, 'hi_knock_back_resistance': 2.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x382e406e
        damage_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d462930
        death_particle_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84f81f55
        unknown_0x84f81f55 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x16e6e8bd
        attack_death_particle_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90610f1a
        unknown_0x90610f1a = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe34dc703
        turn_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7eb5d9e8
        unknown_0x7eb5d9e8 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x826bec80
        is_orbitable = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc01a28e
        unknown_0xbc01a28e = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb02de555
        life_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80bba072
        locomotion_looped_sound = SwarmSoundData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49cfba93
        attack_looped_sound = SwarmSoundData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2646819a
        swarm_sound_data_0x2646819a = SwarmSoundData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x373bebe3
        swarm_sound_data_0x373bebe3 = SwarmSoundData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9c417339
        swarm_sound_data_0x9c417339 = SwarmSoundData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d3c1940
        swarm_sound_data_0x8d3c1940 = SwarmSoundData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc7c3f610
        death_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x56c0d040
        unknown_0x56c0d040 = struct.unpack('>l', data.read(4))[0]
    
        return cls(contact_damage, damage_wait_time, collision_radius, unknown_0xed999133, touch_radius, damage_radius, speed, count, max_count, influence_radius, unknown_0x61959f0d, alignment_priority, separation_priority, path_following_priority, repulsor_avoidance_priority, player_attract_priority, player_attract_distance, spawn_speed, attacker_count, attack_proximity, attack_timer, health, damage_vulnerability, death_particle_effect, unknown_0x84f81f55, attack_death_particle_effect, unknown_0x90610f1a, turn_rate, unknown_0x7eb5d9e8, is_orbitable, unknown_0xbc01a28e, life_time, locomotion_looped_sound, attack_looped_sound, swarm_sound_data_0x2646819a, swarm_sound_data_0x373bebe3, swarm_sound_data_0x9c417339, swarm_sound_data_0x8d3c1940, death_sound, unknown_0x56c0d040)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00(')  # 40 properties

        data.write(b'\xd7VAn')  # 0xd756416e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.contact_damage.to_stream(data, default_override={'di_radius': 5.0, 'di_knock_back_power': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe0\xcd\xc7\xe3')  # 0xe0cdc7e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_wait_time))

        data.write(b'\x8aj\xb19')  # 0x8a6ab139
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.collision_radius))

        data.write(b'\xed\x99\x913')  # 0xed999133
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xed999133))

        data.write(b'\x06\x8c\x8e\x81')  # 0x68c8e81
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.touch_radius))

        data.write(b'\x0fY\x879')  # 0xf598739
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_radius))

        data.write(b'c\x92@N')  # 0x6392404e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed))

        data.write(b'2\x91\xb8\xa2')  # 0x3291b8a2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.count))

        data.write(b'T\xb6\x8cL')  # 0x54b68c4c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_count))

        data.write(b'\xb1`E\x0e')  # 0xb160450e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.influence_radius))

        data.write(b'a\x95\x9f\r')  # 0x61959f0d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x61959f0d))

        data.write(b'HA\xf1\xde')  # 0x4841f1de
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.alignment_priority))

        data.write(b'\xd2\x93\xeb\xc4')  # 0xd293ebc4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.separation_priority))

        data.write(b'\xae\x11\xf9u')  # 0xae11f975
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.path_following_priority))

        data.write(b"\xa92'U")  # 0xa9322755
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.repulsor_avoidance_priority))

        data.write(b'\x87\xed\xbc\xf1')  # 0x87edbcf1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.player_attract_priority))

        data.write(b'T+\xc8\x12')  # 0x542bc812
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.player_attract_distance))

        data.write(b'\xa3U\xc0O')  # 0xa355c04f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.spawn_speed))

        data.write(b'R:@\\')  # 0x523a405c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.attacker_count))

        data.write(b'\x1c\xa0\xe7`')  # 0x1ca0e760
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_proximity))

        data.write(b'\x88\xdf>\xa8')  # 0x88df3ea8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_timer))

        data.write(b'\xcf\x90\xd1^')  # 0xcf90d15e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.health.to_stream(data, default_override={'health': 2.0, 'hi_knock_back_resistance': 2.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'8.@n')  # 0x382e406e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'}F)0')  # 0x7d462930
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.death_particle_effect))

        data.write(b'\x84\xf8\x1fU')  # 0x84f81f55
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x84f81f55))

        data.write(b'\x16\xe6\xe8\xbd')  # 0x16e6e8bd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.attack_death_particle_effect))

        data.write(b'\x90a\x0f\x1a')  # 0x90610f1a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x90610f1a))

        data.write(b'\xe3M\xc7\x03')  # 0xe34dc703
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_rate))

        data.write(b'~\xb5\xd9\xe8')  # 0x7eb5d9e8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x7eb5d9e8))

        data.write(b'\x82k\xec\x80')  # 0x826bec80
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_orbitable))

        data.write(b'\xbc\x01\xa2\x8e')  # 0xbc01a28e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xbc01a28e))

        data.write(b'\xb0-\xe5U')  # 0xb02de555
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.life_time))

        data.write(b'\x80\xbb\xa0r')  # 0x80bba072
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.locomotion_looped_sound.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'I\xcf\xba\x93')  # 0x49cfba93
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack_looped_sound.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'&F\x81\x9a')  # 0x2646819a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.swarm_sound_data_0x2646819a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'7;\xeb\xe3')  # 0x373bebe3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.swarm_sound_data_0x373bebe3.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9cAs9')  # 0x9c417339
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.swarm_sound_data_0x9c417339.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8d<\x19@')  # 0x8d3c1940
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.swarm_sound_data_0x8d3c1940.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc7\xc3\xf6\x10')  # 0xc7c3f610
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.death_sound))

        data.write(b'V\xc0\xd0@')  # 0x56c0d040
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x56c0d040))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SwarmBasicsDataJson", data)
        return cls(
            contact_damage=DamageInfo.from_json(json_data['contact_damage']),
            damage_wait_time=json_data['damage_wait_time'],
            collision_radius=json_data['collision_radius'],
            unknown_0xed999133=json_data['unknown_0xed999133'],
            touch_radius=json_data['touch_radius'],
            damage_radius=json_data['damage_radius'],
            speed=json_data['speed'],
            count=json_data['count'],
            max_count=json_data['max_count'],
            influence_radius=json_data['influence_radius'],
            unknown_0x61959f0d=json_data['unknown_0x61959f0d'],
            alignment_priority=json_data['alignment_priority'],
            separation_priority=json_data['separation_priority'],
            path_following_priority=json_data['path_following_priority'],
            repulsor_avoidance_priority=json_data['repulsor_avoidance_priority'],
            player_attract_priority=json_data['player_attract_priority'],
            player_attract_distance=json_data['player_attract_distance'],
            spawn_speed=json_data['spawn_speed'],
            attacker_count=json_data['attacker_count'],
            attack_proximity=json_data['attack_proximity'],
            attack_timer=json_data['attack_timer'],
            health=HealthInfo.from_json(json_data['health']),
            damage_vulnerability=DamageVulnerability.from_json(json_data['damage_vulnerability']),
            death_particle_effect=json_data['death_particle_effect'],
            unknown_0x84f81f55=json_data['unknown_0x84f81f55'],
            attack_death_particle_effect=json_data['attack_death_particle_effect'],
            unknown_0x90610f1a=json_data['unknown_0x90610f1a'],
            turn_rate=json_data['turn_rate'],
            unknown_0x7eb5d9e8=json_data['unknown_0x7eb5d9e8'],
            is_orbitable=json_data['is_orbitable'],
            unknown_0xbc01a28e=json_data['unknown_0xbc01a28e'],
            life_time=json_data['life_time'],
            locomotion_looped_sound=SwarmSoundData.from_json(json_data['locomotion_looped_sound']),
            attack_looped_sound=SwarmSoundData.from_json(json_data['attack_looped_sound']),
            swarm_sound_data_0x2646819a=SwarmSoundData.from_json(json_data['swarm_sound_data_0x2646819a']),
            swarm_sound_data_0x373bebe3=SwarmSoundData.from_json(json_data['swarm_sound_data_0x373bebe3']),
            swarm_sound_data_0x9c417339=SwarmSoundData.from_json(json_data['swarm_sound_data_0x9c417339']),
            swarm_sound_data_0x8d3c1940=SwarmSoundData.from_json(json_data['swarm_sound_data_0x8d3c1940']),
            death_sound=json_data['death_sound'],
            unknown_0x56c0d040=json_data['unknown_0x56c0d040'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'contact_damage': self.contact_damage.to_json(),
            'damage_wait_time': self.damage_wait_time,
            'collision_radius': self.collision_radius,
            'unknown_0xed999133': self.unknown_0xed999133,
            'touch_radius': self.touch_radius,
            'damage_radius': self.damage_radius,
            'speed': self.speed,
            'count': self.count,
            'max_count': self.max_count,
            'influence_radius': self.influence_radius,
            'unknown_0x61959f0d': self.unknown_0x61959f0d,
            'alignment_priority': self.alignment_priority,
            'separation_priority': self.separation_priority,
            'path_following_priority': self.path_following_priority,
            'repulsor_avoidance_priority': self.repulsor_avoidance_priority,
            'player_attract_priority': self.player_attract_priority,
            'player_attract_distance': self.player_attract_distance,
            'spawn_speed': self.spawn_speed,
            'attacker_count': self.attacker_count,
            'attack_proximity': self.attack_proximity,
            'attack_timer': self.attack_timer,
            'health': self.health.to_json(),
            'damage_vulnerability': self.damage_vulnerability.to_json(),
            'death_particle_effect': self.death_particle_effect,
            'unknown_0x84f81f55': self.unknown_0x84f81f55,
            'attack_death_particle_effect': self.attack_death_particle_effect,
            'unknown_0x90610f1a': self.unknown_0x90610f1a,
            'turn_rate': self.turn_rate,
            'unknown_0x7eb5d9e8': self.unknown_0x7eb5d9e8,
            'is_orbitable': self.is_orbitable,
            'unknown_0xbc01a28e': self.unknown_0xbc01a28e,
            'life_time': self.life_time,
            'locomotion_looped_sound': self.locomotion_looped_sound.to_json(),
            'attack_looped_sound': self.attack_looped_sound.to_json(),
            'swarm_sound_data_0x2646819a': self.swarm_sound_data_0x2646819a.to_json(),
            'swarm_sound_data_0x373bebe3': self.swarm_sound_data_0x373bebe3.to_json(),
            'swarm_sound_data_0x9c417339': self.swarm_sound_data_0x9c417339.to_json(),
            'swarm_sound_data_0x8d3c1940': self.swarm_sound_data_0x8d3c1940.to_json(),
            'death_sound': self.death_sound,
            'unknown_0x56c0d040': self.unknown_0x56c0d040,
        }


def _decode_contact_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_radius': 5.0, 'di_knock_back_power': 5.0})


def _decode_damage_wait_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_collision_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xed999133(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_touch_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_damage_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_max_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_influence_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x61959f0d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_alignment_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_separation_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_path_following_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_repulsor_avoidance_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_player_attract_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_player_attract_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_spawn_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attacker_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_attack_proximity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_health(data: typing.BinaryIO, property_size: int) -> HealthInfo:
    return HealthInfo.from_stream(data, property_size, default_override={'health': 2.0, 'hi_knock_back_resistance': 2.0})


def _decode_death_particle_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x84f81f55(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_attack_death_particle_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x90610f1a(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_turn_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7eb5d9e8(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_is_orbitable(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xbc01a28e(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_life_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_death_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x56c0d040(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xd756416e: ('contact_damage', _decode_contact_damage),
    0xe0cdc7e3: ('damage_wait_time', _decode_damage_wait_time),
    0x8a6ab139: ('collision_radius', _decode_collision_radius),
    0xed999133: ('unknown_0xed999133', _decode_unknown_0xed999133),
    0x68c8e81: ('touch_radius', _decode_touch_radius),
    0xf598739: ('damage_radius', _decode_damage_radius),
    0x6392404e: ('speed', _decode_speed),
    0x3291b8a2: ('count', _decode_count),
    0x54b68c4c: ('max_count', _decode_max_count),
    0xb160450e: ('influence_radius', _decode_influence_radius),
    0x61959f0d: ('unknown_0x61959f0d', _decode_unknown_0x61959f0d),
    0x4841f1de: ('alignment_priority', _decode_alignment_priority),
    0xd293ebc4: ('separation_priority', _decode_separation_priority),
    0xae11f975: ('path_following_priority', _decode_path_following_priority),
    0xa9322755: ('repulsor_avoidance_priority', _decode_repulsor_avoidance_priority),
    0x87edbcf1: ('player_attract_priority', _decode_player_attract_priority),
    0x542bc812: ('player_attract_distance', _decode_player_attract_distance),
    0xa355c04f: ('spawn_speed', _decode_spawn_speed),
    0x523a405c: ('attacker_count', _decode_attacker_count),
    0x1ca0e760: ('attack_proximity', _decode_attack_proximity),
    0x88df3ea8: ('attack_timer', _decode_attack_timer),
    0xcf90d15e: ('health', _decode_health),
    0x382e406e: ('damage_vulnerability', DamageVulnerability.from_stream),
    0x7d462930: ('death_particle_effect', _decode_death_particle_effect),
    0x84f81f55: ('unknown_0x84f81f55', _decode_unknown_0x84f81f55),
    0x16e6e8bd: ('attack_death_particle_effect', _decode_attack_death_particle_effect),
    0x90610f1a: ('unknown_0x90610f1a', _decode_unknown_0x90610f1a),
    0xe34dc703: ('turn_rate', _decode_turn_rate),
    0x7eb5d9e8: ('unknown_0x7eb5d9e8', _decode_unknown_0x7eb5d9e8),
    0x826bec80: ('is_orbitable', _decode_is_orbitable),
    0xbc01a28e: ('unknown_0xbc01a28e', _decode_unknown_0xbc01a28e),
    0xb02de555: ('life_time', _decode_life_time),
    0x80bba072: ('locomotion_looped_sound', SwarmSoundData.from_stream),
    0x49cfba93: ('attack_looped_sound', SwarmSoundData.from_stream),
    0x2646819a: ('swarm_sound_data_0x2646819a', SwarmSoundData.from_stream),
    0x373bebe3: ('swarm_sound_data_0x373bebe3', SwarmSoundData.from_stream),
    0x9c417339: ('swarm_sound_data_0x9c417339', SwarmSoundData.from_stream),
    0x8d3c1940: ('swarm_sound_data_0x8d3c1940', SwarmSoundData.from_stream),
    0xc7c3f610: ('death_sound', _decode_death_sound),
    0x56c0d040: ('unknown_0x56c0d040', _decode_unknown_0x56c0d040),
}
