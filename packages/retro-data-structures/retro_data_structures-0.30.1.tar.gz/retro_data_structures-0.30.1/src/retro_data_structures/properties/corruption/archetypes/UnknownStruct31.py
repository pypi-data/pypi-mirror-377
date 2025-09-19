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
    class UnknownStruct31Json(typing_extensions.TypedDict):
        initial_morph_time: float
        unknown_0xc8cfc063: float
        unknown_0x80c0d235: float
        unknown_0x26fa79a3: float
        unknown_0xc77f29dc: float
        gandrayda_to_berserker: float
        unknown_0xcbbd9a4e: float
        gandrayda_to_swarm: float
        unknown_0xa2675081: float
        unknown_0x413aee5b: float
        unknown_0x931ea2ea: float
        unknown_0x144f7ed6: float
        unknown_0x659d7d56: float
        unknown_0x7a11bb7b: float
        unknown_0xb4089be1: float
        swarm_to_gandrayda: float
        swarm_to_berserker: float
        unknown_0x73ac8586: float
        unknown_0x704c4fc6: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x45161109, 0xc8cfc063, 0x80c0d235, 0x26fa79a3, 0xc77f29dc, 0x141473b5, 0xcbbd9a4e, 0x8d7c6103, 0xa2675081, 0x413aee5b, 0x931ea2ea, 0x144f7ed6, 0x659d7d56, 0x7a11bb7b, 0xb4089be1, 0x20235a31, 0xa772860d, 0x73ac8586, 0x704c4fc6)


@dataclasses.dataclass()
class UnknownStruct31(BaseProperty):
    initial_morph_time: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x45161109, original_name='InitialMorphTime'
        ),
    })
    unknown_0xc8cfc063: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc8cfc063, original_name='Unknown'
        ),
    })
    unknown_0x80c0d235: float = dataclasses.field(default=85.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x80c0d235, original_name='Unknown'
        ),
    })
    unknown_0x26fa79a3: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x26fa79a3, original_name='Unknown'
        ),
    })
    unknown_0xc77f29dc: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc77f29dc, original_name='Unknown'
        ),
    })
    gandrayda_to_berserker: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x141473b5, original_name='GandraydaToBerserker'
        ),
    })
    unknown_0xcbbd9a4e: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcbbd9a4e, original_name='Unknown'
        ),
    })
    gandrayda_to_swarm: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8d7c6103, original_name='GandraydaToSwarm'
        ),
    })
    unknown_0xa2675081: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa2675081, original_name='Unknown'
        ),
    })
    unknown_0x413aee5b: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x413aee5b, original_name='Unknown'
        ),
    })
    unknown_0x931ea2ea: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x931ea2ea, original_name='Unknown'
        ),
    })
    unknown_0x144f7ed6: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x144f7ed6, original_name='Unknown'
        ),
    })
    unknown_0x659d7d56: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x659d7d56, original_name='Unknown'
        ),
    })
    unknown_0x7a11bb7b: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a11bb7b, original_name='Unknown'
        ),
    })
    unknown_0xb4089be1: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb4089be1, original_name='Unknown'
        ),
    })
    swarm_to_gandrayda: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x20235a31, original_name='SwarmToGandrayda'
        ),
    })
    swarm_to_berserker: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa772860d, original_name='SwarmToBerserker'
        ),
    })
    unknown_0x73ac8586: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x73ac8586, original_name='Unknown'
        ),
    })
    unknown_0x704c4fc6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x704c4fc6, original_name='Unknown'
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
        if property_count != 19:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(190))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[33], dec[36], dec[39], dec[42], dec[45], dec[48], dec[51], dec[54]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
            dec[23],
            dec[26],
            dec[29],
            dec[32],
            dec[35],
            dec[38],
            dec[41],
            dec[44],
            dec[47],
            dec[50],
            dec[53],
            dec[56],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x13')  # 19 properties

        data.write(b'E\x16\x11\t')  # 0x45161109
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.initial_morph_time))

        data.write(b'\xc8\xcf\xc0c')  # 0xc8cfc063
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc8cfc063))

        data.write(b'\x80\xc0\xd25')  # 0x80c0d235
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x80c0d235))

        data.write(b'&\xfay\xa3')  # 0x26fa79a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x26fa79a3))

        data.write(b'\xc7\x7f)\xdc')  # 0xc77f29dc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc77f29dc))

        data.write(b'\x14\x14s\xb5')  # 0x141473b5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.gandrayda_to_berserker))

        data.write(b'\xcb\xbd\x9aN')  # 0xcbbd9a4e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcbbd9a4e))

        data.write(b'\x8d|a\x03')  # 0x8d7c6103
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.gandrayda_to_swarm))

        data.write(b'\xa2gP\x81')  # 0xa2675081
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa2675081))

        data.write(b'A:\xee[')  # 0x413aee5b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x413aee5b))

        data.write(b'\x93\x1e\xa2\xea')  # 0x931ea2ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x931ea2ea))

        data.write(b'\x14O~\xd6')  # 0x144f7ed6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x144f7ed6))

        data.write(b'e\x9d}V')  # 0x659d7d56
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x659d7d56))

        data.write(b'z\x11\xbb{')  # 0x7a11bb7b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7a11bb7b))

        data.write(b'\xb4\x08\x9b\xe1')  # 0xb4089be1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb4089be1))

        data.write(b' #Z1')  # 0x20235a31
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.swarm_to_gandrayda))

        data.write(b'\xa7r\x86\r')  # 0xa772860d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.swarm_to_berserker))

        data.write(b's\xac\x85\x86')  # 0x73ac8586
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x73ac8586))

        data.write(b'pLO\xc6')  # 0x704c4fc6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x704c4fc6))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct31Json", data)
        return cls(
            initial_morph_time=json_data['initial_morph_time'],
            unknown_0xc8cfc063=json_data['unknown_0xc8cfc063'],
            unknown_0x80c0d235=json_data['unknown_0x80c0d235'],
            unknown_0x26fa79a3=json_data['unknown_0x26fa79a3'],
            unknown_0xc77f29dc=json_data['unknown_0xc77f29dc'],
            gandrayda_to_berserker=json_data['gandrayda_to_berserker'],
            unknown_0xcbbd9a4e=json_data['unknown_0xcbbd9a4e'],
            gandrayda_to_swarm=json_data['gandrayda_to_swarm'],
            unknown_0xa2675081=json_data['unknown_0xa2675081'],
            unknown_0x413aee5b=json_data['unknown_0x413aee5b'],
            unknown_0x931ea2ea=json_data['unknown_0x931ea2ea'],
            unknown_0x144f7ed6=json_data['unknown_0x144f7ed6'],
            unknown_0x659d7d56=json_data['unknown_0x659d7d56'],
            unknown_0x7a11bb7b=json_data['unknown_0x7a11bb7b'],
            unknown_0xb4089be1=json_data['unknown_0xb4089be1'],
            swarm_to_gandrayda=json_data['swarm_to_gandrayda'],
            swarm_to_berserker=json_data['swarm_to_berserker'],
            unknown_0x73ac8586=json_data['unknown_0x73ac8586'],
            unknown_0x704c4fc6=json_data['unknown_0x704c4fc6'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'initial_morph_time': self.initial_morph_time,
            'unknown_0xc8cfc063': self.unknown_0xc8cfc063,
            'unknown_0x80c0d235': self.unknown_0x80c0d235,
            'unknown_0x26fa79a3': self.unknown_0x26fa79a3,
            'unknown_0xc77f29dc': self.unknown_0xc77f29dc,
            'gandrayda_to_berserker': self.gandrayda_to_berserker,
            'unknown_0xcbbd9a4e': self.unknown_0xcbbd9a4e,
            'gandrayda_to_swarm': self.gandrayda_to_swarm,
            'unknown_0xa2675081': self.unknown_0xa2675081,
            'unknown_0x413aee5b': self.unknown_0x413aee5b,
            'unknown_0x931ea2ea': self.unknown_0x931ea2ea,
            'unknown_0x144f7ed6': self.unknown_0x144f7ed6,
            'unknown_0x659d7d56': self.unknown_0x659d7d56,
            'unknown_0x7a11bb7b': self.unknown_0x7a11bb7b,
            'unknown_0xb4089be1': self.unknown_0xb4089be1,
            'swarm_to_gandrayda': self.swarm_to_gandrayda,
            'swarm_to_berserker': self.swarm_to_berserker,
            'unknown_0x73ac8586': self.unknown_0x73ac8586,
            'unknown_0x704c4fc6': self.unknown_0x704c4fc6,
        }


def _decode_initial_morph_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc8cfc063(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x80c0d235(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x26fa79a3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc77f29dc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_gandrayda_to_berserker(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcbbd9a4e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_gandrayda_to_swarm(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa2675081(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x413aee5b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x931ea2ea(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x144f7ed6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x659d7d56(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7a11bb7b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb4089be1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_swarm_to_gandrayda(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_swarm_to_berserker(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x73ac8586(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x704c4fc6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x45161109: ('initial_morph_time', _decode_initial_morph_time),
    0xc8cfc063: ('unknown_0xc8cfc063', _decode_unknown_0xc8cfc063),
    0x80c0d235: ('unknown_0x80c0d235', _decode_unknown_0x80c0d235),
    0x26fa79a3: ('unknown_0x26fa79a3', _decode_unknown_0x26fa79a3),
    0xc77f29dc: ('unknown_0xc77f29dc', _decode_unknown_0xc77f29dc),
    0x141473b5: ('gandrayda_to_berserker', _decode_gandrayda_to_berserker),
    0xcbbd9a4e: ('unknown_0xcbbd9a4e', _decode_unknown_0xcbbd9a4e),
    0x8d7c6103: ('gandrayda_to_swarm', _decode_gandrayda_to_swarm),
    0xa2675081: ('unknown_0xa2675081', _decode_unknown_0xa2675081),
    0x413aee5b: ('unknown_0x413aee5b', _decode_unknown_0x413aee5b),
    0x931ea2ea: ('unknown_0x931ea2ea', _decode_unknown_0x931ea2ea),
    0x144f7ed6: ('unknown_0x144f7ed6', _decode_unknown_0x144f7ed6),
    0x659d7d56: ('unknown_0x659d7d56', _decode_unknown_0x659d7d56),
    0x7a11bb7b: ('unknown_0x7a11bb7b', _decode_unknown_0x7a11bb7b),
    0xb4089be1: ('unknown_0xb4089be1', _decode_unknown_0xb4089be1),
    0x20235a31: ('swarm_to_gandrayda', _decode_swarm_to_gandrayda),
    0xa772860d: ('swarm_to_berserker', _decode_swarm_to_berserker),
    0x73ac8586: ('unknown_0x73ac8586', _decode_unknown_0x73ac8586),
    0x704c4fc6: ('unknown_0x704c4fc6', _decode_unknown_0x704c4fc6),
}
