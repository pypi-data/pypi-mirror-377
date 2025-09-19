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
from retro_data_structures.properties.corruption.archetypes.FlyerMovementMode import FlyerMovementMode
from retro_data_structures.properties.corruption.archetypes.SpriteStruct import SpriteStruct

if typing.TYPE_CHECKING:
    class UnknownStruct64Json(typing_extensions.TypedDict):
        patrol: json_util.JsonObject
        sprite_struct_0x2cbb438b: json_util.JsonObject
        sprite_struct_0xa80227e6: json_util.JsonObject
        sprite_struct_0x34799811: json_util.JsonObject
        flash_range: float
        flash_range_max: float
        flash_intensity: float
        flash_duration: float
        unknown: float
        flash_delay: float
        scan_delay: float
    

@dataclasses.dataclass()
class UnknownStruct64(BaseProperty):
    patrol: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xccdd3aca, original_name='Patrol', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    sprite_struct_0x2cbb438b: SpriteStruct = dataclasses.field(default_factory=SpriteStruct, metadata={
        'reflection': FieldReflection[SpriteStruct](
            SpriteStruct, id=0x2cbb438b, original_name='SpriteStruct', from_json=SpriteStruct.from_json, to_json=SpriteStruct.to_json
        ),
    })
    sprite_struct_0xa80227e6: SpriteStruct = dataclasses.field(default_factory=SpriteStruct, metadata={
        'reflection': FieldReflection[SpriteStruct](
            SpriteStruct, id=0xa80227e6, original_name='SpriteStruct', from_json=SpriteStruct.from_json, to_json=SpriteStruct.to_json
        ),
    })
    sprite_struct_0x34799811: SpriteStruct = dataclasses.field(default_factory=SpriteStruct, metadata={
        'reflection': FieldReflection[SpriteStruct](
            SpriteStruct, id=0x34799811, original_name='SpriteStruct', from_json=SpriteStruct.from_json, to_json=SpriteStruct.to_json
        ),
    })
    flash_range: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x26945e20, original_name='FlashRange'
        ),
    })
    flash_range_max: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7f878c1c, original_name='FlashRangeMax'
        ),
    })
    flash_intensity: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6e575d67, original_name='FlashIntensity'
        ),
    })
    flash_duration: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8ebea596, original_name='FlashDuration'
        ),
    })
    unknown: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x429c66d3, original_name='Unknown'
        ),
    })
    flash_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x04290e24, original_name='FlashDelay'
        ),
    })
    scan_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7fc827a2, original_name='ScanDelay'
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
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xccdd3aca
        patrol = FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 1.0, 'acceleration': 0.5, 'facing_turn_rate': 10.0, 'turn_threshold': 180.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2cbb438b
        sprite_struct_0x2cbb438b = SpriteStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa80227e6
        sprite_struct_0xa80227e6 = SpriteStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x34799811
        sprite_struct_0x34799811 = SpriteStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x26945e20
        flash_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f878c1c
        flash_range_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6e575d67
        flash_intensity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8ebea596
        flash_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x429c66d3
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x04290e24
        flash_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fc827a2
        scan_delay = struct.unpack('>f', data.read(4))[0]
    
        return cls(patrol, sprite_struct_0x2cbb438b, sprite_struct_0xa80227e6, sprite_struct_0x34799811, flash_range, flash_range_max, flash_intensity, flash_duration, unknown, flash_delay, scan_delay)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'\xcc\xdd:\xca')  # 0xccdd3aca
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patrol.to_stream(data, default_override={'speed': 1.0, 'acceleration': 0.5, 'facing_turn_rate': 10.0, 'turn_threshold': 180.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b',\xbbC\x8b')  # 0x2cbb438b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sprite_struct_0x2cbb438b.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"\xa8\x02'\xe6")  # 0xa80227e6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sprite_struct_0xa80227e6.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'4y\x98\x11')  # 0x34799811
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sprite_struct_0x34799811.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'&\x94^ ')  # 0x26945e20
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flash_range))

        data.write(b'\x7f\x87\x8c\x1c')  # 0x7f878c1c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flash_range_max))

        data.write(b'nW]g')  # 0x6e575d67
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flash_intensity))

        data.write(b'\x8e\xbe\xa5\x96')  # 0x8ebea596
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flash_duration))

        data.write(b'B\x9cf\xd3')  # 0x429c66d3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\x04)\x0e$')  # 0x4290e24
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flash_delay))

        data.write(b"\x7f\xc8'\xa2")  # 0x7fc827a2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_delay))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct64Json", data)
        return cls(
            patrol=FlyerMovementMode.from_json(json_data['patrol']),
            sprite_struct_0x2cbb438b=SpriteStruct.from_json(json_data['sprite_struct_0x2cbb438b']),
            sprite_struct_0xa80227e6=SpriteStruct.from_json(json_data['sprite_struct_0xa80227e6']),
            sprite_struct_0x34799811=SpriteStruct.from_json(json_data['sprite_struct_0x34799811']),
            flash_range=json_data['flash_range'],
            flash_range_max=json_data['flash_range_max'],
            flash_intensity=json_data['flash_intensity'],
            flash_duration=json_data['flash_duration'],
            unknown=json_data['unknown'],
            flash_delay=json_data['flash_delay'],
            scan_delay=json_data['scan_delay'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'patrol': self.patrol.to_json(),
            'sprite_struct_0x2cbb438b': self.sprite_struct_0x2cbb438b.to_json(),
            'sprite_struct_0xa80227e6': self.sprite_struct_0xa80227e6.to_json(),
            'sprite_struct_0x34799811': self.sprite_struct_0x34799811.to_json(),
            'flash_range': self.flash_range,
            'flash_range_max': self.flash_range_max,
            'flash_intensity': self.flash_intensity,
            'flash_duration': self.flash_duration,
            'unknown': self.unknown,
            'flash_delay': self.flash_delay,
            'scan_delay': self.scan_delay,
        }


def _decode_patrol(data: typing.BinaryIO, property_size: int) -> FlyerMovementMode:
    return FlyerMovementMode.from_stream(data, property_size, default_override={'speed': 1.0, 'acceleration': 0.5, 'facing_turn_rate': 10.0, 'turn_threshold': 180.0})


def _decode_flash_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flash_range_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flash_intensity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flash_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flash_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xccdd3aca: ('patrol', _decode_patrol),
    0x2cbb438b: ('sprite_struct_0x2cbb438b', SpriteStruct.from_stream),
    0xa80227e6: ('sprite_struct_0xa80227e6', SpriteStruct.from_stream),
    0x34799811: ('sprite_struct_0x34799811', SpriteStruct.from_stream),
    0x26945e20: ('flash_range', _decode_flash_range),
    0x7f878c1c: ('flash_range_max', _decode_flash_range_max),
    0x6e575d67: ('flash_intensity', _decode_flash_intensity),
    0x8ebea596: ('flash_duration', _decode_flash_duration),
    0x429c66d3: ('unknown', _decode_unknown),
    0x4290e24: ('flash_delay', _decode_flash_delay),
    0x7fc827a2: ('scan_delay', _decode_scan_delay),
}
