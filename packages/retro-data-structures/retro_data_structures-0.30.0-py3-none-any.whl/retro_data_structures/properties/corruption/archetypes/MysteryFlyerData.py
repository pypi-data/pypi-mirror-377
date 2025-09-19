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
from retro_data_structures.properties.corruption.archetypes.GrappleBlock import GrappleBlock
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class MysteryFlyerDataJson(typing_extensions.TypedDict):
        shot_projectile: int
        shot_damage: json_util.JsonObject
        hover_speed: float
        hover_height: float
        separation_distance: float
        unknown: bool
        grapple_block1: json_util.JsonObject
        grapple_block2: json_util.JsonObject
        grapple_block3: json_util.JsonObject
    

@dataclasses.dataclass()
class MysteryFlyerData(BaseProperty):
    shot_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x51253ba3, original_name='ShotProjectile'
        ),
    })
    shot_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xcea30138, original_name='ShotDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    hover_speed: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x845ef489, original_name='HoverSpeed'
        ),
    })
    hover_height: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc75998aa, original_name='HoverHeight'
        ),
    })
    separation_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x01559f27, original_name='SeparationDistance'
        ),
    })
    unknown: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5f3fffd6, original_name='Unknown'
        ),
    })
    grapple_block1: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0x5f669ba0, original_name='GrappleBlock1', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
        ),
    })
    grapple_block2: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0xe2acf76e, original_name='GrappleBlock2', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
        ),
    })
    grapple_block3: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0x3f3a2eeb, original_name='GrappleBlock3', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
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
        if property_count != 9:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x51253ba3
        shot_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcea30138
        shot_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 4294967295, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x845ef489
        hover_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc75998aa
        hover_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01559f27
        separation_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5f3fffd6
        unknown = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5f669ba0
        grapple_block1 = GrappleBlock.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe2acf76e
        grapple_block2 = GrappleBlock.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3f3a2eeb
        grapple_block3 = GrappleBlock.from_stream(data, property_size)
    
        return cls(shot_projectile, shot_damage, hover_speed, hover_height, separation_distance, unknown, grapple_block1, grapple_block2, grapple_block3)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\t')  # 9 properties

        data.write(b'Q%;\xa3')  # 0x51253ba3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.shot_projectile))

        data.write(b'\xce\xa3\x018')  # 0xcea30138
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shot_damage.to_stream(data, default_override={'di_weapon_type': 4294967295, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x84^\xf4\x89')  # 0x845ef489
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_speed))

        data.write(b'\xc7Y\x98\xaa')  # 0xc75998aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_height))

        data.write(b"\x01U\x9f'")  # 0x1559f27
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.separation_distance))

        data.write(b'_?\xff\xd6')  # 0x5f3fffd6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown))

        data.write(b'_f\x9b\xa0')  # 0x5f669ba0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_block1.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe2\xac\xf7n')  # 0xe2acf76e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_block2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'?:.\xeb')  # 0x3f3a2eeb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_block3.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MysteryFlyerDataJson", data)
        return cls(
            shot_projectile=json_data['shot_projectile'],
            shot_damage=DamageInfo.from_json(json_data['shot_damage']),
            hover_speed=json_data['hover_speed'],
            hover_height=json_data['hover_height'],
            separation_distance=json_data['separation_distance'],
            unknown=json_data['unknown'],
            grapple_block1=GrappleBlock.from_json(json_data['grapple_block1']),
            grapple_block2=GrappleBlock.from_json(json_data['grapple_block2']),
            grapple_block3=GrappleBlock.from_json(json_data['grapple_block3']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'shot_projectile': self.shot_projectile,
            'shot_damage': self.shot_damage.to_json(),
            'hover_speed': self.hover_speed,
            'hover_height': self.hover_height,
            'separation_distance': self.separation_distance,
            'unknown': self.unknown,
            'grapple_block1': self.grapple_block1.to_json(),
            'grapple_block2': self.grapple_block2.to_json(),
            'grapple_block3': self.grapple_block3.to_json(),
        }


def _decode_shot_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_shot_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 4294967295, 'di_damage': 5.0})


def _decode_hover_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hover_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_separation_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x51253ba3: ('shot_projectile', _decode_shot_projectile),
    0xcea30138: ('shot_damage', _decode_shot_damage),
    0x845ef489: ('hover_speed', _decode_hover_speed),
    0xc75998aa: ('hover_height', _decode_hover_height),
    0x1559f27: ('separation_distance', _decode_separation_distance),
    0x5f3fffd6: ('unknown', _decode_unknown),
    0x5f669ba0: ('grapple_block1', GrappleBlock.from_stream),
    0xe2acf76e: ('grapple_block2', GrappleBlock.from_stream),
    0x3f3a2eeb: ('grapple_block3', GrappleBlock.from_stream),
}
