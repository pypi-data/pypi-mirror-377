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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class BlinkWolfDataJson(typing_extensions.TypedDict):
        unknown_0x2b3109a6: bool
        start_invisible: bool
        unknown_0x7fdee42c: float
        turn_prediction: float
        spit_prediction: float
        approach_dist: float
        unknown_0x6d6c84cb: float
        jump_apex: float
        min_spit_range: float
        max_spit_range: float
        unknown_0xb6055f35: int
        spit_starting: json_util.JsonObject
        spit_full_speed: json_util.JsonObject
        launch_projectile_data_0x76b1b8e0: json_util.JsonObject
        launch_projectile_data_0xfe3b5965: json_util.JsonObject
        caud: int
        sound_teleport_end: int
        max_head_rotation: float
        head_rotation_speed: float
        unknown_0x0f5a3164: float
        unknown_0x190d9fc8: float
        unknown_0xfcae3411: float
        unknown_0x7ecb92ca: float
        burn_damage: float
        burn_damage_duration: float
        shockwave_range: float
        shockwave_damage: json_util.JsonObject
        shockwave_intensity: float
        unknown_0xb39833c0: float
        unknown_0x96bd6426: float
        unknown_0xd7aa5ba0: float
        blink_out: int
        blink_bubble: int
        min_bubble_time: float
        max_bubble_time: float
        min_blink_range: float
        unknown_0x8e5f1638: float
        warp_increase_intensity: float
        warp_intensity_max: float
        unknown_0x22794c6d: float
        unknown_0x5b9cc474: float
        warp_duration_max: float
        frozen_gib_time: float
        avoidance_range: float
        hearing_radius: float
        recheck_path_time: float
        recheck_path_distance: float
        pain_threshold: float
        unknown_0xa6c1631d: float
        unknown_0x312e194a: float
        unknown_0xc6f92e2f: float
        player_scan_delay: float
        unknown_0x108e8ed8: float
        max_fall_time: float
        unknown_0xc34bffca: float
        unknown_0xf5aa6363: float
        unknown_0xd40c2b10: float
        unknown_0x6bbf9cdc: float
        unknown_0xb2dd7c06: float
    

@dataclasses.dataclass()
class BlinkWolfData(BaseProperty):
    unknown_0x2b3109a6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2b3109a6, original_name='Unknown'
        ),
    })
    start_invisible: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xbb5c37e0, original_name='StartInvisible'
        ),
    })
    unknown_0x7fdee42c: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7fdee42c, original_name='Unknown'
        ),
    })
    turn_prediction: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x983954ae, original_name='TurnPrediction'
        ),
    })
    spit_prediction: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x86b2b7d7, original_name='SpitPrediction'
        ),
    })
    approach_dist: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa1d7e06b, original_name='ApproachDist'
        ),
    })
    unknown_0x6d6c84cb: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6d6c84cb, original_name='Unknown'
        ),
    })
    jump_apex: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf2782501, original_name='JumpApex'
        ),
    })
    min_spit_range: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0236c750, original_name='MinSpitRange'
        ),
    })
    max_spit_range: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x17bd13a2, original_name='MaxSpitRange'
        ),
    })
    unknown_0xb6055f35: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb6055f35, original_name='Unknown'
        ),
    })
    spit_starting: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x6dac116a, original_name='SpitStarting', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    spit_full_speed: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x9aab30f1, original_name='SpitFullSpeed', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    launch_projectile_data_0x76b1b8e0: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x76b1b8e0, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    launch_projectile_data_0xfe3b5965: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0xfe3b5965, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    caud: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x95eaaacb, original_name='CAUD'
        ),
    })
    sound_teleport_end: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd4c88dd1, original_name='Sound_TeleportEnd'
        ),
    })
    max_head_rotation: float = dataclasses.field(default=70.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe68cebb0, original_name='MaxHeadRotation'
        ),
    })
    head_rotation_speed: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b7fcf8c, original_name='HeadRotationSpeed'
        ),
    })
    unknown_0x0f5a3164: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0f5a3164, original_name='Unknown'
        ),
    })
    unknown_0x190d9fc8: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x190d9fc8, original_name='Unknown'
        ),
    })
    unknown_0xfcae3411: float = dataclasses.field(default=24.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfcae3411, original_name='Unknown'
        ),
    })
    unknown_0x7ecb92ca: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7ecb92ca, original_name='Unknown'
        ),
    })
    burn_damage: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcf201bfa, original_name='BurnDamage'
        ),
    })
    burn_damage_duration: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcf495aab, original_name='BurnDamageDuration'
        ),
    })
    shockwave_range: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8d518fd5, original_name='ShockwaveRange'
        ),
    })
    shockwave_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0f2fa713, original_name='ShockwaveDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    shockwave_intensity: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa42dbd9e, original_name='ShockwaveIntensity'
        ),
    })
    unknown_0xb39833c0: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb39833c0, original_name='Unknown'
        ),
    })
    unknown_0x96bd6426: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x96bd6426, original_name='Unknown'
        ),
    })
    unknown_0xd7aa5ba0: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd7aa5ba0, original_name='Unknown'
        ),
    })
    blink_out: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2050f248, original_name='BlinkOut'
        ),
    })
    blink_bubble: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9cb2109a, original_name='BlinkBubble'
        ),
    })
    min_bubble_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4ce0d7e5, original_name='MinBubbleTime'
        ),
    })
    max_bubble_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1f46cf01, original_name='MaxBubbleTime'
        ),
    })
    min_blink_range: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0fc0b9e3, original_name='MinBlinkRange'
        ),
    })
    unknown_0x8e5f1638: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8e5f1638, original_name='Unknown'
        ),
    })
    warp_increase_intensity: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf7ba9e21, original_name='WarpIncreaseIntensity'
        ),
    })
    warp_intensity_max: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1e501419, original_name='WarpIntensityMax'
        ),
    })
    unknown_0x22794c6d: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x22794c6d, original_name='Unknown'
        ),
    })
    unknown_0x5b9cc474: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5b9cc474, original_name='Unknown'
        ),
    })
    warp_duration_max: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x08f1e9d3, original_name='WarpDurationMax'
        ),
    })
    frozen_gib_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x51bb4b6f, original_name='FrozenGibTime'
        ),
    })
    avoidance_range: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x50a9bd0d, original_name='AvoidanceRange'
        ),
    })
    hearing_radius: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed69488f, original_name='HearingRadius'
        ),
    })
    recheck_path_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9aa90b6b, original_name='RecheckPathTime'
        ),
    })
    recheck_path_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7626ec89, original_name='RecheckPathDistance'
        ),
    })
    pain_threshold: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x13a15b89, original_name='PainThreshold'
        ),
    })
    unknown_0xa6c1631d: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa6c1631d, original_name='Unknown'
        ),
    })
    unknown_0x312e194a: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x312e194a, original_name='Unknown'
        ),
    })
    unknown_0xc6f92e2f: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc6f92e2f, original_name='Unknown'
        ),
    })
    player_scan_delay: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1f844b33, original_name='PlayerScanDelay'
        ),
    })
    unknown_0x108e8ed8: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x108e8ed8, original_name='Unknown'
        ),
    })
    max_fall_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x74cc0ccf, original_name='MaxFallTime'
        ),
    })
    unknown_0xc34bffca: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc34bffca, original_name='Unknown'
        ),
    })
    unknown_0xf5aa6363: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf5aa6363, original_name='Unknown'
        ),
    })
    unknown_0xd40c2b10: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd40c2b10, original_name='Unknown'
        ),
    })
    unknown_0x6bbf9cdc: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6bbf9cdc, original_name='Unknown'
        ),
    })
    unknown_0xb2dd7c06: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb2dd7c06, original_name='Unknown'
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
        if property_count != 59:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b3109a6
        unknown_0x2b3109a6 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbb5c37e0
        start_invisible = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fdee42c
        unknown_0x7fdee42c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x983954ae
        turn_prediction = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x86b2b7d7
        spit_prediction = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa1d7e06b
        approach_dist = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d6c84cb
        unknown_0x6d6c84cb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf2782501
        jump_apex = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0236c750
        min_spit_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x17bd13a2
        max_spit_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb6055f35
        unknown_0xb6055f35 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6dac116a
        spit_starting = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9aab30f1
        spit_full_speed = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76b1b8e0
        launch_projectile_data_0x76b1b8e0 = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe3b5965
        launch_projectile_data_0xfe3b5965 = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95eaaacb
        caud = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4c88dd1
        sound_teleport_end = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe68cebb0
        max_head_rotation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b7fcf8c
        head_rotation_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0f5a3164
        unknown_0x0f5a3164 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x190d9fc8
        unknown_0x190d9fc8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfcae3411
        unknown_0xfcae3411 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7ecb92ca
        unknown_0x7ecb92ca = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf201bfa
        burn_damage = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf495aab
        burn_damage_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d518fd5
        shockwave_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0f2fa713
        shockwave_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa42dbd9e
        shockwave_intensity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb39833c0
        unknown_0xb39833c0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x96bd6426
        unknown_0x96bd6426 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd7aa5ba0
        unknown_0xd7aa5ba0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2050f248
        blink_out = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9cb2109a
        blink_bubble = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ce0d7e5
        min_bubble_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1f46cf01
        max_bubble_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0fc0b9e3
        min_blink_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8e5f1638
        unknown_0x8e5f1638 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf7ba9e21
        warp_increase_intensity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1e501419
        warp_intensity_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x22794c6d
        unknown_0x22794c6d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5b9cc474
        unknown_0x5b9cc474 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08f1e9d3
        warp_duration_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x51bb4b6f
        frozen_gib_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x50a9bd0d
        avoidance_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed69488f
        hearing_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9aa90b6b
        recheck_path_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7626ec89
        recheck_path_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13a15b89
        pain_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6c1631d
        unknown_0xa6c1631d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x312e194a
        unknown_0x312e194a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6f92e2f
        unknown_0xc6f92e2f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1f844b33
        player_scan_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x108e8ed8
        unknown_0x108e8ed8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x74cc0ccf
        max_fall_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc34bffca
        unknown_0xc34bffca = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5aa6363
        unknown_0xf5aa6363 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd40c2b10
        unknown_0xd40c2b10 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6bbf9cdc
        unknown_0x6bbf9cdc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2dd7c06
        unknown_0xb2dd7c06 = struct.unpack('>f', data.read(4))[0]
    
        return cls(unknown_0x2b3109a6, start_invisible, unknown_0x7fdee42c, turn_prediction, spit_prediction, approach_dist, unknown_0x6d6c84cb, jump_apex, min_spit_range, max_spit_range, unknown_0xb6055f35, spit_starting, spit_full_speed, launch_projectile_data_0x76b1b8e0, launch_projectile_data_0xfe3b5965, caud, sound_teleport_end, max_head_rotation, head_rotation_speed, unknown_0x0f5a3164, unknown_0x190d9fc8, unknown_0xfcae3411, unknown_0x7ecb92ca, burn_damage, burn_damage_duration, shockwave_range, shockwave_damage, shockwave_intensity, unknown_0xb39833c0, unknown_0x96bd6426, unknown_0xd7aa5ba0, blink_out, blink_bubble, min_bubble_time, max_bubble_time, min_blink_range, unknown_0x8e5f1638, warp_increase_intensity, warp_intensity_max, unknown_0x22794c6d, unknown_0x5b9cc474, warp_duration_max, frozen_gib_time, avoidance_range, hearing_radius, recheck_path_time, recheck_path_distance, pain_threshold, unknown_0xa6c1631d, unknown_0x312e194a, unknown_0xc6f92e2f, player_scan_delay, unknown_0x108e8ed8, max_fall_time, unknown_0xc34bffca, unknown_0xf5aa6363, unknown_0xd40c2b10, unknown_0x6bbf9cdc, unknown_0xb2dd7c06)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00;')  # 59 properties

        data.write(b'+1\t\xa6')  # 0x2b3109a6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x2b3109a6))

        data.write(b'\xbb\\7\xe0')  # 0xbb5c37e0
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.start_invisible))

        data.write(b'\x7f\xde\xe4,')  # 0x7fdee42c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7fdee42c))

        data.write(b'\x989T\xae')  # 0x983954ae
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_prediction))

        data.write(b'\x86\xb2\xb7\xd7')  # 0x86b2b7d7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.spit_prediction))

        data.write(b'\xa1\xd7\xe0k')  # 0xa1d7e06b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.approach_dist))

        data.write(b'ml\x84\xcb')  # 0x6d6c84cb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6d6c84cb))

        data.write(b'\xf2x%\x01')  # 0xf2782501
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.jump_apex))

        data.write(b'\x026\xc7P')  # 0x236c750
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_spit_range))

        data.write(b'\x17\xbd\x13\xa2')  # 0x17bd13a2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_spit_range))

        data.write(b'\xb6\x05_5')  # 0xb6055f35
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xb6055f35))

        data.write(b'm\xac\x11j')  # 0x6dac116a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spit_starting.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9a\xab0\xf1')  # 0x9aab30f1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spit_full_speed.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'v\xb1\xb8\xe0')  # 0x76b1b8e0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data_0x76b1b8e0.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfe;Ye')  # 0xfe3b5965
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data_0xfe3b5965.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x95\xea\xaa\xcb')  # 0x95eaaacb
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud))

        data.write(b'\xd4\xc8\x8d\xd1')  # 0xd4c88dd1
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_teleport_end))

        data.write(b'\xe6\x8c\xeb\xb0')  # 0xe68cebb0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_head_rotation))

        data.write(b'\x8b\x7f\xcf\x8c')  # 0x8b7fcf8c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.head_rotation_speed))

        data.write(b'\x0fZ1d')  # 0xf5a3164
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0f5a3164))

        data.write(b'\x19\r\x9f\xc8')  # 0x190d9fc8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x190d9fc8))

        data.write(b'\xfc\xae4\x11')  # 0xfcae3411
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfcae3411))

        data.write(b'~\xcb\x92\xca')  # 0x7ecb92ca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7ecb92ca))

        data.write(b'\xcf \x1b\xfa')  # 0xcf201bfa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.burn_damage))

        data.write(b'\xcfIZ\xab')  # 0xcf495aab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.burn_damage_duration))

        data.write(b'\x8dQ\x8f\xd5')  # 0x8d518fd5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.shockwave_range))

        data.write(b'\x0f/\xa7\x13')  # 0xf2fa713
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shockwave_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa4-\xbd\x9e')  # 0xa42dbd9e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.shockwave_intensity))

        data.write(b'\xb3\x983\xc0')  # 0xb39833c0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb39833c0))

        data.write(b'\x96\xbdd&')  # 0x96bd6426
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x96bd6426))

        data.write(b'\xd7\xaa[\xa0')  # 0xd7aa5ba0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd7aa5ba0))

        data.write(b' P\xf2H')  # 0x2050f248
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.blink_out))

        data.write(b'\x9c\xb2\x10\x9a')  # 0x9cb2109a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.blink_bubble))

        data.write(b'L\xe0\xd7\xe5')  # 0x4ce0d7e5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_bubble_time))

        data.write(b'\x1fF\xcf\x01')  # 0x1f46cf01
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_bubble_time))

        data.write(b'\x0f\xc0\xb9\xe3')  # 0xfc0b9e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_blink_range))

        data.write(b'\x8e_\x168')  # 0x8e5f1638
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8e5f1638))

        data.write(b'\xf7\xba\x9e!')  # 0xf7ba9e21
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.warp_increase_intensity))

        data.write(b'\x1eP\x14\x19')  # 0x1e501419
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.warp_intensity_max))

        data.write(b'"yLm')  # 0x22794c6d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x22794c6d))

        data.write(b'[\x9c\xc4t')  # 0x5b9cc474
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5b9cc474))

        data.write(b'\x08\xf1\xe9\xd3')  # 0x8f1e9d3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.warp_duration_max))

        data.write(b'Q\xbbKo')  # 0x51bb4b6f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.frozen_gib_time))

        data.write(b'P\xa9\xbd\r')  # 0x50a9bd0d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.avoidance_range))

        data.write(b'\xediH\x8f')  # 0xed69488f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hearing_radius))

        data.write(b'\x9a\xa9\x0bk')  # 0x9aa90b6b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.recheck_path_time))

        data.write(b'v&\xec\x89')  # 0x7626ec89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.recheck_path_distance))

        data.write(b'\x13\xa1[\x89')  # 0x13a15b89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pain_threshold))

        data.write(b'\xa6\xc1c\x1d')  # 0xa6c1631d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa6c1631d))

        data.write(b'1.\x19J')  # 0x312e194a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x312e194a))

        data.write(b'\xc6\xf9./')  # 0xc6f92e2f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc6f92e2f))

        data.write(b'\x1f\x84K3')  # 0x1f844b33
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.player_scan_delay))

        data.write(b'\x10\x8e\x8e\xd8')  # 0x108e8ed8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x108e8ed8))

        data.write(b't\xcc\x0c\xcf')  # 0x74cc0ccf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_fall_time))

        data.write(b'\xc3K\xff\xca')  # 0xc34bffca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc34bffca))

        data.write(b'\xf5\xaacc')  # 0xf5aa6363
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf5aa6363))

        data.write(b'\xd4\x0c+\x10')  # 0xd40c2b10
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd40c2b10))

        data.write(b'k\xbf\x9c\xdc')  # 0x6bbf9cdc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6bbf9cdc))

        data.write(b'\xb2\xdd|\x06')  # 0xb2dd7c06
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb2dd7c06))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("BlinkWolfDataJson", data)
        return cls(
            unknown_0x2b3109a6=json_data['unknown_0x2b3109a6'],
            start_invisible=json_data['start_invisible'],
            unknown_0x7fdee42c=json_data['unknown_0x7fdee42c'],
            turn_prediction=json_data['turn_prediction'],
            spit_prediction=json_data['spit_prediction'],
            approach_dist=json_data['approach_dist'],
            unknown_0x6d6c84cb=json_data['unknown_0x6d6c84cb'],
            jump_apex=json_data['jump_apex'],
            min_spit_range=json_data['min_spit_range'],
            max_spit_range=json_data['max_spit_range'],
            unknown_0xb6055f35=json_data['unknown_0xb6055f35'],
            spit_starting=LaunchProjectileData.from_json(json_data['spit_starting']),
            spit_full_speed=LaunchProjectileData.from_json(json_data['spit_full_speed']),
            launch_projectile_data_0x76b1b8e0=LaunchProjectileData.from_json(json_data['launch_projectile_data_0x76b1b8e0']),
            launch_projectile_data_0xfe3b5965=LaunchProjectileData.from_json(json_data['launch_projectile_data_0xfe3b5965']),
            caud=json_data['caud'],
            sound_teleport_end=json_data['sound_teleport_end'],
            max_head_rotation=json_data['max_head_rotation'],
            head_rotation_speed=json_data['head_rotation_speed'],
            unknown_0x0f5a3164=json_data['unknown_0x0f5a3164'],
            unknown_0x190d9fc8=json_data['unknown_0x190d9fc8'],
            unknown_0xfcae3411=json_data['unknown_0xfcae3411'],
            unknown_0x7ecb92ca=json_data['unknown_0x7ecb92ca'],
            burn_damage=json_data['burn_damage'],
            burn_damage_duration=json_data['burn_damage_duration'],
            shockwave_range=json_data['shockwave_range'],
            shockwave_damage=DamageInfo.from_json(json_data['shockwave_damage']),
            shockwave_intensity=json_data['shockwave_intensity'],
            unknown_0xb39833c0=json_data['unknown_0xb39833c0'],
            unknown_0x96bd6426=json_data['unknown_0x96bd6426'],
            unknown_0xd7aa5ba0=json_data['unknown_0xd7aa5ba0'],
            blink_out=json_data['blink_out'],
            blink_bubble=json_data['blink_bubble'],
            min_bubble_time=json_data['min_bubble_time'],
            max_bubble_time=json_data['max_bubble_time'],
            min_blink_range=json_data['min_blink_range'],
            unknown_0x8e5f1638=json_data['unknown_0x8e5f1638'],
            warp_increase_intensity=json_data['warp_increase_intensity'],
            warp_intensity_max=json_data['warp_intensity_max'],
            unknown_0x22794c6d=json_data['unknown_0x22794c6d'],
            unknown_0x5b9cc474=json_data['unknown_0x5b9cc474'],
            warp_duration_max=json_data['warp_duration_max'],
            frozen_gib_time=json_data['frozen_gib_time'],
            avoidance_range=json_data['avoidance_range'],
            hearing_radius=json_data['hearing_radius'],
            recheck_path_time=json_data['recheck_path_time'],
            recheck_path_distance=json_data['recheck_path_distance'],
            pain_threshold=json_data['pain_threshold'],
            unknown_0xa6c1631d=json_data['unknown_0xa6c1631d'],
            unknown_0x312e194a=json_data['unknown_0x312e194a'],
            unknown_0xc6f92e2f=json_data['unknown_0xc6f92e2f'],
            player_scan_delay=json_data['player_scan_delay'],
            unknown_0x108e8ed8=json_data['unknown_0x108e8ed8'],
            max_fall_time=json_data['max_fall_time'],
            unknown_0xc34bffca=json_data['unknown_0xc34bffca'],
            unknown_0xf5aa6363=json_data['unknown_0xf5aa6363'],
            unknown_0xd40c2b10=json_data['unknown_0xd40c2b10'],
            unknown_0x6bbf9cdc=json_data['unknown_0x6bbf9cdc'],
            unknown_0xb2dd7c06=json_data['unknown_0xb2dd7c06'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x2b3109a6': self.unknown_0x2b3109a6,
            'start_invisible': self.start_invisible,
            'unknown_0x7fdee42c': self.unknown_0x7fdee42c,
            'turn_prediction': self.turn_prediction,
            'spit_prediction': self.spit_prediction,
            'approach_dist': self.approach_dist,
            'unknown_0x6d6c84cb': self.unknown_0x6d6c84cb,
            'jump_apex': self.jump_apex,
            'min_spit_range': self.min_spit_range,
            'max_spit_range': self.max_spit_range,
            'unknown_0xb6055f35': self.unknown_0xb6055f35,
            'spit_starting': self.spit_starting.to_json(),
            'spit_full_speed': self.spit_full_speed.to_json(),
            'launch_projectile_data_0x76b1b8e0': self.launch_projectile_data_0x76b1b8e0.to_json(),
            'launch_projectile_data_0xfe3b5965': self.launch_projectile_data_0xfe3b5965.to_json(),
            'caud': self.caud,
            'sound_teleport_end': self.sound_teleport_end,
            'max_head_rotation': self.max_head_rotation,
            'head_rotation_speed': self.head_rotation_speed,
            'unknown_0x0f5a3164': self.unknown_0x0f5a3164,
            'unknown_0x190d9fc8': self.unknown_0x190d9fc8,
            'unknown_0xfcae3411': self.unknown_0xfcae3411,
            'unknown_0x7ecb92ca': self.unknown_0x7ecb92ca,
            'burn_damage': self.burn_damage,
            'burn_damage_duration': self.burn_damage_duration,
            'shockwave_range': self.shockwave_range,
            'shockwave_damage': self.shockwave_damage.to_json(),
            'shockwave_intensity': self.shockwave_intensity,
            'unknown_0xb39833c0': self.unknown_0xb39833c0,
            'unknown_0x96bd6426': self.unknown_0x96bd6426,
            'unknown_0xd7aa5ba0': self.unknown_0xd7aa5ba0,
            'blink_out': self.blink_out,
            'blink_bubble': self.blink_bubble,
            'min_bubble_time': self.min_bubble_time,
            'max_bubble_time': self.max_bubble_time,
            'min_blink_range': self.min_blink_range,
            'unknown_0x8e5f1638': self.unknown_0x8e5f1638,
            'warp_increase_intensity': self.warp_increase_intensity,
            'warp_intensity_max': self.warp_intensity_max,
            'unknown_0x22794c6d': self.unknown_0x22794c6d,
            'unknown_0x5b9cc474': self.unknown_0x5b9cc474,
            'warp_duration_max': self.warp_duration_max,
            'frozen_gib_time': self.frozen_gib_time,
            'avoidance_range': self.avoidance_range,
            'hearing_radius': self.hearing_radius,
            'recheck_path_time': self.recheck_path_time,
            'recheck_path_distance': self.recheck_path_distance,
            'pain_threshold': self.pain_threshold,
            'unknown_0xa6c1631d': self.unknown_0xa6c1631d,
            'unknown_0x312e194a': self.unknown_0x312e194a,
            'unknown_0xc6f92e2f': self.unknown_0xc6f92e2f,
            'player_scan_delay': self.player_scan_delay,
            'unknown_0x108e8ed8': self.unknown_0x108e8ed8,
            'max_fall_time': self.max_fall_time,
            'unknown_0xc34bffca': self.unknown_0xc34bffca,
            'unknown_0xf5aa6363': self.unknown_0xf5aa6363,
            'unknown_0xd40c2b10': self.unknown_0xd40c2b10,
            'unknown_0x6bbf9cdc': self.unknown_0x6bbf9cdc,
            'unknown_0xb2dd7c06': self.unknown_0xb2dd7c06,
        }


def _decode_unknown_0x2b3109a6(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_start_invisible(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x7fdee42c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_turn_prediction(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_spit_prediction(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_approach_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6d6c84cb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_jump_apex(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_spit_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_spit_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb6055f35(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_caud(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_teleport_end(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_max_head_rotation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_head_rotation_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0f5a3164(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x190d9fc8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfcae3411(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7ecb92ca(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_burn_damage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_burn_damage_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shockwave_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shockwave_intensity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb39833c0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x96bd6426(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd7aa5ba0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_blink_out(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_blink_bubble(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_min_bubble_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_bubble_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_blink_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8e5f1638(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_warp_increase_intensity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_warp_intensity_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x22794c6d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5b9cc474(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_warp_duration_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_frozen_gib_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_avoidance_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hearing_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_recheck_path_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_recheck_path_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pain_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa6c1631d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x312e194a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc6f92e2f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_player_scan_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x108e8ed8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_fall_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc34bffca(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf5aa6363(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd40c2b10(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6bbf9cdc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb2dd7c06(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x2b3109a6: ('unknown_0x2b3109a6', _decode_unknown_0x2b3109a6),
    0xbb5c37e0: ('start_invisible', _decode_start_invisible),
    0x7fdee42c: ('unknown_0x7fdee42c', _decode_unknown_0x7fdee42c),
    0x983954ae: ('turn_prediction', _decode_turn_prediction),
    0x86b2b7d7: ('spit_prediction', _decode_spit_prediction),
    0xa1d7e06b: ('approach_dist', _decode_approach_dist),
    0x6d6c84cb: ('unknown_0x6d6c84cb', _decode_unknown_0x6d6c84cb),
    0xf2782501: ('jump_apex', _decode_jump_apex),
    0x236c750: ('min_spit_range', _decode_min_spit_range),
    0x17bd13a2: ('max_spit_range', _decode_max_spit_range),
    0xb6055f35: ('unknown_0xb6055f35', _decode_unknown_0xb6055f35),
    0x6dac116a: ('spit_starting', LaunchProjectileData.from_stream),
    0x9aab30f1: ('spit_full_speed', LaunchProjectileData.from_stream),
    0x76b1b8e0: ('launch_projectile_data_0x76b1b8e0', LaunchProjectileData.from_stream),
    0xfe3b5965: ('launch_projectile_data_0xfe3b5965', LaunchProjectileData.from_stream),
    0x95eaaacb: ('caud', _decode_caud),
    0xd4c88dd1: ('sound_teleport_end', _decode_sound_teleport_end),
    0xe68cebb0: ('max_head_rotation', _decode_max_head_rotation),
    0x8b7fcf8c: ('head_rotation_speed', _decode_head_rotation_speed),
    0xf5a3164: ('unknown_0x0f5a3164', _decode_unknown_0x0f5a3164),
    0x190d9fc8: ('unknown_0x190d9fc8', _decode_unknown_0x190d9fc8),
    0xfcae3411: ('unknown_0xfcae3411', _decode_unknown_0xfcae3411),
    0x7ecb92ca: ('unknown_0x7ecb92ca', _decode_unknown_0x7ecb92ca),
    0xcf201bfa: ('burn_damage', _decode_burn_damage),
    0xcf495aab: ('burn_damage_duration', _decode_burn_damage_duration),
    0x8d518fd5: ('shockwave_range', _decode_shockwave_range),
    0xf2fa713: ('shockwave_damage', DamageInfo.from_stream),
    0xa42dbd9e: ('shockwave_intensity', _decode_shockwave_intensity),
    0xb39833c0: ('unknown_0xb39833c0', _decode_unknown_0xb39833c0),
    0x96bd6426: ('unknown_0x96bd6426', _decode_unknown_0x96bd6426),
    0xd7aa5ba0: ('unknown_0xd7aa5ba0', _decode_unknown_0xd7aa5ba0),
    0x2050f248: ('blink_out', _decode_blink_out),
    0x9cb2109a: ('blink_bubble', _decode_blink_bubble),
    0x4ce0d7e5: ('min_bubble_time', _decode_min_bubble_time),
    0x1f46cf01: ('max_bubble_time', _decode_max_bubble_time),
    0xfc0b9e3: ('min_blink_range', _decode_min_blink_range),
    0x8e5f1638: ('unknown_0x8e5f1638', _decode_unknown_0x8e5f1638),
    0xf7ba9e21: ('warp_increase_intensity', _decode_warp_increase_intensity),
    0x1e501419: ('warp_intensity_max', _decode_warp_intensity_max),
    0x22794c6d: ('unknown_0x22794c6d', _decode_unknown_0x22794c6d),
    0x5b9cc474: ('unknown_0x5b9cc474', _decode_unknown_0x5b9cc474),
    0x8f1e9d3: ('warp_duration_max', _decode_warp_duration_max),
    0x51bb4b6f: ('frozen_gib_time', _decode_frozen_gib_time),
    0x50a9bd0d: ('avoidance_range', _decode_avoidance_range),
    0xed69488f: ('hearing_radius', _decode_hearing_radius),
    0x9aa90b6b: ('recheck_path_time', _decode_recheck_path_time),
    0x7626ec89: ('recheck_path_distance', _decode_recheck_path_distance),
    0x13a15b89: ('pain_threshold', _decode_pain_threshold),
    0xa6c1631d: ('unknown_0xa6c1631d', _decode_unknown_0xa6c1631d),
    0x312e194a: ('unknown_0x312e194a', _decode_unknown_0x312e194a),
    0xc6f92e2f: ('unknown_0xc6f92e2f', _decode_unknown_0xc6f92e2f),
    0x1f844b33: ('player_scan_delay', _decode_player_scan_delay),
    0x108e8ed8: ('unknown_0x108e8ed8', _decode_unknown_0x108e8ed8),
    0x74cc0ccf: ('max_fall_time', _decode_max_fall_time),
    0xc34bffca: ('unknown_0xc34bffca', _decode_unknown_0xc34bffca),
    0xf5aa6363: ('unknown_0xf5aa6363', _decode_unknown_0xf5aa6363),
    0xd40c2b10: ('unknown_0xd40c2b10', _decode_unknown_0xd40c2b10),
    0x6bbf9cdc: ('unknown_0x6bbf9cdc', _decode_unknown_0x6bbf9cdc),
    0xb2dd7c06: ('unknown_0xb2dd7c06', _decode_unknown_0xb2dd7c06),
}
