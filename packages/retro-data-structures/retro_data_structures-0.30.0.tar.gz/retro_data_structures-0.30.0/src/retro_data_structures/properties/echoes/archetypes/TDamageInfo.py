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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TDamageInfoJson(typing_extensions.TypedDict):
        weapon_type: int
        damage_amount: float
        radius_damage_amount: float
        damage_radius: float
        knock_back_power: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x4d577910, 0xf3ec8748, 0x37b6df3d, 0xf598739, 0x56f98c49)


@dataclasses.dataclass()
class TDamageInfo(BaseProperty):
    weapon_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x4d577910, original_name='WeaponType'
        ),
    })
    damage_amount: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf3ec8748, original_name='DamageAmount'
        ),
    })
    radius_damage_amount: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x37b6df3d, original_name='RadiusDamageAmount'
        ),
    })
    damage_radius: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0f598739, original_name='DamageRadius'
        ),
    })
    knock_back_power: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x56f98c49, original_name='KnockBackPower'
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
        if property_count != 5:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHlLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(50))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'MWy\x10')  # 0x4d577910
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.weapon_type))

        data.write(b'\xf3\xec\x87H')  # 0xf3ec8748
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_amount))

        data.write(b'7\xb6\xdf=')  # 0x37b6df3d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.radius_damage_amount))

        data.write(b'\x0fY\x879')  # 0xf598739
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_radius))

        data.write(b'V\xf9\x8cI')  # 0x56f98c49
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.knock_back_power))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TDamageInfoJson", data)
        return cls(
            weapon_type=json_data['weapon_type'],
            damage_amount=json_data['damage_amount'],
            radius_damage_amount=json_data['radius_damage_amount'],
            damage_radius=json_data['damage_radius'],
            knock_back_power=json_data['knock_back_power'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'weapon_type': self.weapon_type,
            'damage_amount': self.damage_amount,
            'radius_damage_amount': self.radius_damage_amount,
            'damage_radius': self.damage_radius,
            'knock_back_power': self.knock_back_power,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_weapon_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_damage_amount(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_radius_damage_amount(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_damage_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_knock_back_power(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x4d577910: ('weapon_type', _decode_weapon_type),
    0xf3ec8748: ('damage_amount', _decode_damage_amount),
    0x37b6df3d: ('radius_damage_amount', _decode_radius_damage_amount),
    0xf598739: ('damage_radius', _decode_damage_radius),
    0x56f98c49: ('knock_back_power', _decode_knock_back_power),
}
