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
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.IngPossessionData import IngPossessionData
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class GrenchlerJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        unknown_0x04d51e3a: float
        is_grapple_guardian: bool
        has_health_bar: bool
        damage_vulnerability: json_util.JsonObject
        tail: json_util.JsonObject
        unknown_0x0abef809: json_util.JsonObject
        tailless_model: int
        tailless_skin_rules: int
        unknown_0x9b193ae8: json_util.JsonObject
        unknown_0xc24cf580: json_util.JsonObject
        cmdl: int
        cskr: int
        tail_hit_sound: int
        tail_destroyed_sound: int
        unknown_0x5d8f2bee: float
        unknown_0x7bd1a35f: float
        unknown_0xea4b88c8: float
        unknown_0xaa04f0be: float
        unknown_0x98d5d373: float
        unknown_0xd89aab05: float
        unknown_0x2e6096ee: float
        unknown_0x6e2fee98: float
        unknown_0x49632b31: float
        bite_damage: json_util.JsonObject
        unknown_0x262b2508: float
        unknown_0x66645d7e: float
        unknown_0x909e6095: float
        unknown_0xd0d118e3: float
        electric_effect: int
        beam_damage: json_util.JsonObject
        unknown_0x680ce795: float
        audio_playback_parms_0xad47febe: json_util.JsonObject
        unknown_0x06f7ceed: float
        unknown_0x46b8b69b: float
        unknown_0xb0428b70: float
        unknown_0xf00df306: float
        unknown_0xb00775e6: float
        burst_projectile: int
        burst_damage: json_util.JsonObject
        surface_rings_effect: int
        part_0xbf4daae6: int
        part_always_ff: int
        part_0xffcee1a9: int
        grapple_swoosh: int
        grapple_beam_part: int
        grapple_hit_fx: int
        grapple_damage: json_util.JsonObject
        audio_playback_parms_0xb6b9074b: json_util.JsonObject
        beam_effect: int
        unknown_0xd4753ff4: int
        unknown_0x05fc6001: float
        unknown_0x13e5b580: float
        unknown_0xfc6f199d: float
        grapple_visor_effect: int
        damage_info: json_util.JsonObject
        part_0x54b6bfa1: int
        audio_playback_parms_0x5cf705f2: json_util.JsonObject
        part_0xb9f9f4f2: int
        alternate_scannable_info: int
        ing_possession_data: json_util.JsonObject
    

@dataclasses.dataclass()
class Grenchler(BaseObjectType):
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
    unknown_0x04d51e3a: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x04d51e3a, original_name='Unknown'
        ),
    })
    is_grapple_guardian: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x33408e7f, original_name='IsGrappleGuardian'
        ),
    })
    has_health_bar: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x67b6ea0b, original_name='HasHealthBar'
        ),
    })
    damage_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x0a7326a3, original_name='DamageVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    tail: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa18f626b, original_name='Tail', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unknown_0x0abef809: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x0abef809, original_name='Unknown', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    tailless_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4f3a4566, original_name='TaillessModel'
        ),
    })
    tailless_skin_rules: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CSKR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x401bc111, original_name='TaillessSkinRules'
        ),
    })
    unknown_0x9b193ae8: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x9b193ae8, original_name='Unknown', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unknown_0xc24cf580: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xc24cf580, original_name='Unknown', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    cmdl: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x72258fe7, original_name='CMDL'
        ),
    })
    cskr: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CSKR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe5fba24c, original_name='CSKR'
        ),
    })
    tail_hit_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x55c51213, original_name='TailHitSound'
        ),
    })
    tail_destroyed_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x385e4738, original_name='TailDestroyedSound'
        ),
    })
    unknown_0x5d8f2bee: float = dataclasses.field(default=4.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5d8f2bee, original_name='Unknown'
        ),
    })
    unknown_0x7bd1a35f: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7bd1a35f, original_name='Unknown'
        ),
    })
    unknown_0xea4b88c8: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xea4b88c8, original_name='Unknown'
        ),
    })
    unknown_0xaa04f0be: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaa04f0be, original_name='Unknown'
        ),
    })
    unknown_0x98d5d373: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x98d5d373, original_name='Unknown'
        ),
    })
    unknown_0xd89aab05: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd89aab05, original_name='Unknown'
        ),
    })
    unknown_0x2e6096ee: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2e6096ee, original_name='Unknown'
        ),
    })
    unknown_0x6e2fee98: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6e2fee98, original_name='Unknown'
        ),
    })
    unknown_0x49632b31: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x49632b31, original_name='Unknown'
        ),
    })
    bite_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xdf636c4b, original_name='BiteDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x262b2508: float = dataclasses.field(default=9.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x262b2508, original_name='Unknown'
        ),
    })
    unknown_0x66645d7e: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x66645d7e, original_name='Unknown'
        ),
    })
    unknown_0x909e6095: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x909e6095, original_name='Unknown'
        ),
    })
    unknown_0xd0d118e3: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd0d118e3, original_name='Unknown'
        ),
    })
    electric_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x49fae143, original_name='ElectricEffect'
        ),
    })
    beam_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x13e30e4d, original_name='BeamDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x680ce795: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x680ce795, original_name='Unknown'
        ),
    })
    audio_playback_parms_0xad47febe: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xad47febe, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    unknown_0x06f7ceed: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x06f7ceed, original_name='Unknown'
        ),
    })
    unknown_0x46b8b69b: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x46b8b69b, original_name='Unknown'
        ),
    })
    unknown_0xb0428b70: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb0428b70, original_name='Unknown'
        ),
    })
    unknown_0xf00df306: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf00df306, original_name='Unknown'
        ),
    })
    unknown_0xb00775e6: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb00775e6, original_name='Unknown'
        ),
    })
    burst_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7ef9aa67, original_name='BurstProjectile'
        ),
    })
    burst_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x5285db00, original_name='BurstDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    surface_rings_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x30b81a7e, original_name='SurfaceRingsEffect'
        ),
    })
    part_0xbf4daae6: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xbf4daae6, original_name='PART'
        ),
    })
    part_always_ff: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x70247a6e, original_name='PART? (Always FF)'
        ),
    })
    part_0xffcee1a9: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xffcee1a9, original_name='PART'
        ),
    })
    grapple_swoosh: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xae1f2a26, original_name='GrappleSwoosh'
        ),
    })
    grapple_beam_part: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0dabf0af, original_name='GrappleBeamPart'
        ),
    })
    grapple_hit_fx: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe51746d1, original_name='GrappleHitFx'
        ),
    })
    grapple_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x2ce7520f, original_name='GrappleDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    audio_playback_parms_0xb6b9074b: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xb6b9074b, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    beam_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x05439a08, original_name='BeamEffect'
        ),
    })
    unknown_0xd4753ff4: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd4753ff4, original_name='Unknown'
        ),
    })
    unknown_0x05fc6001: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x05fc6001, original_name='Unknown'
        ),
    })
    unknown_0x13e5b580: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x13e5b580, original_name='Unknown'
        ),
    })
    unknown_0xfc6f199d: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfc6f199d, original_name='Unknown'
        ),
    })
    grapple_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf6502596, original_name='GrappleVisorEffect'
        ),
    })
    damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x6ec26414, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    part_0x54b6bfa1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x54b6bfa1, original_name='PART'
        ),
    })
    audio_playback_parms_0x5cf705f2: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x5cf705f2, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    part_0xb9f9f4f2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb9f9f4f2, original_name='PART'
        ),
    })
    alternate_scannable_info: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf60ac5cc, original_name='AlternateScannableInfo'
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
        return 'GRCH'

    @classmethod
    def modules(cls) -> list[str]:
        return ['Grenchler.rel']

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
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'leash_radius': 100.0, 'collision_radius': 1.600000023841858, 'collision_height': 2.5, 'step_up_height': 1.0, 'creature_size': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x04d51e3a
        unknown_0x04d51e3a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x33408e7f
        is_grapple_guardian = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x67b6ea0b
        has_health_bar = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a7326a3
        damage_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa18f626b
        tail = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0abef809
        unknown_0x0abef809 = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f3a4566
        tailless_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x401bc111
        tailless_skin_rules = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9b193ae8
        unknown_0x9b193ae8 = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc24cf580
        unknown_0xc24cf580 = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x72258fe7
        cmdl = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe5fba24c
        cskr = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x55c51213
        tail_hit_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x385e4738
        tail_destroyed_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5d8f2bee
        unknown_0x5d8f2bee = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7bd1a35f
        unknown_0x7bd1a35f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea4b88c8
        unknown_0xea4b88c8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaa04f0be
        unknown_0xaa04f0be = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x98d5d373
        unknown_0x98d5d373 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd89aab05
        unknown_0xd89aab05 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2e6096ee
        unknown_0x2e6096ee = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6e2fee98
        unknown_0x6e2fee98 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49632b31
        unknown_0x49632b31 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdf636c4b
        bite_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x262b2508
        unknown_0x262b2508 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66645d7e
        unknown_0x66645d7e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x909e6095
        unknown_0x909e6095 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0d118e3
        unknown_0xd0d118e3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49fae143
        electric_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13e30e4d
        beam_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x680ce795
        unknown_0x680ce795 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad47febe
        audio_playback_parms_0xad47febe = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x06f7ceed
        unknown_0x06f7ceed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x46b8b69b
        unknown_0x46b8b69b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb0428b70
        unknown_0xb0428b70 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf00df306
        unknown_0xf00df306 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb00775e6
        unknown_0xb00775e6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7ef9aa67
        burst_projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5285db00
        burst_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x30b81a7e
        surface_rings_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbf4daae6
        part_0xbf4daae6 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x70247a6e
        part_always_ff = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xffcee1a9
        part_0xffcee1a9 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xae1f2a26
        grapple_swoosh = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0dabf0af
        grapple_beam_part = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe51746d1
        grapple_hit_fx = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ce7520f
        grapple_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb6b9074b
        audio_playback_parms_0xb6b9074b = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x05439a08
        beam_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4753ff4
        unknown_0xd4753ff4 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x05fc6001
        unknown_0x05fc6001 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13e5b580
        unknown_0x13e5b580 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfc6f199d
        unknown_0xfc6f199d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf6502596
        grapple_visor_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ec26414
        damage_info = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x54b6bfa1
        part_0x54b6bfa1 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5cf705f2
        audio_playback_parms_0x5cf705f2 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb9f9f4f2
        part_0xb9f9f4f2 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf60ac5cc
        alternate_scannable_info = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe61748ed
        ing_possession_data = IngPossessionData.from_stream(data, property_size)
    
        return cls(editor_properties, patterned, actor_information, unknown_0x04d51e3a, is_grapple_guardian, has_health_bar, damage_vulnerability, tail, unknown_0x0abef809, tailless_model, tailless_skin_rules, unknown_0x9b193ae8, unknown_0xc24cf580, cmdl, cskr, tail_hit_sound, tail_destroyed_sound, unknown_0x5d8f2bee, unknown_0x7bd1a35f, unknown_0xea4b88c8, unknown_0xaa04f0be, unknown_0x98d5d373, unknown_0xd89aab05, unknown_0x2e6096ee, unknown_0x6e2fee98, unknown_0x49632b31, bite_damage, unknown_0x262b2508, unknown_0x66645d7e, unknown_0x909e6095, unknown_0xd0d118e3, electric_effect, beam_damage, unknown_0x680ce795, audio_playback_parms_0xad47febe, unknown_0x06f7ceed, unknown_0x46b8b69b, unknown_0xb0428b70, unknown_0xf00df306, unknown_0xb00775e6, burst_projectile, burst_damage, surface_rings_effect, part_0xbf4daae6, part_always_ff, part_0xffcee1a9, grapple_swoosh, grapple_beam_part, grapple_hit_fx, grapple_damage, audio_playback_parms_0xb6b9074b, beam_effect, unknown_0xd4753ff4, unknown_0x05fc6001, unknown_0x13e5b580, unknown_0xfc6f199d, grapple_visor_effect, damage_info, part_0x54b6bfa1, audio_playback_parms_0x5cf705f2, part_0xb9f9f4f2, alternate_scannable_info, ing_possession_data)

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
        self.patterned.to_stream(data, default_override={'leash_radius': 100.0, 'collision_radius': 1.600000023841858, 'collision_height': 2.5, 'step_up_height': 1.0, 'creature_size': 1})
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

        data.write(b'\x04\xd5\x1e:')  # 0x4d51e3a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x04d51e3a))

        data.write(b'3@\x8e\x7f')  # 0x33408e7f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_grapple_guardian))

        data.write(b'g\xb6\xea\x0b')  # 0x67b6ea0b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.has_health_bar))

        data.write(b'\ns&\xa3')  # 0xa7326a3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa1\x8fbk')  # 0xa18f626b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.tail.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\n\xbe\xf8\t')  # 0xabef809
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x0abef809.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'O:Ef')  # 0x4f3a4566
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.tailless_model))

        data.write(b'@\x1b\xc1\x11')  # 0x401bc111
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.tailless_skin_rules))

        data.write(b'\x9b\x19:\xe8')  # 0x9b193ae8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x9b193ae8.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc2L\xf5\x80')  # 0xc24cf580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xc24cf580.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'r%\x8f\xe7')  # 0x72258fe7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.cmdl))

        data.write(b'\xe5\xfb\xa2L')  # 0xe5fba24c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.cskr))

        data.write(b'U\xc5\x12\x13')  # 0x55c51213
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.tail_hit_sound))

        data.write(b'8^G8')  # 0x385e4738
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.tail_destroyed_sound))

        data.write(b']\x8f+\xee')  # 0x5d8f2bee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5d8f2bee))

        data.write(b'{\xd1\xa3_')  # 0x7bd1a35f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7bd1a35f))

        data.write(b'\xeaK\x88\xc8')  # 0xea4b88c8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xea4b88c8))

        data.write(b'\xaa\x04\xf0\xbe')  # 0xaa04f0be
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xaa04f0be))

        data.write(b'\x98\xd5\xd3s')  # 0x98d5d373
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x98d5d373))

        data.write(b'\xd8\x9a\xab\x05')  # 0xd89aab05
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd89aab05))

        data.write(b'.`\x96\xee')  # 0x2e6096ee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2e6096ee))

        data.write(b'n/\xee\x98')  # 0x6e2fee98
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6e2fee98))

        data.write(b'Ic+1')  # 0x49632b31
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x49632b31))

        data.write(b'\xdfclK')  # 0xdf636c4b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.bite_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'&+%\x08')  # 0x262b2508
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x262b2508))

        data.write(b'fd]~')  # 0x66645d7e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x66645d7e))

        data.write(b'\x90\x9e`\x95')  # 0x909e6095
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x909e6095))

        data.write(b'\xd0\xd1\x18\xe3')  # 0xd0d118e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd0d118e3))

        data.write(b'I\xfa\xe1C')  # 0x49fae143
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.electric_effect))

        data.write(b'\x13\xe3\x0eM')  # 0x13e30e4d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'h\x0c\xe7\x95')  # 0x680ce795
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x680ce795))

        data.write(b'\xadG\xfe\xbe')  # 0xad47febe
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xad47febe.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x06\xf7\xce\xed')  # 0x6f7ceed
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x06f7ceed))

        data.write(b'F\xb8\xb6\x9b')  # 0x46b8b69b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x46b8b69b))

        data.write(b'\xb0B\x8bp')  # 0xb0428b70
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb0428b70))

        data.write(b'\xf0\r\xf3\x06')  # 0xf00df306
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf00df306))

        data.write(b'\xb0\x07u\xe6')  # 0xb00775e6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb00775e6))

        data.write(b'~\xf9\xaag')  # 0x7ef9aa67
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.burst_projectile))

        data.write(b'R\x85\xdb\x00')  # 0x5285db00
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.burst_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'0\xb8\x1a~')  # 0x30b81a7e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.surface_rings_effect))

        data.write(b'\xbfM\xaa\xe6')  # 0xbf4daae6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0xbf4daae6))

        data.write(b'p$zn')  # 0x70247a6e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_always_ff))

        data.write(b'\xff\xce\xe1\xa9')  # 0xffcee1a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0xffcee1a9))

        data.write(b'\xae\x1f*&')  # 0xae1f2a26
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.grapple_swoosh))

        data.write(b'\r\xab\xf0\xaf')  # 0xdabf0af
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.grapple_beam_part))

        data.write(b'\xe5\x17F\xd1')  # 0xe51746d1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.grapple_hit_fx))

        data.write(b',\xe7R\x0f')  # 0x2ce7520f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb6\xb9\x07K')  # 0xb6b9074b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xb6b9074b.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x05C\x9a\x08')  # 0x5439a08
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.beam_effect))

        data.write(b'\xd4u?\xf4')  # 0xd4753ff4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xd4753ff4))

        data.write(b'\x05\xfc`\x01')  # 0x5fc6001
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x05fc6001))

        data.write(b'\x13\xe5\xb5\x80')  # 0x13e5b580
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x13e5b580))

        data.write(b'\xfco\x19\x9d')  # 0xfc6f199d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfc6f199d))

        data.write(b'\xf6P%\x96')  # 0xf6502596
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.grapple_visor_effect))

        data.write(b'n\xc2d\x14')  # 0x6ec26414
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'T\xb6\xbf\xa1')  # 0x54b6bfa1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x54b6bfa1))

        data.write(b'\\\xf7\x05\xf2')  # 0x5cf705f2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0x5cf705f2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb9\xf9\xf4\xf2')  # 0xb9f9f4f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0xb9f9f4f2))

        data.write(b'\xf6\n\xc5\xcc')  # 0xf60ac5cc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.alternate_scannable_info))

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
        json_data = typing.cast("GrenchlerJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            unknown_0x04d51e3a=json_data['unknown_0x04d51e3a'],
            is_grapple_guardian=json_data['is_grapple_guardian'],
            has_health_bar=json_data['has_health_bar'],
            damage_vulnerability=DamageVulnerability.from_json(json_data['damage_vulnerability']),
            tail=AnimationParameters.from_json(json_data['tail']),
            unknown_0x0abef809=AnimationParameters.from_json(json_data['unknown_0x0abef809']),
            tailless_model=json_data['tailless_model'],
            tailless_skin_rules=json_data['tailless_skin_rules'],
            unknown_0x9b193ae8=AnimationParameters.from_json(json_data['unknown_0x9b193ae8']),
            unknown_0xc24cf580=AnimationParameters.from_json(json_data['unknown_0xc24cf580']),
            cmdl=json_data['cmdl'],
            cskr=json_data['cskr'],
            tail_hit_sound=json_data['tail_hit_sound'],
            tail_destroyed_sound=json_data['tail_destroyed_sound'],
            unknown_0x5d8f2bee=json_data['unknown_0x5d8f2bee'],
            unknown_0x7bd1a35f=json_data['unknown_0x7bd1a35f'],
            unknown_0xea4b88c8=json_data['unknown_0xea4b88c8'],
            unknown_0xaa04f0be=json_data['unknown_0xaa04f0be'],
            unknown_0x98d5d373=json_data['unknown_0x98d5d373'],
            unknown_0xd89aab05=json_data['unknown_0xd89aab05'],
            unknown_0x2e6096ee=json_data['unknown_0x2e6096ee'],
            unknown_0x6e2fee98=json_data['unknown_0x6e2fee98'],
            unknown_0x49632b31=json_data['unknown_0x49632b31'],
            bite_damage=DamageInfo.from_json(json_data['bite_damage']),
            unknown_0x262b2508=json_data['unknown_0x262b2508'],
            unknown_0x66645d7e=json_data['unknown_0x66645d7e'],
            unknown_0x909e6095=json_data['unknown_0x909e6095'],
            unknown_0xd0d118e3=json_data['unknown_0xd0d118e3'],
            electric_effect=json_data['electric_effect'],
            beam_damage=DamageInfo.from_json(json_data['beam_damage']),
            unknown_0x680ce795=json_data['unknown_0x680ce795'],
            audio_playback_parms_0xad47febe=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xad47febe']),
            unknown_0x06f7ceed=json_data['unknown_0x06f7ceed'],
            unknown_0x46b8b69b=json_data['unknown_0x46b8b69b'],
            unknown_0xb0428b70=json_data['unknown_0xb0428b70'],
            unknown_0xf00df306=json_data['unknown_0xf00df306'],
            unknown_0xb00775e6=json_data['unknown_0xb00775e6'],
            burst_projectile=json_data['burst_projectile'],
            burst_damage=DamageInfo.from_json(json_data['burst_damage']),
            surface_rings_effect=json_data['surface_rings_effect'],
            part_0xbf4daae6=json_data['part_0xbf4daae6'],
            part_always_ff=json_data['part_always_ff'],
            part_0xffcee1a9=json_data['part_0xffcee1a9'],
            grapple_swoosh=json_data['grapple_swoosh'],
            grapple_beam_part=json_data['grapple_beam_part'],
            grapple_hit_fx=json_data['grapple_hit_fx'],
            grapple_damage=DamageInfo.from_json(json_data['grapple_damage']),
            audio_playback_parms_0xb6b9074b=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xb6b9074b']),
            beam_effect=json_data['beam_effect'],
            unknown_0xd4753ff4=json_data['unknown_0xd4753ff4'],
            unknown_0x05fc6001=json_data['unknown_0x05fc6001'],
            unknown_0x13e5b580=json_data['unknown_0x13e5b580'],
            unknown_0xfc6f199d=json_data['unknown_0xfc6f199d'],
            grapple_visor_effect=json_data['grapple_visor_effect'],
            damage_info=DamageInfo.from_json(json_data['damage_info']),
            part_0x54b6bfa1=json_data['part_0x54b6bfa1'],
            audio_playback_parms_0x5cf705f2=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0x5cf705f2']),
            part_0xb9f9f4f2=json_data['part_0xb9f9f4f2'],
            alternate_scannable_info=json_data['alternate_scannable_info'],
            ing_possession_data=IngPossessionData.from_json(json_data['ing_possession_data']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'unknown_0x04d51e3a': self.unknown_0x04d51e3a,
            'is_grapple_guardian': self.is_grapple_guardian,
            'has_health_bar': self.has_health_bar,
            'damage_vulnerability': self.damage_vulnerability.to_json(),
            'tail': self.tail.to_json(),
            'unknown_0x0abef809': self.unknown_0x0abef809.to_json(),
            'tailless_model': self.tailless_model,
            'tailless_skin_rules': self.tailless_skin_rules,
            'unknown_0x9b193ae8': self.unknown_0x9b193ae8.to_json(),
            'unknown_0xc24cf580': self.unknown_0xc24cf580.to_json(),
            'cmdl': self.cmdl,
            'cskr': self.cskr,
            'tail_hit_sound': self.tail_hit_sound,
            'tail_destroyed_sound': self.tail_destroyed_sound,
            'unknown_0x5d8f2bee': self.unknown_0x5d8f2bee,
            'unknown_0x7bd1a35f': self.unknown_0x7bd1a35f,
            'unknown_0xea4b88c8': self.unknown_0xea4b88c8,
            'unknown_0xaa04f0be': self.unknown_0xaa04f0be,
            'unknown_0x98d5d373': self.unknown_0x98d5d373,
            'unknown_0xd89aab05': self.unknown_0xd89aab05,
            'unknown_0x2e6096ee': self.unknown_0x2e6096ee,
            'unknown_0x6e2fee98': self.unknown_0x6e2fee98,
            'unknown_0x49632b31': self.unknown_0x49632b31,
            'bite_damage': self.bite_damage.to_json(),
            'unknown_0x262b2508': self.unknown_0x262b2508,
            'unknown_0x66645d7e': self.unknown_0x66645d7e,
            'unknown_0x909e6095': self.unknown_0x909e6095,
            'unknown_0xd0d118e3': self.unknown_0xd0d118e3,
            'electric_effect': self.electric_effect,
            'beam_damage': self.beam_damage.to_json(),
            'unknown_0x680ce795': self.unknown_0x680ce795,
            'audio_playback_parms_0xad47febe': self.audio_playback_parms_0xad47febe.to_json(),
            'unknown_0x06f7ceed': self.unknown_0x06f7ceed,
            'unknown_0x46b8b69b': self.unknown_0x46b8b69b,
            'unknown_0xb0428b70': self.unknown_0xb0428b70,
            'unknown_0xf00df306': self.unknown_0xf00df306,
            'unknown_0xb00775e6': self.unknown_0xb00775e6,
            'burst_projectile': self.burst_projectile,
            'burst_damage': self.burst_damage.to_json(),
            'surface_rings_effect': self.surface_rings_effect,
            'part_0xbf4daae6': self.part_0xbf4daae6,
            'part_always_ff': self.part_always_ff,
            'part_0xffcee1a9': self.part_0xffcee1a9,
            'grapple_swoosh': self.grapple_swoosh,
            'grapple_beam_part': self.grapple_beam_part,
            'grapple_hit_fx': self.grapple_hit_fx,
            'grapple_damage': self.grapple_damage.to_json(),
            'audio_playback_parms_0xb6b9074b': self.audio_playback_parms_0xb6b9074b.to_json(),
            'beam_effect': self.beam_effect,
            'unknown_0xd4753ff4': self.unknown_0xd4753ff4,
            'unknown_0x05fc6001': self.unknown_0x05fc6001,
            'unknown_0x13e5b580': self.unknown_0x13e5b580,
            'unknown_0xfc6f199d': self.unknown_0xfc6f199d,
            'grapple_visor_effect': self.grapple_visor_effect,
            'damage_info': self.damage_info.to_json(),
            'part_0x54b6bfa1': self.part_0x54b6bfa1,
            'audio_playback_parms_0x5cf705f2': self.audio_playback_parms_0x5cf705f2.to_json(),
            'part_0xb9f9f4f2': self.part_0xb9f9f4f2,
            'alternate_scannable_info': self.alternate_scannable_info,
            'ing_possession_data': self.ing_possession_data.to_json(),
        }

    def _dependencies_for_tailless_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.tailless_model)

    def _dependencies_for_tailless_skin_rules(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.tailless_skin_rules)

    def _dependencies_for_cmdl(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.cmdl)

    def _dependencies_for_cskr(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.cskr)

    def _dependencies_for_tail_hit_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.tail_hit_sound)

    def _dependencies_for_tail_destroyed_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.tail_destroyed_sound)

    def _dependencies_for_electric_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.electric_effect)

    def _dependencies_for_burst_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.burst_projectile)

    def _dependencies_for_surface_rings_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.surface_rings_effect)

    def _dependencies_for_part_0xbf4daae6(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0xbf4daae6)

    def _dependencies_for_part_always_ff(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_always_ff)

    def _dependencies_for_part_0xffcee1a9(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0xffcee1a9)

    def _dependencies_for_grapple_swoosh(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.grapple_swoosh)

    def _dependencies_for_grapple_beam_part(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.grapple_beam_part)

    def _dependencies_for_grapple_hit_fx(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.grapple_hit_fx)

    def _dependencies_for_beam_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.beam_effect)

    def _dependencies_for_grapple_visor_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.grapple_visor_effect)

    def _dependencies_for_part_0x54b6bfa1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x54b6bfa1)

    def _dependencies_for_part_0xb9f9f4f2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0xb9f9f4f2)

    def _dependencies_for_alternate_scannable_info(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.alternate_scannable_info)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self.damage_vulnerability.dependencies_for, "damage_vulnerability", "DamageVulnerability"),
            (self.tail.dependencies_for, "tail", "AnimationParameters"),
            (self.unknown_0x0abef809.dependencies_for, "unknown_0x0abef809", "AnimationParameters"),
            (self._dependencies_for_tailless_model, "tailless_model", "AssetId"),
            (self._dependencies_for_tailless_skin_rules, "tailless_skin_rules", "AssetId"),
            (self.unknown_0x9b193ae8.dependencies_for, "unknown_0x9b193ae8", "AnimationParameters"),
            (self.unknown_0xc24cf580.dependencies_for, "unknown_0xc24cf580", "AnimationParameters"),
            (self._dependencies_for_cmdl, "cmdl", "AssetId"),
            (self._dependencies_for_cskr, "cskr", "AssetId"),
            (self._dependencies_for_tail_hit_sound, "tail_hit_sound", "int"),
            (self._dependencies_for_tail_destroyed_sound, "tail_destroyed_sound", "int"),
            (self.bite_damage.dependencies_for, "bite_damage", "DamageInfo"),
            (self._dependencies_for_electric_effect, "electric_effect", "AssetId"),
            (self.beam_damage.dependencies_for, "beam_damage", "DamageInfo"),
            (self.audio_playback_parms_0xad47febe.dependencies_for, "audio_playback_parms_0xad47febe", "AudioPlaybackParms"),
            (self._dependencies_for_burst_projectile, "burst_projectile", "AssetId"),
            (self.burst_damage.dependencies_for, "burst_damage", "DamageInfo"),
            (self._dependencies_for_surface_rings_effect, "surface_rings_effect", "AssetId"),
            (self._dependencies_for_part_0xbf4daae6, "part_0xbf4daae6", "AssetId"),
            (self._dependencies_for_part_always_ff, "part_always_ff", "AssetId"),
            (self._dependencies_for_part_0xffcee1a9, "part_0xffcee1a9", "AssetId"),
            (self._dependencies_for_grapple_swoosh, "grapple_swoosh", "AssetId"),
            (self._dependencies_for_grapple_beam_part, "grapple_beam_part", "AssetId"),
            (self._dependencies_for_grapple_hit_fx, "grapple_hit_fx", "AssetId"),
            (self.grapple_damage.dependencies_for, "grapple_damage", "DamageInfo"),
            (self.audio_playback_parms_0xb6b9074b.dependencies_for, "audio_playback_parms_0xb6b9074b", "AudioPlaybackParms"),
            (self._dependencies_for_beam_effect, "beam_effect", "AssetId"),
            (self._dependencies_for_grapple_visor_effect, "grapple_visor_effect", "AssetId"),
            (self.damage_info.dependencies_for, "damage_info", "DamageInfo"),
            (self._dependencies_for_part_0x54b6bfa1, "part_0x54b6bfa1", "AssetId"),
            (self.audio_playback_parms_0x5cf705f2.dependencies_for, "audio_playback_parms_0x5cf705f2", "AudioPlaybackParms"),
            (self._dependencies_for_part_0xb9f9f4f2, "part_0xb9f9f4f2", "AssetId"),
            (self._dependencies_for_alternate_scannable_info, "alternate_scannable_info", "AssetId"),
            (self.ing_possession_data.dependencies_for, "ing_possession_data", "IngPossessionData"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Grenchler.{field_name} ({field_type}): {e}"
                )


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'leash_radius': 100.0, 'collision_radius': 1.600000023841858, 'collision_height': 2.5, 'step_up_height': 1.0, 'creature_size': 1})


def _decode_unknown_0x04d51e3a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_is_grapple_guardian(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_has_health_bar(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_tailless_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_tailless_skin_rules(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_cmdl(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_cskr(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_tail_hit_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_tail_destroyed_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x5d8f2bee(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7bd1a35f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xea4b88c8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xaa04f0be(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x98d5d373(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd89aab05(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2e6096ee(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6e2fee98(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x49632b31(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bite_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_unknown_0x262b2508(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x66645d7e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x909e6095(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd0d118e3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_electric_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_beam_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_unknown_0x680ce795(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x06f7ceed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x46b8b69b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb0428b70(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf00df306(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb00775e6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_burst_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_burst_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_surface_rings_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0xbf4daae6(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_always_ff(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0xffcee1a9(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_grapple_swoosh(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_grapple_beam_part(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_grapple_hit_fx(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_beam_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0xd4753ff4(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x05fc6001(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x13e5b580(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfc6f199d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grapple_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_damage_info(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_part_0x54b6bfa1(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0xb9f9f4f2(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_alternate_scannable_info(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x4d51e3a: ('unknown_0x04d51e3a', _decode_unknown_0x04d51e3a),
    0x33408e7f: ('is_grapple_guardian', _decode_is_grapple_guardian),
    0x67b6ea0b: ('has_health_bar', _decode_has_health_bar),
    0xa7326a3: ('damage_vulnerability', DamageVulnerability.from_stream),
    0xa18f626b: ('tail', AnimationParameters.from_stream),
    0xabef809: ('unknown_0x0abef809', AnimationParameters.from_stream),
    0x4f3a4566: ('tailless_model', _decode_tailless_model),
    0x401bc111: ('tailless_skin_rules', _decode_tailless_skin_rules),
    0x9b193ae8: ('unknown_0x9b193ae8', AnimationParameters.from_stream),
    0xc24cf580: ('unknown_0xc24cf580', AnimationParameters.from_stream),
    0x72258fe7: ('cmdl', _decode_cmdl),
    0xe5fba24c: ('cskr', _decode_cskr),
    0x55c51213: ('tail_hit_sound', _decode_tail_hit_sound),
    0x385e4738: ('tail_destroyed_sound', _decode_tail_destroyed_sound),
    0x5d8f2bee: ('unknown_0x5d8f2bee', _decode_unknown_0x5d8f2bee),
    0x7bd1a35f: ('unknown_0x7bd1a35f', _decode_unknown_0x7bd1a35f),
    0xea4b88c8: ('unknown_0xea4b88c8', _decode_unknown_0xea4b88c8),
    0xaa04f0be: ('unknown_0xaa04f0be', _decode_unknown_0xaa04f0be),
    0x98d5d373: ('unknown_0x98d5d373', _decode_unknown_0x98d5d373),
    0xd89aab05: ('unknown_0xd89aab05', _decode_unknown_0xd89aab05),
    0x2e6096ee: ('unknown_0x2e6096ee', _decode_unknown_0x2e6096ee),
    0x6e2fee98: ('unknown_0x6e2fee98', _decode_unknown_0x6e2fee98),
    0x49632b31: ('unknown_0x49632b31', _decode_unknown_0x49632b31),
    0xdf636c4b: ('bite_damage', _decode_bite_damage),
    0x262b2508: ('unknown_0x262b2508', _decode_unknown_0x262b2508),
    0x66645d7e: ('unknown_0x66645d7e', _decode_unknown_0x66645d7e),
    0x909e6095: ('unknown_0x909e6095', _decode_unknown_0x909e6095),
    0xd0d118e3: ('unknown_0xd0d118e3', _decode_unknown_0xd0d118e3),
    0x49fae143: ('electric_effect', _decode_electric_effect),
    0x13e30e4d: ('beam_damage', _decode_beam_damage),
    0x680ce795: ('unknown_0x680ce795', _decode_unknown_0x680ce795),
    0xad47febe: ('audio_playback_parms_0xad47febe', AudioPlaybackParms.from_stream),
    0x6f7ceed: ('unknown_0x06f7ceed', _decode_unknown_0x06f7ceed),
    0x46b8b69b: ('unknown_0x46b8b69b', _decode_unknown_0x46b8b69b),
    0xb0428b70: ('unknown_0xb0428b70', _decode_unknown_0xb0428b70),
    0xf00df306: ('unknown_0xf00df306', _decode_unknown_0xf00df306),
    0xb00775e6: ('unknown_0xb00775e6', _decode_unknown_0xb00775e6),
    0x7ef9aa67: ('burst_projectile', _decode_burst_projectile),
    0x5285db00: ('burst_damage', _decode_burst_damage),
    0x30b81a7e: ('surface_rings_effect', _decode_surface_rings_effect),
    0xbf4daae6: ('part_0xbf4daae6', _decode_part_0xbf4daae6),
    0x70247a6e: ('part_always_ff', _decode_part_always_ff),
    0xffcee1a9: ('part_0xffcee1a9', _decode_part_0xffcee1a9),
    0xae1f2a26: ('grapple_swoosh', _decode_grapple_swoosh),
    0xdabf0af: ('grapple_beam_part', _decode_grapple_beam_part),
    0xe51746d1: ('grapple_hit_fx', _decode_grapple_hit_fx),
    0x2ce7520f: ('grapple_damage', DamageInfo.from_stream),
    0xb6b9074b: ('audio_playback_parms_0xb6b9074b', AudioPlaybackParms.from_stream),
    0x5439a08: ('beam_effect', _decode_beam_effect),
    0xd4753ff4: ('unknown_0xd4753ff4', _decode_unknown_0xd4753ff4),
    0x5fc6001: ('unknown_0x05fc6001', _decode_unknown_0x05fc6001),
    0x13e5b580: ('unknown_0x13e5b580', _decode_unknown_0x13e5b580),
    0xfc6f199d: ('unknown_0xfc6f199d', _decode_unknown_0xfc6f199d),
    0xf6502596: ('grapple_visor_effect', _decode_grapple_visor_effect),
    0x6ec26414: ('damage_info', _decode_damage_info),
    0x54b6bfa1: ('part_0x54b6bfa1', _decode_part_0x54b6bfa1),
    0x5cf705f2: ('audio_playback_parms_0x5cf705f2', AudioPlaybackParms.from_stream),
    0xb9f9f4f2: ('part_0xb9f9f4f2', _decode_part_0xb9f9f4f2),
    0xf60ac5cc: ('alternate_scannable_info', _decode_alternate_scannable_info),
    0xe61748ed: ('ing_possession_data', IngPossessionData.from_stream),
}
