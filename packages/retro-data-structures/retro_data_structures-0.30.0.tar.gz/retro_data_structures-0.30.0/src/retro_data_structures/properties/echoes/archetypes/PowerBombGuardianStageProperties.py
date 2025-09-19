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

    class PowerBombGuardianStagePropertiesJson(typing_extensions.TypedDict):
        unknown_0x95e7a2c2: float
        unknown_0x76ba1c18: float
        unknown_0x3eb2de35: float
        unknown_0xe50d8dd2: float
        unknown_0x64d482d5: int
        unknown_0xc3e002ac: int
        unknown_0xbb4b6680: float
        unknown_0xd356c997: float
        double_shot_chance: float
        unknown_0x87cc8ba4: int
        unknown_0x6491357e: int
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x95e7a2c2, 0x76ba1c18, 0x3eb2de35, 0xe50d8dd2, 0x64d482d5, 0xc3e002ac, 0xbb4b6680, 0xd356c997, 0xca6ac43a, 0x87cc8ba4, 0x6491357e)


@dataclasses.dataclass()
class PowerBombGuardianStageProperties(BaseProperty):
    unknown_0x95e7a2c2: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95e7a2c2, original_name='Unknown'
        ),
    })
    unknown_0x76ba1c18: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x76ba1c18, original_name='Unknown'
        ),
    })
    unknown_0x3eb2de35: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3eb2de35, original_name='Unknown'
        ),
    })
    unknown_0xe50d8dd2: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe50d8dd2, original_name='Unknown'
        ),
    })
    unknown_0x64d482d5: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x64d482d5, original_name='Unknown'
        ),
    })
    unknown_0xc3e002ac: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc3e002ac, original_name='Unknown'
        ),
    })
    unknown_0xbb4b6680: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbb4b6680, original_name='Unknown'
        ),
    })
    unknown_0xd356c997: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd356c997, original_name='Unknown'
        ),
    })
    double_shot_chance: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xca6ac43a, original_name='DoubleShotChance'
        ),
    })
    unknown_0x87cc8ba4: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x87cc8ba4, original_name='Unknown'
        ),
    })
    unknown_0x6491357e: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6491357e, original_name='Unknown'
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
        if property_count != 11:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHlLHlLHfLHfLHfLHlLHl')
    
        dec = _FAST_FORMAT.unpack(data.read(110))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30]) == _FAST_IDS
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
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'\x95\xe7\xa2\xc2')  # 0x95e7a2c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95e7a2c2))

        data.write(b'v\xba\x1c\x18')  # 0x76ba1c18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x76ba1c18))

        data.write(b'>\xb2\xde5')  # 0x3eb2de35
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3eb2de35))

        data.write(b'\xe5\r\x8d\xd2')  # 0xe50d8dd2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe50d8dd2))

        data.write(b'd\xd4\x82\xd5')  # 0x64d482d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x64d482d5))

        data.write(b'\xc3\xe0\x02\xac')  # 0xc3e002ac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc3e002ac))

        data.write(b'\xbbKf\x80')  # 0xbb4b6680
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbb4b6680))

        data.write(b'\xd3V\xc9\x97')  # 0xd356c997
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd356c997))

        data.write(b'\xcaj\xc4:')  # 0xca6ac43a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.double_shot_chance))

        data.write(b'\x87\xcc\x8b\xa4')  # 0x87cc8ba4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x87cc8ba4))

        data.write(b'd\x915~')  # 0x6491357e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x6491357e))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PowerBombGuardianStagePropertiesJson", data)
        return cls(
            unknown_0x95e7a2c2=json_data['unknown_0x95e7a2c2'],
            unknown_0x76ba1c18=json_data['unknown_0x76ba1c18'],
            unknown_0x3eb2de35=json_data['unknown_0x3eb2de35'],
            unknown_0xe50d8dd2=json_data['unknown_0xe50d8dd2'],
            unknown_0x64d482d5=json_data['unknown_0x64d482d5'],
            unknown_0xc3e002ac=json_data['unknown_0xc3e002ac'],
            unknown_0xbb4b6680=json_data['unknown_0xbb4b6680'],
            unknown_0xd356c997=json_data['unknown_0xd356c997'],
            double_shot_chance=json_data['double_shot_chance'],
            unknown_0x87cc8ba4=json_data['unknown_0x87cc8ba4'],
            unknown_0x6491357e=json_data['unknown_0x6491357e'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x95e7a2c2': self.unknown_0x95e7a2c2,
            'unknown_0x76ba1c18': self.unknown_0x76ba1c18,
            'unknown_0x3eb2de35': self.unknown_0x3eb2de35,
            'unknown_0xe50d8dd2': self.unknown_0xe50d8dd2,
            'unknown_0x64d482d5': self.unknown_0x64d482d5,
            'unknown_0xc3e002ac': self.unknown_0xc3e002ac,
            'unknown_0xbb4b6680': self.unknown_0xbb4b6680,
            'unknown_0xd356c997': self.unknown_0xd356c997,
            'double_shot_chance': self.double_shot_chance,
            'unknown_0x87cc8ba4': self.unknown_0x87cc8ba4,
            'unknown_0x6491357e': self.unknown_0x6491357e,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_unknown_0x95e7a2c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x76ba1c18(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3eb2de35(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe50d8dd2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x64d482d5(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xc3e002ac(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xbb4b6680(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd356c997(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_double_shot_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x87cc8ba4(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x6491357e(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x95e7a2c2: ('unknown_0x95e7a2c2', _decode_unknown_0x95e7a2c2),
    0x76ba1c18: ('unknown_0x76ba1c18', _decode_unknown_0x76ba1c18),
    0x3eb2de35: ('unknown_0x3eb2de35', _decode_unknown_0x3eb2de35),
    0xe50d8dd2: ('unknown_0xe50d8dd2', _decode_unknown_0xe50d8dd2),
    0x64d482d5: ('unknown_0x64d482d5', _decode_unknown_0x64d482d5),
    0xc3e002ac: ('unknown_0xc3e002ac', _decode_unknown_0xc3e002ac),
    0xbb4b6680: ('unknown_0xbb4b6680', _decode_unknown_0xbb4b6680),
    0xd356c997: ('unknown_0xd356c997', _decode_unknown_0xd356c997),
    0xca6ac43a: ('double_shot_chance', _decode_double_shot_chance),
    0x87cc8ba4: ('unknown_0x87cc8ba4', _decode_unknown_0x87cc8ba4),
    0x6491357e: ('unknown_0x6491357e', _decode_unknown_0x6491357e),
}
