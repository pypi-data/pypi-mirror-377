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
    class GrappleInfoJson(typing_extensions.TypedDict):
        skeleton_landing: float
        unknown_0x7a5e41e1: float
        unknown_0x76104d9e: float
        visible_through_geometry: bool
        unknown_0x11b6a17a: bool
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x2ba7fabc, 0x7a5e41e1, 0x76104d9e, 0xbaa8a527, 0x11b6a17a)


@dataclasses.dataclass()
class GrappleInfo(BaseProperty):
    skeleton_landing: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2ba7fabc, original_name='SkeletonLanding'
        ),
    })
    unknown_0x7a5e41e1: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a5e41e1, original_name='Unknown'
        ),
    })
    unknown_0x76104d9e: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x76104d9e, original_name='Unknown'
        ),
    })
    visible_through_geometry: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xbaa8a527, original_name='VisibleThroughGeometry'
        ),
    })
    unknown_0x11b6a17a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x11b6a17a, original_name='Unknown'
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
        if property_count != 5:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLH?LH?')
    
        dec = _FAST_FORMAT.unpack(data.read(44))
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

        data.write(b'+\xa7\xfa\xbc')  # 0x2ba7fabc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.skeleton_landing))

        data.write(b'z^A\xe1')  # 0x7a5e41e1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7a5e41e1))

        data.write(b'v\x10M\x9e')  # 0x76104d9e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x76104d9e))

        data.write(b"\xba\xa8\xa5'")  # 0xbaa8a527
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.visible_through_geometry))

        data.write(b'\x11\xb6\xa1z')  # 0x11b6a17a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x11b6a17a))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("GrappleInfoJson", data)
        return cls(
            skeleton_landing=json_data['skeleton_landing'],
            unknown_0x7a5e41e1=json_data['unknown_0x7a5e41e1'],
            unknown_0x76104d9e=json_data['unknown_0x76104d9e'],
            visible_through_geometry=json_data['visible_through_geometry'],
            unknown_0x11b6a17a=json_data['unknown_0x11b6a17a'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'skeleton_landing': self.skeleton_landing,
            'unknown_0x7a5e41e1': self.unknown_0x7a5e41e1,
            'unknown_0x76104d9e': self.unknown_0x76104d9e,
            'visible_through_geometry': self.visible_through_geometry,
            'unknown_0x11b6a17a': self.unknown_0x11b6a17a,
        }


def _decode_skeleton_landing(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7a5e41e1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x76104d9e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_visible_through_geometry(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x11b6a17a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x2ba7fabc: ('skeleton_landing', _decode_skeleton_landing),
    0x7a5e41e1: ('unknown_0x7a5e41e1', _decode_unknown_0x7a5e41e1),
    0x76104d9e: ('unknown_0x76104d9e', _decode_unknown_0x76104d9e),
    0xbaa8a527: ('visible_through_geometry', _decode_visible_through_geometry),
    0x11b6a17a: ('unknown_0x11b6a17a', _decode_unknown_0x11b6a17a),
}
