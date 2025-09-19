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
from retro_data_structures.properties.corruption.archetypes.GhorStructC import GhorStructC

if typing.TYPE_CHECKING:
    class UnknownStruct38Json(typing_extensions.TypedDict):
        force_disable: bool
        ghor_struct_c: json_util.JsonObject
        damage_info: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct38(BaseProperty):
    force_disable: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa8d0ee16, original_name='ForceDisable'
        ),
    })
    ghor_struct_c: GhorStructC = dataclasses.field(default_factory=GhorStructC, metadata={
        'reflection': FieldReflection[GhorStructC](
            GhorStructC, id=0xa82b5daa, original_name='GhorStructC', from_json=GhorStructC.from_json, to_json=GhorStructC.to_json
        ),
    })
    damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xc97013d0, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
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
        if property_count != 3:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa8d0ee16
        force_disable = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa82b5daa
        ghor_struct_c = GhorStructC.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc97013d0
        damage_info = DamageInfo.from_stream(data, property_size)
    
        return cls(force_disable, ghor_struct_c, damage_info)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\xa8\xd0\xee\x16')  # 0xa8d0ee16
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.force_disable))

        data.write(b'\xa8+]\xaa')  # 0xa82b5daa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_c.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc9p\x13\xd0')  # 0xc97013d0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct38Json", data)
        return cls(
            force_disable=json_data['force_disable'],
            ghor_struct_c=GhorStructC.from_json(json_data['ghor_struct_c']),
            damage_info=DamageInfo.from_json(json_data['damage_info']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'force_disable': self.force_disable,
            'ghor_struct_c': self.ghor_struct_c.to_json(),
            'damage_info': self.damage_info.to_json(),
        }


def _decode_force_disable(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xa8d0ee16: ('force_disable', _decode_force_disable),
    0xa82b5daa: ('ghor_struct_c', GhorStructC.from_stream),
    0xc97013d0: ('damage_info', DamageInfo.from_stream),
}
