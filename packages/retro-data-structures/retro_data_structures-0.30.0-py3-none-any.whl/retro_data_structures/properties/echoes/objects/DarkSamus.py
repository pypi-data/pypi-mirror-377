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
from retro_data_structures.properties.echoes.archetypes.AudioPlaybackParms import AudioPlaybackParms
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DarkSamusJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        unknown_0x72edeb7d: float
        unknown_0x74fa22f0: float
        glide_sound: int
        missile_ricochet_sound: int
        unknown_0x6689925b: bool
        txtr_0x3863160b: int
        unknown_0x2c6a3344: float
        melee_attack_damage: json_util.JsonObject
        part_0x6d40aa56: int
        part_0x9603a544: int
        dive_attack_damage: json_util.JsonObject
        unknown_0x4aa5dd62: float
        unknown_0x1ad7dc21: float
        dive_attack_effect: int
        scatter_shot_projectile: int
        scatter_shot_projectile2: int
        scatter_shot_damage: json_util.JsonObject
        unknown_0x378285b9: float
        unknown_0xd242e25f: float
        normal_missile_projectile: int
        normal_missile_damage: json_util.JsonObject
        unknown_0x1f1ef7a9: int
        unknown_0xc4a1a44e: int
        super_missile_projectile: int
        super_missile_damage: json_util.JsonObject
        freeze_beam_projectile: int
        freeze_beam_damage: json_util.JsonObject
        txtr_0x7ffeb33d: int
        damage_interrupt_threshold: float
        unknown_0xf317f4d5: float
        sweep_swoosh: int
        sweep_beam_damage: json_util.JsonObject
        crsc: int
        sweep_beam_sound: int
        unknown_0x0ef8dc15: int
        invulnerable_model: int
        invulnerable_skin_rules: int
        boost_ball_model: json_util.JsonObject
        boost_ball_damage: json_util.JsonObject
        boost_ball_glow: int
        swhc_0x449aa4aa: int
        swhc_0x0345fa17: int
        sound_0x2c72576b: int
        boost_ball_hit_player_sound: int
        boost_ball_collision: int
        audio_playback_parms: json_util.JsonObject
        part_0xa6c42023: int
        ice_spread_sound: int
        part_0x908b06e9: int
        part_0x494de4a4: int
        sound_0xa861649f: int
        damage_info_0x18402aa9: json_util.JsonObject
        part_0xe701daea: int
        phazon_projectile: int
        wpsc: int
        damage_info_0x58769eb2: json_util.JsonObject
        phazon_projectile_damage: json_util.JsonObject
        phazon_enrage_sphere: int
        damage_info_0x8f3af226: json_util.JsonObject
        alternate_scannable_info: int
    

@dataclasses.dataclass()
class DarkSamus(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
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
    unknown_0x72edeb7d: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x72edeb7d, original_name='Unknown'
        ),
    })
    unknown_0x74fa22f0: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x74fa22f0, original_name='Unknown'
        ),
    })
    glide_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x1f468967, original_name='GlideSound'
        ),
    })
    missile_ricochet_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x1a08aadc, original_name='MissileRicochetSound'
        ),
    })
    unknown_0x6689925b: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x6689925b, original_name='Unknown'
        ),
    })
    txtr_0x3863160b: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3863160b, original_name='TXTR'
        ),
    })
    unknown_0x2c6a3344: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2c6a3344, original_name='Unknown'
        ),
    })
    melee_attack_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x4d790ee9, original_name='MeleeAttackDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    part_0x6d40aa56: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6d40aa56, original_name='PART'
        ),
    })
    part_0x9603a544: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9603a544, original_name='PART'
        ),
    })
    dive_attack_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x8688f535, original_name='DiveAttackDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x4aa5dd62: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4aa5dd62, original_name='Unknown'
        ),
    })
    unknown_0x1ad7dc21: float = dataclasses.field(default=500.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1ad7dc21, original_name='Unknown'
        ),
    })
    dive_attack_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xed30b0ef, original_name='DiveAttackEffect'
        ),
    })
    scatter_shot_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x855f0749, original_name='ScatterShotProjectile'
        ),
    })
    scatter_shot_projectile2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x83a5517f, original_name='ScatterShotProjectile2'
        ),
    })
    scatter_shot_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x8ea87062, original_name='ScatterShotDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x378285b9: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x378285b9, original_name='Unknown'
        ),
    })
    unknown_0xd242e25f: float = dataclasses.field(default=300.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd242e25f, original_name='Unknown'
        ),
    })
    normal_missile_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe00db62d, original_name='NormalMissileProjectile'
        ),
    })
    normal_missile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xc4128792, original_name='NormalMissileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x1f1ef7a9: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1f1ef7a9, original_name='Unknown'
        ),
    })
    unknown_0xc4a1a44e: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc4a1a44e, original_name='Unknown'
        ),
    })
    super_missile_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x29db4ee4, original_name='SuperMissileProjectile'
        ),
    })
    super_missile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x26632b7e, original_name='SuperMissileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    freeze_beam_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf9104a69, original_name='FreezeBeamProjectile'
        ),
    })
    freeze_beam_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xb5ba1fe7, original_name='FreezeBeamDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    txtr_0x7ffeb33d: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7ffeb33d, original_name='TXTR'
        ),
    })
    damage_interrupt_threshold: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8f70d3f2, original_name='DamageInterruptThreshold'
        ),
    })
    unknown_0xf317f4d5: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf317f4d5, original_name='Unknown'
        ),
    })
    sweep_swoosh: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd2122711, original_name='SweepSwoosh'
        ),
    })
    sweep_beam_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x08c2bfe0, original_name='SweepBeamDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    crsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CRSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x68b658f2, original_name='CRSC'
        ),
    })
    sweep_beam_sound: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xea17cb66, original_name='SweepBeamSound'
        ),
    })
    unknown_0x0ef8dc15: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0ef8dc15, original_name='Unknown'
        ),
    })
    invulnerable_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x072df331, original_name='InvulnerableModel'
        ),
    })
    invulnerable_skin_rules: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CSKR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xaa96399c, original_name='InvulnerableSkinRules'
        ),
    })
    boost_ball_model: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xf148f728, original_name='BoostBallModel', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    boost_ball_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xe18dc6fc, original_name='BoostBallDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    boost_ball_glow: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xac43ba34, original_name='BoostBallGlow'
        ),
    })
    swhc_0x449aa4aa: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SWHC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x449aa4aa, original_name='SWHC'
        ),
    })
    swhc_0x0345fa17: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SWHC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0345fa17, original_name='SWHC'
        ),
    })
    sound_0x2c72576b: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x2c72576b, original_name='Sound'
        ),
    })
    boost_ball_hit_player_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x9e02691c, original_name='BoostBallHitPlayerSound'
        ),
    })
    boost_ball_collision: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3433bc8b, original_name='BoostBallCollision'
        ),
    })
    audio_playback_parms: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x4841182b, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    part_0xa6c42023: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa6c42023, original_name='PART'
        ),
    })
    ice_spread_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xd3593630, original_name='IceSpreadSound'
        ),
    })
    part_0x908b06e9: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x908b06e9, original_name='PART'
        ),
    })
    part_0x494de4a4: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x494de4a4, original_name='PART'
        ),
    })
    sound_0xa861649f: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xa861649f, original_name='Sound'
        ),
    })
    damage_info_0x18402aa9: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x18402aa9, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    part_0xe701daea: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe701daea, original_name='PART'
        ),
    })
    phazon_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xbf62b633, original_name='PhazonProjectile'
        ),
    })
    wpsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8d123fe9, original_name='WPSC'
        ),
    })
    damage_info_0x58769eb2: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x58769eb2, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    phazon_projectile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x4d8e735f, original_name='PhazonProjectileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    phazon_enrage_sphere: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x83106405, original_name='PhazonEnrageSphere'
        ),
    })
    damage_info_0x8f3af226: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x8f3af226, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    alternate_scannable_info: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf60ac5cc, original_name='AlternateScannableInfo'
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
        return 'DRKS'

    @classmethod
    def modules(cls) -> list[str]:
        return ['DarkSamus.rel']

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
        if property_count != 63:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'detection_range': 32.0, 'collision_radius': 0.5, 'collision_height': 1.0, 'creature_size': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x72edeb7d
        unknown_0x72edeb7d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x74fa22f0
        unknown_0x74fa22f0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1f468967
        glide_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a08aadc
        missile_ricochet_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6689925b
        unknown_0x6689925b = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3863160b
        txtr_0x3863160b = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c6a3344
        unknown_0x2c6a3344 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d790ee9
        melee_attack_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d40aa56
        part_0x6d40aa56 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9603a544
        part_0x9603a544 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8688f535
        dive_attack_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4aa5dd62
        unknown_0x4aa5dd62 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ad7dc21
        unknown_0x1ad7dc21 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed30b0ef
        dive_attack_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x855f0749
        scatter_shot_projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x83a5517f
        scatter_shot_projectile2 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8ea87062
        scatter_shot_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x378285b9
        unknown_0x378285b9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd242e25f
        unknown_0xd242e25f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe00db62d
        normal_missile_projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4128792
        normal_missile_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1f1ef7a9
        unknown_0x1f1ef7a9 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4a1a44e
        unknown_0xc4a1a44e = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x29db4ee4
        super_missile_projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x26632b7e
        super_missile_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf9104a69
        freeze_beam_projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5ba1fe7
        freeze_beam_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7ffeb33d
        txtr_0x7ffeb33d = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f70d3f2
        damage_interrupt_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf317f4d5
        unknown_0xf317f4d5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd2122711
        sweep_swoosh = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08c2bfe0
        sweep_beam_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68b658f2
        crsc = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea17cb66
        sweep_beam_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0ef8dc15
        unknown_0x0ef8dc15 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x072df331
        invulnerable_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaa96399c
        invulnerable_skin_rules = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf148f728
        boost_ball_model = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe18dc6fc
        boost_ball_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xac43ba34
        boost_ball_glow = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x449aa4aa
        swhc_0x449aa4aa = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0345fa17
        swhc_0x0345fa17 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c72576b
        sound_0x2c72576b = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9e02691c
        boost_ball_hit_player_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3433bc8b
        boost_ball_collision = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4841182b
        audio_playback_parms = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6c42023
        part_0xa6c42023 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd3593630
        ice_spread_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x908b06e9
        part_0x908b06e9 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x494de4a4
        part_0x494de4a4 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa861649f
        sound_0xa861649f = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x18402aa9
        damage_info_0x18402aa9 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe701daea
        part_0xe701daea = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbf62b633
        phazon_projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d123fe9
        wpsc = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58769eb2
        damage_info_0x58769eb2 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d8e735f
        phazon_projectile_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_radius': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x83106405
        phazon_enrage_sphere = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f3af226
        damage_info_0x8f3af226 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf60ac5cc
        alternate_scannable_info = struct.unpack(">L", data.read(4))[0]
    
        return cls(editor_properties, patterned, actor_information, unknown_0x72edeb7d, unknown_0x74fa22f0, glide_sound, missile_ricochet_sound, unknown_0x6689925b, txtr_0x3863160b, unknown_0x2c6a3344, melee_attack_damage, part_0x6d40aa56, part_0x9603a544, dive_attack_damage, unknown_0x4aa5dd62, unknown_0x1ad7dc21, dive_attack_effect, scatter_shot_projectile, scatter_shot_projectile2, scatter_shot_damage, unknown_0x378285b9, unknown_0xd242e25f, normal_missile_projectile, normal_missile_damage, unknown_0x1f1ef7a9, unknown_0xc4a1a44e, super_missile_projectile, super_missile_damage, freeze_beam_projectile, freeze_beam_damage, txtr_0x7ffeb33d, damage_interrupt_threshold, unknown_0xf317f4d5, sweep_swoosh, sweep_beam_damage, crsc, sweep_beam_sound, unknown_0x0ef8dc15, invulnerable_model, invulnerable_skin_rules, boost_ball_model, boost_ball_damage, boost_ball_glow, swhc_0x449aa4aa, swhc_0x0345fa17, sound_0x2c72576b, boost_ball_hit_player_sound, boost_ball_collision, audio_playback_parms, part_0xa6c42023, ice_spread_sound, part_0x908b06e9, part_0x494de4a4, sound_0xa861649f, damage_info_0x18402aa9, part_0xe701daea, phazon_projectile, wpsc, damage_info_0x58769eb2, phazon_projectile_damage, phazon_enrage_sphere, damage_info_0x8f3af226, alternate_scannable_info)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00?')  # 63 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data, default_override={'detection_range': 32.0, 'collision_radius': 0.5, 'collision_height': 1.0, 'creature_size': 1})
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

        data.write(b'r\xed\xeb}')  # 0x72edeb7d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x72edeb7d))

        data.write(b't\xfa"\xf0')  # 0x74fa22f0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x74fa22f0))

        data.write(b'\x1fF\x89g')  # 0x1f468967
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.glide_sound))

        data.write(b'\x1a\x08\xaa\xdc')  # 0x1a08aadc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.missile_ricochet_sound))

        data.write(b'f\x89\x92[')  # 0x6689925b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x6689925b))

        data.write(b'8c\x16\x0b')  # 0x3863160b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.txtr_0x3863160b))

        data.write(b',j3D')  # 0x2c6a3344
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2c6a3344))

        data.write(b'My\x0e\xe9')  # 0x4d790ee9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.melee_attack_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'm@\xaaV')  # 0x6d40aa56
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x6d40aa56))

        data.write(b'\x96\x03\xa5D')  # 0x9603a544
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x9603a544))

        data.write(b'\x86\x88\xf55')  # 0x8688f535
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dive_attack_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'J\xa5\xddb')  # 0x4aa5dd62
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4aa5dd62))

        data.write(b'\x1a\xd7\xdc!')  # 0x1ad7dc21
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1ad7dc21))

        data.write(b'\xed0\xb0\xef')  # 0xed30b0ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.dive_attack_effect))

        data.write(b'\x85_\x07I')  # 0x855f0749
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.scatter_shot_projectile))

        data.write(b'\x83\xa5Q\x7f')  # 0x83a5517f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.scatter_shot_projectile2))

        data.write(b'\x8e\xa8pb')  # 0x8ea87062
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.scatter_shot_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'7\x82\x85\xb9')  # 0x378285b9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x378285b9))

        data.write(b'\xd2B\xe2_')  # 0xd242e25f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd242e25f))

        data.write(b'\xe0\r\xb6-')  # 0xe00db62d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.normal_missile_projectile))

        data.write(b'\xc4\x12\x87\x92')  # 0xc4128792
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.normal_missile_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1f\x1e\xf7\xa9')  # 0x1f1ef7a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x1f1ef7a9))

        data.write(b'\xc4\xa1\xa4N')  # 0xc4a1a44e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc4a1a44e))

        data.write(b')\xdbN\xe4')  # 0x29db4ee4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.super_missile_projectile))

        data.write(b'&c+~')  # 0x26632b7e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.super_missile_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf9\x10Ji')  # 0xf9104a69
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.freeze_beam_projectile))

        data.write(b'\xb5\xba\x1f\xe7')  # 0xb5ba1fe7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.freeze_beam_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x7f\xfe\xb3=')  # 0x7ffeb33d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.txtr_0x7ffeb33d))

        data.write(b'\x8fp\xd3\xf2')  # 0x8f70d3f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_interrupt_threshold))

        data.write(b'\xf3\x17\xf4\xd5')  # 0xf317f4d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf317f4d5))

        data.write(b"\xd2\x12'\x11")  # 0xd2122711
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.sweep_swoosh))

        data.write(b'\x08\xc2\xbf\xe0')  # 0x8c2bfe0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sweep_beam_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'h\xb6X\xf2')  # 0x68b658f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.crsc))

        data.write(b'\xea\x17\xcbf')  # 0xea17cb66
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sweep_beam_sound))

        data.write(b'\x0e\xf8\xdc\x15')  # 0xef8dc15
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x0ef8dc15))

        data.write(b'\x07-\xf31')  # 0x72df331
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.invulnerable_model))

        data.write(b'\xaa\x969\x9c')  # 0xaa96399c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.invulnerable_skin_rules))

        data.write(b'\xf1H\xf7(')  # 0xf148f728
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.boost_ball_model.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe1\x8d\xc6\xfc')  # 0xe18dc6fc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.boost_ball_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xacC\xba4')  # 0xac43ba34
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.boost_ball_glow))

        data.write(b'D\x9a\xa4\xaa')  # 0x449aa4aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.swhc_0x449aa4aa))

        data.write(b'\x03E\xfa\x17')  # 0x345fa17
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.swhc_0x0345fa17))

        data.write(b',rWk')  # 0x2c72576b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x2c72576b))

        data.write(b'\x9e\x02i\x1c')  # 0x9e02691c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.boost_ball_hit_player_sound))

        data.write(b'43\xbc\x8b')  # 0x3433bc8b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.boost_ball_collision))

        data.write(b'HA\x18+')  # 0x4841182b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa6\xc4 #')  # 0xa6c42023
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0xa6c42023))

        data.write(b'\xd3Y60')  # 0xd3593630
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.ice_spread_sound))

        data.write(b'\x90\x8b\x06\xe9')  # 0x908b06e9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x908b06e9))

        data.write(b'IM\xe4\xa4')  # 0x494de4a4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x494de4a4))

        data.write(b'\xa8ad\x9f')  # 0xa861649f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0xa861649f))

        data.write(b'\x18@*\xa9')  # 0x18402aa9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x18402aa9.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe7\x01\xda\xea')  # 0xe701daea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0xe701daea))

        data.write(b'\xbfb\xb63')  # 0xbf62b633
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.phazon_projectile))

        data.write(b'\x8d\x12?\xe9')  # 0x8d123fe9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.wpsc))

        data.write(b'Xv\x9e\xb2')  # 0x58769eb2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x58769eb2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'M\x8es_')  # 0x4d8e735f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.phazon_projectile_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_radius': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x83\x10d\x05')  # 0x83106405
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.phazon_enrage_sphere))

        data.write(b'\x8f:\xf2&')  # 0x8f3af226
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x8f3af226.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf6\n\xc5\xcc')  # 0xf60ac5cc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.alternate_scannable_info))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DarkSamusJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            unknown_0x72edeb7d=json_data['unknown_0x72edeb7d'],
            unknown_0x74fa22f0=json_data['unknown_0x74fa22f0'],
            glide_sound=json_data['glide_sound'],
            missile_ricochet_sound=json_data['missile_ricochet_sound'],
            unknown_0x6689925b=json_data['unknown_0x6689925b'],
            txtr_0x3863160b=json_data['txtr_0x3863160b'],
            unknown_0x2c6a3344=json_data['unknown_0x2c6a3344'],
            melee_attack_damage=DamageInfo.from_json(json_data['melee_attack_damage']),
            part_0x6d40aa56=json_data['part_0x6d40aa56'],
            part_0x9603a544=json_data['part_0x9603a544'],
            dive_attack_damage=DamageInfo.from_json(json_data['dive_attack_damage']),
            unknown_0x4aa5dd62=json_data['unknown_0x4aa5dd62'],
            unknown_0x1ad7dc21=json_data['unknown_0x1ad7dc21'],
            dive_attack_effect=json_data['dive_attack_effect'],
            scatter_shot_projectile=json_data['scatter_shot_projectile'],
            scatter_shot_projectile2=json_data['scatter_shot_projectile2'],
            scatter_shot_damage=DamageInfo.from_json(json_data['scatter_shot_damage']),
            unknown_0x378285b9=json_data['unknown_0x378285b9'],
            unknown_0xd242e25f=json_data['unknown_0xd242e25f'],
            normal_missile_projectile=json_data['normal_missile_projectile'],
            normal_missile_damage=DamageInfo.from_json(json_data['normal_missile_damage']),
            unknown_0x1f1ef7a9=json_data['unknown_0x1f1ef7a9'],
            unknown_0xc4a1a44e=json_data['unknown_0xc4a1a44e'],
            super_missile_projectile=json_data['super_missile_projectile'],
            super_missile_damage=DamageInfo.from_json(json_data['super_missile_damage']),
            freeze_beam_projectile=json_data['freeze_beam_projectile'],
            freeze_beam_damage=DamageInfo.from_json(json_data['freeze_beam_damage']),
            txtr_0x7ffeb33d=json_data['txtr_0x7ffeb33d'],
            damage_interrupt_threshold=json_data['damage_interrupt_threshold'],
            unknown_0xf317f4d5=json_data['unknown_0xf317f4d5'],
            sweep_swoosh=json_data['sweep_swoosh'],
            sweep_beam_damage=DamageInfo.from_json(json_data['sweep_beam_damage']),
            crsc=json_data['crsc'],
            sweep_beam_sound=json_data['sweep_beam_sound'],
            unknown_0x0ef8dc15=json_data['unknown_0x0ef8dc15'],
            invulnerable_model=json_data['invulnerable_model'],
            invulnerable_skin_rules=json_data['invulnerable_skin_rules'],
            boost_ball_model=AnimationParameters.from_json(json_data['boost_ball_model']),
            boost_ball_damage=DamageInfo.from_json(json_data['boost_ball_damage']),
            boost_ball_glow=json_data['boost_ball_glow'],
            swhc_0x449aa4aa=json_data['swhc_0x449aa4aa'],
            swhc_0x0345fa17=json_data['swhc_0x0345fa17'],
            sound_0x2c72576b=json_data['sound_0x2c72576b'],
            boost_ball_hit_player_sound=json_data['boost_ball_hit_player_sound'],
            boost_ball_collision=json_data['boost_ball_collision'],
            audio_playback_parms=AudioPlaybackParms.from_json(json_data['audio_playback_parms']),
            part_0xa6c42023=json_data['part_0xa6c42023'],
            ice_spread_sound=json_data['ice_spread_sound'],
            part_0x908b06e9=json_data['part_0x908b06e9'],
            part_0x494de4a4=json_data['part_0x494de4a4'],
            sound_0xa861649f=json_data['sound_0xa861649f'],
            damage_info_0x18402aa9=DamageInfo.from_json(json_data['damage_info_0x18402aa9']),
            part_0xe701daea=json_data['part_0xe701daea'],
            phazon_projectile=json_data['phazon_projectile'],
            wpsc=json_data['wpsc'],
            damage_info_0x58769eb2=DamageInfo.from_json(json_data['damage_info_0x58769eb2']),
            phazon_projectile_damage=DamageInfo.from_json(json_data['phazon_projectile_damage']),
            phazon_enrage_sphere=json_data['phazon_enrage_sphere'],
            damage_info_0x8f3af226=DamageInfo.from_json(json_data['damage_info_0x8f3af226']),
            alternate_scannable_info=json_data['alternate_scannable_info'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'unknown_0x72edeb7d': self.unknown_0x72edeb7d,
            'unknown_0x74fa22f0': self.unknown_0x74fa22f0,
            'glide_sound': self.glide_sound,
            'missile_ricochet_sound': self.missile_ricochet_sound,
            'unknown_0x6689925b': self.unknown_0x6689925b,
            'txtr_0x3863160b': self.txtr_0x3863160b,
            'unknown_0x2c6a3344': self.unknown_0x2c6a3344,
            'melee_attack_damage': self.melee_attack_damage.to_json(),
            'part_0x6d40aa56': self.part_0x6d40aa56,
            'part_0x9603a544': self.part_0x9603a544,
            'dive_attack_damage': self.dive_attack_damage.to_json(),
            'unknown_0x4aa5dd62': self.unknown_0x4aa5dd62,
            'unknown_0x1ad7dc21': self.unknown_0x1ad7dc21,
            'dive_attack_effect': self.dive_attack_effect,
            'scatter_shot_projectile': self.scatter_shot_projectile,
            'scatter_shot_projectile2': self.scatter_shot_projectile2,
            'scatter_shot_damage': self.scatter_shot_damage.to_json(),
            'unknown_0x378285b9': self.unknown_0x378285b9,
            'unknown_0xd242e25f': self.unknown_0xd242e25f,
            'normal_missile_projectile': self.normal_missile_projectile,
            'normal_missile_damage': self.normal_missile_damage.to_json(),
            'unknown_0x1f1ef7a9': self.unknown_0x1f1ef7a9,
            'unknown_0xc4a1a44e': self.unknown_0xc4a1a44e,
            'super_missile_projectile': self.super_missile_projectile,
            'super_missile_damage': self.super_missile_damage.to_json(),
            'freeze_beam_projectile': self.freeze_beam_projectile,
            'freeze_beam_damage': self.freeze_beam_damage.to_json(),
            'txtr_0x7ffeb33d': self.txtr_0x7ffeb33d,
            'damage_interrupt_threshold': self.damage_interrupt_threshold,
            'unknown_0xf317f4d5': self.unknown_0xf317f4d5,
            'sweep_swoosh': self.sweep_swoosh,
            'sweep_beam_damage': self.sweep_beam_damage.to_json(),
            'crsc': self.crsc,
            'sweep_beam_sound': self.sweep_beam_sound,
            'unknown_0x0ef8dc15': self.unknown_0x0ef8dc15,
            'invulnerable_model': self.invulnerable_model,
            'invulnerable_skin_rules': self.invulnerable_skin_rules,
            'boost_ball_model': self.boost_ball_model.to_json(),
            'boost_ball_damage': self.boost_ball_damage.to_json(),
            'boost_ball_glow': self.boost_ball_glow,
            'swhc_0x449aa4aa': self.swhc_0x449aa4aa,
            'swhc_0x0345fa17': self.swhc_0x0345fa17,
            'sound_0x2c72576b': self.sound_0x2c72576b,
            'boost_ball_hit_player_sound': self.boost_ball_hit_player_sound,
            'boost_ball_collision': self.boost_ball_collision,
            'audio_playback_parms': self.audio_playback_parms.to_json(),
            'part_0xa6c42023': self.part_0xa6c42023,
            'ice_spread_sound': self.ice_spread_sound,
            'part_0x908b06e9': self.part_0x908b06e9,
            'part_0x494de4a4': self.part_0x494de4a4,
            'sound_0xa861649f': self.sound_0xa861649f,
            'damage_info_0x18402aa9': self.damage_info_0x18402aa9.to_json(),
            'part_0xe701daea': self.part_0xe701daea,
            'phazon_projectile': self.phazon_projectile,
            'wpsc': self.wpsc,
            'damage_info_0x58769eb2': self.damage_info_0x58769eb2.to_json(),
            'phazon_projectile_damage': self.phazon_projectile_damage.to_json(),
            'phazon_enrage_sphere': self.phazon_enrage_sphere,
            'damage_info_0x8f3af226': self.damage_info_0x8f3af226.to_json(),
            'alternate_scannable_info': self.alternate_scannable_info,
        }

    def _dependencies_for_glide_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.glide_sound)

    def _dependencies_for_missile_ricochet_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.missile_ricochet_sound)

    def _dependencies_for_txtr_0x3863160b(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.txtr_0x3863160b)

    def _dependencies_for_part_0x6d40aa56(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x6d40aa56)

    def _dependencies_for_part_0x9603a544(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x9603a544)

    def _dependencies_for_dive_attack_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.dive_attack_effect)

    def _dependencies_for_scatter_shot_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.scatter_shot_projectile)

    def _dependencies_for_scatter_shot_projectile2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.scatter_shot_projectile2)

    def _dependencies_for_normal_missile_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.normal_missile_projectile)

    def _dependencies_for_super_missile_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.super_missile_projectile)

    def _dependencies_for_freeze_beam_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.freeze_beam_projectile)

    def _dependencies_for_txtr_0x7ffeb33d(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.txtr_0x7ffeb33d)

    def _dependencies_for_sweep_swoosh(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.sweep_swoosh)

    def _dependencies_for_crsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.crsc)

    def _dependencies_for_invulnerable_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.invulnerable_model)

    def _dependencies_for_invulnerable_skin_rules(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.invulnerable_skin_rules)

    def _dependencies_for_boost_ball_glow(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.boost_ball_glow)

    def _dependencies_for_swhc_0x449aa4aa(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.swhc_0x449aa4aa)

    def _dependencies_for_swhc_0x0345fa17(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.swhc_0x0345fa17)

    def _dependencies_for_sound_0x2c72576b(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x2c72576b)

    def _dependencies_for_boost_ball_hit_player_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.boost_ball_hit_player_sound)

    def _dependencies_for_boost_ball_collision(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.boost_ball_collision)

    def _dependencies_for_part_0xa6c42023(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0xa6c42023)

    def _dependencies_for_ice_spread_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.ice_spread_sound)

    def _dependencies_for_part_0x908b06e9(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x908b06e9)

    def _dependencies_for_part_0x494de4a4(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x494de4a4)

    def _dependencies_for_sound_0xa861649f(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0xa861649f)

    def _dependencies_for_part_0xe701daea(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0xe701daea)

    def _dependencies_for_phazon_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.phazon_projectile)

    def _dependencies_for_wpsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc)

    def _dependencies_for_phazon_enrage_sphere(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.phazon_enrage_sphere)

    def _dependencies_for_alternate_scannable_info(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.alternate_scannable_info)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self._dependencies_for_glide_sound, "glide_sound", "int"),
            (self._dependencies_for_missile_ricochet_sound, "missile_ricochet_sound", "int"),
            (self._dependencies_for_txtr_0x3863160b, "txtr_0x3863160b", "AssetId"),
            (self.melee_attack_damage.dependencies_for, "melee_attack_damage", "DamageInfo"),
            (self._dependencies_for_part_0x6d40aa56, "part_0x6d40aa56", "AssetId"),
            (self._dependencies_for_part_0x9603a544, "part_0x9603a544", "AssetId"),
            (self.dive_attack_damage.dependencies_for, "dive_attack_damage", "DamageInfo"),
            (self._dependencies_for_dive_attack_effect, "dive_attack_effect", "AssetId"),
            (self._dependencies_for_scatter_shot_projectile, "scatter_shot_projectile", "AssetId"),
            (self._dependencies_for_scatter_shot_projectile2, "scatter_shot_projectile2", "AssetId"),
            (self.scatter_shot_damage.dependencies_for, "scatter_shot_damage", "DamageInfo"),
            (self._dependencies_for_normal_missile_projectile, "normal_missile_projectile", "AssetId"),
            (self.normal_missile_damage.dependencies_for, "normal_missile_damage", "DamageInfo"),
            (self._dependencies_for_super_missile_projectile, "super_missile_projectile", "AssetId"),
            (self.super_missile_damage.dependencies_for, "super_missile_damage", "DamageInfo"),
            (self._dependencies_for_freeze_beam_projectile, "freeze_beam_projectile", "AssetId"),
            (self.freeze_beam_damage.dependencies_for, "freeze_beam_damage", "DamageInfo"),
            (self._dependencies_for_txtr_0x7ffeb33d, "txtr_0x7ffeb33d", "AssetId"),
            (self._dependencies_for_sweep_swoosh, "sweep_swoosh", "AssetId"),
            (self.sweep_beam_damage.dependencies_for, "sweep_beam_damage", "DamageInfo"),
            (self._dependencies_for_crsc, "crsc", "AssetId"),
            (self._dependencies_for_invulnerable_model, "invulnerable_model", "AssetId"),
            (self._dependencies_for_invulnerable_skin_rules, "invulnerable_skin_rules", "AssetId"),
            (self.boost_ball_model.dependencies_for, "boost_ball_model", "AnimationParameters"),
            (self.boost_ball_damage.dependencies_for, "boost_ball_damage", "DamageInfo"),
            (self._dependencies_for_boost_ball_glow, "boost_ball_glow", "AssetId"),
            (self._dependencies_for_swhc_0x449aa4aa, "swhc_0x449aa4aa", "AssetId"),
            (self._dependencies_for_swhc_0x0345fa17, "swhc_0x0345fa17", "AssetId"),
            (self._dependencies_for_sound_0x2c72576b, "sound_0x2c72576b", "int"),
            (self._dependencies_for_boost_ball_hit_player_sound, "boost_ball_hit_player_sound", "int"),
            (self._dependencies_for_boost_ball_collision, "boost_ball_collision", "AssetId"),
            (self.audio_playback_parms.dependencies_for, "audio_playback_parms", "AudioPlaybackParms"),
            (self._dependencies_for_part_0xa6c42023, "part_0xa6c42023", "AssetId"),
            (self._dependencies_for_ice_spread_sound, "ice_spread_sound", "int"),
            (self._dependencies_for_part_0x908b06e9, "part_0x908b06e9", "AssetId"),
            (self._dependencies_for_part_0x494de4a4, "part_0x494de4a4", "AssetId"),
            (self._dependencies_for_sound_0xa861649f, "sound_0xa861649f", "int"),
            (self.damage_info_0x18402aa9.dependencies_for, "damage_info_0x18402aa9", "DamageInfo"),
            (self._dependencies_for_part_0xe701daea, "part_0xe701daea", "AssetId"),
            (self._dependencies_for_phazon_projectile, "phazon_projectile", "AssetId"),
            (self._dependencies_for_wpsc, "wpsc", "AssetId"),
            (self.damage_info_0x58769eb2.dependencies_for, "damage_info_0x58769eb2", "DamageInfo"),
            (self.phazon_projectile_damage.dependencies_for, "phazon_projectile_damage", "DamageInfo"),
            (self._dependencies_for_phazon_enrage_sphere, "phazon_enrage_sphere", "AssetId"),
            (self.damage_info_0x8f3af226.dependencies_for, "damage_info_0x8f3af226", "DamageInfo"),
            (self._dependencies_for_alternate_scannable_info, "alternate_scannable_info", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for DarkSamus.{field_name} ({field_type}): {e}"
                )


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'detection_range': 32.0, 'collision_radius': 0.5, 'collision_height': 1.0, 'creature_size': 1})


def _decode_unknown_0x72edeb7d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x74fa22f0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_glide_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_missile_ricochet_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x6689925b(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_txtr_0x3863160b(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x2c6a3344(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_part_0x6d40aa56(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0x9603a544(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x4aa5dd62(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1ad7dc21(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dive_attack_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_scatter_shot_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_scatter_shot_projectile2(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x378285b9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd242e25f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_normal_missile_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x1f1ef7a9(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xc4a1a44e(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_super_missile_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_freeze_beam_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_txtr_0x7ffeb33d(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_damage_interrupt_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf317f4d5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sweep_swoosh(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_crsc(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_sweep_beam_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x0ef8dc15(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_invulnerable_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_invulnerable_skin_rules(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_boost_ball_glow(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_swhc_0x449aa4aa(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_swhc_0x0345fa17(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_sound_0x2c72576b(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_boost_ball_hit_player_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_boost_ball_collision(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0xa6c42023(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_ice_spread_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_part_0x908b06e9(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0x494de4a4(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_sound_0xa861649f(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_part_0xe701daea(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_phazon_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_wpsc(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_phazon_projectile_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_radius': 5.0})


def _decode_phazon_enrage_sphere(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_alternate_scannable_info(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x72edeb7d: ('unknown_0x72edeb7d', _decode_unknown_0x72edeb7d),
    0x74fa22f0: ('unknown_0x74fa22f0', _decode_unknown_0x74fa22f0),
    0x1f468967: ('glide_sound', _decode_glide_sound),
    0x1a08aadc: ('missile_ricochet_sound', _decode_missile_ricochet_sound),
    0x6689925b: ('unknown_0x6689925b', _decode_unknown_0x6689925b),
    0x3863160b: ('txtr_0x3863160b', _decode_txtr_0x3863160b),
    0x2c6a3344: ('unknown_0x2c6a3344', _decode_unknown_0x2c6a3344),
    0x4d790ee9: ('melee_attack_damage', DamageInfo.from_stream),
    0x6d40aa56: ('part_0x6d40aa56', _decode_part_0x6d40aa56),
    0x9603a544: ('part_0x9603a544', _decode_part_0x9603a544),
    0x8688f535: ('dive_attack_damage', DamageInfo.from_stream),
    0x4aa5dd62: ('unknown_0x4aa5dd62', _decode_unknown_0x4aa5dd62),
    0x1ad7dc21: ('unknown_0x1ad7dc21', _decode_unknown_0x1ad7dc21),
    0xed30b0ef: ('dive_attack_effect', _decode_dive_attack_effect),
    0x855f0749: ('scatter_shot_projectile', _decode_scatter_shot_projectile),
    0x83a5517f: ('scatter_shot_projectile2', _decode_scatter_shot_projectile2),
    0x8ea87062: ('scatter_shot_damage', DamageInfo.from_stream),
    0x378285b9: ('unknown_0x378285b9', _decode_unknown_0x378285b9),
    0xd242e25f: ('unknown_0xd242e25f', _decode_unknown_0xd242e25f),
    0xe00db62d: ('normal_missile_projectile', _decode_normal_missile_projectile),
    0xc4128792: ('normal_missile_damage', DamageInfo.from_stream),
    0x1f1ef7a9: ('unknown_0x1f1ef7a9', _decode_unknown_0x1f1ef7a9),
    0xc4a1a44e: ('unknown_0xc4a1a44e', _decode_unknown_0xc4a1a44e),
    0x29db4ee4: ('super_missile_projectile', _decode_super_missile_projectile),
    0x26632b7e: ('super_missile_damage', DamageInfo.from_stream),
    0xf9104a69: ('freeze_beam_projectile', _decode_freeze_beam_projectile),
    0xb5ba1fe7: ('freeze_beam_damage', DamageInfo.from_stream),
    0x7ffeb33d: ('txtr_0x7ffeb33d', _decode_txtr_0x7ffeb33d),
    0x8f70d3f2: ('damage_interrupt_threshold', _decode_damage_interrupt_threshold),
    0xf317f4d5: ('unknown_0xf317f4d5', _decode_unknown_0xf317f4d5),
    0xd2122711: ('sweep_swoosh', _decode_sweep_swoosh),
    0x8c2bfe0: ('sweep_beam_damage', DamageInfo.from_stream),
    0x68b658f2: ('crsc', _decode_crsc),
    0xea17cb66: ('sweep_beam_sound', _decode_sweep_beam_sound),
    0xef8dc15: ('unknown_0x0ef8dc15', _decode_unknown_0x0ef8dc15),
    0x72df331: ('invulnerable_model', _decode_invulnerable_model),
    0xaa96399c: ('invulnerable_skin_rules', _decode_invulnerable_skin_rules),
    0xf148f728: ('boost_ball_model', AnimationParameters.from_stream),
    0xe18dc6fc: ('boost_ball_damage', DamageInfo.from_stream),
    0xac43ba34: ('boost_ball_glow', _decode_boost_ball_glow),
    0x449aa4aa: ('swhc_0x449aa4aa', _decode_swhc_0x449aa4aa),
    0x345fa17: ('swhc_0x0345fa17', _decode_swhc_0x0345fa17),
    0x2c72576b: ('sound_0x2c72576b', _decode_sound_0x2c72576b),
    0x9e02691c: ('boost_ball_hit_player_sound', _decode_boost_ball_hit_player_sound),
    0x3433bc8b: ('boost_ball_collision', _decode_boost_ball_collision),
    0x4841182b: ('audio_playback_parms', AudioPlaybackParms.from_stream),
    0xa6c42023: ('part_0xa6c42023', _decode_part_0xa6c42023),
    0xd3593630: ('ice_spread_sound', _decode_ice_spread_sound),
    0x908b06e9: ('part_0x908b06e9', _decode_part_0x908b06e9),
    0x494de4a4: ('part_0x494de4a4', _decode_part_0x494de4a4),
    0xa861649f: ('sound_0xa861649f', _decode_sound_0xa861649f),
    0x18402aa9: ('damage_info_0x18402aa9', DamageInfo.from_stream),
    0xe701daea: ('part_0xe701daea', _decode_part_0xe701daea),
    0xbf62b633: ('phazon_projectile', _decode_phazon_projectile),
    0x8d123fe9: ('wpsc', _decode_wpsc),
    0x58769eb2: ('damage_info_0x58769eb2', DamageInfo.from_stream),
    0x4d8e735f: ('phazon_projectile_damage', _decode_phazon_projectile_damage),
    0x83106405: ('phazon_enrage_sphere', _decode_phazon_enrage_sphere),
    0x8f3af226: ('damage_info_0x8f3af226', DamageInfo.from_stream),
    0xf60ac5cc: ('alternate_scannable_info', _decode_alternate_scannable_info),
}
