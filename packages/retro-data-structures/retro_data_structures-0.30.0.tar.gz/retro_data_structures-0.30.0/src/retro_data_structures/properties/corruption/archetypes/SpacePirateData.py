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
from retro_data_structures.properties.corruption.archetypes.GrappleData import GrappleData
from retro_data_structures.properties.corruption.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.corruption.archetypes.SpacePirateStruct import SpacePirateStruct
from retro_data_structures.properties.corruption.archetypes.SpacePirateWeaponData import SpacePirateWeaponData
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class SpacePirateDataJson(typing_extensions.TypedDict):
        attack_behavior: int
        can_interrupt_tasks: bool
        warp_in: bool
        unknown_0x87929c41: bool
        unknown_0x9a0ce9b2: bool
        unknown_0x4d61342a: bool
        initial_taunt_chance: float
        combat_taunt_chance: float
        instant_attack: bool
        unknown_0x97c95a99: bool
        aggressiveness: float
        cover_check: float
        search_radius: float
        hearing_radius: float
        approach_radius: float
        unknown_0x733da88a: float
        unknown_0x03fdbe4a: bool
        dodge_check: float
        unknown_0x4ead288e: float
        no_backing_up: bool
        no_knockback_movement: bool
        no_melee_attack: bool
        blade_damage: json_util.JsonObject
        unknown_0x71587b45: float
        unknown_0x7903312e: float
        unknown_0x1b454a27: int
        gun_track_delay: float
        unknown_0x615bb850: int
        unknown_0x7b1f1541: int
        has_cloak: bool
        cloak_opacity: float
        cloak_time: float
        decloak_time: float
        cover_cloak_chance: float
        melee_cloak_chance: float
        can_combat_teleport: bool
        min_teleport_dist: float
        min_teleport_time: float
        unknown_0x2eb81206: float
        unknown_0x02e75b93: float
        unknown_0x0881a3b5: bool
        unknown_0x38b6452e: bool
        unknown_0xe3794994: float
        unknown_0x54f66da0: float
        unknown_0x506c5c8a: float
        unknown_0x159f33d6: float
        unknown_0x0524bc7e: json_util.JsonValue
        unknown_0x256b394f: json_util.JsonValue
        unknown_0x824db7ce: float
        unknown_0xe527cde8: bool
        unknown_0x61e801d4: float
        unknown_0xf19b113e: float
        unknown_0x80c6880f: float
        unknown_0x08358a6a: float
        unknown_0xa00204b0: float
        unknown_0x0806c08d: float
        unknown_0x17db0cf2: float
        sound_alert: int
        sound_hurled: int
        sound_death: int
        unknown_0x8a36b5d5: int
        unknown_0x34e20697: float
        grenade_data: json_util.JsonObject
        space_pirate_struct_0x4fdab367: json_util.JsonObject
        space_pirate_struct_0x37212693: json_util.JsonObject
        space_pirate_struct_0x91b4cb73: json_util.JsonObject
        has_shield: bool
        unknown_0x4aee5c47: bool
        shield_vulnerability: json_util.JsonObject
        hyper_shield_vulnerability: json_util.JsonObject
        unknown_0x0d1d1648: float
        char: json_util.JsonObject
        grapple_data: json_util.JsonObject
        shield_busted_scan_info: int
        has_armor: bool
        armor_health: json_util.JsonObject
        armor_vulnerability: json_util.JsonObject
        head_armor_vulnerability: json_util.JsonObject
        armor_broken_model: int
        armor_broken_skin_rules: int
        head_armor_model: int
        collar_armor_model: int
        left_collar_armor_model: int
        right_collar_armor_model: int
        spine1_armor_model: int
        spine2_armor_model: int
        left_hip_armor_model: int
        right_hip_armor_model: int
        skeleton_root_armor_model: int
        is_gandrayda: bool
        unknown_0x040a4edf: int
        unknown_0x5c572665: int
        unknown_0xcca41d93: float
        unknown_0x767f168e: bool
        keep_target_time: float
        unknown_0x668ec0a0: float
        unknown_0x14950f43: float
        unknown_0x761ed7af: int
    

@dataclasses.dataclass()
class SpacePirateData(BaseProperty):
    attack_behavior: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x8e1e1586, original_name='AttackBehavior'
        ),
    })
    can_interrupt_tasks: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa40cb847, original_name='CanInterruptTasks'
        ),
    })
    warp_in: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7428a29f, original_name='WarpIn'
        ),
    })
    unknown_0x87929c41: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x87929c41, original_name='Unknown'
        ),
    })
    unknown_0x9a0ce9b2: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x9a0ce9b2, original_name='Unknown'
        ),
    })
    unknown_0x4d61342a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4d61342a, original_name='Unknown'
        ),
    })
    initial_taunt_chance: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2d8264ea, original_name='InitialTauntChance'
        ),
    })
    combat_taunt_chance: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa6af0c57, original_name='CombatTauntChance'
        ),
    })
    instant_attack: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x6697712a, original_name='InstantAttack'
        ),
    })
    unknown_0x97c95a99: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x97c95a99, original_name='Unknown'
        ),
    })
    aggressiveness: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9579b1f2, original_name='Aggressiveness'
        ),
    })
    cover_check: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf89ab419, original_name='CoverCheck'
        ),
    })
    search_radius: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed9bf5a3, original_name='SearchRadius'
        ),
    })
    hearing_radius: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed69488f, original_name='HearingRadius'
        ),
    })
    approach_radius: float = dataclasses.field(default=1000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3cb99b1e, original_name='ApproachRadius'
        ),
    })
    unknown_0x733da88a: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x733da88a, original_name='Unknown'
        ),
    })
    unknown_0x03fdbe4a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x03fdbe4a, original_name='Unknown'
        ),
    })
    dodge_check: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdc36e745, original_name='DodgeCheck'
        ),
    })
    unknown_0x4ead288e: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4ead288e, original_name='Unknown'
        ),
    })
    no_backing_up: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf11ec8ee, original_name='NoBackingUp'
        ),
    })
    no_knockback_movement: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x808576ee, original_name='NoKnockbackMovement'
        ),
    })
    no_melee_attack: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x6bc22735, original_name='NoMeleeAttack'
        ),
    })
    blade_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xa5912430, original_name='BladeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x71587b45: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x71587b45, original_name='Unknown'
        ),
    })
    unknown_0x7903312e: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7903312e, original_name='Unknown'
        ),
    })
    unknown_0x1b454a27: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1b454a27, original_name='Unknown'
        ),
    })
    gun_track_delay: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb2ac2d96, original_name='GunTrackDelay'
        ),
    })
    unknown_0x615bb850: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x615bb850, original_name='Unknown'
        ),
    })
    unknown_0x7b1f1541: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7b1f1541, original_name='Unknown'
        ),
    })
    has_cloak: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7a4b4aea, original_name='HasCloak'
        ),
    })
    cloak_opacity: float = dataclasses.field(default=0.02500000037252903, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5bc6f1d5, original_name='CloakOpacity'
        ),
    })
    cloak_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x388bc31f, original_name='CloakTime'
        ),
    })
    decloak_time: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4319c840, original_name='DecloakTime'
        ),
    })
    cover_cloak_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8aa60b6c, original_name='CoverCloakChance'
        ),
    })
    melee_cloak_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x57e862aa, original_name='MeleeCloakChance'
        ),
    })
    can_combat_teleport: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xfcd4ed64, original_name='CanCombatTeleport'
        ),
    })
    min_teleport_dist: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfaa81d3a, original_name='MinTeleportDist'
        ),
    })
    min_teleport_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa90369e6, original_name='MinTeleportTime'
        ),
    })
    unknown_0x2eb81206: float = dataclasses.field(default=150.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2eb81206, original_name='Unknown'
        ),
    })
    unknown_0x02e75b93: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x02e75b93, original_name='Unknown'
        ),
    })
    unknown_0x0881a3b5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0881a3b5, original_name='Unknown'
        ),
    })
    unknown_0x38b6452e: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x38b6452e, original_name='Unknown'
        ),
    })
    unknown_0xe3794994: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe3794994, original_name='Unknown'
        ),
    })
    unknown_0x54f66da0: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x54f66da0, original_name='Unknown'
        ),
    })
    unknown_0x506c5c8a: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x506c5c8a, original_name='Unknown'
        ),
    })
    unknown_0x159f33d6: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x159f33d6, original_name='Unknown'
        ),
    })
    unknown_0x0524bc7e: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x0524bc7e, original_name='Unknown', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_0x256b394f: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x256b394f, original_name='Unknown', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_0x824db7ce: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x824db7ce, original_name='Unknown'
        ),
    })
    unknown_0xe527cde8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe527cde8, original_name='Unknown'
        ),
    })
    unknown_0x61e801d4: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x61e801d4, original_name='Unknown'
        ),
    })
    unknown_0xf19b113e: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf19b113e, original_name='Unknown'
        ),
    })
    unknown_0x80c6880f: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x80c6880f, original_name='Unknown'
        ),
    })
    unknown_0x08358a6a: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x08358a6a, original_name='Unknown'
        ),
    })
    unknown_0xa00204b0: float = dataclasses.field(default=16.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa00204b0, original_name='Unknown'
        ),
    })
    unknown_0x0806c08d: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0806c08d, original_name='Unknown'
        ),
    })
    unknown_0x17db0cf2: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x17db0cf2, original_name='Unknown'
        ),
    })
    sound_alert: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc245a874, original_name='Sound_Alert'
        ),
    })
    sound_hurled: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc192e357, original_name='Sound_Hurled'
        ),
    })
    sound_death: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1b412c4b, original_name='Sound_Death'
        ),
    })
    unknown_0x8a36b5d5: int = dataclasses.field(default=10000, metadata={
        'reflection': FieldReflection[int](
            int, id=0x8a36b5d5, original_name='Unknown'
        ),
    })
    unknown_0x34e20697: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x34e20697, original_name='Unknown'
        ),
    })
    grenade_data: SpacePirateWeaponData = dataclasses.field(default_factory=SpacePirateWeaponData, metadata={
        'reflection': FieldReflection[SpacePirateWeaponData](
            SpacePirateWeaponData, id=0xc3b6103b, original_name='GrenadeData', from_json=SpacePirateWeaponData.from_json, to_json=SpacePirateWeaponData.to_json
        ),
    })
    space_pirate_struct_0x4fdab367: SpacePirateStruct = dataclasses.field(default_factory=SpacePirateStruct, metadata={
        'reflection': FieldReflection[SpacePirateStruct](
            SpacePirateStruct, id=0x4fdab367, original_name='SpacePirateStruct', from_json=SpacePirateStruct.from_json, to_json=SpacePirateStruct.to_json
        ),
    })
    space_pirate_struct_0x37212693: SpacePirateStruct = dataclasses.field(default_factory=SpacePirateStruct, metadata={
        'reflection': FieldReflection[SpacePirateStruct](
            SpacePirateStruct, id=0x37212693, original_name='SpacePirateStruct', from_json=SpacePirateStruct.from_json, to_json=SpacePirateStruct.to_json
        ),
    })
    space_pirate_struct_0x91b4cb73: SpacePirateStruct = dataclasses.field(default_factory=SpacePirateStruct, metadata={
        'reflection': FieldReflection[SpacePirateStruct](
            SpacePirateStruct, id=0x91b4cb73, original_name='SpacePirateStruct', from_json=SpacePirateStruct.from_json, to_json=SpacePirateStruct.to_json
        ),
    })
    has_shield: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x07c1de29, original_name='HasShield'
        ),
    })
    unknown_0x4aee5c47: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4aee5c47, original_name='Unknown'
        ),
    })
    shield_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xd34f1323, original_name='ShieldVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    hyper_shield_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x8255f594, original_name='HyperShieldVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_0x0d1d1648: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d1d1648, original_name='Unknown'
        ),
    })
    char: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xc699ad35, original_name='CHAR', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    grapple_data: GrappleData = dataclasses.field(default_factory=GrappleData, metadata={
        'reflection': FieldReflection[GrappleData](
            GrappleData, id=0xbe1afbc0, original_name='GrappleData', from_json=GrappleData.from_json, to_json=GrappleData.to_json
        ),
    })
    shield_busted_scan_info: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x71e83f06, original_name='ShieldBustedScanInfo'
        ),
    })
    has_armor: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xfde9c4df, original_name='HasArmor'
        ),
    })
    armor_health: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0xf18384d4, original_name='ArmorHealth', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    armor_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x896d5bd9, original_name='ArmorVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    head_armor_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xc13a3e1f, original_name='HeadArmorVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    armor_broken_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7579cc86, original_name='ArmorBrokenModel'
        ),
    })
    armor_broken_skin_rules: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CSKR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x65d86552, original_name='ArmorBrokenSkinRules'
        ),
    })
    head_armor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x68002bd7, original_name='HeadArmorModel'
        ),
    })
    collar_armor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xad315c7c, original_name='CollarArmorModel'
        ),
    })
    left_collar_armor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x042a25ed, original_name='LeftCollarArmorModel'
        ),
    })
    right_collar_armor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe39b8b1e, original_name='RightCollarArmorModel'
        ),
    })
    spine1_armor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x356c166a, original_name='Spine1ArmorModel'
        ),
    })
    spine2_armor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1ca4a298, original_name='Spine2ArmorModel'
        ),
    })
    left_hip_armor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xdf44507e, original_name='LeftHipArmorModel'
        ),
    })
    right_hip_armor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd2c9a656, original_name='RightHipArmorModel'
        ),
    })
    skeleton_root_armor_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd4e26a8e, original_name='SkeletonRootArmorModel'
        ),
    })
    is_gandrayda: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x531a8c85, original_name='IsGandrayda'
        ),
    })
    unknown_0x040a4edf: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x040a4edf, original_name='Unknown'
        ),
    })
    unknown_0x5c572665: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5c572665, original_name='Unknown'
        ),
    })
    unknown_0xcca41d93: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcca41d93, original_name='Unknown'
        ),
    })
    unknown_0x767f168e: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x767f168e, original_name='Unknown'
        ),
    })
    keep_target_time: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x89a5edc8, original_name='KeepTargetTime'
        ),
    })
    unknown_0x668ec0a0: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x668ec0a0, original_name='Unknown'
        ),
    })
    unknown_0x14950f43: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x14950f43, original_name='Unknown'
        ),
    })
    unknown_0x761ed7af: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x761ed7af, original_name='Unknown'
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
        if property_count != 98:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8e1e1586
        attack_behavior = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa40cb847
        can_interrupt_tasks = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7428a29f
        warp_in = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87929c41
        unknown_0x87929c41 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a0ce9b2
        unknown_0x9a0ce9b2 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d61342a
        unknown_0x4d61342a = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2d8264ea
        initial_taunt_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6af0c57
        combat_taunt_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6697712a
        instant_attack = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x97c95a99
        unknown_0x97c95a99 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9579b1f2
        aggressiveness = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf89ab419
        cover_check = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed9bf5a3
        search_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed69488f
        hearing_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3cb99b1e
        approach_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x733da88a
        unknown_0x733da88a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03fdbe4a
        unknown_0x03fdbe4a = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdc36e745
        dodge_check = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ead288e
        unknown_0x4ead288e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf11ec8ee
        no_backing_up = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x808576ee
        no_knockback_movement = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6bc22735
        no_melee_attack = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa5912430
        blade_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 10.0, 'di_knock_back_power': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71587b45
        unknown_0x71587b45 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7903312e
        unknown_0x7903312e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b454a27
        unknown_0x1b454a27 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2ac2d96
        gun_track_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x615bb850
        unknown_0x615bb850 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b1f1541
        unknown_0x7b1f1541 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a4b4aea
        has_cloak = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5bc6f1d5
        cloak_opacity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x388bc31f
        cloak_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4319c840
        decloak_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8aa60b6c
        cover_cloak_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x57e862aa
        melee_cloak_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfcd4ed64
        can_combat_teleport = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfaa81d3a
        min_teleport_dist = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa90369e6
        min_teleport_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2eb81206
        unknown_0x2eb81206 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x02e75b93
        unknown_0x02e75b93 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0881a3b5
        unknown_0x0881a3b5 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x38b6452e
        unknown_0x38b6452e = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe3794994
        unknown_0xe3794994 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x54f66da0
        unknown_0x54f66da0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x506c5c8a
        unknown_0x506c5c8a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x159f33d6
        unknown_0x159f33d6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0524bc7e
        unknown_0x0524bc7e = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x256b394f
        unknown_0x256b394f = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x824db7ce
        unknown_0x824db7ce = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe527cde8
        unknown_0xe527cde8 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x61e801d4
        unknown_0x61e801d4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf19b113e
        unknown_0xf19b113e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80c6880f
        unknown_0x80c6880f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08358a6a
        unknown_0x08358a6a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa00204b0
        unknown_0xa00204b0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0806c08d
        unknown_0x0806c08d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x17db0cf2
        unknown_0x17db0cf2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc245a874
        sound_alert = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc192e357
        sound_hurled = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b412c4b
        sound_death = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a36b5d5
        unknown_0x8a36b5d5 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x34e20697
        unknown_0x34e20697 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3b6103b
        grenade_data = SpacePirateWeaponData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4fdab367
        space_pirate_struct_0x4fdab367 = SpacePirateStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37212693
        space_pirate_struct_0x37212693 = SpacePirateStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x91b4cb73
        space_pirate_struct_0x91b4cb73 = SpacePirateStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x07c1de29
        has_shield = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4aee5c47
        unknown_0x4aee5c47 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd34f1323
        shield_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8255f594
        hyper_shield_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d1d1648
        unknown_0x0d1d1648 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc699ad35
        char = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe1afbc0
        grapple_data = GrappleData.from_stream(data, property_size, default_override={'grapple_type': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71e83f06
        shield_busted_scan_info = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfde9c4df
        has_armor = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf18384d4
        armor_health = HealthInfo.from_stream(data, property_size, default_override={'health': 100.0, 'hi_knock_back_resistance': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x896d5bd9
        armor_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc13a3e1f
        head_armor_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7579cc86
        armor_broken_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x65d86552
        armor_broken_skin_rules = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68002bd7
        head_armor_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad315c7c
        collar_armor_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x042a25ed
        left_collar_armor_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe39b8b1e
        right_collar_armor_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x356c166a
        spine1_armor_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ca4a298
        spine2_armor_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdf44507e
        left_hip_armor_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd2c9a656
        right_hip_armor_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4e26a8e
        skeleton_root_armor_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x531a8c85
        is_gandrayda = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x040a4edf
        unknown_0x040a4edf = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5c572665
        unknown_0x5c572665 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcca41d93
        unknown_0xcca41d93 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x767f168e
        unknown_0x767f168e = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x89a5edc8
        keep_target_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x668ec0a0
        unknown_0x668ec0a0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x14950f43
        unknown_0x14950f43 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x761ed7af
        unknown_0x761ed7af = struct.unpack('>l', data.read(4))[0]
    
        return cls(attack_behavior, can_interrupt_tasks, warp_in, unknown_0x87929c41, unknown_0x9a0ce9b2, unknown_0x4d61342a, initial_taunt_chance, combat_taunt_chance, instant_attack, unknown_0x97c95a99, aggressiveness, cover_check, search_radius, hearing_radius, approach_radius, unknown_0x733da88a, unknown_0x03fdbe4a, dodge_check, unknown_0x4ead288e, no_backing_up, no_knockback_movement, no_melee_attack, blade_damage, unknown_0x71587b45, unknown_0x7903312e, unknown_0x1b454a27, gun_track_delay, unknown_0x615bb850, unknown_0x7b1f1541, has_cloak, cloak_opacity, cloak_time, decloak_time, cover_cloak_chance, melee_cloak_chance, can_combat_teleport, min_teleport_dist, min_teleport_time, unknown_0x2eb81206, unknown_0x02e75b93, unknown_0x0881a3b5, unknown_0x38b6452e, unknown_0xe3794994, unknown_0x54f66da0, unknown_0x506c5c8a, unknown_0x159f33d6, unknown_0x0524bc7e, unknown_0x256b394f, unknown_0x824db7ce, unknown_0xe527cde8, unknown_0x61e801d4, unknown_0xf19b113e, unknown_0x80c6880f, unknown_0x08358a6a, unknown_0xa00204b0, unknown_0x0806c08d, unknown_0x17db0cf2, sound_alert, sound_hurled, sound_death, unknown_0x8a36b5d5, unknown_0x34e20697, grenade_data, space_pirate_struct_0x4fdab367, space_pirate_struct_0x37212693, space_pirate_struct_0x91b4cb73, has_shield, unknown_0x4aee5c47, shield_vulnerability, hyper_shield_vulnerability, unknown_0x0d1d1648, char, grapple_data, shield_busted_scan_info, has_armor, armor_health, armor_vulnerability, head_armor_vulnerability, armor_broken_model, armor_broken_skin_rules, head_armor_model, collar_armor_model, left_collar_armor_model, right_collar_armor_model, spine1_armor_model, spine2_armor_model, left_hip_armor_model, right_hip_armor_model, skeleton_root_armor_model, is_gandrayda, unknown_0x040a4edf, unknown_0x5c572665, unknown_0xcca41d93, unknown_0x767f168e, keep_target_time, unknown_0x668ec0a0, unknown_0x14950f43, unknown_0x761ed7af)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00b')  # 98 properties

        data.write(b'\x8e\x1e\x15\x86')  # 0x8e1e1586
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.attack_behavior))

        data.write(b'\xa4\x0c\xb8G')  # 0xa40cb847
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.can_interrupt_tasks))

        data.write(b't(\xa2\x9f')  # 0x7428a29f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.warp_in))

        data.write(b'\x87\x92\x9cA')  # 0x87929c41
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x87929c41))

        data.write(b'\x9a\x0c\xe9\xb2')  # 0x9a0ce9b2
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x9a0ce9b2))

        data.write(b'Ma4*')  # 0x4d61342a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4d61342a))

        data.write(b'-\x82d\xea')  # 0x2d8264ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.initial_taunt_chance))

        data.write(b'\xa6\xaf\x0cW')  # 0xa6af0c57
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.combat_taunt_chance))

        data.write(b'f\x97q*')  # 0x6697712a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.instant_attack))

        data.write(b'\x97\xc9Z\x99')  # 0x97c95a99
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x97c95a99))

        data.write(b'\x95y\xb1\xf2')  # 0x9579b1f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aggressiveness))

        data.write(b'\xf8\x9a\xb4\x19')  # 0xf89ab419
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cover_check))

        data.write(b'\xed\x9b\xf5\xa3')  # 0xed9bf5a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.search_radius))

        data.write(b'\xediH\x8f')  # 0xed69488f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hearing_radius))

        data.write(b'<\xb9\x9b\x1e')  # 0x3cb99b1e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.approach_radius))

        data.write(b's=\xa8\x8a')  # 0x733da88a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x733da88a))

        data.write(b'\x03\xfd\xbeJ')  # 0x3fdbe4a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x03fdbe4a))

        data.write(b'\xdc6\xe7E')  # 0xdc36e745
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_check))

        data.write(b'N\xad(\x8e')  # 0x4ead288e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4ead288e))

        data.write(b'\xf1\x1e\xc8\xee')  # 0xf11ec8ee
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.no_backing_up))

        data.write(b'\x80\x85v\xee')  # 0x808576ee
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.no_knockback_movement))

        data.write(b"k\xc2'5")  # 0x6bc22735
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.no_melee_attack))

        data.write(b'\xa5\x91$0')  # 0xa5912430
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.blade_damage.to_stream(data, default_override={'di_damage': 10.0, 'di_knock_back_power': 5.0})
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

        data.write(b"\x1bEJ'")  # 0x1b454a27
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x1b454a27))

        data.write(b'\xb2\xac-\x96')  # 0xb2ac2d96
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.gun_track_delay))

        data.write(b'a[\xb8P')  # 0x615bb850
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x615bb850))

        data.write(b'{\x1f\x15A')  # 0x7b1f1541
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x7b1f1541))

        data.write(b'zKJ\xea')  # 0x7a4b4aea
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.has_cloak))

        data.write(b'[\xc6\xf1\xd5')  # 0x5bc6f1d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cloak_opacity))

        data.write(b'8\x8b\xc3\x1f')  # 0x388bc31f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cloak_time))

        data.write(b'C\x19\xc8@')  # 0x4319c840
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.decloak_time))

        data.write(b'\x8a\xa6\x0bl')  # 0x8aa60b6c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cover_cloak_chance))

        data.write(b'W\xe8b\xaa')  # 0x57e862aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_cloak_chance))

        data.write(b'\xfc\xd4\xedd')  # 0xfcd4ed64
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.can_combat_teleport))

        data.write(b'\xfa\xa8\x1d:')  # 0xfaa81d3a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_teleport_dist))

        data.write(b'\xa9\x03i\xe6')  # 0xa90369e6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_teleport_time))

        data.write(b'.\xb8\x12\x06')  # 0x2eb81206
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2eb81206))

        data.write(b'\x02\xe7[\x93')  # 0x2e75b93
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x02e75b93))

        data.write(b'\x08\x81\xa3\xb5')  # 0x881a3b5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x0881a3b5))

        data.write(b'8\xb6E.')  # 0x38b6452e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x38b6452e))

        data.write(b'\xe3yI\x94')  # 0xe3794994
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe3794994))

        data.write(b'T\xf6m\xa0')  # 0x54f66da0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x54f66da0))

        data.write(b'Pl\\\x8a')  # 0x506c5c8a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x506c5c8a))

        data.write(b'\x15\x9f3\xd6')  # 0x159f33d6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x159f33d6))

        data.write(b'\x05$\xbc~')  # 0x524bc7e
        data.write(b'\x00\x0c')  # size
        self.unknown_0x0524bc7e.to_stream(data)

        data.write(b'%k9O')  # 0x256b394f
        data.write(b'\x00\x0c')  # size
        self.unknown_0x256b394f.to_stream(data)

        data.write(b'\x82M\xb7\xce')  # 0x824db7ce
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x824db7ce))

        data.write(b"\xe5'\xcd\xe8")  # 0xe527cde8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xe527cde8))

        data.write(b'a\xe8\x01\xd4')  # 0x61e801d4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x61e801d4))

        data.write(b'\xf1\x9b\x11>')  # 0xf19b113e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf19b113e))

        data.write(b'\x80\xc6\x88\x0f')  # 0x80c6880f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x80c6880f))

        data.write(b'\x085\x8aj')  # 0x8358a6a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x08358a6a))

        data.write(b'\xa0\x02\x04\xb0')  # 0xa00204b0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa00204b0))

        data.write(b'\x08\x06\xc0\x8d')  # 0x806c08d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0806c08d))

        data.write(b'\x17\xdb\x0c\xf2')  # 0x17db0cf2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x17db0cf2))

        data.write(b'\xc2E\xa8t')  # 0xc245a874
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_alert))

        data.write(b'\xc1\x92\xe3W')  # 0xc192e357
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_hurled))

        data.write(b'\x1bA,K')  # 0x1b412c4b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_death))

        data.write(b'\x8a6\xb5\xd5')  # 0x8a36b5d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x8a36b5d5))

        data.write(b'4\xe2\x06\x97')  # 0x34e20697
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x34e20697))

        data.write(b'\xc3\xb6\x10;')  # 0xc3b6103b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grenade_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'O\xda\xb3g')  # 0x4fdab367
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.space_pirate_struct_0x4fdab367.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'7!&\x93')  # 0x37212693
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.space_pirate_struct_0x37212693.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x91\xb4\xcbs')  # 0x91b4cb73
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.space_pirate_struct_0x91b4cb73.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x07\xc1\xde)')  # 0x7c1de29
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.has_shield))

        data.write(b'J\xee\\G')  # 0x4aee5c47
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4aee5c47))

        data.write(b'\xd3O\x13#')  # 0xd34f1323
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shield_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x82U\xf5\x94')  # 0x8255f594
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_shield_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\r\x1d\x16H')  # 0xd1d1648
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0d1d1648))

        data.write(b'\xc6\x99\xad5')  # 0xc699ad35
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.char.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbe\x1a\xfb\xc0')  # 0xbe1afbc0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_data.to_stream(data, default_override={'grapple_type': 1})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'q\xe8?\x06')  # 0x71e83f06
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.shield_busted_scan_info))

        data.write(b'\xfd\xe9\xc4\xdf')  # 0xfde9c4df
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.has_armor))

        data.write(b'\xf1\x83\x84\xd4')  # 0xf18384d4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.armor_health.to_stream(data, default_override={'health': 100.0, 'hi_knock_back_resistance': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x89m[\xd9')  # 0x896d5bd9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.armor_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc1:>\x1f')  # 0xc13a3e1f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.head_armor_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'uy\xcc\x86')  # 0x7579cc86
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.armor_broken_model))

        data.write(b'e\xd8eR')  # 0x65d86552
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.armor_broken_skin_rules))

        data.write(b'h\x00+\xd7')  # 0x68002bd7
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.head_armor_model))

        data.write(b'\xad1\\|')  # 0xad315c7c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.collar_armor_model))

        data.write(b'\x04*%\xed')  # 0x42a25ed
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.left_collar_armor_model))

        data.write(b'\xe3\x9b\x8b\x1e')  # 0xe39b8b1e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.right_collar_armor_model))

        data.write(b'5l\x16j')  # 0x356c166a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.spine1_armor_model))

        data.write(b'\x1c\xa4\xa2\x98')  # 0x1ca4a298
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.spine2_armor_model))

        data.write(b'\xdfDP~')  # 0xdf44507e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.left_hip_armor_model))

        data.write(b'\xd2\xc9\xa6V')  # 0xd2c9a656
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.right_hip_armor_model))

        data.write(b'\xd4\xe2j\x8e')  # 0xd4e26a8e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.skeleton_root_armor_model))

        data.write(b'S\x1a\x8c\x85')  # 0x531a8c85
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_gandrayda))

        data.write(b'\x04\nN\xdf')  # 0x40a4edf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x040a4edf))

        data.write(b'\\W&e')  # 0x5c572665
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x5c572665))

        data.write(b'\xcc\xa4\x1d\x93')  # 0xcca41d93
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcca41d93))

        data.write(b'v\x7f\x16\x8e')  # 0x767f168e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x767f168e))

        data.write(b'\x89\xa5\xed\xc8')  # 0x89a5edc8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.keep_target_time))

        data.write(b'f\x8e\xc0\xa0')  # 0x668ec0a0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x668ec0a0))

        data.write(b'\x14\x95\x0fC')  # 0x14950f43
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x14950f43))

        data.write(b'v\x1e\xd7\xaf')  # 0x761ed7af
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x761ed7af))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpacePirateDataJson", data)
        return cls(
            attack_behavior=json_data['attack_behavior'],
            can_interrupt_tasks=json_data['can_interrupt_tasks'],
            warp_in=json_data['warp_in'],
            unknown_0x87929c41=json_data['unknown_0x87929c41'],
            unknown_0x9a0ce9b2=json_data['unknown_0x9a0ce9b2'],
            unknown_0x4d61342a=json_data['unknown_0x4d61342a'],
            initial_taunt_chance=json_data['initial_taunt_chance'],
            combat_taunt_chance=json_data['combat_taunt_chance'],
            instant_attack=json_data['instant_attack'],
            unknown_0x97c95a99=json_data['unknown_0x97c95a99'],
            aggressiveness=json_data['aggressiveness'],
            cover_check=json_data['cover_check'],
            search_radius=json_data['search_radius'],
            hearing_radius=json_data['hearing_radius'],
            approach_radius=json_data['approach_radius'],
            unknown_0x733da88a=json_data['unknown_0x733da88a'],
            unknown_0x03fdbe4a=json_data['unknown_0x03fdbe4a'],
            dodge_check=json_data['dodge_check'],
            unknown_0x4ead288e=json_data['unknown_0x4ead288e'],
            no_backing_up=json_data['no_backing_up'],
            no_knockback_movement=json_data['no_knockback_movement'],
            no_melee_attack=json_data['no_melee_attack'],
            blade_damage=DamageInfo.from_json(json_data['blade_damage']),
            unknown_0x71587b45=json_data['unknown_0x71587b45'],
            unknown_0x7903312e=json_data['unknown_0x7903312e'],
            unknown_0x1b454a27=json_data['unknown_0x1b454a27'],
            gun_track_delay=json_data['gun_track_delay'],
            unknown_0x615bb850=json_data['unknown_0x615bb850'],
            unknown_0x7b1f1541=json_data['unknown_0x7b1f1541'],
            has_cloak=json_data['has_cloak'],
            cloak_opacity=json_data['cloak_opacity'],
            cloak_time=json_data['cloak_time'],
            decloak_time=json_data['decloak_time'],
            cover_cloak_chance=json_data['cover_cloak_chance'],
            melee_cloak_chance=json_data['melee_cloak_chance'],
            can_combat_teleport=json_data['can_combat_teleport'],
            min_teleport_dist=json_data['min_teleport_dist'],
            min_teleport_time=json_data['min_teleport_time'],
            unknown_0x2eb81206=json_data['unknown_0x2eb81206'],
            unknown_0x02e75b93=json_data['unknown_0x02e75b93'],
            unknown_0x0881a3b5=json_data['unknown_0x0881a3b5'],
            unknown_0x38b6452e=json_data['unknown_0x38b6452e'],
            unknown_0xe3794994=json_data['unknown_0xe3794994'],
            unknown_0x54f66da0=json_data['unknown_0x54f66da0'],
            unknown_0x506c5c8a=json_data['unknown_0x506c5c8a'],
            unknown_0x159f33d6=json_data['unknown_0x159f33d6'],
            unknown_0x0524bc7e=Vector.from_json(json_data['unknown_0x0524bc7e']),
            unknown_0x256b394f=Vector.from_json(json_data['unknown_0x256b394f']),
            unknown_0x824db7ce=json_data['unknown_0x824db7ce'],
            unknown_0xe527cde8=json_data['unknown_0xe527cde8'],
            unknown_0x61e801d4=json_data['unknown_0x61e801d4'],
            unknown_0xf19b113e=json_data['unknown_0xf19b113e'],
            unknown_0x80c6880f=json_data['unknown_0x80c6880f'],
            unknown_0x08358a6a=json_data['unknown_0x08358a6a'],
            unknown_0xa00204b0=json_data['unknown_0xa00204b0'],
            unknown_0x0806c08d=json_data['unknown_0x0806c08d'],
            unknown_0x17db0cf2=json_data['unknown_0x17db0cf2'],
            sound_alert=json_data['sound_alert'],
            sound_hurled=json_data['sound_hurled'],
            sound_death=json_data['sound_death'],
            unknown_0x8a36b5d5=json_data['unknown_0x8a36b5d5'],
            unknown_0x34e20697=json_data['unknown_0x34e20697'],
            grenade_data=SpacePirateWeaponData.from_json(json_data['grenade_data']),
            space_pirate_struct_0x4fdab367=SpacePirateStruct.from_json(json_data['space_pirate_struct_0x4fdab367']),
            space_pirate_struct_0x37212693=SpacePirateStruct.from_json(json_data['space_pirate_struct_0x37212693']),
            space_pirate_struct_0x91b4cb73=SpacePirateStruct.from_json(json_data['space_pirate_struct_0x91b4cb73']),
            has_shield=json_data['has_shield'],
            unknown_0x4aee5c47=json_data['unknown_0x4aee5c47'],
            shield_vulnerability=DamageVulnerability.from_json(json_data['shield_vulnerability']),
            hyper_shield_vulnerability=DamageVulnerability.from_json(json_data['hyper_shield_vulnerability']),
            unknown_0x0d1d1648=json_data['unknown_0x0d1d1648'],
            char=AnimationParameters.from_json(json_data['char']),
            grapple_data=GrappleData.from_json(json_data['grapple_data']),
            shield_busted_scan_info=json_data['shield_busted_scan_info'],
            has_armor=json_data['has_armor'],
            armor_health=HealthInfo.from_json(json_data['armor_health']),
            armor_vulnerability=DamageVulnerability.from_json(json_data['armor_vulnerability']),
            head_armor_vulnerability=DamageVulnerability.from_json(json_data['head_armor_vulnerability']),
            armor_broken_model=json_data['armor_broken_model'],
            armor_broken_skin_rules=json_data['armor_broken_skin_rules'],
            head_armor_model=json_data['head_armor_model'],
            collar_armor_model=json_data['collar_armor_model'],
            left_collar_armor_model=json_data['left_collar_armor_model'],
            right_collar_armor_model=json_data['right_collar_armor_model'],
            spine1_armor_model=json_data['spine1_armor_model'],
            spine2_armor_model=json_data['spine2_armor_model'],
            left_hip_armor_model=json_data['left_hip_armor_model'],
            right_hip_armor_model=json_data['right_hip_armor_model'],
            skeleton_root_armor_model=json_data['skeleton_root_armor_model'],
            is_gandrayda=json_data['is_gandrayda'],
            unknown_0x040a4edf=json_data['unknown_0x040a4edf'],
            unknown_0x5c572665=json_data['unknown_0x5c572665'],
            unknown_0xcca41d93=json_data['unknown_0xcca41d93'],
            unknown_0x767f168e=json_data['unknown_0x767f168e'],
            keep_target_time=json_data['keep_target_time'],
            unknown_0x668ec0a0=json_data['unknown_0x668ec0a0'],
            unknown_0x14950f43=json_data['unknown_0x14950f43'],
            unknown_0x761ed7af=json_data['unknown_0x761ed7af'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'attack_behavior': self.attack_behavior,
            'can_interrupt_tasks': self.can_interrupt_tasks,
            'warp_in': self.warp_in,
            'unknown_0x87929c41': self.unknown_0x87929c41,
            'unknown_0x9a0ce9b2': self.unknown_0x9a0ce9b2,
            'unknown_0x4d61342a': self.unknown_0x4d61342a,
            'initial_taunt_chance': self.initial_taunt_chance,
            'combat_taunt_chance': self.combat_taunt_chance,
            'instant_attack': self.instant_attack,
            'unknown_0x97c95a99': self.unknown_0x97c95a99,
            'aggressiveness': self.aggressiveness,
            'cover_check': self.cover_check,
            'search_radius': self.search_radius,
            'hearing_radius': self.hearing_radius,
            'approach_radius': self.approach_radius,
            'unknown_0x733da88a': self.unknown_0x733da88a,
            'unknown_0x03fdbe4a': self.unknown_0x03fdbe4a,
            'dodge_check': self.dodge_check,
            'unknown_0x4ead288e': self.unknown_0x4ead288e,
            'no_backing_up': self.no_backing_up,
            'no_knockback_movement': self.no_knockback_movement,
            'no_melee_attack': self.no_melee_attack,
            'blade_damage': self.blade_damage.to_json(),
            'unknown_0x71587b45': self.unknown_0x71587b45,
            'unknown_0x7903312e': self.unknown_0x7903312e,
            'unknown_0x1b454a27': self.unknown_0x1b454a27,
            'gun_track_delay': self.gun_track_delay,
            'unknown_0x615bb850': self.unknown_0x615bb850,
            'unknown_0x7b1f1541': self.unknown_0x7b1f1541,
            'has_cloak': self.has_cloak,
            'cloak_opacity': self.cloak_opacity,
            'cloak_time': self.cloak_time,
            'decloak_time': self.decloak_time,
            'cover_cloak_chance': self.cover_cloak_chance,
            'melee_cloak_chance': self.melee_cloak_chance,
            'can_combat_teleport': self.can_combat_teleport,
            'min_teleport_dist': self.min_teleport_dist,
            'min_teleport_time': self.min_teleport_time,
            'unknown_0x2eb81206': self.unknown_0x2eb81206,
            'unknown_0x02e75b93': self.unknown_0x02e75b93,
            'unknown_0x0881a3b5': self.unknown_0x0881a3b5,
            'unknown_0x38b6452e': self.unknown_0x38b6452e,
            'unknown_0xe3794994': self.unknown_0xe3794994,
            'unknown_0x54f66da0': self.unknown_0x54f66da0,
            'unknown_0x506c5c8a': self.unknown_0x506c5c8a,
            'unknown_0x159f33d6': self.unknown_0x159f33d6,
            'unknown_0x0524bc7e': self.unknown_0x0524bc7e.to_json(),
            'unknown_0x256b394f': self.unknown_0x256b394f.to_json(),
            'unknown_0x824db7ce': self.unknown_0x824db7ce,
            'unknown_0xe527cde8': self.unknown_0xe527cde8,
            'unknown_0x61e801d4': self.unknown_0x61e801d4,
            'unknown_0xf19b113e': self.unknown_0xf19b113e,
            'unknown_0x80c6880f': self.unknown_0x80c6880f,
            'unknown_0x08358a6a': self.unknown_0x08358a6a,
            'unknown_0xa00204b0': self.unknown_0xa00204b0,
            'unknown_0x0806c08d': self.unknown_0x0806c08d,
            'unknown_0x17db0cf2': self.unknown_0x17db0cf2,
            'sound_alert': self.sound_alert,
            'sound_hurled': self.sound_hurled,
            'sound_death': self.sound_death,
            'unknown_0x8a36b5d5': self.unknown_0x8a36b5d5,
            'unknown_0x34e20697': self.unknown_0x34e20697,
            'grenade_data': self.grenade_data.to_json(),
            'space_pirate_struct_0x4fdab367': self.space_pirate_struct_0x4fdab367.to_json(),
            'space_pirate_struct_0x37212693': self.space_pirate_struct_0x37212693.to_json(),
            'space_pirate_struct_0x91b4cb73': self.space_pirate_struct_0x91b4cb73.to_json(),
            'has_shield': self.has_shield,
            'unknown_0x4aee5c47': self.unknown_0x4aee5c47,
            'shield_vulnerability': self.shield_vulnerability.to_json(),
            'hyper_shield_vulnerability': self.hyper_shield_vulnerability.to_json(),
            'unknown_0x0d1d1648': self.unknown_0x0d1d1648,
            'char': self.char.to_json(),
            'grapple_data': self.grapple_data.to_json(),
            'shield_busted_scan_info': self.shield_busted_scan_info,
            'has_armor': self.has_armor,
            'armor_health': self.armor_health.to_json(),
            'armor_vulnerability': self.armor_vulnerability.to_json(),
            'head_armor_vulnerability': self.head_armor_vulnerability.to_json(),
            'armor_broken_model': self.armor_broken_model,
            'armor_broken_skin_rules': self.armor_broken_skin_rules,
            'head_armor_model': self.head_armor_model,
            'collar_armor_model': self.collar_armor_model,
            'left_collar_armor_model': self.left_collar_armor_model,
            'right_collar_armor_model': self.right_collar_armor_model,
            'spine1_armor_model': self.spine1_armor_model,
            'spine2_armor_model': self.spine2_armor_model,
            'left_hip_armor_model': self.left_hip_armor_model,
            'right_hip_armor_model': self.right_hip_armor_model,
            'skeleton_root_armor_model': self.skeleton_root_armor_model,
            'is_gandrayda': self.is_gandrayda,
            'unknown_0x040a4edf': self.unknown_0x040a4edf,
            'unknown_0x5c572665': self.unknown_0x5c572665,
            'unknown_0xcca41d93': self.unknown_0xcca41d93,
            'unknown_0x767f168e': self.unknown_0x767f168e,
            'keep_target_time': self.keep_target_time,
            'unknown_0x668ec0a0': self.unknown_0x668ec0a0,
            'unknown_0x14950f43': self.unknown_0x14950f43,
            'unknown_0x761ed7af': self.unknown_0x761ed7af,
        }


def _decode_attack_behavior(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_can_interrupt_tasks(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_warp_in(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x87929c41(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x9a0ce9b2(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4d61342a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_initial_taunt_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_combat_taunt_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_instant_attack(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x97c95a99(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_aggressiveness(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cover_check(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_search_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hearing_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_approach_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x733da88a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x03fdbe4a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_dodge_check(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4ead288e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_no_backing_up(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_no_knockback_movement(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_no_melee_attack(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_blade_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 10.0, 'di_knock_back_power': 5.0})


def _decode_unknown_0x71587b45(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7903312e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1b454a27(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_gun_track_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x615bb850(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x7b1f1541(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_has_cloak(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_cloak_opacity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cloak_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_decloak_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cover_cloak_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_cloak_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_can_combat_teleport(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_min_teleport_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_teleport_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2eb81206(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x02e75b93(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0881a3b5(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x38b6452e(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xe3794994(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x54f66da0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x506c5c8a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x159f33d6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0524bc7e(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0x256b394f(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0x824db7ce(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe527cde8(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x61e801d4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf19b113e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x80c6880f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x08358a6a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa00204b0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0806c08d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x17db0cf2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_alert(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_hurled(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_death(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x8a36b5d5(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x34e20697(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_has_shield(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4aee5c47(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x0d1d1648(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grapple_data(data: typing.BinaryIO, property_size: int) -> GrappleData:
    return GrappleData.from_stream(data, property_size, default_override={'grapple_type': 1})


def _decode_shield_busted_scan_info(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_has_armor(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_armor_health(data: typing.BinaryIO, property_size: int) -> HealthInfo:
    return HealthInfo.from_stream(data, property_size, default_override={'health': 100.0, 'hi_knock_back_resistance': 5.0})


def _decode_armor_broken_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_armor_broken_skin_rules(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_head_armor_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_collar_armor_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_left_collar_armor_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_right_collar_armor_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_spine1_armor_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_spine2_armor_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_left_hip_armor_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_right_hip_armor_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_skeleton_root_armor_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_is_gandrayda(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x040a4edf(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x5c572665(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xcca41d93(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x767f168e(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_keep_target_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x668ec0a0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x14950f43(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x761ed7af(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x8e1e1586: ('attack_behavior', _decode_attack_behavior),
    0xa40cb847: ('can_interrupt_tasks', _decode_can_interrupt_tasks),
    0x7428a29f: ('warp_in', _decode_warp_in),
    0x87929c41: ('unknown_0x87929c41', _decode_unknown_0x87929c41),
    0x9a0ce9b2: ('unknown_0x9a0ce9b2', _decode_unknown_0x9a0ce9b2),
    0x4d61342a: ('unknown_0x4d61342a', _decode_unknown_0x4d61342a),
    0x2d8264ea: ('initial_taunt_chance', _decode_initial_taunt_chance),
    0xa6af0c57: ('combat_taunt_chance', _decode_combat_taunt_chance),
    0x6697712a: ('instant_attack', _decode_instant_attack),
    0x97c95a99: ('unknown_0x97c95a99', _decode_unknown_0x97c95a99),
    0x9579b1f2: ('aggressiveness', _decode_aggressiveness),
    0xf89ab419: ('cover_check', _decode_cover_check),
    0xed9bf5a3: ('search_radius', _decode_search_radius),
    0xed69488f: ('hearing_radius', _decode_hearing_radius),
    0x3cb99b1e: ('approach_radius', _decode_approach_radius),
    0x733da88a: ('unknown_0x733da88a', _decode_unknown_0x733da88a),
    0x3fdbe4a: ('unknown_0x03fdbe4a', _decode_unknown_0x03fdbe4a),
    0xdc36e745: ('dodge_check', _decode_dodge_check),
    0x4ead288e: ('unknown_0x4ead288e', _decode_unknown_0x4ead288e),
    0xf11ec8ee: ('no_backing_up', _decode_no_backing_up),
    0x808576ee: ('no_knockback_movement', _decode_no_knockback_movement),
    0x6bc22735: ('no_melee_attack', _decode_no_melee_attack),
    0xa5912430: ('blade_damage', _decode_blade_damage),
    0x71587b45: ('unknown_0x71587b45', _decode_unknown_0x71587b45),
    0x7903312e: ('unknown_0x7903312e', _decode_unknown_0x7903312e),
    0x1b454a27: ('unknown_0x1b454a27', _decode_unknown_0x1b454a27),
    0xb2ac2d96: ('gun_track_delay', _decode_gun_track_delay),
    0x615bb850: ('unknown_0x615bb850', _decode_unknown_0x615bb850),
    0x7b1f1541: ('unknown_0x7b1f1541', _decode_unknown_0x7b1f1541),
    0x7a4b4aea: ('has_cloak', _decode_has_cloak),
    0x5bc6f1d5: ('cloak_opacity', _decode_cloak_opacity),
    0x388bc31f: ('cloak_time', _decode_cloak_time),
    0x4319c840: ('decloak_time', _decode_decloak_time),
    0x8aa60b6c: ('cover_cloak_chance', _decode_cover_cloak_chance),
    0x57e862aa: ('melee_cloak_chance', _decode_melee_cloak_chance),
    0xfcd4ed64: ('can_combat_teleport', _decode_can_combat_teleport),
    0xfaa81d3a: ('min_teleport_dist', _decode_min_teleport_dist),
    0xa90369e6: ('min_teleport_time', _decode_min_teleport_time),
    0x2eb81206: ('unknown_0x2eb81206', _decode_unknown_0x2eb81206),
    0x2e75b93: ('unknown_0x02e75b93', _decode_unknown_0x02e75b93),
    0x881a3b5: ('unknown_0x0881a3b5', _decode_unknown_0x0881a3b5),
    0x38b6452e: ('unknown_0x38b6452e', _decode_unknown_0x38b6452e),
    0xe3794994: ('unknown_0xe3794994', _decode_unknown_0xe3794994),
    0x54f66da0: ('unknown_0x54f66da0', _decode_unknown_0x54f66da0),
    0x506c5c8a: ('unknown_0x506c5c8a', _decode_unknown_0x506c5c8a),
    0x159f33d6: ('unknown_0x159f33d6', _decode_unknown_0x159f33d6),
    0x524bc7e: ('unknown_0x0524bc7e', _decode_unknown_0x0524bc7e),
    0x256b394f: ('unknown_0x256b394f', _decode_unknown_0x256b394f),
    0x824db7ce: ('unknown_0x824db7ce', _decode_unknown_0x824db7ce),
    0xe527cde8: ('unknown_0xe527cde8', _decode_unknown_0xe527cde8),
    0x61e801d4: ('unknown_0x61e801d4', _decode_unknown_0x61e801d4),
    0xf19b113e: ('unknown_0xf19b113e', _decode_unknown_0xf19b113e),
    0x80c6880f: ('unknown_0x80c6880f', _decode_unknown_0x80c6880f),
    0x8358a6a: ('unknown_0x08358a6a', _decode_unknown_0x08358a6a),
    0xa00204b0: ('unknown_0xa00204b0', _decode_unknown_0xa00204b0),
    0x806c08d: ('unknown_0x0806c08d', _decode_unknown_0x0806c08d),
    0x17db0cf2: ('unknown_0x17db0cf2', _decode_unknown_0x17db0cf2),
    0xc245a874: ('sound_alert', _decode_sound_alert),
    0xc192e357: ('sound_hurled', _decode_sound_hurled),
    0x1b412c4b: ('sound_death', _decode_sound_death),
    0x8a36b5d5: ('unknown_0x8a36b5d5', _decode_unknown_0x8a36b5d5),
    0x34e20697: ('unknown_0x34e20697', _decode_unknown_0x34e20697),
    0xc3b6103b: ('grenade_data', SpacePirateWeaponData.from_stream),
    0x4fdab367: ('space_pirate_struct_0x4fdab367', SpacePirateStruct.from_stream),
    0x37212693: ('space_pirate_struct_0x37212693', SpacePirateStruct.from_stream),
    0x91b4cb73: ('space_pirate_struct_0x91b4cb73', SpacePirateStruct.from_stream),
    0x7c1de29: ('has_shield', _decode_has_shield),
    0x4aee5c47: ('unknown_0x4aee5c47', _decode_unknown_0x4aee5c47),
    0xd34f1323: ('shield_vulnerability', DamageVulnerability.from_stream),
    0x8255f594: ('hyper_shield_vulnerability', DamageVulnerability.from_stream),
    0xd1d1648: ('unknown_0x0d1d1648', _decode_unknown_0x0d1d1648),
    0xc699ad35: ('char', AnimationParameters.from_stream),
    0xbe1afbc0: ('grapple_data', _decode_grapple_data),
    0x71e83f06: ('shield_busted_scan_info', _decode_shield_busted_scan_info),
    0xfde9c4df: ('has_armor', _decode_has_armor),
    0xf18384d4: ('armor_health', _decode_armor_health),
    0x896d5bd9: ('armor_vulnerability', DamageVulnerability.from_stream),
    0xc13a3e1f: ('head_armor_vulnerability', DamageVulnerability.from_stream),
    0x7579cc86: ('armor_broken_model', _decode_armor_broken_model),
    0x65d86552: ('armor_broken_skin_rules', _decode_armor_broken_skin_rules),
    0x68002bd7: ('head_armor_model', _decode_head_armor_model),
    0xad315c7c: ('collar_armor_model', _decode_collar_armor_model),
    0x42a25ed: ('left_collar_armor_model', _decode_left_collar_armor_model),
    0xe39b8b1e: ('right_collar_armor_model', _decode_right_collar_armor_model),
    0x356c166a: ('spine1_armor_model', _decode_spine1_armor_model),
    0x1ca4a298: ('spine2_armor_model', _decode_spine2_armor_model),
    0xdf44507e: ('left_hip_armor_model', _decode_left_hip_armor_model),
    0xd2c9a656: ('right_hip_armor_model', _decode_right_hip_armor_model),
    0xd4e26a8e: ('skeleton_root_armor_model', _decode_skeleton_root_armor_model),
    0x531a8c85: ('is_gandrayda', _decode_is_gandrayda),
    0x40a4edf: ('unknown_0x040a4edf', _decode_unknown_0x040a4edf),
    0x5c572665: ('unknown_0x5c572665', _decode_unknown_0x5c572665),
    0xcca41d93: ('unknown_0xcca41d93', _decode_unknown_0xcca41d93),
    0x767f168e: ('unknown_0x767f168e', _decode_unknown_0x767f168e),
    0x89a5edc8: ('keep_target_time', _decode_keep_target_time),
    0x668ec0a0: ('unknown_0x668ec0a0', _decode_unknown_0x668ec0a0),
    0x14950f43: ('unknown_0x14950f43', _decode_unknown_0x14950f43),
    0x761ed7af: ('unknown_0x761ed7af', _decode_unknown_0x761ed7af),
}
