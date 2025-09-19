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

    class BehaveChanceJson(typing_extensions.TypedDict):
        lurk: float
        unknown: float
        attack: float
        move: float
        lurk_time: float
        charge_attack: float
        num_bolts: int
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xd3a313a5, 0x3cfa69f1, 0x1af89f4b, 0xe7e66f66, 0xb9d9c2d2, 0xcfabdd5f, 0x5ab228b6)


@dataclasses.dataclass()
class BehaveChance(BaseProperty):
    lurk: float = dataclasses.field(default=-0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd3a313a5, original_name='Lurk'
        ),
    })
    unknown: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3cfa69f1, original_name='Unknown'
        ),
    })
    attack: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1af89f4b, original_name='Attack'
        ),
    })
    move: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe7e66f66, original_name='Move'
        ),
    })
    lurk_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb9d9c2d2, original_name='LurkTime'
        ),
    })
    charge_attack: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcfabdd5f, original_name='ChargeAttack'
        ),
    })
    num_bolts: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5ab228b6, original_name='NumBolts'
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
        if property_count != 7:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHl')
    
        dec = _FAST_FORMAT.unpack(data.read(70))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'\xd3\xa3\x13\xa5')  # 0xd3a313a5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lurk))

        data.write(b'<\xfai\xf1')  # 0x3cfa69f1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\x1a\xf8\x9fK')  # 0x1af89f4b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack))

        data.write(b'\xe7\xe6of')  # 0xe7e66f66
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.move))

        data.write(b'\xb9\xd9\xc2\xd2')  # 0xb9d9c2d2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lurk_time))

        data.write(b'\xcf\xab\xdd_')  # 0xcfabdd5f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.charge_attack))

        data.write(b'Z\xb2(\xb6')  # 0x5ab228b6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.num_bolts))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("BehaveChanceJson", data)
        return cls(
            lurk=json_data['lurk'],
            unknown=json_data['unknown'],
            attack=json_data['attack'],
            move=json_data['move'],
            lurk_time=json_data['lurk_time'],
            charge_attack=json_data['charge_attack'],
            num_bolts=json_data['num_bolts'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'lurk': self.lurk,
            'unknown': self.unknown,
            'attack': self.attack,
            'move': self.move,
            'lurk_time': self.lurk_time,
            'charge_attack': self.charge_attack,
            'num_bolts': self.num_bolts,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_lurk(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_move(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_lurk_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_charge_attack(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_num_bolts(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xd3a313a5: ('lurk', _decode_lurk),
    0x3cfa69f1: ('unknown', _decode_unknown),
    0x1af89f4b: ('attack', _decode_attack),
    0xe7e66f66: ('move', _decode_move),
    0xb9d9c2d2: ('lurk_time', _decode_lurk_time),
    0xcfabdd5f: ('charge_attack', _decode_charge_attack),
    0x5ab228b6: ('num_bolts', _decode_num_bolts),
}
