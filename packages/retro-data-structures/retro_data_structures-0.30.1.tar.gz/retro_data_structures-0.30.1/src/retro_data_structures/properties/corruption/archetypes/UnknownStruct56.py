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
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct56Json(typing_extensions.TypedDict):
        animation: json_util.JsonObject
        roll_speed_scale: float
        unknown_0x205db165: float
        unknown_0x45515b5e: float
        damage_info: json_util.JsonObject
        trail_effect: int
        glow_effect: int
        wall_collision_sound: int
        player_collision_sound: int
        caud: int
    

@dataclasses.dataclass()
class UnknownStruct56(BaseProperty):
    animation: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa3d63f44, original_name='Animation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    roll_speed_scale: float = dataclasses.field(default=1.2999999523162842, metadata={
        'reflection': FieldReflection[float](
            float, id=0x60ac7175, original_name='RollSpeedScale'
        ),
    })
    unknown_0x205db165: float = dataclasses.field(default=3.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x205db165, original_name='Unknown'
        ),
    })
    unknown_0x45515b5e: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x45515b5e, original_name='Unknown'
        ),
    })
    damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xc97013d0, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    trail_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x36eee791, original_name='TrailEffect'
        ),
    })
    glow_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x845bd2ee, original_name='GlowEffect'
        ),
    })
    wall_collision_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4faba78a, original_name='WallCollisionSound'
        ),
    })
    player_collision_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe90069bd, original_name='PlayerCollisionSound'
        ),
    })
    caud: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6ab7c2f5, original_name='CAUD'
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
        if property_count != 10:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa3d63f44
        animation = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x60ac7175
        roll_speed_scale = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x205db165
        unknown_0x205db165 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x45515b5e
        unknown_0x45515b5e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc97013d0
        damage_info = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x36eee791
        trail_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x845bd2ee
        glow_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4faba78a
        wall_collision_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe90069bd
        player_collision_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ab7c2f5
        caud = struct.unpack(">Q", data.read(8))[0]
    
        return cls(animation, roll_speed_scale, unknown_0x205db165, unknown_0x45515b5e, damage_info, trail_effect, glow_effect, wall_collision_sound, player_collision_sound, caud)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\n')  # 10 properties

        data.write(b'\xa3\xd6?D')  # 0xa3d63f44
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'`\xacqu')  # 0x60ac7175
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.roll_speed_scale))

        data.write(b' ]\xb1e')  # 0x205db165
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x205db165))

        data.write(b'EQ[^')  # 0x45515b5e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x45515b5e))

        data.write(b'\xc9p\x13\xd0')  # 0xc97013d0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'6\xee\xe7\x91')  # 0x36eee791
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.trail_effect))

        data.write(b'\x84[\xd2\xee')  # 0x845bd2ee
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.glow_effect))

        data.write(b'O\xab\xa7\x8a')  # 0x4faba78a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.wall_collision_sound))

        data.write(b'\xe9\x00i\xbd')  # 0xe90069bd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.player_collision_sound))

        data.write(b'j\xb7\xc2\xf5')  # 0x6ab7c2f5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct56Json", data)
        return cls(
            animation=AnimationParameters.from_json(json_data['animation']),
            roll_speed_scale=json_data['roll_speed_scale'],
            unknown_0x205db165=json_data['unknown_0x205db165'],
            unknown_0x45515b5e=json_data['unknown_0x45515b5e'],
            damage_info=DamageInfo.from_json(json_data['damage_info']),
            trail_effect=json_data['trail_effect'],
            glow_effect=json_data['glow_effect'],
            wall_collision_sound=json_data['wall_collision_sound'],
            player_collision_sound=json_data['player_collision_sound'],
            caud=json_data['caud'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'animation': self.animation.to_json(),
            'roll_speed_scale': self.roll_speed_scale,
            'unknown_0x205db165': self.unknown_0x205db165,
            'unknown_0x45515b5e': self.unknown_0x45515b5e,
            'damage_info': self.damage_info.to_json(),
            'trail_effect': self.trail_effect,
            'glow_effect': self.glow_effect,
            'wall_collision_sound': self.wall_collision_sound,
            'player_collision_sound': self.player_collision_sound,
            'caud': self.caud,
        }


def _decode_roll_speed_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x205db165(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x45515b5e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_trail_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_glow_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_wall_collision_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_player_collision_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xa3d63f44: ('animation', AnimationParameters.from_stream),
    0x60ac7175: ('roll_speed_scale', _decode_roll_speed_scale),
    0x205db165: ('unknown_0x205db165', _decode_unknown_0x205db165),
    0x45515b5e: ('unknown_0x45515b5e', _decode_unknown_0x45515b5e),
    0xc97013d0: ('damage_info', DamageInfo.from_stream),
    0x36eee791: ('trail_effect', _decode_trail_effect),
    0x845bd2ee: ('glow_effect', _decode_glow_effect),
    0x4faba78a: ('wall_collision_sound', _decode_wall_collision_sound),
    0xe90069bd: ('player_collision_sound', _decode_player_collision_sound),
    0x6ab7c2f5: ('caud', _decode_caud),
}
