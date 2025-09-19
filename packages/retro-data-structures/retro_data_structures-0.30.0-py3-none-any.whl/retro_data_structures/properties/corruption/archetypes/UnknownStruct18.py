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
    class UnknownStruct18Json(typing_extensions.TypedDict):
        column_effect: int
        column_trail_effect: int
        elsc: int
        visor_effect_electric: int
        unknown_0x01299e29: int
        unknown_0x442bddab: int
        column_damage: json_util.JsonObject
        cross_bar_damage: json_util.JsonObject
        column_damage_radius: float
        initial_speed: float
        acceleration: float
        apex_shockwave_volume: float
        unknown_0x4032c58a: float
        unknown_0x8b6e162f: float
        unknown_0x966b2697: float
    

@dataclasses.dataclass()
class UnknownStruct18(BaseProperty):
    column_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4c28cd13, original_name='ColumnEffect'
        ),
    })
    column_trail_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x32a13dfd, original_name='ColumnTrailEffect'
        ),
    })
    elsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x57f7eff9, original_name='ELSC'
        ),
    })
    visor_effect_electric: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xfd132f70, original_name='VisorEffectElectric'
        ),
    })
    unknown_0x01299e29: int = dataclasses.field(default=6, metadata={
        'reflection': FieldReflection[int](
            int, id=0x01299e29, original_name='Unknown'
        ),
    })
    unknown_0x442bddab: int = dataclasses.field(default=6, metadata={
        'reflection': FieldReflection[int](
            int, id=0x442bddab, original_name='Unknown'
        ),
    })
    column_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x37304f48, original_name='ColumnDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    cross_bar_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xc5528a8d, original_name='CrossBarDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    column_damage_radius: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4b59e590, original_name='ColumnDamageRadius'
        ),
    })
    initial_speed: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcb14d97c, original_name='InitialSpeed'
        ),
    })
    acceleration: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x39fb7978, original_name='Acceleration'
        ),
    })
    apex_shockwave_volume: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc6a6b724, original_name='ApexShockwaveVolume'
        ),
    })
    unknown_0x4032c58a: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4032c58a, original_name='Unknown'
        ),
    })
    unknown_0x8b6e162f: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b6e162f, original_name='Unknown'
        ),
    })
    unknown_0x966b2697: float = dataclasses.field(default=9.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x966b2697, original_name='Unknown'
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
        if property_count != 15:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4c28cd13
        column_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32a13dfd
        column_trail_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x57f7eff9
        elsc = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd132f70
        visor_effect_electric = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01299e29
        unknown_0x01299e29 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x442bddab
        unknown_0x442bddab = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37304f48
        column_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 20.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc5528a8d
        cross_bar_damage = DamageInfo.from_stream(data, property_size, default_override={'di_damage': 20.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4b59e590
        column_damage_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcb14d97c
        initial_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x39fb7978
        acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6a6b724
        apex_shockwave_volume = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4032c58a
        unknown_0x4032c58a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b6e162f
        unknown_0x8b6e162f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x966b2697
        unknown_0x966b2697 = struct.unpack('>f', data.read(4))[0]
    
        return cls(column_effect, column_trail_effect, elsc, visor_effect_electric, unknown_0x01299e29, unknown_0x442bddab, column_damage, cross_bar_damage, column_damage_radius, initial_speed, acceleration, apex_shockwave_volume, unknown_0x4032c58a, unknown_0x8b6e162f, unknown_0x966b2697)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0f')  # 15 properties

        data.write(b'L(\xcd\x13')  # 0x4c28cd13
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.column_effect))

        data.write(b'2\xa1=\xfd')  # 0x32a13dfd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.column_trail_effect))

        data.write(b'W\xf7\xef\xf9')  # 0x57f7eff9
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.elsc))

        data.write(b'\xfd\x13/p')  # 0xfd132f70
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.visor_effect_electric))

        data.write(b'\x01)\x9e)')  # 0x1299e29
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x01299e29))

        data.write(b'D+\xdd\xab')  # 0x442bddab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x442bddab))

        data.write(b'70OH')  # 0x37304f48
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.column_damage.to_stream(data, default_override={'di_damage': 20.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc5R\x8a\x8d')  # 0xc5528a8d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.cross_bar_damage.to_stream(data, default_override={'di_damage': 20.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'KY\xe5\x90')  # 0x4b59e590
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.column_damage_radius))

        data.write(b'\xcb\x14\xd9|')  # 0xcb14d97c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.initial_speed))

        data.write(b'9\xfbyx')  # 0x39fb7978
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.acceleration))

        data.write(b'\xc6\xa6\xb7$')  # 0xc6a6b724
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.apex_shockwave_volume))

        data.write(b'@2\xc5\x8a')  # 0x4032c58a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4032c58a))

        data.write(b'\x8bn\x16/')  # 0x8b6e162f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8b6e162f))

        data.write(b'\x96k&\x97')  # 0x966b2697
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x966b2697))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct18Json", data)
        return cls(
            column_effect=json_data['column_effect'],
            column_trail_effect=json_data['column_trail_effect'],
            elsc=json_data['elsc'],
            visor_effect_electric=json_data['visor_effect_electric'],
            unknown_0x01299e29=json_data['unknown_0x01299e29'],
            unknown_0x442bddab=json_data['unknown_0x442bddab'],
            column_damage=DamageInfo.from_json(json_data['column_damage']),
            cross_bar_damage=DamageInfo.from_json(json_data['cross_bar_damage']),
            column_damage_radius=json_data['column_damage_radius'],
            initial_speed=json_data['initial_speed'],
            acceleration=json_data['acceleration'],
            apex_shockwave_volume=json_data['apex_shockwave_volume'],
            unknown_0x4032c58a=json_data['unknown_0x4032c58a'],
            unknown_0x8b6e162f=json_data['unknown_0x8b6e162f'],
            unknown_0x966b2697=json_data['unknown_0x966b2697'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'column_effect': self.column_effect,
            'column_trail_effect': self.column_trail_effect,
            'elsc': self.elsc,
            'visor_effect_electric': self.visor_effect_electric,
            'unknown_0x01299e29': self.unknown_0x01299e29,
            'unknown_0x442bddab': self.unknown_0x442bddab,
            'column_damage': self.column_damage.to_json(),
            'cross_bar_damage': self.cross_bar_damage.to_json(),
            'column_damage_radius': self.column_damage_radius,
            'initial_speed': self.initial_speed,
            'acceleration': self.acceleration,
            'apex_shockwave_volume': self.apex_shockwave_volume,
            'unknown_0x4032c58a': self.unknown_0x4032c58a,
            'unknown_0x8b6e162f': self.unknown_0x8b6e162f,
            'unknown_0x966b2697': self.unknown_0x966b2697,
        }


def _decode_column_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_column_trail_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_elsc(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_visor_effect_electric(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x01299e29(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x442bddab(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_column_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 20.0, 'di_knock_back_power': 10.0})


def _decode_cross_bar_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_damage': 20.0, 'di_knock_back_power': 10.0})


def _decode_column_damage_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_initial_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_apex_shockwave_volume(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4032c58a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8b6e162f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x966b2697(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x4c28cd13: ('column_effect', _decode_column_effect),
    0x32a13dfd: ('column_trail_effect', _decode_column_trail_effect),
    0x57f7eff9: ('elsc', _decode_elsc),
    0xfd132f70: ('visor_effect_electric', _decode_visor_effect_electric),
    0x1299e29: ('unknown_0x01299e29', _decode_unknown_0x01299e29),
    0x442bddab: ('unknown_0x442bddab', _decode_unknown_0x442bddab),
    0x37304f48: ('column_damage', _decode_column_damage),
    0xc5528a8d: ('cross_bar_damage', _decode_cross_bar_damage),
    0x4b59e590: ('column_damage_radius', _decode_column_damage_radius),
    0xcb14d97c: ('initial_speed', _decode_initial_speed),
    0x39fb7978: ('acceleration', _decode_acceleration),
    0xc6a6b724: ('apex_shockwave_volume', _decode_apex_shockwave_volume),
    0x4032c58a: ('unknown_0x4032c58a', _decode_unknown_0x4032c58a),
    0x8b6e162f: ('unknown_0x8b6e162f', _decode_unknown_0x8b6e162f),
    0x966b2697: ('unknown_0x966b2697', _decode_unknown_0x966b2697),
}
