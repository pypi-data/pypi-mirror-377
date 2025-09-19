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
    class TweakBall_MiscJson(typing_extensions.TypedDict):
        unknown_0x13cfde23: float
        unknown_0xf3499713: float
        unknown_0x895a47fb: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x13cfde23, 0xf3499713, 0x895a47fb)


@dataclasses.dataclass()
class TweakBall_Misc(BaseProperty):
    unknown_0x13cfde23: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x13cfde23, original_name='Unknown'
        ),
    })
    unknown_0xf3499713: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf3499713, original_name='Unknown'
        ),
    })
    unknown_0x895a47fb: float = dataclasses.field(default=200.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x895a47fb, original_name='Unknown'
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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(30))
        assert (dec[0], dec[3], dec[6]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\x13\xcf\xde#')  # 0x13cfde23
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x13cfde23))

        data.write(b'\xf3I\x97\x13')  # 0xf3499713
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf3499713))

        data.write(b'\x89ZG\xfb')  # 0x895a47fb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x895a47fb))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakBall_MiscJson", data)
        return cls(
            unknown_0x13cfde23=json_data['unknown_0x13cfde23'],
            unknown_0xf3499713=json_data['unknown_0xf3499713'],
            unknown_0x895a47fb=json_data['unknown_0x895a47fb'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x13cfde23': self.unknown_0x13cfde23,
            'unknown_0xf3499713': self.unknown_0xf3499713,
            'unknown_0x895a47fb': self.unknown_0x895a47fb,
        }


def _decode_unknown_0x13cfde23(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf3499713(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x895a47fb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x13cfde23: ('unknown_0x13cfde23', _decode_unknown_0x13cfde23),
    0xf3499713: ('unknown_0xf3499713', _decode_unknown_0xf3499713),
    0x895a47fb: ('unknown_0x895a47fb', _decode_unknown_0x895a47fb),
}
