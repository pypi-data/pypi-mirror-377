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
from retro_data_structures.properties.corruption.archetypes.GrappleData import GrappleData
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct55Json(typing_extensions.TypedDict):
        ice_armor_back: int
        ice_armor_head: int
        cmdl_0xac0b1ea5: int
        cmdl_0x508bf168: int
        cmdl_0x02e83a7c: int
        cmdl_0xe7c1049e: int
        cmdl_0x2c41e9a5: int
        cmdl_0x152658fe: int
        cmdl_0xe22a6dda: int
        cmdl_0x1eaa8217: int
        part_0x199a4ca5: int
        part_0x9f0e3e0b: int
        part_0x5452edae: int
        part_0x4957dd16: int
        part_0xa13303f4: int
        wpsc_0x3a2d1aa4: int
        wpsc_0xbcb9680a: int
        wpsc_0x77e5bbaf: int
        wpsc_0x6ae08b17: int
        wpsc_0x4584843b: int
        txtr: int
        part_0xc017cf42: int
        cmdl_0x17789d1c: int
        part_0x8843ce6d: int
        missile_frozen_model: int
        frozen_missile_shatter: int
        missile_freeze_effect: int
        ice_spike_explosion: int
        ice_platform_explosion: int
        surfing_particles: int
        part_0x96b50d90: int
        surfing_projectile: int
        surfing_projectile_visor_effect: int
        caud_0x24964375: int
        max_grapple_distance: float
        grapple_data: json_util.JsonObject
        caud_0xaf284f76: int
        caud_0xd2b71804: int
        unknown: int
        scan: int
    

@dataclasses.dataclass()
class UnknownStruct55(BaseProperty):
    ice_armor_back: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1a662787, original_name='IceArmorBack'
        ),
    })
    ice_armor_head: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6dcb001f, original_name='IceArmorHead'
        ),
    })
    cmdl_0xac0b1ea5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xac0b1ea5, original_name='CMDL'
        ),
    })
    cmdl_0x508bf168: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x508bf168, original_name='CMDL'
        ),
    })
    cmdl_0x02e83a7c: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x02e83a7c, original_name='CMDL'
        ),
    })
    cmdl_0xe7c1049e: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe7c1049e, original_name='CMDL'
        ),
    })
    cmdl_0x2c41e9a5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2c41e9a5, original_name='CMDL'
        ),
    })
    cmdl_0x152658fe: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x152658fe, original_name='CMDL'
        ),
    })
    cmdl_0xe22a6dda: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe22a6dda, original_name='CMDL'
        ),
    })
    cmdl_0x1eaa8217: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1eaa8217, original_name='CMDL'
        ),
    })
    part_0x199a4ca5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x199a4ca5, original_name='PART'
        ),
    })
    part_0x9f0e3e0b: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9f0e3e0b, original_name='PART'
        ),
    })
    part_0x5452edae: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5452edae, original_name='PART'
        ),
    })
    part_0x4957dd16: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4957dd16, original_name='PART'
        ),
    })
    part_0xa13303f4: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa13303f4, original_name='PART'
        ),
    })
    wpsc_0x3a2d1aa4: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3a2d1aa4, original_name='WPSC'
        ),
    })
    wpsc_0xbcb9680a: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xbcb9680a, original_name='WPSC'
        ),
    })
    wpsc_0x77e5bbaf: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x77e5bbaf, original_name='WPSC'
        ),
    })
    wpsc_0x6ae08b17: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6ae08b17, original_name='WPSC'
        ),
    })
    wpsc_0x4584843b: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4584843b, original_name='WPSC'
        ),
    })
    txtr: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x03304d0b, original_name='TXTR'
        ),
    })
    part_0xc017cf42: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc017cf42, original_name='PART'
        ),
    })
    cmdl_0x17789d1c: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x17789d1c, original_name='CMDL'
        ),
    })
    part_0x8843ce6d: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8843ce6d, original_name='PART'
        ),
    })
    missile_frozen_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe039c4bd, original_name='MissileFrozenModel'
        ),
    })
    frozen_missile_shatter: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x09c8db87, original_name='FrozenMissileShatter'
        ),
    })
    missile_freeze_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xcbb55845, original_name='MissileFreezeEffect'
        ),
    })
    ice_spike_explosion: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xedccf9f6, original_name='IceSpikeExplosion'
        ),
    })
    ice_platform_explosion: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9873172a, original_name='IcePlatformExplosion'
        ),
    })
    surfing_particles: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x84c33da6, original_name='SurfingParticles'
        ),
    })
    part_0x96b50d90: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x96b50d90, original_name='PART'
        ),
    })
    surfing_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x757060d4, original_name='SurfingProjectile'
        ),
    })
    surfing_projectile_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa2687ce4, original_name='SurfingProjectileVisorEffect'
        ),
    })
    caud_0x24964375: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x24964375, original_name='CAUD'
        ),
    })
    max_grapple_distance: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1cc93984, original_name='MaxGrappleDistance'
        ),
    })
    grapple_data: GrappleData = dataclasses.field(default_factory=GrappleData, metadata={
        'reflection': FieldReflection[GrappleData](
            GrappleData, id=0xf609c637, original_name='GrappleData', from_json=GrappleData.from_json, to_json=GrappleData.to_json
        ),
    })
    caud_0xaf284f76: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xaf284f76, original_name='CAUD'
        ),
    })
    caud_0xd2b71804: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd2b71804, original_name='CAUD'
        ),
    })
    unknown: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf69bed49, original_name='Unknown'
        ),
    })
    scan: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3d6768d8, original_name='SCAN'
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
        assert property_id == 0x1a662787
        ice_armor_back = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6dcb001f
        ice_armor_head = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xac0b1ea5
        cmdl_0xac0b1ea5 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x508bf168
        cmdl_0x508bf168 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x02e83a7c
        cmdl_0x02e83a7c = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe7c1049e
        cmdl_0xe7c1049e = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c41e9a5
        cmdl_0x2c41e9a5 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x152658fe
        cmdl_0x152658fe = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe22a6dda
        cmdl_0xe22a6dda = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1eaa8217
        cmdl_0x1eaa8217 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x199a4ca5
        part_0x199a4ca5 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f0e3e0b
        part_0x9f0e3e0b = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5452edae
        part_0x5452edae = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4957dd16
        part_0x4957dd16 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa13303f4
        part_0xa13303f4 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3a2d1aa4
        wpsc_0x3a2d1aa4 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbcb9680a
        wpsc_0xbcb9680a = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77e5bbaf
        wpsc_0x77e5bbaf = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ae08b17
        wpsc_0x6ae08b17 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4584843b
        wpsc_0x4584843b = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03304d0b
        txtr = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc017cf42
        part_0xc017cf42 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x17789d1c
        cmdl_0x17789d1c = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8843ce6d
        part_0x8843ce6d = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe039c4bd
        missile_frozen_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x09c8db87
        frozen_missile_shatter = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcbb55845
        missile_freeze_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xedccf9f6
        ice_spike_explosion = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9873172a
        ice_platform_explosion = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84c33da6
        surfing_particles = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x96b50d90
        part_0x96b50d90 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x757060d4
        surfing_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa2687ce4
        surfing_projectile_visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24964375
        caud_0x24964375 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1cc93984
        max_grapple_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf609c637
        grapple_data = GrappleData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaf284f76
        caud_0xaf284f76 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd2b71804
        caud_0xd2b71804 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf69bed49
        unknown = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d6768d8
        scan = struct.unpack(">Q", data.read(8))[0]
    
        return cls(ice_armor_back, ice_armor_head, cmdl_0xac0b1ea5, cmdl_0x508bf168, cmdl_0x02e83a7c, cmdl_0xe7c1049e, cmdl_0x2c41e9a5, cmdl_0x152658fe, cmdl_0xe22a6dda, cmdl_0x1eaa8217, part_0x199a4ca5, part_0x9f0e3e0b, part_0x5452edae, part_0x4957dd16, part_0xa13303f4, wpsc_0x3a2d1aa4, wpsc_0xbcb9680a, wpsc_0x77e5bbaf, wpsc_0x6ae08b17, wpsc_0x4584843b, txtr, part_0xc017cf42, cmdl_0x17789d1c, part_0x8843ce6d, missile_frozen_model, frozen_missile_shatter, missile_freeze_effect, ice_spike_explosion, ice_platform_explosion, surfing_particles, part_0x96b50d90, surfing_projectile, surfing_projectile_visor_effect, caud_0x24964375, max_grapple_distance, grapple_data, caud_0xaf284f76, caud_0xd2b71804, unknown, scan)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00(')  # 40 properties

        data.write(b"\x1af'\x87")  # 0x1a662787
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ice_armor_back))

        data.write(b'm\xcb\x00\x1f')  # 0x6dcb001f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ice_armor_head))

        data.write(b'\xac\x0b\x1e\xa5')  # 0xac0b1ea5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0xac0b1ea5))

        data.write(b'P\x8b\xf1h')  # 0x508bf168
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x508bf168))

        data.write(b'\x02\xe8:|')  # 0x2e83a7c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x02e83a7c))

        data.write(b'\xe7\xc1\x04\x9e')  # 0xe7c1049e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0xe7c1049e))

        data.write(b',A\xe9\xa5')  # 0x2c41e9a5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x2c41e9a5))

        data.write(b'\x15&X\xfe')  # 0x152658fe
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x152658fe))

        data.write(b'\xe2*m\xda')  # 0xe22a6dda
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0xe22a6dda))

        data.write(b'\x1e\xaa\x82\x17')  # 0x1eaa8217
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x1eaa8217))

        data.write(b'\x19\x9aL\xa5')  # 0x199a4ca5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x199a4ca5))

        data.write(b'\x9f\x0e>\x0b')  # 0x9f0e3e0b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x9f0e3e0b))

        data.write(b'TR\xed\xae')  # 0x5452edae
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x5452edae))

        data.write(b'IW\xdd\x16')  # 0x4957dd16
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x4957dd16))

        data.write(b'\xa13\x03\xf4')  # 0xa13303f4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0xa13303f4))

        data.write(b':-\x1a\xa4')  # 0x3a2d1aa4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.wpsc_0x3a2d1aa4))

        data.write(b'\xbc\xb9h\n')  # 0xbcb9680a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.wpsc_0xbcb9680a))

        data.write(b'w\xe5\xbb\xaf')  # 0x77e5bbaf
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.wpsc_0x77e5bbaf))

        data.write(b'j\xe0\x8b\x17')  # 0x6ae08b17
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.wpsc_0x6ae08b17))

        data.write(b'E\x84\x84;')  # 0x4584843b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.wpsc_0x4584843b))

        data.write(b'\x030M\x0b')  # 0x3304d0b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.txtr))

        data.write(b'\xc0\x17\xcfB')  # 0xc017cf42
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0xc017cf42))

        data.write(b'\x17x\x9d\x1c')  # 0x17789d1c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x17789d1c))

        data.write(b'\x88C\xcem')  # 0x8843ce6d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x8843ce6d))

        data.write(b'\xe09\xc4\xbd')  # 0xe039c4bd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.missile_frozen_model))

        data.write(b'\t\xc8\xdb\x87')  # 0x9c8db87
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.frozen_missile_shatter))

        data.write(b'\xcb\xb5XE')  # 0xcbb55845
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.missile_freeze_effect))

        data.write(b'\xed\xcc\xf9\xf6')  # 0xedccf9f6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ice_spike_explosion))

        data.write(b'\x98s\x17*')  # 0x9873172a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ice_platform_explosion))

        data.write(b'\x84\xc3=\xa6')  # 0x84c33da6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.surfing_particles))

        data.write(b'\x96\xb5\r\x90')  # 0x96b50d90
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x96b50d90))

        data.write(b'up`\xd4')  # 0x757060d4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.surfing_projectile))

        data.write(b'\xa2h|\xe4')  # 0xa2687ce4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.surfing_projectile_visor_effect))

        data.write(b'$\x96Cu')  # 0x24964375
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0x24964375))

        data.write(b'\x1c\xc99\x84')  # 0x1cc93984
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_grapple_distance))

        data.write(b'\xf6\t\xc67')  # 0xf609c637
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xaf(Ov')  # 0xaf284f76
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0xaf284f76))

        data.write(b'\xd2\xb7\x18\x04')  # 0xd2b71804
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0xd2b71804))

        data.write(b'\xf6\x9b\xedI')  # 0xf69bed49
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.unknown))

        data.write(b'=gh\xd8')  # 0x3d6768d8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.scan))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct55Json", data)
        return cls(
            ice_armor_back=json_data['ice_armor_back'],
            ice_armor_head=json_data['ice_armor_head'],
            cmdl_0xac0b1ea5=json_data['cmdl_0xac0b1ea5'],
            cmdl_0x508bf168=json_data['cmdl_0x508bf168'],
            cmdl_0x02e83a7c=json_data['cmdl_0x02e83a7c'],
            cmdl_0xe7c1049e=json_data['cmdl_0xe7c1049e'],
            cmdl_0x2c41e9a5=json_data['cmdl_0x2c41e9a5'],
            cmdl_0x152658fe=json_data['cmdl_0x152658fe'],
            cmdl_0xe22a6dda=json_data['cmdl_0xe22a6dda'],
            cmdl_0x1eaa8217=json_data['cmdl_0x1eaa8217'],
            part_0x199a4ca5=json_data['part_0x199a4ca5'],
            part_0x9f0e3e0b=json_data['part_0x9f0e3e0b'],
            part_0x5452edae=json_data['part_0x5452edae'],
            part_0x4957dd16=json_data['part_0x4957dd16'],
            part_0xa13303f4=json_data['part_0xa13303f4'],
            wpsc_0x3a2d1aa4=json_data['wpsc_0x3a2d1aa4'],
            wpsc_0xbcb9680a=json_data['wpsc_0xbcb9680a'],
            wpsc_0x77e5bbaf=json_data['wpsc_0x77e5bbaf'],
            wpsc_0x6ae08b17=json_data['wpsc_0x6ae08b17'],
            wpsc_0x4584843b=json_data['wpsc_0x4584843b'],
            txtr=json_data['txtr'],
            part_0xc017cf42=json_data['part_0xc017cf42'],
            cmdl_0x17789d1c=json_data['cmdl_0x17789d1c'],
            part_0x8843ce6d=json_data['part_0x8843ce6d'],
            missile_frozen_model=json_data['missile_frozen_model'],
            frozen_missile_shatter=json_data['frozen_missile_shatter'],
            missile_freeze_effect=json_data['missile_freeze_effect'],
            ice_spike_explosion=json_data['ice_spike_explosion'],
            ice_platform_explosion=json_data['ice_platform_explosion'],
            surfing_particles=json_data['surfing_particles'],
            part_0x96b50d90=json_data['part_0x96b50d90'],
            surfing_projectile=json_data['surfing_projectile'],
            surfing_projectile_visor_effect=json_data['surfing_projectile_visor_effect'],
            caud_0x24964375=json_data['caud_0x24964375'],
            max_grapple_distance=json_data['max_grapple_distance'],
            grapple_data=GrappleData.from_json(json_data['grapple_data']),
            caud_0xaf284f76=json_data['caud_0xaf284f76'],
            caud_0xd2b71804=json_data['caud_0xd2b71804'],
            unknown=json_data['unknown'],
            scan=json_data['scan'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'ice_armor_back': self.ice_armor_back,
            'ice_armor_head': self.ice_armor_head,
            'cmdl_0xac0b1ea5': self.cmdl_0xac0b1ea5,
            'cmdl_0x508bf168': self.cmdl_0x508bf168,
            'cmdl_0x02e83a7c': self.cmdl_0x02e83a7c,
            'cmdl_0xe7c1049e': self.cmdl_0xe7c1049e,
            'cmdl_0x2c41e9a5': self.cmdl_0x2c41e9a5,
            'cmdl_0x152658fe': self.cmdl_0x152658fe,
            'cmdl_0xe22a6dda': self.cmdl_0xe22a6dda,
            'cmdl_0x1eaa8217': self.cmdl_0x1eaa8217,
            'part_0x199a4ca5': self.part_0x199a4ca5,
            'part_0x9f0e3e0b': self.part_0x9f0e3e0b,
            'part_0x5452edae': self.part_0x5452edae,
            'part_0x4957dd16': self.part_0x4957dd16,
            'part_0xa13303f4': self.part_0xa13303f4,
            'wpsc_0x3a2d1aa4': self.wpsc_0x3a2d1aa4,
            'wpsc_0xbcb9680a': self.wpsc_0xbcb9680a,
            'wpsc_0x77e5bbaf': self.wpsc_0x77e5bbaf,
            'wpsc_0x6ae08b17': self.wpsc_0x6ae08b17,
            'wpsc_0x4584843b': self.wpsc_0x4584843b,
            'txtr': self.txtr,
            'part_0xc017cf42': self.part_0xc017cf42,
            'cmdl_0x17789d1c': self.cmdl_0x17789d1c,
            'part_0x8843ce6d': self.part_0x8843ce6d,
            'missile_frozen_model': self.missile_frozen_model,
            'frozen_missile_shatter': self.frozen_missile_shatter,
            'missile_freeze_effect': self.missile_freeze_effect,
            'ice_spike_explosion': self.ice_spike_explosion,
            'ice_platform_explosion': self.ice_platform_explosion,
            'surfing_particles': self.surfing_particles,
            'part_0x96b50d90': self.part_0x96b50d90,
            'surfing_projectile': self.surfing_projectile,
            'surfing_projectile_visor_effect': self.surfing_projectile_visor_effect,
            'caud_0x24964375': self.caud_0x24964375,
            'max_grapple_distance': self.max_grapple_distance,
            'grapple_data': self.grapple_data.to_json(),
            'caud_0xaf284f76': self.caud_0xaf284f76,
            'caud_0xd2b71804': self.caud_0xd2b71804,
            'unknown': self.unknown,
            'scan': self.scan,
        }


def _decode_ice_armor_back(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ice_armor_head(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0xac0b1ea5(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x508bf168(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x02e83a7c(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0xe7c1049e(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x2c41e9a5(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x152658fe(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0xe22a6dda(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x1eaa8217(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x199a4ca5(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x9f0e3e0b(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x5452edae(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x4957dd16(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0xa13303f4(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_wpsc_0x3a2d1aa4(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_wpsc_0xbcb9680a(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_wpsc_0x77e5bbaf(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_wpsc_0x6ae08b17(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_wpsc_0x4584843b(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_txtr(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0xc017cf42(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x17789d1c(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x8843ce6d(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_missile_frozen_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_frozen_missile_shatter(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_missile_freeze_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ice_spike_explosion(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ice_platform_explosion(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_surfing_particles(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x96b50d90(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_surfing_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_surfing_projectile_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud_0x24964375(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_max_grapple_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_caud_0xaf284f76(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud_0xd2b71804(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_scan(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1a662787: ('ice_armor_back', _decode_ice_armor_back),
    0x6dcb001f: ('ice_armor_head', _decode_ice_armor_head),
    0xac0b1ea5: ('cmdl_0xac0b1ea5', _decode_cmdl_0xac0b1ea5),
    0x508bf168: ('cmdl_0x508bf168', _decode_cmdl_0x508bf168),
    0x2e83a7c: ('cmdl_0x02e83a7c', _decode_cmdl_0x02e83a7c),
    0xe7c1049e: ('cmdl_0xe7c1049e', _decode_cmdl_0xe7c1049e),
    0x2c41e9a5: ('cmdl_0x2c41e9a5', _decode_cmdl_0x2c41e9a5),
    0x152658fe: ('cmdl_0x152658fe', _decode_cmdl_0x152658fe),
    0xe22a6dda: ('cmdl_0xe22a6dda', _decode_cmdl_0xe22a6dda),
    0x1eaa8217: ('cmdl_0x1eaa8217', _decode_cmdl_0x1eaa8217),
    0x199a4ca5: ('part_0x199a4ca5', _decode_part_0x199a4ca5),
    0x9f0e3e0b: ('part_0x9f0e3e0b', _decode_part_0x9f0e3e0b),
    0x5452edae: ('part_0x5452edae', _decode_part_0x5452edae),
    0x4957dd16: ('part_0x4957dd16', _decode_part_0x4957dd16),
    0xa13303f4: ('part_0xa13303f4', _decode_part_0xa13303f4),
    0x3a2d1aa4: ('wpsc_0x3a2d1aa4', _decode_wpsc_0x3a2d1aa4),
    0xbcb9680a: ('wpsc_0xbcb9680a', _decode_wpsc_0xbcb9680a),
    0x77e5bbaf: ('wpsc_0x77e5bbaf', _decode_wpsc_0x77e5bbaf),
    0x6ae08b17: ('wpsc_0x6ae08b17', _decode_wpsc_0x6ae08b17),
    0x4584843b: ('wpsc_0x4584843b', _decode_wpsc_0x4584843b),
    0x3304d0b: ('txtr', _decode_txtr),
    0xc017cf42: ('part_0xc017cf42', _decode_part_0xc017cf42),
    0x17789d1c: ('cmdl_0x17789d1c', _decode_cmdl_0x17789d1c),
    0x8843ce6d: ('part_0x8843ce6d', _decode_part_0x8843ce6d),
    0xe039c4bd: ('missile_frozen_model', _decode_missile_frozen_model),
    0x9c8db87: ('frozen_missile_shatter', _decode_frozen_missile_shatter),
    0xcbb55845: ('missile_freeze_effect', _decode_missile_freeze_effect),
    0xedccf9f6: ('ice_spike_explosion', _decode_ice_spike_explosion),
    0x9873172a: ('ice_platform_explosion', _decode_ice_platform_explosion),
    0x84c33da6: ('surfing_particles', _decode_surfing_particles),
    0x96b50d90: ('part_0x96b50d90', _decode_part_0x96b50d90),
    0x757060d4: ('surfing_projectile', _decode_surfing_projectile),
    0xa2687ce4: ('surfing_projectile_visor_effect', _decode_surfing_projectile_visor_effect),
    0x24964375: ('caud_0x24964375', _decode_caud_0x24964375),
    0x1cc93984: ('max_grapple_distance', _decode_max_grapple_distance),
    0xf609c637: ('grapple_data', GrappleData.from_stream),
    0xaf284f76: ('caud_0xaf284f76', _decode_caud_0xaf284f76),
    0xd2b71804: ('caud_0xd2b71804', _decode_caud_0xd2b71804),
    0xf69bed49: ('unknown', _decode_unknown),
    0x3d6768d8: ('scan', _decode_scan),
}
