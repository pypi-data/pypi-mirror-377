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

    class TweakTargeting_ScanJson(typing_extensions.TypedDict):
        scan_lock_scale: float
        scan_lock_transition_time: float
        scan_lock_translation: float
        unknown: json_util.JsonValue
        scan_lock_locked_color: json_util.JsonValue
        scan_lock_unlocked_color: json_util.JsonValue
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xa0857b6e, 0xa4cce30f, 0x8e9bfea3, 0x768110cd, 0x319f966b, 0xa81f378c)


@dataclasses.dataclass()
class TweakTargeting_Scan(BaseProperty):
    scan_lock_scale: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa0857b6e, original_name='ScanLockScale'
        ),
    })
    scan_lock_transition_time: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa4cce30f, original_name='ScanLockTransitionTime'
        ),
    })
    scan_lock_translation: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8e9bfea3, original_name='ScanLockTranslation'
        ),
    })
    unknown: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x768110cd, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    scan_lock_locked_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x319f966b, original_name='ScanLockLockedColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    scan_lock_unlocked_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xa81f378c, original_name='ScanLockUnlockedColor', from_json=Color.from_json, to_json=Color.to_json
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
        if property_count != 6:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHffffLHffffLHffff')
    
        dec = _FAST_FORMAT.unpack(data.read(96))
        assert (dec[0], dec[3], dec[6], dec[9], dec[15], dec[21]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            Color(*dec[11:15]),
            Color(*dec[17:21]),
            Color(*dec[23:27]),
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'\xa0\x85{n')  # 0xa0857b6e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_lock_scale))

        data.write(b'\xa4\xcc\xe3\x0f')  # 0xa4cce30f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_lock_transition_time))

        data.write(b'\x8e\x9b\xfe\xa3')  # 0x8e9bfea3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_lock_translation))

        data.write(b'v\x81\x10\xcd')  # 0x768110cd
        data.write(b'\x00\x10')  # size
        self.unknown.to_stream(data)

        data.write(b'1\x9f\x96k')  # 0x319f966b
        data.write(b'\x00\x10')  # size
        self.scan_lock_locked_color.to_stream(data)

        data.write(b'\xa8\x1f7\x8c')  # 0xa81f378c
        data.write(b'\x00\x10')  # size
        self.scan_lock_unlocked_color.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakTargeting_ScanJson", data)
        return cls(
            scan_lock_scale=json_data['scan_lock_scale'],
            scan_lock_transition_time=json_data['scan_lock_transition_time'],
            scan_lock_translation=json_data['scan_lock_translation'],
            unknown=Color.from_json(json_data['unknown']),
            scan_lock_locked_color=Color.from_json(json_data['scan_lock_locked_color']),
            scan_lock_unlocked_color=Color.from_json(json_data['scan_lock_unlocked_color']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'scan_lock_scale': self.scan_lock_scale,
            'scan_lock_transition_time': self.scan_lock_transition_time,
            'scan_lock_translation': self.scan_lock_translation,
            'unknown': self.unknown.to_json(),
            'scan_lock_locked_color': self.scan_lock_locked_color.to_json(),
            'scan_lock_unlocked_color': self.scan_lock_unlocked_color.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_scan_lock_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_lock_transition_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_lock_translation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_scan_lock_locked_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_scan_lock_unlocked_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xa0857b6e: ('scan_lock_scale', _decode_scan_lock_scale),
    0xa4cce30f: ('scan_lock_transition_time', _decode_scan_lock_transition_time),
    0x8e9bfea3: ('scan_lock_translation', _decode_scan_lock_translation),
    0x768110cd: ('unknown', _decode_unknown),
    0x319f966b: ('scan_lock_locked_color', _decode_scan_lock_locked_color),
    0xa81f378c: ('scan_lock_unlocked_color', _decode_scan_lock_unlocked_color),
}
