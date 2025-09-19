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
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData
from retro_data_structures.properties.corruption.archetypes.MetroidHopperStruct import MetroidHopperStruct
from retro_data_structures.properties.corruption.archetypes.TeamAIDebugEnum import TeamAIDebugEnum
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class MetroidHopperDataJson(typing_extensions.TypedDict):
        animation_speed: float
        hearing_range: float
        alert_animation_chance: float
        unknown_0x87c38060: bool
        jump_apex: float
        gravity_constant: float
        min_melee_attack_dist: float
        max_melee_attack_dist: float
        unknown_0x68e4097e: float
        light_melee_damage_info: json_util.JsonObject
        heavy_melee_damage_info: json_util.JsonObject
        unknown_0x500683fc: float
        unknown_0x0708d3bf: float
        projectile_info: json_util.JsonObject
        melee_chance: float
        projectile_chance: float
        metroid_hopper_struct_0xd5a8e2da: json_util.JsonObject
        metroid_hopper_struct_0x184991da: json_util.JsonObject
        metroid_hopper_struct_0x7b07aca3: json_util.JsonObject
        hypermode_clear_effect: int
        hypermode_clear_sound: int
        unknown_0x1da1b117: float
        part: int
        super_hopper_explosion_damage: json_util.JsonObject
        team_ai_debug_type: json_util.JsonObject
        debug_patrol: bool
    

@dataclasses.dataclass()
class MetroidHopperData(BaseProperty):
    animation_speed: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc5407757, original_name='AnimationSpeed'
        ),
    })
    hearing_range: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x25474550, original_name='HearingRange'
        ),
    })
    alert_animation_chance: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe6496376, original_name='AlertAnimationChance'
        ),
    })
    unknown_0x87c38060: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x87c38060, original_name='Unknown'
        ),
    })
    jump_apex: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf2782501, original_name='JumpApex'
        ),
    })
    gravity_constant: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7f38dccb, original_name='GravityConstant'
        ),
    })
    min_melee_attack_dist: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x01b7d6b1, original_name='MinMeleeAttackDist'
        ),
    })
    max_melee_attack_dist: float = dataclasses.field(default=11.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x052de79b, original_name='MaxMeleeAttackDist'
        ),
    })
    unknown_0x68e4097e: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x68e4097e, original_name='Unknown'
        ),
    })
    light_melee_damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x2b76b9f1, original_name='LightMeleeDamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    heavy_melee_damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x9ef4a101, original_name='HeavyMeleeDamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x500683fc: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x500683fc, original_name='Unknown'
        ),
    })
    unknown_0x0708d3bf: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0708d3bf, original_name='Unknown'
        ),
    })
    projectile_info: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0xf9ef8d5d, original_name='ProjectileInfo', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    melee_chance: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaecfea2d, original_name='MeleeChance'
        ),
    })
    projectile_chance: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2a7d0101, original_name='ProjectileChance'
        ),
    })
    metroid_hopper_struct_0xd5a8e2da: MetroidHopperStruct = dataclasses.field(default_factory=MetroidHopperStruct, metadata={
        'reflection': FieldReflection[MetroidHopperStruct](
            MetroidHopperStruct, id=0xd5a8e2da, original_name='MetroidHopperStruct', from_json=MetroidHopperStruct.from_json, to_json=MetroidHopperStruct.to_json
        ),
    })
    metroid_hopper_struct_0x184991da: MetroidHopperStruct = dataclasses.field(default_factory=MetroidHopperStruct, metadata={
        'reflection': FieldReflection[MetroidHopperStruct](
            MetroidHopperStruct, id=0x184991da, original_name='MetroidHopperStruct', from_json=MetroidHopperStruct.from_json, to_json=MetroidHopperStruct.to_json
        ),
    })
    metroid_hopper_struct_0x7b07aca3: MetroidHopperStruct = dataclasses.field(default_factory=MetroidHopperStruct, metadata={
        'reflection': FieldReflection[MetroidHopperStruct](
            MetroidHopperStruct, id=0x7b07aca3, original_name='MetroidHopperStruct', from_json=MetroidHopperStruct.from_json, to_json=MetroidHopperStruct.to_json
        ),
    })
    hypermode_clear_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5dde5b25, original_name='HypermodeClearEffect'
        ),
    })
    hypermode_clear_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf95d2033, original_name='HypermodeClearSound'
        ),
    })
    unknown_0x1da1b117: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1da1b117, original_name='Unknown'
        ),
    })
    part: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe0700022, original_name='PART'
        ),
    })
    super_hopper_explosion_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xd1f6c520, original_name='SuperHopperExplosionDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    team_ai_debug_type: TeamAIDebugEnum = dataclasses.field(default_factory=TeamAIDebugEnum, metadata={
        'reflection': FieldReflection[TeamAIDebugEnum](
            TeamAIDebugEnum, id=0xfb648831, original_name='TeamAIDebugType', from_json=TeamAIDebugEnum.from_json, to_json=TeamAIDebugEnum.to_json
        ),
    })
    debug_patrol: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xbb389a82, original_name='DebugPatrol'
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
        if property_count != 26:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc5407757
        animation_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x25474550
        hearing_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe6496376
        alert_animation_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87c38060
        unknown_0x87c38060 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf2782501
        jump_apex = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f38dccb
        gravity_constant = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01b7d6b1
        min_melee_attack_dist = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x052de79b
        max_melee_attack_dist = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68e4097e
        unknown_0x68e4097e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b76b9f1
        light_melee_damage_info = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9ef4a101
        heavy_melee_damage_info = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x500683fc
        unknown_0x500683fc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0708d3bf
        unknown_0x0708d3bf = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf9ef8d5d
        projectile_info = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaecfea2d
        melee_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2a7d0101
        projectile_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd5a8e2da
        metroid_hopper_struct_0xd5a8e2da = MetroidHopperStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x184991da
        metroid_hopper_struct_0x184991da = MetroidHopperStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b07aca3
        metroid_hopper_struct_0x7b07aca3 = MetroidHopperStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5dde5b25
        hypermode_clear_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf95d2033
        hypermode_clear_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1da1b117
        unknown_0x1da1b117 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0700022
        part = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd1f6c520
        super_hopper_explosion_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfb648831
        team_ai_debug_type = TeamAIDebugEnum.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbb389a82
        debug_patrol = struct.unpack('>?', data.read(1))[0]
    
        return cls(animation_speed, hearing_range, alert_animation_chance, unknown_0x87c38060, jump_apex, gravity_constant, min_melee_attack_dist, max_melee_attack_dist, unknown_0x68e4097e, light_melee_damage_info, heavy_melee_damage_info, unknown_0x500683fc, unknown_0x0708d3bf, projectile_info, melee_chance, projectile_chance, metroid_hopper_struct_0xd5a8e2da, metroid_hopper_struct_0x184991da, metroid_hopper_struct_0x7b07aca3, hypermode_clear_effect, hypermode_clear_sound, unknown_0x1da1b117, part, super_hopper_explosion_damage, team_ai_debug_type, debug_patrol)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x1a')  # 26 properties

        data.write(b'\xc5@wW')  # 0xc5407757
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.animation_speed))

        data.write(b'%GEP')  # 0x25474550
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hearing_range))

        data.write(b'\xe6Icv')  # 0xe6496376
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.alert_animation_chance))

        data.write(b'\x87\xc3\x80`')  # 0x87c38060
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x87c38060))

        data.write(b'\xf2x%\x01')  # 0xf2782501
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.jump_apex))

        data.write(b'\x7f8\xdc\xcb')  # 0x7f38dccb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.gravity_constant))

        data.write(b'\x01\xb7\xd6\xb1')  # 0x1b7d6b1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_melee_attack_dist))

        data.write(b'\x05-\xe7\x9b')  # 0x52de79b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_melee_attack_dist))

        data.write(b'h\xe4\t~')  # 0x68e4097e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x68e4097e))

        data.write(b'+v\xb9\xf1')  # 0x2b76b9f1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.light_melee_damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9e\xf4\xa1\x01')  # 0x9ef4a101
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.heavy_melee_damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'P\x06\x83\xfc')  # 0x500683fc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x500683fc))

        data.write(b'\x07\x08\xd3\xbf')  # 0x708d3bf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0708d3bf))

        data.write(b'\xf9\xef\x8d]')  # 0xf9ef8d5d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.projectile_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xae\xcf\xea-')  # 0xaecfea2d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_chance))

        data.write(b'*}\x01\x01')  # 0x2a7d0101
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.projectile_chance))

        data.write(b'\xd5\xa8\xe2\xda')  # 0xd5a8e2da
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.metroid_hopper_struct_0xd5a8e2da.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x18I\x91\xda')  # 0x184991da
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.metroid_hopper_struct_0x184991da.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'{\x07\xac\xa3')  # 0x7b07aca3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.metroid_hopper_struct_0x7b07aca3.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b']\xde[%')  # 0x5dde5b25
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.hypermode_clear_effect))

        data.write(b'\xf9] 3')  # 0xf95d2033
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.hypermode_clear_sound))

        data.write(b'\x1d\xa1\xb1\x17')  # 0x1da1b117
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1da1b117))

        data.write(b'\xe0p\x00"')  # 0xe0700022
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part))

        data.write(b'\xd1\xf6\xc5 ')  # 0xd1f6c520
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.super_hopper_explosion_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfbd\x881')  # 0xfb648831
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.team_ai_debug_type.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbb8\x9a\x82')  # 0xbb389a82
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.debug_patrol))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MetroidHopperDataJson", data)
        return cls(
            animation_speed=json_data['animation_speed'],
            hearing_range=json_data['hearing_range'],
            alert_animation_chance=json_data['alert_animation_chance'],
            unknown_0x87c38060=json_data['unknown_0x87c38060'],
            jump_apex=json_data['jump_apex'],
            gravity_constant=json_data['gravity_constant'],
            min_melee_attack_dist=json_data['min_melee_attack_dist'],
            max_melee_attack_dist=json_data['max_melee_attack_dist'],
            unknown_0x68e4097e=json_data['unknown_0x68e4097e'],
            light_melee_damage_info=DamageInfo.from_json(json_data['light_melee_damage_info']),
            heavy_melee_damage_info=DamageInfo.from_json(json_data['heavy_melee_damage_info']),
            unknown_0x500683fc=json_data['unknown_0x500683fc'],
            unknown_0x0708d3bf=json_data['unknown_0x0708d3bf'],
            projectile_info=LaunchProjectileData.from_json(json_data['projectile_info']),
            melee_chance=json_data['melee_chance'],
            projectile_chance=json_data['projectile_chance'],
            metroid_hopper_struct_0xd5a8e2da=MetroidHopperStruct.from_json(json_data['metroid_hopper_struct_0xd5a8e2da']),
            metroid_hopper_struct_0x184991da=MetroidHopperStruct.from_json(json_data['metroid_hopper_struct_0x184991da']),
            metroid_hopper_struct_0x7b07aca3=MetroidHopperStruct.from_json(json_data['metroid_hopper_struct_0x7b07aca3']),
            hypermode_clear_effect=json_data['hypermode_clear_effect'],
            hypermode_clear_sound=json_data['hypermode_clear_sound'],
            unknown_0x1da1b117=json_data['unknown_0x1da1b117'],
            part=json_data['part'],
            super_hopper_explosion_damage=DamageInfo.from_json(json_data['super_hopper_explosion_damage']),
            team_ai_debug_type=TeamAIDebugEnum.from_json(json_data['team_ai_debug_type']),
            debug_patrol=json_data['debug_patrol'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'animation_speed': self.animation_speed,
            'hearing_range': self.hearing_range,
            'alert_animation_chance': self.alert_animation_chance,
            'unknown_0x87c38060': self.unknown_0x87c38060,
            'jump_apex': self.jump_apex,
            'gravity_constant': self.gravity_constant,
            'min_melee_attack_dist': self.min_melee_attack_dist,
            'max_melee_attack_dist': self.max_melee_attack_dist,
            'unknown_0x68e4097e': self.unknown_0x68e4097e,
            'light_melee_damage_info': self.light_melee_damage_info.to_json(),
            'heavy_melee_damage_info': self.heavy_melee_damage_info.to_json(),
            'unknown_0x500683fc': self.unknown_0x500683fc,
            'unknown_0x0708d3bf': self.unknown_0x0708d3bf,
            'projectile_info': self.projectile_info.to_json(),
            'melee_chance': self.melee_chance,
            'projectile_chance': self.projectile_chance,
            'metroid_hopper_struct_0xd5a8e2da': self.metroid_hopper_struct_0xd5a8e2da.to_json(),
            'metroid_hopper_struct_0x184991da': self.metroid_hopper_struct_0x184991da.to_json(),
            'metroid_hopper_struct_0x7b07aca3': self.metroid_hopper_struct_0x7b07aca3.to_json(),
            'hypermode_clear_effect': self.hypermode_clear_effect,
            'hypermode_clear_sound': self.hypermode_clear_sound,
            'unknown_0x1da1b117': self.unknown_0x1da1b117,
            'part': self.part,
            'super_hopper_explosion_damage': self.super_hopper_explosion_damage.to_json(),
            'team_ai_debug_type': self.team_ai_debug_type.to_json(),
            'debug_patrol': self.debug_patrol,
        }


def _decode_animation_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hearing_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_alert_animation_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x87c38060(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_jump_apex(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_gravity_constant(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_melee_attack_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_melee_attack_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x68e4097e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x500683fc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0708d3bf(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_projectile_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hypermode_clear_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_hypermode_clear_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x1da1b117(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_part(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_debug_patrol(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc5407757: ('animation_speed', _decode_animation_speed),
    0x25474550: ('hearing_range', _decode_hearing_range),
    0xe6496376: ('alert_animation_chance', _decode_alert_animation_chance),
    0x87c38060: ('unknown_0x87c38060', _decode_unknown_0x87c38060),
    0xf2782501: ('jump_apex', _decode_jump_apex),
    0x7f38dccb: ('gravity_constant', _decode_gravity_constant),
    0x1b7d6b1: ('min_melee_attack_dist', _decode_min_melee_attack_dist),
    0x52de79b: ('max_melee_attack_dist', _decode_max_melee_attack_dist),
    0x68e4097e: ('unknown_0x68e4097e', _decode_unknown_0x68e4097e),
    0x2b76b9f1: ('light_melee_damage_info', DamageInfo.from_stream),
    0x9ef4a101: ('heavy_melee_damage_info', DamageInfo.from_stream),
    0x500683fc: ('unknown_0x500683fc', _decode_unknown_0x500683fc),
    0x708d3bf: ('unknown_0x0708d3bf', _decode_unknown_0x0708d3bf),
    0xf9ef8d5d: ('projectile_info', LaunchProjectileData.from_stream),
    0xaecfea2d: ('melee_chance', _decode_melee_chance),
    0x2a7d0101: ('projectile_chance', _decode_projectile_chance),
    0xd5a8e2da: ('metroid_hopper_struct_0xd5a8e2da', MetroidHopperStruct.from_stream),
    0x184991da: ('metroid_hopper_struct_0x184991da', MetroidHopperStruct.from_stream),
    0x7b07aca3: ('metroid_hopper_struct_0x7b07aca3', MetroidHopperStruct.from_stream),
    0x5dde5b25: ('hypermode_clear_effect', _decode_hypermode_clear_effect),
    0xf95d2033: ('hypermode_clear_sound', _decode_hypermode_clear_sound),
    0x1da1b117: ('unknown_0x1da1b117', _decode_unknown_0x1da1b117),
    0xe0700022: ('part', _decode_part),
    0xd1f6c520: ('super_hopper_explosion_damage', DamageInfo.from_stream),
    0xfb648831: ('team_ai_debug_type', TeamAIDebugEnum.from_stream),
    0xbb389a82: ('debug_patrol', _decode_debug_patrol),
}
