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
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class TweakTargeting_UnknownStruct2Json(typing_extensions.TypedDict):
        unknown_0x4b435047: float
        unknown_0x0ece183c: float
        unknown_0xab03dcb9: float
        unknown_0xc0120b9e: float
        unknown_0xf5230e61: float
        unknown_0x70caf349: float
        unknown_0x955a5177: float
        unknown_0x95ed96c2: float
        unknown_0x138b3979: json_util.JsonObject
        unknown_0xdfa46325: json_util.JsonObject
    

@dataclasses.dataclass()
class TweakTargeting_UnknownStruct2(BaseProperty):
    unknown_0x4b435047: float = dataclasses.field(default=500.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4b435047, original_name='Unknown'
        ),
    })
    unknown_0x0ece183c: float = dataclasses.field(default=-0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0ece183c, original_name='Unknown'
        ),
    })
    unknown_0xab03dcb9: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0xab03dcb9, original_name='Unknown'
        ),
    })
    unknown_0xc0120b9e: float = dataclasses.field(default=0.44999998807907104, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc0120b9e, original_name='Unknown'
        ),
    })
    unknown_0xf5230e61: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf5230e61, original_name='Unknown'
        ),
    })
    unknown_0x70caf349: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x70caf349, original_name='Unknown'
        ),
    })
    unknown_0x955a5177: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x955a5177, original_name='Unknown'
        ),
    })
    unknown_0x95ed96c2: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95ed96c2, original_name='Unknown'
        ),
    })
    unknown_0x138b3979: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x138b3979, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0xdfa46325: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xdfa46325, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
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
        if property_count != 10:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4b435047
        unknown_0x4b435047 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0ece183c
        unknown_0x0ece183c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xab03dcb9
        unknown_0xab03dcb9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc0120b9e
        unknown_0xc0120b9e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5230e61
        unknown_0xf5230e61 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x70caf349
        unknown_0x70caf349 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x955a5177
        unknown_0x955a5177 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95ed96c2
        unknown_0x95ed96c2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x138b3979
        unknown_0x138b3979 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdfa46325
        unknown_0xdfa46325 = Spline.from_stream(data, property_size)
    
        return cls(unknown_0x4b435047, unknown_0x0ece183c, unknown_0xab03dcb9, unknown_0xc0120b9e, unknown_0xf5230e61, unknown_0x70caf349, unknown_0x955a5177, unknown_0x95ed96c2, unknown_0x138b3979, unknown_0xdfa46325)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\n')  # 10 properties

        data.write(b'KCPG')  # 0x4b435047
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4b435047))

        data.write(b'\x0e\xce\x18<')  # 0xece183c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0ece183c))

        data.write(b'\xab\x03\xdc\xb9')  # 0xab03dcb9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xab03dcb9))

        data.write(b'\xc0\x12\x0b\x9e')  # 0xc0120b9e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc0120b9e))

        data.write(b'\xf5#\x0ea')  # 0xf5230e61
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf5230e61))

        data.write(b'p\xca\xf3I')  # 0x70caf349
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x70caf349))

        data.write(b'\x95ZQw')  # 0x955a5177
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x955a5177))

        data.write(b'\x95\xed\x96\xc2')  # 0x95ed96c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95ed96c2))

        data.write(b'\x13\x8b9y')  # 0x138b3979
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x138b3979.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdf\xa4c%')  # 0xdfa46325
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xdfa46325.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakTargeting_UnknownStruct2Json", data)
        return cls(
            unknown_0x4b435047=json_data['unknown_0x4b435047'],
            unknown_0x0ece183c=json_data['unknown_0x0ece183c'],
            unknown_0xab03dcb9=json_data['unknown_0xab03dcb9'],
            unknown_0xc0120b9e=json_data['unknown_0xc0120b9e'],
            unknown_0xf5230e61=json_data['unknown_0xf5230e61'],
            unknown_0x70caf349=json_data['unknown_0x70caf349'],
            unknown_0x955a5177=json_data['unknown_0x955a5177'],
            unknown_0x95ed96c2=json_data['unknown_0x95ed96c2'],
            unknown_0x138b3979=Spline.from_json(json_data['unknown_0x138b3979']),
            unknown_0xdfa46325=Spline.from_json(json_data['unknown_0xdfa46325']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x4b435047': self.unknown_0x4b435047,
            'unknown_0x0ece183c': self.unknown_0x0ece183c,
            'unknown_0xab03dcb9': self.unknown_0xab03dcb9,
            'unknown_0xc0120b9e': self.unknown_0xc0120b9e,
            'unknown_0xf5230e61': self.unknown_0xf5230e61,
            'unknown_0x70caf349': self.unknown_0x70caf349,
            'unknown_0x955a5177': self.unknown_0x955a5177,
            'unknown_0x95ed96c2': self.unknown_0x95ed96c2,
            'unknown_0x138b3979': self.unknown_0x138b3979.to_json(),
            'unknown_0xdfa46325': self.unknown_0xdfa46325.to_json(),
        }


def _decode_unknown_0x4b435047(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0ece183c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xab03dcb9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc0120b9e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf5230e61(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x70caf349(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x955a5177(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x95ed96c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x4b435047: ('unknown_0x4b435047', _decode_unknown_0x4b435047),
    0xece183c: ('unknown_0x0ece183c', _decode_unknown_0x0ece183c),
    0xab03dcb9: ('unknown_0xab03dcb9', _decode_unknown_0xab03dcb9),
    0xc0120b9e: ('unknown_0xc0120b9e', _decode_unknown_0xc0120b9e),
    0xf5230e61: ('unknown_0xf5230e61', _decode_unknown_0xf5230e61),
    0x70caf349: ('unknown_0x70caf349', _decode_unknown_0x70caf349),
    0x955a5177: ('unknown_0x955a5177', _decode_unknown_0x955a5177),
    0x95ed96c2: ('unknown_0x95ed96c2', _decode_unknown_0x95ed96c2),
    0x138b3979: ('unknown_0x138b3979', Spline.from_stream),
    0xdfa46325: ('unknown_0xdfa46325', Spline.from_stream),
}
