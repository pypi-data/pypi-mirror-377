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

    class TweakPlayer_SuitDamageReductionJson(typing_extensions.TypedDict):
        varia: float
        dark: float
        light: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xdf131ecd, 0x908a8e6c, 0x95700a27)


@dataclasses.dataclass()
class TweakPlayer_SuitDamageReduction(BaseProperty):
    varia: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdf131ecd, original_name='Varia'
        ),
    })
    dark: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x908a8e6c, original_name='Dark'
        ),
    })
    light: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95700a27, original_name='Light'
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

        data.write(b'\xdf\x13\x1e\xcd')  # 0xdf131ecd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.varia))

        data.write(b'\x90\x8a\x8el')  # 0x908a8e6c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dark))

        data.write(b"\x95p\n'")  # 0x95700a27
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.light))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayer_SuitDamageReductionJson", data)
        return cls(
            varia=json_data['varia'],
            dark=json_data['dark'],
            light=json_data['light'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'varia': self.varia,
            'dark': self.dark,
            'light': self.light,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_varia(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dark(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_light(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xdf131ecd: ('varia', _decode_varia),
    0x908a8e6c: ('dark', _decode_dark),
    0x95700a27: ('light', _decode_light),
}
