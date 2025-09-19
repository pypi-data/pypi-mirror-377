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
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.EchoParameters import EchoParameters
from retro_data_structures.properties.echoes.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class PatternedAITypedefJson(typing_extensions.TypedDict):
        mass: float
        speed: float
        turn_speed: float
        detection_range: float
        detection_height_range: float
        detection_angle: float
        min_attack_range: float
        max_attack_range: float
        average_attack_time: float
        attack_time_variation: float
        leash_radius: float
        player_leash_radius: float
        player_leash_time: float
        contact_damage: json_util.JsonObject
        damage_wait_time: float
        health: json_util.JsonObject
        vulnerability: json_util.JsonObject
        collision_radius: float
        collision_height: float
        collision_offset: json_util.JsonValue
        step_up_height: float
        unknown_0xe287d8dd: float
        unknown_0x66cdc6e8: float
        x_damage_delay: float
        sound_x_damage: int
        animation_information: json_util.JsonObject
        state_machine: int
        state_machine2: int
        unknown_0x87d22d43: float
        unknown_0xf0790c1b: float
        freeze_duration: float
        path_mesh_index: int
        gib_particles_offset: json_util.JsonValue
        gib_particles: int
        unknown_0xf35f5164: int
        ice_gib_particles_offset: json_util.JsonValue
        ice_gib_particles: int
        sound_0x7344d6cd: int
        sound_0x562cf323: int
        sound_frozen: int
        knockback_rules: int
        creature_size: int
        echo_parameters: json_util.JsonObject
    

@dataclasses.dataclass()
class PatternedAITypedef(BaseProperty):
    mass: float = dataclasses.field(default=150.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x75dbb375, original_name='Mass'
        ),
    })
    speed: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6392404e, original_name='Speed'
        ),
    })
    turn_speed: float = dataclasses.field(default=120.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x020c78bb, original_name='TurnSpeed'
        ),
    })
    detection_range: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8db77ee4, original_name='DetectionRange'
        ),
    })
    detection_height_range: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x513f04b8, original_name='DetectionHeightRange'
        ),
    })
    detection_angle: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x83dfc40f, original_name='DetectionAngle'
        ),
    })
    min_attack_range: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x58434916, original_name='MinAttackRange'
        ),
    })
    max_attack_range: float = dataclasses.field(default=11.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xff77c96f, original_name='MaxAttackRange'
        ),
    })
    average_attack_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb0cfe015, original_name='AverageAttackTime'
        ),
    })
    attack_time_variation: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc80e329b, original_name='AttackTimeVariation'
        ),
    })
    leash_radius: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3fae47eb, original_name='LeashRadius'
        ),
    })
    player_leash_radius: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x13f0b18f, original_name='PlayerLeashRadius'
        ),
    })
    player_leash_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d5a0487, original_name='PlayerLeashTime'
        ),
    })
    contact_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xd756416e, original_name='ContactDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_wait_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe0cdc7e3, original_name='DamageWaitTime'
        ),
    })
    health: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0xcf90d15e, original_name='Health', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x7b71ae90, original_name='Vulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    collision_radius: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8a6ab139, original_name='CollisionRadius'
        ),
    })
    collision_height: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3011b5df, original_name='CollisionHeight'
        ),
    })
    collision_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x2e686c2a, original_name='CollisionOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    step_up_height: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd9355674, original_name='StepUpHeight'
        ),
    })
    unknown_0xe287d8dd: float = dataclasses.field(default=1000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe287d8dd, original_name='Unknown'
        ),
    })
    unknown_0x66cdc6e8: float = dataclasses.field(default=1000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x66cdc6e8, original_name='Unknown'
        ),
    })
    x_damage_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x061cbe62, original_name='XDamageDelay'
        ),
    })
    sound_x_damage: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x19f84380, original_name='Sound_XDamage'
        ),
    })
    animation_information: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xe25fb08c, original_name='AnimationInformation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    state_machine: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['AFSM'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x55744160, original_name='StateMachine'
        ),
    })
    state_machine2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['FSM2'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc1c7e255, original_name='StateMachine2'
        ),
    })
    unknown_0x87d22d43: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x87d22d43, original_name='Unknown'
        ),
    })
    unknown_0xf0790c1b: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf0790c1b, original_name='Unknown'
        ),
    })
    freeze_duration: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xef3bd8cf, original_name='FreezeDuration'
        ),
    })
    path_mesh_index: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x98169634, original_name='PathMeshIndex'
        ),
    })
    gib_particles_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x487ef257, original_name='GibParticlesOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    gib_particles: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x684f00c9, original_name='GibParticles'
        ),
    })
    unknown_0xf35f5164: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf35f5164, original_name='Unknown'
        ),
    })
    ice_gib_particles_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x130539a0, original_name='IceGibParticlesOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    ice_gib_particles: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa8da9239, original_name='IceGibParticles'
        ),
    })
    sound_0x7344d6cd: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x7344d6cd, original_name='Sound'
        ),
    })
    sound_0x562cf323: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x562cf323, original_name='Sound'
        ),
    })
    sound_frozen: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xcdd9f41c, original_name='Sound_Frozen'
        ),
    })
    knockback_rules: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['RULE'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x87011652, original_name='KnockbackRules'
        ),
    })
    creature_size: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x4bc4c4d9, original_name='CreatureSize'
        ),
    })
    echo_parameters: EchoParameters = dataclasses.field(default_factory=EchoParameters, metadata={
        'reflection': FieldReflection[EchoParameters](
            EchoParameters, id=0x4476bed8, original_name='EchoParameters', from_json=EchoParameters.from_json, to_json=EchoParameters.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        if property_count != 43:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x75dbb375
        mass = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6392404e
        speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x020c78bb
        turn_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8db77ee4
        detection_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x513f04b8
        detection_height_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x83dfc40f
        detection_angle = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58434916
        min_attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xff77c96f
        max_attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb0cfe015
        average_attack_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc80e329b
        attack_time_variation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3fae47eb
        leash_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13f0b18f
        player_leash_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d5a0487
        player_leash_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd756416e
        contact_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0cdc7e3
        damage_wait_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf90d15e
        health = HealthInfo.from_stream(data, property_size, default_override={'hi_knock_back_resistance': 2.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b71ae90
        vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a6ab139
        collision_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3011b5df
        collision_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2e686c2a
        collision_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd9355674
        step_up_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe287d8dd
        unknown_0xe287d8dd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66cdc6e8
        unknown_0x66cdc6e8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x061cbe62
        x_damage_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19f84380
        sound_x_damage = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe25fb08c
        animation_information = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x55744160
        state_machine = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc1c7e255
        state_machine2 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87d22d43
        unknown_0x87d22d43 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf0790c1b
        unknown_0xf0790c1b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef3bd8cf
        freeze_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x98169634
        path_mesh_index = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x487ef257
        gib_particles_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x684f00c9
        gib_particles = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf35f5164
        unknown_0xf35f5164 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x130539a0
        ice_gib_particles_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa8da9239
        ice_gib_particles = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7344d6cd
        sound_0x7344d6cd = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x562cf323
        sound_0x562cf323 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcdd9f41c
        sound_frozen = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87011652
        knockback_rules = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4bc4c4d9
        creature_size = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4476bed8
        echo_parameters = EchoParameters.from_stream(data, property_size, default_override={'is_echo_emitter': True})
    
        return cls(mass, speed, turn_speed, detection_range, detection_height_range, detection_angle, min_attack_range, max_attack_range, average_attack_time, attack_time_variation, leash_radius, player_leash_radius, player_leash_time, contact_damage, damage_wait_time, health, vulnerability, collision_radius, collision_height, collision_offset, step_up_height, unknown_0xe287d8dd, unknown_0x66cdc6e8, x_damage_delay, sound_x_damage, animation_information, state_machine, state_machine2, unknown_0x87d22d43, unknown_0xf0790c1b, freeze_duration, path_mesh_index, gib_particles_offset, gib_particles, unknown_0xf35f5164, ice_gib_particles_offset, ice_gib_particles, sound_0x7344d6cd, sound_0x562cf323, sound_frozen, knockback_rules, creature_size, echo_parameters)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00+')  # 43 properties

        data.write(b'u\xdb\xb3u')  # 0x75dbb375
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.mass))

        data.write(b'c\x92@N')  # 0x6392404e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed))

        data.write(b'\x02\x0cx\xbb')  # 0x20c78bb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_speed))

        data.write(b'\x8d\xb7~\xe4')  # 0x8db77ee4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detection_range))

        data.write(b'Q?\x04\xb8')  # 0x513f04b8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detection_height_range))

        data.write(b'\x83\xdf\xc4\x0f')  # 0x83dfc40f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detection_angle))

        data.write(b'XCI\x16')  # 0x58434916
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_range))

        data.write(b'\xffw\xc9o')  # 0xff77c96f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_range))

        data.write(b'\xb0\xcf\xe0\x15')  # 0xb0cfe015
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.average_attack_time))

        data.write(b'\xc8\x0e2\x9b')  # 0xc80e329b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_time_variation))

        data.write(b'?\xaeG\xeb')  # 0x3fae47eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.leash_radius))

        data.write(b'\x13\xf0\xb1\x8f')  # 0x13f0b18f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.player_leash_radius))

        data.write(b'}Z\x04\x87')  # 0x7d5a0487
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.player_leash_time))

        data.write(b'\xd7VAn')  # 0xd756416e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.contact_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe0\xcd\xc7\xe3')  # 0xe0cdc7e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_wait_time))

        data.write(b'\xcf\x90\xd1^')  # 0xcf90d15e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.health.to_stream(data, default_override={'hi_knock_back_resistance': 2.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'{q\xae\x90')  # 0x7b71ae90
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8aj\xb19')  # 0x8a6ab139
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.collision_radius))

        data.write(b'0\x11\xb5\xdf')  # 0x3011b5df
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.collision_height))

        data.write(b'.hl*')  # 0x2e686c2a
        data.write(b'\x00\x0c')  # size
        self.collision_offset.to_stream(data)

        data.write(b'\xd95Vt')  # 0xd9355674
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.step_up_height))

        data.write(b'\xe2\x87\xd8\xdd')  # 0xe287d8dd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe287d8dd))

        data.write(b'f\xcd\xc6\xe8')  # 0x66cdc6e8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x66cdc6e8))

        data.write(b'\x06\x1c\xbeb')  # 0x61cbe62
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.x_damage_delay))

        data.write(b'\x19\xf8C\x80')  # 0x19f84380
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_x_damage))

        data.write(b'\xe2_\xb0\x8c')  # 0xe25fb08c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'UtA`')  # 0x55744160
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.state_machine))

        data.write(b'\xc1\xc7\xe2U')  # 0xc1c7e255
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.state_machine2))

        data.write(b'\x87\xd2-C')  # 0x87d22d43
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x87d22d43))

        data.write(b'\xf0y\x0c\x1b')  # 0xf0790c1b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf0790c1b))

        data.write(b'\xef;\xd8\xcf')  # 0xef3bd8cf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.freeze_duration))

        data.write(b'\x98\x16\x964')  # 0x98169634
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.path_mesh_index))

        data.write(b'H~\xf2W')  # 0x487ef257
        data.write(b'\x00\x0c')  # size
        self.gib_particles_offset.to_stream(data)

        data.write(b'hO\x00\xc9')  # 0x684f00c9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.gib_particles))

        data.write(b'\xf3_Qd')  # 0xf35f5164
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.unknown_0xf35f5164))

        data.write(b'\x13\x059\xa0')  # 0x130539a0
        data.write(b'\x00\x0c')  # size
        self.ice_gib_particles_offset.to_stream(data)

        data.write(b'\xa8\xda\x929')  # 0xa8da9239
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.ice_gib_particles))

        data.write(b'sD\xd6\xcd')  # 0x7344d6cd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x7344d6cd))

        data.write(b'V,\xf3#')  # 0x562cf323
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x562cf323))

        data.write(b'\xcd\xd9\xf4\x1c')  # 0xcdd9f41c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_frozen))

        data.write(b'\x87\x01\x16R')  # 0x87011652
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.knockback_rules))

        data.write(b'K\xc4\xc4\xd9')  # 0x4bc4c4d9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.creature_size))

        data.write(b'Dv\xbe\xd8')  # 0x4476bed8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.echo_parameters.to_stream(data, default_override={'is_echo_emitter': True})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PatternedAITypedefJson", data)
        return cls(
            mass=json_data['mass'],
            speed=json_data['speed'],
            turn_speed=json_data['turn_speed'],
            detection_range=json_data['detection_range'],
            detection_height_range=json_data['detection_height_range'],
            detection_angle=json_data['detection_angle'],
            min_attack_range=json_data['min_attack_range'],
            max_attack_range=json_data['max_attack_range'],
            average_attack_time=json_data['average_attack_time'],
            attack_time_variation=json_data['attack_time_variation'],
            leash_radius=json_data['leash_radius'],
            player_leash_radius=json_data['player_leash_radius'],
            player_leash_time=json_data['player_leash_time'],
            contact_damage=DamageInfo.from_json(json_data['contact_damage']),
            damage_wait_time=json_data['damage_wait_time'],
            health=HealthInfo.from_json(json_data['health']),
            vulnerability=DamageVulnerability.from_json(json_data['vulnerability']),
            collision_radius=json_data['collision_radius'],
            collision_height=json_data['collision_height'],
            collision_offset=Vector.from_json(json_data['collision_offset']),
            step_up_height=json_data['step_up_height'],
            unknown_0xe287d8dd=json_data['unknown_0xe287d8dd'],
            unknown_0x66cdc6e8=json_data['unknown_0x66cdc6e8'],
            x_damage_delay=json_data['x_damage_delay'],
            sound_x_damage=json_data['sound_x_damage'],
            animation_information=AnimationParameters.from_json(json_data['animation_information']),
            state_machine=json_data['state_machine'],
            state_machine2=json_data['state_machine2'],
            unknown_0x87d22d43=json_data['unknown_0x87d22d43'],
            unknown_0xf0790c1b=json_data['unknown_0xf0790c1b'],
            freeze_duration=json_data['freeze_duration'],
            path_mesh_index=json_data['path_mesh_index'],
            gib_particles_offset=Vector.from_json(json_data['gib_particles_offset']),
            gib_particles=json_data['gib_particles'],
            unknown_0xf35f5164=json_data['unknown_0xf35f5164'],
            ice_gib_particles_offset=Vector.from_json(json_data['ice_gib_particles_offset']),
            ice_gib_particles=json_data['ice_gib_particles'],
            sound_0x7344d6cd=json_data['sound_0x7344d6cd'],
            sound_0x562cf323=json_data['sound_0x562cf323'],
            sound_frozen=json_data['sound_frozen'],
            knockback_rules=json_data['knockback_rules'],
            creature_size=json_data['creature_size'],
            echo_parameters=EchoParameters.from_json(json_data['echo_parameters']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'mass': self.mass,
            'speed': self.speed,
            'turn_speed': self.turn_speed,
            'detection_range': self.detection_range,
            'detection_height_range': self.detection_height_range,
            'detection_angle': self.detection_angle,
            'min_attack_range': self.min_attack_range,
            'max_attack_range': self.max_attack_range,
            'average_attack_time': self.average_attack_time,
            'attack_time_variation': self.attack_time_variation,
            'leash_radius': self.leash_radius,
            'player_leash_radius': self.player_leash_radius,
            'player_leash_time': self.player_leash_time,
            'contact_damage': self.contact_damage.to_json(),
            'damage_wait_time': self.damage_wait_time,
            'health': self.health.to_json(),
            'vulnerability': self.vulnerability.to_json(),
            'collision_radius': self.collision_radius,
            'collision_height': self.collision_height,
            'collision_offset': self.collision_offset.to_json(),
            'step_up_height': self.step_up_height,
            'unknown_0xe287d8dd': self.unknown_0xe287d8dd,
            'unknown_0x66cdc6e8': self.unknown_0x66cdc6e8,
            'x_damage_delay': self.x_damage_delay,
            'sound_x_damage': self.sound_x_damage,
            'animation_information': self.animation_information.to_json(),
            'state_machine': self.state_machine,
            'state_machine2': self.state_machine2,
            'unknown_0x87d22d43': self.unknown_0x87d22d43,
            'unknown_0xf0790c1b': self.unknown_0xf0790c1b,
            'freeze_duration': self.freeze_duration,
            'path_mesh_index': self.path_mesh_index,
            'gib_particles_offset': self.gib_particles_offset.to_json(),
            'gib_particles': self.gib_particles,
            'unknown_0xf35f5164': self.unknown_0xf35f5164,
            'ice_gib_particles_offset': self.ice_gib_particles_offset.to_json(),
            'ice_gib_particles': self.ice_gib_particles,
            'sound_0x7344d6cd': self.sound_0x7344d6cd,
            'sound_0x562cf323': self.sound_0x562cf323,
            'sound_frozen': self.sound_frozen,
            'knockback_rules': self.knockback_rules,
            'creature_size': self.creature_size,
            'echo_parameters': self.echo_parameters.to_json(),
        }

    def _dependencies_for_sound_x_damage(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_x_damage)

    def _dependencies_for_state_machine(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.state_machine)

    def _dependencies_for_state_machine2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.state_machine2)

    def _dependencies_for_gib_particles(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.gib_particles)

    def _dependencies_for_unknown_0xf35f5164(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.unknown_0xf35f5164)

    def _dependencies_for_ice_gib_particles(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.ice_gib_particles)

    def _dependencies_for_sound_0x7344d6cd(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x7344d6cd)

    def _dependencies_for_sound_0x562cf323(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x562cf323)

    def _dependencies_for_sound_frozen(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_frozen)

    def _dependencies_for_knockback_rules(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.knockback_rules)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.contact_damage.dependencies_for, "contact_damage", "DamageInfo"),
            (self.health.dependencies_for, "health", "HealthInfo"),
            (self.vulnerability.dependencies_for, "vulnerability", "DamageVulnerability"),
            (self._dependencies_for_sound_x_damage, "sound_x_damage", "int"),
            (self.animation_information.dependencies_for, "animation_information", "AnimationParameters"),
            (self._dependencies_for_state_machine, "state_machine", "AssetId"),
            (self._dependencies_for_state_machine2, "state_machine2", "AssetId"),
            (self._dependencies_for_gib_particles, "gib_particles", "AssetId"),
            (self._dependencies_for_unknown_0xf35f5164, "unknown_0xf35f5164", "AssetId"),
            (self._dependencies_for_ice_gib_particles, "ice_gib_particles", "AssetId"),
            (self._dependencies_for_sound_0x7344d6cd, "sound_0x7344d6cd", "int"),
            (self._dependencies_for_sound_0x562cf323, "sound_0x562cf323", "int"),
            (self._dependencies_for_sound_frozen, "sound_frozen", "int"),
            (self._dependencies_for_knockback_rules, "knockback_rules", "AssetId"),
            (self.echo_parameters.dependencies_for, "echo_parameters", "EchoParameters"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for PatternedAITypedef.{field_name} ({field_type}): {e}"
                )


def _decode_mass(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_turn_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detection_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detection_height_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detection_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_average_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_time_variation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_leash_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_player_leash_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_player_leash_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_damage_wait_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_health(data: typing.BinaryIO, property_size: int) -> HealthInfo:
    return HealthInfo.from_stream(data, property_size, default_override={'hi_knock_back_resistance': 2.0})


def _decode_collision_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_collision_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_collision_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_step_up_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe287d8dd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x66cdc6e8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_x_damage_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_x_damage(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_state_machine(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_state_machine2(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x87d22d43(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf0790c1b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_freeze_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_path_mesh_index(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_gib_particles_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_gib_particles(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0xf35f5164(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_ice_gib_particles_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_ice_gib_particles(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_sound_0x7344d6cd(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x562cf323(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_frozen(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_knockback_rules(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_creature_size(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_echo_parameters(data: typing.BinaryIO, property_size: int) -> EchoParameters:
    return EchoParameters.from_stream(data, property_size, default_override={'is_echo_emitter': True})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x75dbb375: ('mass', _decode_mass),
    0x6392404e: ('speed', _decode_speed),
    0x20c78bb: ('turn_speed', _decode_turn_speed),
    0x8db77ee4: ('detection_range', _decode_detection_range),
    0x513f04b8: ('detection_height_range', _decode_detection_height_range),
    0x83dfc40f: ('detection_angle', _decode_detection_angle),
    0x58434916: ('min_attack_range', _decode_min_attack_range),
    0xff77c96f: ('max_attack_range', _decode_max_attack_range),
    0xb0cfe015: ('average_attack_time', _decode_average_attack_time),
    0xc80e329b: ('attack_time_variation', _decode_attack_time_variation),
    0x3fae47eb: ('leash_radius', _decode_leash_radius),
    0x13f0b18f: ('player_leash_radius', _decode_player_leash_radius),
    0x7d5a0487: ('player_leash_time', _decode_player_leash_time),
    0xd756416e: ('contact_damage', DamageInfo.from_stream),
    0xe0cdc7e3: ('damage_wait_time', _decode_damage_wait_time),
    0xcf90d15e: ('health', _decode_health),
    0x7b71ae90: ('vulnerability', DamageVulnerability.from_stream),
    0x8a6ab139: ('collision_radius', _decode_collision_radius),
    0x3011b5df: ('collision_height', _decode_collision_height),
    0x2e686c2a: ('collision_offset', _decode_collision_offset),
    0xd9355674: ('step_up_height', _decode_step_up_height),
    0xe287d8dd: ('unknown_0xe287d8dd', _decode_unknown_0xe287d8dd),
    0x66cdc6e8: ('unknown_0x66cdc6e8', _decode_unknown_0x66cdc6e8),
    0x61cbe62: ('x_damage_delay', _decode_x_damage_delay),
    0x19f84380: ('sound_x_damage', _decode_sound_x_damage),
    0xe25fb08c: ('animation_information', AnimationParameters.from_stream),
    0x55744160: ('state_machine', _decode_state_machine),
    0xc1c7e255: ('state_machine2', _decode_state_machine2),
    0x87d22d43: ('unknown_0x87d22d43', _decode_unknown_0x87d22d43),
    0xf0790c1b: ('unknown_0xf0790c1b', _decode_unknown_0xf0790c1b),
    0xef3bd8cf: ('freeze_duration', _decode_freeze_duration),
    0x98169634: ('path_mesh_index', _decode_path_mesh_index),
    0x487ef257: ('gib_particles_offset', _decode_gib_particles_offset),
    0x684f00c9: ('gib_particles', _decode_gib_particles),
    0xf35f5164: ('unknown_0xf35f5164', _decode_unknown_0xf35f5164),
    0x130539a0: ('ice_gib_particles_offset', _decode_ice_gib_particles_offset),
    0xa8da9239: ('ice_gib_particles', _decode_ice_gib_particles),
    0x7344d6cd: ('sound_0x7344d6cd', _decode_sound_0x7344d6cd),
    0x562cf323: ('sound_0x562cf323', _decode_sound_0x562cf323),
    0xcdd9f41c: ('sound_frozen', _decode_sound_frozen),
    0x87011652: ('knockback_rules', _decode_knockback_rules),
    0x4bc4c4d9: ('creature_size', _decode_creature_size),
    0x4476bed8: ('echo_parameters', _decode_echo_parameters),
}
