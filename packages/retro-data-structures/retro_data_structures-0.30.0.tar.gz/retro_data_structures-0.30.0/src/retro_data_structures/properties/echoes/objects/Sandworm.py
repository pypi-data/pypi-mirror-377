# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.echoes.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.IngPossessionData import IngPossessionData
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.archetypes.SandwormStruct import SandwormStruct
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SandwormJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        unknown_0x06dee4c5: int
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        pincer_scale: float
        walk_sound: int
        walk_vocal_sound: int
        melee_attack_sound: int
        eye_killed_sound: int
        pincer_l: int
        pincer_r: int
        unknown_0x63dcbbb6: float
        unknown_0x2393c3c0: float
        spit_attack_visor_effect: int
        unknown_0x61f75902: float
        charge_range_min: float
        charge_range_max: float
        projectile: int
        projectile_damage: json_util.JsonObject
        charge_impulse_horizontal: float
        charge_impulse_vertical: float
        unknown_0x2b053901: float
        unknown_0x47e969d3: float
        melee_impulse_horizontal: float
        melee_impulse_vertical: float
        morphball_toss_damage: json_util.JsonObject
        pincer_swipe_damage: json_util.JsonObject
        unknown_0xe593f1c6: float
        unknown_0x3c5d53a4: float
        unknown_0xda3dfc45: float
        pursuit_frustration_timer: float
        pursuit_frustration_radius: float
        can_link_transfer: bool
        eye_glow: int
        part_0x3221407e: int
        part_0x8b2a15ee: int
        part_0x526c6956: int
        part_0xd24a1751: int
        ing_boss_bomb_damage: json_util.JsonObject
        unknown_0x3d58f51f: float
        bomb_bounce_sound: int
        bomb_explode_sound: int
        unknown_0x547f9400: float
        unknown_0xefef7b45: float
        sandworm_struct_0xb8c15f15: json_util.JsonObject
        sandworm_struct_0xce246628: json_util.JsonObject
        sandworm_struct_0x55578cfc: json_util.JsonObject
        sandworm_struct_0x23ee1452: json_util.JsonObject
        sandworm_struct_0xb89dfe86: json_util.JsonObject
        ing_possession_data: json_util.JsonObject
    

@dataclasses.dataclass()
class Sandworm(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    unknown_0x06dee4c5: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x06dee4c5, original_name='Unknown'
        ),
    })
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    pincer_scale: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3db583ae, original_name='PincerScale'
        ),
    })
    walk_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xa24376ec, original_name='WalkSound'
        ),
    })
    walk_vocal_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xd35eb69d, original_name='WalkVocalSound'
        ),
    })
    melee_attack_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xaadaabb8, original_name='MeleeAttackSound'
        ),
    })
    eye_killed_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x8128ce4a, original_name='EyeKilledSound'
        ),
    })
    pincer_l: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x66e34a08, original_name='PincerL'
        ),
    })
    pincer_r: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5f3f29e3, original_name='PincerR'
        ),
    })
    unknown_0x63dcbbb6: float = dataclasses.field(default=9.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x63dcbbb6, original_name='Unknown'
        ),
    })
    unknown_0x2393c3c0: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2393c3c0, original_name='Unknown'
        ),
    })
    spit_attack_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf9469e49, original_name='SpitAttackVisorEffect'
        ),
    })
    unknown_0x61f75902: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x61f75902, original_name='Unknown'
        ),
    })
    charge_range_min: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2a7446ee, original_name='ChargeRangeMin'
        ),
    })
    charge_range_max: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcc14e90f, original_name='ChargeRangeMax'
        ),
    })
    projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xef485db9, original_name='Projectile'
        ),
    })
    projectile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x553b1339, original_name='ProjectileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    charge_impulse_horizontal: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x12090da8, original_name='ChargeImpulseHorizontal'
        ),
    })
    charge_impulse_vertical: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc07bbe9a, original_name='ChargeImpulseVertical'
        ),
    })
    unknown_0x2b053901: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2b053901, original_name='Unknown'
        ),
    })
    unknown_0x47e969d3: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x47e969d3, original_name='Unknown'
        ),
    })
    melee_impulse_horizontal: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb8eecc95, original_name='MeleeImpulseHorizontal'
        ),
    })
    melee_impulse_vertical: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf59af01a, original_name='MeleeImpulseVertical'
        ),
    })
    morphball_toss_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xf8fd6885, original_name='MorphballTossDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    pincer_swipe_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x449233bc, original_name='PincerSwipeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xe593f1c6: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe593f1c6, original_name='Unknown'
        ),
    })
    unknown_0x3c5d53a4: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3c5d53a4, original_name='Unknown'
        ),
    })
    unknown_0xda3dfc45: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xda3dfc45, original_name='Unknown'
        ),
    })
    pursuit_frustration_timer: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdfa46e80, original_name='PursuitFrustrationTimer'
        ),
    })
    pursuit_frustration_radius: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x49f36a3f, original_name='PursuitFrustrationRadius'
        ),
    })
    can_link_transfer: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb47dd18f, original_name='CanLinkTransfer'
        ),
    })
    eye_glow: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0ca82d3c, original_name='EyeGlow'
        ),
    })
    part_0x3221407e: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3221407e, original_name='PART'
        ),
    })
    part_0x8b2a15ee: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8b2a15ee, original_name='PART'
        ),
    })
    part_0x526c6956: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x526c6956, original_name='PART'
        ),
    })
    part_0xd24a1751: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd24a1751, original_name='PART'
        ),
    })
    ing_boss_bomb_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x4461a8ad, original_name='IngBossBombDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x3d58f51f: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3d58f51f, original_name='Unknown'
        ),
    })
    bomb_bounce_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x8c41066c, original_name='BombBounceSound'
        ),
    })
    bomb_explode_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x8649fe53, original_name='BombExplodeSound'
        ),
    })
    unknown_0x547f9400: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x547f9400, original_name='Unknown'
        ),
    })
    unknown_0xefef7b45: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xefef7b45, original_name='Unknown'
        ),
    })
    sandworm_struct_0xb8c15f15: SandwormStruct = dataclasses.field(default_factory=SandwormStruct, metadata={
        'reflection': FieldReflection[SandwormStruct](
            SandwormStruct, id=0xb8c15f15, original_name='SandwormStruct', from_json=SandwormStruct.from_json, to_json=SandwormStruct.to_json
        ),
    })
    sandworm_struct_0xce246628: SandwormStruct = dataclasses.field(default_factory=SandwormStruct, metadata={
        'reflection': FieldReflection[SandwormStruct](
            SandwormStruct, id=0xce246628, original_name='SandwormStruct', from_json=SandwormStruct.from_json, to_json=SandwormStruct.to_json
        ),
    })
    sandworm_struct_0x55578cfc: SandwormStruct = dataclasses.field(default_factory=SandwormStruct, metadata={
        'reflection': FieldReflection[SandwormStruct](
            SandwormStruct, id=0x55578cfc, original_name='SandwormStruct', from_json=SandwormStruct.from_json, to_json=SandwormStruct.to_json
        ),
    })
    sandworm_struct_0x23ee1452: SandwormStruct = dataclasses.field(default_factory=SandwormStruct, metadata={
        'reflection': FieldReflection[SandwormStruct](
            SandwormStruct, id=0x23ee1452, original_name='SandwormStruct', from_json=SandwormStruct.from_json, to_json=SandwormStruct.to_json
        ),
    })
    sandworm_struct_0xb89dfe86: SandwormStruct = dataclasses.field(default_factory=SandwormStruct, metadata={
        'reflection': FieldReflection[SandwormStruct](
            SandwormStruct, id=0xb89dfe86, original_name='SandwormStruct', from_json=SandwormStruct.from_json, to_json=SandwormStruct.to_json
        ),
    })
    ing_possession_data: IngPossessionData = dataclasses.field(default_factory=IngPossessionData, metadata={
        'reflection': FieldReflection[IngPossessionData](
            IngPossessionData, id=0xe61748ed, original_name='IngPossessionData', from_json=IngPossessionData.from_json, to_json=IngPossessionData.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'WORM'

    @classmethod
    def modules(cls) -> list[str]:
        return ['Sandworm.rel']

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        struct_id, size, property_count = struct.unpack(">LHH", data.read(8))
        assert struct_id == 0xFFFFFFFF
        root_size_start = data.tell() - 2

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

        assert data.tell() - root_size_start == size
        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 50:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x06dee4c5
        unknown_0x06dee4c5 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'detection_range': 32.0, 'collision_radius': 0.5, 'collision_height': 1.0, 'creature_size': 2})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3db583ae
        pincer_scale = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa24376ec
        walk_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd35eb69d
        walk_vocal_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaadaabb8
        melee_attack_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8128ce4a
        eye_killed_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66e34a08
        pincer_l = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5f3f29e3
        pincer_r = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x63dcbbb6
        unknown_0x63dcbbb6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2393c3c0
        unknown_0x2393c3c0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf9469e49
        spit_attack_visor_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x61f75902
        unknown_0x61f75902 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2a7446ee
        charge_range_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcc14e90f
        charge_range_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef485db9
        projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x553b1339
        projectile_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12090da8
        charge_impulse_horizontal = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc07bbe9a
        charge_impulse_vertical = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b053901
        unknown_0x2b053901 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47e969d3
        unknown_0x47e969d3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb8eecc95
        melee_impulse_horizontal = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf59af01a
        melee_impulse_vertical = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf8fd6885
        morphball_toss_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x449233bc
        pincer_swipe_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe593f1c6
        unknown_0xe593f1c6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c5d53a4
        unknown_0x3c5d53a4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xda3dfc45
        unknown_0xda3dfc45 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdfa46e80
        pursuit_frustration_timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49f36a3f
        pursuit_frustration_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb47dd18f
        can_link_transfer = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0ca82d3c
        eye_glow = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3221407e
        part_0x3221407e = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b2a15ee
        part_0x8b2a15ee = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x526c6956
        part_0x526c6956 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd24a1751
        part_0xd24a1751 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4461a8ad
        ing_boss_bomb_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d58f51f
        unknown_0x3d58f51f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8c41066c
        bomb_bounce_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8649fe53
        bomb_explode_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x547f9400
        unknown_0x547f9400 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xefef7b45
        unknown_0xefef7b45 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb8c15f15
        sandworm_struct_0xb8c15f15 = SandwormStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce246628
        sandworm_struct_0xce246628 = SandwormStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x55578cfc
        sandworm_struct_0x55578cfc = SandwormStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x23ee1452
        sandworm_struct_0x23ee1452 = SandwormStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb89dfe86
        sandworm_struct_0xb89dfe86 = SandwormStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe61748ed
        ing_possession_data = IngPossessionData.from_stream(data, property_size)
    
        return cls(editor_properties, unknown_0x06dee4c5, patterned, actor_information, pincer_scale, walk_sound, walk_vocal_sound, melee_attack_sound, eye_killed_sound, pincer_l, pincer_r, unknown_0x63dcbbb6, unknown_0x2393c3c0, spit_attack_visor_effect, unknown_0x61f75902, charge_range_min, charge_range_max, projectile, projectile_damage, charge_impulse_horizontal, charge_impulse_vertical, unknown_0x2b053901, unknown_0x47e969d3, melee_impulse_horizontal, melee_impulse_vertical, morphball_toss_damage, pincer_swipe_damage, unknown_0xe593f1c6, unknown_0x3c5d53a4, unknown_0xda3dfc45, pursuit_frustration_timer, pursuit_frustration_radius, can_link_transfer, eye_glow, part_0x3221407e, part_0x8b2a15ee, part_0x526c6956, part_0xd24a1751, ing_boss_bomb_damage, unknown_0x3d58f51f, bomb_bounce_sound, bomb_explode_sound, unknown_0x547f9400, unknown_0xefef7b45, sandworm_struct_0xb8c15f15, sandworm_struct_0xce246628, sandworm_struct_0x55578cfc, sandworm_struct_0x23ee1452, sandworm_struct_0xb89dfe86, ing_possession_data)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x002')  # 50 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x06\xde\xe4\xc5')  # 0x6dee4c5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x06dee4c5))

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data, default_override={'detection_range': 32.0, 'collision_radius': 0.5, 'collision_height': 1.0, 'creature_size': 2})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'~9\x7f\xed')  # 0x7e397fed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.actor_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'=\xb5\x83\xae')  # 0x3db583ae
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pincer_scale))

        data.write(b'\xa2Cv\xec')  # 0xa24376ec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.walk_sound))

        data.write(b'\xd3^\xb6\x9d')  # 0xd35eb69d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.walk_vocal_sound))

        data.write(b'\xaa\xda\xab\xb8')  # 0xaadaabb8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.melee_attack_sound))

        data.write(b'\x81(\xceJ')  # 0x8128ce4a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.eye_killed_sound))

        data.write(b'f\xe3J\x08')  # 0x66e34a08
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.pincer_l))

        data.write(b'_?)\xe3')  # 0x5f3f29e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.pincer_r))

        data.write(b'c\xdc\xbb\xb6')  # 0x63dcbbb6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x63dcbbb6))

        data.write(b'#\x93\xc3\xc0')  # 0x2393c3c0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2393c3c0))

        data.write(b'\xf9F\x9eI')  # 0xf9469e49
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.spit_attack_visor_effect))

        data.write(b'a\xf7Y\x02')  # 0x61f75902
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x61f75902))

        data.write(b'*tF\xee')  # 0x2a7446ee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.charge_range_min))

        data.write(b'\xcc\x14\xe9\x0f')  # 0xcc14e90f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.charge_range_max))

        data.write(b'\xefH]\xb9')  # 0xef485db9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.projectile))

        data.write(b'U;\x139')  # 0x553b1339
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.projectile_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x12\t\r\xa8')  # 0x12090da8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.charge_impulse_horizontal))

        data.write(b'\xc0{\xbe\x9a')  # 0xc07bbe9a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.charge_impulse_vertical))

        data.write(b'+\x059\x01')  # 0x2b053901
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2b053901))

        data.write(b'G\xe9i\xd3')  # 0x47e969d3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x47e969d3))

        data.write(b'\xb8\xee\xcc\x95')  # 0xb8eecc95
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_impulse_horizontal))

        data.write(b'\xf5\x9a\xf0\x1a')  # 0xf59af01a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_impulse_vertical))

        data.write(b'\xf8\xfdh\x85')  # 0xf8fd6885
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.morphball_toss_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'D\x923\xbc')  # 0x449233bc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.pincer_swipe_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe5\x93\xf1\xc6')  # 0xe593f1c6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe593f1c6))

        data.write(b'<]S\xa4')  # 0x3c5d53a4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3c5d53a4))

        data.write(b'\xda=\xfcE')  # 0xda3dfc45
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xda3dfc45))

        data.write(b'\xdf\xa4n\x80')  # 0xdfa46e80
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pursuit_frustration_timer))

        data.write(b'I\xf3j?')  # 0x49f36a3f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pursuit_frustration_radius))

        data.write(b'\xb4}\xd1\x8f')  # 0xb47dd18f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.can_link_transfer))

        data.write(b'\x0c\xa8-<')  # 0xca82d3c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.eye_glow))

        data.write(b'2!@~')  # 0x3221407e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x3221407e))

        data.write(b'\x8b*\x15\xee')  # 0x8b2a15ee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x8b2a15ee))

        data.write(b'RliV')  # 0x526c6956
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x526c6956))

        data.write(b'\xd2J\x17Q')  # 0xd24a1751
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0xd24a1751))

        data.write(b'Da\xa8\xad')  # 0x4461a8ad
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_boss_bomb_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'=X\xf5\x1f')  # 0x3d58f51f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3d58f51f))

        data.write(b'\x8cA\x06l')  # 0x8c41066c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.bomb_bounce_sound))

        data.write(b'\x86I\xfeS')  # 0x8649fe53
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.bomb_explode_sound))

        data.write(b'T\x7f\x94\x00')  # 0x547f9400
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x547f9400))

        data.write(b'\xef\xef{E')  # 0xefef7b45
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xefef7b45))

        data.write(b'\xb8\xc1_\x15')  # 0xb8c15f15
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sandworm_struct_0xb8c15f15.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xce$f(')  # 0xce246628
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sandworm_struct_0xce246628.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'UW\x8c\xfc')  # 0x55578cfc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sandworm_struct_0x55578cfc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'#\xee\x14R')  # 0x23ee1452
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sandworm_struct_0x23ee1452.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb8\x9d\xfe\x86')  # 0xb89dfe86
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sandworm_struct_0xb89dfe86.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe6\x17H\xed')  # 0xe61748ed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_possession_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SandwormJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            unknown_0x06dee4c5=json_data['unknown_0x06dee4c5'],
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            pincer_scale=json_data['pincer_scale'],
            walk_sound=json_data['walk_sound'],
            walk_vocal_sound=json_data['walk_vocal_sound'],
            melee_attack_sound=json_data['melee_attack_sound'],
            eye_killed_sound=json_data['eye_killed_sound'],
            pincer_l=json_data['pincer_l'],
            pincer_r=json_data['pincer_r'],
            unknown_0x63dcbbb6=json_data['unknown_0x63dcbbb6'],
            unknown_0x2393c3c0=json_data['unknown_0x2393c3c0'],
            spit_attack_visor_effect=json_data['spit_attack_visor_effect'],
            unknown_0x61f75902=json_data['unknown_0x61f75902'],
            charge_range_min=json_data['charge_range_min'],
            charge_range_max=json_data['charge_range_max'],
            projectile=json_data['projectile'],
            projectile_damage=DamageInfo.from_json(json_data['projectile_damage']),
            charge_impulse_horizontal=json_data['charge_impulse_horizontal'],
            charge_impulse_vertical=json_data['charge_impulse_vertical'],
            unknown_0x2b053901=json_data['unknown_0x2b053901'],
            unknown_0x47e969d3=json_data['unknown_0x47e969d3'],
            melee_impulse_horizontal=json_data['melee_impulse_horizontal'],
            melee_impulse_vertical=json_data['melee_impulse_vertical'],
            morphball_toss_damage=DamageInfo.from_json(json_data['morphball_toss_damage']),
            pincer_swipe_damage=DamageInfo.from_json(json_data['pincer_swipe_damage']),
            unknown_0xe593f1c6=json_data['unknown_0xe593f1c6'],
            unknown_0x3c5d53a4=json_data['unknown_0x3c5d53a4'],
            unknown_0xda3dfc45=json_data['unknown_0xda3dfc45'],
            pursuit_frustration_timer=json_data['pursuit_frustration_timer'],
            pursuit_frustration_radius=json_data['pursuit_frustration_radius'],
            can_link_transfer=json_data['can_link_transfer'],
            eye_glow=json_data['eye_glow'],
            part_0x3221407e=json_data['part_0x3221407e'],
            part_0x8b2a15ee=json_data['part_0x8b2a15ee'],
            part_0x526c6956=json_data['part_0x526c6956'],
            part_0xd24a1751=json_data['part_0xd24a1751'],
            ing_boss_bomb_damage=DamageInfo.from_json(json_data['ing_boss_bomb_damage']),
            unknown_0x3d58f51f=json_data['unknown_0x3d58f51f'],
            bomb_bounce_sound=json_data['bomb_bounce_sound'],
            bomb_explode_sound=json_data['bomb_explode_sound'],
            unknown_0x547f9400=json_data['unknown_0x547f9400'],
            unknown_0xefef7b45=json_data['unknown_0xefef7b45'],
            sandworm_struct_0xb8c15f15=SandwormStruct.from_json(json_data['sandworm_struct_0xb8c15f15']),
            sandworm_struct_0xce246628=SandwormStruct.from_json(json_data['sandworm_struct_0xce246628']),
            sandworm_struct_0x55578cfc=SandwormStruct.from_json(json_data['sandworm_struct_0x55578cfc']),
            sandworm_struct_0x23ee1452=SandwormStruct.from_json(json_data['sandworm_struct_0x23ee1452']),
            sandworm_struct_0xb89dfe86=SandwormStruct.from_json(json_data['sandworm_struct_0xb89dfe86']),
            ing_possession_data=IngPossessionData.from_json(json_data['ing_possession_data']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'unknown_0x06dee4c5': self.unknown_0x06dee4c5,
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'pincer_scale': self.pincer_scale,
            'walk_sound': self.walk_sound,
            'walk_vocal_sound': self.walk_vocal_sound,
            'melee_attack_sound': self.melee_attack_sound,
            'eye_killed_sound': self.eye_killed_sound,
            'pincer_l': self.pincer_l,
            'pincer_r': self.pincer_r,
            'unknown_0x63dcbbb6': self.unknown_0x63dcbbb6,
            'unknown_0x2393c3c0': self.unknown_0x2393c3c0,
            'spit_attack_visor_effect': self.spit_attack_visor_effect,
            'unknown_0x61f75902': self.unknown_0x61f75902,
            'charge_range_min': self.charge_range_min,
            'charge_range_max': self.charge_range_max,
            'projectile': self.projectile,
            'projectile_damage': self.projectile_damage.to_json(),
            'charge_impulse_horizontal': self.charge_impulse_horizontal,
            'charge_impulse_vertical': self.charge_impulse_vertical,
            'unknown_0x2b053901': self.unknown_0x2b053901,
            'unknown_0x47e969d3': self.unknown_0x47e969d3,
            'melee_impulse_horizontal': self.melee_impulse_horizontal,
            'melee_impulse_vertical': self.melee_impulse_vertical,
            'morphball_toss_damage': self.morphball_toss_damage.to_json(),
            'pincer_swipe_damage': self.pincer_swipe_damage.to_json(),
            'unknown_0xe593f1c6': self.unknown_0xe593f1c6,
            'unknown_0x3c5d53a4': self.unknown_0x3c5d53a4,
            'unknown_0xda3dfc45': self.unknown_0xda3dfc45,
            'pursuit_frustration_timer': self.pursuit_frustration_timer,
            'pursuit_frustration_radius': self.pursuit_frustration_radius,
            'can_link_transfer': self.can_link_transfer,
            'eye_glow': self.eye_glow,
            'part_0x3221407e': self.part_0x3221407e,
            'part_0x8b2a15ee': self.part_0x8b2a15ee,
            'part_0x526c6956': self.part_0x526c6956,
            'part_0xd24a1751': self.part_0xd24a1751,
            'ing_boss_bomb_damage': self.ing_boss_bomb_damage.to_json(),
            'unknown_0x3d58f51f': self.unknown_0x3d58f51f,
            'bomb_bounce_sound': self.bomb_bounce_sound,
            'bomb_explode_sound': self.bomb_explode_sound,
            'unknown_0x547f9400': self.unknown_0x547f9400,
            'unknown_0xefef7b45': self.unknown_0xefef7b45,
            'sandworm_struct_0xb8c15f15': self.sandworm_struct_0xb8c15f15.to_json(),
            'sandworm_struct_0xce246628': self.sandworm_struct_0xce246628.to_json(),
            'sandworm_struct_0x55578cfc': self.sandworm_struct_0x55578cfc.to_json(),
            'sandworm_struct_0x23ee1452': self.sandworm_struct_0x23ee1452.to_json(),
            'sandworm_struct_0xb89dfe86': self.sandworm_struct_0xb89dfe86.to_json(),
            'ing_possession_data': self.ing_possession_data.to_json(),
        }

    def _dependencies_for_walk_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.walk_sound)

    def _dependencies_for_walk_vocal_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.walk_vocal_sound)

    def _dependencies_for_melee_attack_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.melee_attack_sound)

    def _dependencies_for_eye_killed_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.eye_killed_sound)

    def _dependencies_for_pincer_l(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.pincer_l)

    def _dependencies_for_pincer_r(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.pincer_r)

    def _dependencies_for_spit_attack_visor_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.spit_attack_visor_effect)

    def _dependencies_for_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.projectile)

    def _dependencies_for_eye_glow(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.eye_glow)

    def _dependencies_for_part_0x3221407e(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x3221407e)

    def _dependencies_for_part_0x8b2a15ee(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x8b2a15ee)

    def _dependencies_for_part_0x526c6956(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x526c6956)

    def _dependencies_for_part_0xd24a1751(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0xd24a1751)

    def _dependencies_for_bomb_bounce_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.bomb_bounce_sound)

    def _dependencies_for_bomb_explode_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.bomb_explode_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self._dependencies_for_walk_sound, "walk_sound", "int"),
            (self._dependencies_for_walk_vocal_sound, "walk_vocal_sound", "int"),
            (self._dependencies_for_melee_attack_sound, "melee_attack_sound", "int"),
            (self._dependencies_for_eye_killed_sound, "eye_killed_sound", "int"),
            (self._dependencies_for_pincer_l, "pincer_l", "AssetId"),
            (self._dependencies_for_pincer_r, "pincer_r", "AssetId"),
            (self._dependencies_for_spit_attack_visor_effect, "spit_attack_visor_effect", "AssetId"),
            (self._dependencies_for_projectile, "projectile", "AssetId"),
            (self.projectile_damage.dependencies_for, "projectile_damage", "DamageInfo"),
            (self.morphball_toss_damage.dependencies_for, "morphball_toss_damage", "DamageInfo"),
            (self.pincer_swipe_damage.dependencies_for, "pincer_swipe_damage", "DamageInfo"),
            (self._dependencies_for_eye_glow, "eye_glow", "AssetId"),
            (self._dependencies_for_part_0x3221407e, "part_0x3221407e", "AssetId"),
            (self._dependencies_for_part_0x8b2a15ee, "part_0x8b2a15ee", "AssetId"),
            (self._dependencies_for_part_0x526c6956, "part_0x526c6956", "AssetId"),
            (self._dependencies_for_part_0xd24a1751, "part_0xd24a1751", "AssetId"),
            (self.ing_boss_bomb_damage.dependencies_for, "ing_boss_bomb_damage", "DamageInfo"),
            (self._dependencies_for_bomb_bounce_sound, "bomb_bounce_sound", "int"),
            (self._dependencies_for_bomb_explode_sound, "bomb_explode_sound", "int"),
            (self.sandworm_struct_0xb8c15f15.dependencies_for, "sandworm_struct_0xb8c15f15", "SandwormStruct"),
            (self.sandworm_struct_0xce246628.dependencies_for, "sandworm_struct_0xce246628", "SandwormStruct"),
            (self.sandworm_struct_0x55578cfc.dependencies_for, "sandworm_struct_0x55578cfc", "SandwormStruct"),
            (self.sandworm_struct_0x23ee1452.dependencies_for, "sandworm_struct_0x23ee1452", "SandwormStruct"),
            (self.sandworm_struct_0xb89dfe86.dependencies_for, "sandworm_struct_0xb89dfe86", "SandwormStruct"),
            (self.ing_possession_data.dependencies_for, "ing_possession_data", "IngPossessionData"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Sandworm.{field_name} ({field_type}): {e}"
                )


def _decode_unknown_0x06dee4c5(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'detection_range': 32.0, 'collision_radius': 0.5, 'collision_height': 1.0, 'creature_size': 2})


def _decode_pincer_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_walk_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_walk_vocal_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_melee_attack_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_eye_killed_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_pincer_l(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_pincer_r(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x63dcbbb6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2393c3c0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_spit_attack_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x61f75902(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_charge_range_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_charge_range_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_projectile_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_charge_impulse_horizontal(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_charge_impulse_vertical(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2b053901(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x47e969d3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_impulse_horizontal(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_impulse_vertical(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_morphball_toss_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_pincer_swipe_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_unknown_0xe593f1c6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3c5d53a4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xda3dfc45(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pursuit_frustration_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pursuit_frustration_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_can_link_transfer(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_eye_glow(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0x3221407e(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0x8b2a15ee(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0x526c6956(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0xd24a1751(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_ing_boss_bomb_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_unknown_0x3d58f51f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bomb_bounce_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_bomb_explode_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x547f9400(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xefef7b45(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x6dee4c5: ('unknown_0x06dee4c5', _decode_unknown_0x06dee4c5),
    0xb3774750: ('patterned', _decode_patterned),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x3db583ae: ('pincer_scale', _decode_pincer_scale),
    0xa24376ec: ('walk_sound', _decode_walk_sound),
    0xd35eb69d: ('walk_vocal_sound', _decode_walk_vocal_sound),
    0xaadaabb8: ('melee_attack_sound', _decode_melee_attack_sound),
    0x8128ce4a: ('eye_killed_sound', _decode_eye_killed_sound),
    0x66e34a08: ('pincer_l', _decode_pincer_l),
    0x5f3f29e3: ('pincer_r', _decode_pincer_r),
    0x63dcbbb6: ('unknown_0x63dcbbb6', _decode_unknown_0x63dcbbb6),
    0x2393c3c0: ('unknown_0x2393c3c0', _decode_unknown_0x2393c3c0),
    0xf9469e49: ('spit_attack_visor_effect', _decode_spit_attack_visor_effect),
    0x61f75902: ('unknown_0x61f75902', _decode_unknown_0x61f75902),
    0x2a7446ee: ('charge_range_min', _decode_charge_range_min),
    0xcc14e90f: ('charge_range_max', _decode_charge_range_max),
    0xef485db9: ('projectile', _decode_projectile),
    0x553b1339: ('projectile_damage', _decode_projectile_damage),
    0x12090da8: ('charge_impulse_horizontal', _decode_charge_impulse_horizontal),
    0xc07bbe9a: ('charge_impulse_vertical', _decode_charge_impulse_vertical),
    0x2b053901: ('unknown_0x2b053901', _decode_unknown_0x2b053901),
    0x47e969d3: ('unknown_0x47e969d3', _decode_unknown_0x47e969d3),
    0xb8eecc95: ('melee_impulse_horizontal', _decode_melee_impulse_horizontal),
    0xf59af01a: ('melee_impulse_vertical', _decode_melee_impulse_vertical),
    0xf8fd6885: ('morphball_toss_damage', _decode_morphball_toss_damage),
    0x449233bc: ('pincer_swipe_damage', _decode_pincer_swipe_damage),
    0xe593f1c6: ('unknown_0xe593f1c6', _decode_unknown_0xe593f1c6),
    0x3c5d53a4: ('unknown_0x3c5d53a4', _decode_unknown_0x3c5d53a4),
    0xda3dfc45: ('unknown_0xda3dfc45', _decode_unknown_0xda3dfc45),
    0xdfa46e80: ('pursuit_frustration_timer', _decode_pursuit_frustration_timer),
    0x49f36a3f: ('pursuit_frustration_radius', _decode_pursuit_frustration_radius),
    0xb47dd18f: ('can_link_transfer', _decode_can_link_transfer),
    0xca82d3c: ('eye_glow', _decode_eye_glow),
    0x3221407e: ('part_0x3221407e', _decode_part_0x3221407e),
    0x8b2a15ee: ('part_0x8b2a15ee', _decode_part_0x8b2a15ee),
    0x526c6956: ('part_0x526c6956', _decode_part_0x526c6956),
    0xd24a1751: ('part_0xd24a1751', _decode_part_0xd24a1751),
    0x4461a8ad: ('ing_boss_bomb_damage', _decode_ing_boss_bomb_damage),
    0x3d58f51f: ('unknown_0x3d58f51f', _decode_unknown_0x3d58f51f),
    0x8c41066c: ('bomb_bounce_sound', _decode_bomb_bounce_sound),
    0x8649fe53: ('bomb_explode_sound', _decode_bomb_explode_sound),
    0x547f9400: ('unknown_0x547f9400', _decode_unknown_0x547f9400),
    0xefef7b45: ('unknown_0xefef7b45', _decode_unknown_0xefef7b45),
    0xb8c15f15: ('sandworm_struct_0xb8c15f15', SandwormStruct.from_stream),
    0xce246628: ('sandworm_struct_0xce246628', SandwormStruct.from_stream),
    0x55578cfc: ('sandworm_struct_0x55578cfc', SandwormStruct.from_stream),
    0x23ee1452: ('sandworm_struct_0x23ee1452', SandwormStruct.from_stream),
    0xb89dfe86: ('sandworm_struct_0xb89dfe86', SandwormStruct.from_stream),
    0xe61748ed: ('ing_possession_data', IngPossessionData.from_stream),
}
