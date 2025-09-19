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
import retro_data_structures.enums.echoes as enums

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DamageInfoJson(typing_extensions.TypedDict):
        di_weapon_type: int
        di_damage: float
        di_radius: float
        di_knock_back_power: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x119fbd31, 0xf2d02613, 0xee1be914, 0x555ff80a)


@dataclasses.dataclass()
class DamageInfo(BaseProperty):
    di_weapon_type: enums.WeaponTypeEnum = dataclasses.field(default=enums.WeaponTypeEnum.Power, metadata={
        'reflection': FieldReflection[enums.WeaponTypeEnum](
            enums.WeaponTypeEnum, id=0x119fbd31, original_name='DI_WeaponType', from_json=enums.WeaponTypeEnum.from_json, to_json=enums.WeaponTypeEnum.to_json
        ),
    })
    di_damage: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf2d02613, original_name='DI_Damage'
        ),
    })
    di_radius: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xee1be914, original_name='DI_Radius'
        ),
    })
    di_knock_back_power: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x555ff80a, original_name='DI_KnockBackPower'
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
        if property_count != 4:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHLLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(40))
        assert (dec[0], dec[3], dec[6], dec[9]) == _FAST_IDS
        return cls(
            enums.WeaponTypeEnum(dec[2]),
            dec[5],
            dec[8],
            dec[11],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'\x11\x9f\xbd1')  # 0x119fbd31
        data.write(b'\x00\x04')  # size
        self.di_weapon_type.to_stream(data)

        data.write(b'\xf2\xd0&\x13')  # 0xf2d02613
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.di_damage))

        data.write(b'\xee\x1b\xe9\x14')  # 0xee1be914
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.di_radius))

        data.write(b'U_\xf8\n')  # 0x555ff80a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.di_knock_back_power))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DamageInfoJson", data)
        return cls(
            di_weapon_type=enums.WeaponTypeEnum.from_json(json_data['di_weapon_type']),
            di_damage=json_data['di_damage'],
            di_radius=json_data['di_radius'],
            di_knock_back_power=json_data['di_knock_back_power'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'di_weapon_type': self.di_weapon_type.to_json(),
            'di_damage': self.di_damage,
            'di_radius': self.di_radius,
            'di_knock_back_power': self.di_knock_back_power,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_di_weapon_type(data: typing.BinaryIO, property_size: int) -> enums.WeaponTypeEnum:
    return enums.WeaponTypeEnum.from_stream(data)


def _decode_di_damage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_di_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_di_knock_back_power(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x119fbd31: ('di_weapon_type', _decode_di_weapon_type),
    0xf2d02613: ('di_damage', _decode_di_damage),
    0xee1be914: ('di_radius', _decode_di_radius),
    0x555ff80a: ('di_knock_back_power', _decode_di_knock_back_power),
}
