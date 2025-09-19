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
    class ShockWaveInfoJson(typing_extensions.TypedDict):
        shock_wave_effect: int
        damage: json_util.JsonObject
        duration: float
        knockback_decay_rate: float
        unknown_0x60df1486: bool
        radius: float
        height: float
        unknown_0xcf6c1de9: float
        radial_velocity: float
        radial_velocity_acceleration: float
        visor_electric_effect: int
        sound_visor_electric: int
        optional_shockwave_sound: int
    

@dataclasses.dataclass()
class ShockWaveInfo(BaseProperty):
    shock_wave_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x369f7d09, original_name='ShockWaveEffect'
        ),
    })
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    duration: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b51e23f, original_name='Duration'
        ),
    })
    knockback_decay_rate: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0320895b, original_name='KnockbackDecayRate'
        ),
    })
    unknown_0x60df1486: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x60df1486, original_name='Unknown'
        ),
    })
    radius: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x78c507eb, original_name='Radius'
        ),
    })
    height: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc2be030d, original_name='Height'
        ),
    })
    unknown_0xcf6c1de9: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcf6c1de9, original_name='Unknown'
        ),
    })
    radial_velocity: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4cd1459b, original_name='RadialVelocity'
        ),
    })
    radial_velocity_acceleration: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0a57b09b, original_name='RadialVelocityAcceleration'
        ),
    })
    visor_electric_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xbd321538, original_name='VisorElectricEffect'
        ),
    })
    sound_visor_electric: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa2850b37, original_name='Sound_VisorElectric'
        ),
    })
    optional_shockwave_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x56936c97, original_name='OptionalShockwaveSound'
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
        if property_count != 13:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x369f7d09
        shock_wave_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b51e23f
        duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0320895b
        knockback_decay_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x60df1486
        unknown_0x60df1486 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78c507eb
        radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc2be030d
        height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf6c1de9
        unknown_0xcf6c1de9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4cd1459b
        radial_velocity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a57b09b
        radial_velocity_acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbd321538
        visor_electric_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa2850b37
        sound_visor_electric = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x56936c97
        optional_shockwave_sound = struct.unpack(">Q", data.read(8))[0]
    
        return cls(shock_wave_effect, damage, duration, knockback_decay_rate, unknown_0x60df1486, radius, height, unknown_0xcf6c1de9, radial_velocity, radial_velocity_acceleration, visor_electric_effect, sound_visor_electric, optional_shockwave_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\r')  # 13 properties

        data.write(b'6\x9f}\t')  # 0x369f7d09
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.shock_wave_effect))

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8bQ\xe2?')  # 0x8b51e23f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.duration))

        data.write(b'\x03 \x89[')  # 0x320895b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.knockback_decay_rate))

        data.write(b'`\xdf\x14\x86')  # 0x60df1486
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x60df1486))

        data.write(b'x\xc5\x07\xeb')  # 0x78c507eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.radius))

        data.write(b'\xc2\xbe\x03\r')  # 0xc2be030d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.height))

        data.write(b'\xcfl\x1d\xe9')  # 0xcf6c1de9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcf6c1de9))

        data.write(b'L\xd1E\x9b')  # 0x4cd1459b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.radial_velocity))

        data.write(b'\nW\xb0\x9b')  # 0xa57b09b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.radial_velocity_acceleration))

        data.write(b'\xbd2\x158')  # 0xbd321538
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.visor_electric_effect))

        data.write(b'\xa2\x85\x0b7')  # 0xa2850b37
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_visor_electric))

        data.write(b'V\x93l\x97')  # 0x56936c97
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.optional_shockwave_sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ShockWaveInfoJson", data)
        return cls(
            shock_wave_effect=json_data['shock_wave_effect'],
            damage=DamageInfo.from_json(json_data['damage']),
            duration=json_data['duration'],
            knockback_decay_rate=json_data['knockback_decay_rate'],
            unknown_0x60df1486=json_data['unknown_0x60df1486'],
            radius=json_data['radius'],
            height=json_data['height'],
            unknown_0xcf6c1de9=json_data['unknown_0xcf6c1de9'],
            radial_velocity=json_data['radial_velocity'],
            radial_velocity_acceleration=json_data['radial_velocity_acceleration'],
            visor_electric_effect=json_data['visor_electric_effect'],
            sound_visor_electric=json_data['sound_visor_electric'],
            optional_shockwave_sound=json_data['optional_shockwave_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'shock_wave_effect': self.shock_wave_effect,
            'damage': self.damage.to_json(),
            'duration': self.duration,
            'knockback_decay_rate': self.knockback_decay_rate,
            'unknown_0x60df1486': self.unknown_0x60df1486,
            'radius': self.radius,
            'height': self.height,
            'unknown_0xcf6c1de9': self.unknown_0xcf6c1de9,
            'radial_velocity': self.radial_velocity,
            'radial_velocity_acceleration': self.radial_velocity_acceleration,
            'visor_electric_effect': self.visor_electric_effect,
            'sound_visor_electric': self.sound_visor_electric,
            'optional_shockwave_sound': self.optional_shockwave_sound,
        }


def _decode_shock_wave_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_knockback_decay_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x60df1486(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcf6c1de9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_radial_velocity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_radial_velocity_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_visor_electric_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_visor_electric(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_optional_shockwave_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x369f7d09: ('shock_wave_effect', _decode_shock_wave_effect),
    0x337f9524: ('damage', DamageInfo.from_stream),
    0x8b51e23f: ('duration', _decode_duration),
    0x320895b: ('knockback_decay_rate', _decode_knockback_decay_rate),
    0x60df1486: ('unknown_0x60df1486', _decode_unknown_0x60df1486),
    0x78c507eb: ('radius', _decode_radius),
    0xc2be030d: ('height', _decode_height),
    0xcf6c1de9: ('unknown_0xcf6c1de9', _decode_unknown_0xcf6c1de9),
    0x4cd1459b: ('radial_velocity', _decode_radial_velocity),
    0xa57b09b: ('radial_velocity_acceleration', _decode_radial_velocity_acceleration),
    0xbd321538: ('visor_electric_effect', _decode_visor_electric_effect),
    0xa2850b37: ('sound_visor_electric', _decode_sound_visor_electric),
    0x56936c97: ('optional_shockwave_sound', _decode_optional_shockwave_sound),
}
