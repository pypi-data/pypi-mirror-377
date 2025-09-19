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

if typing.TYPE_CHECKING:
    class ChakramJson(typing_extensions.TypedDict):
        chakram_model: int
        energy_effect: int
        trail_effect: int
        static_geometry_collision_effect: int
        in_flight_sound: int
        player_impact_sound: int
        caud: int
        damage: json_util.JsonObject
        hyper_damage: json_util.JsonObject
        speed: float
        unknown_0x508c48d7: float
        spin_rate: float
        fade_out_time: float
        visor_effect: int
        stun_time: float
        unknown_0x2f79b3d0: float
        unknown_0x11cc7b58: float
    

@dataclasses.dataclass()
class Chakram(BaseProperty):
    chakram_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x66ab57a4, original_name='ChakramModel'
        ),
    })
    energy_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x14143470, original_name='EnergyEffect'
        ),
    })
    trail_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x36eee791, original_name='TrailEffect'
        ),
    })
    static_geometry_collision_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x52f89bf7, original_name='StaticGeometryCollisionEffect'
        ),
    })
    in_flight_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1a092829, original_name='InFlightSound'
        ),
    })
    player_impact_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe33a996d, original_name='PlayerImpactSound'
        ),
    })
    caud: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xdf64c67a, original_name='CAUD'
        ),
    })
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    hyper_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xb3dabf84, original_name='HyperDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    speed: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6392404e, original_name='Speed'
        ),
    })
    unknown_0x508c48d7: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x508c48d7, original_name='Unknown'
        ),
    })
    spin_rate: float = dataclasses.field(default=720.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b4af5c4, original_name='SpinRate'
        ),
    })
    fade_out_time: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7c269ebc, original_name='FadeOutTime'
        ),
    })
    visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART', 'ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe9c8e2bd, original_name='VisorEffect'
        ),
    })
    stun_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7e192395, original_name='StunTime'
        ),
    })
    unknown_0x2f79b3d0: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2f79b3d0, original_name='Unknown'
        ),
    })
    unknown_0x11cc7b58: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x11cc7b58, original_name='Unknown'
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
        if property_count != 17:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66ab57a4
        chakram_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x14143470
        energy_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x36eee791
        trail_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x52f89bf7
        static_geometry_collision_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a092829
        in_flight_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe33a996d
        player_impact_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdf64c67a
        caud = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3dabf84
        hyper_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6392404e
        speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x508c48d7
        unknown_0x508c48d7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b4af5c4
        spin_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7c269ebc
        fade_out_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9c8e2bd
        visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e192395
        stun_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2f79b3d0
        unknown_0x2f79b3d0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x11cc7b58
        unknown_0x11cc7b58 = struct.unpack('>f', data.read(4))[0]
    
        return cls(chakram_model, energy_effect, trail_effect, static_geometry_collision_effect, in_flight_sound, player_impact_sound, caud, damage, hyper_damage, speed, unknown_0x508c48d7, spin_rate, fade_out_time, visor_effect, stun_time, unknown_0x2f79b3d0, unknown_0x11cc7b58)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x11')  # 17 properties

        data.write(b'f\xabW\xa4')  # 0x66ab57a4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.chakram_model))

        data.write(b'\x14\x144p')  # 0x14143470
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.energy_effect))

        data.write(b'6\xee\xe7\x91')  # 0x36eee791
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.trail_effect))

        data.write(b'R\xf8\x9b\xf7')  # 0x52f89bf7
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.static_geometry_collision_effect))

        data.write(b'\x1a\t()')  # 0x1a092829
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.in_flight_sound))

        data.write(b'\xe3:\x99m')  # 0xe33a996d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.player_impact_sound))

        data.write(b'\xdfd\xc6z')  # 0xdf64c67a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud))

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3\xda\xbf\x84')  # 0xb3dabf84
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'c\x92@N')  # 0x6392404e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed))

        data.write(b'P\x8cH\xd7')  # 0x508c48d7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x508c48d7))

        data.write(b'\x8bJ\xf5\xc4')  # 0x8b4af5c4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.spin_rate))

        data.write(b'|&\x9e\xbc')  # 0x7c269ebc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_out_time))

        data.write(b'\xe9\xc8\xe2\xbd')  # 0xe9c8e2bd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.visor_effect))

        data.write(b'~\x19#\x95')  # 0x7e192395
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.stun_time))

        data.write(b'/y\xb3\xd0')  # 0x2f79b3d0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2f79b3d0))

        data.write(b'\x11\xcc{X')  # 0x11cc7b58
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x11cc7b58))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ChakramJson", data)
        return cls(
            chakram_model=json_data['chakram_model'],
            energy_effect=json_data['energy_effect'],
            trail_effect=json_data['trail_effect'],
            static_geometry_collision_effect=json_data['static_geometry_collision_effect'],
            in_flight_sound=json_data['in_flight_sound'],
            player_impact_sound=json_data['player_impact_sound'],
            caud=json_data['caud'],
            damage=DamageInfo.from_json(json_data['damage']),
            hyper_damage=DamageInfo.from_json(json_data['hyper_damage']),
            speed=json_data['speed'],
            unknown_0x508c48d7=json_data['unknown_0x508c48d7'],
            spin_rate=json_data['spin_rate'],
            fade_out_time=json_data['fade_out_time'],
            visor_effect=json_data['visor_effect'],
            stun_time=json_data['stun_time'],
            unknown_0x2f79b3d0=json_data['unknown_0x2f79b3d0'],
            unknown_0x11cc7b58=json_data['unknown_0x11cc7b58'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'chakram_model': self.chakram_model,
            'energy_effect': self.energy_effect,
            'trail_effect': self.trail_effect,
            'static_geometry_collision_effect': self.static_geometry_collision_effect,
            'in_flight_sound': self.in_flight_sound,
            'player_impact_sound': self.player_impact_sound,
            'caud': self.caud,
            'damage': self.damage.to_json(),
            'hyper_damage': self.hyper_damage.to_json(),
            'speed': self.speed,
            'unknown_0x508c48d7': self.unknown_0x508c48d7,
            'spin_rate': self.spin_rate,
            'fade_out_time': self.fade_out_time,
            'visor_effect': self.visor_effect,
            'stun_time': self.stun_time,
            'unknown_0x2f79b3d0': self.unknown_0x2f79b3d0,
            'unknown_0x11cc7b58': self.unknown_0x11cc7b58,
        }


def _decode_chakram_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_energy_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_trail_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_static_geometry_collision_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_in_flight_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_player_impact_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x508c48d7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_spin_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_out_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_stun_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2f79b3d0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x11cc7b58(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x66ab57a4: ('chakram_model', _decode_chakram_model),
    0x14143470: ('energy_effect', _decode_energy_effect),
    0x36eee791: ('trail_effect', _decode_trail_effect),
    0x52f89bf7: ('static_geometry_collision_effect', _decode_static_geometry_collision_effect),
    0x1a092829: ('in_flight_sound', _decode_in_flight_sound),
    0xe33a996d: ('player_impact_sound', _decode_player_impact_sound),
    0xdf64c67a: ('caud', _decode_caud),
    0x337f9524: ('damage', DamageInfo.from_stream),
    0xb3dabf84: ('hyper_damage', DamageInfo.from_stream),
    0x6392404e: ('speed', _decode_speed),
    0x508c48d7: ('unknown_0x508c48d7', _decode_unknown_0x508c48d7),
    0x8b4af5c4: ('spin_rate', _decode_spin_rate),
    0x7c269ebc: ('fade_out_time', _decode_fade_out_time),
    0xe9c8e2bd: ('visor_effect', _decode_visor_effect),
    0x7e192395: ('stun_time', _decode_stun_time),
    0x2f79b3d0: ('unknown_0x2f79b3d0', _decode_unknown_0x2f79b3d0),
    0x11cc7b58: ('unknown_0x11cc7b58', _decode_unknown_0x11cc7b58),
}
