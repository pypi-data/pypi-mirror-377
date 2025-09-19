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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class SpacePirateWeaponDataJson(typing_extensions.TypedDict):
        scale_radial_damage: bool
        unknown_0xa3b45ab5: bool
        unknown_0xa93e9e12: bool
        unknown_0x01c62b32: bool
        unknown_0x71f8b8f4: bool
        unknown_0xc7f4966c: bool
        unknown_0x96db63f9: bool
        can_be_shot_down: bool
        unknown_0x9e20f24e: bool
        unknown_0x51a7ff4c: bool
        unknown_0xe33b92c9: bool
        grenade_model: int
        unknown_0x25f822c4: float
        unknown_0x765e3a20: float
        grenade_damage: json_util.JsonObject
        grenade_damage_hard: json_util.JsonObject
        grenade_damage_elite: json_util.JsonObject
        grenade_explosion: int
        grenade_effect: int
        grenade_trail: int
        grenade_mass: float
        unknown_0xed086ce0: float
        unknown_0x00fc6646: float
        unknown_0xa7c8e63f: float
        unknown_0xa7261cf9: float
        unknown_0xb463fa52: float
        unknown_0x223b58e8: float
        unknown_0x454f16b1: int
        sound_grenade_bounce: int
        sound_grenade_explode: int
        unknown_0xa46a487e: int
        unknown_0x36d1b707: float
        unknown_0xd2ee80b9: float
        unknown_0x95c7f681: float
        unknown_0x9e69bcfb: float
        sound_grenade_flight: int
        caud: int
        sound_stick: int
        unknown_0xbf95a130: json_util.JsonValue
        unknown_0x8b4a07d2: json_util.JsonValue
        part: int
        unknown_0x491bf41d: int
        unknown_0x1fb988f2: float
        unknown_0x32dcc4f9: float
        unknown_0xe1558837: float
    

@dataclasses.dataclass()
class SpacePirateWeaponData(BaseProperty):
    scale_radial_damage: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf1c823a6, original_name='ScaleRadialDamage'
        ),
    })
    unknown_0xa3b45ab5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa3b45ab5, original_name='Unknown'
        ),
    })
    unknown_0xa93e9e12: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa93e9e12, original_name='Unknown'
        ),
    })
    unknown_0x01c62b32: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x01c62b32, original_name='Unknown'
        ),
    })
    unknown_0x71f8b8f4: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x71f8b8f4, original_name='Unknown'
        ),
    })
    unknown_0xc7f4966c: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc7f4966c, original_name='Unknown'
        ),
    })
    unknown_0x96db63f9: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x96db63f9, original_name='Unknown'
        ),
    })
    can_be_shot_down: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0b3bf4c6, original_name='CanBeShotDown'
        ),
    })
    unknown_0x9e20f24e: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x9e20f24e, original_name='Unknown'
        ),
    })
    unknown_0x51a7ff4c: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x51a7ff4c, original_name='Unknown'
        ),
    })
    unknown_0xe33b92c9: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe33b92c9, original_name='Unknown'
        ),
    })
    grenade_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2245a396, original_name='GrenadeModel'
        ),
    })
    unknown_0x25f822c4: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x25f822c4, original_name='Unknown'
        ),
    })
    unknown_0x765e3a20: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x765e3a20, original_name='Unknown'
        ),
    })
    grenade_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x14d1a3a8, original_name='GrenadeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    grenade_damage_hard: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x4dd7c2f9, original_name='GrenadeDamageHard', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    grenade_damage_elite: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x9ae342fb, original_name='GrenadeDamageElite', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    grenade_explosion: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1319e077, original_name='GrenadeExplosion'
        ),
    })
    grenade_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd207ff0f, original_name='GrenadeEffect'
        ),
    })
    grenade_trail: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2b31c882, original_name='GrenadeTrail'
        ),
    })
    grenade_mass: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9a6bb47f, original_name='GrenadeMass'
        ),
    })
    unknown_0xed086ce0: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed086ce0, original_name='Unknown'
        ),
    })
    unknown_0x00fc6646: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00fc6646, original_name='Unknown'
        ),
    })
    unknown_0xa7c8e63f: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa7c8e63f, original_name='Unknown'
        ),
    })
    unknown_0xa7261cf9: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa7261cf9, original_name='Unknown'
        ),
    })
    unknown_0xb463fa52: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb463fa52, original_name='Unknown'
        ),
    })
    unknown_0x223b58e8: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x223b58e8, original_name='Unknown'
        ),
    })
    unknown_0x454f16b1: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x454f16b1, original_name='Unknown'
        ),
    })
    sound_grenade_bounce: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xdfada7c3, original_name='Sound_GrenadeBounce'
        ),
    })
    sound_grenade_explode: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x554b3450, original_name='Sound_GrenadeExplode'
        ),
    })
    unknown_0xa46a487e: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa46a487e, original_name='Unknown'
        ),
    })
    unknown_0x36d1b707: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x36d1b707, original_name='Unknown'
        ),
    })
    unknown_0xd2ee80b9: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd2ee80b9, original_name='Unknown'
        ),
    })
    unknown_0x95c7f681: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95c7f681, original_name='Unknown'
        ),
    })
    unknown_0x9e69bcfb: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9e69bcfb, original_name='Unknown'
        ),
    })
    sound_grenade_flight: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1b7540c8, original_name='Sound_GrenadeFlight'
        ),
    })
    caud: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6c14cd39, original_name='CAUD'
        ),
    })
    sound_stick: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x92802bb3, original_name='Sound_Stick'
        ),
    })
    unknown_0xbf95a130: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xbf95a130, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x8b4a07d2: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x8b4a07d2, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    part: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf769f604, original_name='PART'
        ),
    })
    unknown_0x491bf41d: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x491bf41d, original_name='Unknown'
        ),
    })
    unknown_0x1fb988f2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1fb988f2, original_name='Unknown'
        ),
    })
    unknown_0x32dcc4f9: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x32dcc4f9, original_name='Unknown'
        ),
    })
    unknown_0xe1558837: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe1558837, original_name='Unknown'
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
        if property_count != 45:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf1c823a6
        scale_radial_damage = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa3b45ab5
        unknown_0xa3b45ab5 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa93e9e12
        unknown_0xa93e9e12 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01c62b32
        unknown_0x01c62b32 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71f8b8f4
        unknown_0x71f8b8f4 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc7f4966c
        unknown_0xc7f4966c = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x96db63f9
        unknown_0x96db63f9 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0b3bf4c6
        can_be_shot_down = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9e20f24e
        unknown_0x9e20f24e = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x51a7ff4c
        unknown_0x51a7ff4c = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe33b92c9
        unknown_0xe33b92c9 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2245a396
        grenade_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x25f822c4
        unknown_0x25f822c4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x765e3a20
        unknown_0x765e3a20 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x14d1a3a8
        grenade_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4dd7c2f9
        grenade_damage_hard = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9ae342fb
        grenade_damage_elite = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1319e077
        grenade_explosion = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd207ff0f
        grenade_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b31c882
        grenade_trail = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a6bb47f
        grenade_mass = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed086ce0
        unknown_0xed086ce0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x00fc6646
        unknown_0x00fc6646 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7c8e63f
        unknown_0xa7c8e63f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7261cf9
        unknown_0xa7261cf9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb463fa52
        unknown_0xb463fa52 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x223b58e8
        unknown_0x223b58e8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x454f16b1
        unknown_0x454f16b1 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdfada7c3
        sound_grenade_bounce = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x554b3450
        sound_grenade_explode = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa46a487e
        unknown_0xa46a487e = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x36d1b707
        unknown_0x36d1b707 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd2ee80b9
        unknown_0xd2ee80b9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95c7f681
        unknown_0x95c7f681 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9e69bcfb
        unknown_0x9e69bcfb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b7540c8
        sound_grenade_flight = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c14cd39
        caud = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x92802bb3
        sound_stick = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbf95a130
        unknown_0xbf95a130 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b4a07d2
        unknown_0x8b4a07d2 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf769f604
        part = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x491bf41d
        unknown_0x491bf41d = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1fb988f2
        unknown_0x1fb988f2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32dcc4f9
        unknown_0x32dcc4f9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe1558837
        unknown_0xe1558837 = struct.unpack('>f', data.read(4))[0]
    
        return cls(scale_radial_damage, unknown_0xa3b45ab5, unknown_0xa93e9e12, unknown_0x01c62b32, unknown_0x71f8b8f4, unknown_0xc7f4966c, unknown_0x96db63f9, can_be_shot_down, unknown_0x9e20f24e, unknown_0x51a7ff4c, unknown_0xe33b92c9, grenade_model, unknown_0x25f822c4, unknown_0x765e3a20, grenade_damage, grenade_damage_hard, grenade_damage_elite, grenade_explosion, grenade_effect, grenade_trail, grenade_mass, unknown_0xed086ce0, unknown_0x00fc6646, unknown_0xa7c8e63f, unknown_0xa7261cf9, unknown_0xb463fa52, unknown_0x223b58e8, unknown_0x454f16b1, sound_grenade_bounce, sound_grenade_explode, unknown_0xa46a487e, unknown_0x36d1b707, unknown_0xd2ee80b9, unknown_0x95c7f681, unknown_0x9e69bcfb, sound_grenade_flight, caud, sound_stick, unknown_0xbf95a130, unknown_0x8b4a07d2, part, unknown_0x491bf41d, unknown_0x1fb988f2, unknown_0x32dcc4f9, unknown_0xe1558837)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00-')  # 45 properties

        data.write(b'\xf1\xc8#\xa6')  # 0xf1c823a6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.scale_radial_damage))

        data.write(b'\xa3\xb4Z\xb5')  # 0xa3b45ab5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xa3b45ab5))

        data.write(b'\xa9>\x9e\x12')  # 0xa93e9e12
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xa93e9e12))

        data.write(b'\x01\xc6+2')  # 0x1c62b32
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x01c62b32))

        data.write(b'q\xf8\xb8\xf4')  # 0x71f8b8f4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x71f8b8f4))

        data.write(b'\xc7\xf4\x96l')  # 0xc7f4966c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xc7f4966c))

        data.write(b'\x96\xdbc\xf9')  # 0x96db63f9
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x96db63f9))

        data.write(b'\x0b;\xf4\xc6')  # 0xb3bf4c6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.can_be_shot_down))

        data.write(b'\x9e \xf2N')  # 0x9e20f24e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x9e20f24e))

        data.write(b'Q\xa7\xffL')  # 0x51a7ff4c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x51a7ff4c))

        data.write(b'\xe3;\x92\xc9')  # 0xe33b92c9
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xe33b92c9))

        data.write(b'"E\xa3\x96')  # 0x2245a396
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.grenade_model))

        data.write(b'%\xf8"\xc4')  # 0x25f822c4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x25f822c4))

        data.write(b'v^: ')  # 0x765e3a20
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x765e3a20))

        data.write(b'\x14\xd1\xa3\xa8')  # 0x14d1a3a8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grenade_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'M\xd7\xc2\xf9')  # 0x4dd7c2f9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grenade_damage_hard.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9a\xe3B\xfb')  # 0x9ae342fb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grenade_damage_elite.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x13\x19\xe0w')  # 0x1319e077
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.grenade_explosion))

        data.write(b'\xd2\x07\xff\x0f')  # 0xd207ff0f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.grenade_effect))

        data.write(b'+1\xc8\x82')  # 0x2b31c882
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.grenade_trail))

        data.write(b'\x9ak\xb4\x7f')  # 0x9a6bb47f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grenade_mass))

        data.write(b'\xed\x08l\xe0')  # 0xed086ce0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xed086ce0))

        data.write(b'\x00\xfcfF')  # 0xfc6646
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x00fc6646))

        data.write(b'\xa7\xc8\xe6?')  # 0xa7c8e63f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa7c8e63f))

        data.write(b'\xa7&\x1c\xf9')  # 0xa7261cf9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa7261cf9))

        data.write(b'\xb4c\xfaR')  # 0xb463fa52
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb463fa52))

        data.write(b'";X\xe8')  # 0x223b58e8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x223b58e8))

        data.write(b'EO\x16\xb1')  # 0x454f16b1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x454f16b1))

        data.write(b'\xdf\xad\xa7\xc3')  # 0xdfada7c3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_grenade_bounce))

        data.write(b'UK4P')  # 0x554b3450
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_grenade_explode))

        data.write(b'\xa4jH~')  # 0xa46a487e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.unknown_0xa46a487e))

        data.write(b'6\xd1\xb7\x07')  # 0x36d1b707
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x36d1b707))

        data.write(b'\xd2\xee\x80\xb9')  # 0xd2ee80b9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd2ee80b9))

        data.write(b'\x95\xc7\xf6\x81')  # 0x95c7f681
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95c7f681))

        data.write(b'\x9ei\xbc\xfb')  # 0x9e69bcfb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9e69bcfb))

        data.write(b'\x1bu@\xc8')  # 0x1b7540c8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_grenade_flight))

        data.write(b'l\x14\xcd9')  # 0x6c14cd39
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud))

        data.write(b'\x92\x80+\xb3')  # 0x92802bb3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_stick))

        data.write(b'\xbf\x95\xa10')  # 0xbf95a130
        data.write(b'\x00\x10')  # size
        self.unknown_0xbf95a130.to_stream(data)

        data.write(b'\x8bJ\x07\xd2')  # 0x8b4a07d2
        data.write(b'\x00\x10')  # size
        self.unknown_0x8b4a07d2.to_stream(data)

        data.write(b'\xf7i\xf6\x04')  # 0xf769f604
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part))

        data.write(b'I\x1b\xf4\x1d')  # 0x491bf41d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.unknown_0x491bf41d))

        data.write(b'\x1f\xb9\x88\xf2')  # 0x1fb988f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1fb988f2))

        data.write(b'2\xdc\xc4\xf9')  # 0x32dcc4f9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x32dcc4f9))

        data.write(b'\xe1U\x887')  # 0xe1558837
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe1558837))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpacePirateWeaponDataJson", data)
        return cls(
            scale_radial_damage=json_data['scale_radial_damage'],
            unknown_0xa3b45ab5=json_data['unknown_0xa3b45ab5'],
            unknown_0xa93e9e12=json_data['unknown_0xa93e9e12'],
            unknown_0x01c62b32=json_data['unknown_0x01c62b32'],
            unknown_0x71f8b8f4=json_data['unknown_0x71f8b8f4'],
            unknown_0xc7f4966c=json_data['unknown_0xc7f4966c'],
            unknown_0x96db63f9=json_data['unknown_0x96db63f9'],
            can_be_shot_down=json_data['can_be_shot_down'],
            unknown_0x9e20f24e=json_data['unknown_0x9e20f24e'],
            unknown_0x51a7ff4c=json_data['unknown_0x51a7ff4c'],
            unknown_0xe33b92c9=json_data['unknown_0xe33b92c9'],
            grenade_model=json_data['grenade_model'],
            unknown_0x25f822c4=json_data['unknown_0x25f822c4'],
            unknown_0x765e3a20=json_data['unknown_0x765e3a20'],
            grenade_damage=DamageInfo.from_json(json_data['grenade_damage']),
            grenade_damage_hard=DamageInfo.from_json(json_data['grenade_damage_hard']),
            grenade_damage_elite=DamageInfo.from_json(json_data['grenade_damage_elite']),
            grenade_explosion=json_data['grenade_explosion'],
            grenade_effect=json_data['grenade_effect'],
            grenade_trail=json_data['grenade_trail'],
            grenade_mass=json_data['grenade_mass'],
            unknown_0xed086ce0=json_data['unknown_0xed086ce0'],
            unknown_0x00fc6646=json_data['unknown_0x00fc6646'],
            unknown_0xa7c8e63f=json_data['unknown_0xa7c8e63f'],
            unknown_0xa7261cf9=json_data['unknown_0xa7261cf9'],
            unknown_0xb463fa52=json_data['unknown_0xb463fa52'],
            unknown_0x223b58e8=json_data['unknown_0x223b58e8'],
            unknown_0x454f16b1=json_data['unknown_0x454f16b1'],
            sound_grenade_bounce=json_data['sound_grenade_bounce'],
            sound_grenade_explode=json_data['sound_grenade_explode'],
            unknown_0xa46a487e=json_data['unknown_0xa46a487e'],
            unknown_0x36d1b707=json_data['unknown_0x36d1b707'],
            unknown_0xd2ee80b9=json_data['unknown_0xd2ee80b9'],
            unknown_0x95c7f681=json_data['unknown_0x95c7f681'],
            unknown_0x9e69bcfb=json_data['unknown_0x9e69bcfb'],
            sound_grenade_flight=json_data['sound_grenade_flight'],
            caud=json_data['caud'],
            sound_stick=json_data['sound_stick'],
            unknown_0xbf95a130=Color.from_json(json_data['unknown_0xbf95a130']),
            unknown_0x8b4a07d2=Color.from_json(json_data['unknown_0x8b4a07d2']),
            part=json_data['part'],
            unknown_0x491bf41d=json_data['unknown_0x491bf41d'],
            unknown_0x1fb988f2=json_data['unknown_0x1fb988f2'],
            unknown_0x32dcc4f9=json_data['unknown_0x32dcc4f9'],
            unknown_0xe1558837=json_data['unknown_0xe1558837'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'scale_radial_damage': self.scale_radial_damage,
            'unknown_0xa3b45ab5': self.unknown_0xa3b45ab5,
            'unknown_0xa93e9e12': self.unknown_0xa93e9e12,
            'unknown_0x01c62b32': self.unknown_0x01c62b32,
            'unknown_0x71f8b8f4': self.unknown_0x71f8b8f4,
            'unknown_0xc7f4966c': self.unknown_0xc7f4966c,
            'unknown_0x96db63f9': self.unknown_0x96db63f9,
            'can_be_shot_down': self.can_be_shot_down,
            'unknown_0x9e20f24e': self.unknown_0x9e20f24e,
            'unknown_0x51a7ff4c': self.unknown_0x51a7ff4c,
            'unknown_0xe33b92c9': self.unknown_0xe33b92c9,
            'grenade_model': self.grenade_model,
            'unknown_0x25f822c4': self.unknown_0x25f822c4,
            'unknown_0x765e3a20': self.unknown_0x765e3a20,
            'grenade_damage': self.grenade_damage.to_json(),
            'grenade_damage_hard': self.grenade_damage_hard.to_json(),
            'grenade_damage_elite': self.grenade_damage_elite.to_json(),
            'grenade_explosion': self.grenade_explosion,
            'grenade_effect': self.grenade_effect,
            'grenade_trail': self.grenade_trail,
            'grenade_mass': self.grenade_mass,
            'unknown_0xed086ce0': self.unknown_0xed086ce0,
            'unknown_0x00fc6646': self.unknown_0x00fc6646,
            'unknown_0xa7c8e63f': self.unknown_0xa7c8e63f,
            'unknown_0xa7261cf9': self.unknown_0xa7261cf9,
            'unknown_0xb463fa52': self.unknown_0xb463fa52,
            'unknown_0x223b58e8': self.unknown_0x223b58e8,
            'unknown_0x454f16b1': self.unknown_0x454f16b1,
            'sound_grenade_bounce': self.sound_grenade_bounce,
            'sound_grenade_explode': self.sound_grenade_explode,
            'unknown_0xa46a487e': self.unknown_0xa46a487e,
            'unknown_0x36d1b707': self.unknown_0x36d1b707,
            'unknown_0xd2ee80b9': self.unknown_0xd2ee80b9,
            'unknown_0x95c7f681': self.unknown_0x95c7f681,
            'unknown_0x9e69bcfb': self.unknown_0x9e69bcfb,
            'sound_grenade_flight': self.sound_grenade_flight,
            'caud': self.caud,
            'sound_stick': self.sound_stick,
            'unknown_0xbf95a130': self.unknown_0xbf95a130.to_json(),
            'unknown_0x8b4a07d2': self.unknown_0x8b4a07d2.to_json(),
            'part': self.part,
            'unknown_0x491bf41d': self.unknown_0x491bf41d,
            'unknown_0x1fb988f2': self.unknown_0x1fb988f2,
            'unknown_0x32dcc4f9': self.unknown_0x32dcc4f9,
            'unknown_0xe1558837': self.unknown_0xe1558837,
        }


def _decode_scale_radial_damage(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xa3b45ab5(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xa93e9e12(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x01c62b32(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x71f8b8f4(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xc7f4966c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x96db63f9(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_can_be_shot_down(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x9e20f24e(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x51a7ff4c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xe33b92c9(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_grenade_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x25f822c4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x765e3a20(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grenade_explosion(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_grenade_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_grenade_trail(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_grenade_mass(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xed086ce0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x00fc6646(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa7c8e63f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa7261cf9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb463fa52(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x223b58e8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x454f16b1(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_grenade_bounce(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_grenade_explode(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xa46a487e(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x36d1b707(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd2ee80b9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x95c7f681(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9e69bcfb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_grenade_flight(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_stick(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xbf95a130(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x8b4a07d2(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_part(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x491bf41d(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x1fb988f2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x32dcc4f9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe1558837(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xf1c823a6: ('scale_radial_damage', _decode_scale_radial_damage),
    0xa3b45ab5: ('unknown_0xa3b45ab5', _decode_unknown_0xa3b45ab5),
    0xa93e9e12: ('unknown_0xa93e9e12', _decode_unknown_0xa93e9e12),
    0x1c62b32: ('unknown_0x01c62b32', _decode_unknown_0x01c62b32),
    0x71f8b8f4: ('unknown_0x71f8b8f4', _decode_unknown_0x71f8b8f4),
    0xc7f4966c: ('unknown_0xc7f4966c', _decode_unknown_0xc7f4966c),
    0x96db63f9: ('unknown_0x96db63f9', _decode_unknown_0x96db63f9),
    0xb3bf4c6: ('can_be_shot_down', _decode_can_be_shot_down),
    0x9e20f24e: ('unknown_0x9e20f24e', _decode_unknown_0x9e20f24e),
    0x51a7ff4c: ('unknown_0x51a7ff4c', _decode_unknown_0x51a7ff4c),
    0xe33b92c9: ('unknown_0xe33b92c9', _decode_unknown_0xe33b92c9),
    0x2245a396: ('grenade_model', _decode_grenade_model),
    0x25f822c4: ('unknown_0x25f822c4', _decode_unknown_0x25f822c4),
    0x765e3a20: ('unknown_0x765e3a20', _decode_unknown_0x765e3a20),
    0x14d1a3a8: ('grenade_damage', DamageInfo.from_stream),
    0x4dd7c2f9: ('grenade_damage_hard', DamageInfo.from_stream),
    0x9ae342fb: ('grenade_damage_elite', DamageInfo.from_stream),
    0x1319e077: ('grenade_explosion', _decode_grenade_explosion),
    0xd207ff0f: ('grenade_effect', _decode_grenade_effect),
    0x2b31c882: ('grenade_trail', _decode_grenade_trail),
    0x9a6bb47f: ('grenade_mass', _decode_grenade_mass),
    0xed086ce0: ('unknown_0xed086ce0', _decode_unknown_0xed086ce0),
    0xfc6646: ('unknown_0x00fc6646', _decode_unknown_0x00fc6646),
    0xa7c8e63f: ('unknown_0xa7c8e63f', _decode_unknown_0xa7c8e63f),
    0xa7261cf9: ('unknown_0xa7261cf9', _decode_unknown_0xa7261cf9),
    0xb463fa52: ('unknown_0xb463fa52', _decode_unknown_0xb463fa52),
    0x223b58e8: ('unknown_0x223b58e8', _decode_unknown_0x223b58e8),
    0x454f16b1: ('unknown_0x454f16b1', _decode_unknown_0x454f16b1),
    0xdfada7c3: ('sound_grenade_bounce', _decode_sound_grenade_bounce),
    0x554b3450: ('sound_grenade_explode', _decode_sound_grenade_explode),
    0xa46a487e: ('unknown_0xa46a487e', _decode_unknown_0xa46a487e),
    0x36d1b707: ('unknown_0x36d1b707', _decode_unknown_0x36d1b707),
    0xd2ee80b9: ('unknown_0xd2ee80b9', _decode_unknown_0xd2ee80b9),
    0x95c7f681: ('unknown_0x95c7f681', _decode_unknown_0x95c7f681),
    0x9e69bcfb: ('unknown_0x9e69bcfb', _decode_unknown_0x9e69bcfb),
    0x1b7540c8: ('sound_grenade_flight', _decode_sound_grenade_flight),
    0x6c14cd39: ('caud', _decode_caud),
    0x92802bb3: ('sound_stick', _decode_sound_stick),
    0xbf95a130: ('unknown_0xbf95a130', _decode_unknown_0xbf95a130),
    0x8b4a07d2: ('unknown_0x8b4a07d2', _decode_unknown_0x8b4a07d2),
    0xf769f604: ('part', _decode_part),
    0x491bf41d: ('unknown_0x491bf41d', _decode_unknown_0x491bf41d),
    0x1fb988f2: ('unknown_0x1fb988f2', _decode_unknown_0x1fb988f2),
    0x32dcc4f9: ('unknown_0x32dcc4f9', _decode_unknown_0x32dcc4f9),
    0xe1558837: ('unknown_0xe1558837', _decode_unknown_0xe1558837),
}
