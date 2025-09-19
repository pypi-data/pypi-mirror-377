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
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class GunTurretBaseJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        attack_damage: json_util.JsonObject
        hurt_sleep_delay: float
        gun_aim_turn_speed: float
        unknown_0xc80bc7c5: float
        unknown_0x95e7a2c2: float
        unknown_0x76ba1c18: float
        unknown_0x3eb2de35: float
        unknown_0xe50d8dd2: float
        unknown_0x64d482d5: int
        unknown_0xc3e002ac: int
        unknown_0x5ade66a9: float
        unknown_0x8dd2c329: float
        unknown_0xfc036e93: float
        shot_angle_variance: float
        patrol_delay: float
        withdraw_delay: float
        unknown_0x8a35b1ea: float
        unknown_0xd49bec5a: float
        unknown_0x80ce481a: float
        attack_delay: float
        detection_height_up: float
        detection_height_down: float
        attack_leash_time: float
        gun_respawns: bool
        unknown_0x5cf12e9a: bool
        unknown_0x479d8dc4: bool
        is_pirate_turret: bool
        crsc: int
        pirate_projectile_effect: int
        always_ff: int
        sound_0x23316032: int
        sound_0xa3b39766: int
        lock_on_sound: int
        gun_pan_sound: int
        sound_0xf57880ec: int
        sound_0x99fe97f6: int
        sound_0xa2714856: int
        sound_0xd58a2fa7: int
        sound_0xb381355a: int
        sound_0x00628c84: int
        sound_0x40533b8d: int
        sound_0x613cafd8: int
        pole_sparks_sound: int
        max_audible_distance: float
        unknown_0xd2986c43: float
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
    

@dataclasses.dataclass()
class GunTurretBase(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    attack_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x66dcaacb, original_name='AttackDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    hurt_sleep_delay: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9b5a4744, original_name='HurtSleepDelay'
        ),
    })
    gun_aim_turn_speed: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x30967020, original_name='GunAimTurnSpeed'
        ),
    })
    unknown_0xc80bc7c5: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc80bc7c5, original_name='Unknown'
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
    unknown_0x5ade66a9: float = dataclasses.field(default=85.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5ade66a9, original_name='Unknown'
        ),
    })
    unknown_0x8dd2c329: float = dataclasses.field(default=-45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8dd2c329, original_name='Unknown'
        ),
    })
    unknown_0xfc036e93: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfc036e93, original_name='Unknown'
        ),
    })
    shot_angle_variance: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd75f9cf2, original_name='ShotAngleVariance'
        ),
    })
    patrol_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x013184c7, original_name='PatrolDelay'
        ),
    })
    withdraw_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5aea7978, original_name='WithdrawDelay'
        ),
    })
    unknown_0x8a35b1ea: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8a35b1ea, original_name='Unknown'
        ),
    })
    unknown_0xd49bec5a: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd49bec5a, original_name='Unknown'
        ),
    })
    unknown_0x80ce481a: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x80ce481a, original_name='Unknown'
        ),
    })
    attack_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1b67981a, original_name='AttackDelay'
        ),
    })
    detection_height_up: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa115a5d6, original_name='DetectionHeightUp'
        ),
    })
    detection_height_down: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2718ced1, original_name='DetectionHeightDown'
        ),
    })
    attack_leash_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb881b8b3, original_name='AttackLeashTime'
        ),
    })
    gun_respawns: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x32d6d325, original_name='GunRespawns'
        ),
    })
    unknown_0x5cf12e9a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5cf12e9a, original_name='Unknown'
        ),
    })
    unknown_0x479d8dc4: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x479d8dc4, original_name='Unknown'
        ),
    })
    is_pirate_turret: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x701d65cd, original_name='IsPirateTurret'
        ),
    })
    crsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CRSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa33d1c6d, original_name='CRSC'
        ),
    })
    pirate_projectile_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2d1c5515, original_name='PirateProjectileEffect'
        ),
    })
    always_ff: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x45b71390, original_name='Always FF'
        ),
    })
    sound_0x23316032: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x23316032, original_name='Sound'
        ),
    })
    sound_0xa3b39766: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xa3b39766, original_name='Sound'
        ),
    })
    lock_on_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x9674eff1, original_name='LockOnSound'
        ),
    })
    gun_pan_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x49880c24, original_name='GunPanSound'
        ),
    })
    sound_0xf57880ec: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xf57880ec, original_name='Sound'
        ),
    })
    sound_0x99fe97f6: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x99fe97f6, original_name='Sound'
        ),
    })
    sound_0xa2714856: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xa2714856, original_name='Sound'
        ),
    })
    sound_0xd58a2fa7: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xd58a2fa7, original_name='Sound'
        ),
    })
    sound_0xb381355a: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xb381355a, original_name='Sound'
        ),
    })
    sound_0x00628c84: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00628c84, original_name='Sound'
        ),
    })
    sound_0x40533b8d: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x40533b8d, original_name='Sound'
        ),
    })
    sound_0x613cafd8: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x613cafd8, original_name='Sound'
        ),
    })
    pole_sparks_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x20c03692, original_name='PoleSparksSound'
        ),
    })
    max_audible_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x214e48a0, original_name='MaxAudibleDistance'
        ),
    })
    unknown_0xd2986c43: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd2986c43, original_name='Unknown'
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

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'GNTB'

    @classmethod
    def modules(cls) -> list[str]:
        return ['GunTurret.rel']

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
        if property_count != 48:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66dcaacb
        attack_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9b5a4744
        hurt_sleep_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x30967020
        gun_aim_turn_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc80bc7c5
        unknown_0xc80bc7c5 = struct.unpack('>f', data.read(4))[0]
    
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
        assert property_id == 0x5ade66a9
        unknown_0x5ade66a9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8dd2c329
        unknown_0x8dd2c329 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfc036e93
        unknown_0xfc036e93 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd75f9cf2
        shot_angle_variance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x013184c7
        patrol_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5aea7978
        withdraw_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a35b1ea
        unknown_0x8a35b1ea = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd49bec5a
        unknown_0xd49bec5a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80ce481a
        unknown_0x80ce481a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b67981a
        attack_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa115a5d6
        detection_height_up = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2718ced1
        detection_height_down = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb881b8b3
        attack_leash_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32d6d325
        gun_respawns = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5cf12e9a
        unknown_0x5cf12e9a = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x479d8dc4
        unknown_0x479d8dc4 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x701d65cd
        is_pirate_turret = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa33d1c6d
        crsc = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2d1c5515
        pirate_projectile_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x45b71390
        always_ff = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x23316032
        sound_0x23316032 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa3b39766
        sound_0xa3b39766 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9674eff1
        lock_on_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49880c24
        gun_pan_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf57880ec
        sound_0xf57880ec = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x99fe97f6
        sound_0x99fe97f6 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa2714856
        sound_0xa2714856 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd58a2fa7
        sound_0xd58a2fa7 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb381355a
        sound_0xb381355a = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x00628c84
        sound_0x00628c84 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x40533b8d
        sound_0x40533b8d = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x613cafd8
        sound_0x613cafd8 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x20c03692
        pole_sparks_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x214e48a0
        max_audible_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd2986c43
        unknown_0xd2986c43 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        return cls(editor_properties, attack_damage, hurt_sleep_delay, gun_aim_turn_speed, unknown_0xc80bc7c5, unknown_0x95e7a2c2, unknown_0x76ba1c18, unknown_0x3eb2de35, unknown_0xe50d8dd2, unknown_0x64d482d5, unknown_0xc3e002ac, unknown_0x5ade66a9, unknown_0x8dd2c329, unknown_0xfc036e93, shot_angle_variance, patrol_delay, withdraw_delay, unknown_0x8a35b1ea, unknown_0xd49bec5a, unknown_0x80ce481a, attack_delay, detection_height_up, detection_height_down, attack_leash_time, gun_respawns, unknown_0x5cf12e9a, unknown_0x479d8dc4, is_pirate_turret, crsc, pirate_projectile_effect, always_ff, sound_0x23316032, sound_0xa3b39766, lock_on_sound, gun_pan_sound, sound_0xf57880ec, sound_0x99fe97f6, sound_0xa2714856, sound_0xd58a2fa7, sound_0xb381355a, sound_0x00628c84, sound_0x40533b8d, sound_0x613cafd8, pole_sparks_sound, max_audible_distance, unknown_0xd2986c43, patterned, actor_information)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x000')  # 48 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'f\xdc\xaa\xcb')  # 0x66dcaacb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9bZGD')  # 0x9b5a4744
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hurt_sleep_delay))

        data.write(b'0\x96p ')  # 0x30967020
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.gun_aim_turn_speed))

        data.write(b'\xc8\x0b\xc7\xc5')  # 0xc80bc7c5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc80bc7c5))

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

        data.write(b'Z\xdef\xa9')  # 0x5ade66a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5ade66a9))

        data.write(b'\x8d\xd2\xc3)')  # 0x8dd2c329
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8dd2c329))

        data.write(b'\xfc\x03n\x93')  # 0xfc036e93
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfc036e93))

        data.write(b'\xd7_\x9c\xf2')  # 0xd75f9cf2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.shot_angle_variance))

        data.write(b'\x011\x84\xc7')  # 0x13184c7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.patrol_delay))

        data.write(b'Z\xeayx')  # 0x5aea7978
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.withdraw_delay))

        data.write(b'\x8a5\xb1\xea')  # 0x8a35b1ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8a35b1ea))

        data.write(b'\xd4\x9b\xecZ')  # 0xd49bec5a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd49bec5a))

        data.write(b'\x80\xceH\x1a')  # 0x80ce481a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x80ce481a))

        data.write(b'\x1bg\x98\x1a')  # 0x1b67981a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_delay))

        data.write(b'\xa1\x15\xa5\xd6')  # 0xa115a5d6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detection_height_up))

        data.write(b"'\x18\xce\xd1")  # 0x2718ced1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detection_height_down))

        data.write(b'\xb8\x81\xb8\xb3')  # 0xb881b8b3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_leash_time))

        data.write(b'2\xd6\xd3%')  # 0x32d6d325
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.gun_respawns))

        data.write(b'\\\xf1.\x9a')  # 0x5cf12e9a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x5cf12e9a))

        data.write(b'G\x9d\x8d\xc4')  # 0x479d8dc4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x479d8dc4))

        data.write(b'p\x1de\xcd')  # 0x701d65cd
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_pirate_turret))

        data.write(b'\xa3=\x1cm')  # 0xa33d1c6d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.crsc))

        data.write(b'-\x1cU\x15')  # 0x2d1c5515
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.pirate_projectile_effect))

        data.write(b'E\xb7\x13\x90')  # 0x45b71390
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.always_ff))

        data.write(b'#1`2')  # 0x23316032
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x23316032))

        data.write(b'\xa3\xb3\x97f')  # 0xa3b39766
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0xa3b39766))

        data.write(b'\x96t\xef\xf1')  # 0x9674eff1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.lock_on_sound))

        data.write(b'I\x88\x0c$')  # 0x49880c24
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.gun_pan_sound))

        data.write(b'\xf5x\x80\xec')  # 0xf57880ec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0xf57880ec))

        data.write(b'\x99\xfe\x97\xf6')  # 0x99fe97f6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x99fe97f6))

        data.write(b'\xa2qHV')  # 0xa2714856
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0xa2714856))

        data.write(b'\xd5\x8a/\xa7')  # 0xd58a2fa7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0xd58a2fa7))

        data.write(b'\xb3\x815Z')  # 0xb381355a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0xb381355a))

        data.write(b'\x00b\x8c\x84')  # 0x628c84
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x00628c84))

        data.write(b'@S;\x8d')  # 0x40533b8d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x40533b8d))

        data.write(b'a<\xaf\xd8')  # 0x613cafd8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x613cafd8))

        data.write(b' \xc06\x92')  # 0x20c03692
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.pole_sparks_sound))

        data.write(b'!NH\xa0')  # 0x214e48a0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_audible_distance))

        data.write(b'\xd2\x98lC')  # 0xd2986c43
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd2986c43))

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

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("GunTurretBaseJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            attack_damage=DamageInfo.from_json(json_data['attack_damage']),
            hurt_sleep_delay=json_data['hurt_sleep_delay'],
            gun_aim_turn_speed=json_data['gun_aim_turn_speed'],
            unknown_0xc80bc7c5=json_data['unknown_0xc80bc7c5'],
            unknown_0x95e7a2c2=json_data['unknown_0x95e7a2c2'],
            unknown_0x76ba1c18=json_data['unknown_0x76ba1c18'],
            unknown_0x3eb2de35=json_data['unknown_0x3eb2de35'],
            unknown_0xe50d8dd2=json_data['unknown_0xe50d8dd2'],
            unknown_0x64d482d5=json_data['unknown_0x64d482d5'],
            unknown_0xc3e002ac=json_data['unknown_0xc3e002ac'],
            unknown_0x5ade66a9=json_data['unknown_0x5ade66a9'],
            unknown_0x8dd2c329=json_data['unknown_0x8dd2c329'],
            unknown_0xfc036e93=json_data['unknown_0xfc036e93'],
            shot_angle_variance=json_data['shot_angle_variance'],
            patrol_delay=json_data['patrol_delay'],
            withdraw_delay=json_data['withdraw_delay'],
            unknown_0x8a35b1ea=json_data['unknown_0x8a35b1ea'],
            unknown_0xd49bec5a=json_data['unknown_0xd49bec5a'],
            unknown_0x80ce481a=json_data['unknown_0x80ce481a'],
            attack_delay=json_data['attack_delay'],
            detection_height_up=json_data['detection_height_up'],
            detection_height_down=json_data['detection_height_down'],
            attack_leash_time=json_data['attack_leash_time'],
            gun_respawns=json_data['gun_respawns'],
            unknown_0x5cf12e9a=json_data['unknown_0x5cf12e9a'],
            unknown_0x479d8dc4=json_data['unknown_0x479d8dc4'],
            is_pirate_turret=json_data['is_pirate_turret'],
            crsc=json_data['crsc'],
            pirate_projectile_effect=json_data['pirate_projectile_effect'],
            always_ff=json_data['always_ff'],
            sound_0x23316032=json_data['sound_0x23316032'],
            sound_0xa3b39766=json_data['sound_0xa3b39766'],
            lock_on_sound=json_data['lock_on_sound'],
            gun_pan_sound=json_data['gun_pan_sound'],
            sound_0xf57880ec=json_data['sound_0xf57880ec'],
            sound_0x99fe97f6=json_data['sound_0x99fe97f6'],
            sound_0xa2714856=json_data['sound_0xa2714856'],
            sound_0xd58a2fa7=json_data['sound_0xd58a2fa7'],
            sound_0xb381355a=json_data['sound_0xb381355a'],
            sound_0x00628c84=json_data['sound_0x00628c84'],
            sound_0x40533b8d=json_data['sound_0x40533b8d'],
            sound_0x613cafd8=json_data['sound_0x613cafd8'],
            pole_sparks_sound=json_data['pole_sparks_sound'],
            max_audible_distance=json_data['max_audible_distance'],
            unknown_0xd2986c43=json_data['unknown_0xd2986c43'],
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'attack_damage': self.attack_damage.to_json(),
            'hurt_sleep_delay': self.hurt_sleep_delay,
            'gun_aim_turn_speed': self.gun_aim_turn_speed,
            'unknown_0xc80bc7c5': self.unknown_0xc80bc7c5,
            'unknown_0x95e7a2c2': self.unknown_0x95e7a2c2,
            'unknown_0x76ba1c18': self.unknown_0x76ba1c18,
            'unknown_0x3eb2de35': self.unknown_0x3eb2de35,
            'unknown_0xe50d8dd2': self.unknown_0xe50d8dd2,
            'unknown_0x64d482d5': self.unknown_0x64d482d5,
            'unknown_0xc3e002ac': self.unknown_0xc3e002ac,
            'unknown_0x5ade66a9': self.unknown_0x5ade66a9,
            'unknown_0x8dd2c329': self.unknown_0x8dd2c329,
            'unknown_0xfc036e93': self.unknown_0xfc036e93,
            'shot_angle_variance': self.shot_angle_variance,
            'patrol_delay': self.patrol_delay,
            'withdraw_delay': self.withdraw_delay,
            'unknown_0x8a35b1ea': self.unknown_0x8a35b1ea,
            'unknown_0xd49bec5a': self.unknown_0xd49bec5a,
            'unknown_0x80ce481a': self.unknown_0x80ce481a,
            'attack_delay': self.attack_delay,
            'detection_height_up': self.detection_height_up,
            'detection_height_down': self.detection_height_down,
            'attack_leash_time': self.attack_leash_time,
            'gun_respawns': self.gun_respawns,
            'unknown_0x5cf12e9a': self.unknown_0x5cf12e9a,
            'unknown_0x479d8dc4': self.unknown_0x479d8dc4,
            'is_pirate_turret': self.is_pirate_turret,
            'crsc': self.crsc,
            'pirate_projectile_effect': self.pirate_projectile_effect,
            'always_ff': self.always_ff,
            'sound_0x23316032': self.sound_0x23316032,
            'sound_0xa3b39766': self.sound_0xa3b39766,
            'lock_on_sound': self.lock_on_sound,
            'gun_pan_sound': self.gun_pan_sound,
            'sound_0xf57880ec': self.sound_0xf57880ec,
            'sound_0x99fe97f6': self.sound_0x99fe97f6,
            'sound_0xa2714856': self.sound_0xa2714856,
            'sound_0xd58a2fa7': self.sound_0xd58a2fa7,
            'sound_0xb381355a': self.sound_0xb381355a,
            'sound_0x00628c84': self.sound_0x00628c84,
            'sound_0x40533b8d': self.sound_0x40533b8d,
            'sound_0x613cafd8': self.sound_0x613cafd8,
            'pole_sparks_sound': self.pole_sparks_sound,
            'max_audible_distance': self.max_audible_distance,
            'unknown_0xd2986c43': self.unknown_0xd2986c43,
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
        }

    def _dependencies_for_crsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.crsc)

    def _dependencies_for_pirate_projectile_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.pirate_projectile_effect)

    def _dependencies_for_always_ff(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.always_ff)

    def _dependencies_for_sound_0x23316032(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x23316032)

    def _dependencies_for_sound_0xa3b39766(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0xa3b39766)

    def _dependencies_for_lock_on_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.lock_on_sound)

    def _dependencies_for_gun_pan_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.gun_pan_sound)

    def _dependencies_for_sound_0xf57880ec(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0xf57880ec)

    def _dependencies_for_sound_0x99fe97f6(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x99fe97f6)

    def _dependencies_for_sound_0xa2714856(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0xa2714856)

    def _dependencies_for_sound_0xd58a2fa7(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0xd58a2fa7)

    def _dependencies_for_sound_0xb381355a(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0xb381355a)

    def _dependencies_for_sound_0x00628c84(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x00628c84)

    def _dependencies_for_sound_0x40533b8d(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x40533b8d)

    def _dependencies_for_sound_0x613cafd8(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x613cafd8)

    def _dependencies_for_pole_sparks_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.pole_sparks_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.attack_damage.dependencies_for, "attack_damage", "DamageInfo"),
            (self._dependencies_for_crsc, "crsc", "AssetId"),
            (self._dependencies_for_pirate_projectile_effect, "pirate_projectile_effect", "AssetId"),
            (self._dependencies_for_always_ff, "always_ff", "int"),
            (self._dependencies_for_sound_0x23316032, "sound_0x23316032", "int"),
            (self._dependencies_for_sound_0xa3b39766, "sound_0xa3b39766", "int"),
            (self._dependencies_for_lock_on_sound, "lock_on_sound", "int"),
            (self._dependencies_for_gun_pan_sound, "gun_pan_sound", "int"),
            (self._dependencies_for_sound_0xf57880ec, "sound_0xf57880ec", "int"),
            (self._dependencies_for_sound_0x99fe97f6, "sound_0x99fe97f6", "int"),
            (self._dependencies_for_sound_0xa2714856, "sound_0xa2714856", "int"),
            (self._dependencies_for_sound_0xd58a2fa7, "sound_0xd58a2fa7", "int"),
            (self._dependencies_for_sound_0xb381355a, "sound_0xb381355a", "int"),
            (self._dependencies_for_sound_0x00628c84, "sound_0x00628c84", "int"),
            (self._dependencies_for_sound_0x40533b8d, "sound_0x40533b8d", "int"),
            (self._dependencies_for_sound_0x613cafd8, "sound_0x613cafd8", "int"),
            (self._dependencies_for_pole_sparks_sound, "pole_sparks_sound", "int"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for GunTurretBase.{field_name} ({field_type}): {e}"
                )


def _decode_attack_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_hurt_sleep_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_gun_aim_turn_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc80bc7c5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


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


def _decode_unknown_0x5ade66a9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8dd2c329(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfc036e93(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shot_angle_variance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_patrol_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_withdraw_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8a35b1ea(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd49bec5a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x80ce481a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detection_height_up(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detection_height_down(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_leash_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_gun_respawns(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x5cf12e9a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x479d8dc4(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_is_pirate_turret(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_crsc(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_pirate_projectile_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_always_ff(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x23316032(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0xa3b39766(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_lock_on_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_gun_pan_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0xf57880ec(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x99fe97f6(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0xa2714856(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0xd58a2fa7(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0xb381355a(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x00628c84(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x40533b8d(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x613cafd8(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_pole_sparks_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_max_audible_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd2986c43(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x66dcaacb: ('attack_damage', _decode_attack_damage),
    0x9b5a4744: ('hurt_sleep_delay', _decode_hurt_sleep_delay),
    0x30967020: ('gun_aim_turn_speed', _decode_gun_aim_turn_speed),
    0xc80bc7c5: ('unknown_0xc80bc7c5', _decode_unknown_0xc80bc7c5),
    0x95e7a2c2: ('unknown_0x95e7a2c2', _decode_unknown_0x95e7a2c2),
    0x76ba1c18: ('unknown_0x76ba1c18', _decode_unknown_0x76ba1c18),
    0x3eb2de35: ('unknown_0x3eb2de35', _decode_unknown_0x3eb2de35),
    0xe50d8dd2: ('unknown_0xe50d8dd2', _decode_unknown_0xe50d8dd2),
    0x64d482d5: ('unknown_0x64d482d5', _decode_unknown_0x64d482d5),
    0xc3e002ac: ('unknown_0xc3e002ac', _decode_unknown_0xc3e002ac),
    0x5ade66a9: ('unknown_0x5ade66a9', _decode_unknown_0x5ade66a9),
    0x8dd2c329: ('unknown_0x8dd2c329', _decode_unknown_0x8dd2c329),
    0xfc036e93: ('unknown_0xfc036e93', _decode_unknown_0xfc036e93),
    0xd75f9cf2: ('shot_angle_variance', _decode_shot_angle_variance),
    0x13184c7: ('patrol_delay', _decode_patrol_delay),
    0x5aea7978: ('withdraw_delay', _decode_withdraw_delay),
    0x8a35b1ea: ('unknown_0x8a35b1ea', _decode_unknown_0x8a35b1ea),
    0xd49bec5a: ('unknown_0xd49bec5a', _decode_unknown_0xd49bec5a),
    0x80ce481a: ('unknown_0x80ce481a', _decode_unknown_0x80ce481a),
    0x1b67981a: ('attack_delay', _decode_attack_delay),
    0xa115a5d6: ('detection_height_up', _decode_detection_height_up),
    0x2718ced1: ('detection_height_down', _decode_detection_height_down),
    0xb881b8b3: ('attack_leash_time', _decode_attack_leash_time),
    0x32d6d325: ('gun_respawns', _decode_gun_respawns),
    0x5cf12e9a: ('unknown_0x5cf12e9a', _decode_unknown_0x5cf12e9a),
    0x479d8dc4: ('unknown_0x479d8dc4', _decode_unknown_0x479d8dc4),
    0x701d65cd: ('is_pirate_turret', _decode_is_pirate_turret),
    0xa33d1c6d: ('crsc', _decode_crsc),
    0x2d1c5515: ('pirate_projectile_effect', _decode_pirate_projectile_effect),
    0x45b71390: ('always_ff', _decode_always_ff),
    0x23316032: ('sound_0x23316032', _decode_sound_0x23316032),
    0xa3b39766: ('sound_0xa3b39766', _decode_sound_0xa3b39766),
    0x9674eff1: ('lock_on_sound', _decode_lock_on_sound),
    0x49880c24: ('gun_pan_sound', _decode_gun_pan_sound),
    0xf57880ec: ('sound_0xf57880ec', _decode_sound_0xf57880ec),
    0x99fe97f6: ('sound_0x99fe97f6', _decode_sound_0x99fe97f6),
    0xa2714856: ('sound_0xa2714856', _decode_sound_0xa2714856),
    0xd58a2fa7: ('sound_0xd58a2fa7', _decode_sound_0xd58a2fa7),
    0xb381355a: ('sound_0xb381355a', _decode_sound_0xb381355a),
    0x628c84: ('sound_0x00628c84', _decode_sound_0x00628c84),
    0x40533b8d: ('sound_0x40533b8d', _decode_sound_0x40533b8d),
    0x613cafd8: ('sound_0x613cafd8', _decode_sound_0x613cafd8),
    0x20c03692: ('pole_sparks_sound', _decode_pole_sparks_sound),
    0x214e48a0: ('max_audible_distance', _decode_max_audible_distance),
    0xd2986c43: ('unknown_0xd2986c43', _decode_unknown_0xd2986c43),
    0xb3774750: ('patterned', PatternedAITypedef.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
}
