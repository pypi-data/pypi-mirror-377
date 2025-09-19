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
from retro_data_structures.properties.corruption.archetypes.HoverThenHomeProjectile import HoverThenHomeProjectile
from retro_data_structures.properties.corruption.archetypes.PlasmaBeamInfo import PlasmaBeamInfo
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct27Json(typing_extensions.TypedDict):
        unknown_0xb5049bbb: float
        unknown_0x3390e915: float
        unknown_0xf8cc3ab0: float
        unknown_0xe5c90a08: float
        unknown_0x2e95d9ad: float
        scan: int
        unknown_0x00d1aa67: int
        unknown_0xa57b4fac: int
        unknown_0x8836c426: int
        unknown_0xb87c5139: int
        unknown_0x9f566db4: int
        unknown_0xa2aac8e7: int
        unknown_0xf8aca397: int
        unknown_0x80a0b2cb: int
        unknown_0x69ed492e: int
        unknown_0x90419a55: int
        unknown_0x761db727: int
        unknown_0xdcb8af1c: int
        unknown_0x9cfddba8: int
        wpsc_0xf5056d9d: int
        wpsc_0x58dbcc52: int
        part_0x3a6d3a64: int
        pillar_base: int
        pillar_explosion_effect: int
        part_0xe8706e6e: int
        plasma_beam_info_0x6cc7412a: json_util.JsonObject
        homing_missile_projectile: int
        hover_then_home_projectile: json_util.JsonObject
        echo_animation_information: json_util.JsonObject
        echo_explosion: int
        echo_scan: int
        energy_wave_projectile: int
        plasma_beam_info_0xec493f59: json_util.JsonObject
        super_loop_projectile: int
        part_0x8e96e5e4: int
        txtr: int
        unknown_0x4f6e81a8: float
        unknown_0xe8f323f9: int
        caud: int
        unknown_0x8b8b33d9: int
        unknown_0x09133ecd: int
        is_dash_automatically: int
        sound_invulnerable_loop: int
        sound_shockwave: int
    

@dataclasses.dataclass()
class UnknownStruct27(BaseProperty):
    unknown_0xb5049bbb: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb5049bbb, original_name='Unknown'
        ),
    })
    unknown_0x3390e915: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3390e915, original_name='Unknown'
        ),
    })
    unknown_0xf8cc3ab0: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf8cc3ab0, original_name='Unknown'
        ),
    })
    unknown_0xe5c90a08: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe5c90a08, original_name='Unknown'
        ),
    })
    unknown_0x2e95d9ad: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2e95d9ad, original_name='Unknown'
        ),
    })
    scan: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x21e4d323, original_name='SCAN'
        ),
    })
    unknown_0x00d1aa67: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00d1aa67, original_name='Unknown'
        ),
    })
    unknown_0xa57b4fac: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa57b4fac, original_name='Unknown'
        ),
    })
    unknown_0x8836c426: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x8836c426, original_name='Unknown'
        ),
    })
    unknown_0xb87c5139: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb87c5139, original_name='Unknown'
        ),
    })
    unknown_0x9f566db4: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9f566db4, original_name='Unknown'
        ),
    })
    unknown_0xa2aac8e7: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa2aac8e7, original_name='Unknown'
        ),
    })
    unknown_0xf8aca397: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xf8aca397, original_name='Unknown'
        ),
    })
    unknown_0x80a0b2cb: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x80a0b2cb, original_name='Unknown'
        ),
    })
    unknown_0x69ed492e: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x69ed492e, original_name='Unknown'
        ),
    })
    unknown_0x90419a55: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x90419a55, original_name='Unknown'
        ),
    })
    unknown_0x761db727: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x761db727, original_name='Unknown'
        ),
    })
    unknown_0xdcb8af1c: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xdcb8af1c, original_name='Unknown'
        ),
    })
    unknown_0x9cfddba8: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9cfddba8, original_name='Unknown'
        ),
    })
    wpsc_0xf5056d9d: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf5056d9d, original_name='WPSC'
        ),
    })
    wpsc_0x58dbcc52: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x58dbcc52, original_name='WPSC'
        ),
    })
    part_0x3a6d3a64: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3a6d3a64, original_name='PART'
        ),
    })
    pillar_base: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf3d84488, original_name='PillarBase'
        ),
    })
    pillar_explosion_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x49be8a11, original_name='PillarExplosionEffect'
        ),
    })
    part_0xe8706e6e: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe8706e6e, original_name='PART'
        ),
    })
    plasma_beam_info_0x6cc7412a: PlasmaBeamInfo = dataclasses.field(default_factory=PlasmaBeamInfo, metadata={
        'reflection': FieldReflection[PlasmaBeamInfo](
            PlasmaBeamInfo, id=0x6cc7412a, original_name='PlasmaBeamInfo', from_json=PlasmaBeamInfo.from_json, to_json=PlasmaBeamInfo.to_json
        ),
    })
    homing_missile_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xacfd8ea8, original_name='HomingMissileProjectile'
        ),
    })
    hover_then_home_projectile: HoverThenHomeProjectile = dataclasses.field(default_factory=HoverThenHomeProjectile, metadata={
        'reflection': FieldReflection[HoverThenHomeProjectile](
            HoverThenHomeProjectile, id=0xe8fc7798, original_name='HoverThenHomeProjectile', from_json=HoverThenHomeProjectile.from_json, to_json=HoverThenHomeProjectile.to_json
        ),
    })
    echo_animation_information: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x5377d4b5, original_name='EchoAnimationInformation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    echo_explosion: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4c8aee6d, original_name='EchoExplosion'
        ),
    })
    echo_scan: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0b17536c, original_name='EchoScan'
        ),
    })
    energy_wave_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x76c64459, original_name='EnergyWaveProjectile'
        ),
    })
    plasma_beam_info_0xec493f59: PlasmaBeamInfo = dataclasses.field(default_factory=PlasmaBeamInfo, metadata={
        'reflection': FieldReflection[PlasmaBeamInfo](
            PlasmaBeamInfo, id=0xec493f59, original_name='PlasmaBeamInfo', from_json=PlasmaBeamInfo.from_json, to_json=PlasmaBeamInfo.to_json
        ),
    })
    super_loop_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd1d51e35, original_name='SuperLoopProjectile'
        ),
    })
    part_0x8e96e5e4: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8e96e5e4, original_name='PART'
        ),
    })
    txtr: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5b67a4e7, original_name='TXTR'
        ),
    })
    unknown_0x4f6e81a8: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4f6e81a8, original_name='Unknown'
        ),
    })
    unknown_0xe8f323f9: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe8f323f9, original_name='Unknown'
        ),
    })
    caud: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9049a2fb, original_name='CAUD'
        ),
    })
    unknown_0x8b8b33d9: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8b8b33d9, original_name='Unknown'
        ),
    })
    unknown_0x09133ecd: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x09133ecd, original_name='Unknown'
        ),
    })
    is_dash_automatically: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3c67b14e, original_name='IsDashAutomatically'
        ),
    })
    sound_invulnerable_loop: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xaf6889b0, original_name='Sound_InvulnerableLoop'
        ),
    })
    sound_shockwave: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa47e51d3, original_name='Sound_Shockwave'
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
        if property_count != 44:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5049bbb
        unknown_0xb5049bbb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3390e915
        unknown_0x3390e915 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf8cc3ab0
        unknown_0xf8cc3ab0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe5c90a08
        unknown_0xe5c90a08 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2e95d9ad
        unknown_0x2e95d9ad = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x21e4d323
        scan = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x00d1aa67
        unknown_0x00d1aa67 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa57b4fac
        unknown_0xa57b4fac = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8836c426
        unknown_0x8836c426 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb87c5139
        unknown_0xb87c5139 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f566db4
        unknown_0x9f566db4 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa2aac8e7
        unknown_0xa2aac8e7 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf8aca397
        unknown_0xf8aca397 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80a0b2cb
        unknown_0x80a0b2cb = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69ed492e
        unknown_0x69ed492e = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90419a55
        unknown_0x90419a55 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x761db727
        unknown_0x761db727 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdcb8af1c
        unknown_0xdcb8af1c = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9cfddba8
        unknown_0x9cfddba8 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5056d9d
        wpsc_0xf5056d9d = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58dbcc52
        wpsc_0x58dbcc52 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3a6d3a64
        part_0x3a6d3a64 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3d84488
        pillar_base = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49be8a11
        pillar_explosion_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8706e6e
        part_0xe8706e6e = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6cc7412a
        plasma_beam_info_0x6cc7412a = PlasmaBeamInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xacfd8ea8
        homing_missile_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8fc7798
        hover_then_home_projectile = HoverThenHomeProjectile.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5377d4b5
        echo_animation_information = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4c8aee6d
        echo_explosion = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0b17536c
        echo_scan = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76c64459
        energy_wave_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xec493f59
        plasma_beam_info_0xec493f59 = PlasmaBeamInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd1d51e35
        super_loop_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8e96e5e4
        part_0x8e96e5e4 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5b67a4e7
        txtr = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f6e81a8
        unknown_0x4f6e81a8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8f323f9
        unknown_0xe8f323f9 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9049a2fb
        caud = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b8b33d9
        unknown_0x8b8b33d9 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x09133ecd
        unknown_0x09133ecd = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c67b14e
        is_dash_automatically = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaf6889b0
        sound_invulnerable_loop = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa47e51d3
        sound_shockwave = struct.unpack(">Q", data.read(8))[0]
    
        return cls(unknown_0xb5049bbb, unknown_0x3390e915, unknown_0xf8cc3ab0, unknown_0xe5c90a08, unknown_0x2e95d9ad, scan, unknown_0x00d1aa67, unknown_0xa57b4fac, unknown_0x8836c426, unknown_0xb87c5139, unknown_0x9f566db4, unknown_0xa2aac8e7, unknown_0xf8aca397, unknown_0x80a0b2cb, unknown_0x69ed492e, unknown_0x90419a55, unknown_0x761db727, unknown_0xdcb8af1c, unknown_0x9cfddba8, wpsc_0xf5056d9d, wpsc_0x58dbcc52, part_0x3a6d3a64, pillar_base, pillar_explosion_effect, part_0xe8706e6e, plasma_beam_info_0x6cc7412a, homing_missile_projectile, hover_then_home_projectile, echo_animation_information, echo_explosion, echo_scan, energy_wave_projectile, plasma_beam_info_0xec493f59, super_loop_projectile, part_0x8e96e5e4, txtr, unknown_0x4f6e81a8, unknown_0xe8f323f9, caud, unknown_0x8b8b33d9, unknown_0x09133ecd, is_dash_automatically, sound_invulnerable_loop, sound_shockwave)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00,')  # 44 properties

        data.write(b'\xb5\x04\x9b\xbb')  # 0xb5049bbb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb5049bbb))

        data.write(b'3\x90\xe9\x15')  # 0x3390e915
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3390e915))

        data.write(b'\xf8\xcc:\xb0')  # 0xf8cc3ab0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf8cc3ab0))

        data.write(b'\xe5\xc9\n\x08')  # 0xe5c90a08
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe5c90a08))

        data.write(b'.\x95\xd9\xad')  # 0x2e95d9ad
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2e95d9ad))

        data.write(b'!\xe4\xd3#')  # 0x21e4d323
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.scan))

        data.write(b'\x00\xd1\xaag')  # 0xd1aa67
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x00d1aa67))

        data.write(b'\xa5{O\xac')  # 0xa57b4fac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xa57b4fac))

        data.write(b'\x886\xc4&')  # 0x8836c426
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x8836c426))

        data.write(b'\xb8|Q9')  # 0xb87c5139
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xb87c5139))

        data.write(b'\x9fVm\xb4')  # 0x9f566db4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x9f566db4))

        data.write(b'\xa2\xaa\xc8\xe7')  # 0xa2aac8e7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xa2aac8e7))

        data.write(b'\xf8\xac\xa3\x97')  # 0xf8aca397
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xf8aca397))

        data.write(b'\x80\xa0\xb2\xcb')  # 0x80a0b2cb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x80a0b2cb))

        data.write(b'i\xedI.')  # 0x69ed492e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x69ed492e))

        data.write(b'\x90A\x9aU')  # 0x90419a55
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x90419a55))

        data.write(b"v\x1d\xb7'")  # 0x761db727
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x761db727))

        data.write(b'\xdc\xb8\xaf\x1c')  # 0xdcb8af1c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xdcb8af1c))

        data.write(b'\x9c\xfd\xdb\xa8')  # 0x9cfddba8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x9cfddba8))

        data.write(b'\xf5\x05m\x9d')  # 0xf5056d9d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.wpsc_0xf5056d9d))

        data.write(b'X\xdb\xccR')  # 0x58dbcc52
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.wpsc_0x58dbcc52))

        data.write(b':m:d')  # 0x3a6d3a64
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x3a6d3a64))

        data.write(b'\xf3\xd8D\x88')  # 0xf3d84488
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.pillar_base))

        data.write(b'I\xbe\x8a\x11')  # 0x49be8a11
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.pillar_explosion_effect))

        data.write(b'\xe8pnn')  # 0xe8706e6e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0xe8706e6e))

        data.write(b'l\xc7A*')  # 0x6cc7412a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.plasma_beam_info_0x6cc7412a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xac\xfd\x8e\xa8')  # 0xacfd8ea8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.homing_missile_projectile))

        data.write(b'\xe8\xfcw\x98')  # 0xe8fc7798
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hover_then_home_projectile.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'Sw\xd4\xb5')  # 0x5377d4b5
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.echo_animation_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'L\x8a\xeem')  # 0x4c8aee6d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.echo_explosion))

        data.write(b'\x0b\x17Sl')  # 0xb17536c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.echo_scan))

        data.write(b'v\xc6DY')  # 0x76c64459
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.energy_wave_projectile))

        data.write(b'\xecI?Y')  # 0xec493f59
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.plasma_beam_info_0xec493f59.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd1\xd5\x1e5')  # 0xd1d51e35
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.super_loop_projectile))

        data.write(b'\x8e\x96\xe5\xe4')  # 0x8e96e5e4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x8e96e5e4))

        data.write(b'[g\xa4\xe7')  # 0x5b67a4e7
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.txtr))

        data.write(b'On\x81\xa8')  # 0x4f6e81a8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4f6e81a8))

        data.write(b'\xe8\xf3#\xf9')  # 0xe8f323f9
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.unknown_0xe8f323f9))

        data.write(b'\x90I\xa2\xfb')  # 0x9049a2fb
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud))

        data.write(b'\x8b\x8b3\xd9')  # 0x8b8b33d9
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.unknown_0x8b8b33d9))

        data.write(b'\t\x13>\xcd')  # 0x9133ecd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.unknown_0x09133ecd))

        data.write(b'<g\xb1N')  # 0x3c67b14e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.is_dash_automatically))

        data.write(b'\xafh\x89\xb0')  # 0xaf6889b0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_invulnerable_loop))

        data.write(b'\xa4~Q\xd3')  # 0xa47e51d3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_shockwave))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct27Json", data)
        return cls(
            unknown_0xb5049bbb=json_data['unknown_0xb5049bbb'],
            unknown_0x3390e915=json_data['unknown_0x3390e915'],
            unknown_0xf8cc3ab0=json_data['unknown_0xf8cc3ab0'],
            unknown_0xe5c90a08=json_data['unknown_0xe5c90a08'],
            unknown_0x2e95d9ad=json_data['unknown_0x2e95d9ad'],
            scan=json_data['scan'],
            unknown_0x00d1aa67=json_data['unknown_0x00d1aa67'],
            unknown_0xa57b4fac=json_data['unknown_0xa57b4fac'],
            unknown_0x8836c426=json_data['unknown_0x8836c426'],
            unknown_0xb87c5139=json_data['unknown_0xb87c5139'],
            unknown_0x9f566db4=json_data['unknown_0x9f566db4'],
            unknown_0xa2aac8e7=json_data['unknown_0xa2aac8e7'],
            unknown_0xf8aca397=json_data['unknown_0xf8aca397'],
            unknown_0x80a0b2cb=json_data['unknown_0x80a0b2cb'],
            unknown_0x69ed492e=json_data['unknown_0x69ed492e'],
            unknown_0x90419a55=json_data['unknown_0x90419a55'],
            unknown_0x761db727=json_data['unknown_0x761db727'],
            unknown_0xdcb8af1c=json_data['unknown_0xdcb8af1c'],
            unknown_0x9cfddba8=json_data['unknown_0x9cfddba8'],
            wpsc_0xf5056d9d=json_data['wpsc_0xf5056d9d'],
            wpsc_0x58dbcc52=json_data['wpsc_0x58dbcc52'],
            part_0x3a6d3a64=json_data['part_0x3a6d3a64'],
            pillar_base=json_data['pillar_base'],
            pillar_explosion_effect=json_data['pillar_explosion_effect'],
            part_0xe8706e6e=json_data['part_0xe8706e6e'],
            plasma_beam_info_0x6cc7412a=PlasmaBeamInfo.from_json(json_data['plasma_beam_info_0x6cc7412a']),
            homing_missile_projectile=json_data['homing_missile_projectile'],
            hover_then_home_projectile=HoverThenHomeProjectile.from_json(json_data['hover_then_home_projectile']),
            echo_animation_information=AnimationParameters.from_json(json_data['echo_animation_information']),
            echo_explosion=json_data['echo_explosion'],
            echo_scan=json_data['echo_scan'],
            energy_wave_projectile=json_data['energy_wave_projectile'],
            plasma_beam_info_0xec493f59=PlasmaBeamInfo.from_json(json_data['plasma_beam_info_0xec493f59']),
            super_loop_projectile=json_data['super_loop_projectile'],
            part_0x8e96e5e4=json_data['part_0x8e96e5e4'],
            txtr=json_data['txtr'],
            unknown_0x4f6e81a8=json_data['unknown_0x4f6e81a8'],
            unknown_0xe8f323f9=json_data['unknown_0xe8f323f9'],
            caud=json_data['caud'],
            unknown_0x8b8b33d9=json_data['unknown_0x8b8b33d9'],
            unknown_0x09133ecd=json_data['unknown_0x09133ecd'],
            is_dash_automatically=json_data['is_dash_automatically'],
            sound_invulnerable_loop=json_data['sound_invulnerable_loop'],
            sound_shockwave=json_data['sound_shockwave'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xb5049bbb': self.unknown_0xb5049bbb,
            'unknown_0x3390e915': self.unknown_0x3390e915,
            'unknown_0xf8cc3ab0': self.unknown_0xf8cc3ab0,
            'unknown_0xe5c90a08': self.unknown_0xe5c90a08,
            'unknown_0x2e95d9ad': self.unknown_0x2e95d9ad,
            'scan': self.scan,
            'unknown_0x00d1aa67': self.unknown_0x00d1aa67,
            'unknown_0xa57b4fac': self.unknown_0xa57b4fac,
            'unknown_0x8836c426': self.unknown_0x8836c426,
            'unknown_0xb87c5139': self.unknown_0xb87c5139,
            'unknown_0x9f566db4': self.unknown_0x9f566db4,
            'unknown_0xa2aac8e7': self.unknown_0xa2aac8e7,
            'unknown_0xf8aca397': self.unknown_0xf8aca397,
            'unknown_0x80a0b2cb': self.unknown_0x80a0b2cb,
            'unknown_0x69ed492e': self.unknown_0x69ed492e,
            'unknown_0x90419a55': self.unknown_0x90419a55,
            'unknown_0x761db727': self.unknown_0x761db727,
            'unknown_0xdcb8af1c': self.unknown_0xdcb8af1c,
            'unknown_0x9cfddba8': self.unknown_0x9cfddba8,
            'wpsc_0xf5056d9d': self.wpsc_0xf5056d9d,
            'wpsc_0x58dbcc52': self.wpsc_0x58dbcc52,
            'part_0x3a6d3a64': self.part_0x3a6d3a64,
            'pillar_base': self.pillar_base,
            'pillar_explosion_effect': self.pillar_explosion_effect,
            'part_0xe8706e6e': self.part_0xe8706e6e,
            'plasma_beam_info_0x6cc7412a': self.plasma_beam_info_0x6cc7412a.to_json(),
            'homing_missile_projectile': self.homing_missile_projectile,
            'hover_then_home_projectile': self.hover_then_home_projectile.to_json(),
            'echo_animation_information': self.echo_animation_information.to_json(),
            'echo_explosion': self.echo_explosion,
            'echo_scan': self.echo_scan,
            'energy_wave_projectile': self.energy_wave_projectile,
            'plasma_beam_info_0xec493f59': self.plasma_beam_info_0xec493f59.to_json(),
            'super_loop_projectile': self.super_loop_projectile,
            'part_0x8e96e5e4': self.part_0x8e96e5e4,
            'txtr': self.txtr,
            'unknown_0x4f6e81a8': self.unknown_0x4f6e81a8,
            'unknown_0xe8f323f9': self.unknown_0xe8f323f9,
            'caud': self.caud,
            'unknown_0x8b8b33d9': self.unknown_0x8b8b33d9,
            'unknown_0x09133ecd': self.unknown_0x09133ecd,
            'is_dash_automatically': self.is_dash_automatically,
            'sound_invulnerable_loop': self.sound_invulnerable_loop,
            'sound_shockwave': self.sound_shockwave,
        }


def _decode_unknown_0xb5049bbb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3390e915(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf8cc3ab0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe5c90a08(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2e95d9ad(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x00d1aa67(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xa57b4fac(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x8836c426(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xb87c5139(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x9f566db4(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xa2aac8e7(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xf8aca397(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x80a0b2cb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x69ed492e(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x90419a55(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x761db727(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xdcb8af1c(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x9cfddba8(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_wpsc_0xf5056d9d(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_wpsc_0x58dbcc52(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x3a6d3a64(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_pillar_base(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_pillar_explosion_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0xe8706e6e(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_homing_missile_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_echo_explosion(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_echo_scan(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_energy_wave_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_super_loop_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x8e96e5e4(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_txtr(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x4f6e81a8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe8f323f9(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x8b8b33d9(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x09133ecd(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_is_dash_automatically(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_invulnerable_loop(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_shockwave(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb5049bbb: ('unknown_0xb5049bbb', _decode_unknown_0xb5049bbb),
    0x3390e915: ('unknown_0x3390e915', _decode_unknown_0x3390e915),
    0xf8cc3ab0: ('unknown_0xf8cc3ab0', _decode_unknown_0xf8cc3ab0),
    0xe5c90a08: ('unknown_0xe5c90a08', _decode_unknown_0xe5c90a08),
    0x2e95d9ad: ('unknown_0x2e95d9ad', _decode_unknown_0x2e95d9ad),
    0x21e4d323: ('scan', _decode_scan),
    0xd1aa67: ('unknown_0x00d1aa67', _decode_unknown_0x00d1aa67),
    0xa57b4fac: ('unknown_0xa57b4fac', _decode_unknown_0xa57b4fac),
    0x8836c426: ('unknown_0x8836c426', _decode_unknown_0x8836c426),
    0xb87c5139: ('unknown_0xb87c5139', _decode_unknown_0xb87c5139),
    0x9f566db4: ('unknown_0x9f566db4', _decode_unknown_0x9f566db4),
    0xa2aac8e7: ('unknown_0xa2aac8e7', _decode_unknown_0xa2aac8e7),
    0xf8aca397: ('unknown_0xf8aca397', _decode_unknown_0xf8aca397),
    0x80a0b2cb: ('unknown_0x80a0b2cb', _decode_unknown_0x80a0b2cb),
    0x69ed492e: ('unknown_0x69ed492e', _decode_unknown_0x69ed492e),
    0x90419a55: ('unknown_0x90419a55', _decode_unknown_0x90419a55),
    0x761db727: ('unknown_0x761db727', _decode_unknown_0x761db727),
    0xdcb8af1c: ('unknown_0xdcb8af1c', _decode_unknown_0xdcb8af1c),
    0x9cfddba8: ('unknown_0x9cfddba8', _decode_unknown_0x9cfddba8),
    0xf5056d9d: ('wpsc_0xf5056d9d', _decode_wpsc_0xf5056d9d),
    0x58dbcc52: ('wpsc_0x58dbcc52', _decode_wpsc_0x58dbcc52),
    0x3a6d3a64: ('part_0x3a6d3a64', _decode_part_0x3a6d3a64),
    0xf3d84488: ('pillar_base', _decode_pillar_base),
    0x49be8a11: ('pillar_explosion_effect', _decode_pillar_explosion_effect),
    0xe8706e6e: ('part_0xe8706e6e', _decode_part_0xe8706e6e),
    0x6cc7412a: ('plasma_beam_info_0x6cc7412a', PlasmaBeamInfo.from_stream),
    0xacfd8ea8: ('homing_missile_projectile', _decode_homing_missile_projectile),
    0xe8fc7798: ('hover_then_home_projectile', HoverThenHomeProjectile.from_stream),
    0x5377d4b5: ('echo_animation_information', AnimationParameters.from_stream),
    0x4c8aee6d: ('echo_explosion', _decode_echo_explosion),
    0xb17536c: ('echo_scan', _decode_echo_scan),
    0x76c64459: ('energy_wave_projectile', _decode_energy_wave_projectile),
    0xec493f59: ('plasma_beam_info_0xec493f59', PlasmaBeamInfo.from_stream),
    0xd1d51e35: ('super_loop_projectile', _decode_super_loop_projectile),
    0x8e96e5e4: ('part_0x8e96e5e4', _decode_part_0x8e96e5e4),
    0x5b67a4e7: ('txtr', _decode_txtr),
    0x4f6e81a8: ('unknown_0x4f6e81a8', _decode_unknown_0x4f6e81a8),
    0xe8f323f9: ('unknown_0xe8f323f9', _decode_unknown_0xe8f323f9),
    0x9049a2fb: ('caud', _decode_caud),
    0x8b8b33d9: ('unknown_0x8b8b33d9', _decode_unknown_0x8b8b33d9),
    0x9133ecd: ('unknown_0x09133ecd', _decode_unknown_0x09133ecd),
    0x3c67b14e: ('is_dash_automatically', _decode_is_dash_automatically),
    0xaf6889b0: ('sound_invulnerable_loop', _decode_sound_invulnerable_loop),
    0xa47e51d3: ('sound_shockwave', _decode_sound_shockwave),
}
