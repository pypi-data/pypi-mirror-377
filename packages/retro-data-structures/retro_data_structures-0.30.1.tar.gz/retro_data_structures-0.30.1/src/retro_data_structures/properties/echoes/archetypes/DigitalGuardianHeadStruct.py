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

    class DigitalGuardianHeadStructJson(typing_extensions.TypedDict):
        first_shot_type: int
        projectile_telegraph_time: float
        projectile_attack_time: float
        unknown_0xfdfca535: float
        unknown_0xcd03632c: float
        unknown_0xf1548397: float
        unknown_0xf967e246: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xd20288a4, 0x75dc92bc, 0x9e1c3f6c, 0xfdfca535, 0xcd03632c, 0xf1548397, 0xf967e246)


@dataclasses.dataclass()
class DigitalGuardianHeadStruct(BaseProperty):
    first_shot_type: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd20288a4, original_name='FirstShotType'
        ),
    })
    projectile_telegraph_time: float = dataclasses.field(default=1.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x75dc92bc, original_name='ProjectileTelegraphTime'
        ),
    })
    projectile_attack_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9e1c3f6c, original_name='ProjectileAttackTime'
        ),
    })
    unknown_0xfdfca535: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfdfca535, original_name='Unknown'
        ),
    })
    unknown_0xcd03632c: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcd03632c, original_name='Unknown'
        ),
    })
    unknown_0xf1548397: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf1548397, original_name='Unknown'
        ),
    })
    unknown_0xf967e246: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf967e246, original_name='Unknown'
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
            _FAST_FORMAT = struct.Struct('>LHlLHfLHfLHfLHfLHfLHf')
    
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

        data.write(b'\xd2\x02\x88\xa4')  # 0xd20288a4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.first_shot_type))

        data.write(b'u\xdc\x92\xbc')  # 0x75dc92bc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.projectile_telegraph_time))

        data.write(b'\x9e\x1c?l')  # 0x9e1c3f6c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.projectile_attack_time))

        data.write(b'\xfd\xfc\xa55')  # 0xfdfca535
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfdfca535))

        data.write(b'\xcd\x03c,')  # 0xcd03632c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcd03632c))

        data.write(b'\xf1T\x83\x97')  # 0xf1548397
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf1548397))

        data.write(b'\xf9g\xe2F')  # 0xf967e246
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf967e246))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DigitalGuardianHeadStructJson", data)
        return cls(
            first_shot_type=json_data['first_shot_type'],
            projectile_telegraph_time=json_data['projectile_telegraph_time'],
            projectile_attack_time=json_data['projectile_attack_time'],
            unknown_0xfdfca535=json_data['unknown_0xfdfca535'],
            unknown_0xcd03632c=json_data['unknown_0xcd03632c'],
            unknown_0xf1548397=json_data['unknown_0xf1548397'],
            unknown_0xf967e246=json_data['unknown_0xf967e246'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'first_shot_type': self.first_shot_type,
            'projectile_telegraph_time': self.projectile_telegraph_time,
            'projectile_attack_time': self.projectile_attack_time,
            'unknown_0xfdfca535': self.unknown_0xfdfca535,
            'unknown_0xcd03632c': self.unknown_0xcd03632c,
            'unknown_0xf1548397': self.unknown_0xf1548397,
            'unknown_0xf967e246': self.unknown_0xf967e246,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_first_shot_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_projectile_telegraph_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_projectile_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfdfca535(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcd03632c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf1548397(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf967e246(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xd20288a4: ('first_shot_type', _decode_first_shot_type),
    0x75dc92bc: ('projectile_telegraph_time', _decode_projectile_telegraph_time),
    0x9e1c3f6c: ('projectile_attack_time', _decode_projectile_attack_time),
    0xfdfca535: ('unknown_0xfdfca535', _decode_unknown_0xfdfca535),
    0xcd03632c: ('unknown_0xcd03632c', _decode_unknown_0xcd03632c),
    0xf1548397: ('unknown_0xf1548397', _decode_unknown_0xf1548397),
    0xf967e246: ('unknown_0xf967e246', _decode_unknown_0xf967e246),
}
