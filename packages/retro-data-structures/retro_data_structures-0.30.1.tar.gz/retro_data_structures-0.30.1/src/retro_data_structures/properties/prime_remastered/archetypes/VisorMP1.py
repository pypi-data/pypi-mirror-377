# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection

if typing.TYPE_CHECKING:
    class VisorMP1Json(typing_extensions.TypedDict):
        unknown_1: bool
        unknown_2: bool
        unknown_3: bool
        visor_flags: int
    

class VisorFlags(enum.IntFlag):
    Combat = 1
    Scan = 2
    Thermal = 4
    XRay = 8

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack("<L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack("<L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x82f75015, 0x5149fc12, 0x1382ca50, 0x528a56a5)


@dataclasses.dataclass()
class VisorMP1(BaseProperty):
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x82f75015, original_name='Unknown 1'
        ),
    })
    unknown_2: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5149fc12, original_name='Unknown 2'
        ),
    })
    unknown_3: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1382ca50, original_name='Unknown 3'
        ),
    })
    visor_flags: VisorFlags = dataclasses.field(default=VisorFlags(0), metadata={
        'reflection': FieldReflection[VisorFlags](
            VisorFlags, id=0x528a56a5, original_name='Visor Flags', from_json=VisorFlags.from_json, to_json=VisorFlags.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME_REMASTER

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack("<H", data.read(2))[0]
        if (result := cls._fast_decode(data, property_count)) is not None:
            return result

        present_fields = default_override or {}
        for _ in range(property_count):
            property_id, property_size = struct.unpack("<LH", data.read(6))
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
            _FAST_FORMAT = struct.Struct('<LH?LH?LH?LHL')
    
        dec = _FAST_FORMAT.unpack(data.read(31))
        assert (dec[0], dec[3], dec[6], dec[9]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            VisorFlags(dec[11]),
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        num_properties_offset = data.tell()
        data.write(b'\x00\x00')  # 0 properties
        num_properties_written = 0

        if self.unknown_1 != default_override.get('unknown_1', False):
            num_properties_written += 1
            data.write(b'\x15P\xf7\x82')  # 0x82f75015
            data.write(b'\x01\x00')  # size
            data.write(struct.pack('<?', self.unknown_1))

        if self.unknown_2 != default_override.get('unknown_2', False):
            num_properties_written += 1
            data.write(b'\x12\xfcIQ')  # 0x5149fc12
            data.write(b'\x01\x00')  # size
            data.write(struct.pack('<?', self.unknown_2))

        if self.unknown_3 != default_override.get('unknown_3', False):
            num_properties_written += 1
            data.write(b'P\xca\x82\x13')  # 0x1382ca50
            data.write(b'\x01\x00')  # size
            data.write(struct.pack('<?', self.unknown_3))

        if self.visor_flags != default_override.get('visor_flags', VisorFlags(0)):
            num_properties_written += 1
            data.write(b'\xa5V\x8aR')  # 0x528a56a5
            data.write(b'\x04\x00')  # size
            self.visor_flags.to_stream(data)

        if num_properties_written != 0:
            struct_end_offset = data.tell()
            data.seek(num_properties_offset)
            data.write(struct.pack("<H", num_properties_written))
            data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("VisorMP1Json", data)
        return cls(
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            visor_flags=VisorFlags.from_json(json_data['visor_flags']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'visor_flags': self.visor_flags.to_json(),
        }


def _decode_unknown_1(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('<?', data.read(1))[0]


def _decode_unknown_2(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('<?', data.read(1))[0]


def _decode_unknown_3(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('<?', data.read(1))[0]


def _decode_visor_flags(data: typing.BinaryIO, property_size: int) -> VisorFlags:
    return VisorFlags.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x82f75015: ('unknown_1', _decode_unknown_1),
    0x5149fc12: ('unknown_2', _decode_unknown_2),
    0x1382ca50: ('unknown_3', _decode_unknown_3),
    0x528a56a5: ('visor_flags', _decode_visor_flags),
}
