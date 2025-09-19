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

    class TweakPlayerControls_UnknownStruct2Json(typing_extensions.TypedDict):
        unknown_0xff1b0413: bool
        unknown_0xe0c1d958: bool
        toggle_aim_position: bool
        unknown_0x1f99c6ba: bool
        unknown_0x18eb3ab5: bool
        unknown_0xbdc01c71: bool
        fixed_vertical_aim: bool
        unknown_0xda97bbcd: bool
        orbit_around_enemies: bool
        unknown_0xc224d966: bool
        add_grenade_alert: bool
        unknown_0x3fb16819: bool
        unknown_0x4fcf4b70: bool
        unknown_0x07bb06a6: bool
        unknown_0x04d8d57b: bool
        unknown_0x5282c47e: bool
        falling_double_jump: bool
        impulse_double_jump: bool
        unknown_0xa796a8b9: bool
        unknown_0x7c0599c8: bool
        unknown_0x522ab1ac: bool
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xff1b0413, 0xe0c1d958, 0x55c20d58, 0x1f99c6ba, 0x18eb3ab5, 0xbdc01c71, 0x1c30f1a6, 0xda97bbcd, 0x83583abd, 0xc224d966, 0x1fcfaf3f, 0x3fb16819, 0x4fcf4b70, 0x7bb06a6, 0x4d8d57b, 0x5282c47e, 0x7304dafa, 0x7a49267d, 0xa796a8b9, 0x7c0599c8, 0x522ab1ac)


@dataclasses.dataclass()
class TweakPlayerControls_UnknownStruct2(BaseProperty):
    unknown_0xff1b0413: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xff1b0413, original_name='Unknown'
        ),
    })
    unknown_0xe0c1d958: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe0c1d958, original_name='Unknown'
        ),
    })
    toggle_aim_position: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x55c20d58, original_name='ToggleAimPosition'
        ),
    })
    unknown_0x1f99c6ba: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1f99c6ba, original_name='Unknown'
        ),
    })
    unknown_0x18eb3ab5: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x18eb3ab5, original_name='Unknown'
        ),
    })
    unknown_0xbdc01c71: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xbdc01c71, original_name='Unknown'
        ),
    })
    fixed_vertical_aim: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1c30f1a6, original_name='FixedVerticalAim'
        ),
    })
    unknown_0xda97bbcd: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xda97bbcd, original_name='Unknown'
        ),
    })
    orbit_around_enemies: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x83583abd, original_name='OrbitAroundEnemies?'
        ),
    })
    unknown_0xc224d966: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc224d966, original_name='Unknown'
        ),
    })
    add_grenade_alert: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1fcfaf3f, original_name='AddGrenadeAlert?'
        ),
    })
    unknown_0x3fb16819: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3fb16819, original_name='Unknown'
        ),
    })
    unknown_0x4fcf4b70: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4fcf4b70, original_name='Unknown'
        ),
    })
    unknown_0x07bb06a6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x07bb06a6, original_name='Unknown'
        ),
    })
    unknown_0x04d8d57b: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x04d8d57b, original_name='Unknown'
        ),
    })
    unknown_0x5282c47e: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5282c47e, original_name='Unknown'
        ),
    })
    falling_double_jump: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7304dafa, original_name='FallingDoubleJump'
        ),
    })
    impulse_double_jump: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7a49267d, original_name='ImpulseDoubleJump'
        ),
    })
    unknown_0xa796a8b9: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa796a8b9, original_name='Unknown'
        ),
    })
    unknown_0x7c0599c8: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7c0599c8, original_name='Unknown'
        ),
    })
    unknown_0x522ab1ac: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x522ab1ac, original_name='Unknown'
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
        if property_count != 21:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?LH?')
    
        dec = _FAST_FORMAT.unpack(data.read(147))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[33], dec[36], dec[39], dec[42], dec[45], dec[48], dec[51], dec[54], dec[57], dec[60]) == _FAST_IDS
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
            dec[59],
            dec[62],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x15')  # 21 properties

        data.write(b'\xff\x1b\x04\x13')  # 0xff1b0413
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xff1b0413))

        data.write(b'\xe0\xc1\xd9X')  # 0xe0c1d958
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xe0c1d958))

        data.write(b'U\xc2\rX')  # 0x55c20d58
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.toggle_aim_position))

        data.write(b'\x1f\x99\xc6\xba')  # 0x1f99c6ba
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x1f99c6ba))

        data.write(b'\x18\xeb:\xb5')  # 0x18eb3ab5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x18eb3ab5))

        data.write(b'\xbd\xc0\x1cq')  # 0xbdc01c71
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xbdc01c71))

        data.write(b'\x1c0\xf1\xa6')  # 0x1c30f1a6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.fixed_vertical_aim))

        data.write(b'\xda\x97\xbb\xcd')  # 0xda97bbcd
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xda97bbcd))

        data.write(b'\x83X:\xbd')  # 0x83583abd
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.orbit_around_enemies))

        data.write(b'\xc2$\xd9f')  # 0xc224d966
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xc224d966))

        data.write(b'\x1f\xcf\xaf?')  # 0x1fcfaf3f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.add_grenade_alert))

        data.write(b'?\xb1h\x19')  # 0x3fb16819
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x3fb16819))

        data.write(b'O\xcfKp')  # 0x4fcf4b70
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4fcf4b70))

        data.write(b'\x07\xbb\x06\xa6')  # 0x7bb06a6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x07bb06a6))

        data.write(b'\x04\xd8\xd5{')  # 0x4d8d57b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x04d8d57b))

        data.write(b'R\x82\xc4~')  # 0x5282c47e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x5282c47e))

        data.write(b's\x04\xda\xfa')  # 0x7304dafa
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.falling_double_jump))

        data.write(b'zI&}')  # 0x7a49267d
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.impulse_double_jump))

        data.write(b'\xa7\x96\xa8\xb9')  # 0xa796a8b9
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xa796a8b9))

        data.write(b'|\x05\x99\xc8')  # 0x7c0599c8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x7c0599c8))

        data.write(b'R*\xb1\xac')  # 0x522ab1ac
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x522ab1ac))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayerControls_UnknownStruct2Json", data)
        return cls(
            unknown_0xff1b0413=json_data['unknown_0xff1b0413'],
            unknown_0xe0c1d958=json_data['unknown_0xe0c1d958'],
            toggle_aim_position=json_data['toggle_aim_position'],
            unknown_0x1f99c6ba=json_data['unknown_0x1f99c6ba'],
            unknown_0x18eb3ab5=json_data['unknown_0x18eb3ab5'],
            unknown_0xbdc01c71=json_data['unknown_0xbdc01c71'],
            fixed_vertical_aim=json_data['fixed_vertical_aim'],
            unknown_0xda97bbcd=json_data['unknown_0xda97bbcd'],
            orbit_around_enemies=json_data['orbit_around_enemies'],
            unknown_0xc224d966=json_data['unknown_0xc224d966'],
            add_grenade_alert=json_data['add_grenade_alert'],
            unknown_0x3fb16819=json_data['unknown_0x3fb16819'],
            unknown_0x4fcf4b70=json_data['unknown_0x4fcf4b70'],
            unknown_0x07bb06a6=json_data['unknown_0x07bb06a6'],
            unknown_0x04d8d57b=json_data['unknown_0x04d8d57b'],
            unknown_0x5282c47e=json_data['unknown_0x5282c47e'],
            falling_double_jump=json_data['falling_double_jump'],
            impulse_double_jump=json_data['impulse_double_jump'],
            unknown_0xa796a8b9=json_data['unknown_0xa796a8b9'],
            unknown_0x7c0599c8=json_data['unknown_0x7c0599c8'],
            unknown_0x522ab1ac=json_data['unknown_0x522ab1ac'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xff1b0413': self.unknown_0xff1b0413,
            'unknown_0xe0c1d958': self.unknown_0xe0c1d958,
            'toggle_aim_position': self.toggle_aim_position,
            'unknown_0x1f99c6ba': self.unknown_0x1f99c6ba,
            'unknown_0x18eb3ab5': self.unknown_0x18eb3ab5,
            'unknown_0xbdc01c71': self.unknown_0xbdc01c71,
            'fixed_vertical_aim': self.fixed_vertical_aim,
            'unknown_0xda97bbcd': self.unknown_0xda97bbcd,
            'orbit_around_enemies': self.orbit_around_enemies,
            'unknown_0xc224d966': self.unknown_0xc224d966,
            'add_grenade_alert': self.add_grenade_alert,
            'unknown_0x3fb16819': self.unknown_0x3fb16819,
            'unknown_0x4fcf4b70': self.unknown_0x4fcf4b70,
            'unknown_0x07bb06a6': self.unknown_0x07bb06a6,
            'unknown_0x04d8d57b': self.unknown_0x04d8d57b,
            'unknown_0x5282c47e': self.unknown_0x5282c47e,
            'falling_double_jump': self.falling_double_jump,
            'impulse_double_jump': self.impulse_double_jump,
            'unknown_0xa796a8b9': self.unknown_0xa796a8b9,
            'unknown_0x7c0599c8': self.unknown_0x7c0599c8,
            'unknown_0x522ab1ac': self.unknown_0x522ab1ac,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_unknown_0xff1b0413(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xe0c1d958(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_toggle_aim_position(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x1f99c6ba(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x18eb3ab5(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xbdc01c71(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_fixed_vertical_aim(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xda97bbcd(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_orbit_around_enemies(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xc224d966(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_add_grenade_alert(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x3fb16819(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4fcf4b70(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x07bb06a6(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x04d8d57b(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x5282c47e(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_falling_double_jump(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_impulse_double_jump(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xa796a8b9(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x7c0599c8(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x522ab1ac(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xff1b0413: ('unknown_0xff1b0413', _decode_unknown_0xff1b0413),
    0xe0c1d958: ('unknown_0xe0c1d958', _decode_unknown_0xe0c1d958),
    0x55c20d58: ('toggle_aim_position', _decode_toggle_aim_position),
    0x1f99c6ba: ('unknown_0x1f99c6ba', _decode_unknown_0x1f99c6ba),
    0x18eb3ab5: ('unknown_0x18eb3ab5', _decode_unknown_0x18eb3ab5),
    0xbdc01c71: ('unknown_0xbdc01c71', _decode_unknown_0xbdc01c71),
    0x1c30f1a6: ('fixed_vertical_aim', _decode_fixed_vertical_aim),
    0xda97bbcd: ('unknown_0xda97bbcd', _decode_unknown_0xda97bbcd),
    0x83583abd: ('orbit_around_enemies', _decode_orbit_around_enemies),
    0xc224d966: ('unknown_0xc224d966', _decode_unknown_0xc224d966),
    0x1fcfaf3f: ('add_grenade_alert', _decode_add_grenade_alert),
    0x3fb16819: ('unknown_0x3fb16819', _decode_unknown_0x3fb16819),
    0x4fcf4b70: ('unknown_0x4fcf4b70', _decode_unknown_0x4fcf4b70),
    0x7bb06a6: ('unknown_0x07bb06a6', _decode_unknown_0x07bb06a6),
    0x4d8d57b: ('unknown_0x04d8d57b', _decode_unknown_0x04d8d57b),
    0x5282c47e: ('unknown_0x5282c47e', _decode_unknown_0x5282c47e),
    0x7304dafa: ('falling_double_jump', _decode_falling_double_jump),
    0x7a49267d: ('impulse_double_jump', _decode_impulse_double_jump),
    0xa796a8b9: ('unknown_0xa796a8b9', _decode_unknown_0xa796a8b9),
    0x7c0599c8: ('unknown_0x7c0599c8', _decode_unknown_0x7c0599c8),
    0x522ab1ac: ('unknown_0x522ab1ac', _decode_unknown_0x522ab1ac),
}
