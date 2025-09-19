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
from retro_data_structures.properties.corruption.archetypes.HoverThenHomeProjectile import HoverThenHomeProjectile
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData
from retro_data_structures.properties.corruption.archetypes.ShockWaveInfo import ShockWaveInfo
from retro_data_structures.properties.corruption.archetypes.UnknownStruct16 import UnknownStruct16
from retro_data_structures.properties.corruption.archetypes.UnknownStruct17 import UnknownStruct17
from retro_data_structures.properties.corruption.archetypes.UnknownStruct19 import UnknownStruct19
from retro_data_structures.properties.corruption.archetypes.UnknownStruct20 import UnknownStruct20
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class SeedBoss3DataJson(typing_extensions.TypedDict):
        tail_damage: json_util.JsonObject
        bite_damage: json_util.JsonObject
        hand_swipe_damage: json_util.JsonObject
        damage_info_0xc2fff029: json_util.JsonObject
        shockwave: json_util.JsonObject
        unknown_0x8e2a47ce: float
        shockwave_push_damage: json_util.JsonObject
        fireball: json_util.JsonObject
        fireballs_min: float
        fireballs_max: float
        unknown_struct16: json_util.JsonObject
        caud: int
        launch_projectile_data: json_util.JsonObject
        hover_then_home_projectile: json_util.JsonObject
        ground_fire: int
        ground_fire_damage: json_util.JsonObject
        ground_fire_size: json_util.JsonValue
        sound_ground_fire: int
        unknown_0x980c9fdc: float
        dash_damage: json_util.JsonObject
        unknown_0xa0ace6ae: float
        unknown_0x86ec276a: float
        unknown_0xad422d66: float
        damage_info_0x761d4bf4: json_util.JsonObject
        unknown_0xca2d694d: float
        hover_speed: float
        hover_acceleration: float
        unknown_0x5af9e379: int
        unknown_0x1ffba0fb: int
        unknown_0x9af26c4e: float
        unknown_struct17: json_util.JsonObject
        unknown_struct19: json_util.JsonObject
        unknown_struct20: json_util.JsonObject
        scan_0x6c3a6799: int
        scan_0xe37a0d97: int
        scan_0xd1c7504d: int
        scan_0x1a9b83e8: int
    

@dataclasses.dataclass()
class SeedBoss3Data(BaseProperty):
    tail_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0e995010, original_name='TailDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    bite_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xdf636c4b, original_name='BiteDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    hand_swipe_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x1d5fb7d6, original_name='HandSwipeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_0xc2fff029: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xc2fff029, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    shockwave: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0x3ce6e482, original_name='Shockwave', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })
    unknown_0x8e2a47ce: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8e2a47ce, original_name='Unknown'
        ),
    })
    shockwave_push_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x2ab7e3cc, original_name='ShockwavePushDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    fireball: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0xc1f06d19, original_name='Fireball', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    fireballs_min: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9a509c55, original_name='FireballsMin'
        ),
    })
    fireballs_max: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7c3033b4, original_name='FireballsMax'
        ),
    })
    unknown_struct16: UnknownStruct16 = dataclasses.field(default_factory=UnknownStruct16, metadata={
        'reflection': FieldReflection[UnknownStruct16](
            UnknownStruct16, id=0x40a2fe3e, original_name='UnknownStruct16', from_json=UnknownStruct16.from_json, to_json=UnknownStruct16.to_json
        ),
    })
    caud: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x859c432c, original_name='CAUD'
        ),
    })
    launch_projectile_data: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x1a25a969, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    hover_then_home_projectile: HoverThenHomeProjectile = dataclasses.field(default_factory=HoverThenHomeProjectile, metadata={
        'reflection': FieldReflection[HoverThenHomeProjectile](
            HoverThenHomeProjectile, id=0x29a8b77d, original_name='HoverThenHomeProjectile', from_json=HoverThenHomeProjectile.from_json, to_json=HoverThenHomeProjectile.to_json
        ),
    })
    ground_fire: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb87c2c9b, original_name='GroundFire'
        ),
    })
    ground_fire_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xbe7ea088, original_name='GroundFireDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    ground_fire_size: Vector = dataclasses.field(default_factory=lambda: Vector(x=1.5, y=1.5, z=1.5), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x4ad191db, original_name='GroundFireSize', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    sound_ground_fire: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x47d79eff, original_name='Sound_GroundFire'
        ),
    })
    unknown_0x980c9fdc: float = dataclasses.field(default=500.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x980c9fdc, original_name='Unknown'
        ),
    })
    dash_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xa171456d, original_name='DashDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xa0ace6ae: float = dataclasses.field(default=56.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa0ace6ae, original_name='Unknown'
        ),
    })
    unknown_0x86ec276a: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x86ec276a, original_name='Unknown'
        ),
    })
    unknown_0xad422d66: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad422d66, original_name='Unknown'
        ),
    })
    damage_info_0x761d4bf4: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x761d4bf4, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xca2d694d: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xca2d694d, original_name='Unknown'
        ),
    })
    hover_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x845ef489, original_name='HoverSpeed'
        ),
    })
    hover_acceleration: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd657f545, original_name='HoverAcceleration'
        ),
    })
    unknown_0x5af9e379: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5af9e379, original_name='Unknown'
        ),
    })
    unknown_0x1ffba0fb: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1ffba0fb, original_name='Unknown'
        ),
    })
    unknown_0x9af26c4e: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9af26c4e, original_name='Unknown'
        ),
    })
    unknown_struct17: UnknownStruct17 = dataclasses.field(default_factory=UnknownStruct17, metadata={
        'reflection': FieldReflection[UnknownStruct17](
            UnknownStruct17, id=0x4802add9, original_name='UnknownStruct17', from_json=UnknownStruct17.from_json, to_json=UnknownStruct17.to_json
        ),
    })
    unknown_struct19: UnknownStruct19 = dataclasses.field(default_factory=UnknownStruct19, metadata={
        'reflection': FieldReflection[UnknownStruct19](
            UnknownStruct19, id=0xa00b9ac3, original_name='UnknownStruct19', from_json=UnknownStruct19.from_json, to_json=UnknownStruct19.to_json
        ),
    })
    unknown_struct20: UnknownStruct20 = dataclasses.field(default_factory=UnknownStruct20, metadata={
        'reflection': FieldReflection[UnknownStruct20](
            UnknownStruct20, id=0xf80c8835, original_name='UnknownStruct20', from_json=UnknownStruct20.from_json, to_json=UnknownStruct20.to_json
        ),
    })
    scan_0x6c3a6799: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6c3a6799, original_name='SCAN'
        ),
    })
    scan_0xe37a0d97: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe37a0d97, original_name='SCAN'
        ),
    })
    scan_0xd1c7504d: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd1c7504d, original_name='SCAN'
        ),
    })
    scan_0x1a9b83e8: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1a9b83e8, original_name='SCAN'
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
        if property_count != 37:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0e995010
        tail_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 0.05000000074505806, 'di_knock_back_power': 20.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdf636c4b
        bite_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 2.0, 'di_knock_back_power': 20.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1d5fb7d6
        hand_swipe_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 2.0, 'di_knock_back_power': 20.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc2fff029
        damage_info_0xc2fff029 = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 10.0, 'di_radius': 7.0, 'di_knock_back_power': 20.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3ce6e482
        shockwave = ShockWaveInfo.from_stream(data, property_size, default_override={'duration': 5.0, 'radius': 1.0, 'height': 2.0, 'radial_velocity': 50.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8e2a47ce
        unknown_0x8e2a47ce = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ab7e3cc
        shockwave_push_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 1.0, 'di_knock_back_power': 50.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc1f06d19
        fireball = LaunchProjectileData.from_stream(data, property_size, default_override={'delay': 0.5, 'stop_homing_range': 5.0, 'generate_pickup_chance': 0.5})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a509c55
        fireballs_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7c3033b4
        fireballs_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x40a2fe3e
        unknown_struct16 = UnknownStruct16.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x859c432c
        caud = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a25a969
        launch_projectile_data = LaunchProjectileData.from_stream(data, property_size, default_override={'delay': 0.20000000298023224, 'stop_homing_range': 10.0, 'generate_pickup_chance': 0.25})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x29a8b77d
        hover_then_home_projectile = HoverThenHomeProjectile.from_stream(data, property_size, default_override={'hover_distance': 20.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb87c2c9b
        ground_fire = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe7ea088
        ground_fire_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 0.05000000074505806, 'di_radius': 1.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ad191db
        ground_fire_size = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47d79eff
        sound_ground_fire = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x980c9fdc
        unknown_0x980c9fdc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa171456d
        dash_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 1.0, 'di_knock_back_power': 50.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa0ace6ae
        unknown_0xa0ace6ae = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x86ec276a
        unknown_0x86ec276a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad422d66
        unknown_0xad422d66 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x761d4bf4
        damage_info_0x761d4bf4 = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 10.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xca2d694d
        unknown_0xca2d694d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x845ef489
        hover_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd657f545
        hover_acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5af9e379
        unknown_0x5af9e379 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ffba0fb
        unknown_0x1ffba0fb = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9af26c4e
        unknown_0x9af26c4e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4802add9
        unknown_struct17 = UnknownStruct17.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa00b9ac3
        unknown_struct19 = UnknownStruct19.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf80c8835
        unknown_struct20 = UnknownStruct20.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c3a6799
        scan_0x6c3a6799 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe37a0d97
        scan_0xe37a0d97 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd1c7504d
        scan_0xd1c7504d = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a9b83e8
        scan_0x1a9b83e8 = struct.unpack(">Q", data.read(8))[0]
    
        return cls(tail_damage, bite_damage, hand_swipe_damage, damage_info_0xc2fff029, shockwave, unknown_0x8e2a47ce, shockwave_push_damage, fireball, fireballs_min, fireballs_max, unknown_struct16, caud, launch_projectile_data, hover_then_home_projectile, ground_fire, ground_fire_damage, ground_fire_size, sound_ground_fire, unknown_0x980c9fdc, dash_damage, unknown_0xa0ace6ae, unknown_0x86ec276a, unknown_0xad422d66, damage_info_0x761d4bf4, unknown_0xca2d694d, hover_speed, hover_acceleration, unknown_0x5af9e379, unknown_0x1ffba0fb, unknown_0x9af26c4e, unknown_struct17, unknown_struct19, unknown_struct20, scan_0x6c3a6799, scan_0xe37a0d97, scan_0xd1c7504d, scan_0x1a9b83e8)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00%')  # 37 properties

        data.write(b'\x0e\x99P\x10')  # 0xe995010
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.tail_damage.to_stream(data, default_override={'di_damage': 0.05000000074505806, 'di_knock_back_power': 20.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdfclK')  # 0xdf636c4b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.bite_damage.to_stream(data, default_override={'di_damage': 2.0, 'di_knock_back_power': 20.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1d_\xb7\xd6')  # 0x1d5fb7d6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hand_swipe_damage.to_stream(data, default_override={'di_damage': 2.0, 'di_knock_back_power': 20.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc2\xff\xf0)')  # 0xc2fff029
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0xc2fff029.to_stream(data, default_override={'di_damage': 10.0, 'di_radius': 7.0, 'di_knock_back_power': 20.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'<\xe6\xe4\x82')  # 0x3ce6e482
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shockwave.to_stream(data, default_override={'duration': 5.0, 'radius': 1.0, 'height': 2.0, 'radial_velocity': 50.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8e*G\xce')  # 0x8e2a47ce
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8e2a47ce))

        data.write(b'*\xb7\xe3\xcc')  # 0x2ab7e3cc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shockwave_push_damage.to_stream(data, default_override={'di_damage': 1.0, 'di_knock_back_power': 50.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc1\xf0m\x19')  # 0xc1f06d19
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.fireball.to_stream(data, default_override={'delay': 0.5, 'stop_homing_range': 5.0, 'generate_pickup_chance': 0.5})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9aP\x9cU')  # 0x9a509c55
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fireballs_min))

        data.write(b'|03\xb4')  # 0x7c3033b4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fireballs_max))

        data.write(b'@\xa2\xfe>')  # 0x40a2fe3e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct16.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x85\x9cC,')  # 0x859c432c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud))

        data.write(b'\x1a%\xa9i')  # 0x1a25a969
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data.to_stream(data, default_override={'delay': 0.20000000298023224, 'stop_homing_range': 10.0, 'generate_pickup_chance': 0.25})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b')\xa8\xb7}')  # 0x29a8b77d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hover_then_home_projectile.to_stream(data, default_override={'hover_distance': 20.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb8|,\x9b')  # 0xb87c2c9b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ground_fire))

        data.write(b'\xbe~\xa0\x88')  # 0xbe7ea088
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ground_fire_damage.to_stream(data, default_override={'di_damage': 0.05000000074505806, 'di_radius': 1.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'J\xd1\x91\xdb')  # 0x4ad191db
        data.write(b'\x00\x0c')  # size
        self.ground_fire_size.to_stream(data)

        data.write(b'G\xd7\x9e\xff')  # 0x47d79eff
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_ground_fire))

        data.write(b'\x98\x0c\x9f\xdc')  # 0x980c9fdc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x980c9fdc))

        data.write(b'\xa1qEm')  # 0xa171456d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dash_damage.to_stream(data, default_override={'di_damage': 1.0, 'di_knock_back_power': 50.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa0\xac\xe6\xae')  # 0xa0ace6ae
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa0ace6ae))

        data.write(b"\x86\xec'j")  # 0x86ec276a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x86ec276a))

        data.write(b'\xadB-f')  # 0xad422d66
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xad422d66))

        data.write(b'v\x1dK\xf4')  # 0x761d4bf4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x761d4bf4.to_stream(data, default_override={'di_damage': 10.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xca-iM')  # 0xca2d694d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xca2d694d))

        data.write(b'\x84^\xf4\x89')  # 0x845ef489
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_speed))

        data.write(b'\xd6W\xf5E')  # 0xd657f545
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_acceleration))

        data.write(b'Z\xf9\xe3y')  # 0x5af9e379
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x5af9e379))

        data.write(b'\x1f\xfb\xa0\xfb')  # 0x1ffba0fb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x1ffba0fb))

        data.write(b'\x9a\xf2lN')  # 0x9af26c4e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9af26c4e))

        data.write(b'H\x02\xad\xd9')  # 0x4802add9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct17.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa0\x0b\x9a\xc3')  # 0xa00b9ac3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct19.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf8\x0c\x885')  # 0xf80c8835
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct20.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'l:g\x99')  # 0x6c3a6799
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.scan_0x6c3a6799))

        data.write(b'\xe3z\r\x97')  # 0xe37a0d97
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.scan_0xe37a0d97))

        data.write(b'\xd1\xc7PM')  # 0xd1c7504d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.scan_0xd1c7504d))

        data.write(b'\x1a\x9b\x83\xe8')  # 0x1a9b83e8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.scan_0x1a9b83e8))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SeedBoss3DataJson", data)
        return cls(
            tail_damage=DamageInfo.from_json(json_data['tail_damage']),
            bite_damage=DamageInfo.from_json(json_data['bite_damage']),
            hand_swipe_damage=DamageInfo.from_json(json_data['hand_swipe_damage']),
            damage_info_0xc2fff029=DamageInfo.from_json(json_data['damage_info_0xc2fff029']),
            shockwave=ShockWaveInfo.from_json(json_data['shockwave']),
            unknown_0x8e2a47ce=json_data['unknown_0x8e2a47ce'],
            shockwave_push_damage=DamageInfo.from_json(json_data['shockwave_push_damage']),
            fireball=LaunchProjectileData.from_json(json_data['fireball']),
            fireballs_min=json_data['fireballs_min'],
            fireballs_max=json_data['fireballs_max'],
            unknown_struct16=UnknownStruct16.from_json(json_data['unknown_struct16']),
            caud=json_data['caud'],
            launch_projectile_data=LaunchProjectileData.from_json(json_data['launch_projectile_data']),
            hover_then_home_projectile=HoverThenHomeProjectile.from_json(json_data['hover_then_home_projectile']),
            ground_fire=json_data['ground_fire'],
            ground_fire_damage=DamageInfo.from_json(json_data['ground_fire_damage']),
            ground_fire_size=Vector.from_json(json_data['ground_fire_size']),
            sound_ground_fire=json_data['sound_ground_fire'],
            unknown_0x980c9fdc=json_data['unknown_0x980c9fdc'],
            dash_damage=DamageInfo.from_json(json_data['dash_damage']),
            unknown_0xa0ace6ae=json_data['unknown_0xa0ace6ae'],
            unknown_0x86ec276a=json_data['unknown_0x86ec276a'],
            unknown_0xad422d66=json_data['unknown_0xad422d66'],
            damage_info_0x761d4bf4=DamageInfo.from_json(json_data['damage_info_0x761d4bf4']),
            unknown_0xca2d694d=json_data['unknown_0xca2d694d'],
            hover_speed=json_data['hover_speed'],
            hover_acceleration=json_data['hover_acceleration'],
            unknown_0x5af9e379=json_data['unknown_0x5af9e379'],
            unknown_0x1ffba0fb=json_data['unknown_0x1ffba0fb'],
            unknown_0x9af26c4e=json_data['unknown_0x9af26c4e'],
            unknown_struct17=UnknownStruct17.from_json(json_data['unknown_struct17']),
            unknown_struct19=UnknownStruct19.from_json(json_data['unknown_struct19']),
            unknown_struct20=UnknownStruct20.from_json(json_data['unknown_struct20']),
            scan_0x6c3a6799=json_data['scan_0x6c3a6799'],
            scan_0xe37a0d97=json_data['scan_0xe37a0d97'],
            scan_0xd1c7504d=json_data['scan_0xd1c7504d'],
            scan_0x1a9b83e8=json_data['scan_0x1a9b83e8'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'tail_damage': self.tail_damage.to_json(),
            'bite_damage': self.bite_damage.to_json(),
            'hand_swipe_damage': self.hand_swipe_damage.to_json(),
            'damage_info_0xc2fff029': self.damage_info_0xc2fff029.to_json(),
            'shockwave': self.shockwave.to_json(),
            'unknown_0x8e2a47ce': self.unknown_0x8e2a47ce,
            'shockwave_push_damage': self.shockwave_push_damage.to_json(),
            'fireball': self.fireball.to_json(),
            'fireballs_min': self.fireballs_min,
            'fireballs_max': self.fireballs_max,
            'unknown_struct16': self.unknown_struct16.to_json(),
            'caud': self.caud,
            'launch_projectile_data': self.launch_projectile_data.to_json(),
            'hover_then_home_projectile': self.hover_then_home_projectile.to_json(),
            'ground_fire': self.ground_fire,
            'ground_fire_damage': self.ground_fire_damage.to_json(),
            'ground_fire_size': self.ground_fire_size.to_json(),
            'sound_ground_fire': self.sound_ground_fire,
            'unknown_0x980c9fdc': self.unknown_0x980c9fdc,
            'dash_damage': self.dash_damage.to_json(),
            'unknown_0xa0ace6ae': self.unknown_0xa0ace6ae,
            'unknown_0x86ec276a': self.unknown_0x86ec276a,
            'unknown_0xad422d66': self.unknown_0xad422d66,
            'damage_info_0x761d4bf4': self.damage_info_0x761d4bf4.to_json(),
            'unknown_0xca2d694d': self.unknown_0xca2d694d,
            'hover_speed': self.hover_speed,
            'hover_acceleration': self.hover_acceleration,
            'unknown_0x5af9e379': self.unknown_0x5af9e379,
            'unknown_0x1ffba0fb': self.unknown_0x1ffba0fb,
            'unknown_0x9af26c4e': self.unknown_0x9af26c4e,
            'unknown_struct17': self.unknown_struct17.to_json(),
            'unknown_struct19': self.unknown_struct19.to_json(),
            'unknown_struct20': self.unknown_struct20.to_json(),
            'scan_0x6c3a6799': self.scan_0x6c3a6799,
            'scan_0xe37a0d97': self.scan_0xe37a0d97,
            'scan_0xd1c7504d': self.scan_0xd1c7504d,
            'scan_0x1a9b83e8': self.scan_0x1a9b83e8,
        }


def _decode_tail_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 0.05000000074505806, 'di_knock_back_power': 20.0})


def _decode_bite_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 2.0, 'di_knock_back_power': 20.0})


def _decode_hand_swipe_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 2.0, 'di_knock_back_power': 20.0})


def _decode_damage_info_0xc2fff029(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 10.0, 'di_radius': 7.0, 'di_knock_back_power': 20.0})


def _decode_shockwave(data: typing.BinaryIO, property_size: int) -> ShockWaveInfo:
    return ShockWaveInfo.from_stream(data, property_size, default_override={'duration': 5.0, 'radius': 1.0, 'height': 2.0, 'radial_velocity': 50.0})


def _decode_unknown_0x8e2a47ce(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shockwave_push_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 1.0, 'di_knock_back_power': 50.0})


def _decode_fireball(data: typing.BinaryIO, property_size: int) -> LaunchProjectileData:
    return LaunchProjectileData.from_stream(data, property_size, default_override={'delay': 0.5, 'stop_homing_range': 5.0, 'generate_pickup_chance': 0.5})


def _decode_fireballs_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fireballs_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_caud(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_launch_projectile_data(data: typing.BinaryIO, property_size: int) -> LaunchProjectileData:
    return LaunchProjectileData.from_stream(data, property_size, default_override={'delay': 0.20000000298023224, 'stop_homing_range': 10.0, 'generate_pickup_chance': 0.25})


def _decode_hover_then_home_projectile(data: typing.BinaryIO, property_size: int) -> HoverThenHomeProjectile:
    return HoverThenHomeProjectile.from_stream(data, property_size, default_override={'hover_distance': 20.0})


def _decode_ground_fire(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ground_fire_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 0.05000000074505806, 'di_radius': 1.0})


def _decode_ground_fire_size(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_sound_ground_fire(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x980c9fdc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dash_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 1.0, 'di_knock_back_power': 50.0})


def _decode_unknown_0xa0ace6ae(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x86ec276a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xad422d66(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_damage_info_0x761d4bf4(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 10.0, 'di_knock_back_power': 10.0})


def _decode_unknown_0xca2d694d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hover_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hover_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5af9e379(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x1ffba0fb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x9af26c4e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_0x6c3a6799(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_scan_0xe37a0d97(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_scan_0xd1c7504d(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_scan_0x1a9b83e8(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xe995010: ('tail_damage', _decode_tail_damage),
    0xdf636c4b: ('bite_damage', _decode_bite_damage),
    0x1d5fb7d6: ('hand_swipe_damage', _decode_hand_swipe_damage),
    0xc2fff029: ('damage_info_0xc2fff029', _decode_damage_info_0xc2fff029),
    0x3ce6e482: ('shockwave', _decode_shockwave),
    0x8e2a47ce: ('unknown_0x8e2a47ce', _decode_unknown_0x8e2a47ce),
    0x2ab7e3cc: ('shockwave_push_damage', _decode_shockwave_push_damage),
    0xc1f06d19: ('fireball', _decode_fireball),
    0x9a509c55: ('fireballs_min', _decode_fireballs_min),
    0x7c3033b4: ('fireballs_max', _decode_fireballs_max),
    0x40a2fe3e: ('unknown_struct16', UnknownStruct16.from_stream),
    0x859c432c: ('caud', _decode_caud),
    0x1a25a969: ('launch_projectile_data', _decode_launch_projectile_data),
    0x29a8b77d: ('hover_then_home_projectile', _decode_hover_then_home_projectile),
    0xb87c2c9b: ('ground_fire', _decode_ground_fire),
    0xbe7ea088: ('ground_fire_damage', _decode_ground_fire_damage),
    0x4ad191db: ('ground_fire_size', _decode_ground_fire_size),
    0x47d79eff: ('sound_ground_fire', _decode_sound_ground_fire),
    0x980c9fdc: ('unknown_0x980c9fdc', _decode_unknown_0x980c9fdc),
    0xa171456d: ('dash_damage', _decode_dash_damage),
    0xa0ace6ae: ('unknown_0xa0ace6ae', _decode_unknown_0xa0ace6ae),
    0x86ec276a: ('unknown_0x86ec276a', _decode_unknown_0x86ec276a),
    0xad422d66: ('unknown_0xad422d66', _decode_unknown_0xad422d66),
    0x761d4bf4: ('damage_info_0x761d4bf4', _decode_damage_info_0x761d4bf4),
    0xca2d694d: ('unknown_0xca2d694d', _decode_unknown_0xca2d694d),
    0x845ef489: ('hover_speed', _decode_hover_speed),
    0xd657f545: ('hover_acceleration', _decode_hover_acceleration),
    0x5af9e379: ('unknown_0x5af9e379', _decode_unknown_0x5af9e379),
    0x1ffba0fb: ('unknown_0x1ffba0fb', _decode_unknown_0x1ffba0fb),
    0x9af26c4e: ('unknown_0x9af26c4e', _decode_unknown_0x9af26c4e),
    0x4802add9: ('unknown_struct17', UnknownStruct17.from_stream),
    0xa00b9ac3: ('unknown_struct19', UnknownStruct19.from_stream),
    0xf80c8835: ('unknown_struct20', UnknownStruct20.from_stream),
    0x6c3a6799: ('scan_0x6c3a6799', _decode_scan_0x6c3a6799),
    0xe37a0d97: ('scan_0xe37a0d97', _decode_scan_0xe37a0d97),
    0xd1c7504d: ('scan_0xd1c7504d', _decode_scan_0xd1c7504d),
    0x1a9b83e8: ('scan_0x1a9b83e8', _decode_scan_0x1a9b83e8),
}
