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
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ShockWaveInfoJson(typing_extensions.TypedDict):
        shock_wave_effect: int
        damage: json_util.JsonObject
        radius: float
        height: float
        unknown: float
        radial_velocity: float
        radial_velocity_acceleration: float
        visor_electric_effect: int
        sound_visor_electric: int
    

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
    unknown: float = dataclasses.field(default=0.5, metadata={
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
    sound_visor_electric: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x58a492ef, original_name='Sound_VisorElectric'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        assert property_id == 0x369f7d09
        shock_wave_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78c507eb
        radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc2be030d
        height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf6c1de9
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4cd1459b
        radial_velocity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a57b09b
        radial_velocity_acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbd321538
        visor_electric_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58a492ef
        sound_visor_electric = struct.unpack('>l', data.read(4))[0]
    
        return cls(shock_wave_effect, damage, radius, height, unknown, radial_velocity, radial_velocity_acceleration, visor_electric_effect, sound_visor_electric)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\t')  # 9 properties

        data.write(b'6\x9f}\t')  # 0x369f7d09
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.shock_wave_effect))

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'x\xc5\x07\xeb')  # 0x78c507eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.radius))

        data.write(b'\xc2\xbe\x03\r')  # 0xc2be030d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.height))

        data.write(b'\xcfl\x1d\xe9')  # 0xcf6c1de9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'L\xd1E\x9b')  # 0x4cd1459b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.radial_velocity))

        data.write(b'\nW\xb0\x9b')  # 0xa57b09b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.radial_velocity_acceleration))

        data.write(b'\xbd2\x158')  # 0xbd321538
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.visor_electric_effect))

        data.write(b'X\xa4\x92\xef')  # 0x58a492ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_visor_electric))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ShockWaveInfoJson", data)
        return cls(
            shock_wave_effect=json_data['shock_wave_effect'],
            damage=DamageInfo.from_json(json_data['damage']),
            radius=json_data['radius'],
            height=json_data['height'],
            unknown=json_data['unknown'],
            radial_velocity=json_data['radial_velocity'],
            radial_velocity_acceleration=json_data['radial_velocity_acceleration'],
            visor_electric_effect=json_data['visor_electric_effect'],
            sound_visor_electric=json_data['sound_visor_electric'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'shock_wave_effect': self.shock_wave_effect,
            'damage': self.damage.to_json(),
            'radius': self.radius,
            'height': self.height,
            'unknown': self.unknown,
            'radial_velocity': self.radial_velocity,
            'radial_velocity_acceleration': self.radial_velocity_acceleration,
            'visor_electric_effect': self.visor_electric_effect,
            'sound_visor_electric': self.sound_visor_electric,
        }

    def _dependencies_for_shock_wave_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.shock_wave_effect)

    def _dependencies_for_visor_electric_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.visor_electric_effect)

    def _dependencies_for_sound_visor_electric(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_visor_electric)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_shock_wave_effect, "shock_wave_effect", "AssetId"),
            (self.damage.dependencies_for, "damage", "DamageInfo"),
            (self._dependencies_for_visor_electric_effect, "visor_electric_effect", "AssetId"),
            (self._dependencies_for_sound_visor_electric, "sound_visor_electric", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ShockWaveInfo.{field_name} ({field_type}): {e}"
                )


def _decode_shock_wave_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_radial_velocity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_radial_velocity_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_visor_electric_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_sound_visor_electric(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x369f7d09: ('shock_wave_effect', _decode_shock_wave_effect),
    0x337f9524: ('damage', DamageInfo.from_stream),
    0x78c507eb: ('radius', _decode_radius),
    0xc2be030d: ('height', _decode_height),
    0xcf6c1de9: ('unknown', _decode_unknown),
    0x4cd1459b: ('radial_velocity', _decode_radial_velocity),
    0xa57b09b: ('radial_velocity_acceleration', _decode_radial_velocity_acceleration),
    0xbd321538: ('visor_electric_effect', _decode_visor_electric_effect),
    0x58a492ef: ('sound_visor_electric', _decode_sound_visor_electric),
}
