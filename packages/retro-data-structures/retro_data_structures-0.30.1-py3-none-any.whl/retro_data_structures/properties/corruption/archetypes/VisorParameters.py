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
    class VisorParametersJson(typing_extensions.TypedDict):
        scan_through: bool
        visor_flags: int
        unknown: int
        visor_zoom_distance: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xfe9dc266, 0xca19e8c6, 0x46175a3d, 0xca6e30b1)


@dataclasses.dataclass()
class VisorParameters(BaseProperty):
    scan_through: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xfe9dc266, original_name='ScanThrough'
        ),
    })
    visor_flags: int = dataclasses.field(default=15, metadata={
        'reflection': FieldReflection[int](
            int, id=0xca19e8c6, original_name='VisorFlags'
        ),
    })  # Flagset
    unknown: int = dataclasses.field(default=15, metadata={
        'reflection': FieldReflection[int](
            int, id=0x46175a3d, original_name='Unknown'
        ),
    })
    visor_zoom_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xca6e30b1, original_name='VisorZoomDistance'
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
            _FAST_FORMAT = struct.Struct('>LH?LHLLHlLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(37))
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

        data.write(b'\xfe\x9d\xc2f')  # 0xfe9dc266
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.scan_through))

        data.write(b'\xca\x19\xe8\xc6')  # 0xca19e8c6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.visor_flags))

        data.write(b'F\x17Z=')  # 0x46175a3d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown))

        data.write(b'\xcan0\xb1')  # 0xca6e30b1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.visor_zoom_distance))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("VisorParametersJson", data)
        return cls(
            scan_through=json_data['scan_through'],
            visor_flags=json_data['visor_flags'],
            unknown=json_data['unknown'],
            visor_zoom_distance=json_data['visor_zoom_distance'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'scan_through': self.scan_through,
            'visor_flags': self.visor_flags,
            'unknown': self.unknown,
            'visor_zoom_distance': self.visor_zoom_distance,
        }


def _decode_scan_through(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_visor_flags(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_visor_zoom_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xfe9dc266: ('scan_through', _decode_scan_through),
    0xca19e8c6: ('visor_flags', _decode_visor_flags),
    0x46175a3d: ('unknown', _decode_unknown),
    0xca6e30b1: ('visor_zoom_distance', _decode_visor_zoom_distance),
}
