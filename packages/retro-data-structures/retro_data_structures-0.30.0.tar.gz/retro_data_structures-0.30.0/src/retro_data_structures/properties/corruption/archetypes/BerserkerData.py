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
from retro_data_structures.properties.corruption.archetypes.PlasmaBeamInfo import PlasmaBeamInfo
from retro_data_structures.properties.corruption.archetypes.ShockWaveInfo import ShockWaveInfo
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class BerserkerDataJson(typing_extensions.TypedDict):
        turn_threshold: float
        unknown_0x76ebc21a: bool
        melee_attack_range: float
        unknown_0xc4db42e3: bool
        ball_slam_damage: json_util.JsonObject
        damage_info_0xbb7977b9: json_util.JsonObject
        ground_pound_damage: json_util.JsonObject
        pirate_as_projectile_damage: json_util.JsonObject
        phazon_cannon_beam_info: json_util.JsonObject
        damage_info_0x97321af1: json_util.JsonObject
        unknown_0xfd5e7062: float
        unknown_0xbd110814: float
        unknown_0x3d947337: float
        unknown_0x1a975a02: float
        launch_projectile_data_0x066bc855: json_util.JsonObject
        unknown_0x67e0e4b4: float
        unknown_0xb7ad7067: float
        unknown_0xf7e20811: float
        unknown_0x4db474b8: float
        unknown_0x68d3daa4: json_util.JsonObject
        unknown_0x1b359207: float
        unknown_0xc12f397a: float
        unknown_0x4bfee56b: float
        unknown_0x8f3be6e1: float
        unknown_0xdd825dc3: float
        unknown_0x869415a3: float
        unknown_0xc6db6dd5: float
        phazon_grapple_time: float
        unknown_0x58e6d9b8: float
        unknown_0xcf111a99: float
        phazon_grapple_damage: json_util.JsonObject
        unknown_0x92f0b2c7: float
        unknown_0xbc2f8f30: float
        unknown_0x910ad1e0: float
        unknown_0x4566b3ef: float
        approach_player_chance: float
        unknown_0x24f779ca: float
        armored_vulnerability: json_util.JsonObject
        armor_health: float
        armor_model1: int
        armor_model2: int
        armor_model3: int
        armor_model4: int
        armor_model5: int
        unknown_0x09e8c7fd: float
        weak_spot_model: int
        provoked_head_vulnerability: json_util.JsonObject
        unknown_0x69d66ec4: float
        unknown_0x299916b2: float
        launch_projectile_data_0xfe51924e: json_util.JsonObject
        launch_projectile_data_0x9b9c702c: json_util.JsonObject
        launch_projectile_data_0x567ba94a: json_util.JsonObject
        launch_projectile_data_0xf4d5150f: json_util.JsonObject
        launch_projectile_data_0x8647c581: json_util.JsonObject
        unknown_0x15d26d26: float
        unknown_0x81eaa9d4: float
        is_gandrayda: bool
        is_chieftain: bool
        shoulder_vulnerability: json_util.JsonObject
        shoulder_health: float
        unknown_0x268e5cb2: float
        left_shoulder_model: int
        right_shoulder_model: int
        weak_spot_armored_vulnerability: json_util.JsonObject
        damage_vulnerability_0x200545bd: json_util.JsonObject
        damage_vulnerability_0xf3ea94dc: json_util.JsonObject
        unknown_0xedf1189f: bool
        minor_shockwave: json_util.JsonObject
        shock_wave_info: json_util.JsonObject
        unknown_0x0c1a5644: float
        unknown_0xc6af2fd0: float
    

@dataclasses.dataclass()
class BerserkerData(BaseProperty):
    turn_threshold: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc0ac271e, original_name='TurnThreshold'
        ),
    })
    unknown_0x76ebc21a: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x76ebc21a, original_name='Unknown'
        ),
    })
    melee_attack_range: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3e43d0e, original_name='MeleeAttackRange'
        ),
    })
    unknown_0xc4db42e3: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc4db42e3, original_name='Unknown'
        ),
    })
    ball_slam_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x74bffa78, original_name='BallSlamDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_0xbb7977b9: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xbb7977b9, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    ground_pound_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x4738c321, original_name='GroundPoundDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    pirate_as_projectile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xf4e003c1, original_name='PirateAsProjectileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    phazon_cannon_beam_info: PlasmaBeamInfo = dataclasses.field(default_factory=PlasmaBeamInfo, metadata={
        'reflection': FieldReflection[PlasmaBeamInfo](
            PlasmaBeamInfo, id=0xe0dbf22f, original_name='PhazonCannonBeamInfo', from_json=PlasmaBeamInfo.from_json, to_json=PlasmaBeamInfo.to_json
        ),
    })
    damage_info_0x97321af1: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x97321af1, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xfd5e7062: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfd5e7062, original_name='Unknown'
        ),
    })
    unknown_0xbd110814: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbd110814, original_name='Unknown'
        ),
    })
    unknown_0x3d947337: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3d947337, original_name='Unknown'
        ),
    })
    unknown_0x1a975a02: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1a975a02, original_name='Unknown'
        ),
    })
    launch_projectile_data_0x066bc855: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x066bc855, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    unknown_0x67e0e4b4: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x67e0e4b4, original_name='Unknown'
        ),
    })
    unknown_0xb7ad7067: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb7ad7067, original_name='Unknown'
        ),
    })
    unknown_0xf7e20811: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf7e20811, original_name='Unknown'
        ),
    })
    unknown_0x4db474b8: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4db474b8, original_name='Unknown'
        ),
    })
    unknown_0x68d3daa4: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x68d3daa4, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x1b359207: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1b359207, original_name='Unknown'
        ),
    })
    unknown_0xc12f397a: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc12f397a, original_name='Unknown'
        ),
    })
    unknown_0x4bfee56b: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4bfee56b, original_name='Unknown'
        ),
    })
    unknown_0x8f3be6e1: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8f3be6e1, original_name='Unknown'
        ),
    })
    unknown_0xdd825dc3: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdd825dc3, original_name='Unknown'
        ),
    })
    unknown_0x869415a3: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x869415a3, original_name='Unknown'
        ),
    })
    unknown_0xc6db6dd5: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc6db6dd5, original_name='Unknown'
        ),
    })
    phazon_grapple_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdc8d7887, original_name='PhazonGrappleTime'
        ),
    })
    unknown_0x58e6d9b8: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x58e6d9b8, original_name='Unknown'
        ),
    })
    unknown_0xcf111a99: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcf111a99, original_name='Unknown'
        ),
    })
    phazon_grapple_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x719fd06b, original_name='PhazonGrappleDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x92f0b2c7: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x92f0b2c7, original_name='Unknown'
        ),
    })
    unknown_0xbc2f8f30: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbc2f8f30, original_name='Unknown'
        ),
    })
    unknown_0x910ad1e0: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x910ad1e0, original_name='Unknown'
        ),
    })
    unknown_0x4566b3ef: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4566b3ef, original_name='Unknown'
        ),
    })
    approach_player_chance: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6fe50d32, original_name='ApproachPlayerChance'
        ),
    })
    unknown_0x24f779ca: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0x24f779ca, original_name='Unknown'
        ),
    })
    armored_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xc6ba9753, original_name='ArmoredVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    armor_health: float = dataclasses.field(default=500.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x83439084, original_name='ArmorHealth'
        ),
    })
    armor_model1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x04547d34, original_name='ArmorModel1'
        ),
    })
    armor_model2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x82c00f9a, original_name='ArmorModel2'
        ),
    })
    armor_model3: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x499cdc3f, original_name='ArmorModel3'
        ),
    })
    armor_model4: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5499ec87, original_name='ArmorModel4'
        ),
    })
    armor_model5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9fc53f22, original_name='ArmorModel5'
        ),
    })
    unknown_0x09e8c7fd: float = dataclasses.field(default=1.399999976158142, metadata={
        'reflection': FieldReflection[float](
            float, id=0x09e8c7fd, original_name='Unknown'
        ),
    })
    weak_spot_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4ae57feb, original_name='WeakSpotModel'
        ),
    })
    provoked_head_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x4e1d71a1, original_name='ProvokedHeadVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_0x69d66ec4: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x69d66ec4, original_name='Unknown'
        ),
    })
    unknown_0x299916b2: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x299916b2, original_name='Unknown'
        ),
    })
    launch_projectile_data_0xfe51924e: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0xfe51924e, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    launch_projectile_data_0x9b9c702c: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x9b9c702c, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    launch_projectile_data_0x567ba94a: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x567ba94a, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    launch_projectile_data_0xf4d5150f: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0xf4d5150f, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    launch_projectile_data_0x8647c581: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x8647c581, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    unknown_0x15d26d26: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x15d26d26, original_name='Unknown'
        ),
    })
    unknown_0x81eaa9d4: float = dataclasses.field(default=250.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x81eaa9d4, original_name='Unknown'
        ),
    })
    is_gandrayda: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x531a8c85, original_name='IsGandrayda'
        ),
    })
    is_chieftain: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x677bd8ab, original_name='IsChieftain'
        ),
    })
    shoulder_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xc6e6300f, original_name='ShoulderVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    shoulder_health: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1520568a, original_name='ShoulderHealth'
        ),
    })
    unknown_0x268e5cb2: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x268e5cb2, original_name='Unknown'
        ),
    })
    left_shoulder_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x650ba238, original_name='LeftShoulderModel'
        ),
    })
    right_shoulder_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x68865410, original_name='RightShoulderModel'
        ),
    })
    weak_spot_armored_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x342dae7a, original_name='WeakSpotArmoredVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    damage_vulnerability_0x200545bd: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x200545bd, original_name='DamageVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    damage_vulnerability_0xf3ea94dc: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xf3ea94dc, original_name='DamageVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_0xedf1189f: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xedf1189f, original_name='Unknown'
        ),
    })
    minor_shockwave: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0x846533cc, original_name='MinorShockwave', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })
    shock_wave_info: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0x2af1548b, original_name='ShockWaveInfo', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })
    unknown_0x0c1a5644: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0c1a5644, original_name='Unknown'
        ),
    })
    unknown_0xc6af2fd0: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc6af2fd0, original_name='Unknown'
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
        if property_count != 71:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc0ac271e
        turn_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76ebc21a
        unknown_0x76ebc21a = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3e43d0e
        melee_attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4db42e3
        unknown_0xc4db42e3 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x74bffa78
        ball_slam_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbb7977b9
        damage_info_0xbb7977b9 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4738c321
        ground_pound_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf4e003c1
        pirate_as_projectile_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0dbf22f
        phazon_cannon_beam_info = PlasmaBeamInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x97321af1
        damage_info_0x97321af1 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd5e7062
        unknown_0xfd5e7062 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbd110814
        unknown_0xbd110814 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d947337
        unknown_0x3d947337 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a975a02
        unknown_0x1a975a02 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x066bc855
        launch_projectile_data_0x066bc855 = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x67e0e4b4
        unknown_0x67e0e4b4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb7ad7067
        unknown_0xb7ad7067 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf7e20811
        unknown_0xf7e20811 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4db474b8
        unknown_0x4db474b8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68d3daa4
        unknown_0x68d3daa4 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b359207
        unknown_0x1b359207 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc12f397a
        unknown_0xc12f397a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4bfee56b
        unknown_0x4bfee56b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f3be6e1
        unknown_0x8f3be6e1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd825dc3
        unknown_0xdd825dc3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x869415a3
        unknown_0x869415a3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6db6dd5
        unknown_0xc6db6dd5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdc8d7887
        phazon_grapple_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58e6d9b8
        unknown_0x58e6d9b8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf111a99
        unknown_0xcf111a99 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x719fd06b
        phazon_grapple_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x92f0b2c7
        unknown_0x92f0b2c7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc2f8f30
        unknown_0xbc2f8f30 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x910ad1e0
        unknown_0x910ad1e0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4566b3ef
        unknown_0x4566b3ef = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6fe50d32
        approach_player_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24f779ca
        unknown_0x24f779ca = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6ba9753
        armored_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x83439084
        armor_health = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x04547d34
        armor_model1 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x82c00f9a
        armor_model2 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x499cdc3f
        armor_model3 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5499ec87
        armor_model4 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9fc53f22
        armor_model5 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x09e8c7fd
        unknown_0x09e8c7fd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ae57feb
        weak_spot_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4e1d71a1
        provoked_head_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69d66ec4
        unknown_0x69d66ec4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x299916b2
        unknown_0x299916b2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe51924e
        launch_projectile_data_0xfe51924e = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9b9c702c
        launch_projectile_data_0x9b9c702c = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x567ba94a
        launch_projectile_data_0x567ba94a = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf4d5150f
        launch_projectile_data_0xf4d5150f = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8647c581
        launch_projectile_data_0x8647c581 = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15d26d26
        unknown_0x15d26d26 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81eaa9d4
        unknown_0x81eaa9d4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x531a8c85
        is_gandrayda = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x677bd8ab
        is_chieftain = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6e6300f
        shoulder_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1520568a
        shoulder_health = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x268e5cb2
        unknown_0x268e5cb2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x650ba238
        left_shoulder_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68865410
        right_shoulder_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x342dae7a
        weak_spot_armored_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x200545bd
        damage_vulnerability_0x200545bd = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3ea94dc
        damage_vulnerability_0xf3ea94dc = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xedf1189f
        unknown_0xedf1189f = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x846533cc
        minor_shockwave = ShockWaveInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2af1548b
        shock_wave_info = ShockWaveInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0c1a5644
        unknown_0x0c1a5644 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6af2fd0
        unknown_0xc6af2fd0 = struct.unpack('>f', data.read(4))[0]
    
        return cls(turn_threshold, unknown_0x76ebc21a, melee_attack_range, unknown_0xc4db42e3, ball_slam_damage, damage_info_0xbb7977b9, ground_pound_damage, pirate_as_projectile_damage, phazon_cannon_beam_info, damage_info_0x97321af1, unknown_0xfd5e7062, unknown_0xbd110814, unknown_0x3d947337, unknown_0x1a975a02, launch_projectile_data_0x066bc855, unknown_0x67e0e4b4, unknown_0xb7ad7067, unknown_0xf7e20811, unknown_0x4db474b8, unknown_0x68d3daa4, unknown_0x1b359207, unknown_0xc12f397a, unknown_0x4bfee56b, unknown_0x8f3be6e1, unknown_0xdd825dc3, unknown_0x869415a3, unknown_0xc6db6dd5, phazon_grapple_time, unknown_0x58e6d9b8, unknown_0xcf111a99, phazon_grapple_damage, unknown_0x92f0b2c7, unknown_0xbc2f8f30, unknown_0x910ad1e0, unknown_0x4566b3ef, approach_player_chance, unknown_0x24f779ca, armored_vulnerability, armor_health, armor_model1, armor_model2, armor_model3, armor_model4, armor_model5, unknown_0x09e8c7fd, weak_spot_model, provoked_head_vulnerability, unknown_0x69d66ec4, unknown_0x299916b2, launch_projectile_data_0xfe51924e, launch_projectile_data_0x9b9c702c, launch_projectile_data_0x567ba94a, launch_projectile_data_0xf4d5150f, launch_projectile_data_0x8647c581, unknown_0x15d26d26, unknown_0x81eaa9d4, is_gandrayda, is_chieftain, shoulder_vulnerability, shoulder_health, unknown_0x268e5cb2, left_shoulder_model, right_shoulder_model, weak_spot_armored_vulnerability, damage_vulnerability_0x200545bd, damage_vulnerability_0xf3ea94dc, unknown_0xedf1189f, minor_shockwave, shock_wave_info, unknown_0x0c1a5644, unknown_0xc6af2fd0)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00G')  # 71 properties

        data.write(b"\xc0\xac'\x1e")  # 0xc0ac271e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_threshold))

        data.write(b'v\xeb\xc2\x1a')  # 0x76ebc21a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x76ebc21a))

        data.write(b'\xc3\xe4=\x0e')  # 0xc3e43d0e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_attack_range))

        data.write(b'\xc4\xdbB\xe3')  # 0xc4db42e3
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xc4db42e3))

        data.write(b't\xbf\xfax')  # 0x74bffa78
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ball_slam_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbbyw\xb9')  # 0xbb7977b9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0xbb7977b9.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'G8\xc3!')  # 0x4738c321
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ground_pound_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf4\xe0\x03\xc1')  # 0xf4e003c1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.pirate_as_projectile_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe0\xdb\xf2/')  # 0xe0dbf22f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.phazon_cannon_beam_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x972\x1a\xf1')  # 0x97321af1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x97321af1.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfd^pb')  # 0xfd5e7062
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfd5e7062))

        data.write(b'\xbd\x11\x08\x14')  # 0xbd110814
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbd110814))

        data.write(b'=\x94s7')  # 0x3d947337
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3d947337))

        data.write(b'\x1a\x97Z\x02')  # 0x1a975a02
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1a975a02))

        data.write(b'\x06k\xc8U')  # 0x66bc855
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data_0x066bc855.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'g\xe0\xe4\xb4')  # 0x67e0e4b4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x67e0e4b4))

        data.write(b'\xb7\xadpg')  # 0xb7ad7067
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb7ad7067))

        data.write(b'\xf7\xe2\x08\x11')  # 0xf7e20811
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf7e20811))

        data.write(b'M\xb4t\xb8')  # 0x4db474b8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4db474b8))

        data.write(b'h\xd3\xda\xa4')  # 0x68d3daa4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x68d3daa4.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1b5\x92\x07')  # 0x1b359207
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1b359207))

        data.write(b'\xc1/9z')  # 0xc12f397a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc12f397a))

        data.write(b'K\xfe\xe5k')  # 0x4bfee56b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4bfee56b))

        data.write(b'\x8f;\xe6\xe1')  # 0x8f3be6e1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8f3be6e1))

        data.write(b'\xdd\x82]\xc3')  # 0xdd825dc3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdd825dc3))

        data.write(b'\x86\x94\x15\xa3')  # 0x869415a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x869415a3))

        data.write(b'\xc6\xdbm\xd5')  # 0xc6db6dd5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc6db6dd5))

        data.write(b'\xdc\x8dx\x87')  # 0xdc8d7887
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.phazon_grapple_time))

        data.write(b'X\xe6\xd9\xb8')  # 0x58e6d9b8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x58e6d9b8))

        data.write(b'\xcf\x11\x1a\x99')  # 0xcf111a99
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcf111a99))

        data.write(b'q\x9f\xd0k')  # 0x719fd06b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.phazon_grapple_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x92\xf0\xb2\xc7')  # 0x92f0b2c7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x92f0b2c7))

        data.write(b'\xbc/\x8f0')  # 0xbc2f8f30
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbc2f8f30))

        data.write(b'\x91\n\xd1\xe0')  # 0x910ad1e0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x910ad1e0))

        data.write(b'Ef\xb3\xef')  # 0x4566b3ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4566b3ef))

        data.write(b'o\xe5\r2')  # 0x6fe50d32
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.approach_player_chance))

        data.write(b'$\xf7y\xca')  # 0x24f779ca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x24f779ca))

        data.write(b'\xc6\xba\x97S')  # 0xc6ba9753
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.armored_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x83C\x90\x84')  # 0x83439084
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.armor_health))

        data.write(b'\x04T}4')  # 0x4547d34
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.armor_model1))

        data.write(b'\x82\xc0\x0f\x9a')  # 0x82c00f9a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.armor_model2))

        data.write(b'I\x9c\xdc?')  # 0x499cdc3f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.armor_model3))

        data.write(b'T\x99\xec\x87')  # 0x5499ec87
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.armor_model4))

        data.write(b'\x9f\xc5?"')  # 0x9fc53f22
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.armor_model5))

        data.write(b'\t\xe8\xc7\xfd')  # 0x9e8c7fd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x09e8c7fd))

        data.write(b'J\xe5\x7f\xeb')  # 0x4ae57feb
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.weak_spot_model))

        data.write(b'N\x1dq\xa1')  # 0x4e1d71a1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.provoked_head_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'i\xd6n\xc4')  # 0x69d66ec4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x69d66ec4))

        data.write(b')\x99\x16\xb2')  # 0x299916b2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x299916b2))

        data.write(b'\xfeQ\x92N')  # 0xfe51924e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data_0xfe51924e.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9b\x9cp,')  # 0x9b9c702c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data_0x9b9c702c.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'V{\xa9J')  # 0x567ba94a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data_0x567ba94a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf4\xd5\x15\x0f')  # 0xf4d5150f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data_0xf4d5150f.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x86G\xc5\x81')  # 0x8647c581
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data_0x8647c581.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x15\xd2m&')  # 0x15d26d26
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x15d26d26))

        data.write(b'\x81\xea\xa9\xd4')  # 0x81eaa9d4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x81eaa9d4))

        data.write(b'S\x1a\x8c\x85')  # 0x531a8c85
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_gandrayda))

        data.write(b'g{\xd8\xab')  # 0x677bd8ab
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_chieftain))

        data.write(b'\xc6\xe60\x0f')  # 0xc6e6300f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shoulder_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x15 V\x8a')  # 0x1520568a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.shoulder_health))

        data.write(b'&\x8e\\\xb2')  # 0x268e5cb2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x268e5cb2))

        data.write(b'e\x0b\xa28')  # 0x650ba238
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.left_shoulder_model))

        data.write(b'h\x86T\x10')  # 0x68865410
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.right_shoulder_model))

        data.write(b'4-\xaez')  # 0x342dae7a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weak_spot_armored_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b' \x05E\xbd')  # 0x200545bd
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_vulnerability_0x200545bd.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf3\xea\x94\xdc')  # 0xf3ea94dc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_vulnerability_0xf3ea94dc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed\xf1\x18\x9f')  # 0xedf1189f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xedf1189f))

        data.write(b'\x84e3\xcc')  # 0x846533cc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.minor_shockwave.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'*\xf1T\x8b')  # 0x2af1548b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shock_wave_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0c\x1aVD')  # 0xc1a5644
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0c1a5644))

        data.write(b'\xc6\xaf/\xd0')  # 0xc6af2fd0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc6af2fd0))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("BerserkerDataJson", data)
        return cls(
            turn_threshold=json_data['turn_threshold'],
            unknown_0x76ebc21a=json_data['unknown_0x76ebc21a'],
            melee_attack_range=json_data['melee_attack_range'],
            unknown_0xc4db42e3=json_data['unknown_0xc4db42e3'],
            ball_slam_damage=DamageInfo.from_json(json_data['ball_slam_damage']),
            damage_info_0xbb7977b9=DamageInfo.from_json(json_data['damage_info_0xbb7977b9']),
            ground_pound_damage=DamageInfo.from_json(json_data['ground_pound_damage']),
            pirate_as_projectile_damage=DamageInfo.from_json(json_data['pirate_as_projectile_damage']),
            phazon_cannon_beam_info=PlasmaBeamInfo.from_json(json_data['phazon_cannon_beam_info']),
            damage_info_0x97321af1=DamageInfo.from_json(json_data['damage_info_0x97321af1']),
            unknown_0xfd5e7062=json_data['unknown_0xfd5e7062'],
            unknown_0xbd110814=json_data['unknown_0xbd110814'],
            unknown_0x3d947337=json_data['unknown_0x3d947337'],
            unknown_0x1a975a02=json_data['unknown_0x1a975a02'],
            launch_projectile_data_0x066bc855=LaunchProjectileData.from_json(json_data['launch_projectile_data_0x066bc855']),
            unknown_0x67e0e4b4=json_data['unknown_0x67e0e4b4'],
            unknown_0xb7ad7067=json_data['unknown_0xb7ad7067'],
            unknown_0xf7e20811=json_data['unknown_0xf7e20811'],
            unknown_0x4db474b8=json_data['unknown_0x4db474b8'],
            unknown_0x68d3daa4=Spline.from_json(json_data['unknown_0x68d3daa4']),
            unknown_0x1b359207=json_data['unknown_0x1b359207'],
            unknown_0xc12f397a=json_data['unknown_0xc12f397a'],
            unknown_0x4bfee56b=json_data['unknown_0x4bfee56b'],
            unknown_0x8f3be6e1=json_data['unknown_0x8f3be6e1'],
            unknown_0xdd825dc3=json_data['unknown_0xdd825dc3'],
            unknown_0x869415a3=json_data['unknown_0x869415a3'],
            unknown_0xc6db6dd5=json_data['unknown_0xc6db6dd5'],
            phazon_grapple_time=json_data['phazon_grapple_time'],
            unknown_0x58e6d9b8=json_data['unknown_0x58e6d9b8'],
            unknown_0xcf111a99=json_data['unknown_0xcf111a99'],
            phazon_grapple_damage=DamageInfo.from_json(json_data['phazon_grapple_damage']),
            unknown_0x92f0b2c7=json_data['unknown_0x92f0b2c7'],
            unknown_0xbc2f8f30=json_data['unknown_0xbc2f8f30'],
            unknown_0x910ad1e0=json_data['unknown_0x910ad1e0'],
            unknown_0x4566b3ef=json_data['unknown_0x4566b3ef'],
            approach_player_chance=json_data['approach_player_chance'],
            unknown_0x24f779ca=json_data['unknown_0x24f779ca'],
            armored_vulnerability=DamageVulnerability.from_json(json_data['armored_vulnerability']),
            armor_health=json_data['armor_health'],
            armor_model1=json_data['armor_model1'],
            armor_model2=json_data['armor_model2'],
            armor_model3=json_data['armor_model3'],
            armor_model4=json_data['armor_model4'],
            armor_model5=json_data['armor_model5'],
            unknown_0x09e8c7fd=json_data['unknown_0x09e8c7fd'],
            weak_spot_model=json_data['weak_spot_model'],
            provoked_head_vulnerability=DamageVulnerability.from_json(json_data['provoked_head_vulnerability']),
            unknown_0x69d66ec4=json_data['unknown_0x69d66ec4'],
            unknown_0x299916b2=json_data['unknown_0x299916b2'],
            launch_projectile_data_0xfe51924e=LaunchProjectileData.from_json(json_data['launch_projectile_data_0xfe51924e']),
            launch_projectile_data_0x9b9c702c=LaunchProjectileData.from_json(json_data['launch_projectile_data_0x9b9c702c']),
            launch_projectile_data_0x567ba94a=LaunchProjectileData.from_json(json_data['launch_projectile_data_0x567ba94a']),
            launch_projectile_data_0xf4d5150f=LaunchProjectileData.from_json(json_data['launch_projectile_data_0xf4d5150f']),
            launch_projectile_data_0x8647c581=LaunchProjectileData.from_json(json_data['launch_projectile_data_0x8647c581']),
            unknown_0x15d26d26=json_data['unknown_0x15d26d26'],
            unknown_0x81eaa9d4=json_data['unknown_0x81eaa9d4'],
            is_gandrayda=json_data['is_gandrayda'],
            is_chieftain=json_data['is_chieftain'],
            shoulder_vulnerability=DamageVulnerability.from_json(json_data['shoulder_vulnerability']),
            shoulder_health=json_data['shoulder_health'],
            unknown_0x268e5cb2=json_data['unknown_0x268e5cb2'],
            left_shoulder_model=json_data['left_shoulder_model'],
            right_shoulder_model=json_data['right_shoulder_model'],
            weak_spot_armored_vulnerability=DamageVulnerability.from_json(json_data['weak_spot_armored_vulnerability']),
            damage_vulnerability_0x200545bd=DamageVulnerability.from_json(json_data['damage_vulnerability_0x200545bd']),
            damage_vulnerability_0xf3ea94dc=DamageVulnerability.from_json(json_data['damage_vulnerability_0xf3ea94dc']),
            unknown_0xedf1189f=json_data['unknown_0xedf1189f'],
            minor_shockwave=ShockWaveInfo.from_json(json_data['minor_shockwave']),
            shock_wave_info=ShockWaveInfo.from_json(json_data['shock_wave_info']),
            unknown_0x0c1a5644=json_data['unknown_0x0c1a5644'],
            unknown_0xc6af2fd0=json_data['unknown_0xc6af2fd0'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'turn_threshold': self.turn_threshold,
            'unknown_0x76ebc21a': self.unknown_0x76ebc21a,
            'melee_attack_range': self.melee_attack_range,
            'unknown_0xc4db42e3': self.unknown_0xc4db42e3,
            'ball_slam_damage': self.ball_slam_damage.to_json(),
            'damage_info_0xbb7977b9': self.damage_info_0xbb7977b9.to_json(),
            'ground_pound_damage': self.ground_pound_damage.to_json(),
            'pirate_as_projectile_damage': self.pirate_as_projectile_damage.to_json(),
            'phazon_cannon_beam_info': self.phazon_cannon_beam_info.to_json(),
            'damage_info_0x97321af1': self.damage_info_0x97321af1.to_json(),
            'unknown_0xfd5e7062': self.unknown_0xfd5e7062,
            'unknown_0xbd110814': self.unknown_0xbd110814,
            'unknown_0x3d947337': self.unknown_0x3d947337,
            'unknown_0x1a975a02': self.unknown_0x1a975a02,
            'launch_projectile_data_0x066bc855': self.launch_projectile_data_0x066bc855.to_json(),
            'unknown_0x67e0e4b4': self.unknown_0x67e0e4b4,
            'unknown_0xb7ad7067': self.unknown_0xb7ad7067,
            'unknown_0xf7e20811': self.unknown_0xf7e20811,
            'unknown_0x4db474b8': self.unknown_0x4db474b8,
            'unknown_0x68d3daa4': self.unknown_0x68d3daa4.to_json(),
            'unknown_0x1b359207': self.unknown_0x1b359207,
            'unknown_0xc12f397a': self.unknown_0xc12f397a,
            'unknown_0x4bfee56b': self.unknown_0x4bfee56b,
            'unknown_0x8f3be6e1': self.unknown_0x8f3be6e1,
            'unknown_0xdd825dc3': self.unknown_0xdd825dc3,
            'unknown_0x869415a3': self.unknown_0x869415a3,
            'unknown_0xc6db6dd5': self.unknown_0xc6db6dd5,
            'phazon_grapple_time': self.phazon_grapple_time,
            'unknown_0x58e6d9b8': self.unknown_0x58e6d9b8,
            'unknown_0xcf111a99': self.unknown_0xcf111a99,
            'phazon_grapple_damage': self.phazon_grapple_damage.to_json(),
            'unknown_0x92f0b2c7': self.unknown_0x92f0b2c7,
            'unknown_0xbc2f8f30': self.unknown_0xbc2f8f30,
            'unknown_0x910ad1e0': self.unknown_0x910ad1e0,
            'unknown_0x4566b3ef': self.unknown_0x4566b3ef,
            'approach_player_chance': self.approach_player_chance,
            'unknown_0x24f779ca': self.unknown_0x24f779ca,
            'armored_vulnerability': self.armored_vulnerability.to_json(),
            'armor_health': self.armor_health,
            'armor_model1': self.armor_model1,
            'armor_model2': self.armor_model2,
            'armor_model3': self.armor_model3,
            'armor_model4': self.armor_model4,
            'armor_model5': self.armor_model5,
            'unknown_0x09e8c7fd': self.unknown_0x09e8c7fd,
            'weak_spot_model': self.weak_spot_model,
            'provoked_head_vulnerability': self.provoked_head_vulnerability.to_json(),
            'unknown_0x69d66ec4': self.unknown_0x69d66ec4,
            'unknown_0x299916b2': self.unknown_0x299916b2,
            'launch_projectile_data_0xfe51924e': self.launch_projectile_data_0xfe51924e.to_json(),
            'launch_projectile_data_0x9b9c702c': self.launch_projectile_data_0x9b9c702c.to_json(),
            'launch_projectile_data_0x567ba94a': self.launch_projectile_data_0x567ba94a.to_json(),
            'launch_projectile_data_0xf4d5150f': self.launch_projectile_data_0xf4d5150f.to_json(),
            'launch_projectile_data_0x8647c581': self.launch_projectile_data_0x8647c581.to_json(),
            'unknown_0x15d26d26': self.unknown_0x15d26d26,
            'unknown_0x81eaa9d4': self.unknown_0x81eaa9d4,
            'is_gandrayda': self.is_gandrayda,
            'is_chieftain': self.is_chieftain,
            'shoulder_vulnerability': self.shoulder_vulnerability.to_json(),
            'shoulder_health': self.shoulder_health,
            'unknown_0x268e5cb2': self.unknown_0x268e5cb2,
            'left_shoulder_model': self.left_shoulder_model,
            'right_shoulder_model': self.right_shoulder_model,
            'weak_spot_armored_vulnerability': self.weak_spot_armored_vulnerability.to_json(),
            'damage_vulnerability_0x200545bd': self.damage_vulnerability_0x200545bd.to_json(),
            'damage_vulnerability_0xf3ea94dc': self.damage_vulnerability_0xf3ea94dc.to_json(),
            'unknown_0xedf1189f': self.unknown_0xedf1189f,
            'minor_shockwave': self.minor_shockwave.to_json(),
            'shock_wave_info': self.shock_wave_info.to_json(),
            'unknown_0x0c1a5644': self.unknown_0x0c1a5644,
            'unknown_0xc6af2fd0': self.unknown_0xc6af2fd0,
        }


def _decode_turn_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x76ebc21a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_melee_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc4db42e3(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xfd5e7062(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbd110814(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3d947337(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1a975a02(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x67e0e4b4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb7ad7067(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf7e20811(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4db474b8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1b359207(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc12f397a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4bfee56b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8f3be6e1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdd825dc3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x869415a3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc6db6dd5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_phazon_grapple_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x58e6d9b8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcf111a99(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x92f0b2c7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbc2f8f30(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x910ad1e0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4566b3ef(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_approach_player_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x24f779ca(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_armor_health(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_armor_model1(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_armor_model2(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_armor_model3(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_armor_model4(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_armor_model5(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x09e8c7fd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_weak_spot_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x69d66ec4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x299916b2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x15d26d26(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x81eaa9d4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_is_gandrayda(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_is_chieftain(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_shoulder_health(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x268e5cb2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_left_shoulder_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_right_shoulder_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xedf1189f(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x0c1a5644(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc6af2fd0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc0ac271e: ('turn_threshold', _decode_turn_threshold),
    0x76ebc21a: ('unknown_0x76ebc21a', _decode_unknown_0x76ebc21a),
    0xc3e43d0e: ('melee_attack_range', _decode_melee_attack_range),
    0xc4db42e3: ('unknown_0xc4db42e3', _decode_unknown_0xc4db42e3),
    0x74bffa78: ('ball_slam_damage', DamageInfo.from_stream),
    0xbb7977b9: ('damage_info_0xbb7977b9', DamageInfo.from_stream),
    0x4738c321: ('ground_pound_damage', DamageInfo.from_stream),
    0xf4e003c1: ('pirate_as_projectile_damage', DamageInfo.from_stream),
    0xe0dbf22f: ('phazon_cannon_beam_info', PlasmaBeamInfo.from_stream),
    0x97321af1: ('damage_info_0x97321af1', DamageInfo.from_stream),
    0xfd5e7062: ('unknown_0xfd5e7062', _decode_unknown_0xfd5e7062),
    0xbd110814: ('unknown_0xbd110814', _decode_unknown_0xbd110814),
    0x3d947337: ('unknown_0x3d947337', _decode_unknown_0x3d947337),
    0x1a975a02: ('unknown_0x1a975a02', _decode_unknown_0x1a975a02),
    0x66bc855: ('launch_projectile_data_0x066bc855', LaunchProjectileData.from_stream),
    0x67e0e4b4: ('unknown_0x67e0e4b4', _decode_unknown_0x67e0e4b4),
    0xb7ad7067: ('unknown_0xb7ad7067', _decode_unknown_0xb7ad7067),
    0xf7e20811: ('unknown_0xf7e20811', _decode_unknown_0xf7e20811),
    0x4db474b8: ('unknown_0x4db474b8', _decode_unknown_0x4db474b8),
    0x68d3daa4: ('unknown_0x68d3daa4', Spline.from_stream),
    0x1b359207: ('unknown_0x1b359207', _decode_unknown_0x1b359207),
    0xc12f397a: ('unknown_0xc12f397a', _decode_unknown_0xc12f397a),
    0x4bfee56b: ('unknown_0x4bfee56b', _decode_unknown_0x4bfee56b),
    0x8f3be6e1: ('unknown_0x8f3be6e1', _decode_unknown_0x8f3be6e1),
    0xdd825dc3: ('unknown_0xdd825dc3', _decode_unknown_0xdd825dc3),
    0x869415a3: ('unknown_0x869415a3', _decode_unknown_0x869415a3),
    0xc6db6dd5: ('unknown_0xc6db6dd5', _decode_unknown_0xc6db6dd5),
    0xdc8d7887: ('phazon_grapple_time', _decode_phazon_grapple_time),
    0x58e6d9b8: ('unknown_0x58e6d9b8', _decode_unknown_0x58e6d9b8),
    0xcf111a99: ('unknown_0xcf111a99', _decode_unknown_0xcf111a99),
    0x719fd06b: ('phazon_grapple_damage', DamageInfo.from_stream),
    0x92f0b2c7: ('unknown_0x92f0b2c7', _decode_unknown_0x92f0b2c7),
    0xbc2f8f30: ('unknown_0xbc2f8f30', _decode_unknown_0xbc2f8f30),
    0x910ad1e0: ('unknown_0x910ad1e0', _decode_unknown_0x910ad1e0),
    0x4566b3ef: ('unknown_0x4566b3ef', _decode_unknown_0x4566b3ef),
    0x6fe50d32: ('approach_player_chance', _decode_approach_player_chance),
    0x24f779ca: ('unknown_0x24f779ca', _decode_unknown_0x24f779ca),
    0xc6ba9753: ('armored_vulnerability', DamageVulnerability.from_stream),
    0x83439084: ('armor_health', _decode_armor_health),
    0x4547d34: ('armor_model1', _decode_armor_model1),
    0x82c00f9a: ('armor_model2', _decode_armor_model2),
    0x499cdc3f: ('armor_model3', _decode_armor_model3),
    0x5499ec87: ('armor_model4', _decode_armor_model4),
    0x9fc53f22: ('armor_model5', _decode_armor_model5),
    0x9e8c7fd: ('unknown_0x09e8c7fd', _decode_unknown_0x09e8c7fd),
    0x4ae57feb: ('weak_spot_model', _decode_weak_spot_model),
    0x4e1d71a1: ('provoked_head_vulnerability', DamageVulnerability.from_stream),
    0x69d66ec4: ('unknown_0x69d66ec4', _decode_unknown_0x69d66ec4),
    0x299916b2: ('unknown_0x299916b2', _decode_unknown_0x299916b2),
    0xfe51924e: ('launch_projectile_data_0xfe51924e', LaunchProjectileData.from_stream),
    0x9b9c702c: ('launch_projectile_data_0x9b9c702c', LaunchProjectileData.from_stream),
    0x567ba94a: ('launch_projectile_data_0x567ba94a', LaunchProjectileData.from_stream),
    0xf4d5150f: ('launch_projectile_data_0xf4d5150f', LaunchProjectileData.from_stream),
    0x8647c581: ('launch_projectile_data_0x8647c581', LaunchProjectileData.from_stream),
    0x15d26d26: ('unknown_0x15d26d26', _decode_unknown_0x15d26d26),
    0x81eaa9d4: ('unknown_0x81eaa9d4', _decode_unknown_0x81eaa9d4),
    0x531a8c85: ('is_gandrayda', _decode_is_gandrayda),
    0x677bd8ab: ('is_chieftain', _decode_is_chieftain),
    0xc6e6300f: ('shoulder_vulnerability', DamageVulnerability.from_stream),
    0x1520568a: ('shoulder_health', _decode_shoulder_health),
    0x268e5cb2: ('unknown_0x268e5cb2', _decode_unknown_0x268e5cb2),
    0x650ba238: ('left_shoulder_model', _decode_left_shoulder_model),
    0x68865410: ('right_shoulder_model', _decode_right_shoulder_model),
    0x342dae7a: ('weak_spot_armored_vulnerability', DamageVulnerability.from_stream),
    0x200545bd: ('damage_vulnerability_0x200545bd', DamageVulnerability.from_stream),
    0xf3ea94dc: ('damage_vulnerability_0xf3ea94dc', DamageVulnerability.from_stream),
    0xedf1189f: ('unknown_0xedf1189f', _decode_unknown_0xedf1189f),
    0x846533cc: ('minor_shockwave', ShockWaveInfo.from_stream),
    0x2af1548b: ('shock_wave_info', ShockWaveInfo.from_stream),
    0xc1a5644: ('unknown_0x0c1a5644', _decode_unknown_0x0c1a5644),
    0xc6af2fd0: ('unknown_0xc6af2fd0', _decode_unknown_0xc6af2fd0),
}
