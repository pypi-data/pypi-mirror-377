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
from retro_data_structures.properties.corruption.archetypes.TWeaponDamage import TWeaponDamage

if typing.TYPE_CHECKING:
    class TBeamInfoJson(typing_extensions.TypedDict):
        cooldown: float
        damage_info: json_util.JsonObject
    

@dataclasses.dataclass()
class TBeamInfo(BaseProperty):
    cooldown: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x102e085f, original_name='Cooldown'
        ),
    })
    damage_info: TWeaponDamage = dataclasses.field(default_factory=TWeaponDamage, metadata={
        'reflection': FieldReflection[TWeaponDamage](
            TWeaponDamage, id=0xfaa71e25, original_name='DamageInfo', from_json=TWeaponDamage.from_json, to_json=TWeaponDamage.to_json
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
        if property_count != 2:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x102e085f
        cooldown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfaa71e25
        damage_info = TWeaponDamage.from_stream(data, property_size)
    
        return cls(cooldown, damage_info)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'\x10.\x08_')  # 0x102e085f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cooldown))

        data.write(b'\xfa\xa7\x1e%')  # 0xfaa71e25
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TBeamInfoJson", data)
        return cls(
            cooldown=json_data['cooldown'],
            damage_info=TWeaponDamage.from_json(json_data['damage_info']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'cooldown': self.cooldown,
            'damage_info': self.damage_info.to_json(),
        }


def _decode_cooldown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x102e085f: ('cooldown', _decode_cooldown),
    0xfaa71e25: ('damage_info', TWeaponDamage.from_stream),
}
