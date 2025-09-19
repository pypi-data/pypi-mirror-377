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
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakTargeting_Charge_GaugeJson(typing_extensions.TypedDict):
        unknown_0xd032c2a1: float
        unknown_0xa118e250: float
        unknown_0xdb1ac8ee: float
        unknown_0xecd100f8: float
        charge_gauge_scale: float
        charge_gauge_color: json_util.JsonValue
        unknown_0xed78e6eb: int
        unknown_0x2c3d9e27: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xd032c2a1, 0xa118e250, 0xdb1ac8ee, 0xecd100f8, 0x49f8161f, 0x526e60f4, 0xed78e6eb, 0x2c3d9e27)


@dataclasses.dataclass()
class TweakTargeting_Charge_Gauge(BaseProperty):
    unknown_0xd032c2a1: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd032c2a1, original_name='Unknown'
        ),
    })
    unknown_0xa118e250: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa118e250, original_name='Unknown'
        ),
    })
    unknown_0xdb1ac8ee: float = dataclasses.field(default=150.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdb1ac8ee, original_name='Unknown'
        ),
    })
    unknown_0xecd100f8: float = dataclasses.field(default=210.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xecd100f8, original_name='Unknown'
        ),
    })
    charge_gauge_scale: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x49f8161f, original_name='ChargeGaugeScale'
        ),
    })
    charge_gauge_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x526e60f4, original_name='ChargeGaugeColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xed78e6eb: int = dataclasses.field(default=14, metadata={
        'reflection': FieldReflection[int](
            int, id=0xed78e6eb, original_name='Unknown'
        ),
    })
    unknown_0x2c3d9e27: float = dataclasses.field(default=8.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2c3d9e27, original_name='Unknown'
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
        if property_count != 8:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHffffLHlLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(92))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[21], dec[24]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            Color(*dec[17:21]),
            dec[23],
            dec[26],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'\xd02\xc2\xa1')  # 0xd032c2a1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd032c2a1))

        data.write(b'\xa1\x18\xe2P')  # 0xa118e250
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa118e250))

        data.write(b'\xdb\x1a\xc8\xee')  # 0xdb1ac8ee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdb1ac8ee))

        data.write(b'\xec\xd1\x00\xf8')  # 0xecd100f8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xecd100f8))

        data.write(b'I\xf8\x16\x1f')  # 0x49f8161f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.charge_gauge_scale))

        data.write(b'Rn`\xf4')  # 0x526e60f4
        data.write(b'\x00\x10')  # size
        self.charge_gauge_color.to_stream(data)

        data.write(b'\xedx\xe6\xeb')  # 0xed78e6eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xed78e6eb))

        data.write(b",=\x9e'")  # 0x2c3d9e27
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2c3d9e27))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakTargeting_Charge_GaugeJson", data)
        return cls(
            unknown_0xd032c2a1=json_data['unknown_0xd032c2a1'],
            unknown_0xa118e250=json_data['unknown_0xa118e250'],
            unknown_0xdb1ac8ee=json_data['unknown_0xdb1ac8ee'],
            unknown_0xecd100f8=json_data['unknown_0xecd100f8'],
            charge_gauge_scale=json_data['charge_gauge_scale'],
            charge_gauge_color=Color.from_json(json_data['charge_gauge_color']),
            unknown_0xed78e6eb=json_data['unknown_0xed78e6eb'],
            unknown_0x2c3d9e27=json_data['unknown_0x2c3d9e27'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xd032c2a1': self.unknown_0xd032c2a1,
            'unknown_0xa118e250': self.unknown_0xa118e250,
            'unknown_0xdb1ac8ee': self.unknown_0xdb1ac8ee,
            'unknown_0xecd100f8': self.unknown_0xecd100f8,
            'charge_gauge_scale': self.charge_gauge_scale,
            'charge_gauge_color': self.charge_gauge_color.to_json(),
            'unknown_0xed78e6eb': self.unknown_0xed78e6eb,
            'unknown_0x2c3d9e27': self.unknown_0x2c3d9e27,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_unknown_0xd032c2a1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa118e250(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdb1ac8ee(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xecd100f8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_charge_gauge_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_charge_gauge_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xed78e6eb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x2c3d9e27(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xd032c2a1: ('unknown_0xd032c2a1', _decode_unknown_0xd032c2a1),
    0xa118e250: ('unknown_0xa118e250', _decode_unknown_0xa118e250),
    0xdb1ac8ee: ('unknown_0xdb1ac8ee', _decode_unknown_0xdb1ac8ee),
    0xecd100f8: ('unknown_0xecd100f8', _decode_unknown_0xecd100f8),
    0x49f8161f: ('charge_gauge_scale', _decode_charge_gauge_scale),
    0x526e60f4: ('charge_gauge_color', _decode_charge_gauge_color),
    0xed78e6eb: ('unknown_0xed78e6eb', _decode_unknown_0xed78e6eb),
    0x2c3d9e27: ('unknown_0x2c3d9e27', _decode_unknown_0x2c3d9e27),
}
