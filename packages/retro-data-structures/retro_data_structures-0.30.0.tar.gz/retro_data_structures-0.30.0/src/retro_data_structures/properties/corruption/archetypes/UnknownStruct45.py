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
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData
from retro_data_structures.properties.corruption.archetypes.PuddleControlData import PuddleControlData
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct45Json(typing_extensions.TypedDict):
        projectile: json_util.JsonObject
        projectile_delay_min: float
        projectile_delay_max: float
        min_puddle_time: float
        speed: float
        contact_damage: json_util.JsonObject
        unknown_0x49f4c4ee: float
        dot_damage: json_util.JsonObject
        dot_frequency: float
        dot_duration: float
        shell_start_duration: float
        splash_delay: float
        min_splash_speed: float
        max_splash_speed: float
        unknown_0xa6bc177f: float
        unknown_0x7d034498: float
        min_wake_speed: float
        texture_align_delay: float
        normal: json_util.JsonObject
        explosion: json_util.JsonObject
        contact: json_util.JsonObject
        blob_effect: int
        hit_normal_damage: int
        hit_heavy_damage: int
        death: int
        explosion_splash: int
        contact_splash: int
        ball_shell_start: int
        ball_shell_continue: int
        ball_shell_end: int
        ball_wake: int
        ball_wake_end: int
        sound_ball_shell_continue: int
        sound_ball_shell_end: int
        sound_touch: int
        caud_0x49b30de2: int
        caud_0xdecd5831: int
        sound_death: int
        vulnerability: json_util.JsonObject
        grapple_data: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct45(BaseProperty):
    projectile: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x2c83c012, original_name='Projectile', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    projectile_delay_min: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdb254386, original_name='ProjectileDelayMin'
        ),
    })
    projectile_delay_max: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3d45ec67, original_name='ProjectileDelayMax'
        ),
    })
    min_puddle_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xefdc8306, original_name='MinPuddleTime'
        ),
    })
    speed: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6392404e, original_name='Speed'
        ),
    })
    contact_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xd756416e, original_name='ContactDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x49f4c4ee: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x49f4c4ee, original_name='Unknown'
        ),
    })
    dot_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xa7a47350, original_name='DotDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    dot_frequency: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x955a61ef, original_name='DotFrequency'
        ),
    })
    dot_duration: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x77a4efb5, original_name='DotDuration'
        ),
    })
    shell_start_duration: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x45134ace, original_name='ShellStartDuration'
        ),
    })
    splash_delay: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x308d4f23, original_name='SplashDelay'
        ),
    })
    min_splash_speed: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x26797df9, original_name='MinSplashSpeed'
        ),
    })
    max_splash_speed: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x814dfd80, original_name='MaxSplashSpeed'
        ),
    })
    unknown_0xa6bc177f: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa6bc177f, original_name='Unknown'
        ),
    })
    unknown_0x7d034498: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d034498, original_name='Unknown'
        ),
    })
    min_wake_speed: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa4985156, original_name='MinWakeSpeed'
        ),
    })
    texture_align_delay: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x91d5b3ca, original_name='TextureAlignDelay'
        ),
    })
    normal: PuddleControlData = dataclasses.field(default_factory=PuddleControlData, metadata={
        'reflection': FieldReflection[PuddleControlData](
            PuddleControlData, id=0x5ee136e3, original_name='Normal', from_json=PuddleControlData.from_json, to_json=PuddleControlData.to_json
        ),
    })
    explosion: PuddleControlData = dataclasses.field(default_factory=PuddleControlData, metadata={
        'reflection': FieldReflection[PuddleControlData](
            PuddleControlData, id=0xfd6d2b52, original_name='Explosion', from_json=PuddleControlData.from_json, to_json=PuddleControlData.to_json
        ),
    })
    contact: PuddleControlData = dataclasses.field(default_factory=PuddleControlData, metadata={
        'reflection': FieldReflection[PuddleControlData](
            PuddleControlData, id=0x17b1c55e, original_name='Contact', from_json=PuddleControlData.from_json, to_json=PuddleControlData.to_json
        ),
    })
    blob_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2367f689, original_name='BlobEffect'
        ),
    })
    hit_normal_damage: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd473158d, original_name='HitNormalDamage'
        ),
    })
    hit_heavy_damage: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xcca298b4, original_name='HitHeavyDamage'
        ),
    })
    death: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb99c80d3, original_name='Death'
        ),
    })
    explosion_splash: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x96ea9f4b, original_name='ExplosionSplash'
        ),
    })
    contact_splash: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x21655924, original_name='ContactSplash'
        ),
    })
    ball_shell_start: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe482bca4, original_name='BallShellStart'
        ),
    })
    ball_shell_continue: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x812e9cc8, original_name='BallShellContinue'
        ),
    })
    ball_shell_end: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xaeade325, original_name='BallShellEnd'
        ),
    })
    ball_wake: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x10cffad6, original_name='BallWake'
        ),
    })
    ball_wake_end: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x78685eb2, original_name='BallWakeEnd'
        ),
    })
    sound_ball_shell_continue: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7027ee36, original_name='Sound_BallShellContinue'
        ),
    })
    sound_ball_shell_end: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8a53608d, original_name='Sound_BallShellEnd'
        ),
    })
    sound_touch: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf349baac, original_name='Sound_Touch'
        ),
    })
    caud_0x49b30de2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x49b30de2, original_name='CAUD'
        ),
    })
    caud_0xdecd5831: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xdecd5831, original_name='CAUD'
        ),
    })
    sound_death: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1b412c4b, original_name='Sound_Death'
        ),
    })
    vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x7b71ae90, original_name='Vulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    grapple_data: GrappleData = dataclasses.field(default_factory=GrappleData, metadata={
        'reflection': FieldReflection[GrappleData](
            GrappleData, id=0xf609c637, original_name='GrappleData', from_json=GrappleData.from_json, to_json=GrappleData.to_json
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
        if property_count != 40:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c83c012
        projectile = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdb254386
        projectile_delay_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d45ec67
        projectile_delay_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xefdc8306
        min_puddle_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6392404e
        speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd756416e
        contact_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49f4c4ee
        unknown_0x49f4c4ee = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7a47350
        dot_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x955a61ef
        dot_frequency = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77a4efb5
        dot_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x45134ace
        shell_start_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x308d4f23
        splash_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x26797df9
        min_splash_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x814dfd80
        max_splash_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6bc177f
        unknown_0xa6bc177f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d034498
        unknown_0x7d034498 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa4985156
        min_wake_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x91d5b3ca
        texture_align_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5ee136e3
        normal = PuddleControlData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd6d2b52
        explosion = PuddleControlData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x17b1c55e
        contact = PuddleControlData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2367f689
        blob_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd473158d
        hit_normal_damage = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcca298b4
        hit_heavy_damage = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb99c80d3
        death = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x96ea9f4b
        explosion_splash = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x21655924
        contact_splash = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe482bca4
        ball_shell_start = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x812e9cc8
        ball_shell_continue = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaeade325
        ball_shell_end = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x10cffad6
        ball_wake = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78685eb2
        ball_wake_end = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7027ee36
        sound_ball_shell_continue = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a53608d
        sound_ball_shell_end = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf349baac
        sound_touch = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49b30de2
        caud_0x49b30de2 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdecd5831
        caud_0xdecd5831 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b412c4b
        sound_death = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b71ae90
        vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf609c637
        grapple_data = GrappleData.from_stream(data, property_size, default_override={'grapple_type': 1})
    
        return cls(projectile, projectile_delay_min, projectile_delay_max, min_puddle_time, speed, contact_damage, unknown_0x49f4c4ee, dot_damage, dot_frequency, dot_duration, shell_start_duration, splash_delay, min_splash_speed, max_splash_speed, unknown_0xa6bc177f, unknown_0x7d034498, min_wake_speed, texture_align_delay, normal, explosion, contact, blob_effect, hit_normal_damage, hit_heavy_damage, death, explosion_splash, contact_splash, ball_shell_start, ball_shell_continue, ball_shell_end, ball_wake, ball_wake_end, sound_ball_shell_continue, sound_ball_shell_end, sound_touch, caud_0x49b30de2, caud_0xdecd5831, sound_death, vulnerability, grapple_data)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00(')  # 40 properties

        data.write(b',\x83\xc0\x12')  # 0x2c83c012
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.projectile.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdb%C\x86')  # 0xdb254386
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.projectile_delay_min))

        data.write(b'=E\xecg')  # 0x3d45ec67
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.projectile_delay_max))

        data.write(b'\xef\xdc\x83\x06')  # 0xefdc8306
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_puddle_time))

        data.write(b'c\x92@N')  # 0x6392404e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed))

        data.write(b'\xd7VAn')  # 0xd756416e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.contact_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'I\xf4\xc4\xee')  # 0x49f4c4ee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x49f4c4ee))

        data.write(b'\xa7\xa4sP')  # 0xa7a47350
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dot_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x95Za\xef')  # 0x955a61ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dot_frequency))

        data.write(b'w\xa4\xef\xb5')  # 0x77a4efb5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dot_duration))

        data.write(b'E\x13J\xce')  # 0x45134ace
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.shell_start_duration))

        data.write(b'0\x8dO#')  # 0x308d4f23
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.splash_delay))

        data.write(b'&y}\xf9')  # 0x26797df9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_splash_speed))

        data.write(b'\x81M\xfd\x80')  # 0x814dfd80
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_splash_speed))

        data.write(b'\xa6\xbc\x17\x7f')  # 0xa6bc177f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa6bc177f))

        data.write(b'}\x03D\x98')  # 0x7d034498
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7d034498))

        data.write(b'\xa4\x98QV')  # 0xa4985156
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_wake_speed))

        data.write(b'\x91\xd5\xb3\xca')  # 0x91d5b3ca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.texture_align_delay))

        data.write(b'^\xe16\xe3')  # 0x5ee136e3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.normal.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfdm+R')  # 0xfd6d2b52
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.explosion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x17\xb1\xc5^')  # 0x17b1c55e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.contact.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'#g\xf6\x89')  # 0x2367f689
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.blob_effect))

        data.write(b'\xd4s\x15\x8d')  # 0xd473158d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.hit_normal_damage))

        data.write(b'\xcc\xa2\x98\xb4')  # 0xcca298b4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.hit_heavy_damage))

        data.write(b'\xb9\x9c\x80\xd3')  # 0xb99c80d3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.death))

        data.write(b'\x96\xea\x9fK')  # 0x96ea9f4b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.explosion_splash))

        data.write(b'!eY$')  # 0x21655924
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.contact_splash))

        data.write(b'\xe4\x82\xbc\xa4')  # 0xe482bca4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ball_shell_start))

        data.write(b'\x81.\x9c\xc8')  # 0x812e9cc8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ball_shell_continue))

        data.write(b'\xae\xad\xe3%')  # 0xaeade325
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ball_shell_end))

        data.write(b'\x10\xcf\xfa\xd6')  # 0x10cffad6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ball_wake))

        data.write(b'xh^\xb2')  # 0x78685eb2
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ball_wake_end))

        data.write(b"p'\xee6")  # 0x7027ee36
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_ball_shell_continue))

        data.write(b'\x8aS`\x8d')  # 0x8a53608d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_ball_shell_end))

        data.write(b'\xf3I\xba\xac')  # 0xf349baac
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_touch))

        data.write(b'I\xb3\r\xe2')  # 0x49b30de2
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0x49b30de2))

        data.write(b'\xde\xcdX1')  # 0xdecd5831
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0xdecd5831))

        data.write(b'\x1bA,K')  # 0x1b412c4b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_death))

        data.write(b'{q\xae\x90')  # 0x7b71ae90
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf6\t\xc67')  # 0xf609c637
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_data.to_stream(data, default_override={'grapple_type': 1})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct45Json", data)
        return cls(
            projectile=LaunchProjectileData.from_json(json_data['projectile']),
            projectile_delay_min=json_data['projectile_delay_min'],
            projectile_delay_max=json_data['projectile_delay_max'],
            min_puddle_time=json_data['min_puddle_time'],
            speed=json_data['speed'],
            contact_damage=DamageInfo.from_json(json_data['contact_damage']),
            unknown_0x49f4c4ee=json_data['unknown_0x49f4c4ee'],
            dot_damage=DamageInfo.from_json(json_data['dot_damage']),
            dot_frequency=json_data['dot_frequency'],
            dot_duration=json_data['dot_duration'],
            shell_start_duration=json_data['shell_start_duration'],
            splash_delay=json_data['splash_delay'],
            min_splash_speed=json_data['min_splash_speed'],
            max_splash_speed=json_data['max_splash_speed'],
            unknown_0xa6bc177f=json_data['unknown_0xa6bc177f'],
            unknown_0x7d034498=json_data['unknown_0x7d034498'],
            min_wake_speed=json_data['min_wake_speed'],
            texture_align_delay=json_data['texture_align_delay'],
            normal=PuddleControlData.from_json(json_data['normal']),
            explosion=PuddleControlData.from_json(json_data['explosion']),
            contact=PuddleControlData.from_json(json_data['contact']),
            blob_effect=json_data['blob_effect'],
            hit_normal_damage=json_data['hit_normal_damage'],
            hit_heavy_damage=json_data['hit_heavy_damage'],
            death=json_data['death'],
            explosion_splash=json_data['explosion_splash'],
            contact_splash=json_data['contact_splash'],
            ball_shell_start=json_data['ball_shell_start'],
            ball_shell_continue=json_data['ball_shell_continue'],
            ball_shell_end=json_data['ball_shell_end'],
            ball_wake=json_data['ball_wake'],
            ball_wake_end=json_data['ball_wake_end'],
            sound_ball_shell_continue=json_data['sound_ball_shell_continue'],
            sound_ball_shell_end=json_data['sound_ball_shell_end'],
            sound_touch=json_data['sound_touch'],
            caud_0x49b30de2=json_data['caud_0x49b30de2'],
            caud_0xdecd5831=json_data['caud_0xdecd5831'],
            sound_death=json_data['sound_death'],
            vulnerability=DamageVulnerability.from_json(json_data['vulnerability']),
            grapple_data=GrappleData.from_json(json_data['grapple_data']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'projectile': self.projectile.to_json(),
            'projectile_delay_min': self.projectile_delay_min,
            'projectile_delay_max': self.projectile_delay_max,
            'min_puddle_time': self.min_puddle_time,
            'speed': self.speed,
            'contact_damage': self.contact_damage.to_json(),
            'unknown_0x49f4c4ee': self.unknown_0x49f4c4ee,
            'dot_damage': self.dot_damage.to_json(),
            'dot_frequency': self.dot_frequency,
            'dot_duration': self.dot_duration,
            'shell_start_duration': self.shell_start_duration,
            'splash_delay': self.splash_delay,
            'min_splash_speed': self.min_splash_speed,
            'max_splash_speed': self.max_splash_speed,
            'unknown_0xa6bc177f': self.unknown_0xa6bc177f,
            'unknown_0x7d034498': self.unknown_0x7d034498,
            'min_wake_speed': self.min_wake_speed,
            'texture_align_delay': self.texture_align_delay,
            'normal': self.normal.to_json(),
            'explosion': self.explosion.to_json(),
            'contact': self.contact.to_json(),
            'blob_effect': self.blob_effect,
            'hit_normal_damage': self.hit_normal_damage,
            'hit_heavy_damage': self.hit_heavy_damage,
            'death': self.death,
            'explosion_splash': self.explosion_splash,
            'contact_splash': self.contact_splash,
            'ball_shell_start': self.ball_shell_start,
            'ball_shell_continue': self.ball_shell_continue,
            'ball_shell_end': self.ball_shell_end,
            'ball_wake': self.ball_wake,
            'ball_wake_end': self.ball_wake_end,
            'sound_ball_shell_continue': self.sound_ball_shell_continue,
            'sound_ball_shell_end': self.sound_ball_shell_end,
            'sound_touch': self.sound_touch,
            'caud_0x49b30de2': self.caud_0x49b30de2,
            'caud_0xdecd5831': self.caud_0xdecd5831,
            'sound_death': self.sound_death,
            'vulnerability': self.vulnerability.to_json(),
            'grapple_data': self.grapple_data.to_json(),
        }


def _decode_projectile_delay_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_projectile_delay_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_puddle_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x49f4c4ee(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dot_frequency(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dot_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shell_start_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_splash_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_splash_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_splash_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa6bc177f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7d034498(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_wake_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_texture_align_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_blob_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_hit_normal_damage(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_hit_heavy_damage(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_death(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_explosion_splash(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_contact_splash(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ball_shell_start(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ball_shell_continue(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ball_shell_end(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ball_wake(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ball_wake_end(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_ball_shell_continue(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_ball_shell_end(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_touch(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud_0x49b30de2(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud_0xdecd5831(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_death(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_grapple_data(data: typing.BinaryIO, property_size: int) -> GrappleData:
    return GrappleData.from_stream(data, property_size, default_override={'grapple_type': 1})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x2c83c012: ('projectile', LaunchProjectileData.from_stream),
    0xdb254386: ('projectile_delay_min', _decode_projectile_delay_min),
    0x3d45ec67: ('projectile_delay_max', _decode_projectile_delay_max),
    0xefdc8306: ('min_puddle_time', _decode_min_puddle_time),
    0x6392404e: ('speed', _decode_speed),
    0xd756416e: ('contact_damage', DamageInfo.from_stream),
    0x49f4c4ee: ('unknown_0x49f4c4ee', _decode_unknown_0x49f4c4ee),
    0xa7a47350: ('dot_damage', DamageInfo.from_stream),
    0x955a61ef: ('dot_frequency', _decode_dot_frequency),
    0x77a4efb5: ('dot_duration', _decode_dot_duration),
    0x45134ace: ('shell_start_duration', _decode_shell_start_duration),
    0x308d4f23: ('splash_delay', _decode_splash_delay),
    0x26797df9: ('min_splash_speed', _decode_min_splash_speed),
    0x814dfd80: ('max_splash_speed', _decode_max_splash_speed),
    0xa6bc177f: ('unknown_0xa6bc177f', _decode_unknown_0xa6bc177f),
    0x7d034498: ('unknown_0x7d034498', _decode_unknown_0x7d034498),
    0xa4985156: ('min_wake_speed', _decode_min_wake_speed),
    0x91d5b3ca: ('texture_align_delay', _decode_texture_align_delay),
    0x5ee136e3: ('normal', PuddleControlData.from_stream),
    0xfd6d2b52: ('explosion', PuddleControlData.from_stream),
    0x17b1c55e: ('contact', PuddleControlData.from_stream),
    0x2367f689: ('blob_effect', _decode_blob_effect),
    0xd473158d: ('hit_normal_damage', _decode_hit_normal_damage),
    0xcca298b4: ('hit_heavy_damage', _decode_hit_heavy_damage),
    0xb99c80d3: ('death', _decode_death),
    0x96ea9f4b: ('explosion_splash', _decode_explosion_splash),
    0x21655924: ('contact_splash', _decode_contact_splash),
    0xe482bca4: ('ball_shell_start', _decode_ball_shell_start),
    0x812e9cc8: ('ball_shell_continue', _decode_ball_shell_continue),
    0xaeade325: ('ball_shell_end', _decode_ball_shell_end),
    0x10cffad6: ('ball_wake', _decode_ball_wake),
    0x78685eb2: ('ball_wake_end', _decode_ball_wake_end),
    0x7027ee36: ('sound_ball_shell_continue', _decode_sound_ball_shell_continue),
    0x8a53608d: ('sound_ball_shell_end', _decode_sound_ball_shell_end),
    0xf349baac: ('sound_touch', _decode_sound_touch),
    0x49b30de2: ('caud_0x49b30de2', _decode_caud_0x49b30de2),
    0xdecd5831: ('caud_0xdecd5831', _decode_caud_0xdecd5831),
    0x1b412c4b: ('sound_death', _decode_sound_death),
    0x7b71ae90: ('vulnerability', DamageVulnerability.from_stream),
    0xf609c637: ('grapple_data', _decode_grapple_data),
}
