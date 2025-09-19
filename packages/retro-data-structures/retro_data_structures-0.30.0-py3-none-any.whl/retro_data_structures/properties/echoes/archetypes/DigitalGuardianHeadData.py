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
from retro_data_structures.properties.echoes.archetypes.AudioPlaybackParms import AudioPlaybackParms
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.DigitalGuardianHeadStruct import DigitalGuardianHeadStruct
from retro_data_structures.properties.echoes.archetypes.EchoParameters import EchoParameters
from retro_data_structures.properties.echoes.archetypes.PlasmaBeamInfo import PlasmaBeamInfo
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DigitalGuardianHeadDataJson(typing_extensions.TypedDict):
        scannable_info_shield_head: int
        scannable_info_stunned_head: int
        scannable_info_final_head: int
        head_armor: int
        max_turn_speed: float
        max_linear_velocity: float
        unknown_0xe7de8b82: float
        unknown_0x96e18283: float
        unknown_0xf77138d5: float
        unknown_0x8a83a097: float
        unknown_0xd919fb13: float
        audio_playback_parms_0x0a693a04: json_util.JsonObject
        unknown_0x1cc6d870: float
        part_0x5ff0b26c: int
        audio_playback_parms_0x50baee63: json_util.JsonObject
        audio_playback_parms_0xa5e1ec03: json_util.JsonObject
        audio_playback_parms_0x8d6053cb: json_util.JsonObject
        part_0xc91ef399: int
        unknown_0x7d3d44af: float
        echo_targets: int
        part_0x342ae844: int
        explode_energy_stuff: int
        audio_playback_parms_0x76eedd2a: json_util.JsonObject
        audio_playback_parms_0xa5ecbe17: json_util.JsonObject
        audio_playback_parms_0xb1fc705f: json_util.JsonObject
        audio_playback_parms_0x2bc2677a: json_util.JsonObject
        audio_playback_parms_0x7f5b82b2: json_util.JsonObject
        echo_parameters: json_util.JsonObject
        unknown_0x8317610f: float
        part_0x321c97a9: int
        audio_playback_parms_0xd5cc7e71: json_util.JsonObject
        audio_playback_parms_0xa62c0ea7: json_util.JsonObject
        audio_playback_parms_0xfd9f5486: json_util.JsonObject
        annihilator_pulse: int
        annihilator_pulse_damage: json_util.JsonObject
        annihilator_charge: int
        annihilator_charge_damage: json_util.JsonObject
        unknown_0xff7688bf: float
        unknown_0x12ebb390: int
        frme: int
        plasma_beam_info: json_util.JsonObject
        lock_on_missiles: int
        lock_on_missiles_damage: json_util.JsonObject
        machine_gun: int
        machine_gun_damage: json_util.JsonObject
        sound_machine_gun: json_util.JsonObject
        unknown_0x4ab23ffe: float
        unknown_0x81a8474f: float
        unknown_0x71c406ac: float
        unknown_0xe5bc88b7: float
        digital_guardian_head_struct_0x8f6732ea: json_util.JsonObject
        digital_guardian_head_struct_0x8e128141: json_util.JsonObject
        digital_guardian_head_struct_0xea54b390: json_util.JsonObject
        digital_guardian_head_struct_0xbbd3e7a7: json_util.JsonObject
        digital_guardian_head_struct_0x2dd88764: json_util.JsonObject
        digital_guardian_head_struct_0x48b46e55: json_util.JsonObject
        bomb_pit_vulnerability: json_util.JsonObject
        echo_target_vulnerability: json_util.JsonObject
    

@dataclasses.dataclass()
class DigitalGuardianHeadData(BaseProperty):
    scannable_info_shield_head: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4eaf47d7, original_name='ScannableInfoShieldHead'
        ),
    })
    scannable_info_stunned_head: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x390f3677, original_name='ScannableInfoStunnedHead'
        ),
    })
    scannable_info_final_head: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb6eea4ce, original_name='ScannableInfoFinalHead'
        ),
    })
    head_armor: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x07d8cc4f, original_name='HeadArmor'
        ),
    })
    max_turn_speed: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0b5c3c1a, original_name='MaxTurnSpeed'
        ),
    })
    max_linear_velocity: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00d74fc3, original_name='MaxLinearVelocity'
        ),
    })
    unknown_0xe7de8b82: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe7de8b82, original_name='Unknown'
        ),
    })
    unknown_0x96e18283: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x96e18283, original_name='Unknown'
        ),
    })
    unknown_0xf77138d5: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf77138d5, original_name='Unknown'
        ),
    })
    unknown_0x8a83a097: float = dataclasses.field(default=22.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8a83a097, original_name='Unknown'
        ),
    })
    unknown_0xd919fb13: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd919fb13, original_name='Unknown'
        ),
    })
    audio_playback_parms_0x0a693a04: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x0a693a04, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    unknown_0x1cc6d870: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1cc6d870, original_name='Unknown'
        ),
    })
    part_0x5ff0b26c: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5ff0b26c, original_name='PART'
        ),
    })
    audio_playback_parms_0x50baee63: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x50baee63, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0xa5e1ec03: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xa5e1ec03, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0x8d6053cb: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x8d6053cb, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    part_0xc91ef399: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc91ef399, original_name='PART'
        ),
    })
    unknown_0x7d3d44af: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d3d44af, original_name='Unknown'
        ),
    })
    echo_targets: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2fa93722, original_name='EchoTargets'
        ),
    })
    part_0x342ae844: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x342ae844, original_name='PART'
        ),
    })
    explode_energy_stuff: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xcf98f423, original_name='ExplodeEnergyStuff'
        ),
    })
    audio_playback_parms_0x76eedd2a: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x76eedd2a, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0xa5ecbe17: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xa5ecbe17, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0xb1fc705f: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xb1fc705f, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0x2bc2677a: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x2bc2677a, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0x7f5b82b2: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x7f5b82b2, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    echo_parameters: EchoParameters = dataclasses.field(default_factory=EchoParameters, metadata={
        'reflection': FieldReflection[EchoParameters](
            EchoParameters, id=0x331fd5f7, original_name='EchoParameters', from_json=EchoParameters.from_json, to_json=EchoParameters.to_json
        ),
    })
    unknown_0x8317610f: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8317610f, original_name='Unknown'
        ),
    })
    part_0x321c97a9: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x321c97a9, original_name='PART'
        ),
    })
    audio_playback_parms_0xd5cc7e71: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xd5cc7e71, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0xa62c0ea7: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xa62c0ea7, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    audio_playback_parms_0xfd9f5486: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xfd9f5486, original_name='AudioPlaybackParms', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    annihilator_pulse: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x27464886, original_name='AnnihilatorPulse'
        ),
    })
    annihilator_pulse_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x4eaf615f, original_name='AnnihilatorPulseDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    annihilator_charge: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd669f12c, original_name='AnnihilatorCharge'
        ),
    })
    annihilator_charge_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x41177ac6, original_name='AnnihilatorChargeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xff7688bf: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xff7688bf, original_name='Unknown'
        ),
    })
    unknown_0x12ebb390: int = dataclasses.field(default=1500, metadata={
        'reflection': FieldReflection[int](
            int, id=0x12ebb390, original_name='Unknown'
        ),
    })
    frme: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['FRME'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xad151546, original_name='FRME'
        ),
    })
    plasma_beam_info: PlasmaBeamInfo = dataclasses.field(default_factory=PlasmaBeamInfo, metadata={
        'reflection': FieldReflection[PlasmaBeamInfo](
            PlasmaBeamInfo, id=0xc7cf5db1, original_name='PlasmaBeamInfo', from_json=PlasmaBeamInfo.from_json, to_json=PlasmaBeamInfo.to_json
        ),
    })
    lock_on_missiles: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd187f05c, original_name='LockOnMissiles'
        ),
    })
    lock_on_missiles_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xa8c6106b, original_name='LockOnMissilesDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    machine_gun: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0b5498d6, original_name='MachineGun'
        ),
    })
    machine_gun_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x45ef2edc, original_name='MachineGunDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    sound_machine_gun: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x47c8115e, original_name='Sound_MachineGun', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    unknown_0x4ab23ffe: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4ab23ffe, original_name='Unknown'
        ),
    })
    unknown_0x81a8474f: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x81a8474f, original_name='Unknown'
        ),
    })
    unknown_0x71c406ac: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x71c406ac, original_name='Unknown'
        ),
    })
    unknown_0xe5bc88b7: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe5bc88b7, original_name='Unknown'
        ),
    })
    digital_guardian_head_struct_0x8f6732ea: DigitalGuardianHeadStruct = dataclasses.field(default_factory=DigitalGuardianHeadStruct, metadata={
        'reflection': FieldReflection[DigitalGuardianHeadStruct](
            DigitalGuardianHeadStruct, id=0x8f6732ea, original_name='DigitalGuardianHeadStruct', from_json=DigitalGuardianHeadStruct.from_json, to_json=DigitalGuardianHeadStruct.to_json
        ),
    })
    digital_guardian_head_struct_0x8e128141: DigitalGuardianHeadStruct = dataclasses.field(default_factory=DigitalGuardianHeadStruct, metadata={
        'reflection': FieldReflection[DigitalGuardianHeadStruct](
            DigitalGuardianHeadStruct, id=0x8e128141, original_name='DigitalGuardianHeadStruct', from_json=DigitalGuardianHeadStruct.from_json, to_json=DigitalGuardianHeadStruct.to_json
        ),
    })
    digital_guardian_head_struct_0xea54b390: DigitalGuardianHeadStruct = dataclasses.field(default_factory=DigitalGuardianHeadStruct, metadata={
        'reflection': FieldReflection[DigitalGuardianHeadStruct](
            DigitalGuardianHeadStruct, id=0xea54b390, original_name='DigitalGuardianHeadStruct', from_json=DigitalGuardianHeadStruct.from_json, to_json=DigitalGuardianHeadStruct.to_json
        ),
    })
    digital_guardian_head_struct_0xbbd3e7a7: DigitalGuardianHeadStruct = dataclasses.field(default_factory=DigitalGuardianHeadStruct, metadata={
        'reflection': FieldReflection[DigitalGuardianHeadStruct](
            DigitalGuardianHeadStruct, id=0xbbd3e7a7, original_name='DigitalGuardianHeadStruct', from_json=DigitalGuardianHeadStruct.from_json, to_json=DigitalGuardianHeadStruct.to_json
        ),
    })
    digital_guardian_head_struct_0x2dd88764: DigitalGuardianHeadStruct = dataclasses.field(default_factory=DigitalGuardianHeadStruct, metadata={
        'reflection': FieldReflection[DigitalGuardianHeadStruct](
            DigitalGuardianHeadStruct, id=0x2dd88764, original_name='DigitalGuardianHeadStruct', from_json=DigitalGuardianHeadStruct.from_json, to_json=DigitalGuardianHeadStruct.to_json
        ),
    })
    digital_guardian_head_struct_0x48b46e55: DigitalGuardianHeadStruct = dataclasses.field(default_factory=DigitalGuardianHeadStruct, metadata={
        'reflection': FieldReflection[DigitalGuardianHeadStruct](
            DigitalGuardianHeadStruct, id=0x48b46e55, original_name='DigitalGuardianHeadStruct', from_json=DigitalGuardianHeadStruct.from_json, to_json=DigitalGuardianHeadStruct.to_json
        ),
    })
    bomb_pit_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x7352d60a, original_name='BombPitVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    echo_target_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x1b2aa049, original_name='EchoTargetVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        if property_count != 58:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4eaf47d7
        scannable_info_shield_head = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x390f3677
        scannable_info_stunned_head = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb6eea4ce
        scannable_info_final_head = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x07d8cc4f
        head_armor = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0b5c3c1a
        max_turn_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x00d74fc3
        max_linear_velocity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe7de8b82
        unknown_0xe7de8b82 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x96e18283
        unknown_0x96e18283 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf77138d5
        unknown_0xf77138d5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a83a097
        unknown_0x8a83a097 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd919fb13
        unknown_0xd919fb13 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a693a04
        audio_playback_parms_0x0a693a04 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1cc6d870
        unknown_0x1cc6d870 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5ff0b26c
        part_0x5ff0b26c = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x50baee63
        audio_playback_parms_0x50baee63 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa5e1ec03
        audio_playback_parms_0xa5e1ec03 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d6053cb
        audio_playback_parms_0x8d6053cb = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc91ef399
        part_0xc91ef399 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d3d44af
        unknown_0x7d3d44af = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2fa93722
        echo_targets = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x342ae844
        part_0x342ae844 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf98f423
        explode_energy_stuff = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76eedd2a
        audio_playback_parms_0x76eedd2a = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa5ecbe17
        audio_playback_parms_0xa5ecbe17 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb1fc705f
        audio_playback_parms_0xb1fc705f = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2bc2677a
        audio_playback_parms_0x2bc2677a = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f5b82b2
        audio_playback_parms_0x7f5b82b2 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x331fd5f7
        echo_parameters = EchoParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8317610f
        unknown_0x8317610f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x321c97a9
        part_0x321c97a9 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd5cc7e71
        audio_playback_parms_0xd5cc7e71 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa62c0ea7
        audio_playback_parms_0xa62c0ea7 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd9f5486
        audio_playback_parms_0xfd9f5486 = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x27464886
        annihilator_pulse = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4eaf615f
        annihilator_pulse_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd669f12c
        annihilator_charge = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x41177ac6
        annihilator_charge_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xff7688bf
        unknown_0xff7688bf = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12ebb390
        unknown_0x12ebb390 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad151546
        frme = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc7cf5db1
        plasma_beam_info = PlasmaBeamInfo.from_stream(data, property_size, default_override={'length': 500.0, 'expansion_speed': 4.0, 'life_time': 1.0, 'pulse_speed': 20.0, 'shutdown_time': 0.25, 'pulse_effect_scale': 2.0, 'inner_color': Color(r=0.49803900718688965, g=0.0, b=0.0, a=0.49803900718688965), 'outer_color': Color(r=0.6980389952659607, g=0.0, b=0.0, a=0.49803900718688965)})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd187f05c
        lock_on_missiles = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa8c6106b
        lock_on_missiles_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0b5498d6
        machine_gun = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x45ef2edc
        machine_gun_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47c8115e
        sound_machine_gun = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ab23ffe
        unknown_0x4ab23ffe = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81a8474f
        unknown_0x81a8474f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71c406ac
        unknown_0x71c406ac = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe5bc88b7
        unknown_0xe5bc88b7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f6732ea
        digital_guardian_head_struct_0x8f6732ea = DigitalGuardianHeadStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8e128141
        digital_guardian_head_struct_0x8e128141 = DigitalGuardianHeadStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea54b390
        digital_guardian_head_struct_0xea54b390 = DigitalGuardianHeadStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbbd3e7a7
        digital_guardian_head_struct_0xbbd3e7a7 = DigitalGuardianHeadStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2dd88764
        digital_guardian_head_struct_0x2dd88764 = DigitalGuardianHeadStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x48b46e55
        digital_guardian_head_struct_0x48b46e55 = DigitalGuardianHeadStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7352d60a
        bomb_pit_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b2aa049
        echo_target_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        return cls(scannable_info_shield_head, scannable_info_stunned_head, scannable_info_final_head, head_armor, max_turn_speed, max_linear_velocity, unknown_0xe7de8b82, unknown_0x96e18283, unknown_0xf77138d5, unknown_0x8a83a097, unknown_0xd919fb13, audio_playback_parms_0x0a693a04, unknown_0x1cc6d870, part_0x5ff0b26c, audio_playback_parms_0x50baee63, audio_playback_parms_0xa5e1ec03, audio_playback_parms_0x8d6053cb, part_0xc91ef399, unknown_0x7d3d44af, echo_targets, part_0x342ae844, explode_energy_stuff, audio_playback_parms_0x76eedd2a, audio_playback_parms_0xa5ecbe17, audio_playback_parms_0xb1fc705f, audio_playback_parms_0x2bc2677a, audio_playback_parms_0x7f5b82b2, echo_parameters, unknown_0x8317610f, part_0x321c97a9, audio_playback_parms_0xd5cc7e71, audio_playback_parms_0xa62c0ea7, audio_playback_parms_0xfd9f5486, annihilator_pulse, annihilator_pulse_damage, annihilator_charge, annihilator_charge_damage, unknown_0xff7688bf, unknown_0x12ebb390, frme, plasma_beam_info, lock_on_missiles, lock_on_missiles_damage, machine_gun, machine_gun_damage, sound_machine_gun, unknown_0x4ab23ffe, unknown_0x81a8474f, unknown_0x71c406ac, unknown_0xe5bc88b7, digital_guardian_head_struct_0x8f6732ea, digital_guardian_head_struct_0x8e128141, digital_guardian_head_struct_0xea54b390, digital_guardian_head_struct_0xbbd3e7a7, digital_guardian_head_struct_0x2dd88764, digital_guardian_head_struct_0x48b46e55, bomb_pit_vulnerability, echo_target_vulnerability)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00:')  # 58 properties

        data.write(b'N\xafG\xd7')  # 0x4eaf47d7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.scannable_info_shield_head))

        data.write(b'9\x0f6w')  # 0x390f3677
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.scannable_info_stunned_head))

        data.write(b'\xb6\xee\xa4\xce')  # 0xb6eea4ce
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.scannable_info_final_head))

        data.write(b'\x07\xd8\xccO')  # 0x7d8cc4f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.head_armor))

        data.write(b'\x0b\\<\x1a')  # 0xb5c3c1a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_turn_speed))

        data.write(b'\x00\xd7O\xc3')  # 0xd74fc3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_linear_velocity))

        data.write(b'\xe7\xde\x8b\x82')  # 0xe7de8b82
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe7de8b82))

        data.write(b'\x96\xe1\x82\x83')  # 0x96e18283
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x96e18283))

        data.write(b'\xf7q8\xd5')  # 0xf77138d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf77138d5))

        data.write(b'\x8a\x83\xa0\x97')  # 0x8a83a097
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8a83a097))

        data.write(b'\xd9\x19\xfb\x13')  # 0xd919fb13
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd919fb13))

        data.write(b'\ni:\x04')  # 0xa693a04
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0x0a693a04.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1c\xc6\xd8p')  # 0x1cc6d870
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1cc6d870))

        data.write(b'_\xf0\xb2l')  # 0x5ff0b26c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x5ff0b26c))

        data.write(b'P\xba\xeec')  # 0x50baee63
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0x50baee63.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa5\xe1\xec\x03')  # 0xa5e1ec03
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xa5e1ec03.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8d`S\xcb')  # 0x8d6053cb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0x8d6053cb.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc9\x1e\xf3\x99')  # 0xc91ef399
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0xc91ef399))

        data.write(b'}=D\xaf')  # 0x7d3d44af
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7d3d44af))

        data.write(b'/\xa97"')  # 0x2fa93722
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.echo_targets))

        data.write(b'4*\xe8D')  # 0x342ae844
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x342ae844))

        data.write(b'\xcf\x98\xf4#')  # 0xcf98f423
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.explode_energy_stuff))

        data.write(b'v\xee\xdd*')  # 0x76eedd2a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0x76eedd2a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa5\xec\xbe\x17')  # 0xa5ecbe17
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xa5ecbe17.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb1\xfcp_')  # 0xb1fc705f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xb1fc705f.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'+\xc2gz')  # 0x2bc2677a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0x2bc2677a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x7f[\x82\xb2')  # 0x7f5b82b2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0x7f5b82b2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'3\x1f\xd5\xf7')  # 0x331fd5f7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.echo_parameters.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x83\x17a\x0f')  # 0x8317610f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8317610f))

        data.write(b'2\x1c\x97\xa9')  # 0x321c97a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part_0x321c97a9))

        data.write(b'\xd5\xcc~q')  # 0xd5cc7e71
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xd5cc7e71.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa6,\x0e\xa7')  # 0xa62c0ea7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xa62c0ea7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfd\x9fT\x86')  # 0xfd9f5486
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.audio_playback_parms_0xfd9f5486.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"'FH\x86")  # 0x27464886
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.annihilator_pulse))

        data.write(b'N\xafa_')  # 0x4eaf615f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.annihilator_pulse_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd6i\xf1,')  # 0xd669f12c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.annihilator_charge))

        data.write(b'A\x17z\xc6')  # 0x41177ac6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.annihilator_charge_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xffv\x88\xbf')  # 0xff7688bf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xff7688bf))

        data.write(b'\x12\xeb\xb3\x90')  # 0x12ebb390
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x12ebb390))

        data.write(b'\xad\x15\x15F')  # 0xad151546
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.frme))

        data.write(b'\xc7\xcf]\xb1')  # 0xc7cf5db1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.plasma_beam_info.to_stream(data, default_override={'length': 500.0, 'expansion_speed': 4.0, 'life_time': 1.0, 'pulse_speed': 20.0, 'shutdown_time': 0.25, 'pulse_effect_scale': 2.0, 'inner_color': Color(r=0.49803900718688965, g=0.0, b=0.0, a=0.49803900718688965), 'outer_color': Color(r=0.6980389952659607, g=0.0, b=0.0, a=0.49803900718688965)})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd1\x87\xf0\\')  # 0xd187f05c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.lock_on_missiles))

        data.write(b'\xa8\xc6\x10k')  # 0xa8c6106b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.lock_on_missiles_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0bT\x98\xd6')  # 0xb5498d6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.machine_gun))

        data.write(b'E\xef.\xdc')  # 0x45ef2edc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.machine_gun_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'G\xc8\x11^')  # 0x47c8115e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sound_machine_gun.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'J\xb2?\xfe')  # 0x4ab23ffe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4ab23ffe))

        data.write(b'\x81\xa8GO')  # 0x81a8474f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x81a8474f))

        data.write(b'q\xc4\x06\xac')  # 0x71c406ac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x71c406ac))

        data.write(b'\xe5\xbc\x88\xb7')  # 0xe5bc88b7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe5bc88b7))

        data.write(b'\x8fg2\xea')  # 0x8f6732ea
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.digital_guardian_head_struct_0x8f6732ea.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8e\x12\x81A')  # 0x8e128141
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.digital_guardian_head_struct_0x8e128141.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xeaT\xb3\x90')  # 0xea54b390
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.digital_guardian_head_struct_0xea54b390.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbb\xd3\xe7\xa7')  # 0xbbd3e7a7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.digital_guardian_head_struct_0xbbd3e7a7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'-\xd8\x87d')  # 0x2dd88764
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.digital_guardian_head_struct_0x2dd88764.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'H\xb4nU')  # 0x48b46e55
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.digital_guardian_head_struct_0x48b46e55.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'sR\xd6\n')  # 0x7352d60a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.bomb_pit_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1b*\xa0I')  # 0x1b2aa049
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.echo_target_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DigitalGuardianHeadDataJson", data)
        return cls(
            scannable_info_shield_head=json_data['scannable_info_shield_head'],
            scannable_info_stunned_head=json_data['scannable_info_stunned_head'],
            scannable_info_final_head=json_data['scannable_info_final_head'],
            head_armor=json_data['head_armor'],
            max_turn_speed=json_data['max_turn_speed'],
            max_linear_velocity=json_data['max_linear_velocity'],
            unknown_0xe7de8b82=json_data['unknown_0xe7de8b82'],
            unknown_0x96e18283=json_data['unknown_0x96e18283'],
            unknown_0xf77138d5=json_data['unknown_0xf77138d5'],
            unknown_0x8a83a097=json_data['unknown_0x8a83a097'],
            unknown_0xd919fb13=json_data['unknown_0xd919fb13'],
            audio_playback_parms_0x0a693a04=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0x0a693a04']),
            unknown_0x1cc6d870=json_data['unknown_0x1cc6d870'],
            part_0x5ff0b26c=json_data['part_0x5ff0b26c'],
            audio_playback_parms_0x50baee63=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0x50baee63']),
            audio_playback_parms_0xa5e1ec03=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xa5e1ec03']),
            audio_playback_parms_0x8d6053cb=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0x8d6053cb']),
            part_0xc91ef399=json_data['part_0xc91ef399'],
            unknown_0x7d3d44af=json_data['unknown_0x7d3d44af'],
            echo_targets=json_data['echo_targets'],
            part_0x342ae844=json_data['part_0x342ae844'],
            explode_energy_stuff=json_data['explode_energy_stuff'],
            audio_playback_parms_0x76eedd2a=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0x76eedd2a']),
            audio_playback_parms_0xa5ecbe17=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xa5ecbe17']),
            audio_playback_parms_0xb1fc705f=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xb1fc705f']),
            audio_playback_parms_0x2bc2677a=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0x2bc2677a']),
            audio_playback_parms_0x7f5b82b2=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0x7f5b82b2']),
            echo_parameters=EchoParameters.from_json(json_data['echo_parameters']),
            unknown_0x8317610f=json_data['unknown_0x8317610f'],
            part_0x321c97a9=json_data['part_0x321c97a9'],
            audio_playback_parms_0xd5cc7e71=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xd5cc7e71']),
            audio_playback_parms_0xa62c0ea7=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xa62c0ea7']),
            audio_playback_parms_0xfd9f5486=AudioPlaybackParms.from_json(json_data['audio_playback_parms_0xfd9f5486']),
            annihilator_pulse=json_data['annihilator_pulse'],
            annihilator_pulse_damage=DamageInfo.from_json(json_data['annihilator_pulse_damage']),
            annihilator_charge=json_data['annihilator_charge'],
            annihilator_charge_damage=DamageInfo.from_json(json_data['annihilator_charge_damage']),
            unknown_0xff7688bf=json_data['unknown_0xff7688bf'],
            unknown_0x12ebb390=json_data['unknown_0x12ebb390'],
            frme=json_data['frme'],
            plasma_beam_info=PlasmaBeamInfo.from_json(json_data['plasma_beam_info']),
            lock_on_missiles=json_data['lock_on_missiles'],
            lock_on_missiles_damage=DamageInfo.from_json(json_data['lock_on_missiles_damage']),
            machine_gun=json_data['machine_gun'],
            machine_gun_damage=DamageInfo.from_json(json_data['machine_gun_damage']),
            sound_machine_gun=AudioPlaybackParms.from_json(json_data['sound_machine_gun']),
            unknown_0x4ab23ffe=json_data['unknown_0x4ab23ffe'],
            unknown_0x81a8474f=json_data['unknown_0x81a8474f'],
            unknown_0x71c406ac=json_data['unknown_0x71c406ac'],
            unknown_0xe5bc88b7=json_data['unknown_0xe5bc88b7'],
            digital_guardian_head_struct_0x8f6732ea=DigitalGuardianHeadStruct.from_json(json_data['digital_guardian_head_struct_0x8f6732ea']),
            digital_guardian_head_struct_0x8e128141=DigitalGuardianHeadStruct.from_json(json_data['digital_guardian_head_struct_0x8e128141']),
            digital_guardian_head_struct_0xea54b390=DigitalGuardianHeadStruct.from_json(json_data['digital_guardian_head_struct_0xea54b390']),
            digital_guardian_head_struct_0xbbd3e7a7=DigitalGuardianHeadStruct.from_json(json_data['digital_guardian_head_struct_0xbbd3e7a7']),
            digital_guardian_head_struct_0x2dd88764=DigitalGuardianHeadStruct.from_json(json_data['digital_guardian_head_struct_0x2dd88764']),
            digital_guardian_head_struct_0x48b46e55=DigitalGuardianHeadStruct.from_json(json_data['digital_guardian_head_struct_0x48b46e55']),
            bomb_pit_vulnerability=DamageVulnerability.from_json(json_data['bomb_pit_vulnerability']),
            echo_target_vulnerability=DamageVulnerability.from_json(json_data['echo_target_vulnerability']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'scannable_info_shield_head': self.scannable_info_shield_head,
            'scannable_info_stunned_head': self.scannable_info_stunned_head,
            'scannable_info_final_head': self.scannable_info_final_head,
            'head_armor': self.head_armor,
            'max_turn_speed': self.max_turn_speed,
            'max_linear_velocity': self.max_linear_velocity,
            'unknown_0xe7de8b82': self.unknown_0xe7de8b82,
            'unknown_0x96e18283': self.unknown_0x96e18283,
            'unknown_0xf77138d5': self.unknown_0xf77138d5,
            'unknown_0x8a83a097': self.unknown_0x8a83a097,
            'unknown_0xd919fb13': self.unknown_0xd919fb13,
            'audio_playback_parms_0x0a693a04': self.audio_playback_parms_0x0a693a04.to_json(),
            'unknown_0x1cc6d870': self.unknown_0x1cc6d870,
            'part_0x5ff0b26c': self.part_0x5ff0b26c,
            'audio_playback_parms_0x50baee63': self.audio_playback_parms_0x50baee63.to_json(),
            'audio_playback_parms_0xa5e1ec03': self.audio_playback_parms_0xa5e1ec03.to_json(),
            'audio_playback_parms_0x8d6053cb': self.audio_playback_parms_0x8d6053cb.to_json(),
            'part_0xc91ef399': self.part_0xc91ef399,
            'unknown_0x7d3d44af': self.unknown_0x7d3d44af,
            'echo_targets': self.echo_targets,
            'part_0x342ae844': self.part_0x342ae844,
            'explode_energy_stuff': self.explode_energy_stuff,
            'audio_playback_parms_0x76eedd2a': self.audio_playback_parms_0x76eedd2a.to_json(),
            'audio_playback_parms_0xa5ecbe17': self.audio_playback_parms_0xa5ecbe17.to_json(),
            'audio_playback_parms_0xb1fc705f': self.audio_playback_parms_0xb1fc705f.to_json(),
            'audio_playback_parms_0x2bc2677a': self.audio_playback_parms_0x2bc2677a.to_json(),
            'audio_playback_parms_0x7f5b82b2': self.audio_playback_parms_0x7f5b82b2.to_json(),
            'echo_parameters': self.echo_parameters.to_json(),
            'unknown_0x8317610f': self.unknown_0x8317610f,
            'part_0x321c97a9': self.part_0x321c97a9,
            'audio_playback_parms_0xd5cc7e71': self.audio_playback_parms_0xd5cc7e71.to_json(),
            'audio_playback_parms_0xa62c0ea7': self.audio_playback_parms_0xa62c0ea7.to_json(),
            'audio_playback_parms_0xfd9f5486': self.audio_playback_parms_0xfd9f5486.to_json(),
            'annihilator_pulse': self.annihilator_pulse,
            'annihilator_pulse_damage': self.annihilator_pulse_damage.to_json(),
            'annihilator_charge': self.annihilator_charge,
            'annihilator_charge_damage': self.annihilator_charge_damage.to_json(),
            'unknown_0xff7688bf': self.unknown_0xff7688bf,
            'unknown_0x12ebb390': self.unknown_0x12ebb390,
            'frme': self.frme,
            'plasma_beam_info': self.plasma_beam_info.to_json(),
            'lock_on_missiles': self.lock_on_missiles,
            'lock_on_missiles_damage': self.lock_on_missiles_damage.to_json(),
            'machine_gun': self.machine_gun,
            'machine_gun_damage': self.machine_gun_damage.to_json(),
            'sound_machine_gun': self.sound_machine_gun.to_json(),
            'unknown_0x4ab23ffe': self.unknown_0x4ab23ffe,
            'unknown_0x81a8474f': self.unknown_0x81a8474f,
            'unknown_0x71c406ac': self.unknown_0x71c406ac,
            'unknown_0xe5bc88b7': self.unknown_0xe5bc88b7,
            'digital_guardian_head_struct_0x8f6732ea': self.digital_guardian_head_struct_0x8f6732ea.to_json(),
            'digital_guardian_head_struct_0x8e128141': self.digital_guardian_head_struct_0x8e128141.to_json(),
            'digital_guardian_head_struct_0xea54b390': self.digital_guardian_head_struct_0xea54b390.to_json(),
            'digital_guardian_head_struct_0xbbd3e7a7': self.digital_guardian_head_struct_0xbbd3e7a7.to_json(),
            'digital_guardian_head_struct_0x2dd88764': self.digital_guardian_head_struct_0x2dd88764.to_json(),
            'digital_guardian_head_struct_0x48b46e55': self.digital_guardian_head_struct_0x48b46e55.to_json(),
            'bomb_pit_vulnerability': self.bomb_pit_vulnerability.to_json(),
            'echo_target_vulnerability': self.echo_target_vulnerability.to_json(),
        }

    def _dependencies_for_scannable_info_shield_head(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.scannable_info_shield_head)

    def _dependencies_for_scannable_info_stunned_head(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.scannable_info_stunned_head)

    def _dependencies_for_scannable_info_final_head(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.scannable_info_final_head)

    def _dependencies_for_head_armor(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.head_armor)

    def _dependencies_for_part_0x5ff0b26c(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x5ff0b26c)

    def _dependencies_for_part_0xc91ef399(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0xc91ef399)

    def _dependencies_for_echo_targets(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.echo_targets)

    def _dependencies_for_part_0x342ae844(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x342ae844)

    def _dependencies_for_explode_energy_stuff(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.explode_energy_stuff)

    def _dependencies_for_part_0x321c97a9(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part_0x321c97a9)

    def _dependencies_for_annihilator_pulse(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.annihilator_pulse)

    def _dependencies_for_annihilator_charge(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.annihilator_charge)

    def _dependencies_for_frme(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.frme)

    def _dependencies_for_lock_on_missiles(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.lock_on_missiles)

    def _dependencies_for_machine_gun(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.machine_gun)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_scannable_info_shield_head, "scannable_info_shield_head", "AssetId"),
            (self._dependencies_for_scannable_info_stunned_head, "scannable_info_stunned_head", "AssetId"),
            (self._dependencies_for_scannable_info_final_head, "scannable_info_final_head", "AssetId"),
            (self._dependencies_for_head_armor, "head_armor", "AssetId"),
            (self.audio_playback_parms_0x0a693a04.dependencies_for, "audio_playback_parms_0x0a693a04", "AudioPlaybackParms"),
            (self._dependencies_for_part_0x5ff0b26c, "part_0x5ff0b26c", "AssetId"),
            (self.audio_playback_parms_0x50baee63.dependencies_for, "audio_playback_parms_0x50baee63", "AudioPlaybackParms"),
            (self.audio_playback_parms_0xa5e1ec03.dependencies_for, "audio_playback_parms_0xa5e1ec03", "AudioPlaybackParms"),
            (self.audio_playback_parms_0x8d6053cb.dependencies_for, "audio_playback_parms_0x8d6053cb", "AudioPlaybackParms"),
            (self._dependencies_for_part_0xc91ef399, "part_0xc91ef399", "AssetId"),
            (self._dependencies_for_echo_targets, "echo_targets", "AssetId"),
            (self._dependencies_for_part_0x342ae844, "part_0x342ae844", "AssetId"),
            (self._dependencies_for_explode_energy_stuff, "explode_energy_stuff", "AssetId"),
            (self.audio_playback_parms_0x76eedd2a.dependencies_for, "audio_playback_parms_0x76eedd2a", "AudioPlaybackParms"),
            (self.audio_playback_parms_0xa5ecbe17.dependencies_for, "audio_playback_parms_0xa5ecbe17", "AudioPlaybackParms"),
            (self.audio_playback_parms_0xb1fc705f.dependencies_for, "audio_playback_parms_0xb1fc705f", "AudioPlaybackParms"),
            (self.audio_playback_parms_0x2bc2677a.dependencies_for, "audio_playback_parms_0x2bc2677a", "AudioPlaybackParms"),
            (self.audio_playback_parms_0x7f5b82b2.dependencies_for, "audio_playback_parms_0x7f5b82b2", "AudioPlaybackParms"),
            (self.echo_parameters.dependencies_for, "echo_parameters", "EchoParameters"),
            (self._dependencies_for_part_0x321c97a9, "part_0x321c97a9", "AssetId"),
            (self.audio_playback_parms_0xd5cc7e71.dependencies_for, "audio_playback_parms_0xd5cc7e71", "AudioPlaybackParms"),
            (self.audio_playback_parms_0xa62c0ea7.dependencies_for, "audio_playback_parms_0xa62c0ea7", "AudioPlaybackParms"),
            (self.audio_playback_parms_0xfd9f5486.dependencies_for, "audio_playback_parms_0xfd9f5486", "AudioPlaybackParms"),
            (self._dependencies_for_annihilator_pulse, "annihilator_pulse", "AssetId"),
            (self.annihilator_pulse_damage.dependencies_for, "annihilator_pulse_damage", "DamageInfo"),
            (self._dependencies_for_annihilator_charge, "annihilator_charge", "AssetId"),
            (self.annihilator_charge_damage.dependencies_for, "annihilator_charge_damage", "DamageInfo"),
            (self._dependencies_for_frme, "frme", "AssetId"),
            (self.plasma_beam_info.dependencies_for, "plasma_beam_info", "PlasmaBeamInfo"),
            (self._dependencies_for_lock_on_missiles, "lock_on_missiles", "AssetId"),
            (self.lock_on_missiles_damage.dependencies_for, "lock_on_missiles_damage", "DamageInfo"),
            (self._dependencies_for_machine_gun, "machine_gun", "AssetId"),
            (self.machine_gun_damage.dependencies_for, "machine_gun_damage", "DamageInfo"),
            (self.sound_machine_gun.dependencies_for, "sound_machine_gun", "AudioPlaybackParms"),
            (self.digital_guardian_head_struct_0x8f6732ea.dependencies_for, "digital_guardian_head_struct_0x8f6732ea", "DigitalGuardianHeadStruct"),
            (self.digital_guardian_head_struct_0x8e128141.dependencies_for, "digital_guardian_head_struct_0x8e128141", "DigitalGuardianHeadStruct"),
            (self.digital_guardian_head_struct_0xea54b390.dependencies_for, "digital_guardian_head_struct_0xea54b390", "DigitalGuardianHeadStruct"),
            (self.digital_guardian_head_struct_0xbbd3e7a7.dependencies_for, "digital_guardian_head_struct_0xbbd3e7a7", "DigitalGuardianHeadStruct"),
            (self.digital_guardian_head_struct_0x2dd88764.dependencies_for, "digital_guardian_head_struct_0x2dd88764", "DigitalGuardianHeadStruct"),
            (self.digital_guardian_head_struct_0x48b46e55.dependencies_for, "digital_guardian_head_struct_0x48b46e55", "DigitalGuardianHeadStruct"),
            (self.bomb_pit_vulnerability.dependencies_for, "bomb_pit_vulnerability", "DamageVulnerability"),
            (self.echo_target_vulnerability.dependencies_for, "echo_target_vulnerability", "DamageVulnerability"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for DigitalGuardianHeadData.{field_name} ({field_type}): {e}"
                )


def _decode_scannable_info_shield_head(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_scannable_info_stunned_head(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_scannable_info_final_head(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_head_armor(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_max_turn_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_linear_velocity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe7de8b82(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x96e18283(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf77138d5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8a83a097(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd919fb13(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1cc6d870(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_part_0x5ff0b26c(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0xc91ef399(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x7d3d44af(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_echo_targets(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part_0x342ae844(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_explode_energy_stuff(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x8317610f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_part_0x321c97a9(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_annihilator_pulse(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_annihilator_pulse_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})


def _decode_annihilator_charge(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_annihilator_charge_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})


def _decode_unknown_0xff7688bf(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x12ebb390(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_frme(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_plasma_beam_info(data: typing.BinaryIO, property_size: int) -> PlasmaBeamInfo:
    return PlasmaBeamInfo.from_stream(data, property_size, default_override={'length': 500.0, 'expansion_speed': 4.0, 'life_time': 1.0, 'pulse_speed': 20.0, 'shutdown_time': 0.25, 'pulse_effect_scale': 2.0, 'inner_color': Color(r=0.49803900718688965, g=0.0, b=0.0, a=0.49803900718688965), 'outer_color': Color(r=0.6980389952659607, g=0.0, b=0.0, a=0.49803900718688965)})


def _decode_lock_on_missiles(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_lock_on_missiles_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})


def _decode_machine_gun(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_machine_gun_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 20.0, 'di_knock_back_power': 10.0})


def _decode_unknown_0x4ab23ffe(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x81a8474f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x71c406ac(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe5bc88b7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x4eaf47d7: ('scannable_info_shield_head', _decode_scannable_info_shield_head),
    0x390f3677: ('scannable_info_stunned_head', _decode_scannable_info_stunned_head),
    0xb6eea4ce: ('scannable_info_final_head', _decode_scannable_info_final_head),
    0x7d8cc4f: ('head_armor', _decode_head_armor),
    0xb5c3c1a: ('max_turn_speed', _decode_max_turn_speed),
    0xd74fc3: ('max_linear_velocity', _decode_max_linear_velocity),
    0xe7de8b82: ('unknown_0xe7de8b82', _decode_unknown_0xe7de8b82),
    0x96e18283: ('unknown_0x96e18283', _decode_unknown_0x96e18283),
    0xf77138d5: ('unknown_0xf77138d5', _decode_unknown_0xf77138d5),
    0x8a83a097: ('unknown_0x8a83a097', _decode_unknown_0x8a83a097),
    0xd919fb13: ('unknown_0xd919fb13', _decode_unknown_0xd919fb13),
    0xa693a04: ('audio_playback_parms_0x0a693a04', AudioPlaybackParms.from_stream),
    0x1cc6d870: ('unknown_0x1cc6d870', _decode_unknown_0x1cc6d870),
    0x5ff0b26c: ('part_0x5ff0b26c', _decode_part_0x5ff0b26c),
    0x50baee63: ('audio_playback_parms_0x50baee63', AudioPlaybackParms.from_stream),
    0xa5e1ec03: ('audio_playback_parms_0xa5e1ec03', AudioPlaybackParms.from_stream),
    0x8d6053cb: ('audio_playback_parms_0x8d6053cb', AudioPlaybackParms.from_stream),
    0xc91ef399: ('part_0xc91ef399', _decode_part_0xc91ef399),
    0x7d3d44af: ('unknown_0x7d3d44af', _decode_unknown_0x7d3d44af),
    0x2fa93722: ('echo_targets', _decode_echo_targets),
    0x342ae844: ('part_0x342ae844', _decode_part_0x342ae844),
    0xcf98f423: ('explode_energy_stuff', _decode_explode_energy_stuff),
    0x76eedd2a: ('audio_playback_parms_0x76eedd2a', AudioPlaybackParms.from_stream),
    0xa5ecbe17: ('audio_playback_parms_0xa5ecbe17', AudioPlaybackParms.from_stream),
    0xb1fc705f: ('audio_playback_parms_0xb1fc705f', AudioPlaybackParms.from_stream),
    0x2bc2677a: ('audio_playback_parms_0x2bc2677a', AudioPlaybackParms.from_stream),
    0x7f5b82b2: ('audio_playback_parms_0x7f5b82b2', AudioPlaybackParms.from_stream),
    0x331fd5f7: ('echo_parameters', EchoParameters.from_stream),
    0x8317610f: ('unknown_0x8317610f', _decode_unknown_0x8317610f),
    0x321c97a9: ('part_0x321c97a9', _decode_part_0x321c97a9),
    0xd5cc7e71: ('audio_playback_parms_0xd5cc7e71', AudioPlaybackParms.from_stream),
    0xa62c0ea7: ('audio_playback_parms_0xa62c0ea7', AudioPlaybackParms.from_stream),
    0xfd9f5486: ('audio_playback_parms_0xfd9f5486', AudioPlaybackParms.from_stream),
    0x27464886: ('annihilator_pulse', _decode_annihilator_pulse),
    0x4eaf615f: ('annihilator_pulse_damage', _decode_annihilator_pulse_damage),
    0xd669f12c: ('annihilator_charge', _decode_annihilator_charge),
    0x41177ac6: ('annihilator_charge_damage', _decode_annihilator_charge_damage),
    0xff7688bf: ('unknown_0xff7688bf', _decode_unknown_0xff7688bf),
    0x12ebb390: ('unknown_0x12ebb390', _decode_unknown_0x12ebb390),
    0xad151546: ('frme', _decode_frme),
    0xc7cf5db1: ('plasma_beam_info', _decode_plasma_beam_info),
    0xd187f05c: ('lock_on_missiles', _decode_lock_on_missiles),
    0xa8c6106b: ('lock_on_missiles_damage', _decode_lock_on_missiles_damage),
    0xb5498d6: ('machine_gun', _decode_machine_gun),
    0x45ef2edc: ('machine_gun_damage', _decode_machine_gun_damage),
    0x47c8115e: ('sound_machine_gun', AudioPlaybackParms.from_stream),
    0x4ab23ffe: ('unknown_0x4ab23ffe', _decode_unknown_0x4ab23ffe),
    0x81a8474f: ('unknown_0x81a8474f', _decode_unknown_0x81a8474f),
    0x71c406ac: ('unknown_0x71c406ac', _decode_unknown_0x71c406ac),
    0xe5bc88b7: ('unknown_0xe5bc88b7', _decode_unknown_0xe5bc88b7),
    0x8f6732ea: ('digital_guardian_head_struct_0x8f6732ea', DigitalGuardianHeadStruct.from_stream),
    0x8e128141: ('digital_guardian_head_struct_0x8e128141', DigitalGuardianHeadStruct.from_stream),
    0xea54b390: ('digital_guardian_head_struct_0xea54b390', DigitalGuardianHeadStruct.from_stream),
    0xbbd3e7a7: ('digital_guardian_head_struct_0xbbd3e7a7', DigitalGuardianHeadStruct.from_stream),
    0x2dd88764: ('digital_guardian_head_struct_0x2dd88764', DigitalGuardianHeadStruct.from_stream),
    0x48b46e55: ('digital_guardian_head_struct_0x48b46e55', DigitalGuardianHeadStruct.from_stream),
    0x7352d60a: ('bomb_pit_vulnerability', DamageVulnerability.from_stream),
    0x1b2aa049: ('echo_target_vulnerability', DamageVulnerability.from_stream),
}
