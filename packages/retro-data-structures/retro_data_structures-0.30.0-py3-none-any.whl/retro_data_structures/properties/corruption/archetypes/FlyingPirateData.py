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
from retro_data_structures.properties.corruption.archetypes.Armor import Armor
from retro_data_structures.properties.corruption.archetypes.FlyingPirateHelixMissileData import FlyingPirateHelixMissileData
from retro_data_structures.properties.corruption.archetypes.FlyingPirateStruct import FlyingPirateStruct
from retro_data_structures.properties.corruption.archetypes.JetPack import JetPack
from retro_data_structures.properties.corruption.archetypes.ParticleBlaster import ParticleBlaster
from retro_data_structures.properties.corruption.archetypes.RagDollData import RagDollData
from retro_data_structures.properties.corruption.archetypes.SpacePirateWeaponData import SpacePirateWeaponData
from retro_data_structures.properties.corruption.archetypes.UnknownStruct28 import UnknownStruct28
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class FlyingPirateDataJson(typing_extensions.TypedDict):
        unknown_0xa8b7379d: bool
        unknown_0xf37267ef: bool
        disable_particle_blaster: bool
        disable_weapon_pods: bool
        unknown_0x767f168e: bool
        keep_target_time: float
        unknown_0xd73ec5bc: float
        unknown_0x907f8e96: float
        unknown_0x610c0165: float
        unknown_0x0d2531e7: float
        land_check_time: float
        land_check_chance: float
        flight_check_time: float
        flight_check_chance: float
        left_weapon_pod_model: int
        right_weapon_pod_model: int
        unknown_0x4fa0ea5c: float
        unknown_0x0263834d: float
        flight_max_speed: float
        flight_acceleration: float
        flight_deceleration: float
        flight_turn_speed: float
        flight_hover_height: float
        unknown_0x7bb971f1: float
        rotate_rolling_duration: float
        dip_check_time: float
        dip_chance: float
        dodge_chance: float
        unknown_0xac2b567d: float
        unknown_0x740b661e: float
        attack_run_chance: float
        unknown_0xc02bb7c5: float
        unknown_0x2b15406d: float
        particle_blaster: json_util.JsonObject
        helix_missiles: json_util.JsonObject
        space_pirate_weapon_data: json_util.JsonObject
        flying_pirate_struct_0x3f07905e: json_util.JsonObject
        flying_pirate_struct_0x097203ab: json_util.JsonObject
        flying_pirate_struct_0x4123a3b6: json_util.JsonObject
        armor: json_util.JsonObject
        jet_pack: json_util.JsonObject
        rag_doll: json_util.JsonObject
        is_gandrayda: bool
        unknown_0x516cb29d: bool
        unknown_struct28: json_util.JsonObject
        unknown_0x97f7a52d: float
    

@dataclasses.dataclass()
class FlyingPirateData(BaseProperty):
    unknown_0xa8b7379d: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa8b7379d, original_name='Unknown'
        ),
    })
    unknown_0xf37267ef: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf37267ef, original_name='Unknown'
        ),
    })
    disable_particle_blaster: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf56589a6, original_name='DisableParticleBlaster'
        ),
    })
    disable_weapon_pods: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xcdd1db4f, original_name='DisableWeaponPods'
        ),
    })
    unknown_0x767f168e: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x767f168e, original_name='Unknown'
        ),
    })
    keep_target_time: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x89a5edc8, original_name='KeepTargetTime'
        ),
    })
    unknown_0xd73ec5bc: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd73ec5bc, original_name='Unknown'
        ),
    })
    unknown_0x907f8e96: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x907f8e96, original_name='Unknown'
        ),
    })
    unknown_0x610c0165: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x610c0165, original_name='Unknown'
        ),
    })
    unknown_0x0d2531e7: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d2531e7, original_name='Unknown'
        ),
    })
    land_check_time: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7f7f8028, original_name='LandCheckTime'
        ),
    })
    land_check_chance: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd2046050, original_name='LandCheckChance'
        ),
    })
    flight_check_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2454fb04, original_name='FlightCheckTime'
        ),
    })
    flight_check_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2ce2f861, original_name='FlightCheckChance'
        ),
    })
    left_weapon_pod_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x95c8719d, original_name='LeftWeaponPodModel'
        ),
    })
    right_weapon_pod_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa0705491, original_name='RightWeaponPodModel'
        ),
    })
    unknown_0x4fa0ea5c: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4fa0ea5c, original_name='Unknown'
        ),
    })
    unknown_0x0263834d: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0263834d, original_name='Unknown'
        ),
    })
    flight_max_speed: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd4dec629, original_name='FlightMaxSpeed'
        ),
    })
    flight_acceleration: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a2bb377, original_name='FlightAcceleration'
        ),
    })
    flight_deceleration: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdd14361f, original_name='FlightDeceleration'
        ),
    })
    flight_turn_speed: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6c317b96, original_name='FlightTurnSpeed'
        ),
    })
    flight_hover_height: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7e7afdc2, original_name='FlightHoverHeight'
        ),
    })
    unknown_0x7bb971f1: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7bb971f1, original_name='Unknown'
        ),
    })
    rotate_rolling_duration: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3aae4e77, original_name='RotateRollingDuration'
        ),
    })
    dip_check_time: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9e156b9d, original_name='DipCheckTime'
        ),
    })
    dip_chance: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x357ed28d, original_name='DipChance'
        ),
    })
    dodge_chance: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x47be3298, original_name='DodgeChance'
        ),
    })
    unknown_0xac2b567d: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xac2b567d, original_name='Unknown'
        ),
    })
    unknown_0x740b661e: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x740b661e, original_name='Unknown'
        ),
    })
    attack_run_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc50d5431, original_name='AttackRunChance'
        ),
    })
    unknown_0xc02bb7c5: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc02bb7c5, original_name='Unknown'
        ),
    })
    unknown_0x2b15406d: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2b15406d, original_name='Unknown'
        ),
    })
    particle_blaster: ParticleBlaster = dataclasses.field(default_factory=ParticleBlaster, metadata={
        'reflection': FieldReflection[ParticleBlaster](
            ParticleBlaster, id=0x672b454d, original_name='ParticleBlaster', from_json=ParticleBlaster.from_json, to_json=ParticleBlaster.to_json
        ),
    })
    helix_missiles: FlyingPirateHelixMissileData = dataclasses.field(default_factory=FlyingPirateHelixMissileData, metadata={
        'reflection': FieldReflection[FlyingPirateHelixMissileData](
            FlyingPirateHelixMissileData, id=0x92b304ad, original_name='HelixMissiles', from_json=FlyingPirateHelixMissileData.from_json, to_json=FlyingPirateHelixMissileData.to_json
        ),
    })
    space_pirate_weapon_data: SpacePirateWeaponData = dataclasses.field(default_factory=SpacePirateWeaponData, metadata={
        'reflection': FieldReflection[SpacePirateWeaponData](
            SpacePirateWeaponData, id=0x2263e77f, original_name='SpacePirateWeaponData', from_json=SpacePirateWeaponData.from_json, to_json=SpacePirateWeaponData.to_json
        ),
    })
    flying_pirate_struct_0x3f07905e: FlyingPirateStruct = dataclasses.field(default_factory=FlyingPirateStruct, metadata={
        'reflection': FieldReflection[FlyingPirateStruct](
            FlyingPirateStruct, id=0x3f07905e, original_name='FlyingPirateStruct', from_json=FlyingPirateStruct.from_json, to_json=FlyingPirateStruct.to_json
        ),
    })
    flying_pirate_struct_0x097203ab: FlyingPirateStruct = dataclasses.field(default_factory=FlyingPirateStruct, metadata={
        'reflection': FieldReflection[FlyingPirateStruct](
            FlyingPirateStruct, id=0x097203ab, original_name='FlyingPirateStruct', from_json=FlyingPirateStruct.from_json, to_json=FlyingPirateStruct.to_json
        ),
    })
    flying_pirate_struct_0x4123a3b6: FlyingPirateStruct = dataclasses.field(default_factory=FlyingPirateStruct, metadata={
        'reflection': FieldReflection[FlyingPirateStruct](
            FlyingPirateStruct, id=0x4123a3b6, original_name='FlyingPirateStruct', from_json=FlyingPirateStruct.from_json, to_json=FlyingPirateStruct.to_json
        ),
    })
    armor: Armor = dataclasses.field(default_factory=Armor, metadata={
        'reflection': FieldReflection[Armor](
            Armor, id=0x70b96a25, original_name='Armor', from_json=Armor.from_json, to_json=Armor.to_json
        ),
    })
    jet_pack: JetPack = dataclasses.field(default_factory=JetPack, metadata={
        'reflection': FieldReflection[JetPack](
            JetPack, id=0xfbaa9f01, original_name='JetPack', from_json=JetPack.from_json, to_json=JetPack.to_json
        ),
    })
    rag_doll: RagDollData = dataclasses.field(default_factory=RagDollData, metadata={
        'reflection': FieldReflection[RagDollData](
            RagDollData, id=0xe39738ea, original_name='RagDoll', from_json=RagDollData.from_json, to_json=RagDollData.to_json
        ),
    })
    is_gandrayda: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x531a8c85, original_name='IsGandrayda'
        ),
    })
    unknown_0x516cb29d: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x516cb29d, original_name='Unknown'
        ),
    })
    unknown_struct28: UnknownStruct28 = dataclasses.field(default_factory=UnknownStruct28, metadata={
        'reflection': FieldReflection[UnknownStruct28](
            UnknownStruct28, id=0xf82f61c9, original_name='UnknownStruct28', from_json=UnknownStruct28.from_json, to_json=UnknownStruct28.to_json
        ),
    })
    unknown_0x97f7a52d: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x97f7a52d, original_name='Unknown'
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
        if property_count != 46:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa8b7379d
        unknown_0xa8b7379d = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf37267ef
        unknown_0xf37267ef = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf56589a6
        disable_particle_blaster = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcdd1db4f
        disable_weapon_pods = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x767f168e
        unknown_0x767f168e = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x89a5edc8
        keep_target_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd73ec5bc
        unknown_0xd73ec5bc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x907f8e96
        unknown_0x907f8e96 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x610c0165
        unknown_0x610c0165 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d2531e7
        unknown_0x0d2531e7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f7f8028
        land_check_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd2046050
        land_check_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2454fb04
        flight_check_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ce2f861
        flight_check_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95c8719d
        left_weapon_pod_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa0705491
        right_weapon_pod_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4fa0ea5c
        unknown_0x4fa0ea5c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0263834d
        unknown_0x0263834d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4dec629
        flight_max_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a2bb377
        flight_acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd14361f
        flight_deceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c317b96
        flight_turn_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e7afdc2
        flight_hover_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7bb971f1
        unknown_0x7bb971f1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3aae4e77
        rotate_rolling_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9e156b9d
        dip_check_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x357ed28d
        dip_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47be3298
        dodge_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xac2b567d
        unknown_0xac2b567d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x740b661e
        unknown_0x740b661e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc50d5431
        attack_run_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc02bb7c5
        unknown_0xc02bb7c5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b15406d
        unknown_0x2b15406d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x672b454d
        particle_blaster = ParticleBlaster.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x92b304ad
        helix_missiles = FlyingPirateHelixMissileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2263e77f
        space_pirate_weapon_data = SpacePirateWeaponData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3f07905e
        flying_pirate_struct_0x3f07905e = FlyingPirateStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x097203ab
        flying_pirate_struct_0x097203ab = FlyingPirateStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4123a3b6
        flying_pirate_struct_0x4123a3b6 = FlyingPirateStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x70b96a25
        armor = Armor.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfbaa9f01
        jet_pack = JetPack.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe39738ea
        rag_doll = RagDollData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x531a8c85
        is_gandrayda = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x516cb29d
        unknown_0x516cb29d = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf82f61c9
        unknown_struct28 = UnknownStruct28.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x97f7a52d
        unknown_0x97f7a52d = struct.unpack('>f', data.read(4))[0]
    
        return cls(unknown_0xa8b7379d, unknown_0xf37267ef, disable_particle_blaster, disable_weapon_pods, unknown_0x767f168e, keep_target_time, unknown_0xd73ec5bc, unknown_0x907f8e96, unknown_0x610c0165, unknown_0x0d2531e7, land_check_time, land_check_chance, flight_check_time, flight_check_chance, left_weapon_pod_model, right_weapon_pod_model, unknown_0x4fa0ea5c, unknown_0x0263834d, flight_max_speed, flight_acceleration, flight_deceleration, flight_turn_speed, flight_hover_height, unknown_0x7bb971f1, rotate_rolling_duration, dip_check_time, dip_chance, dodge_chance, unknown_0xac2b567d, unknown_0x740b661e, attack_run_chance, unknown_0xc02bb7c5, unknown_0x2b15406d, particle_blaster, helix_missiles, space_pirate_weapon_data, flying_pirate_struct_0x3f07905e, flying_pirate_struct_0x097203ab, flying_pirate_struct_0x4123a3b6, armor, jet_pack, rag_doll, is_gandrayda, unknown_0x516cb29d, unknown_struct28, unknown_0x97f7a52d)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00.')  # 46 properties

        data.write(b'\xa8\xb77\x9d')  # 0xa8b7379d
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xa8b7379d))

        data.write(b'\xf3rg\xef')  # 0xf37267ef
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xf37267ef))

        data.write(b'\xf5e\x89\xa6')  # 0xf56589a6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.disable_particle_blaster))

        data.write(b'\xcd\xd1\xdbO')  # 0xcdd1db4f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.disable_weapon_pods))

        data.write(b'v\x7f\x16\x8e')  # 0x767f168e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x767f168e))

        data.write(b'\x89\xa5\xed\xc8')  # 0x89a5edc8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.keep_target_time))

        data.write(b'\xd7>\xc5\xbc')  # 0xd73ec5bc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd73ec5bc))

        data.write(b'\x90\x7f\x8e\x96')  # 0x907f8e96
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x907f8e96))

        data.write(b'a\x0c\x01e')  # 0x610c0165
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x610c0165))

        data.write(b'\r%1\xe7')  # 0xd2531e7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0d2531e7))

        data.write(b'\x7f\x7f\x80(')  # 0x7f7f8028
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.land_check_time))

        data.write(b'\xd2\x04`P')  # 0xd2046050
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.land_check_chance))

        data.write(b'$T\xfb\x04')  # 0x2454fb04
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_check_time))

        data.write(b',\xe2\xf8a')  # 0x2ce2f861
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_check_chance))

        data.write(b'\x95\xc8q\x9d')  # 0x95c8719d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.left_weapon_pod_model))

        data.write(b'\xa0pT\x91')  # 0xa0705491
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.right_weapon_pod_model))

        data.write(b'O\xa0\xea\\')  # 0x4fa0ea5c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4fa0ea5c))

        data.write(b'\x02c\x83M')  # 0x263834d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0263834d))

        data.write(b'\xd4\xde\xc6)')  # 0xd4dec629
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_max_speed))

        data.write(b'z+\xb3w')  # 0x7a2bb377
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_acceleration))

        data.write(b'\xdd\x146\x1f')  # 0xdd14361f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_deceleration))

        data.write(b'l1{\x96')  # 0x6c317b96
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_turn_speed))

        data.write(b'~z\xfd\xc2')  # 0x7e7afdc2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_hover_height))

        data.write(b'{\xb9q\xf1')  # 0x7bb971f1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7bb971f1))

        data.write(b':\xaeNw')  # 0x3aae4e77
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.rotate_rolling_duration))

        data.write(b'\x9e\x15k\x9d')  # 0x9e156b9d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dip_check_time))

        data.write(b'5~\xd2\x8d')  # 0x357ed28d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dip_chance))

        data.write(b'G\xbe2\x98')  # 0x47be3298
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_chance))

        data.write(b'\xac+V}')  # 0xac2b567d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xac2b567d))

        data.write(b't\x0bf\x1e')  # 0x740b661e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x740b661e))

        data.write(b'\xc5\rT1')  # 0xc50d5431
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_run_chance))

        data.write(b'\xc0+\xb7\xc5')  # 0xc02bb7c5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc02bb7c5))

        data.write(b'+\x15@m')  # 0x2b15406d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2b15406d))

        data.write(b'g+EM')  # 0x672b454d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.particle_blaster.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x92\xb3\x04\xad')  # 0x92b304ad
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.helix_missiles.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'"c\xe7\x7f')  # 0x2263e77f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.space_pirate_weapon_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'?\x07\x90^')  # 0x3f07905e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flying_pirate_struct_0x3f07905e.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\tr\x03\xab')  # 0x97203ab
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flying_pirate_struct_0x097203ab.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'A#\xa3\xb6')  # 0x4123a3b6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flying_pirate_struct_0x4123a3b6.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'p\xb9j%')  # 0x70b96a25
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.armor.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfb\xaa\x9f\x01')  # 0xfbaa9f01
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.jet_pack.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe3\x978\xea')  # 0xe39738ea
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.rag_doll.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'S\x1a\x8c\x85')  # 0x531a8c85
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_gandrayda))

        data.write(b'Ql\xb2\x9d')  # 0x516cb29d
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x516cb29d))

        data.write(b'\xf8/a\xc9')  # 0xf82f61c9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct28.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x97\xf7\xa5-')  # 0x97f7a52d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x97f7a52d))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("FlyingPirateDataJson", data)
        return cls(
            unknown_0xa8b7379d=json_data['unknown_0xa8b7379d'],
            unknown_0xf37267ef=json_data['unknown_0xf37267ef'],
            disable_particle_blaster=json_data['disable_particle_blaster'],
            disable_weapon_pods=json_data['disable_weapon_pods'],
            unknown_0x767f168e=json_data['unknown_0x767f168e'],
            keep_target_time=json_data['keep_target_time'],
            unknown_0xd73ec5bc=json_data['unknown_0xd73ec5bc'],
            unknown_0x907f8e96=json_data['unknown_0x907f8e96'],
            unknown_0x610c0165=json_data['unknown_0x610c0165'],
            unknown_0x0d2531e7=json_data['unknown_0x0d2531e7'],
            land_check_time=json_data['land_check_time'],
            land_check_chance=json_data['land_check_chance'],
            flight_check_time=json_data['flight_check_time'],
            flight_check_chance=json_data['flight_check_chance'],
            left_weapon_pod_model=json_data['left_weapon_pod_model'],
            right_weapon_pod_model=json_data['right_weapon_pod_model'],
            unknown_0x4fa0ea5c=json_data['unknown_0x4fa0ea5c'],
            unknown_0x0263834d=json_data['unknown_0x0263834d'],
            flight_max_speed=json_data['flight_max_speed'],
            flight_acceleration=json_data['flight_acceleration'],
            flight_deceleration=json_data['flight_deceleration'],
            flight_turn_speed=json_data['flight_turn_speed'],
            flight_hover_height=json_data['flight_hover_height'],
            unknown_0x7bb971f1=json_data['unknown_0x7bb971f1'],
            rotate_rolling_duration=json_data['rotate_rolling_duration'],
            dip_check_time=json_data['dip_check_time'],
            dip_chance=json_data['dip_chance'],
            dodge_chance=json_data['dodge_chance'],
            unknown_0xac2b567d=json_data['unknown_0xac2b567d'],
            unknown_0x740b661e=json_data['unknown_0x740b661e'],
            attack_run_chance=json_data['attack_run_chance'],
            unknown_0xc02bb7c5=json_data['unknown_0xc02bb7c5'],
            unknown_0x2b15406d=json_data['unknown_0x2b15406d'],
            particle_blaster=ParticleBlaster.from_json(json_data['particle_blaster']),
            helix_missiles=FlyingPirateHelixMissileData.from_json(json_data['helix_missiles']),
            space_pirate_weapon_data=SpacePirateWeaponData.from_json(json_data['space_pirate_weapon_data']),
            flying_pirate_struct_0x3f07905e=FlyingPirateStruct.from_json(json_data['flying_pirate_struct_0x3f07905e']),
            flying_pirate_struct_0x097203ab=FlyingPirateStruct.from_json(json_data['flying_pirate_struct_0x097203ab']),
            flying_pirate_struct_0x4123a3b6=FlyingPirateStruct.from_json(json_data['flying_pirate_struct_0x4123a3b6']),
            armor=Armor.from_json(json_data['armor']),
            jet_pack=JetPack.from_json(json_data['jet_pack']),
            rag_doll=RagDollData.from_json(json_data['rag_doll']),
            is_gandrayda=json_data['is_gandrayda'],
            unknown_0x516cb29d=json_data['unknown_0x516cb29d'],
            unknown_struct28=UnknownStruct28.from_json(json_data['unknown_struct28']),
            unknown_0x97f7a52d=json_data['unknown_0x97f7a52d'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xa8b7379d': self.unknown_0xa8b7379d,
            'unknown_0xf37267ef': self.unknown_0xf37267ef,
            'disable_particle_blaster': self.disable_particle_blaster,
            'disable_weapon_pods': self.disable_weapon_pods,
            'unknown_0x767f168e': self.unknown_0x767f168e,
            'keep_target_time': self.keep_target_time,
            'unknown_0xd73ec5bc': self.unknown_0xd73ec5bc,
            'unknown_0x907f8e96': self.unknown_0x907f8e96,
            'unknown_0x610c0165': self.unknown_0x610c0165,
            'unknown_0x0d2531e7': self.unknown_0x0d2531e7,
            'land_check_time': self.land_check_time,
            'land_check_chance': self.land_check_chance,
            'flight_check_time': self.flight_check_time,
            'flight_check_chance': self.flight_check_chance,
            'left_weapon_pod_model': self.left_weapon_pod_model,
            'right_weapon_pod_model': self.right_weapon_pod_model,
            'unknown_0x4fa0ea5c': self.unknown_0x4fa0ea5c,
            'unknown_0x0263834d': self.unknown_0x0263834d,
            'flight_max_speed': self.flight_max_speed,
            'flight_acceleration': self.flight_acceleration,
            'flight_deceleration': self.flight_deceleration,
            'flight_turn_speed': self.flight_turn_speed,
            'flight_hover_height': self.flight_hover_height,
            'unknown_0x7bb971f1': self.unknown_0x7bb971f1,
            'rotate_rolling_duration': self.rotate_rolling_duration,
            'dip_check_time': self.dip_check_time,
            'dip_chance': self.dip_chance,
            'dodge_chance': self.dodge_chance,
            'unknown_0xac2b567d': self.unknown_0xac2b567d,
            'unknown_0x740b661e': self.unknown_0x740b661e,
            'attack_run_chance': self.attack_run_chance,
            'unknown_0xc02bb7c5': self.unknown_0xc02bb7c5,
            'unknown_0x2b15406d': self.unknown_0x2b15406d,
            'particle_blaster': self.particle_blaster.to_json(),
            'helix_missiles': self.helix_missiles.to_json(),
            'space_pirate_weapon_data': self.space_pirate_weapon_data.to_json(),
            'flying_pirate_struct_0x3f07905e': self.flying_pirate_struct_0x3f07905e.to_json(),
            'flying_pirate_struct_0x097203ab': self.flying_pirate_struct_0x097203ab.to_json(),
            'flying_pirate_struct_0x4123a3b6': self.flying_pirate_struct_0x4123a3b6.to_json(),
            'armor': self.armor.to_json(),
            'jet_pack': self.jet_pack.to_json(),
            'rag_doll': self.rag_doll.to_json(),
            'is_gandrayda': self.is_gandrayda,
            'unknown_0x516cb29d': self.unknown_0x516cb29d,
            'unknown_struct28': self.unknown_struct28.to_json(),
            'unknown_0x97f7a52d': self.unknown_0x97f7a52d,
        }


def _decode_unknown_0xa8b7379d(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xf37267ef(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_disable_particle_blaster(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_disable_weapon_pods(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x767f168e(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_keep_target_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd73ec5bc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x907f8e96(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x610c0165(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0d2531e7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_land_check_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_land_check_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_check_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_check_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_left_weapon_pod_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_right_weapon_pod_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x4fa0ea5c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0263834d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_max_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_deceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_turn_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_hover_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7bb971f1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_rotate_rolling_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dip_check_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dip_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dodge_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xac2b567d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x740b661e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_run_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc02bb7c5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2b15406d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_is_gandrayda(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x516cb29d(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x97f7a52d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xa8b7379d: ('unknown_0xa8b7379d', _decode_unknown_0xa8b7379d),
    0xf37267ef: ('unknown_0xf37267ef', _decode_unknown_0xf37267ef),
    0xf56589a6: ('disable_particle_blaster', _decode_disable_particle_blaster),
    0xcdd1db4f: ('disable_weapon_pods', _decode_disable_weapon_pods),
    0x767f168e: ('unknown_0x767f168e', _decode_unknown_0x767f168e),
    0x89a5edc8: ('keep_target_time', _decode_keep_target_time),
    0xd73ec5bc: ('unknown_0xd73ec5bc', _decode_unknown_0xd73ec5bc),
    0x907f8e96: ('unknown_0x907f8e96', _decode_unknown_0x907f8e96),
    0x610c0165: ('unknown_0x610c0165', _decode_unknown_0x610c0165),
    0xd2531e7: ('unknown_0x0d2531e7', _decode_unknown_0x0d2531e7),
    0x7f7f8028: ('land_check_time', _decode_land_check_time),
    0xd2046050: ('land_check_chance', _decode_land_check_chance),
    0x2454fb04: ('flight_check_time', _decode_flight_check_time),
    0x2ce2f861: ('flight_check_chance', _decode_flight_check_chance),
    0x95c8719d: ('left_weapon_pod_model', _decode_left_weapon_pod_model),
    0xa0705491: ('right_weapon_pod_model', _decode_right_weapon_pod_model),
    0x4fa0ea5c: ('unknown_0x4fa0ea5c', _decode_unknown_0x4fa0ea5c),
    0x263834d: ('unknown_0x0263834d', _decode_unknown_0x0263834d),
    0xd4dec629: ('flight_max_speed', _decode_flight_max_speed),
    0x7a2bb377: ('flight_acceleration', _decode_flight_acceleration),
    0xdd14361f: ('flight_deceleration', _decode_flight_deceleration),
    0x6c317b96: ('flight_turn_speed', _decode_flight_turn_speed),
    0x7e7afdc2: ('flight_hover_height', _decode_flight_hover_height),
    0x7bb971f1: ('unknown_0x7bb971f1', _decode_unknown_0x7bb971f1),
    0x3aae4e77: ('rotate_rolling_duration', _decode_rotate_rolling_duration),
    0x9e156b9d: ('dip_check_time', _decode_dip_check_time),
    0x357ed28d: ('dip_chance', _decode_dip_chance),
    0x47be3298: ('dodge_chance', _decode_dodge_chance),
    0xac2b567d: ('unknown_0xac2b567d', _decode_unknown_0xac2b567d),
    0x740b661e: ('unknown_0x740b661e', _decode_unknown_0x740b661e),
    0xc50d5431: ('attack_run_chance', _decode_attack_run_chance),
    0xc02bb7c5: ('unknown_0xc02bb7c5', _decode_unknown_0xc02bb7c5),
    0x2b15406d: ('unknown_0x2b15406d', _decode_unknown_0x2b15406d),
    0x672b454d: ('particle_blaster', ParticleBlaster.from_stream),
    0x92b304ad: ('helix_missiles', FlyingPirateHelixMissileData.from_stream),
    0x2263e77f: ('space_pirate_weapon_data', SpacePirateWeaponData.from_stream),
    0x3f07905e: ('flying_pirate_struct_0x3f07905e', FlyingPirateStruct.from_stream),
    0x97203ab: ('flying_pirate_struct_0x097203ab', FlyingPirateStruct.from_stream),
    0x4123a3b6: ('flying_pirate_struct_0x4123a3b6', FlyingPirateStruct.from_stream),
    0x70b96a25: ('armor', Armor.from_stream),
    0xfbaa9f01: ('jet_pack', JetPack.from_stream),
    0xe39738ea: ('rag_doll', RagDollData.from_stream),
    0x531a8c85: ('is_gandrayda', _decode_is_gandrayda),
    0x516cb29d: ('unknown_0x516cb29d', _decode_unknown_0x516cb29d),
    0xf82f61c9: ('unknown_struct28', UnknownStruct28.from_stream),
    0x97f7a52d: ('unknown_0x97f7a52d', _decode_unknown_0x97f7a52d),
}
