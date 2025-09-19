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
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.ShockWaveInfo import ShockWaveInfo
from retro_data_structures.properties.echoes.archetypes.SwampBossStage1Struct import SwampBossStage1Struct
from retro_data_structures.properties.echoes.archetypes.UnknownStruct36 import UnknownStruct36
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct37Json(typing_extensions.TypedDict):
        dark_water_ring_effect: int
        unknown_0x27a06f6a: float
        unknown_0x233a5e40: float
        pre_jump_telegraph_effect: int
        splash_shock_wave: json_util.JsonObject
        tongue_particle_effect: int
        tongue_particle_model: int
        tongue_tip_model: int
        damage_info: json_util.JsonObject
        part: int
        unknown_0x78755da3: float
        unknown_0x74e1a041: float
        unknown_0x1f4e7c2c: float
        unknown_0xee6b6f47: float
        unknown_0x3ce96c9d: float
        weak_spot_vulnerability: json_util.JsonObject
        weak_spot_damage_multiplier: float
        spit_projectile: int
        spit_damage: json_util.JsonObject
        spit_visor_effect: int
        sound_spit_visor: int
        spit_projectile_radius: float
        unknown_struct36: json_util.JsonObject
        swamp_boss_stage1_struct_0x4500f774: json_util.JsonObject
        swamp_boss_stage1_struct_0x3e1e7597: json_util.JsonObject
        swamp_boss_stage1_struct_0xa1c4f609: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct37(BaseProperty):
    dark_water_ring_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6cedf364, original_name='DarkWaterRingEffect'
        ),
    })
    unknown_0x27a06f6a: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x27a06f6a, original_name='Unknown'
        ),
    })
    unknown_0x233a5e40: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x233a5e40, original_name='Unknown'
        ),
    })
    pre_jump_telegraph_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xef7c65ac, original_name='PreJumpTelegraphEffect'
        ),
    })
    splash_shock_wave: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0x6c0f7aa3, original_name='SplashShockWave', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })
    tongue_particle_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x762cd5b7, original_name='TongueParticleEffect'
        ),
    })
    tongue_particle_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd8ab76f0, original_name='TongueParticleModel'
        ),
    })
    tongue_tip_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x145debea, original_name='TongueTipModel'
        ),
    })
    damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xd0b0f21f, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    part: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0a078586, original_name='PART'
        ),
    })
    unknown_0x78755da3: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x78755da3, original_name='Unknown'
        ),
    })
    unknown_0x74e1a041: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x74e1a041, original_name='Unknown'
        ),
    })
    unknown_0x1f4e7c2c: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1f4e7c2c, original_name='Unknown'
        ),
    })
    unknown_0xee6b6f47: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xee6b6f47, original_name='Unknown'
        ),
    })
    unknown_0x3ce96c9d: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3ce96c9d, original_name='Unknown'
        ),
    })
    weak_spot_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x950318f0, original_name='WeakSpotVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    weak_spot_damage_multiplier: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xba694941, original_name='WeakSpotDamageMultiplier'
        ),
    })
    spit_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xcfe37ebf, original_name='SpitProjectile'
        ),
    })
    spit_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xda3c9b32, original_name='SpitDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    spit_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x008becab, original_name='SpitVisorEffect'
        ),
    })
    sound_spit_visor: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xf3af8417, original_name='Sound_SpitVisor'
        ),
    })
    spit_projectile_radius: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdadc5bc9, original_name='SpitProjectileRadius'
        ),
    })
    unknown_struct36: UnknownStruct36 = dataclasses.field(default_factory=UnknownStruct36, metadata={
        'reflection': FieldReflection[UnknownStruct36](
            UnknownStruct36, id=0xd402095f, original_name='UnknownStruct36', from_json=UnknownStruct36.from_json, to_json=UnknownStruct36.to_json
        ),
    })
    swamp_boss_stage1_struct_0x4500f774: SwampBossStage1Struct = dataclasses.field(default_factory=SwampBossStage1Struct, metadata={
        'reflection': FieldReflection[SwampBossStage1Struct](
            SwampBossStage1Struct, id=0x4500f774, original_name='SwampBossStage1Struct', from_json=SwampBossStage1Struct.from_json, to_json=SwampBossStage1Struct.to_json
        ),
    })
    swamp_boss_stage1_struct_0x3e1e7597: SwampBossStage1Struct = dataclasses.field(default_factory=SwampBossStage1Struct, metadata={
        'reflection': FieldReflection[SwampBossStage1Struct](
            SwampBossStage1Struct, id=0x3e1e7597, original_name='SwampBossStage1Struct', from_json=SwampBossStage1Struct.from_json, to_json=SwampBossStage1Struct.to_json
        ),
    })
    swamp_boss_stage1_struct_0xa1c4f609: SwampBossStage1Struct = dataclasses.field(default_factory=SwampBossStage1Struct, metadata={
        'reflection': FieldReflection[SwampBossStage1Struct](
            SwampBossStage1Struct, id=0xa1c4f609, original_name='SwampBossStage1Struct', from_json=SwampBossStage1Struct.from_json, to_json=SwampBossStage1Struct.to_json
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
        if property_count != 26:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6cedf364
        dark_water_ring_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x27a06f6a
        unknown_0x27a06f6a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x233a5e40
        unknown_0x233a5e40 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef7c65ac
        pre_jump_telegraph_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c0f7aa3
        splash_shock_wave = ShockWaveInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x762cd5b7
        tongue_particle_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd8ab76f0
        tongue_particle_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x145debea
        tongue_tip_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0b0f21f
        damage_info = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a078586
        part = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78755da3
        unknown_0x78755da3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x74e1a041
        unknown_0x74e1a041 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1f4e7c2c
        unknown_0x1f4e7c2c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xee6b6f47
        unknown_0xee6b6f47 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3ce96c9d
        unknown_0x3ce96c9d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x950318f0
        weak_spot_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba694941
        weak_spot_damage_multiplier = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcfe37ebf
        spit_projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xda3c9b32
        spit_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x008becab
        spit_visor_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3af8417
        sound_spit_visor = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdadc5bc9
        spit_projectile_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd402095f
        unknown_struct36 = UnknownStruct36.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4500f774
        swamp_boss_stage1_struct_0x4500f774 = SwampBossStage1Struct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e1e7597
        swamp_boss_stage1_struct_0x3e1e7597 = SwampBossStage1Struct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa1c4f609
        swamp_boss_stage1_struct_0xa1c4f609 = SwampBossStage1Struct.from_stream(data, property_size)
    
        return cls(dark_water_ring_effect, unknown_0x27a06f6a, unknown_0x233a5e40, pre_jump_telegraph_effect, splash_shock_wave, tongue_particle_effect, tongue_particle_model, tongue_tip_model, damage_info, part, unknown_0x78755da3, unknown_0x74e1a041, unknown_0x1f4e7c2c, unknown_0xee6b6f47, unknown_0x3ce96c9d, weak_spot_vulnerability, weak_spot_damage_multiplier, spit_projectile, spit_damage, spit_visor_effect, sound_spit_visor, spit_projectile_radius, unknown_struct36, swamp_boss_stage1_struct_0x4500f774, swamp_boss_stage1_struct_0x3e1e7597, swamp_boss_stage1_struct_0xa1c4f609)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x1a')  # 26 properties

        data.write(b'l\xed\xf3d')  # 0x6cedf364
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.dark_water_ring_effect))

        data.write(b"'\xa0oj")  # 0x27a06f6a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x27a06f6a))

        data.write(b'#:^@')  # 0x233a5e40
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x233a5e40))

        data.write(b'\xef|e\xac')  # 0xef7c65ac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.pre_jump_telegraph_effect))

        data.write(b'l\x0fz\xa3')  # 0x6c0f7aa3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.splash_shock_wave.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'v,\xd5\xb7')  # 0x762cd5b7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.tongue_particle_effect))

        data.write(b'\xd8\xabv\xf0')  # 0xd8ab76f0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.tongue_particle_model))

        data.write(b'\x14]\xeb\xea')  # 0x145debea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.tongue_tip_model))

        data.write(b'\xd0\xb0\xf2\x1f')  # 0xd0b0f21f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\n\x07\x85\x86')  # 0xa078586
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part))

        data.write(b'xu]\xa3')  # 0x78755da3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x78755da3))

        data.write(b't\xe1\xa0A')  # 0x74e1a041
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x74e1a041))

        data.write(b'\x1fN|,')  # 0x1f4e7c2c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1f4e7c2c))

        data.write(b'\xeekoG')  # 0xee6b6f47
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xee6b6f47))

        data.write(b'<\xe9l\x9d')  # 0x3ce96c9d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3ce96c9d))

        data.write(b'\x95\x03\x18\xf0')  # 0x950318f0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weak_spot_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbaiIA')  # 0xba694941
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.weak_spot_damage_multiplier))

        data.write(b'\xcf\xe3~\xbf')  # 0xcfe37ebf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.spit_projectile))

        data.write(b'\xda<\x9b2')  # 0xda3c9b32
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spit_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x00\x8b\xec\xab')  # 0x8becab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.spit_visor_effect))

        data.write(b'\xf3\xaf\x84\x17')  # 0xf3af8417
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_spit_visor))

        data.write(b'\xda\xdc[\xc9')  # 0xdadc5bc9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.spit_projectile_radius))

        data.write(b'\xd4\x02\t_')  # 0xd402095f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct36.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'E\x00\xf7t')  # 0x4500f774
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.swamp_boss_stage1_struct_0x4500f774.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'>\x1eu\x97')  # 0x3e1e7597
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.swamp_boss_stage1_struct_0x3e1e7597.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa1\xc4\xf6\t')  # 0xa1c4f609
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.swamp_boss_stage1_struct_0xa1c4f609.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct37Json", data)
        return cls(
            dark_water_ring_effect=json_data['dark_water_ring_effect'],
            unknown_0x27a06f6a=json_data['unknown_0x27a06f6a'],
            unknown_0x233a5e40=json_data['unknown_0x233a5e40'],
            pre_jump_telegraph_effect=json_data['pre_jump_telegraph_effect'],
            splash_shock_wave=ShockWaveInfo.from_json(json_data['splash_shock_wave']),
            tongue_particle_effect=json_data['tongue_particle_effect'],
            tongue_particle_model=json_data['tongue_particle_model'],
            tongue_tip_model=json_data['tongue_tip_model'],
            damage_info=DamageInfo.from_json(json_data['damage_info']),
            part=json_data['part'],
            unknown_0x78755da3=json_data['unknown_0x78755da3'],
            unknown_0x74e1a041=json_data['unknown_0x74e1a041'],
            unknown_0x1f4e7c2c=json_data['unknown_0x1f4e7c2c'],
            unknown_0xee6b6f47=json_data['unknown_0xee6b6f47'],
            unknown_0x3ce96c9d=json_data['unknown_0x3ce96c9d'],
            weak_spot_vulnerability=DamageVulnerability.from_json(json_data['weak_spot_vulnerability']),
            weak_spot_damage_multiplier=json_data['weak_spot_damage_multiplier'],
            spit_projectile=json_data['spit_projectile'],
            spit_damage=DamageInfo.from_json(json_data['spit_damage']),
            spit_visor_effect=json_data['spit_visor_effect'],
            sound_spit_visor=json_data['sound_spit_visor'],
            spit_projectile_radius=json_data['spit_projectile_radius'],
            unknown_struct36=UnknownStruct36.from_json(json_data['unknown_struct36']),
            swamp_boss_stage1_struct_0x4500f774=SwampBossStage1Struct.from_json(json_data['swamp_boss_stage1_struct_0x4500f774']),
            swamp_boss_stage1_struct_0x3e1e7597=SwampBossStage1Struct.from_json(json_data['swamp_boss_stage1_struct_0x3e1e7597']),
            swamp_boss_stage1_struct_0xa1c4f609=SwampBossStage1Struct.from_json(json_data['swamp_boss_stage1_struct_0xa1c4f609']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'dark_water_ring_effect': self.dark_water_ring_effect,
            'unknown_0x27a06f6a': self.unknown_0x27a06f6a,
            'unknown_0x233a5e40': self.unknown_0x233a5e40,
            'pre_jump_telegraph_effect': self.pre_jump_telegraph_effect,
            'splash_shock_wave': self.splash_shock_wave.to_json(),
            'tongue_particle_effect': self.tongue_particle_effect,
            'tongue_particle_model': self.tongue_particle_model,
            'tongue_tip_model': self.tongue_tip_model,
            'damage_info': self.damage_info.to_json(),
            'part': self.part,
            'unknown_0x78755da3': self.unknown_0x78755da3,
            'unknown_0x74e1a041': self.unknown_0x74e1a041,
            'unknown_0x1f4e7c2c': self.unknown_0x1f4e7c2c,
            'unknown_0xee6b6f47': self.unknown_0xee6b6f47,
            'unknown_0x3ce96c9d': self.unknown_0x3ce96c9d,
            'weak_spot_vulnerability': self.weak_spot_vulnerability.to_json(),
            'weak_spot_damage_multiplier': self.weak_spot_damage_multiplier,
            'spit_projectile': self.spit_projectile,
            'spit_damage': self.spit_damage.to_json(),
            'spit_visor_effect': self.spit_visor_effect,
            'sound_spit_visor': self.sound_spit_visor,
            'spit_projectile_radius': self.spit_projectile_radius,
            'unknown_struct36': self.unknown_struct36.to_json(),
            'swamp_boss_stage1_struct_0x4500f774': self.swamp_boss_stage1_struct_0x4500f774.to_json(),
            'swamp_boss_stage1_struct_0x3e1e7597': self.swamp_boss_stage1_struct_0x3e1e7597.to_json(),
            'swamp_boss_stage1_struct_0xa1c4f609': self.swamp_boss_stage1_struct_0xa1c4f609.to_json(),
        }

    def _dependencies_for_dark_water_ring_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.dark_water_ring_effect)

    def _dependencies_for_pre_jump_telegraph_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.pre_jump_telegraph_effect)

    def _dependencies_for_tongue_particle_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.tongue_particle_effect)

    def _dependencies_for_tongue_particle_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.tongue_particle_model)

    def _dependencies_for_tongue_tip_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.tongue_tip_model)

    def _dependencies_for_part(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part)

    def _dependencies_for_spit_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.spit_projectile)

    def _dependencies_for_spit_visor_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.spit_visor_effect)

    def _dependencies_for_sound_spit_visor(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_spit_visor)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_dark_water_ring_effect, "dark_water_ring_effect", "AssetId"),
            (self._dependencies_for_pre_jump_telegraph_effect, "pre_jump_telegraph_effect", "AssetId"),
            (self.splash_shock_wave.dependencies_for, "splash_shock_wave", "ShockWaveInfo"),
            (self._dependencies_for_tongue_particle_effect, "tongue_particle_effect", "AssetId"),
            (self._dependencies_for_tongue_particle_model, "tongue_particle_model", "AssetId"),
            (self._dependencies_for_tongue_tip_model, "tongue_tip_model", "AssetId"),
            (self.damage_info.dependencies_for, "damage_info", "DamageInfo"),
            (self._dependencies_for_part, "part", "AssetId"),
            (self.weak_spot_vulnerability.dependencies_for, "weak_spot_vulnerability", "DamageVulnerability"),
            (self._dependencies_for_spit_projectile, "spit_projectile", "AssetId"),
            (self.spit_damage.dependencies_for, "spit_damage", "DamageInfo"),
            (self._dependencies_for_spit_visor_effect, "spit_visor_effect", "AssetId"),
            (self._dependencies_for_sound_spit_visor, "sound_spit_visor", "int"),
            (self.unknown_struct36.dependencies_for, "unknown_struct36", "UnknownStruct36"),
            (self.swamp_boss_stage1_struct_0x4500f774.dependencies_for, "swamp_boss_stage1_struct_0x4500f774", "SwampBossStage1Struct"),
            (self.swamp_boss_stage1_struct_0x3e1e7597.dependencies_for, "swamp_boss_stage1_struct_0x3e1e7597", "SwampBossStage1Struct"),
            (self.swamp_boss_stage1_struct_0xa1c4f609.dependencies_for, "swamp_boss_stage1_struct_0xa1c4f609", "SwampBossStage1Struct"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct37.{field_name} ({field_type}): {e}"
                )


def _decode_dark_water_ring_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x27a06f6a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x233a5e40(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pre_jump_telegraph_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_tongue_particle_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_tongue_particle_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_tongue_tip_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_part(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x78755da3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x74e1a041(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1f4e7c2c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xee6b6f47(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3ce96c9d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_weak_spot_damage_multiplier(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_spit_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_spit_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_spit_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_sound_spit_visor(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_spit_projectile_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x6cedf364: ('dark_water_ring_effect', _decode_dark_water_ring_effect),
    0x27a06f6a: ('unknown_0x27a06f6a', _decode_unknown_0x27a06f6a),
    0x233a5e40: ('unknown_0x233a5e40', _decode_unknown_0x233a5e40),
    0xef7c65ac: ('pre_jump_telegraph_effect', _decode_pre_jump_telegraph_effect),
    0x6c0f7aa3: ('splash_shock_wave', ShockWaveInfo.from_stream),
    0x762cd5b7: ('tongue_particle_effect', _decode_tongue_particle_effect),
    0xd8ab76f0: ('tongue_particle_model', _decode_tongue_particle_model),
    0x145debea: ('tongue_tip_model', _decode_tongue_tip_model),
    0xd0b0f21f: ('damage_info', DamageInfo.from_stream),
    0xa078586: ('part', _decode_part),
    0x78755da3: ('unknown_0x78755da3', _decode_unknown_0x78755da3),
    0x74e1a041: ('unknown_0x74e1a041', _decode_unknown_0x74e1a041),
    0x1f4e7c2c: ('unknown_0x1f4e7c2c', _decode_unknown_0x1f4e7c2c),
    0xee6b6f47: ('unknown_0xee6b6f47', _decode_unknown_0xee6b6f47),
    0x3ce96c9d: ('unknown_0x3ce96c9d', _decode_unknown_0x3ce96c9d),
    0x950318f0: ('weak_spot_vulnerability', DamageVulnerability.from_stream),
    0xba694941: ('weak_spot_damage_multiplier', _decode_weak_spot_damage_multiplier),
    0xcfe37ebf: ('spit_projectile', _decode_spit_projectile),
    0xda3c9b32: ('spit_damage', _decode_spit_damage),
    0x8becab: ('spit_visor_effect', _decode_spit_visor_effect),
    0xf3af8417: ('sound_spit_visor', _decode_sound_spit_visor),
    0xdadc5bc9: ('spit_projectile_radius', _decode_spit_projectile_radius),
    0xd402095f: ('unknown_struct36', UnknownStruct36.from_stream),
    0x4500f774: ('swamp_boss_stage1_struct_0x4500f774', SwampBossStage1Struct.from_stream),
    0x3e1e7597: ('swamp_boss_stage1_struct_0x3e1e7597', SwampBossStage1Struct.from_stream),
    0xa1c4f609: ('swamp_boss_stage1_struct_0xa1c4f609', SwampBossStage1Struct.from_stream),
}
