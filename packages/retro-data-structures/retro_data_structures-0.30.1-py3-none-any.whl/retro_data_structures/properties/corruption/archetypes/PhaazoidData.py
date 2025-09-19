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
from retro_data_structures.properties.corruption.archetypes.ShockWaveInfo import ShockWaveInfo
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class PhaazoidDataJson(typing_extensions.TypedDict):
        stage: int
        unknown_0x02a3e092: bool
        play_initial_anim: bool
        acceleration: float
        max_speed: float
        min_attack_dist: float
        max_attack_dist: float
        unknown_0xb5d19503: float
        unknown_0xe2dfc540: float
        moving_map_opacity: float
        unknown_0xd04a6e1c: float
        shock_wave_info: json_util.JsonObject
        phaazoid_projectile: int
        damage_info: json_util.JsonObject
    

@dataclasses.dataclass()
class PhaazoidData(BaseProperty):
    stage: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb25774e2, original_name='Stage'
        ),
    })
    unknown_0x02a3e092: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x02a3e092, original_name='Unknown'
        ),
    })
    play_initial_anim: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x88fde98c, original_name='PlayInitialAnim'
        ),
    })
    acceleration: float = dataclasses.field(default=65.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x39fb7978, original_name='Acceleration'
        ),
    })
    max_speed: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x82db0cbe, original_name='MaxSpeed'
        ),
    })
    min_attack_dist: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d7447b4, original_name='MinAttackDist'
        ),
    })
    max_attack_dist: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2ed25f50, original_name='MaxAttackDist'
        ),
    })
    unknown_0xb5d19503: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb5d19503, original_name='Unknown'
        ),
    })
    unknown_0xe2dfc540: float = dataclasses.field(default=3.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe2dfc540, original_name='Unknown'
        ),
    })
    moving_map_opacity: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3317d0c6, original_name='MovingMapOpacity'
        ),
    })
    unknown_0xd04a6e1c: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd04a6e1c, original_name='Unknown'
        ),
    })
    shock_wave_info: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0x12b8e543, original_name='ShockWaveInfo', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })
    phaazoid_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe8cd9627, original_name='PhaazoidProjectile'
        ),
    })
    damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x1dc69e38, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
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
        if property_count != 14:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb25774e2
        stage = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x02a3e092
        unknown_0x02a3e092 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88fde98c
        play_initial_anim = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x39fb7978
        acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x82db0cbe
        max_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d7447b4
        min_attack_dist = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ed25f50
        max_attack_dist = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5d19503
        unknown_0xb5d19503 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe2dfc540
        unknown_0xe2dfc540 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3317d0c6
        moving_map_opacity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd04a6e1c
        unknown_0xd04a6e1c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12b8e543
        shock_wave_info = ShockWaveInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8cd9627
        phaazoid_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1dc69e38
        damage_info = DamageInfo.from_stream(data, property_size)
    
        return cls(stage, unknown_0x02a3e092, play_initial_anim, acceleration, max_speed, min_attack_dist, max_attack_dist, unknown_0xb5d19503, unknown_0xe2dfc540, moving_map_opacity, unknown_0xd04a6e1c, shock_wave_info, phaazoid_projectile, damage_info)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'\xb2Wt\xe2')  # 0xb25774e2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.stage))

        data.write(b'\x02\xa3\xe0\x92')  # 0x2a3e092
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x02a3e092))

        data.write(b'\x88\xfd\xe9\x8c')  # 0x88fde98c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.play_initial_anim))

        data.write(b'9\xfbyx')  # 0x39fb7978
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.acceleration))

        data.write(b'\x82\xdb\x0c\xbe')  # 0x82db0cbe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_speed))

        data.write(b'}tG\xb4')  # 0x7d7447b4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_dist))

        data.write(b'.\xd2_P')  # 0x2ed25f50
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_dist))

        data.write(b'\xb5\xd1\x95\x03')  # 0xb5d19503
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb5d19503))

        data.write(b'\xe2\xdf\xc5@')  # 0xe2dfc540
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe2dfc540))

        data.write(b'3\x17\xd0\xc6')  # 0x3317d0c6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.moving_map_opacity))

        data.write(b'\xd0Jn\x1c')  # 0xd04a6e1c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd04a6e1c))

        data.write(b'\x12\xb8\xe5C')  # 0x12b8e543
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shock_wave_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"\xe8\xcd\x96'")  # 0xe8cd9627
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.phaazoid_projectile))

        data.write(b'\x1d\xc6\x9e8')  # 0x1dc69e38
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PhaazoidDataJson", data)
        return cls(
            stage=json_data['stage'],
            unknown_0x02a3e092=json_data['unknown_0x02a3e092'],
            play_initial_anim=json_data['play_initial_anim'],
            acceleration=json_data['acceleration'],
            max_speed=json_data['max_speed'],
            min_attack_dist=json_data['min_attack_dist'],
            max_attack_dist=json_data['max_attack_dist'],
            unknown_0xb5d19503=json_data['unknown_0xb5d19503'],
            unknown_0xe2dfc540=json_data['unknown_0xe2dfc540'],
            moving_map_opacity=json_data['moving_map_opacity'],
            unknown_0xd04a6e1c=json_data['unknown_0xd04a6e1c'],
            shock_wave_info=ShockWaveInfo.from_json(json_data['shock_wave_info']),
            phaazoid_projectile=json_data['phaazoid_projectile'],
            damage_info=DamageInfo.from_json(json_data['damage_info']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'stage': self.stage,
            'unknown_0x02a3e092': self.unknown_0x02a3e092,
            'play_initial_anim': self.play_initial_anim,
            'acceleration': self.acceleration,
            'max_speed': self.max_speed,
            'min_attack_dist': self.min_attack_dist,
            'max_attack_dist': self.max_attack_dist,
            'unknown_0xb5d19503': self.unknown_0xb5d19503,
            'unknown_0xe2dfc540': self.unknown_0xe2dfc540,
            'moving_map_opacity': self.moving_map_opacity,
            'unknown_0xd04a6e1c': self.unknown_0xd04a6e1c,
            'shock_wave_info': self.shock_wave_info.to_json(),
            'phaazoid_projectile': self.phaazoid_projectile,
            'damage_info': self.damage_info.to_json(),
        }


def _decode_stage(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x02a3e092(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_play_initial_anim(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attack_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb5d19503(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe2dfc540(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_moving_map_opacity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd04a6e1c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_phaazoid_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb25774e2: ('stage', _decode_stage),
    0x2a3e092: ('unknown_0x02a3e092', _decode_unknown_0x02a3e092),
    0x88fde98c: ('play_initial_anim', _decode_play_initial_anim),
    0x39fb7978: ('acceleration', _decode_acceleration),
    0x82db0cbe: ('max_speed', _decode_max_speed),
    0x7d7447b4: ('min_attack_dist', _decode_min_attack_dist),
    0x2ed25f50: ('max_attack_dist', _decode_max_attack_dist),
    0xb5d19503: ('unknown_0xb5d19503', _decode_unknown_0xb5d19503),
    0xe2dfc540: ('unknown_0xe2dfc540', _decode_unknown_0xe2dfc540),
    0x3317d0c6: ('moving_map_opacity', _decode_moving_map_opacity),
    0xd04a6e1c: ('unknown_0xd04a6e1c', _decode_unknown_0xd04a6e1c),
    0x12b8e543: ('shock_wave_info', ShockWaveInfo.from_stream),
    0xe8cd9627: ('phaazoid_projectile', _decode_phaazoid_projectile),
    0x1dc69e38: ('damage_info', DamageInfo.from_stream),
}
