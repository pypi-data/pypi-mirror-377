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
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.archetypes.PowerBombGuardianStageProperties import PowerBombGuardianStageProperties
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SporbBaseJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        unknown_0x95e7a2c2: float
        unknown_0x76ba1c18: float
        unknown_0x3eb2de35: float
        unknown_0xe50d8dd2: float
        unknown_0x64d482d5: int
        unknown_0xc3e002ac: int
        shot_angle_variance: float
        attack_aim_offset: json_util.JsonValue
        tendril_particle_effect: int
        unknown_0x35557a83: float
        grabber_out_acceleration: float
        grabber_in_acceleration: float
        unknown_0xbfddabd4: float
        unknown_0x62bfaa35: float
        grabber_attach_time: float
        unknown_0xed82c56a: float
        unknown_0xe918f440: float
        spit_force: float
        spit_damage: float
        grab_damage: float
        unknown_0x2cfade2c: float
        unknown_0xb68e75cc: float
        unknown_0x6d31262b: float
        is_power_bomb_guardian: bool
        wpsc: int
        power_bomb_projectile_damage: json_util.JsonObject
        unknown_0x03a76d35: float
        unknown_0x6d4e0f5a: float
        unknown_0x3538d49b: float
        unknown_0xe89c7707: float
        unknown_0x738d1f51: float
        sound_0x9480c6d7: int
        unknown_0x48df4182: float
        unknown_0xe39482ad: float
        unknown_0xdd8502cc: float
        unknown_0x4ab8cf7d: float
        unknown_0xf5e28404: float
        grabber_fire_sound: int
        grabber_flight_sound: int
        grabber_hit_player_sound: int
        grabber_hit_world_sound: int
        grabber_retract_sound: int
        sound_0x64e9152d: int
        morphball_spit_sound: int
        grabber_explosion_sound: int
        ball_escape_sound: int
        needle_telegraph_sound: int
        grabber_telegraph_sound: int
        power_bomb_guardian_stage_properties_0x510dba97: json_util.JsonObject
        power_bomb_guardian_stage_properties_0x0b6c85f7: json_util.JsonObject
        power_bomb_guardian_stage_properties_0x8b9c92e8: json_util.JsonObject
        power_bomb_guardian_stage_properties_0xbfaefb37: json_util.JsonObject
    

@dataclasses.dataclass()
class SporbBase(BaseObjectType):
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
    unknown_0x95e7a2c2: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95e7a2c2, original_name='Unknown'
        ),
    })
    unknown_0x76ba1c18: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x76ba1c18, original_name='Unknown'
        ),
    })
    unknown_0x3eb2de35: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3eb2de35, original_name='Unknown'
        ),
    })
    unknown_0xe50d8dd2: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe50d8dd2, original_name='Unknown'
        ),
    })
    unknown_0x64d482d5: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x64d482d5, original_name='Unknown'
        ),
    })
    unknown_0xc3e002ac: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc3e002ac, original_name='Unknown'
        ),
    })
    shot_angle_variance: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd75f9cf2, original_name='ShotAngleVariance'
        ),
    })
    attack_aim_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x540c1f87, original_name='AttackAimOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    tendril_particle_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x33868c8f, original_name='TendrilParticleEffect'
        ),
    })
    unknown_0x35557a83: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x35557a83, original_name='Unknown'
        ),
    })
    grabber_out_acceleration: float = dataclasses.field(default=-10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x23bd3943, original_name='GrabberOutAcceleration'
        ),
    })
    grabber_in_acceleration: float = dataclasses.field(default=-100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd92f485d, original_name='GrabberInAcceleration'
        ),
    })
    unknown_0xbfddabd4: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbfddabd4, original_name='Unknown'
        ),
    })
    unknown_0x62bfaa35: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x62bfaa35, original_name='Unknown'
        ),
    })
    grabber_attach_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x433b5e30, original_name='GrabberAttachTime'
        ),
    })
    unknown_0xed82c56a: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed82c56a, original_name='Unknown'
        ),
    })
    unknown_0xe918f440: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe918f440, original_name='Unknown'
        ),
    })
    spit_force: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2731ad74, original_name='SpitForce'
        ),
    })
    spit_damage: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x03fb2dd4, original_name='SpitDamage'
        ),
    })
    grab_damage: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95ad8824, original_name='GrabDamage'
        ),
    })
    unknown_0x2cfade2c: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2cfade2c, original_name='Unknown'
        ),
    })
    unknown_0xb68e75cc: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb68e75cc, original_name='Unknown'
        ),
    })
    unknown_0x6d31262b: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6d31262b, original_name='Unknown'
        ),
    })
    is_power_bomb_guardian: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb628855a, original_name='IsPowerBombGuardian'
        ),
    })
    wpsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x990745dd, original_name='WPSC'
        ),
    })
    power_bomb_projectile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x5f3c27c6, original_name='PowerBombProjectileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x03a76d35: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x03a76d35, original_name='Unknown'
        ),
    })
    unknown_0x6d4e0f5a: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6d4e0f5a, original_name='Unknown'
        ),
    })
    unknown_0x3538d49b: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3538d49b, original_name='Unknown'
        ),
    })
    unknown_0xe89c7707: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe89c7707, original_name='Unknown'
        ),
    })
    unknown_0x738d1f51: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x738d1f51, original_name='Unknown'
        ),
    })
    sound_0x9480c6d7: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9480c6d7, original_name='Sound'
        ),
    })
    unknown_0x48df4182: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x48df4182, original_name='Unknown'
        ),
    })
    unknown_0xe39482ad: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe39482ad, original_name='Unknown'
        ),
    })
    unknown_0xdd8502cc: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdd8502cc, original_name='Unknown'
        ),
    })
    unknown_0x4ab8cf7d: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4ab8cf7d, original_name='Unknown'
        ),
    })
    unknown_0xf5e28404: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf5e28404, original_name='Unknown'
        ),
    })
    grabber_fire_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xa87d72fc, original_name='GrabberFireSound'
        ),
    })
    grabber_flight_sound: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x8661285e, original_name='GrabberFlightSound'
        ),
    })
    grabber_hit_player_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x4123323a, original_name='GrabberHitPlayerSound'
        ),
    })
    grabber_hit_world_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x4d2ec538, original_name='GrabberHitWorldSound'
        ),
    })
    grabber_retract_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xd51ca051, original_name='GrabberRetractSound'
        ),
    })
    sound_0x64e9152d: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x64e9152d, original_name='Sound'
        ),
    })
    morphball_spit_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x3acd0ecc, original_name='MorphballSpitSound'
        ),
    })
    grabber_explosion_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xfeb67317, original_name='GrabberExplosionSound'
        ),
    })
    ball_escape_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x88a20db0, original_name='BallEscapeSound'
        ),
    })
    needle_telegraph_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x95c1257f, original_name='NeedleTelegraphSound'
        ),
    })
    grabber_telegraph_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x2690e216, original_name='GrabberTelegraphSound'
        ),
    })
    power_bomb_guardian_stage_properties_0x510dba97: PowerBombGuardianStageProperties = dataclasses.field(default_factory=PowerBombGuardianStageProperties, metadata={
        'reflection': FieldReflection[PowerBombGuardianStageProperties](
            PowerBombGuardianStageProperties, id=0x510dba97, original_name='PowerBombGuardianStageProperties', from_json=PowerBombGuardianStageProperties.from_json, to_json=PowerBombGuardianStageProperties.to_json
        ),
    })
    power_bomb_guardian_stage_properties_0x0b6c85f7: PowerBombGuardianStageProperties = dataclasses.field(default_factory=PowerBombGuardianStageProperties, metadata={
        'reflection': FieldReflection[PowerBombGuardianStageProperties](
            PowerBombGuardianStageProperties, id=0x0b6c85f7, original_name='PowerBombGuardianStageProperties', from_json=PowerBombGuardianStageProperties.from_json, to_json=PowerBombGuardianStageProperties.to_json
        ),
    })
    power_bomb_guardian_stage_properties_0x8b9c92e8: PowerBombGuardianStageProperties = dataclasses.field(default_factory=PowerBombGuardianStageProperties, metadata={
        'reflection': FieldReflection[PowerBombGuardianStageProperties](
            PowerBombGuardianStageProperties, id=0x8b9c92e8, original_name='PowerBombGuardianStageProperties', from_json=PowerBombGuardianStageProperties.from_json, to_json=PowerBombGuardianStageProperties.to_json
        ),
    })
    power_bomb_guardian_stage_properties_0xbfaefb37: PowerBombGuardianStageProperties = dataclasses.field(default_factory=PowerBombGuardianStageProperties, metadata={
        'reflection': FieldReflection[PowerBombGuardianStageProperties](
            PowerBombGuardianStageProperties, id=0xbfaefb37, original_name='PowerBombGuardianStageProperties', from_json=PowerBombGuardianStageProperties.from_json, to_json=PowerBombGuardianStageProperties.to_json
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
        return 'SPBB'

    @classmethod
    def modules(cls) -> list[str]:
        return ['Sporb.rel']

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
        if property_count != 55:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95e7a2c2
        unknown_0x95e7a2c2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76ba1c18
        unknown_0x76ba1c18 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3eb2de35
        unknown_0x3eb2de35 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe50d8dd2
        unknown_0xe50d8dd2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x64d482d5
        unknown_0x64d482d5 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3e002ac
        unknown_0xc3e002ac = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd75f9cf2
        shot_angle_variance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x540c1f87
        attack_aim_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x33868c8f
        tendril_particle_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x35557a83
        unknown_0x35557a83 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x23bd3943
        grabber_out_acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd92f485d
        grabber_in_acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbfddabd4
        unknown_0xbfddabd4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x62bfaa35
        unknown_0x62bfaa35 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x433b5e30
        grabber_attach_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed82c56a
        unknown_0xed82c56a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe918f440
        unknown_0xe918f440 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2731ad74
        spit_force = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03fb2dd4
        spit_damage = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95ad8824
        grab_damage = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2cfade2c
        unknown_0x2cfade2c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb68e75cc
        unknown_0xb68e75cc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d31262b
        unknown_0x6d31262b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb628855a
        is_power_bomb_guardian = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x990745dd
        wpsc = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5f3c27c6
        power_bomb_projectile_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0, 'di_knock_back_power': 2.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03a76d35
        unknown_0x03a76d35 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d4e0f5a
        unknown_0x6d4e0f5a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3538d49b
        unknown_0x3538d49b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe89c7707
        unknown_0xe89c7707 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x738d1f51
        unknown_0x738d1f51 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9480c6d7
        sound_0x9480c6d7 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x48df4182
        unknown_0x48df4182 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe39482ad
        unknown_0xe39482ad = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd8502cc
        unknown_0xdd8502cc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ab8cf7d
        unknown_0x4ab8cf7d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5e28404
        unknown_0xf5e28404 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa87d72fc
        grabber_fire_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8661285e
        grabber_flight_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4123323a
        grabber_hit_player_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d2ec538
        grabber_hit_world_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd51ca051
        grabber_retract_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x64e9152d
        sound_0x64e9152d = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3acd0ecc
        morphball_spit_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfeb67317
        grabber_explosion_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88a20db0
        ball_escape_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95c1257f
        needle_telegraph_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2690e216
        grabber_telegraph_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x510dba97
        power_bomb_guardian_stage_properties_0x510dba97 = PowerBombGuardianStageProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0b6c85f7
        power_bomb_guardian_stage_properties_0x0b6c85f7 = PowerBombGuardianStageProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b9c92e8
        power_bomb_guardian_stage_properties_0x8b9c92e8 = PowerBombGuardianStageProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbfaefb37
        power_bomb_guardian_stage_properties_0xbfaefb37 = PowerBombGuardianStageProperties.from_stream(data, property_size)
    
        return cls(editor_properties, patterned, actor_information, unknown_0x95e7a2c2, unknown_0x76ba1c18, unknown_0x3eb2de35, unknown_0xe50d8dd2, unknown_0x64d482d5, unknown_0xc3e002ac, shot_angle_variance, attack_aim_offset, tendril_particle_effect, unknown_0x35557a83, grabber_out_acceleration, grabber_in_acceleration, unknown_0xbfddabd4, unknown_0x62bfaa35, grabber_attach_time, unknown_0xed82c56a, unknown_0xe918f440, spit_force, spit_damage, grab_damage, unknown_0x2cfade2c, unknown_0xb68e75cc, unknown_0x6d31262b, is_power_bomb_guardian, wpsc, power_bomb_projectile_damage, unknown_0x03a76d35, unknown_0x6d4e0f5a, unknown_0x3538d49b, unknown_0xe89c7707, unknown_0x738d1f51, sound_0x9480c6d7, unknown_0x48df4182, unknown_0xe39482ad, unknown_0xdd8502cc, unknown_0x4ab8cf7d, unknown_0xf5e28404, grabber_fire_sound, grabber_flight_sound, grabber_hit_player_sound, grabber_hit_world_sound, grabber_retract_sound, sound_0x64e9152d, morphball_spit_sound, grabber_explosion_sound, ball_escape_sound, needle_telegraph_sound, grabber_telegraph_sound, power_bomb_guardian_stage_properties_0x510dba97, power_bomb_guardian_stage_properties_0x0b6c85f7, power_bomb_guardian_stage_properties_0x8b9c92e8, power_bomb_guardian_stage_properties_0xbfaefb37)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x007')  # 55 properties

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
        self.patterned.to_stream(data)
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

        data.write(b'\x95\xe7\xa2\xc2')  # 0x95e7a2c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95e7a2c2))

        data.write(b'v\xba\x1c\x18')  # 0x76ba1c18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x76ba1c18))

        data.write(b'>\xb2\xde5')  # 0x3eb2de35
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3eb2de35))

        data.write(b'\xe5\r\x8d\xd2')  # 0xe50d8dd2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe50d8dd2))

        data.write(b'd\xd4\x82\xd5')  # 0x64d482d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x64d482d5))

        data.write(b'\xc3\xe0\x02\xac')  # 0xc3e002ac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc3e002ac))

        data.write(b'\xd7_\x9c\xf2')  # 0xd75f9cf2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.shot_angle_variance))

        data.write(b'T\x0c\x1f\x87')  # 0x540c1f87
        data.write(b'\x00\x0c')  # size
        self.attack_aim_offset.to_stream(data)

        data.write(b'3\x86\x8c\x8f')  # 0x33868c8f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.tendril_particle_effect))

        data.write(b'5Uz\x83')  # 0x35557a83
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x35557a83))

        data.write(b'#\xbd9C')  # 0x23bd3943
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grabber_out_acceleration))

        data.write(b'\xd9/H]')  # 0xd92f485d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grabber_in_acceleration))

        data.write(b'\xbf\xdd\xab\xd4')  # 0xbfddabd4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbfddabd4))

        data.write(b'b\xbf\xaa5')  # 0x62bfaa35
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x62bfaa35))

        data.write(b'C;^0')  # 0x433b5e30
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grabber_attach_time))

        data.write(b'\xed\x82\xc5j')  # 0xed82c56a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xed82c56a))

        data.write(b'\xe9\x18\xf4@')  # 0xe918f440
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe918f440))

        data.write(b"'1\xadt")  # 0x2731ad74
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.spit_force))

        data.write(b'\x03\xfb-\xd4')  # 0x3fb2dd4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.spit_damage))

        data.write(b'\x95\xad\x88$')  # 0x95ad8824
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grab_damage))

        data.write(b',\xfa\xde,')  # 0x2cfade2c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2cfade2c))

        data.write(b'\xb6\x8eu\xcc')  # 0xb68e75cc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb68e75cc))

        data.write(b'm1&+')  # 0x6d31262b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6d31262b))

        data.write(b'\xb6(\x85Z')  # 0xb628855a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_power_bomb_guardian))

        data.write(b'\x99\x07E\xdd')  # 0x990745dd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.wpsc))

        data.write(b"_<'\xc6")  # 0x5f3c27c6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.power_bomb_projectile_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0, 'di_knock_back_power': 2.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x03\xa7m5')  # 0x3a76d35
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x03a76d35))

        data.write(b'mN\x0fZ')  # 0x6d4e0f5a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6d4e0f5a))

        data.write(b'58\xd4\x9b')  # 0x3538d49b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3538d49b))

        data.write(b'\xe8\x9cw\x07')  # 0xe89c7707
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe89c7707))

        data.write(b's\x8d\x1fQ')  # 0x738d1f51
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x738d1f51))

        data.write(b'\x94\x80\xc6\xd7')  # 0x9480c6d7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x9480c6d7))

        data.write(b'H\xdfA\x82')  # 0x48df4182
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x48df4182))

        data.write(b'\xe3\x94\x82\xad')  # 0xe39482ad
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe39482ad))

        data.write(b'\xdd\x85\x02\xcc')  # 0xdd8502cc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdd8502cc))

        data.write(b'J\xb8\xcf}')  # 0x4ab8cf7d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4ab8cf7d))

        data.write(b'\xf5\xe2\x84\x04')  # 0xf5e28404
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf5e28404))

        data.write(b'\xa8}r\xfc')  # 0xa87d72fc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.grabber_fire_sound))

        data.write(b'\x86a(^')  # 0x8661285e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.grabber_flight_sound))

        data.write(b'A#2:')  # 0x4123323a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.grabber_hit_player_sound))

        data.write(b'M.\xc58')  # 0x4d2ec538
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.grabber_hit_world_sound))

        data.write(b'\xd5\x1c\xa0Q')  # 0xd51ca051
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.grabber_retract_sound))

        data.write(b'd\xe9\x15-')  # 0x64e9152d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x64e9152d))

        data.write(b':\xcd\x0e\xcc')  # 0x3acd0ecc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.morphball_spit_sound))

        data.write(b'\xfe\xb6s\x17')  # 0xfeb67317
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.grabber_explosion_sound))

        data.write(b'\x88\xa2\r\xb0')  # 0x88a20db0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.ball_escape_sound))

        data.write(b'\x95\xc1%\x7f')  # 0x95c1257f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.needle_telegraph_sound))

        data.write(b'&\x90\xe2\x16')  # 0x2690e216
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.grabber_telegraph_sound))

        data.write(b'Q\r\xba\x97')  # 0x510dba97
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.power_bomb_guardian_stage_properties_0x510dba97.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0bl\x85\xf7')  # 0xb6c85f7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.power_bomb_guardian_stage_properties_0x0b6c85f7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8b\x9c\x92\xe8')  # 0x8b9c92e8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.power_bomb_guardian_stage_properties_0x8b9c92e8.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbf\xae\xfb7')  # 0xbfaefb37
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.power_bomb_guardian_stage_properties_0xbfaefb37.to_stream(data)
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
        json_data = typing.cast("SporbBaseJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            unknown_0x95e7a2c2=json_data['unknown_0x95e7a2c2'],
            unknown_0x76ba1c18=json_data['unknown_0x76ba1c18'],
            unknown_0x3eb2de35=json_data['unknown_0x3eb2de35'],
            unknown_0xe50d8dd2=json_data['unknown_0xe50d8dd2'],
            unknown_0x64d482d5=json_data['unknown_0x64d482d5'],
            unknown_0xc3e002ac=json_data['unknown_0xc3e002ac'],
            shot_angle_variance=json_data['shot_angle_variance'],
            attack_aim_offset=Vector.from_json(json_data['attack_aim_offset']),
            tendril_particle_effect=json_data['tendril_particle_effect'],
            unknown_0x35557a83=json_data['unknown_0x35557a83'],
            grabber_out_acceleration=json_data['grabber_out_acceleration'],
            grabber_in_acceleration=json_data['grabber_in_acceleration'],
            unknown_0xbfddabd4=json_data['unknown_0xbfddabd4'],
            unknown_0x62bfaa35=json_data['unknown_0x62bfaa35'],
            grabber_attach_time=json_data['grabber_attach_time'],
            unknown_0xed82c56a=json_data['unknown_0xed82c56a'],
            unknown_0xe918f440=json_data['unknown_0xe918f440'],
            spit_force=json_data['spit_force'],
            spit_damage=json_data['spit_damage'],
            grab_damage=json_data['grab_damage'],
            unknown_0x2cfade2c=json_data['unknown_0x2cfade2c'],
            unknown_0xb68e75cc=json_data['unknown_0xb68e75cc'],
            unknown_0x6d31262b=json_data['unknown_0x6d31262b'],
            is_power_bomb_guardian=json_data['is_power_bomb_guardian'],
            wpsc=json_data['wpsc'],
            power_bomb_projectile_damage=DamageInfo.from_json(json_data['power_bomb_projectile_damage']),
            unknown_0x03a76d35=json_data['unknown_0x03a76d35'],
            unknown_0x6d4e0f5a=json_data['unknown_0x6d4e0f5a'],
            unknown_0x3538d49b=json_data['unknown_0x3538d49b'],
            unknown_0xe89c7707=json_data['unknown_0xe89c7707'],
            unknown_0x738d1f51=json_data['unknown_0x738d1f51'],
            sound_0x9480c6d7=json_data['sound_0x9480c6d7'],
            unknown_0x48df4182=json_data['unknown_0x48df4182'],
            unknown_0xe39482ad=json_data['unknown_0xe39482ad'],
            unknown_0xdd8502cc=json_data['unknown_0xdd8502cc'],
            unknown_0x4ab8cf7d=json_data['unknown_0x4ab8cf7d'],
            unknown_0xf5e28404=json_data['unknown_0xf5e28404'],
            grabber_fire_sound=json_data['grabber_fire_sound'],
            grabber_flight_sound=json_data['grabber_flight_sound'],
            grabber_hit_player_sound=json_data['grabber_hit_player_sound'],
            grabber_hit_world_sound=json_data['grabber_hit_world_sound'],
            grabber_retract_sound=json_data['grabber_retract_sound'],
            sound_0x64e9152d=json_data['sound_0x64e9152d'],
            morphball_spit_sound=json_data['morphball_spit_sound'],
            grabber_explosion_sound=json_data['grabber_explosion_sound'],
            ball_escape_sound=json_data['ball_escape_sound'],
            needle_telegraph_sound=json_data['needle_telegraph_sound'],
            grabber_telegraph_sound=json_data['grabber_telegraph_sound'],
            power_bomb_guardian_stage_properties_0x510dba97=PowerBombGuardianStageProperties.from_json(json_data['power_bomb_guardian_stage_properties_0x510dba97']),
            power_bomb_guardian_stage_properties_0x0b6c85f7=PowerBombGuardianStageProperties.from_json(json_data['power_bomb_guardian_stage_properties_0x0b6c85f7']),
            power_bomb_guardian_stage_properties_0x8b9c92e8=PowerBombGuardianStageProperties.from_json(json_data['power_bomb_guardian_stage_properties_0x8b9c92e8']),
            power_bomb_guardian_stage_properties_0xbfaefb37=PowerBombGuardianStageProperties.from_json(json_data['power_bomb_guardian_stage_properties_0xbfaefb37']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'unknown_0x95e7a2c2': self.unknown_0x95e7a2c2,
            'unknown_0x76ba1c18': self.unknown_0x76ba1c18,
            'unknown_0x3eb2de35': self.unknown_0x3eb2de35,
            'unknown_0xe50d8dd2': self.unknown_0xe50d8dd2,
            'unknown_0x64d482d5': self.unknown_0x64d482d5,
            'unknown_0xc3e002ac': self.unknown_0xc3e002ac,
            'shot_angle_variance': self.shot_angle_variance,
            'attack_aim_offset': self.attack_aim_offset.to_json(),
            'tendril_particle_effect': self.tendril_particle_effect,
            'unknown_0x35557a83': self.unknown_0x35557a83,
            'grabber_out_acceleration': self.grabber_out_acceleration,
            'grabber_in_acceleration': self.grabber_in_acceleration,
            'unknown_0xbfddabd4': self.unknown_0xbfddabd4,
            'unknown_0x62bfaa35': self.unknown_0x62bfaa35,
            'grabber_attach_time': self.grabber_attach_time,
            'unknown_0xed82c56a': self.unknown_0xed82c56a,
            'unknown_0xe918f440': self.unknown_0xe918f440,
            'spit_force': self.spit_force,
            'spit_damage': self.spit_damage,
            'grab_damage': self.grab_damage,
            'unknown_0x2cfade2c': self.unknown_0x2cfade2c,
            'unknown_0xb68e75cc': self.unknown_0xb68e75cc,
            'unknown_0x6d31262b': self.unknown_0x6d31262b,
            'is_power_bomb_guardian': self.is_power_bomb_guardian,
            'wpsc': self.wpsc,
            'power_bomb_projectile_damage': self.power_bomb_projectile_damage.to_json(),
            'unknown_0x03a76d35': self.unknown_0x03a76d35,
            'unknown_0x6d4e0f5a': self.unknown_0x6d4e0f5a,
            'unknown_0x3538d49b': self.unknown_0x3538d49b,
            'unknown_0xe89c7707': self.unknown_0xe89c7707,
            'unknown_0x738d1f51': self.unknown_0x738d1f51,
            'sound_0x9480c6d7': self.sound_0x9480c6d7,
            'unknown_0x48df4182': self.unknown_0x48df4182,
            'unknown_0xe39482ad': self.unknown_0xe39482ad,
            'unknown_0xdd8502cc': self.unknown_0xdd8502cc,
            'unknown_0x4ab8cf7d': self.unknown_0x4ab8cf7d,
            'unknown_0xf5e28404': self.unknown_0xf5e28404,
            'grabber_fire_sound': self.grabber_fire_sound,
            'grabber_flight_sound': self.grabber_flight_sound,
            'grabber_hit_player_sound': self.grabber_hit_player_sound,
            'grabber_hit_world_sound': self.grabber_hit_world_sound,
            'grabber_retract_sound': self.grabber_retract_sound,
            'sound_0x64e9152d': self.sound_0x64e9152d,
            'morphball_spit_sound': self.morphball_spit_sound,
            'grabber_explosion_sound': self.grabber_explosion_sound,
            'ball_escape_sound': self.ball_escape_sound,
            'needle_telegraph_sound': self.needle_telegraph_sound,
            'grabber_telegraph_sound': self.grabber_telegraph_sound,
            'power_bomb_guardian_stage_properties_0x510dba97': self.power_bomb_guardian_stage_properties_0x510dba97.to_json(),
            'power_bomb_guardian_stage_properties_0x0b6c85f7': self.power_bomb_guardian_stage_properties_0x0b6c85f7.to_json(),
            'power_bomb_guardian_stage_properties_0x8b9c92e8': self.power_bomb_guardian_stage_properties_0x8b9c92e8.to_json(),
            'power_bomb_guardian_stage_properties_0xbfaefb37': self.power_bomb_guardian_stage_properties_0xbfaefb37.to_json(),
        }

    def _dependencies_for_tendril_particle_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.tendril_particle_effect)

    def _dependencies_for_wpsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc)

    def _dependencies_for_grabber_fire_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.grabber_fire_sound)

    def _dependencies_for_grabber_hit_player_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.grabber_hit_player_sound)

    def _dependencies_for_grabber_hit_world_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.grabber_hit_world_sound)

    def _dependencies_for_grabber_retract_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.grabber_retract_sound)

    def _dependencies_for_sound_0x64e9152d(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x64e9152d)

    def _dependencies_for_morphball_spit_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.morphball_spit_sound)

    def _dependencies_for_grabber_explosion_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.grabber_explosion_sound)

    def _dependencies_for_ball_escape_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.ball_escape_sound)

    def _dependencies_for_needle_telegraph_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.needle_telegraph_sound)

    def _dependencies_for_grabber_telegraph_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.grabber_telegraph_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self._dependencies_for_tendril_particle_effect, "tendril_particle_effect", "AssetId"),
            (self._dependencies_for_wpsc, "wpsc", "AssetId"),
            (self.power_bomb_projectile_damage.dependencies_for, "power_bomb_projectile_damage", "DamageInfo"),
            (self._dependencies_for_grabber_fire_sound, "grabber_fire_sound", "int"),
            (self._dependencies_for_grabber_hit_player_sound, "grabber_hit_player_sound", "int"),
            (self._dependencies_for_grabber_hit_world_sound, "grabber_hit_world_sound", "int"),
            (self._dependencies_for_grabber_retract_sound, "grabber_retract_sound", "int"),
            (self._dependencies_for_sound_0x64e9152d, "sound_0x64e9152d", "int"),
            (self._dependencies_for_morphball_spit_sound, "morphball_spit_sound", "int"),
            (self._dependencies_for_grabber_explosion_sound, "grabber_explosion_sound", "int"),
            (self._dependencies_for_ball_escape_sound, "ball_escape_sound", "int"),
            (self._dependencies_for_needle_telegraph_sound, "needle_telegraph_sound", "int"),
            (self._dependencies_for_grabber_telegraph_sound, "grabber_telegraph_sound", "int"),
            (self.power_bomb_guardian_stage_properties_0x510dba97.dependencies_for, "power_bomb_guardian_stage_properties_0x510dba97", "PowerBombGuardianStageProperties"),
            (self.power_bomb_guardian_stage_properties_0x0b6c85f7.dependencies_for, "power_bomb_guardian_stage_properties_0x0b6c85f7", "PowerBombGuardianStageProperties"),
            (self.power_bomb_guardian_stage_properties_0x8b9c92e8.dependencies_for, "power_bomb_guardian_stage_properties_0x8b9c92e8", "PowerBombGuardianStageProperties"),
            (self.power_bomb_guardian_stage_properties_0xbfaefb37.dependencies_for, "power_bomb_guardian_stage_properties_0xbfaefb37", "PowerBombGuardianStageProperties"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for SporbBase.{field_name} ({field_type}): {e}"
                )


def _decode_unknown_0x95e7a2c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x76ba1c18(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3eb2de35(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe50d8dd2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x64d482d5(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xc3e002ac(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_shot_angle_variance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_aim_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_tendril_particle_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x35557a83(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grabber_out_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grabber_in_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbfddabd4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x62bfaa35(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grabber_attach_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xed82c56a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe918f440(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_spit_force(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_spit_damage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grab_damage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2cfade2c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb68e75cc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6d31262b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_is_power_bomb_guardian(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_wpsc(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_power_bomb_projectile_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0, 'di_knock_back_power': 2.0})


def _decode_unknown_0x03a76d35(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6d4e0f5a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3538d49b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe89c7707(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x738d1f51(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_0x9480c6d7(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x48df4182(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe39482ad(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdd8502cc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4ab8cf7d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf5e28404(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grabber_fire_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_grabber_flight_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_grabber_hit_player_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_grabber_hit_world_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_grabber_retract_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x64e9152d(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_morphball_spit_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_grabber_explosion_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_ball_escape_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_needle_telegraph_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_grabber_telegraph_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', PatternedAITypedef.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x95e7a2c2: ('unknown_0x95e7a2c2', _decode_unknown_0x95e7a2c2),
    0x76ba1c18: ('unknown_0x76ba1c18', _decode_unknown_0x76ba1c18),
    0x3eb2de35: ('unknown_0x3eb2de35', _decode_unknown_0x3eb2de35),
    0xe50d8dd2: ('unknown_0xe50d8dd2', _decode_unknown_0xe50d8dd2),
    0x64d482d5: ('unknown_0x64d482d5', _decode_unknown_0x64d482d5),
    0xc3e002ac: ('unknown_0xc3e002ac', _decode_unknown_0xc3e002ac),
    0xd75f9cf2: ('shot_angle_variance', _decode_shot_angle_variance),
    0x540c1f87: ('attack_aim_offset', _decode_attack_aim_offset),
    0x33868c8f: ('tendril_particle_effect', _decode_tendril_particle_effect),
    0x35557a83: ('unknown_0x35557a83', _decode_unknown_0x35557a83),
    0x23bd3943: ('grabber_out_acceleration', _decode_grabber_out_acceleration),
    0xd92f485d: ('grabber_in_acceleration', _decode_grabber_in_acceleration),
    0xbfddabd4: ('unknown_0xbfddabd4', _decode_unknown_0xbfddabd4),
    0x62bfaa35: ('unknown_0x62bfaa35', _decode_unknown_0x62bfaa35),
    0x433b5e30: ('grabber_attach_time', _decode_grabber_attach_time),
    0xed82c56a: ('unknown_0xed82c56a', _decode_unknown_0xed82c56a),
    0xe918f440: ('unknown_0xe918f440', _decode_unknown_0xe918f440),
    0x2731ad74: ('spit_force', _decode_spit_force),
    0x3fb2dd4: ('spit_damage', _decode_spit_damage),
    0x95ad8824: ('grab_damage', _decode_grab_damage),
    0x2cfade2c: ('unknown_0x2cfade2c', _decode_unknown_0x2cfade2c),
    0xb68e75cc: ('unknown_0xb68e75cc', _decode_unknown_0xb68e75cc),
    0x6d31262b: ('unknown_0x6d31262b', _decode_unknown_0x6d31262b),
    0xb628855a: ('is_power_bomb_guardian', _decode_is_power_bomb_guardian),
    0x990745dd: ('wpsc', _decode_wpsc),
    0x5f3c27c6: ('power_bomb_projectile_damage', _decode_power_bomb_projectile_damage),
    0x3a76d35: ('unknown_0x03a76d35', _decode_unknown_0x03a76d35),
    0x6d4e0f5a: ('unknown_0x6d4e0f5a', _decode_unknown_0x6d4e0f5a),
    0x3538d49b: ('unknown_0x3538d49b', _decode_unknown_0x3538d49b),
    0xe89c7707: ('unknown_0xe89c7707', _decode_unknown_0xe89c7707),
    0x738d1f51: ('unknown_0x738d1f51', _decode_unknown_0x738d1f51),
    0x9480c6d7: ('sound_0x9480c6d7', _decode_sound_0x9480c6d7),
    0x48df4182: ('unknown_0x48df4182', _decode_unknown_0x48df4182),
    0xe39482ad: ('unknown_0xe39482ad', _decode_unknown_0xe39482ad),
    0xdd8502cc: ('unknown_0xdd8502cc', _decode_unknown_0xdd8502cc),
    0x4ab8cf7d: ('unknown_0x4ab8cf7d', _decode_unknown_0x4ab8cf7d),
    0xf5e28404: ('unknown_0xf5e28404', _decode_unknown_0xf5e28404),
    0xa87d72fc: ('grabber_fire_sound', _decode_grabber_fire_sound),
    0x8661285e: ('grabber_flight_sound', _decode_grabber_flight_sound),
    0x4123323a: ('grabber_hit_player_sound', _decode_grabber_hit_player_sound),
    0x4d2ec538: ('grabber_hit_world_sound', _decode_grabber_hit_world_sound),
    0xd51ca051: ('grabber_retract_sound', _decode_grabber_retract_sound),
    0x64e9152d: ('sound_0x64e9152d', _decode_sound_0x64e9152d),
    0x3acd0ecc: ('morphball_spit_sound', _decode_morphball_spit_sound),
    0xfeb67317: ('grabber_explosion_sound', _decode_grabber_explosion_sound),
    0x88a20db0: ('ball_escape_sound', _decode_ball_escape_sound),
    0x95c1257f: ('needle_telegraph_sound', _decode_needle_telegraph_sound),
    0x2690e216: ('grabber_telegraph_sound', _decode_grabber_telegraph_sound),
    0x510dba97: ('power_bomb_guardian_stage_properties_0x510dba97', PowerBombGuardianStageProperties.from_stream),
    0xb6c85f7: ('power_bomb_guardian_stage_properties_0x0b6c85f7', PowerBombGuardianStageProperties.from_stream),
    0x8b9c92e8: ('power_bomb_guardian_stage_properties_0x8b9c92e8', PowerBombGuardianStageProperties.from_stream),
    0xbfaefb37: ('power_bomb_guardian_stage_properties_0xbfaefb37', PowerBombGuardianStageProperties.from_stream),
}
