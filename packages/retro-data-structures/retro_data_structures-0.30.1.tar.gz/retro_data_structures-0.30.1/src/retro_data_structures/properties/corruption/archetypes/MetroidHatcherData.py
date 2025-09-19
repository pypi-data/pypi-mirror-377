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
from retro_data_structures.properties.corruption.archetypes.FlyerMovementMode import FlyerMovementMode
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class MetroidHatcherDataJson(typing_extensions.TypedDict):
        hearing_range: float
        lose_interest_range: float
        lose_interest_time: float
        unknown_0xfe4588a1: float
        unknown_0xc2688b41: float
        unknown_0x7b0cc30d: float
        damage_vulnerability: json_util.JsonObject
        body_vulnerability: json_util.JsonObject
        brain_vulnerability: json_util.JsonObject
        brain_x_ray_radius: float
        brain_radius: float
        leg_vulnerability: json_util.JsonObject
        unknown_0xb9e0c90d: float
        unknown_0x81d39802: float
        tentacle_regrow_time: float
        unknown_0xf79a10b0: float
        unknown_0xc550a481: float
        unknown_0x95e7a2c2: float
        unknown_0x76ba1c18: float
        unknown_0xe08106ed: float
        unknown_0x88d7c540: float
        unknown_0xace62367: float
        unknown_0x620b1b3d: float
        max_attack_height: float
        min_attack_height: float
        max_attack_forward: float
        min_attack_forward: float
        unknown_0x0978b98a: float
        unknown_0xcfcd32bb: float
        unknown_0x17d71349: float
        recheck_path_time: float
        recheck_path_distance: float
        max_num_metroids: int
        auto_spawn: bool
        max_spawn_delay: float
        min_spawn_delay: float
        unknown_0x6089191d: int
        unknown_0x258b5a9f: int
        unknown_0x2ae610e5: float
        hatch_chance: float
        maya_double: float
        unknown_0x3fee1ba4: float
        spin_attack_damage: json_util.JsonObject
        max_spin_attack_delay: float
        min_spin_attack_delay: float
        unknown_0xbeaf2105: float
        unknown_0x54ff4d38: float
        unknown_0xb29fe2d9: float
        dodge_chance: float
        unknown_0x42647ad7: float
        unknown_0xa404d536: float
        unknown_0x248d3599: float
        unknown_0xbfd77e62: float
        unknown_0xcdaa2c74: float
        unknown_0x2bca8395: float
        patrol: json_util.JsonObject
        attack_path: json_util.JsonObject
        combat: json_util.JsonObject
        stab_attack: json_util.JsonObject
        flyer_movement_mode_0x6ca56014: json_util.JsonObject
        flyer_movement_mode_0xe20e51c3: json_util.JsonObject
        flyer_movement_mode_0x25a68a0e: json_util.JsonObject
        flyer_movement_mode_0xd9b5d506: json_util.JsonObject
        flyer_movement_mode_0x8bb1c3a2: json_util.JsonObject
        stunned: json_util.JsonObject
        flyer_movement_mode_0xfb2ddfad: json_util.JsonObject
        dash: json_util.JsonObject
        flyer_movement_mode_0x5fe13a7b: json_util.JsonObject
        claw: json_util.JsonObject
        char_0x4d7dbeab: json_util.JsonObject
        char_0xa17c09bb: json_util.JsonObject
        char_0x11dc2dab: json_util.JsonObject
        char_0xfddd9abb: json_util.JsonObject
        unknown_0xc99cee00: float
        unknown_0x2ffc41e1: float
        unknown_0x7f5d9ab7: float
        unknown_0x993d3556: float
        unknown_0x08efeb79: float
        unknown_0xee8f4498: float
        unknown_0xc24d8fbd: float
        unknown_0x242d205c: float
        stun_threshold: float
        electric_ball_effect: int
        sound_ball_effect: int
        electric_visor_effect: int
        sound_visor_effect: int
        leg_hit_splash: int
    

@dataclasses.dataclass()
class MetroidHatcherData(BaseProperty):
    hearing_range: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x25474550, original_name='HearingRange'
        ),
    })
    lose_interest_range: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x474fa589, original_name='LoseInterestRange'
        ),
    })
    lose_interest_time: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf8b0c2bb, original_name='LoseInterestTime'
        ),
    })
    unknown_0xfe4588a1: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfe4588a1, original_name='Unknown'
        ),
    })
    unknown_0xc2688b41: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc2688b41, original_name='Unknown'
        ),
    })
    unknown_0x7b0cc30d: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7b0cc30d, original_name='Unknown'
        ),
    })
    damage_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x742b3336, original_name='DamageVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    body_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x0d9230d1, original_name='BodyVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    brain_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x243ab10d, original_name='BrainVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    brain_x_ray_radius: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x012115a2, original_name='BrainXRayRadius'
        ),
    })
    brain_radius: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa12a4409, original_name='BrainRadius'
        ),
    })
    leg_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x9f0ff852, original_name='LegVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_0xb9e0c90d: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb9e0c90d, original_name='Unknown'
        ),
    })
    unknown_0x81d39802: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x81d39802, original_name='Unknown'
        ),
    })
    tentacle_regrow_time: float = dataclasses.field(default=0.33329999446868896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xba002dcb, original_name='TentacleRegrowTime'
        ),
    })
    unknown_0xf79a10b0: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf79a10b0, original_name='Unknown'
        ),
    })
    unknown_0xc550a481: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc550a481, original_name='Unknown'
        ),
    })
    unknown_0x95e7a2c2: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95e7a2c2, original_name='Unknown'
        ),
    })
    unknown_0x76ba1c18: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x76ba1c18, original_name='Unknown'
        ),
    })
    unknown_0xe08106ed: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe08106ed, original_name='Unknown'
        ),
    })
    unknown_0x88d7c540: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x88d7c540, original_name='Unknown'
        ),
    })
    unknown_0xace62367: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xace62367, original_name='Unknown'
        ),
    })
    unknown_0x620b1b3d: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x620b1b3d, original_name='Unknown'
        ),
    })
    max_attack_height: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe1ae51d8, original_name='MaxAttackHeight'
        ),
    })
    min_attack_height: float = dataclasses.field(default=9.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc8d0acc0, original_name='MinAttackHeight'
        ),
    })
    max_attack_forward: float = dataclasses.field(default=16.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf3e8012d, original_name='MaxAttackForward'
        ),
    })
    min_attack_forward: float = dataclasses.field(default=14.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe0ade786, original_name='MinAttackForward'
        ),
    })
    unknown_0x0978b98a: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0978b98a, original_name='Unknown'
        ),
    })
    unknown_0xcfcd32bb: float = dataclasses.field(default=-1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcfcd32bb, original_name='Unknown'
        ),
    })
    unknown_0x17d71349: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x17d71349, original_name='Unknown'
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
    max_num_metroids: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7915e2b3, original_name='MaxNumMetroids'
        ),
    })
    auto_spawn: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xccc0cf92, original_name='AutoSpawn'
        ),
    })
    max_spawn_delay: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x75e0b0a7, original_name='MaxSpawnDelay'
        ),
    })
    min_spawn_delay: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2646a843, original_name='MinSpawnDelay'
        ),
    })
    unknown_0x6089191d: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6089191d, original_name='Unknown'
        ),
    })
    unknown_0x258b5a9f: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x258b5a9f, original_name='Unknown'
        ),
    })
    unknown_0x2ae610e5: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2ae610e5, original_name='Unknown'
        ),
    })
    hatch_chance: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x354bae31, original_name='HatchChance'
        ),
    })
    maya_double: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf4b2c801, original_name='MayaDouble'
        ),
    })
    unknown_0x3fee1ba4: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3fee1ba4, original_name='Unknown'
        ),
    })
    spin_attack_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xcfacff53, original_name='SpinAttackDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    max_spin_attack_delay: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6cb6d8c7, original_name='MaxSpinAttackDelay'
        ),
    })
    min_spin_attack_delay: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x682ce9ed, original_name='MinSpinAttackDelay'
        ),
    })
    unknown_0xbeaf2105: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbeaf2105, original_name='Unknown'
        ),
    })
    unknown_0x54ff4d38: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x54ff4d38, original_name='Unknown'
        ),
    })
    unknown_0xb29fe2d9: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb29fe2d9, original_name='Unknown'
        ),
    })
    dodge_chance: float = dataclasses.field(default=0.0010000000474974513, metadata={
        'reflection': FieldReflection[float](
            float, id=0x47be3298, original_name='DodgeChance'
        ),
    })
    unknown_0x42647ad7: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x42647ad7, original_name='Unknown'
        ),
    })
    unknown_0xa404d536: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa404d536, original_name='Unknown'
        ),
    })
    unknown_0x248d3599: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x248d3599, original_name='Unknown'
        ),
    })
    unknown_0xbfd77e62: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbfd77e62, original_name='Unknown'
        ),
    })
    unknown_0xcdaa2c74: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcdaa2c74, original_name='Unknown'
        ),
    })
    unknown_0x2bca8395: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2bca8395, original_name='Unknown'
        ),
    })
    patrol: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xccdd3aca, original_name='Patrol', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    attack_path: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xc845d3c0, original_name='AttackPath', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    combat: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xcc7d2e98, original_name='Combat', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    stab_attack: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xb9c3db94, original_name='StabAttack', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    flyer_movement_mode_0x6ca56014: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0x6ca56014, original_name='FlyerMovementMode', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    flyer_movement_mode_0xe20e51c3: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xe20e51c3, original_name='FlyerMovementMode', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    flyer_movement_mode_0x25a68a0e: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0x25a68a0e, original_name='FlyerMovementMode', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    flyer_movement_mode_0xd9b5d506: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xd9b5d506, original_name='FlyerMovementMode', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    flyer_movement_mode_0x8bb1c3a2: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0x8bb1c3a2, original_name='FlyerMovementMode', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    stunned: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0x389cb515, original_name='Stunned', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    flyer_movement_mode_0xfb2ddfad: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xfb2ddfad, original_name='FlyerMovementMode', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    dash: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xc558bc0d, original_name='Dash', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    flyer_movement_mode_0x5fe13a7b: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0x5fe13a7b, original_name='FlyerMovementMode', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    claw: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xfd38a106, original_name='Claw', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    char_0x4d7dbeab: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x4d7dbeab, original_name='CHAR', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    char_0xa17c09bb: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa17c09bb, original_name='CHAR', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    char_0x11dc2dab: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x11dc2dab, original_name='CHAR', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    char_0xfddd9abb: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xfddd9abb, original_name='CHAR', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unknown_0xc99cee00: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc99cee00, original_name='Unknown'
        ),
    })
    unknown_0x2ffc41e1: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2ffc41e1, original_name='Unknown'
        ),
    })
    unknown_0x7f5d9ab7: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7f5d9ab7, original_name='Unknown'
        ),
    })
    unknown_0x993d3556: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x993d3556, original_name='Unknown'
        ),
    })
    unknown_0x08efeb79: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x08efeb79, original_name='Unknown'
        ),
    })
    unknown_0xee8f4498: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xee8f4498, original_name='Unknown'
        ),
    })
    unknown_0xc24d8fbd: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc24d8fbd, original_name='Unknown'
        ),
    })
    unknown_0x242d205c: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x242d205c, original_name='Unknown'
        ),
    })
    stun_threshold: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5bdd1e4c, original_name='StunThreshold'
        ),
    })
    electric_ball_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6da4a3b0, original_name='ElectricBallEffect'
        ),
    })
    sound_ball_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3fcd8b66, original_name='Sound_BallEffect'
        ),
    })
    electric_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xcc0af287, original_name='ElectricVisorEffect'
        ),
    })
    sound_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa3e8ec4e, original_name='Sound_VisorEffect'
        ),
    })
    leg_hit_splash: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf40a9c9d, original_name='LegHitSplash'
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
        if property_count != 87:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x25474550
        hearing_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x474fa589
        lose_interest_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf8b0c2bb
        lose_interest_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe4588a1
        unknown_0xfe4588a1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc2688b41
        unknown_0xc2688b41 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b0cc30d
        unknown_0x7b0cc30d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x742b3336
        damage_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d9230d1
        body_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x243ab10d
        brain_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x012115a2
        brain_x_ray_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa12a4409
        brain_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f0ff852
        leg_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb9e0c90d
        unknown_0xb9e0c90d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81d39802
        unknown_0x81d39802 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba002dcb
        tentacle_regrow_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf79a10b0
        unknown_0xf79a10b0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc550a481
        unknown_0xc550a481 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95e7a2c2
        unknown_0x95e7a2c2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76ba1c18
        unknown_0x76ba1c18 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe08106ed
        unknown_0xe08106ed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88d7c540
        unknown_0x88d7c540 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xace62367
        unknown_0xace62367 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x620b1b3d
        unknown_0x620b1b3d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe1ae51d8
        max_attack_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8d0acc0
        min_attack_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3e8012d
        max_attack_forward = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0ade786
        min_attack_forward = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0978b98a
        unknown_0x0978b98a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcfcd32bb
        unknown_0xcfcd32bb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x17d71349
        unknown_0x17d71349 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9aa90b6b
        recheck_path_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7626ec89
        recheck_path_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7915e2b3
        max_num_metroids = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xccc0cf92
        auto_spawn = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x75e0b0a7
        max_spawn_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2646a843
        min_spawn_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6089191d
        unknown_0x6089191d = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x258b5a9f
        unknown_0x258b5a9f = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ae610e5
        unknown_0x2ae610e5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x354bae31
        hatch_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf4b2c801
        maya_double = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3fee1ba4
        unknown_0x3fee1ba4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcfacff53
        spin_attack_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 30.0, 'di_knock_back_power': 20.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6cb6d8c7
        max_spin_attack_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x682ce9ed
        min_spin_attack_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbeaf2105
        unknown_0xbeaf2105 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x54ff4d38
        unknown_0x54ff4d38 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb29fe2d9
        unknown_0xb29fe2d9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47be3298
        dodge_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42647ad7
        unknown_0x42647ad7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa404d536
        unknown_0xa404d536 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x248d3599
        unknown_0x248d3599 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbfd77e62
        unknown_0xbfd77e62 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcdaa2c74
        unknown_0xcdaa2c74 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2bca8395
        unknown_0x2bca8395 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xccdd3aca
        patrol = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 3.0, 'acceleration': 1.0, 'facing_turn_rate': 30.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc845d3c0
        attack_path = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 3.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcc7d2e98
        combat = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 3.0, 'acceleration': 10.0, 'turn_threshold': 181.0, 'floor_buffer': 11.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb9c3db94
        stab_attack = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 0.10000000149011612, 'acceleration': 10.0, 'turn_rate': 10800.0, 'facing_turn_rate': 120.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 0.0, 'floor_buffer': 8.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ca56014
        flyer_movement_mode_0x6ca56014 = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 30.0, 'acceleration': 50.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 0.0, 'floor_buffer': 3.5, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe20e51c3
        flyer_movement_mode_0xe20e51c3 = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 30.0, 'acceleration': 10.0, 'facing_turn_rate': 1.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 1.0, 'floor_buffer': 5.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x25a68a0e
        flyer_movement_mode_0x25a68a0e = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 1.0, 'acceleration': 10.0, 'turn_threshold': 181.0, 'height_variation_max': 0.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd9b5d506
        flyer_movement_mode_0xd9b5d506 = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 30.0, 'acceleration': 20.0, 'facing_turn_rate': 1.0, 'turn_threshold': 181.0, 'height_variation_max': 1.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8bb1c3a2
        flyer_movement_mode_0x8bb1c3a2 = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 1.0, 'acceleration': 10.0, 'turn_threshold': 181.0, 'height_variation_max': 1.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x389cb515
        stunned = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 5.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 1.0, 'floor_buffer': 5.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfb2ddfad
        flyer_movement_mode_0xfb2ddfad = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 5.0, 'acceleration': 10.0, 'facing_turn_rate': 15.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_min': 1.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc558bc0d
        dash = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 40.0, 'acceleration': 100.0, 'turn_rate': 360.0, 'turn_threshold': 181.0, 'avoidance_range': 1.0, 'height_variation_max': 0.5, 'floor_buffer': 13.0, 'ceiling_buffer': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5fe13a7b
        flyer_movement_mode_0x5fe13a7b = FlyerMovementMode.from_stream(data, property_size, default_override={'acceleration': 20.0, 'turn_threshold': 181.0, 'floor_buffer': 12.0, 'ceiling_buffer': 12.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd38a106
        claw = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d7dbeab
        char_0x4d7dbeab = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa17c09bb
        char_0xa17c09bb = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x11dc2dab
        char_0x11dc2dab = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfddd9abb
        char_0xfddd9abb = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc99cee00
        unknown_0xc99cee00 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ffc41e1
        unknown_0x2ffc41e1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f5d9ab7
        unknown_0x7f5d9ab7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x993d3556
        unknown_0x993d3556 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08efeb79
        unknown_0x08efeb79 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xee8f4498
        unknown_0xee8f4498 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc24d8fbd
        unknown_0xc24d8fbd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x242d205c
        unknown_0x242d205c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5bdd1e4c
        stun_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6da4a3b0
        electric_ball_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3fcd8b66
        sound_ball_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcc0af287
        electric_visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa3e8ec4e
        sound_visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf40a9c9d
        leg_hit_splash = struct.unpack(">Q", data.read(8))[0]
    
        return cls(hearing_range, lose_interest_range, lose_interest_time, unknown_0xfe4588a1, unknown_0xc2688b41, unknown_0x7b0cc30d, damage_vulnerability, body_vulnerability, brain_vulnerability, brain_x_ray_radius, brain_radius, leg_vulnerability, unknown_0xb9e0c90d, unknown_0x81d39802, tentacle_regrow_time, unknown_0xf79a10b0, unknown_0xc550a481, unknown_0x95e7a2c2, unknown_0x76ba1c18, unknown_0xe08106ed, unknown_0x88d7c540, unknown_0xace62367, unknown_0x620b1b3d, max_attack_height, min_attack_height, max_attack_forward, min_attack_forward, unknown_0x0978b98a, unknown_0xcfcd32bb, unknown_0x17d71349, recheck_path_time, recheck_path_distance, max_num_metroids, auto_spawn, max_spawn_delay, min_spawn_delay, unknown_0x6089191d, unknown_0x258b5a9f, unknown_0x2ae610e5, hatch_chance, maya_double, unknown_0x3fee1ba4, spin_attack_damage, max_spin_attack_delay, min_spin_attack_delay, unknown_0xbeaf2105, unknown_0x54ff4d38, unknown_0xb29fe2d9, dodge_chance, unknown_0x42647ad7, unknown_0xa404d536, unknown_0x248d3599, unknown_0xbfd77e62, unknown_0xcdaa2c74, unknown_0x2bca8395, patrol, attack_path, combat, stab_attack, flyer_movement_mode_0x6ca56014, flyer_movement_mode_0xe20e51c3, flyer_movement_mode_0x25a68a0e, flyer_movement_mode_0xd9b5d506, flyer_movement_mode_0x8bb1c3a2, stunned, flyer_movement_mode_0xfb2ddfad, dash, flyer_movement_mode_0x5fe13a7b, claw, char_0x4d7dbeab, char_0xa17c09bb, char_0x11dc2dab, char_0xfddd9abb, unknown_0xc99cee00, unknown_0x2ffc41e1, unknown_0x7f5d9ab7, unknown_0x993d3556, unknown_0x08efeb79, unknown_0xee8f4498, unknown_0xc24d8fbd, unknown_0x242d205c, stun_threshold, electric_ball_effect, sound_ball_effect, electric_visor_effect, sound_visor_effect, leg_hit_splash)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00W')  # 87 properties

        data.write(b'%GEP')  # 0x25474550
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hearing_range))

        data.write(b'GO\xa5\x89')  # 0x474fa589
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lose_interest_range))

        data.write(b'\xf8\xb0\xc2\xbb')  # 0xf8b0c2bb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lose_interest_time))

        data.write(b'\xfeE\x88\xa1')  # 0xfe4588a1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfe4588a1))

        data.write(b'\xc2h\x8bA')  # 0xc2688b41
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc2688b41))

        data.write(b'{\x0c\xc3\r')  # 0x7b0cc30d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7b0cc30d))

        data.write(b't+36')  # 0x742b3336
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_vulnerability.to_stream(data)
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

        data.write(b'$:\xb1\r')  # 0x243ab10d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.brain_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x01!\x15\xa2')  # 0x12115a2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.brain_x_ray_radius))

        data.write(b'\xa1*D\t')  # 0xa12a4409
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.brain_radius))

        data.write(b'\x9f\x0f\xf8R')  # 0x9f0ff852
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.leg_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb9\xe0\xc9\r')  # 0xb9e0c90d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb9e0c90d))

        data.write(b'\x81\xd3\x98\x02')  # 0x81d39802
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x81d39802))

        data.write(b'\xba\x00-\xcb')  # 0xba002dcb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.tentacle_regrow_time))

        data.write(b'\xf7\x9a\x10\xb0')  # 0xf79a10b0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf79a10b0))

        data.write(b'\xc5P\xa4\x81')  # 0xc550a481
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc550a481))

        data.write(b'\x95\xe7\xa2\xc2')  # 0x95e7a2c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95e7a2c2))

        data.write(b'v\xba\x1c\x18')  # 0x76ba1c18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x76ba1c18))

        data.write(b'\xe0\x81\x06\xed')  # 0xe08106ed
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe08106ed))

        data.write(b'\x88\xd7\xc5@')  # 0x88d7c540
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x88d7c540))

        data.write(b'\xac\xe6#g')  # 0xace62367
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xace62367))

        data.write(b'b\x0b\x1b=')  # 0x620b1b3d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x620b1b3d))

        data.write(b'\xe1\xaeQ\xd8')  # 0xe1ae51d8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_height))

        data.write(b'\xc8\xd0\xac\xc0')  # 0xc8d0acc0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_height))

        data.write(b'\xf3\xe8\x01-')  # 0xf3e8012d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_forward))

        data.write(b'\xe0\xad\xe7\x86')  # 0xe0ade786
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_forward))

        data.write(b'\tx\xb9\x8a')  # 0x978b98a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0978b98a))

        data.write(b'\xcf\xcd2\xbb')  # 0xcfcd32bb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcfcd32bb))

        data.write(b'\x17\xd7\x13I')  # 0x17d71349
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x17d71349))

        data.write(b'\x9a\xa9\x0bk')  # 0x9aa90b6b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.recheck_path_time))

        data.write(b'v&\xec\x89')  # 0x7626ec89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.recheck_path_distance))

        data.write(b'y\x15\xe2\xb3')  # 0x7915e2b3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_num_metroids))

        data.write(b'\xcc\xc0\xcf\x92')  # 0xccc0cf92
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.auto_spawn))

        data.write(b'u\xe0\xb0\xa7')  # 0x75e0b0a7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_spawn_delay))

        data.write(b'&F\xa8C')  # 0x2646a843
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_spawn_delay))

        data.write(b'`\x89\x19\x1d')  # 0x6089191d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x6089191d))

        data.write(b'%\x8bZ\x9f')  # 0x258b5a9f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x258b5a9f))

        data.write(b'*\xe6\x10\xe5')  # 0x2ae610e5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2ae610e5))

        data.write(b'5K\xae1')  # 0x354bae31
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hatch_chance))

        data.write(b'\xf4\xb2\xc8\x01')  # 0xf4b2c801
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.maya_double))

        data.write(b'?\xee\x1b\xa4')  # 0x3fee1ba4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3fee1ba4))

        data.write(b'\xcf\xac\xffS')  # 0xcfacff53
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spin_attack_damage.to_stream(data, default_override={'di_damage': 30.0, 'di_knock_back_power': 20.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'l\xb6\xd8\xc7')  # 0x6cb6d8c7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_spin_attack_delay))

        data.write(b'h,\xe9\xed')  # 0x682ce9ed
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_spin_attack_delay))

        data.write(b'\xbe\xaf!\x05')  # 0xbeaf2105
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbeaf2105))

        data.write(b'T\xffM8')  # 0x54ff4d38
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x54ff4d38))

        data.write(b'\xb2\x9f\xe2\xd9')  # 0xb29fe2d9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb29fe2d9))

        data.write(b'G\xbe2\x98')  # 0x47be3298
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_chance))

        data.write(b'Bdz\xd7')  # 0x42647ad7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x42647ad7))

        data.write(b'\xa4\x04\xd56')  # 0xa404d536
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa404d536))

        data.write(b'$\x8d5\x99')  # 0x248d3599
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x248d3599))

        data.write(b'\xbf\xd7~b')  # 0xbfd77e62
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbfd77e62))

        data.write(b'\xcd\xaa,t')  # 0xcdaa2c74
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcdaa2c74))

        data.write(b'+\xca\x83\x95')  # 0x2bca8395
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2bca8395))

        data.write(b'\xcc\xdd:\xca')  # 0xccdd3aca
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patrol.to_stream(data, default_override={'speed': 3.0, 'acceleration': 1.0, 'facing_turn_rate': 30.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc8E\xd3\xc0')  # 0xc845d3c0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack_path.to_stream(data, default_override={'speed': 3.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xcc}.\x98')  # 0xcc7d2e98
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.combat.to_stream(data, default_override={'speed': 3.0, 'acceleration': 10.0, 'turn_threshold': 181.0, 'floor_buffer': 11.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb9\xc3\xdb\x94')  # 0xb9c3db94
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.stab_attack.to_stream(data, default_override={'speed': 0.10000000149011612, 'acceleration': 10.0, 'turn_rate': 10800.0, 'facing_turn_rate': 120.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 0.0, 'floor_buffer': 8.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'l\xa5`\x14')  # 0x6ca56014
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flyer_movement_mode_0x6ca56014.to_stream(data, default_override={'speed': 30.0, 'acceleration': 50.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 0.0, 'floor_buffer': 3.5, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe2\x0eQ\xc3')  # 0xe20e51c3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flyer_movement_mode_0xe20e51c3.to_stream(data, default_override={'speed': 30.0, 'acceleration': 10.0, 'facing_turn_rate': 1.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 1.0, 'floor_buffer': 5.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'%\xa6\x8a\x0e')  # 0x25a68a0e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flyer_movement_mode_0x25a68a0e.to_stream(data, default_override={'speed': 1.0, 'acceleration': 10.0, 'turn_threshold': 181.0, 'height_variation_max': 0.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd9\xb5\xd5\x06')  # 0xd9b5d506
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flyer_movement_mode_0xd9b5d506.to_stream(data, default_override={'speed': 30.0, 'acceleration': 20.0, 'facing_turn_rate': 1.0, 'turn_threshold': 181.0, 'height_variation_max': 1.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8b\xb1\xc3\xa2')  # 0x8bb1c3a2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flyer_movement_mode_0x8bb1c3a2.to_stream(data, default_override={'speed': 1.0, 'acceleration': 10.0, 'turn_threshold': 181.0, 'height_variation_max': 1.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'8\x9c\xb5\x15')  # 0x389cb515
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.stunned.to_stream(data, default_override={'speed': 5.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 1.0, 'floor_buffer': 5.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfb-\xdf\xad')  # 0xfb2ddfad
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flyer_movement_mode_0xfb2ddfad.to_stream(data, default_override={'speed': 5.0, 'acceleration': 10.0, 'facing_turn_rate': 15.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_min': 1.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc5X\xbc\r')  # 0xc558bc0d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dash.to_stream(data, default_override={'speed': 40.0, 'acceleration': 100.0, 'turn_rate': 360.0, 'turn_threshold': 181.0, 'avoidance_range': 1.0, 'height_variation_max': 0.5, 'floor_buffer': 13.0, 'ceiling_buffer': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'_\xe1:{')  # 0x5fe13a7b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flyer_movement_mode_0x5fe13a7b.to_stream(data, default_override={'acceleration': 20.0, 'turn_threshold': 181.0, 'floor_buffer': 12.0, 'ceiling_buffer': 12.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfd8\xa1\x06')  # 0xfd38a106
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.claw.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'M}\xbe\xab')  # 0x4d7dbeab
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.char_0x4d7dbeab.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa1|\t\xbb')  # 0xa17c09bb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.char_0xa17c09bb.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x11\xdc-\xab')  # 0x11dc2dab
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.char_0x11dc2dab.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfd\xdd\x9a\xbb')  # 0xfddd9abb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.char_0xfddd9abb.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc9\x9c\xee\x00')  # 0xc99cee00
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc99cee00))

        data.write(b'/\xfcA\xe1')  # 0x2ffc41e1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2ffc41e1))

        data.write(b'\x7f]\x9a\xb7')  # 0x7f5d9ab7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7f5d9ab7))

        data.write(b'\x99=5V')  # 0x993d3556
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x993d3556))

        data.write(b'\x08\xef\xeby')  # 0x8efeb79
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x08efeb79))

        data.write(b'\xee\x8fD\x98')  # 0xee8f4498
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xee8f4498))

        data.write(b'\xc2M\x8f\xbd')  # 0xc24d8fbd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc24d8fbd))

        data.write(b'$- \\')  # 0x242d205c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x242d205c))

        data.write(b'[\xdd\x1eL')  # 0x5bdd1e4c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.stun_threshold))

        data.write(b'm\xa4\xa3\xb0')  # 0x6da4a3b0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.electric_ball_effect))

        data.write(b'?\xcd\x8bf')  # 0x3fcd8b66
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_ball_effect))

        data.write(b'\xcc\n\xf2\x87')  # 0xcc0af287
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.electric_visor_effect))

        data.write(b'\xa3\xe8\xecN')  # 0xa3e8ec4e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_visor_effect))

        data.write(b'\xf4\n\x9c\x9d')  # 0xf40a9c9d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.leg_hit_splash))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MetroidHatcherDataJson", data)
        return cls(
            hearing_range=json_data['hearing_range'],
            lose_interest_range=json_data['lose_interest_range'],
            lose_interest_time=json_data['lose_interest_time'],
            unknown_0xfe4588a1=json_data['unknown_0xfe4588a1'],
            unknown_0xc2688b41=json_data['unknown_0xc2688b41'],
            unknown_0x7b0cc30d=json_data['unknown_0x7b0cc30d'],
            damage_vulnerability=DamageVulnerability.from_json(json_data['damage_vulnerability']),
            body_vulnerability=DamageVulnerability.from_json(json_data['body_vulnerability']),
            brain_vulnerability=DamageVulnerability.from_json(json_data['brain_vulnerability']),
            brain_x_ray_radius=json_data['brain_x_ray_radius'],
            brain_radius=json_data['brain_radius'],
            leg_vulnerability=DamageVulnerability.from_json(json_data['leg_vulnerability']),
            unknown_0xb9e0c90d=json_data['unknown_0xb9e0c90d'],
            unknown_0x81d39802=json_data['unknown_0x81d39802'],
            tentacle_regrow_time=json_data['tentacle_regrow_time'],
            unknown_0xf79a10b0=json_data['unknown_0xf79a10b0'],
            unknown_0xc550a481=json_data['unknown_0xc550a481'],
            unknown_0x95e7a2c2=json_data['unknown_0x95e7a2c2'],
            unknown_0x76ba1c18=json_data['unknown_0x76ba1c18'],
            unknown_0xe08106ed=json_data['unknown_0xe08106ed'],
            unknown_0x88d7c540=json_data['unknown_0x88d7c540'],
            unknown_0xace62367=json_data['unknown_0xace62367'],
            unknown_0x620b1b3d=json_data['unknown_0x620b1b3d'],
            max_attack_height=json_data['max_attack_height'],
            min_attack_height=json_data['min_attack_height'],
            max_attack_forward=json_data['max_attack_forward'],
            min_attack_forward=json_data['min_attack_forward'],
            unknown_0x0978b98a=json_data['unknown_0x0978b98a'],
            unknown_0xcfcd32bb=json_data['unknown_0xcfcd32bb'],
            unknown_0x17d71349=json_data['unknown_0x17d71349'],
            recheck_path_time=json_data['recheck_path_time'],
            recheck_path_distance=json_data['recheck_path_distance'],
            max_num_metroids=json_data['max_num_metroids'],
            auto_spawn=json_data['auto_spawn'],
            max_spawn_delay=json_data['max_spawn_delay'],
            min_spawn_delay=json_data['min_spawn_delay'],
            unknown_0x6089191d=json_data['unknown_0x6089191d'],
            unknown_0x258b5a9f=json_data['unknown_0x258b5a9f'],
            unknown_0x2ae610e5=json_data['unknown_0x2ae610e5'],
            hatch_chance=json_data['hatch_chance'],
            maya_double=json_data['maya_double'],
            unknown_0x3fee1ba4=json_data['unknown_0x3fee1ba4'],
            spin_attack_damage=DamageInfo.from_json(json_data['spin_attack_damage']),
            max_spin_attack_delay=json_data['max_spin_attack_delay'],
            min_spin_attack_delay=json_data['min_spin_attack_delay'],
            unknown_0xbeaf2105=json_data['unknown_0xbeaf2105'],
            unknown_0x54ff4d38=json_data['unknown_0x54ff4d38'],
            unknown_0xb29fe2d9=json_data['unknown_0xb29fe2d9'],
            dodge_chance=json_data['dodge_chance'],
            unknown_0x42647ad7=json_data['unknown_0x42647ad7'],
            unknown_0xa404d536=json_data['unknown_0xa404d536'],
            unknown_0x248d3599=json_data['unknown_0x248d3599'],
            unknown_0xbfd77e62=json_data['unknown_0xbfd77e62'],
            unknown_0xcdaa2c74=json_data['unknown_0xcdaa2c74'],
            unknown_0x2bca8395=json_data['unknown_0x2bca8395'],
            patrol=FlyerMovementMode.from_json(json_data['patrol']),
            attack_path=FlyerMovementMode.from_json(json_data['attack_path']),
            combat=FlyerMovementMode.from_json(json_data['combat']),
            stab_attack=FlyerMovementMode.from_json(json_data['stab_attack']),
            flyer_movement_mode_0x6ca56014=FlyerMovementMode.from_json(json_data['flyer_movement_mode_0x6ca56014']),
            flyer_movement_mode_0xe20e51c3=FlyerMovementMode.from_json(json_data['flyer_movement_mode_0xe20e51c3']),
            flyer_movement_mode_0x25a68a0e=FlyerMovementMode.from_json(json_data['flyer_movement_mode_0x25a68a0e']),
            flyer_movement_mode_0xd9b5d506=FlyerMovementMode.from_json(json_data['flyer_movement_mode_0xd9b5d506']),
            flyer_movement_mode_0x8bb1c3a2=FlyerMovementMode.from_json(json_data['flyer_movement_mode_0x8bb1c3a2']),
            stunned=FlyerMovementMode.from_json(json_data['stunned']),
            flyer_movement_mode_0xfb2ddfad=FlyerMovementMode.from_json(json_data['flyer_movement_mode_0xfb2ddfad']),
            dash=FlyerMovementMode.from_json(json_data['dash']),
            flyer_movement_mode_0x5fe13a7b=FlyerMovementMode.from_json(json_data['flyer_movement_mode_0x5fe13a7b']),
            claw=AnimationParameters.from_json(json_data['claw']),
            char_0x4d7dbeab=AnimationParameters.from_json(json_data['char_0x4d7dbeab']),
            char_0xa17c09bb=AnimationParameters.from_json(json_data['char_0xa17c09bb']),
            char_0x11dc2dab=AnimationParameters.from_json(json_data['char_0x11dc2dab']),
            char_0xfddd9abb=AnimationParameters.from_json(json_data['char_0xfddd9abb']),
            unknown_0xc99cee00=json_data['unknown_0xc99cee00'],
            unknown_0x2ffc41e1=json_data['unknown_0x2ffc41e1'],
            unknown_0x7f5d9ab7=json_data['unknown_0x7f5d9ab7'],
            unknown_0x993d3556=json_data['unknown_0x993d3556'],
            unknown_0x08efeb79=json_data['unknown_0x08efeb79'],
            unknown_0xee8f4498=json_data['unknown_0xee8f4498'],
            unknown_0xc24d8fbd=json_data['unknown_0xc24d8fbd'],
            unknown_0x242d205c=json_data['unknown_0x242d205c'],
            stun_threshold=json_data['stun_threshold'],
            electric_ball_effect=json_data['electric_ball_effect'],
            sound_ball_effect=json_data['sound_ball_effect'],
            electric_visor_effect=json_data['electric_visor_effect'],
            sound_visor_effect=json_data['sound_visor_effect'],
            leg_hit_splash=json_data['leg_hit_splash'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'hearing_range': self.hearing_range,
            'lose_interest_range': self.lose_interest_range,
            'lose_interest_time': self.lose_interest_time,
            'unknown_0xfe4588a1': self.unknown_0xfe4588a1,
            'unknown_0xc2688b41': self.unknown_0xc2688b41,
            'unknown_0x7b0cc30d': self.unknown_0x7b0cc30d,
            'damage_vulnerability': self.damage_vulnerability.to_json(),
            'body_vulnerability': self.body_vulnerability.to_json(),
            'brain_vulnerability': self.brain_vulnerability.to_json(),
            'brain_x_ray_radius': self.brain_x_ray_radius,
            'brain_radius': self.brain_radius,
            'leg_vulnerability': self.leg_vulnerability.to_json(),
            'unknown_0xb9e0c90d': self.unknown_0xb9e0c90d,
            'unknown_0x81d39802': self.unknown_0x81d39802,
            'tentacle_regrow_time': self.tentacle_regrow_time,
            'unknown_0xf79a10b0': self.unknown_0xf79a10b0,
            'unknown_0xc550a481': self.unknown_0xc550a481,
            'unknown_0x95e7a2c2': self.unknown_0x95e7a2c2,
            'unknown_0x76ba1c18': self.unknown_0x76ba1c18,
            'unknown_0xe08106ed': self.unknown_0xe08106ed,
            'unknown_0x88d7c540': self.unknown_0x88d7c540,
            'unknown_0xace62367': self.unknown_0xace62367,
            'unknown_0x620b1b3d': self.unknown_0x620b1b3d,
            'max_attack_height': self.max_attack_height,
            'min_attack_height': self.min_attack_height,
            'max_attack_forward': self.max_attack_forward,
            'min_attack_forward': self.min_attack_forward,
            'unknown_0x0978b98a': self.unknown_0x0978b98a,
            'unknown_0xcfcd32bb': self.unknown_0xcfcd32bb,
            'unknown_0x17d71349': self.unknown_0x17d71349,
            'recheck_path_time': self.recheck_path_time,
            'recheck_path_distance': self.recheck_path_distance,
            'max_num_metroids': self.max_num_metroids,
            'auto_spawn': self.auto_spawn,
            'max_spawn_delay': self.max_spawn_delay,
            'min_spawn_delay': self.min_spawn_delay,
            'unknown_0x6089191d': self.unknown_0x6089191d,
            'unknown_0x258b5a9f': self.unknown_0x258b5a9f,
            'unknown_0x2ae610e5': self.unknown_0x2ae610e5,
            'hatch_chance': self.hatch_chance,
            'maya_double': self.maya_double,
            'unknown_0x3fee1ba4': self.unknown_0x3fee1ba4,
            'spin_attack_damage': self.spin_attack_damage.to_json(),
            'max_spin_attack_delay': self.max_spin_attack_delay,
            'min_spin_attack_delay': self.min_spin_attack_delay,
            'unknown_0xbeaf2105': self.unknown_0xbeaf2105,
            'unknown_0x54ff4d38': self.unknown_0x54ff4d38,
            'unknown_0xb29fe2d9': self.unknown_0xb29fe2d9,
            'dodge_chance': self.dodge_chance,
            'unknown_0x42647ad7': self.unknown_0x42647ad7,
            'unknown_0xa404d536': self.unknown_0xa404d536,
            'unknown_0x248d3599': self.unknown_0x248d3599,
            'unknown_0xbfd77e62': self.unknown_0xbfd77e62,
            'unknown_0xcdaa2c74': self.unknown_0xcdaa2c74,
            'unknown_0x2bca8395': self.unknown_0x2bca8395,
            'patrol': self.patrol.to_json(),
            'attack_path': self.attack_path.to_json(),
            'combat': self.combat.to_json(),
            'stab_attack': self.stab_attack.to_json(),
            'flyer_movement_mode_0x6ca56014': self.flyer_movement_mode_0x6ca56014.to_json(),
            'flyer_movement_mode_0xe20e51c3': self.flyer_movement_mode_0xe20e51c3.to_json(),
            'flyer_movement_mode_0x25a68a0e': self.flyer_movement_mode_0x25a68a0e.to_json(),
            'flyer_movement_mode_0xd9b5d506': self.flyer_movement_mode_0xd9b5d506.to_json(),
            'flyer_movement_mode_0x8bb1c3a2': self.flyer_movement_mode_0x8bb1c3a2.to_json(),
            'stunned': self.stunned.to_json(),
            'flyer_movement_mode_0xfb2ddfad': self.flyer_movement_mode_0xfb2ddfad.to_json(),
            'dash': self.dash.to_json(),
            'flyer_movement_mode_0x5fe13a7b': self.flyer_movement_mode_0x5fe13a7b.to_json(),
            'claw': self.claw.to_json(),
            'char_0x4d7dbeab': self.char_0x4d7dbeab.to_json(),
            'char_0xa17c09bb': self.char_0xa17c09bb.to_json(),
            'char_0x11dc2dab': self.char_0x11dc2dab.to_json(),
            'char_0xfddd9abb': self.char_0xfddd9abb.to_json(),
            'unknown_0xc99cee00': self.unknown_0xc99cee00,
            'unknown_0x2ffc41e1': self.unknown_0x2ffc41e1,
            'unknown_0x7f5d9ab7': self.unknown_0x7f5d9ab7,
            'unknown_0x993d3556': self.unknown_0x993d3556,
            'unknown_0x08efeb79': self.unknown_0x08efeb79,
            'unknown_0xee8f4498': self.unknown_0xee8f4498,
            'unknown_0xc24d8fbd': self.unknown_0xc24d8fbd,
            'unknown_0x242d205c': self.unknown_0x242d205c,
            'stun_threshold': self.stun_threshold,
            'electric_ball_effect': self.electric_ball_effect,
            'sound_ball_effect': self.sound_ball_effect,
            'electric_visor_effect': self.electric_visor_effect,
            'sound_visor_effect': self.sound_visor_effect,
            'leg_hit_splash': self.leg_hit_splash,
        }


def _decode_hearing_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_lose_interest_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_lose_interest_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfe4588a1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc2688b41(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7b0cc30d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_brain_x_ray_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_brain_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb9e0c90d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x81d39802(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_tentacle_regrow_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf79a10b0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc550a481(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x95e7a2c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x76ba1c18(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe08106ed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x88d7c540(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xace62367(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x620b1b3d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attack_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_forward(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attack_forward(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0978b98a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcfcd32bb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x17d71349(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_recheck_path_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_recheck_path_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_num_metroids(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_auto_spawn(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_max_spawn_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_spawn_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6089191d(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x258b5a9f(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x2ae610e5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hatch_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_maya_double(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3fee1ba4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_spin_attack_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 30.0, 'di_knock_back_power': 20.0})


def _decode_max_spin_attack_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_spin_attack_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbeaf2105(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x54ff4d38(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb29fe2d9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dodge_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x42647ad7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa404d536(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x248d3599(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbfd77e62(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcdaa2c74(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2bca8395(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_patrol(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 3.0, 'acceleration': 1.0, 'facing_turn_rate': 30.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})


def _decode_attack_path(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 3.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})


def _decode_combat(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 3.0, 'acceleration': 10.0, 'turn_threshold': 181.0, 'floor_buffer': 11.0, 'ceiling_buffer': 8.0})


def _decode_stab_attack(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 0.10000000149011612, 'acceleration': 10.0, 'turn_rate': 10800.0, 'facing_turn_rate': 120.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 0.0, 'floor_buffer': 8.0, 'ceiling_buffer': 8.0})


def _decode_flyer_movement_mode_0x6ca56014(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 30.0, 'acceleration': 50.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 0.0, 'floor_buffer': 3.5, 'ceiling_buffer': 8.0})


def _decode_flyer_movement_mode_0xe20e51c3(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 30.0, 'acceleration': 10.0, 'facing_turn_rate': 1.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 1.0, 'floor_buffer': 5.0, 'ceiling_buffer': 8.0})


def _decode_flyer_movement_mode_0x25a68a0e(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 1.0, 'acceleration': 10.0, 'turn_threshold': 181.0, 'height_variation_max': 0.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})


def _decode_flyer_movement_mode_0xd9b5d506(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 30.0, 'acceleration': 20.0, 'facing_turn_rate': 1.0, 'turn_threshold': 181.0, 'height_variation_max': 1.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})


def _decode_flyer_movement_mode_0x8bb1c3a2(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 1.0, 'acceleration': 10.0, 'turn_threshold': 181.0, 'height_variation_max': 1.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})


def _decode_stunned(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 5.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_max': 1.0, 'floor_buffer': 5.0, 'ceiling_buffer': 8.0})


def _decode_flyer_movement_mode_0xfb2ddfad(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 5.0, 'acceleration': 10.0, 'facing_turn_rate': 15.0, 'turn_threshold': 181.0, 'use_avoidance': False, 'height_variation_min': 1.0, 'floor_buffer': 10.0, 'ceiling_buffer': 8.0})


def _decode_dash(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 40.0, 'acceleration': 100.0, 'turn_rate': 360.0, 'turn_threshold': 181.0, 'avoidance_range': 1.0, 'height_variation_max': 0.5, 'floor_buffer': 13.0, 'ceiling_buffer': 8.0})


def _decode_flyer_movement_mode_0x5fe13a7b(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'acceleration': 20.0, 'turn_threshold': 181.0, 'floor_buffer': 12.0, 'ceiling_buffer': 12.0})


def _decode_unknown_0xc99cee00(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2ffc41e1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7f5d9ab7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x993d3556(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x08efeb79(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xee8f4498(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc24d8fbd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x242d205c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_stun_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_electric_ball_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_ball_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_electric_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_leg_hit_splash(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x25474550: ('hearing_range', _decode_hearing_range),
    0x474fa589: ('lose_interest_range', _decode_lose_interest_range),
    0xf8b0c2bb: ('lose_interest_time', _decode_lose_interest_time),
    0xfe4588a1: ('unknown_0xfe4588a1', _decode_unknown_0xfe4588a1),
    0xc2688b41: ('unknown_0xc2688b41', _decode_unknown_0xc2688b41),
    0x7b0cc30d: ('unknown_0x7b0cc30d', _decode_unknown_0x7b0cc30d),
    0x742b3336: ('damage_vulnerability', DamageVulnerability.from_stream),
    0xd9230d1: ('body_vulnerability', DamageVulnerability.from_stream),
    0x243ab10d: ('brain_vulnerability', DamageVulnerability.from_stream),
    0x12115a2: ('brain_x_ray_radius', _decode_brain_x_ray_radius),
    0xa12a4409: ('brain_radius', _decode_brain_radius),
    0x9f0ff852: ('leg_vulnerability', DamageVulnerability.from_stream),
    0xb9e0c90d: ('unknown_0xb9e0c90d', _decode_unknown_0xb9e0c90d),
    0x81d39802: ('unknown_0x81d39802', _decode_unknown_0x81d39802),
    0xba002dcb: ('tentacle_regrow_time', _decode_tentacle_regrow_time),
    0xf79a10b0: ('unknown_0xf79a10b0', _decode_unknown_0xf79a10b0),
    0xc550a481: ('unknown_0xc550a481', _decode_unknown_0xc550a481),
    0x95e7a2c2: ('unknown_0x95e7a2c2', _decode_unknown_0x95e7a2c2),
    0x76ba1c18: ('unknown_0x76ba1c18', _decode_unknown_0x76ba1c18),
    0xe08106ed: ('unknown_0xe08106ed', _decode_unknown_0xe08106ed),
    0x88d7c540: ('unknown_0x88d7c540', _decode_unknown_0x88d7c540),
    0xace62367: ('unknown_0xace62367', _decode_unknown_0xace62367),
    0x620b1b3d: ('unknown_0x620b1b3d', _decode_unknown_0x620b1b3d),
    0xe1ae51d8: ('max_attack_height', _decode_max_attack_height),
    0xc8d0acc0: ('min_attack_height', _decode_min_attack_height),
    0xf3e8012d: ('max_attack_forward', _decode_max_attack_forward),
    0xe0ade786: ('min_attack_forward', _decode_min_attack_forward),
    0x978b98a: ('unknown_0x0978b98a', _decode_unknown_0x0978b98a),
    0xcfcd32bb: ('unknown_0xcfcd32bb', _decode_unknown_0xcfcd32bb),
    0x17d71349: ('unknown_0x17d71349', _decode_unknown_0x17d71349),
    0x9aa90b6b: ('recheck_path_time', _decode_recheck_path_time),
    0x7626ec89: ('recheck_path_distance', _decode_recheck_path_distance),
    0x7915e2b3: ('max_num_metroids', _decode_max_num_metroids),
    0xccc0cf92: ('auto_spawn', _decode_auto_spawn),
    0x75e0b0a7: ('max_spawn_delay', _decode_max_spawn_delay),
    0x2646a843: ('min_spawn_delay', _decode_min_spawn_delay),
    0x6089191d: ('unknown_0x6089191d', _decode_unknown_0x6089191d),
    0x258b5a9f: ('unknown_0x258b5a9f', _decode_unknown_0x258b5a9f),
    0x2ae610e5: ('unknown_0x2ae610e5', _decode_unknown_0x2ae610e5),
    0x354bae31: ('hatch_chance', _decode_hatch_chance),
    0xf4b2c801: ('maya_double', _decode_maya_double),
    0x3fee1ba4: ('unknown_0x3fee1ba4', _decode_unknown_0x3fee1ba4),
    0xcfacff53: ('spin_attack_damage', _decode_spin_attack_damage),
    0x6cb6d8c7: ('max_spin_attack_delay', _decode_max_spin_attack_delay),
    0x682ce9ed: ('min_spin_attack_delay', _decode_min_spin_attack_delay),
    0xbeaf2105: ('unknown_0xbeaf2105', _decode_unknown_0xbeaf2105),
    0x54ff4d38: ('unknown_0x54ff4d38', _decode_unknown_0x54ff4d38),
    0xb29fe2d9: ('unknown_0xb29fe2d9', _decode_unknown_0xb29fe2d9),
    0x47be3298: ('dodge_chance', _decode_dodge_chance),
    0x42647ad7: ('unknown_0x42647ad7', _decode_unknown_0x42647ad7),
    0xa404d536: ('unknown_0xa404d536', _decode_unknown_0xa404d536),
    0x248d3599: ('unknown_0x248d3599', _decode_unknown_0x248d3599),
    0xbfd77e62: ('unknown_0xbfd77e62', _decode_unknown_0xbfd77e62),
    0xcdaa2c74: ('unknown_0xcdaa2c74', _decode_unknown_0xcdaa2c74),
    0x2bca8395: ('unknown_0x2bca8395', _decode_unknown_0x2bca8395),
    0xccdd3aca: ('patrol', _decode_patrol),
    0xc845d3c0: ('attack_path', _decode_attack_path),
    0xcc7d2e98: ('combat', _decode_combat),
    0xb9c3db94: ('stab_attack', _decode_stab_attack),
    0x6ca56014: ('flyer_movement_mode_0x6ca56014', _decode_flyer_movement_mode_0x6ca56014),
    0xe20e51c3: ('flyer_movement_mode_0xe20e51c3', _decode_flyer_movement_mode_0xe20e51c3),
    0x25a68a0e: ('flyer_movement_mode_0x25a68a0e', _decode_flyer_movement_mode_0x25a68a0e),
    0xd9b5d506: ('flyer_movement_mode_0xd9b5d506', _decode_flyer_movement_mode_0xd9b5d506),
    0x8bb1c3a2: ('flyer_movement_mode_0x8bb1c3a2', _decode_flyer_movement_mode_0x8bb1c3a2),
    0x389cb515: ('stunned', _decode_stunned),
    0xfb2ddfad: ('flyer_movement_mode_0xfb2ddfad', _decode_flyer_movement_mode_0xfb2ddfad),
    0xc558bc0d: ('dash', _decode_dash),
    0x5fe13a7b: ('flyer_movement_mode_0x5fe13a7b', _decode_flyer_movement_mode_0x5fe13a7b),
    0xfd38a106: ('claw', AnimationParameters.from_stream),
    0x4d7dbeab: ('char_0x4d7dbeab', AnimationParameters.from_stream),
    0xa17c09bb: ('char_0xa17c09bb', AnimationParameters.from_stream),
    0x11dc2dab: ('char_0x11dc2dab', AnimationParameters.from_stream),
    0xfddd9abb: ('char_0xfddd9abb', AnimationParameters.from_stream),
    0xc99cee00: ('unknown_0xc99cee00', _decode_unknown_0xc99cee00),
    0x2ffc41e1: ('unknown_0x2ffc41e1', _decode_unknown_0x2ffc41e1),
    0x7f5d9ab7: ('unknown_0x7f5d9ab7', _decode_unknown_0x7f5d9ab7),
    0x993d3556: ('unknown_0x993d3556', _decode_unknown_0x993d3556),
    0x8efeb79: ('unknown_0x08efeb79', _decode_unknown_0x08efeb79),
    0xee8f4498: ('unknown_0xee8f4498', _decode_unknown_0xee8f4498),
    0xc24d8fbd: ('unknown_0xc24d8fbd', _decode_unknown_0xc24d8fbd),
    0x242d205c: ('unknown_0x242d205c', _decode_unknown_0x242d205c),
    0x5bdd1e4c: ('stun_threshold', _decode_stun_threshold),
    0x6da4a3b0: ('electric_ball_effect', _decode_electric_ball_effect),
    0x3fcd8b66: ('sound_ball_effect', _decode_sound_ball_effect),
    0xcc0af287: ('electric_visor_effect', _decode_electric_visor_effect),
    0xa3e8ec4e: ('sound_visor_effect', _decode_sound_visor_effect),
    0xf40a9c9d: ('leg_hit_splash', _decode_leg_hit_splash),
}
