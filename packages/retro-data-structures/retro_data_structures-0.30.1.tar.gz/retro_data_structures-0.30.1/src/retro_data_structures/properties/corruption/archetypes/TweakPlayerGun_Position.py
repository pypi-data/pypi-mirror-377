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
    class TweakPlayerGun_PositionJson(typing_extensions.TypedDict):
        unknown: float
        x: float
        y: float
        z: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x1547d77b, 0xa1677d4e, 0x6a3baeeb, 0xecafdc45)


@dataclasses.dataclass()
class TweakPlayerGun_Position(BaseProperty):
    unknown: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1547d77b, original_name='Unknown'
        ),
    })
    x: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa1677d4e, original_name='X'
        ),
    })
    y: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6a3baeeb, original_name='Y'
        ),
    })
    z: float = dataclasses.field(default=-0.3499999940395355, metadata={
        'reflection': FieldReflection[float](
            float, id=0xecafdc45, original_name='Z'
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
        if property_count != 4:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(40))
        assert (dec[0], dec[3], dec[6], dec[9]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'\x15G\xd7{')  # 0x1547d77b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\xa1g}N')  # 0xa1677d4e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.x))

        data.write(b'j;\xae\xeb')  # 0x6a3baeeb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.y))

        data.write(b'\xec\xaf\xdcE')  # 0xecafdc45
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.z))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayerGun_PositionJson", data)
        return cls(
            unknown=json_data['unknown'],
            x=json_data['x'],
            y=json_data['y'],
            z=json_data['z'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown': self.unknown,
            'x': self.x,
            'y': self.y,
            'z': self.z,
        }


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_x(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_y(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_z(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1547d77b: ('unknown', _decode_unknown),
    0xa1677d4e: ('x', _decode_x),
    0x6a3baeeb: ('y', _decode_y),
    0xecafdc45: ('z', _decode_z),
}
